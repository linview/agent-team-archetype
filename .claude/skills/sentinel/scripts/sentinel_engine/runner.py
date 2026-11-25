"""五步调度引擎 (design v1.2 §5.3)。

契约:探针只实现 resolve/execute/extract 三步;assert 与 emit 由本引擎统一接管。
这保证断言语义一致、探针实现极简、且可对探针单独 UT(§15.3)。

五步:resolve → execute → extract(探针) → assert(引擎,据 assertion.value 从 signals 取值)
     → emit(累积为 SentinelReport,交 reporter)。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from sentinel_engine import assertion
from sentinel_engine.probes import (
    http_probe, log_grep, metrics_scrape, schedule_liveness, api_query, db_query, api_smoke,
)

# 探针注册表(STORY-1-02: http_probe/log_grep;STORY-1-03 扩展 metrics_scrape/
# schedule_liveness/api_query/db_query;STORY-1-04 补 api_smoke —— 7 探针覆盖 wizard
# 模式 A/B/C + §17 inspect 升格为 synthetic 族 api_smoke)
PROBES = {
    "http_probe": http_probe,
    "log_grep": log_grep,
    "metrics_scrape": metrics_scrape,
    "schedule_liveness": schedule_liveness,
    "api_query": api_query,
    "db_query": db_query,
    "api_smoke": api_smoke,
}


@dataclass
class ProbeOutcome:
    name: str
    type: str
    target: str
    signals: dict
    assert_result: object = None   # AssertionResult 或 None(执行失败时)
    status: str = "pass"           # pass / fail / error
    detail: str = ""


@dataclass
class SentinelReport:
    sentinel: str
    outcomes: list = field(default_factory=list)

    @property
    def all_pass(self) -> bool:
        return bool(self.outcomes) and all(o.status == "pass" for o in self.outcomes)

    @property
    def failures(self) -> list:
        return [o for o in self.outcomes if o.status != "pass"]


def run_probe(probe_decl) -> ProbeOutcome:
    """单探针:resolve→execute→extract→assert(emit 由 run_declaration 累积)。"""
    mod = PROBES.get(probe_decl.type)
    if mod is None:
        return ProbeOutcome(probe_decl.type, probe_decl.type, probe_decl.target,
                            {}, status="error", detail=f"未知探针类型: {probe_decl.type}")
    params = probe_decl.params or {}
    # 1-3 resolve / execute / extract(探针负责);探针意外异常 → 降级 error,不崩引擎
    try:
        resolved = mod.resolve(probe_decl.target, params)
        raw = mod.execute(resolved, params)
        pr = mod.extract(raw, params)
    except Exception as e:
        return ProbeOutcome(probe_decl.type, probe_decl.type, probe_decl.target,
                            {}, assert_result=None, status="error",
                            detail=f"探针执行异常: {type(e).__name__}: {e}")
    # 执行失败(连接层 error / extract 不可断言)→ error,不进入 assert
    if not pr.assertable:
        return ProbeOutcome(probe_decl.type, probe_decl.type, probe_decl.target,
                            pr.signals, assert_result=None, status="error",
                            detail=pr.error or "extract 结果不可断言")
    # 4 assert(引擎统一):从 signals 取断言对象值
    key = probe_decl.assertion.get("value")
    signal_value = pr.signals.get(key)
    # STORY-1-06 #2:evaluate 可能抛 NotImplementedError(expect_trend 未实现)等
    # —— 降级为 error outcome,不中断 run_declaration 循环、不影响后续探针。
    try:
        ar = assertion.evaluate(signal_value, probe_decl.assertion)
    except NotImplementedError as e:
        return ProbeOutcome(probe_decl.type, probe_decl.type, probe_decl.target,
                            pr.signals, assert_result=None, status="error",
                            detail=f"断言原语未实现: {e}")
    except Exception as e:
        return ProbeOutcome(probe_decl.type, probe_decl.type, probe_decl.target,
                            pr.signals, assert_result=None, status="error",
                            detail=f"断言异常: {type(e).__name__}: {e}")
    status = "pass" if ar.passed else "fail"
    return ProbeOutcome(probe_decl.type, probe_decl.type, probe_decl.target,
                        pr.signals, assert_result=ar, status=status, detail=ar.detail)


def run_declaration(declaration) -> SentinelReport:
    """调度 declaration 所有探针 → SentinelReport。

    凭据注入(§12.1)由上层 cli 在调用本函数前完成——引擎本身不碰凭据。
    """
    report = SentinelReport(sentinel=declaration.sentinel)
    for pd in declaration.probes:
        report.outcomes.append(run_probe(pd))
    return report

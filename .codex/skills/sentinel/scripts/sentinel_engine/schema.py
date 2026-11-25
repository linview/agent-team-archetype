"""声明 schema 加载与确定性校验 (design v1.2 §9 / §7.3 / §12.1)。

校验是纯函数:同输入同输出、无副作用。失败抛 SchemaError(明确字段)。

§12.1 凭据铁律:credentials 值为 .env.skill toml 的 **section 名**(非内联值);
schema 层只验类型(section 名为非空 str),'section 存在 + 值非凭据明文'由 resolver 运行时把关。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import yaml

# 合法探针类型(§6.2 全集;本 Story 只实现 http_probe/log_grep,但校验集覆盖 design 全部定义)
PROBE_TYPES = {
    # external
    "http_probe", "tcp_probe", "icmp_probe", "dns_probe", "grpc_probe",
    # internal
    "metrics_scrape", "api_query", "db_query",
    # log
    "log_grep", "log_tail_anomaly",
    # synthetic
    "api_smoke", "e2e_flow",
    # data
    "count_caliber", "schema_check", "drift_check", "schedule_liveness",
}

# 合除断言 op(§7:5 确定性 + 1 有状态)
ASSERT_OPS = {"expect_eq", "expect_le", "expect_ge", "expect_in", "expect_regex", "expect_trend"}

# 各 op 必须的比较 key(§7;STORY-1-06 #3 fail-fast:schema 层校验存在,缺失即报错)。
# expect_trend 需历史快照(§7.2 本 Story 不实现),不强制 key——runtime 降级 error(见 runner #2)。
OP_REQUIRED_KEY = {
    "expect_eq": "equals",
    "expect_le": "max",
    "expect_ge": "min",
    "expect_in": "in",
    "expect_regex": "not_match",
}

SCHEMA_VERSION = 1


class SchemaError(ValueError):
    """声明校验失败。"""


@dataclass
class ProbeDecl:
    """§9.1 probes[] 单项。yaml 字段 assert 映射为 assertion(避开 Python 关键字)。"""
    type: str
    target: str
    assertion: dict                 # §7.3 断言块
    params: dict = field(default_factory=dict)
    signals: list = field(default_factory=list)
    on_fail: str = "warn"


@dataclass
class Declaration:
    """§9.1 顶层声明。"""
    sentinel: str
    schedule: str
    probes: list                    # list[ProbeDecl]
    schema_version: int = SCHEMA_VERSION
    description: str = ""
    durable: bool = True
    recurring_expiry: str = "7d"
    credentials: dict = field(default_factory=dict)
    on_anomaly: dict = field(default_factory=dict)
    on_success: str = "silent"
    source_path: str = ""           # 加载来源(调试/报告用)


def load(path) -> Declaration:
    """加载 yaml 声明并校验。"""
    p = Path(path)
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    return validate(raw, source_path=str(p))


def validate(raw: dict, source_path: str = "") -> Declaration:
    """校验声明 dict → Declaration。纯函数。"""
    if not isinstance(raw, dict):
        raise SchemaError("声明根必须是 mapping")
    # schema_version
    sv = raw.get("schema_version", SCHEMA_VERSION)
    if sv != SCHEMA_VERSION:
        raise SchemaError(f"不支持的 schema_version: {sv}(当前 {SCHEMA_VERSION})")
    # 必填顶层字段
    sentinel = raw.get("sentinel")
    if not sentinel:
        raise SchemaError("缺少必填字段: sentinel")
    schedule = raw.get("schedule")
    if not schedule:
        raise SchemaError("缺少必填字段: schedule")
    probes_raw = raw.get("probes")
    if not probes_raw or not isinstance(probes_raw, list):
        raise SchemaError("缺少必填字段: probes(非空列表)")
    # credentials: 值为 .env.skill toml section 名,禁止内联凭据值(§12.1)
    credentials = raw.get("credentials") or {}
    _check_credentials(credentials)
    # 各探针
    probes = [_validate_probe(p, i) for i, p in enumerate(probes_raw)]
    return Declaration(
        sentinel=sentinel, schedule=schedule, probes=probes,
        schema_version=sv, description=raw.get("description", ""),
        durable=raw.get("durable", True),
        recurring_expiry=raw.get("recurring_expiry", "7d"),
        credentials=credentials,
        on_anomaly=raw.get("on_anomaly") or {},
        on_success=raw.get("on_success", "silent"),
        source_path=source_path,
    )


def _check_credentials(creds: dict) -> None:
    """credentials 各值必须是 .env.skill toml 的 section 名(非空 str),禁止内联凭据值(§12.1 铁律)。

    分层:schema 验类型(section 名为非空 str);'section 存在 + 值非凭据明文'由 resolver 运行时把关(§12.1)。
    """
    if not isinstance(creds, dict):
        raise SchemaError("credentials 必须是 mapping")
    for key, val in creds.items():
        if not isinstance(val, str) or not val:
            raise SchemaError(
                f"credentials.{key} 必须是 .env.skill toml section 名(非空字符串),禁止内联凭据值(§12.1)"
            )


def _validate_probe(raw: dict, idx: int) -> ProbeDecl:
    if not isinstance(raw, dict):
        raise SchemaError(f"probes[{idx}] 必须是 mapping")
    ptype = raw.get("type")
    if ptype not in PROBE_TYPES:
        raise SchemaError(f"probes[{idx}].type 非法: {ptype!r}(合法集见 §6.2)")
    target = raw.get("target")
    if not target:
        raise SchemaError(f"probes[{idx}] 缺少必填字段: target")
    ass = raw.get("assert")
    if not isinstance(ass, dict):
        raise SchemaError(f"probes[{idx}] 缺少 assert 断言块(§7.3)")
    op = ass.get("op")
    if op not in ASSERT_OPS:
        raise SchemaError(f"probes[{idx}].assert.op 非法: {op!r}(合法集 §7)")
    if not ass.get("value"):
        raise SchemaError(f"probes[{idx}].assert 缺少 value(引用 signal key)")
    req = OP_REQUIRED_KEY.get(op)
    if req and req not in ass:
        raise SchemaError(f"probes[{idx}].assert.op={op} 缺少比较 key `{req}`(§7;STORY-1-06 #3 fail-fast)")
    return ProbeDecl(
        type=ptype, target=target, assertion=ass,
        params=raw.get("params") or {},
        signals=raw.get("signals") or [],
        on_fail=raw.get("on_fail", "warn"),
    )

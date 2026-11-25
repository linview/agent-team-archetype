"""api_smoke: synthetic 族多端点冒烟探针 (design v1.2 §6.2 synthetic / §17 inspect 升格)。

承接 §17 资产迁移:旧 `scripts/inspect`(bash 硬编码多端点冒烟:healthz/资源查询/错误场景)
升格为本声明驱动探针——用户在声明里列 endpoints 清单,引擎一次跑完多端点冒烟。

契约同 http_probe(§6.1):resolve/extract 纯函数,execute 是唯一 IO 步骤;
assert/emit 由引擎接管,不在探针内(§5.3)。

**多端点单断言设计**:schema 单探针只一个 assert 块(§9.1),故 extract 产**汇总** signal
`all_passed`(所有端点 status==expect_status);每端点期望状态(expect_status,默认 200)
在 params.endpoints 声明,execute 逐个打、extract 比对汇总。assert 用
`expect_eq all_passed equals True`。这把 inspect 的"多端点冒烟"能力收敛进单探针单断言,
契合 schema,无需用户手写 N 个 http_probe。

依赖:仅 stdlib(urllib),与 http_probe 同,保证可移植。
"""
from __future__ import annotations
import urllib.request
import urllib.error
from sentinel_engine.probes import ProbeResult


def resolve(target: str, params: dict) -> str:
    """resolve(纯): API base url 透传(真实场景可做 ${HOST}/${PORT} 替换,纯映射无 IO)。"""
    return target


def _fetch_one(url: str, timeout: int) -> dict:
    """打单个端点 → {status, error?}(照 http_probe.execute 错误处理)。

    4xx/5xx 也是"成功拿到响应",status 即比对对象;连接层失败(超时/拒绝)→ status=None + error。
    """
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()  # 消费 body(释放连接)
            return {"status": resp.status}
    except urllib.error.HTTPError as e:
        return {"status": e.code}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"status": None, "error": f"{type(e).__name__}: {e}"}
    except Exception as e:  # 兜底:任何意外都不让引擎崩
        return {"status": None, "error": f"{type(e).__name__}: {e}"}


def execute(base_url: str, params: dict) -> dict:
    """execute(IO): 遍历 params.endpoints 逐个 GET base_url+path,collect {key: {status, error?}}。

    endpoints: list[{path, key?, expect_status?}](key 默认取 path;expect_status 默认 200,extract 用)。
    副作用严格隔离:不发其他全局副作用;失败不抛、记 error 键交 extract 判定。
    """
    timeout = params.get("timeout", 5)
    endpoints = params.get("endpoints") or []
    results = {}
    for ep in endpoints:
        path = ep.get("path")
        key = ep.get("key") or path
        if not path:
            results[key or "?"] = {"status": None, "error": "endpoint 缺必填 path"}
            continue
        url = base_url.rstrip("/") + "/" + str(path).lstrip("/")
        results[key] = _fetch_one(url, timeout)
    return {"endpoints": results}


def extract(raw: dict, params: dict) -> ProbeResult:
    """extract(纯): 汇总各端点状态 → signals(all_passed + pass_count/fail_count + 每端点 <key>_status)。

    - all_passed = 所有端点 status == expect_status(默认 200)。
    - 任一端点连接层 error(status is None)→ assertable=False(执行错误,无法判定 pass/fail)。
    - 无 endpoints → assertable=False。
    """
    endpoints_decl = params.get("endpoints") or []
    expect_map = {(ep.get("key") or ep.get("path")): ep.get("expect_status", 200) for ep in endpoints_decl}
    raw_results = raw.get("endpoints") or {}
    if not raw_results:
        return ProbeResult(raw=raw, signals={}, assertable=False, error="未配置 endpoints 或 execute 未产出")
    signals: dict = {}
    pass_count = 0
    fail_count = 0
    had_error = False
    errored_keys = []
    for key, r in raw_results.items():
        status = r.get("status")
        signals[f"{key}_status"] = status
        if status is None:
            had_error = True
            errored_keys.append(key)
            fail_count += 1
            continue
        if status == expect_map.get(key, 200):
            pass_count += 1
        else:
            fail_count += 1
    signals["pass_count"] = pass_count
    signals["fail_count"] = fail_count
    if had_error:
        # 连接层失败:不可断言(报告里仍保留各端点 status 供归因)
        return ProbeResult(raw=raw, signals=signals, assertable=False,
                           error=f"端点连接失败: {errored_keys}")
    signals["all_passed"] = (fail_count == 0)
    return ProbeResult(raw=raw, signals=signals, assertable=True)

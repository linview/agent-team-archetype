"""http_probe: lifecycle 三步 resolve/execute/extract (design v1.2 §6.1)。

契约铁律:resolve 与 extract 是纯函数(同入同出、无副作用、确定性);
execute 是探针中**唯一**带 IO 副作用的步骤(发 HTTP 请求)。
assert/emit 由引擎接管,不在探针内(§5.3)。

extract_rules 的 regex 经 safe_regex_search(预编译 + 超时防灾难回溯,承接 POC H2)。
依赖:仅 stdlib(urllib),无第三方 HTTP 客户端,保证可移植。
"""
from __future__ import annotations
import re
import urllib.request
import urllib.error
from sentinel_engine.probes import ProbeResult, safe_regex_search


def resolve(target: str, params: dict) -> str:
    """resolve(纯): target URL 的规范化/变量替换(纯映射,无 IO)。

    真实场景可在此做 ${HOST}/${PORT} 替换或目标别名解析——但都是纯映射,无 IO。
    """
    return target


def execute(url: str, params: dict) -> dict:
    """execute(IO): 发 GET 请求,返回 raw dict(status_code/body/headers)。

    副作用严格隔离在本函数:不读/写全局,不改入参,不开持久连接。
    失败(超时/连接拒绝)不抛异常,而是在 raw 里带 error 键——交给 extract 判定 assertable=False。
    """
    timeout = params.get("timeout", 5)
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {"status_code": resp.status, "body": body, "headers": dict(resp.headers)}
    except urllib.error.HTTPError as e:
        # 4xx/5xx 也算"成功拿到响应",status_code 即断言对象
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return {"status_code": e.code, "body": body, "headers": dict(e.headers or {})}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        # 连接层失败(超时/拒绝):无 status_code,不可断言
        return {"status_code": None, "body": "", "headers": {}, "error": f"{type(e).__name__}: {e}"}
    except Exception as e:  # 兜底:任何意外都不让引擎崩
        return {"status_code": None, "body": "", "headers": {}, "error": f"{type(e).__name__}: {e}"}


def extract(raw: dict, params: dict) -> ProbeResult:
    """extract(纯): 从 raw 提取 signals(断言对象)。

    默认 signal: status_code。
    可选: params.extract_rules = {signal_key: regex} 从 body 提取额外 signal(safe_regex 超时防护)。
    若 raw 带 error(连接层失败)→ assertable=False,引擎据此跳过断言、记为执行失败。
    """
    if raw.get("error"):
        return ProbeResult(raw=raw, signals={}, assertable=False, error=raw["error"])
    signals = {"status_code": raw.get("status_code")}
    rules = params.get("extract_rules") or {}
    for key, pattern in rules.items():
        try:
            m = safe_regex_search(pattern, raw.get("body", ""))
        except re.error:
            continue  # 坏 pattern 跳过该 signal(不崩)
        if m:
            signals[key] = m.group(1) if m.groups() else m.group(0)
    return ProbeResult(raw=raw, signals=signals, assertable="status_code" in signals)

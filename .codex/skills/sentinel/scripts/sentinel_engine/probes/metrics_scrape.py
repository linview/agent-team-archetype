"""metrics_scrape: Prometheus /metrics 抓取 + exposition 文本解析 (design v1.2 §6.2)。

lifecycle 三步:resolve(纯 target 规范化)→ execute(IO urllib GET /metrics 文本)
→ extract(纯:解析 Prometheus exposition 格式,按 queries 取指标值)。

契约铁律同 http_probe:resolve/extract 是纯函数(同入同出、无副作用、确定性),
execute 是探针唯一 IO 副作用步骤。失败(超时/连接拒绝)raw 带 error → extract assertable=False。

依赖:仅 stdlib(urllib + 正则),无第三方 Prometheus 客户端,保证可移植。
"""
from __future__ import annotations
import re
import urllib.request
import urllib.error
from sentinel_engine.probes import ProbeResult

# Prometheus exposition 行: name{labels} value  或  name value
# name 首字符限制 [a-zA-Z_:],续字符 [a-zA-Z0-9_:];值为数值(科学计数/负数/小数)。
_METRIC_LINE = re.compile(r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{[^}]*\})?\s+([-+]?[\d.]+(?:[eE][-+]?\d+)?)')


def resolve(target: str, params: dict) -> str:
    """resolve(纯): target URL 规范化/变量替换(纯映射,无 IO)。"""
    return target


def execute(url: str, params: dict) -> dict:
    """execute(IO): GET /metrics → raw{status_code, text}。失败 raw 带 error(不抛,交 extract 判定)。"""
    timeout = params.get("timeout", 5)
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            return {"status_code": resp.status, "text": text}
    except urllib.error.HTTPError as e:
        # 4xx/5xx:拿到了响应但非 200,视为抓取失败(error),不当作可断言的指标源
        try:
            text = e.read().decode("utf-8", errors="replace")
        except Exception:
            text = ""
        return {"status_code": e.code, "text": text, "error": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"status_code": None, "text": "", "error": f"{type(e).__name__}: {e}"}
    except Exception as e:  # 兜底:任何意外都不让引擎崩
        return {"status_code": None, "text": "", "error": f"{type(e).__name__}: {e}"}


def _parse_exposition(text: str) -> dict:
    """纯函数:解析 Prometheus exposition 文本 → {metric_name: 最新数值}。

    - 注释行(# 开头,HELP/TYPE)跳过
    - 带 label 的行去掉 {labels} 取 name
    - 同名多样本取最后出现(典型:取最新)
    - 非数值(+Inf/NaN 等不匹配数值 regex 的)跳过,不崩
    同入同出、无副作用、确定性(承接 POC H2 deepcopy 双跑基础)。
    """
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _METRIC_LINE.match(line)
        if m:
            name, raw_val = m.group(1), m.group(2)
            try:
                values[name] = float(raw_val)
            except ValueError:
                continue
    return values


def extract(raw: dict, params: dict) -> ProbeResult:
    """extract(纯): 按 params.queries(dict{signal_key: metric_name})从 /metrics 解析 → signals。

    未命中的 metric 不入 signals。raw 带 error → assertable=False。
    可断言性:至少 1 个 query 命中(避免空 signals 被引擎误判 pass)。
    """
    if raw.get("error"):
        return ProbeResult(raw=raw, signals={}, assertable=False, error=raw["error"])
    values = _parse_exposition(raw.get("text", ""))
    queries = params.get("queries") or {}
    signals = {sig: values[m] for sig, m in queries.items() if m in values}
    return ProbeResult(raw=raw, signals=signals, assertable=bool(signals))

"""探针契约类型 + 共用 regex 工具 (design v1.2 §6.1)。

ProbeResult: 探针 resolve/execute/extract 的产物;assert/emit 由引擎接管(§5.3)。
探针只负责产 ProbeResult,不造断言、不做 emit。

safe_regex_*: 预编译 + SIGALRM 超时保护的 regex(防灾难回溯,承接 POC H2 enhancement)。
主线程(unix)用超时;非主线程/信号不可用 → 退化为无超时(仅预编译)。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import re
import signal

_REGEX_TIMEOUT = 2.0  # 秒;灾难回溯防护上限


def _regex_timeout_handler(signum, frame):
    raise TimeoutError("regex 超时(灾难回溯防护)")


@dataclass
class ProbeResult:
    raw: Any = None                              # 原始结果(调试用)
    signals: dict = field(default_factory=dict)  # 产出信号值,如 {"status_code": 200, "latency_ms": 12}
    assertable: bool = False                     # 是否可断言(execute 成功)
    error: str | None = None                     # execute/resolve 失败原因


def _run_with_timeout(fn, timeout, *args):
    """主线程(unix)用 SIGALRM 限时执行 fn;超时返回 None;非主线程/信号不可用 → 无超时退化。"""
    try:
        old = signal.signal(signal.SIGALRM, _regex_timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, timeout)
        try:
            return fn(*args)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
    except TimeoutError:
        return None
    except (ValueError, OSError):
        # 非主线程或平台无 SIGALRM → 退化为无超时
        return fn(*args)


def safe_regex_search(pattern, text, timeout=_REGEX_TIMEOUT):
    """预编译 + 超时 regex search;超时/退化 → None(无匹配)。坏 pattern 抛 re.error(调用方捕获)。"""
    compiled = re.compile(pattern)
    return _run_with_timeout(compiled.search, timeout, text)


def safe_regex_findall(pattern, text, timeout=_REGEX_TIMEOUT):
    """预编译 + 超时 regex findall;超时/退化 → [](无匹配)。"""
    compiled = re.compile(pattern)
    r = _run_with_timeout(compiled.findall, timeout, text)
    return [] if r is None else r

"""log_grep:经凭据连接目标取日志 + grep (design v1.2 §6.2 / §6.1 lifecycle / §14.2 H5)。

execute 是探针唯一 IO 步:subprocess 调 fetcher(模拟远程取日志),凭据值经 env
传入子进程并参与鉴权(token 比对)——这是 H5「探针真用凭据值连接目标」的闭环。
resolve/extract 保持纯函数(同入同出、无副作用、确定性)。

fetcher 由 params.fetcher 或 env SENTINEL_LOG_FETCHER 指定(引擎不内置 fetcher;
本地验证可指向任意打印日志的脚本替身,真实场景换 ssh/scp wrapper)。
lifecycle 三步契约不变。
"""
from __future__ import annotations
import os
import sys
import subprocess
from sentinel_engine.probes import ProbeResult, safe_regex_findall


def resolve(target: str, params: dict) -> str:
    return target


def execute(path: str, params: dict) -> dict:
    """subprocess(IO):经凭据连接目标取日志 → raw{text}。

    凭据值从不作为参数传入(§12.1);requires_env 声明所需 env 键,缺失即失败;
    fetcher 读 LOG_TOKEN 与 LOG_TOKEN_EXPECTED 比对,真正消费凭据值。
    stderr 被捕获(纳入 H5 不泄漏守卫范围),不回显 token。
    """
    required = params.get("requires_env") or []
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        return {"text": "", "error": f"凭据未注入: {missing}"}
    fetcher = params.get("fetcher") or os.environ.get("SENTINEL_LOG_FETCHER")
    if not fetcher or not os.path.isfile(fetcher):
        return {"text": "", "error": "log_grep 未配置 fetcher(params.fetcher 或 env SENTINEL_LOG_FETCHER)"}
    env = {**os.environ, "LOG_PATH": path}
    try:
        proc = subprocess.run(
            [sys.executable, fetcher], env=env,
            capture_output=True, text=True, timeout=params.get("timeout", 10),
        )
    except subprocess.TimeoutExpired:
        return {"text": "", "error": "fetch 超时"}
    if proc.returncode != 0:
        return {"text": "", "error": f"fetch rc={proc.returncode}: {proc.stderr.strip()}"}
    return {"text": proc.stdout, "stderr": proc.stderr}


def extract(raw: dict, params: dict) -> ProbeResult:
    """纯函数:grep pattern 计数 → signals{match_count, matched[首5]}。"""
    if raw.get("error"):
        return ProbeResult(raw=raw, signals={}, assertable=False, error=raw["error"])
    pattern = params.get("pattern", "")
    hits = safe_regex_findall(pattern, raw.get("text", "")) if pattern else []
    return ProbeResult(
        raw=raw,
        signals={"match_count": len(hits), "matched": hits[:5]},
        assertable=True,
    )

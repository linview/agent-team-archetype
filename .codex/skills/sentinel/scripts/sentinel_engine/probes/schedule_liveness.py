"""schedule_liveness: 定时任务心跳探针(design v1.2 §6.2 data 族)。

经凭据连接目标取"调度日志"(近 since 窗口),regex trigger_pattern 计触发次数 →
signals{trigger_count}。用途:ETL/批处理项目的 cron heartbeat 验证(§8.1 模式 B)。

机制同 log_grep(fetcher 模式:subprocess 调 params.fetcher,凭据经 env 注入子进程
并参与鉴权 —— 承接 POC H5「探针真用凭据值连接目标」);extract 用 trigger_pattern
计数,语义聚焦"近窗口定时触发数"(区别于 log_grep 的通用错误检索)。

resolve/extract 是纯函数(同入同出、无副作用、确定性);execute 是唯一 IO 步。
fetcher 由 params.fetcher 或 env SENTINEL_LOG_FETCHER 指定(引擎不内置 fetcher,
本地验证可指向任意打印日志的脚本替身,真实场景换 ssh/scp wrapper)。
"""
from __future__ import annotations
import os
import sys
import subprocess
from sentinel_engine.probes import ProbeResult, safe_regex_findall


def resolve(target: str, params: dict) -> str:
    """resolve(纯): target(日志路径/docker:/ssh: 形态)规范化(纯映射,无 IO)。"""
    return target


def execute(path: str, params: dict) -> dict:
    """subprocess(IO):经凭据连接目标取调度日志 → raw{text}。

    凭据值从不作为参数传入(§12.1);requires_env 声明所需 env 键,缺失即失败;
    fetcher 读 LOG_TOKEN 与 LOG_TOKEN_EXPECTED 比对,真正消费凭据值(H5 闭环)。
    stderr 捕获(纳入 H5 不泄漏守卫范围),不回显 token。
    """
    required = params.get("requires_env") or []
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        return {"text": "", "error": f"凭据未注入: {missing}"}
    fetcher = params.get("fetcher") or os.environ.get("SENTINEL_LOG_FETCHER")
    if not fetcher or not os.path.isfile(fetcher):
        return {"text": "", "error": "schedule_liveness 未配置 fetcher(params.fetcher 或 env SENTINEL_LOG_FETCHER)"}
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
    """纯函数:trigger_pattern 计数 → signals{trigger_count}。

    "近窗口定时触发数"心跳(§8.1 模式 B ETL):trigger_count = 窗口内匹配
    trigger_pattern 的行数。raw 带 error → assertable=False;
    否则恒 assertable(0 触发仍可断言,由 expect_ge trigger_count min N 判 fail)。
    """
    if raw.get("error"):
        return ProbeResult(raw=raw, signals={}, assertable=False, error=raw["error"])
    pattern = params.get("trigger_pattern", "")
    hits = safe_regex_findall(pattern, raw.get("text", "")) if pattern else []
    return ProbeResult(
        raw=raw,
        signals={"trigger_count": len(hits)},
        assertable=True,
    )

"""api_query: 容器/资源健康查询探针(design v1.2 §6.2 internal 族 / §8.1 §8.2)。

首批 adapter:docker_inspect —— 取容器健康(§8.1 容器编排基础设施行 / §8.2 混合型
模式 B 的 container_health)。经 fetcher 模式 subprocess 调 adapter 脚本
(params.fetcher 或 env SENTINEL_API_FETCHER)取目标 JSON → 按 fields 提取 signals。

只读:docker inspect / k8s get 天然只读(§12.2),探针不触发任何写操作。
机制同 log_grep:fetcher 由外部提供,引擎不内置连接逻辑(可移植 + 不碰真实环境);
测试用 tools/api_fetcher_mock.py 替身返固定 JSON,真实场景换 docker/k8s adapter
wrapper。凭据(k8s kubeconfig 等)经 env 注入(§12.1)。

resolve/extract 是纯函数(同入同出、无副作用、确定性);execute 是唯一 IO 步。
"""
from __future__ import annotations
import os
import sys
import json
import subprocess
from sentinel_engine.probes import ProbeResult


def resolve(target: str, params: dict) -> str:
    """resolve(纯): target 形态(docker:<name> / k8s:<res> / <url>)原样透传。

    纯映射,无 IO;真实 docker/k8s 地址解析在 adapter fetcher 侧(可替换)。
    """
    return target


def _run_adapter_fetcher(target: str, adapter: str, params: dict) -> dict:
    """subprocess(IO):调 adapter fetcher 取 JSON。凭据经 env(§12.1);缺失/失败 → error。"""
    required = params.get("requires_env") or []
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        return {"json": None, "error": f"凭据未注入: {missing}"}
    fetcher = params.get("fetcher") or os.environ.get("SENTINEL_API_FETCHER")
    if not fetcher or not os.path.isfile(fetcher):
        return {"json": None, "error": f"api_query 未配置 fetcher(adapter={adapter};params.fetcher 或 env SENTINEL_API_FETCHER)"}
    env = {**os.environ, "SENTINEL_TARGET": target, "SENTINEL_ADAPTER": adapter}
    try:
        proc = subprocess.run(
            [sys.executable, fetcher], env=env,
            capture_output=True, text=True, timeout=params.get("timeout", 10),
        )
    except subprocess.TimeoutExpired:
        return {"json": None, "error": "fetch 超时"}
    if proc.returncode != 0:
        return {"json": None, "error": f"fetch rc={proc.returncode}: {proc.stderr.strip()}"}
    try:
        return {"json": json.loads(proc.stdout), "stderr": proc.stderr}
    except json.JSONDecodeError as e:
        return {"json": None, "error": f"fetcher 输出非 JSON: {e}"}


def execute(target: str, params: dict) -> dict:
    """execute(IO): 按 adapter 取目标 JSON。adapter 默认 docker_inspect。"""
    adapter = params.get("adapter", "docker_inspect")
    return _run_adapter_fetcher(target, adapter, params)


def _get_path(obj, dotted: str):
    """纯函数:dotted path(如 'State.Status' / 'Mounts.0.Source')从嵌套 dict/list 取值。

    缺失 / 类型不符 → None。同入同出、无副作用、确定性。
    """
    cur = obj
    for seg in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur.get(seg)
        elif isinstance(cur, list):
            try:
                cur = cur[int(seg)]
            except (ValueError, IndexError):
                return None
        else:
            return None
        if cur is None:
            return None
    return cur


def extract(raw: dict, params: dict) -> ProbeResult:
    """纯函数:按 params.fields(dict{signal_key: dotted_path})从 JSON 提取 → signals。

    docker_inspect 返 list([ContainerData]);取首个元素为查询对象(典型单容器)。
    raw 带 error / 无 JSON → assertable=False。未命中 field 不入 signals;
    至少 1 field 命中才 assertable(防空 signals 误判 pass)。
    """
    if raw.get("error"):
        return ProbeResult(raw=raw, signals={}, assertable=False, error=raw["error"])
    data = raw.get("json")
    if data is None:
        return ProbeResult(raw=raw, signals={}, assertable=False, error="无 JSON 数据")
    if isinstance(data, list) and data:
        data = data[0]
    fields = params.get("fields") or {}
    signals = {sig: _get_path(data, path) for sig, path in fields.items()}
    hit = {k: v for k, v in signals.items() if v is not None}
    return ProbeResult(raw=raw, signals=hit, assertable=bool(hit))

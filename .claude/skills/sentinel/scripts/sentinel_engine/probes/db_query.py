"""db_query: 只读 SQL 查询探针(design v1.2 §6.2 data 族 / §8.1 模式 C DB)。

经 fetcher 模式 subprocess 调 db fetcher(params.fetcher 或 env SENTINEL_DB_FETCHER)
执行只读 SQL → 解析输出 → signals{row_count, 列值}。用途:数据-DB 项目的行数 /
口径 / 完整性验证(§8.1 数据-DB 模式 C)。

只读铁律(§12.2):execute 前对 sql 做白名单校验(仅 SELECT/WITH 开头,拒绝任何写
关键字 INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/INTO 等),fail-fast 不连 DB;
fetcher 层真实只读由 wrapper 保证(双重保险)。凭据(DSN/HOST/USER/PASS)经 env 注入
(§12.1 .env.skill section),绝不进 target/sql 文本。

机制同 log_grep:fetcher 由外部提供,引擎不内置 DB 客户端(可移植 + 标准库优先 +
不碰真实 PG,守 CLAUDE.md);测试用 tools/db_fetcher_mock.py 替身,真实换 psql/pg
wrapper。resolve/extract 是纯函数;execute 是唯一 IO 步。
"""
from __future__ import annotations
import os
import re
import sys
import json
import subprocess
from sentinel_engine.probes import ProbeResult

# 写操作关键字(词边界检测,拒绝任何写操作,守 §12.2 只读)
_WRITE_KEYWORDS = ("insert", "update", "delete", "drop", "alter", "truncate",
                   "create", "replace", "merge", "grant", "revoke", "vacuum", "into")


def _is_readonly(sql: str) -> bool:
    """纯函数:校验 sql 只读。SELECT/WITH 开头 + 不含写关键字(词边界)。

    同入同出、无副作用、确定性。SELECT INTO 亦被拒(INTO 是写操作)。
    """
    s = sql.strip().lower().lstrip("(")
    if not (s.startswith("select") or s.startswith("with")):
        return False
    for kw in _WRITE_KEYWORDS:
        if re.search(rf"\b{kw}\b", s):
            return False
    return True


def resolve(target: str, params: dict) -> str:
    """resolve(纯): target 逻辑名(db://primary)原样透传;实际连接参数从 env 取(§12.1)。"""
    return target


def execute(target: str, params: dict) -> dict:
    """subprocess(IO):经 db fetcher 执行只读 SQL → raw{rows}。

    只读 fail-fast(§12.2):sql 非只读 → error,不连 DB。
    凭据从 env(§12.1);fetcher 不存在/失败/超时 → error(不抛,交 extract 判定)。
    """
    sql = params.get("sql", "")
    if not _is_readonly(sql):
        return {"rows": None, "error": f"非只读 SQL 被拒(§12.2): {sql[:60]!r}"}
    required = params.get("requires_env") or []
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        return {"rows": None, "error": f"凭据未注入: {missing}"}
    fetcher = params.get("fetcher") or os.environ.get("SENTINEL_DB_FETCHER")
    if not fetcher or not os.path.isfile(fetcher):
        return {"rows": None, "error": "db_query 未配置 fetcher(params.fetcher 或 env SENTINEL_DB_FETCHER)"}
    env = {**os.environ, "SENTINEL_TARGET": target, "SENTINEL_SQL": sql}
    try:
        proc = subprocess.run(
            [sys.executable, fetcher], env=env,
            capture_output=True, text=True, timeout=params.get("timeout", 15),
        )
    except subprocess.TimeoutExpired:
        return {"rows": None, "error": "query 超时"}
    if proc.returncode != 0:
        return {"rows": None, "error": f"query rc={proc.returncode}: {proc.stderr.strip()}"}
    try:
        return {"rows": json.loads(proc.stdout), "stderr": proc.stderr}
    except json.JSONDecodeError as e:
        return {"rows": None, "error": f"fetcher 输出非 JSON: {e}"}


def extract(raw: dict, params: dict) -> ProbeResult:
    """纯函数:从查询结果提 row_count + 指定列值 → signals。

    fetcher 输出 JSON:list[dict] 行。signals 固含 row_count;params.columns
    (list[col_name])取首行列值(典型口径/完整性校验)。raw error / 无结果
    → assertable=False;否则恒 assertable(row_count 0 仍可断言,由 expect_ge
    row_count min N 判 fail)。
    """
    if raw.get("error"):
        return ProbeResult(raw=raw, signals={}, assertable=False, error=raw["error"])
    rows = raw.get("rows")
    if rows is None:
        return ProbeResult(raw=raw, signals={}, assertable=False, error="无查询结果")
    row_count = len(rows) if isinstance(rows, list) else 0
    signals = {"row_count": row_count}
    columns = params.get("columns") or []
    first = rows[0] if (isinstance(rows, list) and rows and isinstance(rows[0], dict)) else {}
    for col in columns:
        if col in first:
            signals[col] = first[col]
    return ProbeResult(raw=raw, signals=signals, assertable=True)

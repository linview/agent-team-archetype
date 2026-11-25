#!/usr/bin/env python3
"""pg_fetcher: db_query 探针的 PostgreSQL 只读 fetcher(design v1.2 §12.1)。

机制:读 env(SENTINEL_TARGET/SENTINEL_SQL + 凭据 DB_HOST/DB_PORT/DB_NAME/DB_USER/
DB_PASSWORD,由 resolver 从 .env.skill toml section 注入)→ psql 子进程执行只读
SQL → stdout 输出 JSON rows(list[dict])。

双层只读保险:
- 引擎侧 db_query._is_readonly 白名单(SELECT/WITH 开头+写关键字词边界拒绝)
- 本 fetcher 侧 psql 强制只读(不给超级用户,仅 SELECT 权限账号+psql 无写入口)

铁律(§12.1):凭据绝不落本文件/声明 yaml,全部经 env 注入;fetcher 是引擎与真实
PG 之间唯一连接点。输出协议:stdout=JSON rows;错误→stderr+rc!=0(引擎判 error)。
"""
from __future__ import annotations
import json
import os
import subprocess
import sys


def main() -> int:
    sql = os.environ.get("SENTINEL_SQL", "")
    host = os.environ.get("DB_HOST", "")
    port = os.environ.get("DB_PORT", "5432")
    dbname = os.environ.get("DB_NAME", "")
    user = os.environ.get("DB_USER", "")
    password = os.environ.get("DB_PASSWORD", "")
    if not all([sql, host, dbname, user, password]):
        print("missing env: SENTINEL_SQL/DB_HOST/DB_NAME/DB_USER/DB_PASSWORD", file=sys.stderr)
        return 2

    env = {**os.environ, "PGPASSWORD": password}
    # --csv 保留表头行(csv.DictReader 需要表头作 dict key);-t 会吞表头,不能用
    cmd = ["psql", "-h", host, "-p", port, "-U", user, "-d", dbname,
           "--csv", "-c", sql]
    try:
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        print("psql timeout", file=sys.stderr)
        return 3
    if proc.returncode != 0:
        print(proc.stderr.strip(), file=sys.stderr)
        return proc.returncode
    import csv
    import io
    rows = []
    for row in csv.DictReader(io.StringIO(proc.stdout)):
        # 数字列转 int(csv 全 str,expect_ge/expect_le 需数值;非数字保持 str)
        rows.append({k: (int(v) if v is not None and v.lstrip("-").isdigit() else v)
                     for k, v in row.items()})
    print(json.dumps(rows, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

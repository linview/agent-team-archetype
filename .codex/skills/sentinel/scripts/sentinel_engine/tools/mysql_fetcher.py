#!/usr/bin/env python3
"""mysql_fetcher: db_query 探针的 MySQL 只读 fetcher(design v1.2 §12.1)。

机制同 pg_fetcher:凭据经 env(DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD)注入 →
mysql 客户端子进程执行只读 SQL → stdout JSON rows。双层只读保险同 pg_fetcher。
"""
from __future__ import annotations
import csv
import io
import json
import os
import subprocess
import sys


def main() -> int:
    sql = os.environ.get("SENTINEL_SQL", "")
    host = os.environ.get("DB_HOST", "")
    port = os.environ.get("DB_PORT", "3306")
    dbname = os.environ.get("DB_NAME", "")
    user = os.environ.get("DB_USER", "")
    password = os.environ.get("DB_PASSWORD", "")
    if not all([sql, host, dbname, user, password]):
        print("missing env: SENTINEL_SQL/DB_HOST/DB_NAME/DB_USER/DB_PASSWORD", file=sys.stderr)
        return 2

    # 密码经 MYSQL_PWD env 注入(不用 -p 参数:命令行凭据在进程列表可见,违 §12.1
    # 凭据不泄漏原则;与 pg_fetcher 的 PGPASSWORD 对称)
    env = {**os.environ, "MYSQL_PWD": password}
    cmd = ["mysql", "-h", host, "-P", port, "-u", user,
           dbname, "-B", "-e", sql]
    try:
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        print("mysql timeout", file=sys.stderr)
        return 3
    if proc.returncode != 0:
        print(proc.stderr.strip(), file=sys.stderr)
        return proc.returncode
    rows = []
    for row in csv.DictReader(io.StringIO(proc.stdout), delimiter="\t"):
        # 数字列转 int(csv 全 str,expect_ge/expect_le 需数值;非数字保持 str)
        rows.append({k: (int(v) if v is not None and v.lstrip("-").isdigit() else v)
                     for k, v in row.items()})
    print(json.dumps(rows, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

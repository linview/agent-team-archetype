"""CLI 入口 (design v1.2 §10.2 确定性 CLI)。

sentinel run <yaml>       加载声明 → 注入凭据 → 跑引擎 → reporter
                           (全 pass 打一行 ok 静默 / 有 fail 落 md)
sentinel register <yaml>  生成薄 prompt + scheduled_tasks.json mock (§11.1)

执行模型铁律(§10.2):CronCreate 唤醒时只携带薄 prompt → 触发本 CLI →
确定性引擎完成全部逻辑。prompt 内零 probe 逻辑、零凭据。
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
from sentinel_engine import schema, resolver, runner, reporter, register


def _env_skill_path(yaml_path: str) -> str:
    """§12.1:.env.skill(toml)路径:优先 SENTINEL_ENV_SKILL env var,否则项目根(git root,无 .git 取 cwd)。"""
    p = os.environ.get("SENTINEL_ENV_SKILL")
    if p:
        return p
    # 向上找 git root 作为项目根;整棵树无 .git(如临时目录)则退回 cwd
    cur = Path(yaml_path).resolve()
    for anc in [cur, *cur.parents]:
        if (anc / ".git").exists():
            return str(anc / ".env.skill")
    return str(Path.cwd() / ".env.skill")


def run(yaml_path: str, reports_dir: str = "test_reports") -> int:
    decl = schema.load(yaml_path)
    if decl.credentials:                          # §12.1:按 toml section 名加载凭据 → 注入 env(无 credentials 则空操作)
        resolver.inject_credentials(decl, _env_skill_path(yaml_path))
    rep = runner.run_declaration(decl)
    if reporter.should_emit_md(rep):
        target = Path(reports_dir) / f"sentinel_{decl.sentinel}_anomaly.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(reporter.render(rep), encoding="utf-8")
        print(f"[sentinel:{decl.sentinel}] 检出异常 → 落盘 {target}")
        return 1
    print(reporter.render(rep))                  # 全 pass:一行 ok(静默,约零 token)
    return 0


def main(argv=None) -> int:
    argv = list(argv or sys.argv[1:])
    if len(argv) < 2:
        print("用法: python -m sentinel_engine run <yaml> | register <yaml>", file=sys.stderr)
        return 2
    cmd, yaml_path = argv[0], argv[1]
    if cmd == "run":
        return run(yaml_path)
    if cmd == "register":
        register.register(yaml_path)
        return 0
    print(f"未知命令: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

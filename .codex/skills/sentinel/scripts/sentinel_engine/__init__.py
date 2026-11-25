"""sentinel 通用巡检引擎 (design v1.2)。

声明驱动巡检引擎:yaml 声明 → 薄 prompt(CronCreate)→ 本引擎确定性执行
(resolve→execute→extract→assert→emit)→ 全 pass 静默 / 有 fail 落 md 归因。

引擎是 sentinel skill 的功能核心,自包含于 SKILL 内(发布即可用,不依赖外部包)。
依赖:仅 stdlib + PyYAML(yaml 声明解析)。Python 3.10+(3.10 手写 toml 子集,3.11+ 可换 tomllib)。

入口:`python -m sentinel_engine run <yaml>` / `python -m sentinel_engine register <yaml>`。
"""
__version__ = "1.0.0"

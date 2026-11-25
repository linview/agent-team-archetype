"""凭据解析与注入 (design v1.2 §12.1 凭据边界 —— .env.skill toml section 版)。

铁律:凭据值经 .env.skill(toml)→ os.environ → 探针读取**使用**;
绝不作为 prompt 文本 / 声明内联值 / scheduled_tasks.json / reporter 输出 / subprocess stderr。

v1.2:凭据统一存 .env.skill toml,按 section 分区;声明 credentials 写 **section 名**
(如 {ssh: ssh}),resolver 运行时从 .env.skill 取对应 section 的 KV 注入 env。
section 内可带 desc 字段描述(§12.1,不作为凭据注入)。

分层:
- schema 层只验 credentials 值是 section 名(非空 str);
- 本模块(resolver)运行时加载 .env.skill toml、按 section 名取 KV 注入 env;
- assert_no_secret_leak 是纯函数守卫,横跨 reporter md(含 error/signals)/ stderr 做不泄漏断言。

Python 3.10 无 tomllib(3.11+ stdlib),故手写 .env.skill 所需 toml 子集 parser
(支持 [section] / key=value(str/int/float/bool)/ # 注释)。3.11+ 可换 tomllib。
"""
from __future__ import annotations
import os
from pathlib import Path


def _strip_comment(value: str) -> str:
    """剥离行尾注释:仅当 # 在引号外时才切。

    STORY-1-06 #1:引号内的 # 是值的一部分(如 token="ab#cd"),
    不能当注释截断。引号成对识别(单/双引号互不嵌套),引号内 # 原样保留。
    """
    in_single = in_double = False
    for i, ch in enumerate(value):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return value[:i]
    return value


def _coerce(v: str):
    """toml 子集值类型推断:str / int / float / bool。"""
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    if v in ("true", "false"):
        return v == "true"
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v


def parse_toml_subset(text: str) -> dict:
    """极简 toml reader:[section] + key=value + # 注释,忽略空行。

    非 [section] 下的顶层 KV 归入 "" 键(保留兼容,本引擎不用)。
    生产可换 tomllib(3.11+);3.10 无 tomllib,故手写所需子集。
    """
    sections: dict = {}
    cur = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            cur = line[1:-1].strip()
            sections.setdefault(cur, {})
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = _strip_comment(v).strip()  # 仅切引号外 # (STORY-1-06 #1:引号内 # 是值一部分)
        sections.setdefault(cur, {})[k] = _coerce(v)
    return sections


def load_toml(path) -> dict:
    """纯函数:读 .env.skill → {section: {key: value}}(经 toml 子集 parser)。文件不存在抛 FileNotFoundError。"""
    return parse_toml_subset(Path(path).read_text(encoding="utf-8"))


def inject_credentials(declaration, env_skill_path) -> dict:
    """副作用步:加载 .env.skill toml → 按 declaration.credentials 的 **section 名**
    取 KV → 注入 os.environ(desc 字段跳过)。

    declaration.credentials = {ref_name: section_name}(section 名,非文件路径)。
    返回注入摘要(仅 key 名列表,**不含值**)——供审计与 H5 不泄漏断言。
    section 不存在抛 KeyError(运行时把关,§12.1)。
    """
    data = load_toml(env_skill_path)
    injected = {}
    for ref_name, section_name in (declaration.credentials or {}).items():
        section = data.get(section_name)
        if not isinstance(section, dict):
            raise KeyError(f".env.skill 无 section [{section_name}](credentials.{ref_name})")
        pairs = {k: str(v) for k, v in section.items() if k != "desc"}
        for k, v in pairs.items():
            os.environ[k] = v
        injected[ref_name] = sorted(pairs.keys())
    return injected


def assert_no_secret_leak(text: str, secret_values) -> tuple:
    """纯函数守卫:断言 text 不含任何凭据值。

    返回 (clean: bool, offender: str)。H5 核心:覆盖
    薄 prompt / scheduled_tasks.json / reporter md(含 ProbeResult.error / signals)/ subprocess stderr。
    规避空值与过短值(<4 字符,防常见短串误报);strip 后大小写敏感比对。
    """
    for secret in secret_values:
        s = str(secret).strip() if secret else ""
        if len(s) < 4:
            continue
        if s in text:
            return False, s
    return True, ""

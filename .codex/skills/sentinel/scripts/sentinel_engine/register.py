"""注册器 (design v1.2 §11.1 / §10.2 执行模型铁律)。

生成两样东西:
1. **薄 prompt**(仅触发指令:运行 sentinel run <yaml>;全 pass 静默 / 有 fail 落盘归因)
2. **scheduled_tasks.json mock**(CronCreate 唤醒时携带的载荷)

铁律:薄 prompt 与 json 都**不含 probe 逻辑**(逻辑在确定性引擎里)、**不含凭据值**(§12.1)。
这是 H1 的核心——LLM/CronCreate 只负责"触发",不负责"推理"。

assert_prompt_is_thin:薄 prompt 自检(字符白名单全集,承接 POC H1 enhancement)——
遍历 PROBE_TYPES ∪ ASSERT_OPS 全集断言都不在 prompt,防止未来回退为厚 prompt。
"""
from __future__ import annotations
import json
from pathlib import Path
from sentinel_engine import schema

THIN_PROMPT_TEMPLATE = (
    "运行 sentinel run {yaml};"
    "全 pass 则静默(打印一行 ok),有 fail 则落盘 md 归因;"
    "不在本 prompt 内做 probe 推理或读取凭据。"
)


def build_thin_prompt(yaml_path: str) -> str:
    """薄 prompt:仅触发指令,不含 probe 逻辑/凭据。"""
    return THIN_PROMPT_TEMPLATE.format(yaml=yaml_path)


def assert_prompt_is_thin(prompt: str) -> None:
    """薄 prompt 自检:不含任何探针类型名 / 断言 op(防止回退为厚 prompt)。

    字符白名单全集(覆盖 PROBE_TYPES ∪ ASSERT_OPS),非封闭抽样。
    register 编译期可调用本函数做断言;违反则抛 AssertionError。
    """
    forbidden = schema.PROBE_TYPES | schema.ASSERT_OPS
    found = [t for t in forbidden if t in prompt]
    if found:
        raise AssertionError(f"薄 prompt 含 probe 逻辑 token: {found}")


def build_scheduled_task(yaml_path: str, declaration) -> dict:
    """scheduled_tasks.json mock 单条:CronCreate 唤醒载荷。

    只携带 cron + 薄 prompt + yaml 路径 + credentials ref 名(仅 key,无值/无文件路径)。
    """
    return {
        "yaml": yaml_path,
        "cron": declaration.schedule,
        "prompt": build_thin_prompt(yaml_path),
        "credentials_refs": sorted((declaration.credentials or {}).keys()),
    }


def register(yaml_path: str, out_dir: str = "test_reports/sentinel"):
    """注册:校验声明 → 写薄 prompt + 合并 scheduled_tasks.json mock。返回 (prompt_path, json_path)。

    out_dir 默认 test_reports/sentinel(register 产物是过渡性文件,统一归
    test_reports/ 不污染项目根;显式传参可覆盖)。
    """
    decl = schema.load(yaml_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    prompt = build_thin_prompt(yaml_path)
    assert_prompt_is_thin(prompt)  # 自检:防回退为厚 prompt
    prompt_path = out / f".sentinel_prompt_{decl.sentinel}.txt"
    json_path = out / "scheduled_tasks.json"
    prompt_path.write_text(prompt, encoding="utf-8")
    # 合并:同 yaml 替换,不同 yaml 追加(模拟多 sentinel 共存)
    try:
        tasks = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else []
    except Exception:
        tasks = []
    if not isinstance(tasks, list):
        tasks = []
    tasks = [t for t in tasks if t.get("yaml") != yaml_path] + [build_scheduled_task(yaml_path, decl)]
    json_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[register] 薄 prompt   → {prompt_path}")
    print(f"[register] scheduled  → {json_path}")
    return prompt_path, json_path

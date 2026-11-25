"""报告器 (design v1.2 §13 LLM 角色边界)。

- 全 pass → 静默:返回一行 ok(约零 token,LLM 无需介入归因)。
- 有 fail/error → 落 md:供 LLM 做异常归因;输出确定性,无随机源。

§12.1:输出绝不含凭据值——只用 probe 名 / target / signal / assert detail,
不打印 ProbeResult.raw(body 可能含敏感内容)。H5 端到端守卫见 test_reporter。
"""
from __future__ import annotations


def should_emit_md(report) -> bool:
    """§13:仅 fail/error 才落 md(触发 LLM 归因);全 pass 静默。"""
    return not report.all_pass


def render(report) -> str:
    if report.all_pass:
        # 全 pass 静默:一行 ok,LLM 无需归因
        names = ",".join(o.type for o in report.outcomes)
        return f"[sentinel:{report.sentinel}] OK ({len(report.outcomes)} probes: {names})"
    lines = [f"# Sentinel 异常报告: {report.sentinel}", ""]
    for o in report.outcomes:
        icon = {"pass": "✅", "fail": "❌", "error": "⚠️"}[o.status]
        lines.append(f"## {icon} {o.type} `{o.target}` — {o.status}")
        lines.append("")
        if o.status == "error":
            lines.append(f"- 执行失败: {o.detail}")
        else:
            ar = o.assert_result
            lines.append(f"- 断言: `{ar.op}` on `{ar.value_key}`")
            lines.append(f"- 详情: {ar.detail}")
        lines.append(f"- signals: `{o.signals}`")
        lines.append("")
    return "\n".join(lines)

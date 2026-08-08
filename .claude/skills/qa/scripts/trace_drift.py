#!/usr/bin/env python3
"""
trace_drift.py — @trace 标注的"设计↔测试"漂移检测器(qa skill 工具)

消费方:/qa 定期**分层用例 review** —— 看 design 版本/意图是否变更,
       进而做 design↔test 内容 review,决定用例 update/retire/add。

纯静态扫描:
  - regex 扫 tests/**/*.py 的 @pytest.mark.trace(...) / @trace(...) 调用,抽 kwargs;
  - 对 design 锚:对比 pin 版本 vs docs/design 下当前版本(归档规则:旧版进 archive/),
    并在当前版本文档里校验 #章节 是否仍存在;
  - 对 story 定位符:检查 story 文件 status 是否 CANCELLED(用例应随 story 退役)。
  - 不开 pytest、不连 PG/K8s,环境安全。

四态:
  ✅ 同步        pin 版本==当前版本,且章节仍在
  ⚠️ 版本漂移   pin 版本 < 当前版本(design 已演进,用例可能过期)
  ⚠️ 章节漂移   pin 版本==当前,但 #章节 在当前文档找不到(重排/改名/删除)
  🔴 悬空       doc 族消失,或 story 状态为 CANCELLED

用法:
  python trace_drift.py [--test-dir DIR] [--design-dir DIR] [--scrum-dir DIR] [-o OUT]

默认路径指向 examples/backend(仓库内实例化)。报告输出到 test_reports/(遵循全局临时文件规范)。
"""

import argparse
import os
import re
import sys
from pathlib import Path

# 捕获 @pytest.mark.trace(...) / @trace(...) 块 + 紧随的 def test_xxx
_TRACE_BLOCK_RE = re.compile(
    r"@(?:pytest\.mark\.)?trace\(\s*(?P<kwargs>[^)]*?)\)\s*\n\s*def\s+(?P<test>test_\w+)",
    re.DOTALL,
)
# 从 kwargs 文本抽 key="value"
_KV_RE = re.compile(r'(?P<k>story|epic|endpoint|ac|design|note)\s*=\s*"(?P<v>[^"]*)"')
# design 锚版本:stem_vX.Y
_DESIGN_VER_RE = re.compile(r"_v(?P<v>\d+\.\d+)$")
_DESIGN_PREFIX_RE = re.compile(r"^(?P<p>.+)_v\d+\.\d+$")
# doc 文件名版本: stem_vX.Y.md
_DOC_FILE_VER_RE = re.compile(r"_v(?P<v>\d+\.\d+)\.md$")
# story 文件: STORY-6-02 -> story-6-02-*.md
_STORY_ID_RE = re.compile(r"STORY-(?P<epic>\d+)-(?P<seq>\d+)")

# 不含 UT:UT 不使用 @trace(真实来源=代码符号,追溯交 spec-xchecker CT 层)。
# 与 trace_framework.VALID_AC 保持一致(本检测器实际按 design 锚漂移分类,不强校验 ac 枚举)。
VALID_AC = {"API", "SIT", "E2E", "UAT"}


def _parse_version(s):
    """'4.2' -> (4, 2)。"""
    try:
        a, b = s.split(".")
        return (int(a), int(b))
    except (ValueError, AttributeError):
        return (0, 0)


def scan_trace_markers(test_dir):
    """扫 test_dir 下所有 *.py,返回 [{test, story, epic, endpoint, ac, design, note, file}]。"""
    found = []
    for py in sorted(Path(test_dir).rglob("*.py")):
        try:
            text = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in _TRACE_BLOCK_RE.finditer(text):
            kvs = dict(_KV_RE.findall(m.group("kwargs")))
            found.append({
                "test": m.group("test"),
                "file": str(py),
                **{k: kvs.get(k) for k in ("story", "epic", "endpoint", "ac", "design", "note")},
            })
    return found


def _current_design_doc(design_dir, stem):
    """在 design_dir(非 archive)下找该 doc 族当前版本文件。

    返回 (current_version_str, current_file_path) 或 (None, None)。
    """
    if stem.endswith(".md"):
        stem = stem[:-3]
    pm = _DESIGN_PREFIX_RE.match(stem)
    prefix = pm.group("p") if pm else stem
    candidates = []
    for p in Path(design_dir).rglob(f"{prefix}_v*.md"):
        if "archive" in p.parts:  # 旧版本归档,不作为"当前"
            continue
        vm = _DOC_FILE_VER_RE.search(p.name)
        if vm:
            candidates.append((_parse_version(vm.group("v")), vm.group("v"), p))
    if not candidates:
        return (None, None)
    candidates.sort(key=lambda x: x[0])
    return (candidates[-1][1], candidates[-1][2])


def _section_exists(doc_path, section):
    """#章节 是否在文档里作为标题出现(子串匹配,容错 emoji/编号)。"""
    try:
        text = doc_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    sec = section.strip()
    for line in text.splitlines():
        if line.lstrip().startswith("#") and sec and sec in line:
            return True
    return False


def _story_status(scrum_dir, story_id):
    """读 story 文件 status;不存在返回 None。"""
    sm = _STORY_ID_RE.match(story_id or "")
    if not sm:
        return None
    epic, seq = sm.group("epic"), sm.group("seq")
    for p in Path(scrum_dir, "story").glob(f"story-{epic}-{seq}-*.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        vm = re.search(r"^status:\s*(?P<s>\S+)", text, re.MULTILINE)
        if vm:
            return vm.group("s").strip()
    return None


def classify(entry, design_dir, scrum_dir):
    """分类一条 trace 标注为四态之一。返回 (state, detail, advice)。"""
    design = entry.get("design")
    story = entry.get("story")

    # 生命周期:story 退役 → 用例应退役
    if story:
        st = _story_status(scrum_dir, story)
        if st and st.upper() == "CANCELLED":
            return ("dangling", f"story {story} 状态={st}", "用例随 story 退役(RETIRE)")

    # 无 design 锚(UT / 用户层 epic-only):不在漂移检测范围
    if not design:
        loc = story or entry.get("epic") or entry.get("endpoint") or entry.get("note")
        return ("no_design", f"定位符={loc}", "用户层/符号锚,无 design 版本锚(正常)")

    stem, _, section = design.partition("#")
    cur_ver, cur_doc = _current_design_doc(design_dir, stem)
    if cur_ver is None:
        return ("dangling", f"doc 族 {stem} 在 {design_dir} 消失", "源文档已删除(RETIRE 或重指向)")

    pm = _DESIGN_VER_RE.search(stem)
    pin_ver = pm.group("v") if pm else None
    if pin_ver and _parse_version(pin_ver) < _parse_version(cur_ver):
        return ("version_drift",
                f"pin v{pin_ver} < 当前 v{cur_ver}",
                "design 已演进 → 复核内容是否仍有效(UPDATE/RETIRE)")

    if section and not _section_exists(cur_doc, section):
        return ("section_drift",
                f"#章节 '{section}' 在当前 v{cur_ver} 文档找不到",
                "章节重排/改名/删除 → 重新对齐锚(UPDATE)")

    return ("sync", f"pin={pin_ver} 当前={cur_ver} 章节='{section}'", "已对齐,无需动作")


STATE_META = {
    "dangling":       ("🔴 悬空",     0),
    "version_drift":  ("⚠️ 版本漂移", 1),
    "section_drift":  ("⚠️ 章节漂移", 2),
    "sync":           ("✅ 同步",     3),
    "no_design":      ("ℹ️ 无 design 锚(正常)", 4),
}


def main():
    ap = argparse.ArgumentParser(description="@trace 设计↔测试漂移检测器")
    ap.add_argument("--test-dir", default="examples/backend/tests",
                    help="测试目录(默认 examples/backend/tests)")
    ap.add_argument("--design-dir", default="examples/backend/docs/design",
                    help="设计文档目录(默认 examples/backend/docs/design)")
    ap.add_argument("--scrum-dir", default="examples/backend/docs/scrum",
                    help="scrum 文档目录(默认 examples/backend/docs/scrum)")
    ap.add_argument("-o", "--out", default="test_reports/trace_drift_report.md",
                    help="报告输出路径(默认 test_reports/trace_drift_report.md)")
    args = ap.parse_args()

    if not Path(args.test_dir).is_dir():
        print(f"❌ test-dir 不存在: {args.test_dir}", file=sys.stderr)
        return 2

    entries = scan_trace_markers(args.test_dir)
    if not entries:
        print(f"ℹ️ 在 {args.test_dir} 未发现 @trace 标注(漏标检测不在本期范围)。", file=sys.stderr)

    results = []
    for e in entries:
        state, detail, advice = classify(e, args.design_dir, args.scrum_dir)
        ac = e.get("ac") or "?"
        loc = e.get("story") or e.get("epic") or e.get("endpoint") or e.get("note") or "—"
        results.append({**e, "state": state, "detail": detail, "advice": advice,
                        "ac": ac, "loc": loc})

    results.sort(key=lambda r: STATE_META[r["state"]][1])

    # 计数
    counts = {k: 0 for k in STATE_META}
    for r in results:
        counts[r["state"]] += 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# @trace 设计↔测试 漂移检测报告",
        "",
        f"- 测试目录: `{args.test_dir}`",
        f"- 设计目录: `{args.design_dir}` | Scrum 目录: `{args.scrum_dir}`",
        f"- 标注用例总数: **{len(results)}**",
        "",
        "## 摘要",
        "",
        "| 态 | 数量 | 说明 |",
        "|---|---|---|",
        "| 🔴 悬空 | %d | doc 族消失或 story CANCELLED |" % counts["dangling"],
        "| ⚠️ 版本漂移 | %d | design 已演进,用例可能过期 |" % counts["version_drift"],
        "| ⚠️ 章节漂移 | %d | 章节重排/改名/删除 |" % counts["section_drift"],
        "| ✅ 同步 | %d | 已对齐 |" % counts["sync"],
        "| ℹ️ 无 design 锚 | %d | 用户层/符号锚,正常 |" % counts["no_design"],
        "",
        "> 消费方:/qa 分层用例 review。按态排序(🔴→⚠️→✅→ℹ️),对每条做内容 review,决定 UPDATE/RETIRE/ADD。",
        "",
    ]
    cur = None
    for r in results:
        if r["state"] != cur:
            cur = r["state"]
            lines += ["", f"## {STATE_META[cur][0]}", "",
                      "| 用例 | ac | 定位符 | 检测详情 | 建议 |", "|---|---|---|---|---|"]
        lines.append(
            f"| `{r['test']}` | {r['ac']} | {r['loc']} | {r['detail']} | {r['advice']} |"
        )
    lines += [
        "",
        "---",
        "*本报告由 `.claude/skills/qa/scripts/trace_drift.py` 静态生成;未连任何外部环境(PG/K8s)。*",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")

    print(f"✅ 报告已生成: {out}")
    print(f"   标注用例 {len(results)} 条 | "
          f"🔴{counts['dangling']} ⚠️版本{counts['version_drift']} "
          f"⚠️章节{counts['section_drift']} ✅{counts['sync']} ℹ️{counts['no_design']}")
    # 有 actionable 漂移时,exit=1 便于 CI/review 流程感知
    actionable = counts["dangling"] + counts["version_drift"] + counts["section_drift"]
    return 1 if actionable else 0


if __name__ == "__main__":
    sys.exit(main())

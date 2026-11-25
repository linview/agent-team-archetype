#!/usr/bin/env python3
"""设计文档成稿自检——结构机械项拦截器（arch skill v2.5 配套）。

检查项（机械可判定部分，语义 review 五问仍由 AI/审查者执行）：
  1. YAML frontmatter 必填字段（version/status/created）与版本三处一致（文件名/frontmatter/标题）
  2. TOC 存在性（主文档 >100 行必须提供）
  3. 标题编号纪律：单调不回退、无复用、无占位编号（如 "5.x"）、层级与编号深度一致
  4. 相对链接目标存在；引用不入库路径（test_reports/）拦截
  5. TOC 条目与实际标题锚点一致性（best-effort，警告级）

用法：
  python doc_structure_check.py <doc.md> [more.md ...] [--json]

退出码：存在 FAIL → 1；仅 WARN/通过 → 0。
"""

import json
import os
import re
import sys

FRONTMATTER_REQUIRED = ("version", "status", "created")
TOC_THRESHOLD_LINES = 100  # 主文档超过此行数必须有 TOC
TOC_SCAN_WINDOW = 80       # 正文前 N 行内寻找 TOC
CELL_HINT = 200            # 表格单元格散文提示阈值（提示级，不阻断）


def strip_code_fences(text):
    """剥离 ``` 围栏块，避免代码/SQL/mermaid 内容干扰标题与链接扫描。"""
    lines, out, in_fence = text.split("\n"), [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def parse_frontmatter(text):
    """返回 (metadata dict, error or None)。naive 解析：顶层 key: value / key: 列表项。"""
    if not text.startswith("---"):
        return {}, "缺少 YAML frontmatter（--- 段）——版本元数据必须 frontmatter 化，不得以正文形式堆叠在头部"
    parts = text.split("\n---", 1)
    block = parts[0][3:].strip("\n")
    meta, current_key = {}, None

    def unquote(val):
        # 去包裹引号（YAML 字符串常带 "..." / '...'）
        return val[1:-1] if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'" else val

    for raw in block.split("\n"):
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        if raw.startswith(("  ", "-", "\t")) and current_key:
            meta.setdefault(current_key, []).append(unquote(raw.strip().lstrip("- ").strip()))
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", raw)
        if m:
            current_key = m.group(1)
            val = unquote(m.group(2).strip())
            meta[current_key] = [] if val == "" else val
        else:
            current_key = None
    return meta, None


NUM_RE = re.compile(r"^(\d+(?:\.\d+)*)([a-z]?)\b\.?\s*(.*)$")
PLACEHOLDER_RE = re.compile(r"^\d+(?:\.\d+)*\.[xX*?]\b")
SENTINEL = "__PLACEHOLDER__"


def extract_headings(body):
    """返回 [(line_no, level, num_token|None, title)]，按文档顺序。"""
    result = []
    for i, line in enumerate(body.split("\n"), 1):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not m:
            continue
        level, title = len(m.group(1)), m.group(2).strip()
        if PLACEHOLDER_RE.match(title):
            # 占位编号（如 "### 5.x ..."）——NUM_RE 只能取到 "5"，必须在标题层拦截
            result.append((i, level, SENTINEL, title))
            continue
        nm = NUM_RE.match(title)
        token = (nm.group(1) + nm.group(2)) if nm else None
        result.append((i, level, token, title))
    return result


def check_numbering(headings, errors, warnings):
    seen = {}
    last_top = None
    last_sibling = {}  # 父路径 -> 最后一个同级子编号，同级编号须单调不回退
    for line_no, level, token, title in headings:
        if token is None:
            continue
        # 占位编号（如 5.x / 2.*）
        if token == SENTINEL:
            errors.append(f"L{line_no}: 占位编号未落定（{title[:40]}）")
            continue
        parts = token.rstrip("abcdefghijklmnopqrstuvwxyz").split(".")
        depth = len(parts)
        # 层级与编号深度一致：depth d → markdown level d+1（# 为文档标题，不编号）
        expected_level = depth + 1
        if level != expected_level:
            errors.append(
                f"L{line_no}: 标题层级与编号深度不一致——「{token}」为 {depth} 级编号，"
                f"应为 {'#' * expected_level}（H{expected_level}），实际 {'#' * level}（H{level}）"
            )
        # 顶层编号单调不回退（§8 殿后在 §11 后即在此拦截）
        top = int(parts[0])
        if depth == 1:
            if last_top is not None and top <= last_top:
                errors.append(
                    f"L{line_no}: 顶层章节编号回退/复用——「{token}」出现在 {last_top} 之后"
                )
            last_top = top
        else:
            # 同级编号单调不回退（3.1.1 出现在 3.1.2 之后即在此拦截）
            # 同数不同后缀（3.1.0 / 3.1.0a）视为变体，不算回退
            parent = tuple(parts[:-1])
            num = int(parts[-1])
            prev = last_sibling.get(parent)
            if prev is not None and num < prev:
                errors.append(
                    f"L{line_no}: 同级编号回退——「{token}」小于同级前序编号 {prev}"
                )
            last_sibling[parent] = max(num, prev) if prev is not None else num
        key = token
        if key in seen:
            errors.append(f"L{line_no}: 章节编号复用「{token}」（首次见 L{seen[key]}）")
        else:
            seen[key] = line_no


def github_slug(title):
    """best-effort GitHub 风格锚点：去标点保留 CJK/字母/数字/连字符，空格转连字符，小写。"""
    s = title.strip().lower()
    s = re.sub(r"[^\w一-鿿　-〿\- ]", "", s)
    s = re.sub(r"\s", "-", s)
    return s


def check_toc(body, headings, total_lines, errors, warnings):
    if total_lines <= TOC_THRESHOLD_LINES:
        return
    window = "\n".join(body.split("\n")[:TOC_SCAN_WINDOW])
    has_toc_heading = re.search(r"^#{1,4}.*(目录|TOC)", window, re.M) is not None
    anchor_count = len(re.findall(r"\]\(#", window))
    if not (has_toc_heading or anchor_count >= 5):
        errors.append(
            f"文档 {total_lines} 行 > {TOC_THRESHOLD_LINES} 行，正文头部未见 TOC（目录标题或锚点链接列表）"
        )
        return
    # TOC 条目与标题锚点一致性（best-effort，警告级）
    slugs = {github_slug(t) for _, _, _, t in headings}
    for m in re.finditer(r"\]\(#([^)]+)\)", window):
        anchor = m.group(1)
        if anchor and anchor not in slugs:
            warnings.append(f"TOC 锚点 #{anchor} 未匹配到任何标题（best-effort 校验，请人工确认）")


LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def check_links(text, doc_dir, errors, warnings):
    for m in LINK_RE.finditer(text):
        target = m.group(2)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path = target.split("#")[0]
        if not path:
            continue
        norm = os.path.normpath(os.path.join(doc_dir, path))
        if "test_reports" in norm.split(os.sep):
            errors.append(f"链接指向不入库路径（gitignored）「{target}」——结论须先迁 analysis/ 再引用")
            continue
        if not os.path.exists(norm):
            errors.append(f"链接目标不存在「{target}」→ 解析为 {norm}")


def check_doc(path, emit_json=False):
    errors, warnings = [], []
    with open(path, encoding="utf-8") as f:
        text = f.read()
    total_lines = text.count("\n") + 1
    body = strip_code_fences(text)

    # 1. frontmatter
    meta, fm_err = parse_frontmatter(text)
    if fm_err:
        errors.append(fm_err)
    else:
        for key in FRONTMATTER_REQUIRED:
            if key not in meta:
                errors.append(f"frontmatter 缺少必填字段「{key}」")
        fname_ver = re.search(r"_v(\d+(?:\.\d+)*)", os.path.basename(path))
        if fname_ver and "version" in meta:
            doc_ver = re.sub(r"^v", "", str(meta["version"]).strip())
            if doc_ver != fname_ver.group(1):
                errors.append(
                    f"版本三处不一致——文件名 v{fname_ver.group(1)} vs frontmatter「{meta['version']}」"
                )
        # 标题版本（正文第一个 H1）
        h1 = re.search(r"^#\s+(.*)$", body, re.M)
        if h1 and "version" in meta:
            hv = re.search(r"v(\d+(?:\.\d+)*)", h1.group(1))
            dv = re.sub(r"^v", "", str(meta["version"]).strip())
            if hv and hv.group(1) != dv:
                errors.append(
                    f"版本三处不一致——frontmatter v{dv} vs 正文标题「{hv.group(1)}」（{h1.group(1)[:30]}）"
                )

    # 2/3. 标题编号 + TOC
    headings = extract_headings(body)
    check_numbering(headings, errors, warnings)
    check_toc(body, headings, total_lines, errors, warnings)

    # 4. 链接
    check_links(body, os.path.dirname(os.path.abspath(path)), errors, warnings)

    # 提示级：超大表格单元格（散文误置信号，人工判断）
    for i, line in enumerate(text.split("\n"), 1):
        if line.startswith("|") and len(line) > CELL_HINT * 2:
            warnings.append(f"L{i}: 表格行超长（{len(line)} 字符）——疑似散文误置入表格单元格，请人工判断")

    return {
        "file": path,
        "total_lines": total_lines,
        "errors": errors,
        "warnings": warnings,
        "result": "FAIL" if errors else ("WARN" if warnings else "PASS"),
    }


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    emit_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        return 2
    reports = [check_doc(p) for p in args]
    if emit_json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        for r in reports:
            print(f"== {r['file']} —— {r['result']}（{r['total_lines']} 行）")
            for e in r["errors"]:
                print(f"  [FAIL] {e}")
            for w in r["warnings"]:
                print(f"  [WARN] {w}")
            if not r["errors"] and not r["warnings"]:
                print("  全部机械检查项通过")
    return 1 if any(r["errors"] for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())

"""
trace_framework.py — @trace 主追溯 marker 框架(qa skill 规范参考代码)

这是 qa skill 的可复制粘贴框架代码。复制本文件到项目后即可使用:
  - trace(**kwargs)        marker 工厂(对 pytest.mark.trace 的薄封装,统一入口)
  - validate_trace_items() pytest_collection_modify_items 校验 hook(给 marker 牙齿)

落地三步:
  1. pytest.ini 的 [pytest] markers = 块加一行(见 pytest_trace_marker.ini.snippet)
  2. 把本文件放进项目(如 tests/trace_framework.py)
  3. conftest.py:
       from trace_framework import validate_trace_items
       def pytest_collection_modifyitems(config, items):
           validate_trace_items(config, items)

设计要点(详见 references/test_traceability.md):
  - 两维度:定位符(查阅·空间)+ 版本化源锚(漂移检测·时间)
  - 定位符 story/epic/endpoint 三选一(一测一主功能锚)
  - ac 必须在 {API,SIT,E2E,UAT}(不含 UT——UT 不使用 @trace)
  - design 源锚格式:<doc_stem>_vX.Y#<真实章节>(版本借文件名,#后为真实标题)
  - note:hotfix/探索性退化口(有 note 时允许无定位符)
  - 默认 warning;设环境变量 TRACE_STRICT=1 升为收集期 fail
"""

import os
import re
import warnings

import pytest

# 层归属枚举(对齐 pm ac_testing_strategy.md 的 [LAYER] AC 标签)
# 注:不含 UT——UT 的唯一真实来源是代码符号(被测函数本身),非设计文档;UT↔代码的
# 追溯交 spec-xchecker CT 层(symbol↔test_),不进 @trace 通道。详见 test_traceability.md §3/§6。
VALID_AC = {"API", "SIT", "E2E", "UAT"}

# 定位符(三选一)
LOCATORS = ("story", "epic", "endpoint")

# ============================================================
# 元不变式:VALID_AC ↔ SSOT 语义对齐(防 v7.2 UT 偏差重演)
# ------------------------------------------------------------
# @trace 能表达的"锚"只有:定位符(story/epic/endpoint)+ design 源锚。一个 ac 值能进
# VALID_AC,当且仅当它的唯一真实来源(SSOT)落在上述锚体系内。UT 的 SSOT 是代码符号
# (被测函数本身),锚体系覆盖不到 → 不在 VALID_AC,追溯交 spec-xchecker CT 层。
# 下表把这条原则焊进自测:改 VALID_AC 不同步改两张表 → __main__ 自测矛盾报警。
# ============================================================
# 合法层:SSOT 落在 @trace 锚体系内 → 可进 VALID_AC
_AC_SSOT = {
    "API": "endpoint 契约 → @trace(endpoint + design)",
    "SIT": "服务层设计文档 → @trace(story + design)",
    "E2E": "PRD/Epic(用户旅程)→ @trace(epic)",
    "UAT": "PRD/Epic → @trace(epic)",
}
# 排除层:SSOT 落不在锚体系内 → 禁止进 VALID_AC(带理由,防悄悄加回)
_AC_EXCLUDED = {
    "UT": "SSOT=代码符号(被测函数本身),非 story/epic/endpoint/design;追溯交 spec-xchecker CT 层",
}


def _assert_validac_ssot_alignment():
    """VALID_AC 必须与 _AC_SSOT 完全一致,且与 _AC_EXCLUDED 无交集。

    新增/删除 ac 值不同步改这两张表 → 断言失败,强制作者复核"机制↔原则语义对齐"。
    """
    valid, ssot = set(VALID_AC), set(_AC_SSOT)
    assert valid == ssot, (
        f"VALID_AC({sorted(valid)}) != 合法层映射({sorted(ssot)}):"
        f" 多出 {sorted(valid - ssot) or '∅'} / 缺少 {sorted(ssot - valid) or '∅'}。"
        f" 新增 ac 值须先确认其 SSOT 被 @trace 锚体系覆盖(见 _AC_SSOT / _AC_EXCLUDED)。"
    )
    bad = valid & set(_AC_EXCLUDED)
    assert not bad, (
        "VALID_AC 含不应使用 @trace 的层: "
        + "; ".join(f"{k} → {v}" for k, v in _AC_EXCLUDED.items() if k in bad)
    )


# design 源锚:<ascii stem>_vX.Y#<章节>   例: service_layer_architecture_v4.2#查询路由策略
_DESIGN_RE = re.compile(r"^[A-Za-z0-9_./-]+_v\d+\.\d+#.+$")

# seq 强制两位(02d):与 pm story_template 的 STORY-{epic}-{seq:02d} 对齐,
# 也与 trace_drift 的 story 文件 glob(story-{epic}-{seq}-*.md)假设一致 —— 避免
# 校验放行 STORY-6-3 而检测器漏判 CANCELLED 的不一致。
_STORY_RE = re.compile(r"^STORY-\d+-\d{2}$")
_EPIC_RE = re.compile(r"^EPIC-\d+$")


def trace(**kwargs):
    """@trace 主追溯 marker 工厂。

    等价于 pytest.mark.trace(**kwargs),仅作统一入口。也可直接用 @pytest.mark.trace。

    示例:
        @trace(story="STORY-15-23", ac="SIT",
               design="service_layer_architecture_v4.2#查询路由策略")
        @trace(epic="EPIC-6", ac="UAT")
        @trace(note="hotfix-2026-07-29", ac="API")
    """
    return pytest.mark.trace(**kwargs)


def _validate_kwargs(kwargs):
    """校验单个 @trace 的 kwargs,返回问题描述列表(空=通过)。"""
    issues = []
    has_note = bool(kwargs.get("note"))
    present = [k for k in LOCATORS if kwargs.get(k)]

    if has_note:
        # 退化口(hotfix/探索性):允许无定位符,但仍只能 ≤1 个
        if len(present) > 1:
            issues.append(f"note 模式下定位符应 ≤1,实有 {present}")
    else:
        if len(present) == 0:
            issues.append("缺定位符(story/epic/endpoint 之一);若无 story 请用 note 退化口")
        elif len(present) > 1:
            issues.append(f"定位符必须唯一(一测一主功能锚),现有 {present}")

    ac = kwargs.get("ac")
    if ac == "UT":
        # UT 不应使用 @trace:UT 真实来源是代码符号(被测函数本身),非设计文档;
        # UT↔代码的追溯由 spec-xchecker CT 层(symbol↔test_)负责,不经过 @trace。
        issues.append(
            "ac='UT': UT 不应使用 @trace——UT 的唯一真实来源是代码符号(被测函数本身),"
            "非设计文档;UT↔代码的追溯由 spec-xchecker CT 层(symbol↔test_)负责。"
            "请移除本用例的 @trace 标注。"
        )
    elif ac not in VALID_AC:
        issues.append(f"ac={ac!r} 不在枚举 {sorted(VALID_AC)}")

    design = kwargs.get("design")
    if design and not _DESIGN_RE.match(design):
        issues.append(f"design={design!r} 格式应为 '<doc_stem>_vX.Y#<真实章节>'")

    story = kwargs.get("story")
    if story and not _STORY_RE.match(str(story)):
        issues.append(f"story={story!r} 格式应为 'STORY-<epic>-<seq:02d>'"
                      "(两位 seq,如 STORY-15-23,非 STORY-15-3)")

    epic = kwargs.get("epic")
    if epic and not _EPIC_RE.match(str(epic)):
        issues.append(f"epic={epic!r} 格式应为 'EPIC-<seq>'(如 EPIC-6)")

    return issues


def validate_trace_items(config, items):
    """pytest_collection_modifyitems hook:校验所有 @trace 标注。

    只检查带 trace marker 的用例;未标注的不报(漏标检测不在本期范围)。
    违规默认 warning;TRACE_STRICT=1 时收集期 fail。
    """
    strict = os.getenv("TRACE_STRICT") == "1"
    problems = []
    for item in items:
        marker = item.get_closest_marker("trace")
        if not marker:
            continue
        issues = _validate_kwargs(dict(marker.kwargs))
        for it in issues:
            problems.append(f"{item.nodeid}: {it}")

    if not problems:
        return

    msg = "[@trace] 校验发现问题(详见 qa/references/test_traceability.md):\n  - " + \
          "\n  - ".join(problems)
    if strict:
        raise pytest.UsageError(msg)
    warnings.warn(msg, stacklevel=2)


# ============================================================
# 自测:python trace_framework.py 可独立验证校验逻辑
# ============================================================
if __name__ == "__main__":
    class _Item:
        def __init__(self, nodeid, kwargs):
            self.nodeid = nodeid
            self._kwargs = kwargs

        def get_closest_marker(self, name):
            if name != "trace" or self._kwargs is None:
                return None

            class _M:
                kwargs = self._kwargs
            return _M()

    class _Cfg:
        pass

    # 元不变式:改 VALID_AC 必须同步改 _AC_SSOT/_AC_EXCLUDED,否则此处报警
    _assert_validac_ssot_alignment()
    print("[META] VALID_AC ↔ SSOT 对齐不变式: PASS")

    cases = [
        ("ok/sit", dict(story="STORY-6-02", ac="SIT",
                        design="service_layer_architecture_v4.2#查询路由策略")),
        ("ok/api", dict(endpoint="GET /api/v1/gpu-usage", ac="API",
                        design="api_design_v1.3#API 语法设计")),
        ("ok/uat", dict(epic="EPIC-6", ac="UAT")),
        ("ok/hotfix", dict(note="hotfix-2026-07-29", ac="API")),
        ("bad/双定位符", dict(story="STORY-6-02", epic="EPIC-6", ac="SIT")),
        ("bad/缺定位符", dict(ac="SIT")),
        ("bad/ac枚举", dict(story="STORY-6-02", ac="sit")),
        ("bad/design格式", dict(story="STORY-6-02", ac="SIT", design="service_layer.md#3.2")),
        ("bad/ut-not-allowed", dict(story="STORY-6-02", ac="UT")),
    ]
    for name, kw in cases:
        issues = _validate_kwargs(kw)
        tag = "PASS" if not issues else "FAIL"
        print(f"[{tag}] {name}: {issues or 'ok'}")

"""断言原语:5 确定性 + 1 有状态 (design v1.2 §7)。

每个原语是纯函数: (signal_value, assert_block) -> AssertionResult。
expect_trend 需历史快照(§7.2),本 Story 不实现(raise NotImplementedError)。
expect_regex 仅负极性(not_match 取反);正极性需求由 wizard 规避(§7.1)。
"""
from __future__ import annotations
from dataclasses import dataclass
import re


@dataclass
class AssertionResult:
    op: str
    value_key: str
    passed: bool
    detail: str = ""


def evaluate(signal_value, assert_block: dict) -> AssertionResult:
    """断言派发:据 op 调用对应原语。纯函数。"""
    op = assert_block.get("op")
    key = assert_block.get("value", "<unknown>")
    dispatch = {
        "expect_eq": _expect_eq,
        "expect_le": _expect_le,
        "expect_ge": _expect_ge,
        "expect_in": _expect_in,
        "expect_regex": _expect_regex,
        "expect_trend": _expect_trend,
    }
    fn = dispatch.get(op)
    if fn is None:
        return AssertionResult(op, key, False, f"未知 op: {op}")
    return fn(signal_value, assert_block, key)


def _expect_eq(v, block, key) -> AssertionResult:
    expected = block.get("equals")
    passed = v == expected
    return AssertionResult("expect_eq", key, passed,
                           f"{v!r} == {expected!r}" if passed else f"{v!r} != expected {expected!r}")


def _expect_le(v, block, key) -> AssertionResult:
    mx = block.get("max")
    try:
        passed = v <= mx
    except TypeError:
        return AssertionResult("expect_le", key, False, f"类型不可比较: {v!r} <= {mx!r}")
    return AssertionResult("expect_le", key, passed,
                           f"{v!r} <= {mx!r}" if passed else f"{v!r} > max {mx!r}")


def _expect_ge(v, block, key) -> AssertionResult:
    mn = block.get("min")
    try:
        passed = v >= mn
    except TypeError:
        return AssertionResult("expect_ge", key, False, f"类型不可比较: {v!r} >= {mn!r}")
    return AssertionResult("expect_ge", key, passed,
                           f"{v!r} >= {mn!r}" if passed else f"{v!r} < min {mn!r}")


def _expect_in(v, block, key) -> AssertionResult:
    allowed = block.get("in", [])
    passed = v in allowed
    return AssertionResult("expect_in", key, passed,
                           f"{v!r} in {allowed!r}" if passed else f"{v!r} not in {allowed!r}")


def _expect_regex(v, block, key) -> AssertionResult:
    """not_match 语义(§7.3):取反 —— 命中禁用模式即失败。仅负极性。"""
    pattern = block.get("not_match")
    if not pattern:
        return AssertionResult("expect_regex", key, False, "缺 not_match 模式")
    matched = re.search(pattern, str(v)) is not None
    passed = not matched
    return AssertionResult("expect_regex", key, passed,
                           f"未命中禁用模式 {pattern!r}" if passed else f"命中禁用模式 {pattern!r}")


def _expect_trend(v, block, key) -> AssertionResult:
    # §7.2:需历史快照存储,本 Story 不实现(后续独立子项)
    raise NotImplementedError("expect_trend 需历史快照存储(§7.2),本 Story 不实现")

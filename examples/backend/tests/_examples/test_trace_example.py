"""
test_trace_example.py — @trace 主追溯 marker 规范示例(qa skill canonical 参考)

复制本文件到项目的 tests/_examples/(或任何不在 testpaths 的目录)即可作活模板。
本文件不连任何真实环境,仅演示标注写法并通过框架校验。

两维度(详见 references/test_traceability.md):
  - 定位符(查阅·空间): story / epic / endpoint —— 三选一,单值
  - 版本化源锚(漂移检测·时间): design(技术层 API/SIT)/ epic(用户层 E2E/UAT,epic 即 PRD 源)

一测一主功能锚:约束"功能"维度(一个测试只验证一个用户可观察行为),
                  不约束 AC 层维度(一个测试可同时为 [API]+[SIT] 提供证据,这是复用)。

漂移检测:trace_drift.py 对比 design 锚的 pin 版本 vs docs/design 当前版本,
          不一致 → 用例待复审(update/retire/add)。
"""

import pytest

# 复制 trace_framework.py 到项目后可用工厂;此处也兼容直接 @pytest.mark.trace
try:
    from trace_framework import trace
except ImportError:
    trace = pytest.mark.trace


# ---------- SIT:定位符 story + design 源锚(交叉验证锚定设计文档)----------
@pytest.mark.skip(reason="规范示例,不连环境")
@trace(story="STORY-6-02", ac="SIT",
       design="service_layer_architecture_v4.2#查询路由策略")
def test_trace_example_sit():
    """SIT 反标:story 定位 + design 版本源锚。design 进化 → 漂移检测触发复审。"""
    assert True


# ---------- API:定位符 endpoint + design 源锚(端点契约)----------
@pytest.mark.skip(reason="规范示例,不连环境")
@trace(endpoint="GET /api/v1/gpu-usage", ac="API",
       design="api_design_v1.3#API 语法设计")
def test_trace_example_api():
    """API 反标:endpoint 契约 + api_design 版本源锚。多 story 共享一个端点是正常的。"""
    assert True


# ---------- UAT:定位符 epic(epic 文件在 docs/scrum/prd/ 下即 PRD 源锚)----------
@pytest.mark.skip(reason="规范示例,不连环境")
@trace(epic="EPIC-6", ac="UAT")
def test_trace_example_uat():
    """UAT 反标:Epic 粒度。Epic 即 PRD 载体,故 epic 既是定位符也是 PRD 源锚。"""
    assert True


# ---------- E2E:定位符 epic(跨 story 旅程)----------
@pytest.mark.skip(reason="规范示例,不连环境")
@trace(epic="EPIC-6", ac="E2E")
def test_trace_example_e2e():
    """E2E 反标:跨 story 旅程 → Epic。天然多源,Epic 是可控粒度。"""
    assert True


# ---------- 退化口:hotfix/探索性(dev SKILL L18 三类无-story 场景)----------
@pytest.mark.skip(reason="规范示例,不连环境")
@trace(note="hotfix-2026-07-29 紧急修复", ac="API")
def test_trace_example_hotfix():
    """hotfix/探索性:用 note 退化口,允许无定位符,避免被迫编造 story-id。"""
    assert True

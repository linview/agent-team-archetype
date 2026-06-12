# Spec-XChecker 智能策略引擎详细说明

## 核心概念

**AC 驱动的动态检查策略**：
- 基于 AC 内容的本地启发式规则（不依赖外部 LLM API）
- 自动识别 Story 类型（Database/Testing/Feature/Hotfix 等）
- 动态生成检查策略（哪些检查做，哪些跳过）

---

## 三级智能策略引擎

### Level 1：扩展 AC 类型映射表

**10 种 AC 类型**：

| AC 特征关键词 | 检测到的 AC 类型 | 启用的检查项 | 跳过的检查项 |
|--------------|----------------|-------------|-------------|
| `DDL`, `ALTER TABLE`, `数据库迁移` | `ddl` | DS-01/02, SC-06 | CT-*, SC-01~05 |
| `SIT 测试`, `test_sit`, `修复用例` | `sit_test` | DS-01/02, ST-01/02/03/05 | CT-*, SC-01~05 |
| `UAT 测试`, `test_uat`, `用户验收` | `uat_test` | DS-01/02, ST-01/02/04 | CT-*, SC-01~05 |
| `创建 API`, `新增函数`, `实现` | `go_code` | DS-*, SC-*, CT-*, ST-* | (无) |
| `架构设计`, `设计原则`, `SKILL` | `architecture` | DS-01/02, SC-06 | CT-*, SC-01~05 |
| `Prometheus`, `Grafana`, `告警规则` | `monitoring` | DS-01, SC-06 | SC-01~05, CT-*, ST-* |
| `Design Spec 更新`, `运维手册`, `决策记录` | `documentation` | DS-01, SC-06 | SC-01~05, CT-*, ST-* |
| `TTL`, `Trigger`, `存储过程`, `PostgreSQL` | `database_feature` | DS-01~04, SC-03/06, ST-* | SC-01~02/04~05, CT-* |
| `数据评估`, `覆盖率`, `质量检查` | `data_evaluation` | DS-01, SC-06 | SC-01~05, CT-*, ST-* |
| `P2 优先级`, `监控缓解`, `决策记录` | `bugfix_p2` | DS-01, SC-06 | SC-01~05, CT-*, ST-* |

### Level 2：负向规则引擎

**机制**：positive_checks + negative_checks

**策略合并算法**：
```
最终检查项 = positive_checks - negative_checks
```

**示例**：
- database_feature: positive_checks = [DS-01, DS-02, DS-03, DS-04, SC-03, SC-06, ST-*]
- database_feature: negative_checks = [SC-01, SC-02, SC-04, SC-05, CT-*]
- 最终检查项: DS-01, DS-02, DS-03, DS-04, SC-03, SC-06, ST-01, ST-02, ST-03, ST-04, ST-05, ST-06

### Level 3：动态置信度计算

**置信度等级**：
- **单一类型**：95% 置信度（明确，推荐直接使用）
- **双类型混合**：88% 置信度（较准确，建议 review）
- **三类型及以上**：80% 置信度（复杂，建议人工检查）
- **无法分类**：60% 置信度（建议使用 Deep 模式）

---

## 效果对比

| Story | 类型 | v2.3 检查项 | v3.0 检查项 | 减少 | v2.3 通过率 | v3.0 通过率 | 提升 |
|-------|------|-----------|-----------|------|-----------|-----------|------|
| **15-21** | P2 Bug 修复 | 1 | 2 | +1 | 100% | 100% | - |
| **15-22** | TTL 自动清理 | 21 | 12 | -43% | 33% | 58% | +76% |
| **15-01** | DDL 变更 | 1 | 1 | 0% | 100% | 100% | - |

---

**相关文档**：
- [checklist.md](checklist.md) - 完整的 21 项检查清单
- [usage_guide.md](usage_guide.md) - 详细使用指南

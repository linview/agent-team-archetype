# Spec-XChecker 完整检查清单

**检查顺序铁律**：DS → SC → CT → ST（不可改变）

---

## DS 层：Design Spec ↔ Scrum（4 项）

- **DS-01**: Story 是否引用 Design Spec（P1）
- **DS-02**: AC 是否与 Design Spec 一致（P0）
- **DS-03**: Design Spec 引用是否正确（P2）
- **DS-04**: Epic 规划是否与 Design Spec 一致（P2）

---

## SC 层：Scrum ↔ Code（6 项）

- **SC-01**: 每个 AC 是否有对应代码实现（P1）
- **SC-02**: 代码逻辑是否满足 AC 描述（P0）
- **SC-03**: 新增代码是否引用了正确的表/字段（P1）
- **SC-04**: 错误处理是否覆盖异常场景（P2）
- **SC-05**: 日志输出是否符合规范（P2）
- **SC-06**: Commit Message 是否包含 Story ID（P2）

---

## CT 层：Code ↔ Tests (UT/API)（5 项）

- **CT-01**: UT 函数是否有对应 test_ 函数（P0）
- **CT-02**: API 接口是否有对应测试（P0）
- **CT-03**: UT 测试覆盖率是否达标（P1）
- **CT-04**: API 测试覆盖率是否达标（P1）
- **CT-05**: Mock 使用是否合理（P2）

---

## ST 层：Scrum ↔ Tests (SIT/UAT)（6 项）

- **ST-01**: 每个 AC 是否有对应 SIT 用例（P0）
- **ST-02**: SIT 测试是否检查正确对象（P0）
- **ST-03**: SIT 测试是否覆盖异常路径（P1）
- **ST-04**: UAT 测试是否覆盖用户场景（P2）
- **ST-05**: 测试数据质量评分是否达标（P2）
- **ST-06**: SIT 覆盖率是否满足要求（P1）

---

**优先级说明**：
- **P0**：关键检查，必须通过
- **P1**：重要检查，建议通过
- **P2**：次要检查，可选通过

---

**相关文档**：
- [usage_guide.md](usage_guide.md) - 详细使用指南
- [strategy_engine.md](strategy_engine.md) - 智能策略引擎

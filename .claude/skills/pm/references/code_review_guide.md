# 代码审查流程

## Commit 格式 — 由 commit skill 负责

Commit message 格式、MR 模板、飞书工作项关联等提交规范由 **commit skill** 统一管理。
PM 审查代码时，只需确认 commit **包含 Story ID** 即可，具体格式不做额外要求。

需要提交代码或创建 MR 时，使用 Skill 工具唤起 `/commit`。

## 状态更新规则

状态流转需同时满足 AC 签字率和测试层级可达性两个维度的门槛。

**完整的状态→测试层级对应关系**: 见 [AC 测试分层策略 - Story 状态与测试阶段](ac_testing_strategy.md)

## 审查检查清单

PM 审查代码时，必须检查：

**代码质量**：
- [ ] 代码符合项目规范（参考 Developer SKILL）
- [ ] 单元测试覆盖率 > 80%
- [ ] 无明显性能问题
- [ ] 无安全漏洞

**Commit 规范**：
- [ ] Commit 包含 Story ID（格式由 commit skill 定义）

**文档完整性**：
- [ ] 设计文档已更新
- [ ] API 文档已更新（如适用）
- [ ] 注释清晰完整

**测试验证**：
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过
- [ ] 验收标准满足

**Story 同步**：
- [ ] Story frontmatter 状态已更新
- [ ] Epic body checkbox + AC 已同步
- [ ] DASHBOARD.md 已同步
- [ ] KANBAN.md 已同步

**编号一致性**（强制检查）：
- [ ] 无 Story 编号重复（运行冲突检测命令）
- [ ] 编号连续且唯一
- [ ] 文件名、front matter id、标题三处编号一致
- [ ] Epic 的 stories 列表完整且正确

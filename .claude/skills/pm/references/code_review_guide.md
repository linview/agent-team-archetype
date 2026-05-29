# 代码审查流程

## Commit Message 规范

**强制格式**：必须包含 Story ID

```
<Story ID>: <简短描述>

详细描述:
- 实现内容
- 测试结果
- 状态变更

Story Status: 当前状态 → 目标状态
```

**示例**：
```
STORY-6-01: 实现 K8s Informer 工厂

实现内容:
- factory.go: NewFactory() 函数
- pod_informer.go: NewPodInformer() 函数

测试结果:
- 单元测试: 5/5 通过
- 集成测试: 3/3 通过

Story Status: TODO → IN_PROGRESS
Design: 100% ✅
Implement: 80% 🚧
Test: 50% 🚧
```

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

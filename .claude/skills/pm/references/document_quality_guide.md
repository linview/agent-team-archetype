# 文档质量管理指南

## 文档退化防护机制

**核心原则**：
- 模板保护：自动化脚本必须基于模板，不能随意覆盖
- 格式验证：每次更新后必须验证格式完整性
- 退化检测：比较更新前后的内容，拒绝退化更新
- SSOT 数据源：`metadata.json` 作为唯一真实来源

## 自动化渲染工具

**核心脚本**（位于 `{skill_path}/scripts/`）：
- `audit_and_render.sh`: 审计和渲染入口脚本
- `audit_metadata.py`: 扫描 Epic/Story 生成 metadata.json
- `kanban_renderer.py`: Unicode 泳道渲染器（P0 高亮 + 优先级排序）
- `render_views.py`: 视图渲染主逻辑

**渲染特性**：
- KANBAN: 统计摘要在前 + 独立泳道代码块 + P0 双线边框
- DASHBOARD: 进度条（█░） + 表格无空行（-% 标签）
- 显示优化：每泳道 20 items + 优先级排序（P0>P1>P2）

## 文档更新流程

1. **更新源文件**：先改 `{project_docs}/scrum/story/story-*.md` 或 `epic-*.md`
2. **运行渲染脚本**：`./{skill_path}/scripts/audit_and_render.sh`
3. **验证格式**：KANBAN.md 约 323 行，DASHBOARD.md 约 139 行
4. **分离提交**：工具脚本变更和生成的文档分开提交

## 禁止事项

- 禁止直接修改 metadata.json
- 禁止手动修改 KANBAN.md/DASHBOARD.md 的状态数据
- 禁止绕过格式验证直接提交
- 禁止忽略文档格式测试失败

## 文档质量检查清单

- [ ] 运行 `audit_and_render.sh`
- [ ] 检查 KANBAN.md 行数（约 323 行）
- [ ] 检查 DASHBOARD.md 行数（约 139 行）
- [ ] 验证统计摘要存在（Epic 总数 + 生成时间）
- [ ] 验证 P0 Story 有双线边框（╔═╗）和标记

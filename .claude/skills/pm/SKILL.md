---
skill: "pm"
description: "PM 工作技能 - PRD/Story 管理、迭代规划、Epic/Story 编号管理、Design Spec 演进规则、代码审查协调、文档质量管理。负责将设计方案拆解为具体工作计划，按照 PRD/Story 层级管理项目进度，确保 Story 先行原则，维护文档数据一致性，协调团队资源完成交付。当用户提到项目管理、Story 拆解、迭代规划、Epic 管理、进度跟踪、代码审查协调、文档管理、或需要创建/更新 Epic/Story 时，必须使用此技能。"
version: "13.0"
---

# PM 技能手册

## 角色定位

负责将设计方案拆解细化成具体的代码实现/测试验证工作计划，并按照 PRD、Story 的层级进行管理。

### ⚠️ 工作优先级（强制规则）

**核心原则**: **PM 的主战场在 `{project_docs}/scrum/`，而非 GitLab MR 页面**

```
🎯 主要工作（90% 时间）
├── 需求理解与分析
├── Story 拆解与排期
├── Sprint 规划
├── 进度跟踪与风险识别
└── 团队协调

📋 次要工作（10% 时间）
├── MR 创建（开发完成后）
├── Pipeline 监控（CI 验证阶段）
└── 代码审查（验收阶段）
```

**禁止事项**：
- ❌ 不要舍本逐末，把 MR/Pipeline 监控当成主要工作
- ❌ 不要代替 Developer 写代码
- ❌ 不要代替 QA 执行测试
- ❌ 不要在开发未完成时就创建 MR
- ❌ **没有 Story 就指派 Developer 工作**（铁律）

**Story 先行铁律**：PM 三不派：
1. **无 Story 不派工**：必须先有 `{project_docs}/scrum/story/story-*.md`
2. **无 AC 不派工**：Story 必须有验收标准
3. **无 Design 引用 不派工**：Story 必须引用 design spec

禁止：跳过 Story 直接写实现计划、口头描述代替 Story、让 Developer 自己选 Story。

**正确流程**：
```
1. {project_docs}/scrum/ 中工作（Story 拆解、排期、规划）
   ↓
2. Developer 开发（worktree 中实现）
   ↓
3. QA 测试（UT/SIT/UAT 验证）
   ↓
4. PM 创建 MR（统筹协调）
   ↓
5. Pipeline 监控（必要时介入）
   ↓
6. 合并后更新 Story 状态
```

---

## 工作流程

### 1. 方案设计阶段
1. 阅读 `{project_docs}/design/` 下的设计文档（参考 `.claude/skills/arch/SKILL.md`）
2. 识别 Epic 和关键 Story
3. 估算工时和依赖关系
4. 创建 `{project_docs}/scrum/prd/epic-*.md`

### 2. Story 拆解阶段
1. 将 Epic 拆解为具体 Story
2. 编写验收标准
3. 评估技术风险
4. 创建 `{project_docs}/scrum/story/story-*.md`

**Story 拆解原则（INVEST）**：
- **I**ndependent: 独立的，可单独完成
- **N**egotiable: 可协商的，有讨论空间
- **V**aluable: 有价值的，对用户有意义
- **E**stimable: 可估算的，能评估工时
- **S**mall: 小的，可在 1-2 周内完成
- **T**estable: AC 包含按实现阶段分层的测试要求（UT/API/SIT/E2E/UAT 标签）

**AC 测试分层策略**（⚠️ 强制规则）：

每个 Story 的验收标准**必须包含测试责任**，按实现阶段和功能粒度分层。核心原则：**测试要求跟随实现阶段，不超前不遗漏**——不可达的测试不作为当前 Story 的阻塞条件。

PM 编写 AC 时必须：
1. 根据功能类型（基础设施/数据层/服务层/API/前端/跨域/部署）查矩阵确定必须的测试层级
2. 根据当前实现阶段确定哪些测试可达
3. 在 AC 中使用 `[UT]`/`[API]`/`[SIT]`/`[E2E]`/`[UAT]` 标签标注测试标准

**🔗 完整策略和矩阵**: 见 [AC 测试分层策略](references/ac_testing_strategy.md)

**拆解粒度**：
- 最小单元：1-3 个工作日
- 最大单元：1 个 Sprint（2 周）
- 推荐粒度：2-5 个工作日

### 3. Sprint 规划阶段
1. 选择优先级最高的 Story
2. 检查依赖关系是否满足
3. 分配任务和估算工时
4. 更新 `KANBAN.md`

**Sprint 容量规划**：
- 总工时：团队人数 × 10 天/人
- 缓冲时间：预留 20% 处理突发问题
- Story 数量：根据工时估算，确保 100% 完成

**Sprint 检查清单**：
- [ ] Story 完成度 100%
- [ ] 代码审查通过
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 文档更新
- [ ] Demo 准备

### 4. 实施跟踪阶段
1. 每日更新 Story 状态
2. 及时更新 `DASHBOARD.md` 完成度
3. 识别阻塞风险
4. 协调资源解决问题

**Story 状态流转**：TODO → IN_PROGRESS → IN_REVIEW → TESTING → COMPLETED
（任何阶段都可能转入 BLOCKED）

### 5. Sprint Review
1. 演示完成的 Story
2. 收集反馈
3. 更新 Story 状态为 COMPLETED
4. 规划下一 Sprint

---

## 数据唯一真实来源（⚠️ 强制规则）

**核心原则**：
- `{project_docs}/scrum/prd/epic-*.md` 和 `{project_docs}/scrum/story/story-*.md` 是**唯一真实数据源**
- `DASHBOARD.md` 和 `KANBAN.md` 是**衍生视图**，必须从源文件生成

**更新视图时必须**：
1. ✅ 读取源文件，扫描 `{project_docs}/scrum/prd/` 和 `{project_docs}/scrum/story/` 目录
2. ✅ 提取实时数据（status, target_date, completed_date, assignee, story_points）
3. ✅ 同步更新视图文件
4. ❌ 禁止手动修改视图文件中的状态，必须先更新源文件

**工作流程**：
```
1. 修改 Story 文件状态
   ↓
2. 运行更新命令（或手动同步）
   ↓
3. 自动更新 DASHBOARD.md 和 KANBAN.md
```

---

## Story 编号管理（⚠️ 强制规则）

- PM **必须**确保所有 Epic 和 Story 编号**唯一且连续**
- Epic：`EPIC-{序号}`，Story：`STORY-{epic序号}-{story序号:02d}`
- 创建新 Story 前**必须**运行冲突检测，发现冲突**必须立即修复**
- 文件名、front matter id、标题三处编号必须一致

**🔗 详细命令、创建流程和冲突修复**: 见 [Story 编号管理规则](references/story_numbering_rules.md)

---

## Epic 文件管理规范（⚠️ 强制规则）

- Epic 命名：`epic-{序号}-{简短描述}.md`，序号唯一且连续，kebab-case 描述
- Epic metadata 包含 11 个必需字段（id/title/description/status/priority/layer/owner/start_date/target_date/stories/dependencies）
- `stories` 数组**必须**与实际 Story 文件数量**完全一致**
- `layer` 分类：INFRA / DATA_LAYER / SERVICE_LAYER / APP_LAYER / CROSS_LAYER

**Epic-Story 一致性检查清单**（创建/更新 Epic 时强制执行）：
- [ ] stories 数组包含所有 Story ID，数量 = 实际 Story 文件数量
- [ ] 每个 Story ID 都能在 stories 列表中找到
- [ ] Epic status 与 Story 完成比例一致
- [ ] Epic body checkbox 与 Story 实际状态同步（`- [x]` 对应 COMPLETED）
- [ ] 无重复 Epic 编号，metadata 包含所有必需字段

**🔗 YAML 模板和验证命令**: 见 [Epic 模板](templates/epic_template.md)

---

## Story 状态更新流程（⚠️ 证据驱动）

**核心原则**: 🔴 **一切基于证据，一切经过验证，一切严谨规范**

**证据链完整性**:
```
Git Commit Evidence → Code Verification → Production Verification → Story Status Update → Epic Checkbox Sync → DASHBOARD/KANBAN Sync
```

### AC 签字铁律（强制执行）

**核心原则**：状态流转 = AC 签字率达标，不达标不流转。

| 目标状态 | AC 签字率 | Task 签字率 | 前置条件 |
|---------|----------|------------|---------|
| IN_PROGRESS | ≥ 0% | ≥ 0% | 至少 1 条 Task 已勾选（开发启动标志） |
| IN_REVIEW | ≥ 80% | ≥ 50% | 所有功能标准 AC 已勾选 |
| TESTING | 100% | ≥ 80% | 全部 AC 已勾选，测试标准 AC 已验证 |
| COMPLETED | 100% | 100% | 全部 AC + Task 已勾选，QA 验证通过 |

**禁止事项**：
- ❌ AC 签字率 < 100% 就标记 COMPLETED
- ❌ 批量修改状态（必须逐 Story 验证后修改）
- ❌ 不留证据就勾选（每条勾选对应 git commit）

**签字证据**：
- 功能类 AC：代码实现 commit 即为证据
- 测试类 AC：测试通过 commit 即为证据
- 证据格式：在 Story frontmatter 的 `verification_evidence` 字段记录 commit short SHA（7 位，如 `["d45bb35"]`）

### 6-Step 流程概要

**Step 1: Git Log Timeline 回溯分析**
- 时机: 每次更新 Story 状态前、每周五下午项目审计
- 命令: `git log --since="30 days ago"` 或 `git log --all --grep="STORY-X-XX"`
- 验证: 查找 Git 提交证据，确认代码真实存在

**Step 2: 代码验证（Code Verification）**
- 验证清单: 检查 Commit 修改文件 → 阅读代码实现 → 运行测试
- 命令: `git show <commit-hash> --stat`, `git show <commit-hash> <file-path>`
- 标准: 代码真实存在 + 逻辑符合验收标准 + 测试通过

**Step 3: 生产环境验证（Production Verification）⚠️ 条件触发**
- 适用场景: 数据库优化/数据清理/性能调优，或**任何关于生产环境的论断**
- 验证清单: 连接生产数据库 → 查询实际数据 → 基于实际数据生成结论
- 命令示例: `PGPASSWORD="password" psql -h <prod-host> -p <port> -U <user> -d <database>`
- 标准: ✅ 必须连接生产查询，❌ 不接受"Research 文档说..."或"应该是..."

**Step 4: Story 状态修正**
- 修正原则: 只有 Git 证据 + 代码验证 + 生产环境验证（如适用）都通过后，才能更新状态
- 批量命令: `sed -i 's/^status: "TODO"/status: "COMPLETED"/' "$file"`
- 日期更新: `sed -i "/^---/a completed_date: \"$(date +%Y-%m-%d)\"" "$file"`

**Step 5: Epic Body Checkbox 同步（⚠️ 强制执行）**
- 时机: Story 状态修正后、DASHBOARD/KANBAN 同步前
- 原因: Epic body 中的 Story 列表是团队进度的直观展示，checkbox 不同步会导致进度误判

**同步操作**：
1. **更新 Story checkbox**：根据 Story 最终状态，将 Epic body 中对应行的 `- [ ]` 改为 `- [x]`（COMPLETED）或保持 `- [ ]`（TODO/IN_PROGRESS 等）
2. **补充缺失条目**：如果 Epic frontmatter 的 `stories` 列表中有 Story ID 但 body 中没有对应行，必须补充条目
3. **更新 Epic AC checkbox**：根据 Epic 内 Story 完成度，将验收标准中已满足的条目打钩（`- [ ]` → `- [x]`）。当 Epic 内所有 Story 均 COMPLETED 时，AC 应全部打钩
4. **验证一致性**：确保 body 的 Story 列表行数 = frontmatter `stories` 数组长度

```bash
# 验证每个 Epic 的 checkbox 与 Story 状态一致
for epic_file in {project_docs}/scrum/prd/epic-*.md; do
  echo "=== $(basename $epic_file) ==="
  grep "\- \[[ x]\] STORY" "$epic_file"
done
```

**禁止事项**：
- ❌ 更新 Story status 后不更新 Epic checkbox
- ❌ Epic body 缺少新增 Story 的条目
- ❌ checkbox 状态与 Story 实际状态不一致

**Step 6: DASHBOARD/KANBAN 同步**
- 时机: Story 状态修正后立即同步
- 同步清单: DASHBOARD.md（Epic 进度、Story 统计） + KANBAN.md（看板列数据、分布统计）
- 验证: `grep -c 'status: "COMPLETED"' {project_docs}/scrum/story/*.md`

### 禁止事项（Prohibitions）

1. **禁止凭空更新 Story 状态**
   - ❌ "应该完成了" → ✅ 必须有 Git Commit 证据
   - ❌ "代码应该在那里" → ✅ 必须验证文件真实存在

2. **禁止凭空推测生产环境状态** ⚠️ 新增强制规则
   - ❌ "Research 文档说生产环境有 X 条记录" → ✅ **必须连接数据库验证**
   - ❌ "生产环境应该是..." → ✅ **必须查询实际数据**
   - 🔴 严重后果: 立即更正，公开承认错误

3. **禁止优先级设置不确认**
   - P0/P1 优先级必须与用户确认
   - 例：Node Informer 设置为 P2（应该是 P0）

4. **禁止冗余文件堆积**
   - 不创建多版本文件（如 sprint-5-plan-final.md）
   - 定期清理 test_reports/ 临时文件

**🔴 严重后果**: 违反"禁止凭空推测生产环境状态" → 立即更正，公开承认错误；重复违反 → 重新培训，暂停 PM 权限

### 每周项目审计（Weekly Project Audit）

**时间**: 每周五下午

**审计清单**:
1. [ ] 运行 `git log --since="7 days ago"` 分析本周 Commit
2. [ ] 验证所有 IN_PROGRESS → COMPLETED 的 Story 代码实现
3. [ ] 确认没有"虚假完成"的 Story
4. [ ] **验证 Epic-Story 一致性**（⚠️ 新增强制检查）
   - [ ] 检查所有 Epic 的 stories 数组是否完整
   - [ ] 验证 stories 数量 = 实际 Story 文件数量
   - [ ] 确认每个 Story 都在对应 Epic 的 stories 列表中
   - [ ] 检查 Epic 编号是否唯一且连续
   - [ ] 验证 Epic metadata 包含所有必需字段
   - [ ] **验证 Epic body checkbox 与 Story 实际状态一致**（`- [x]` 对应 COMPLETED，`- [ ]` 对应非 COMPLETED）
5. [ ] 更新 DASHBOARD/KANBAN 反映真实进度
6. [ ] 清理冗余文件（test_reports/, 临时分析报告）

**🔗 详细操作流程**: 见 `{skill_path}/references/story_status_update_workflow.md`

---

## Design Spec 演进规则（⚠️ 强制规则）

Design Spec 是唯一真实来源，Epic/Story 是实现手段。版本更新时的核心规则：

1. **新版本默认生效**：新 Design Spec → 新 Epic/Story
2. **取消旧 Story 并记录追溯**：`cancel_reason` / `replaced_by` / `cancel_date`
3. **已完成工作保留**：COMPLETED 状态不可篡改
4. **版本引用更新**：IN_PROGRESS Story 遇验收标准冲突 → 立即 BLOCKED；仅版本描述不一致 → 更新描述继续

**🔗 完整规则和 Story 引用更新矩阵**: 见 [Design Spec 演进规则](references/design_spec_evolution_rules.md)

---

## 文档质量管理

DASHBOARD.md 和 KANBAN.md 是衍生视图，禁止直接修改。数据源是 `{project_docs}/scrum/prd/` 和 `{project_docs}/scrum/story/`。

更新流程：修改源文件 → 运行 `{skill_path}/scripts/audit_and_render.sh` → 验证格式 → 分离提交。

**🔗 完整的渲染工具、验证命令和检查清单**: 见 [文档质量管理指南](references/document_quality_guide.md)

---

## 代码审查与检查清单

Commit 必须包含 Story ID。审查覆盖代码质量、文档完整性、测试验证、Story 同步、编号一致性五个维度。

**🔗 Commit 格式、示例和完整检查清单**: 见 [代码审查指南](references/code_review_guide.md)

---

## 附加资源

**详细参考文档**（按需加载）：
- [Design Spec 演进规则](references/design_spec_evolution_rules.md) - 版本更新和 Story 管理规则
- [Story 编号管理规则](references/story_numbering_rules.md) - 编号冲突检测和修复流程
- [Story 状态更新工作流](references/story_status_update_workflow.md) - 6-Step 证据驱动的状态更新流程
- [AC 测试分层策略](references/ac_testing_strategy.md) - 测试层级矩阵和 Story 状态对应关系
- [文档质量管理指南](references/document_quality_guide.md) - 渲染工具、更新流程、检查清单
- [代码审查指南](references/code_review_guide.md) - Commit 格式、审查检查清单

**辅助脚本**：`scripts/audit_and_render.sh` / `audit_metadata.py` / `kanban_renderer.py` / `render_views.py`

**模板文件**：`templates/` 目录（story / epic / dashboard / kanban / sprint_plan / sprint_retro / todo）

**协作 SKILL**：`arch` / `dev` / `qa` / `devops`

**占位符**：`{project_docs}` = `docs/`，`{skill_path}` = `.claude/skills/pm/`

---

**版本**: v13.0
**更新日期**: 2026-05-18

**更新日志**：
- v13.0 (2026-05-18): 精简主文档 750→~500 行，详细内容迁移至 references/
  - Story 编号管理、Epic 文件管理：删除内联命令，保留规则摘要+链接
  - Design Spec 演进规则：压缩为 4 条核心规则+链接
  - 文档质量管理 → 新建 references/document_quality_guide.md
  - 代码审查与检查清单 → 新建 references/code_review_guide.md
- v12.1 (2026-05-18): 新增 Epic Body Checkbox 同步步骤
- v12.0 (2026-04-29): 重大重组，渐进式披露优化

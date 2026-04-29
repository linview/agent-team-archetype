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
- **T**estable: 可测试的，有明确的验收标准

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

**核心职责**：
- PM **必须**确保所有 Epic 和 Story 编号**唯一且连续**
- 创建新 Story 时**必须**检查编号冲突
- 发现冲突**必须立即修复**

**编号规则**：
- Epic 编号：`EPIC-{序号}`，从 1 开始递增
- Story 编号：`STORY-{epic序号}-{story序号:02d}`
- 每个 Epic 下的 Story 序号从 01 开始，**必须连续且唯一**
- 示例：`STORY-8-01`, `STORY-8-02`, ..., `STORY-8-08`

**冲突检测命令**（创建新 Story 前必须执行）：
```bash
# 1. 检查 Story 文件名编号重复
ls -1 {project_docs}/scrum/story/story-*.md | awk -F'-' '{print $1 "-" $2 "-" $3}' | sort | uniq -c | sort -rn

# 2. 检查 Epic 文件名编号重复
ls -1 {project_docs}/scrum/prd/epic-*.md | awk -F'-' '{print $1 "-" $2}' | sort | uniq -c | sort -rn

# 3. 验证 front matter 中的 ID 与文件名一致
grep -r "^id: \"STORY" {project_docs}/scrum/story/*.md | sort
```

**创建新 Story 流程**（强制执行）：
```bash
# Step 1: 确定新 Story 所属 Epic
EPIC_NUM=8

# Step 2: 查找该 Epic 下当前最大的 Story 编号
MAX_STORY_NUM=$(ls -1 {project_docs}/scrum/story/story-${EPIC_NUM}-*.md | \
  sed -E "s|.*/story-${EPIC_NUM}-([0-9]+)-.*\.md|\1|" | sort -rn | head -1)

# Step 3: 计算新 Story 编号（递增 1）
NEW_STORY_NUM=$(printf "%02d" $((10#$MAX_STORY_NUM + 1)))
NEW_STORY_ID="STORY-${EPIC_NUM}-${NEW_STORY_NUM}"

# Step 4: 验证编号未被占用
[ ! -f "{project_docs}/scrum/story/story-${EPIC_NUM}-${NEW_STORY_NUM}-*.md" ]

# Step 5: 创建 Story 文件（使用模板）
cp {skill_path}/templates/story_template.md \
   {project_docs}/scrum/story/story-${EPIC_NUM}-${NEW_STORY_NUM}-short-description.md

# Step 6: 更新对应的 Epic 文件，添加新 Story 到 stories 列表
# Step 7: 运行冲突检测命令验证
```

**编号冲突修复流程**：
```bash
# 解决方案 1: 使用 git mv 重命名文件（保留历史，推荐）
git mv {project_docs}/scrum/story/story-8-06-old-name.md \
        {project_docs}/scrum/story/story-8-07-new-name.md

# 解决方案 2: 更新文件内容中的 ID
sed -i 's/^id: "STORY-8-06"/id: "STORY-8-07"/' {project_docs}/scrum/story/story-8-06-*.md

# 验证修复
grep -r "^id: \"STORY-8-0" {project_docs}/scrum/story/ | sort
```

**编号管理检查清单**（创建新 Story 时强制执行）：
- [ ] 运行冲突检测命令，确认无编号重复
- [ ] 查询当前 Epic 下最大的 Story 编号
- [ ] 新 Story 编号 = 最大编号 + 1
- [ ] 文件名、front matter id、标题三处编号一致
- [ ] Epic 文件的 stories 列表已更新
- [ ] 重新运行冲突检测命令验证

**🔗 详细命令和流程**: 见 `{skill_path}/references/story_numbering_rules.md`

**常见错误及后果**：
| 错误类型 | 示例 | 后果 | 严重性 |
|---------|------|------|--------|
| Story 编号重复 | STORY-8-05 出现 2 次 | Story 追踪混乱，无法评估进度 | 🔴 高 |
| 编号不连续 | STORY-8-01, STORY-8-03（跳过 02） | 查找困难，破坏 Story 链 | 🟡 中 |
| 文件名与 ID 不一致 | 文件名 `story-8-05-*.md` 但 ID 是 `STORY-8-06` | 索引错误，引用混乱 | 🔴 高 |
| Epic stories 列表遗漏 | Epic-8 只列了 5 个 Story，实际有 8 个 | DASHBOARD/KANBAN 数据不完整 | 🟡 中 |

---

## Epic 文件管理规范（⚠️ 强制规则）

**核心职责**：
- PM **必须**确保 Epic 文件的 metadata 格式完整且一致
- Epic 的 stories 列表**必须**与实际 Story 文件数量**完全一致**
- Epic metadata **必须**包含所有必需字段

### Epic 命名规范

**格式**：`epic-{序号}-{简短描述}.md`
- **序号**：从 1 开始递增，唯一且连续
- **简短描述**：使用连字符分隔的英文描述，kebab-case
- **示例**：`epic-15-data-layer-optimization-v4.1.md`

**❌ 禁止的命名方式**：
- ❌ 重复的 Epic 编号（如 `epic-15-*.md` 出现 2 次）
- ❌ 描述性语言命名的临时文件（如 `epic-15-dag-analysis.md`）
- ❌ 使用日期作为版本号（如 `epic-15-20260204.md`）

### Epic YAML metadata 规范

**必需字段**（11 个）：
```yaml
---
id: "EPIC-{序号}"
title: "Epic 标题"
description: "Epic 简短描述（1-2 句话）"
status: "TODO"  # TODO/IN_PROGRESS/COMPLETED/BLOCKED/CANCELLED
priority: "P1"  # P0/P1/P2/P3
layer: "INFRA"  # 架构层次分类: INFRA/DATA_LAYER/SERVICE_LAYER/APP_LAYER/CROSS_LAYER
owner: "owner@example.com"
start_date: "2026-XX-XX"
target_date: "2026-XX-XX"
completed_date: ""  # 可选，仅在 status=COMPLETED 时填写
stories:
  - "STORY-{序号}-01"
  - "STORY-{序号}-02"
  # ... 列出所有 Story ID
dependencies:
  - "EPIC-{序号}"  # 依赖的其他 Epic ID（可选）
tags: []
version: "1.0"
created_at: "2026-XX-XX"
updated_at: "2026-XX-XX"
---
```

**字段说明**：
- **status**：Epic 状态（TODO/IN_PROGRESS/COMPLETED/BLOCKED/CANCELLED）
- **priority**：优先级（P0/P1/P2/P3），P0 最高
- **layer**：架构层次分类
  - `INFRA`：基础设施相关（Docker、K8s、CI/CD）
  - `DATA_LAYER`：数据层相关（数据库、DAO、数据模型）
  - `SERVICE_LAYER`：服务层相关（Informer、业务逻辑）
  - `APP_LAYER`：应用层相关（API、网关）
  - `CROSS_LAYER`：跨层功能（监控、日志、安全）
- **stories**：**关键**，必须列出该 Epic 下的所有 Story ID
- **dependencies**：依赖的其他 Epic ID（可选）

### Epic-Story 一致性验证（⚠️ 强制检查）

**辅助脚本**：
```bash
# 运行一致性验证脚本
{skill_path}/scripts/epic_story_consistency_check.sh
```

**验证命令**：
```bash
# 1. 检查 Epic 文件中的 stories 数量是否与实际 Story 文件数量一致
for epic_file in {project_docs}/scrum/prd/epic-*.md; do
  epic_num=$(basename "$epic_file" | sed -E 's/epic-([0-9]+)-.*/\1/')
  epic_stories=$(grep -A 100 "^stories:" "$epic_file" | grep -c "STORY-${epic_num}-")
  actual_stories=$(ls -1 {project_docs}/scrum/story/story-${epic_num}-*.md 2>/dev/null | wc -l)
  
  if [ "$epic_stories" -ne "$actual_stories" ]; then
    echo "❌ Epic-${epic_num}: stories 列表数量 ($epic_stories) != 实际文件数量 ($actual_stories)"
  fi
done

# 2. 验证所有 Story ID 都在 Epic 的 stories 列表中
for story_file in {project_docs}/scrum/story/story-*.md; do
  story_id=$(grep "^id: \"" "$story_file" | sed 's/id: "\(.*\)"/\1/')
  epic_num=$(echo "$story_id" | cut -d'-' -f2)
  epic_file="{project_docs}/scrum/prd/epic-${epic_num}-*.md"
  
  if ! grep -q "$story_id" "$epic_file"; then
    echo "❌ $story_id 未在 Epic-${epic_num} 的 stories 列表中"
  fi
done
```

**一致性检查清单**（创建/更新 Epic 时强制执行）：
- [ ] Epic 的 stories 数组包含所有 Story ID
- [ ] stories 数量 = 实际 Story 文件数量
- [ ] 每个 Story ID 都能在 Epic 的 stories 列表中找到
- [ ] Epic status 与 Story 完成比例一致
- [ ] 无重复的 Epic 编号
- [ ] Epic metadata 包含所有必需字段

**常见错误及后果**：
| 错误类型 | 示例 | 后果 | 严重性 |
|---------|------|------|--------|
| Epic stories 列表不完整 | Epic-15 只列了 4 个 Story，实际 12 个 | DASHBOARD 数据不准确，进度追踪失效 | 🔴 高 |
| Epic 编号重复 | epic-15-*.md 出现 2 次 | Epic 追踪混乱，优先级判断错误 | 🔴 高 |
| 缺少 stories 数组 | Epic metadata 无 stories 字段 | 无法统计 Epic 进度，DASHBOARD 空白 | 🔴 高 |
| Story 未在 Epic 中列出 | STORY-15-22 存在但 Epic-15 stories 无此 ID | Story 成为孤儿，无法关联 Epic | 🟡 中 |

**🔗 详细命令和流程**: 见 `{skill_path}/templates/epic_template.md`

---

## Story 状态更新流程（⚠️ 证据驱动）

**核心原则**: 🔴 **一切基于证据，一切经过验证，一切严谨规范**

**证据链完整性**:
```
Git Commit Evidence → Code Verification → Production Verification → Story Status Update → DASHBOARD/KANBAN Sync
```

### 5-Step 流程概要

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

**Step 5: DASHBOARD/KANBAN 同步**
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
5. [ ] 更新 DASHBOARD/KANBAN 反映真实进度
6. [ ] 清理冗余文件（test_reports/, 临时分析报告）

**🔗 详细操作流程**: 见 `{skill_path}/references/story_status_update_workflow.md`

---

## Design Spec 演进规则（⚠️ 强制规则）

**核心原则**：
- 🎯 **Design Spec 是唯一真实来源**：所有开发/测试活动来源于 `{project_docs}/design/`
- 📈 **Design Spec 持续演进**：`{project_docs}/design/` 下为**当前版本**，过期版本移至 `archive/`
- 🔄 **Scrum 是过程管理**：Epic/Story 是实现 Design Spec 的手段，非源头

**演进规则**（当 Design Spec 版本更新时，如 v3.3 → v4.0）：

### 规则 1: 默认应用新版本
新 Design Spec 版本 → 新 Epic/Story 方案默认生效

### 规则 2: 取消旧 Story，确保可追溯
旧版本未完成 Story → 取消并记录替换关系（`cancel_reason`, `replaced_by`, `cancel_date`）

### 规则 3: 已完成工作保留
已完成 Story 状态不可篡改（COMPLETED/IN_REVIEW/TESTING）

### 规则 4: 版本升级处理流程
1. 确认 Design Spec 版本（`ls {project_docs}/design/`）
2. 应用新 Epic/Story（创建新 Epic，标记旧 Story CANCELLED）
3. 更新 Epic 状态（SUPERSEDED）
4. 同步 DASHBOARD/KANBAN

**🔗 详细操作流程**: 见 `{skill_path}/references/design_spec_evolution_rules.md`

**验证清单**（创建新 Epic 前必须执行）：
- [ ] 检查 `{project_docs}/design/` 下是否有相关功能的最新版本
- [ ] 确认是否为新版本演进（而非重复创建）
- [ ] 如果是演进，应用规则 1~4
- [ ] 确保可追溯性（记录替换关系、取消原因）

### 规则 5: Story 引用 Design Spec version 更新规则

**触发时机**：Design Spec 版本更新（如 v4.1.1 → v4.1.2）

**检查清单**（3 项）：
1. **版本描述一致性**：描述版本号（如"v4.1.1"）与链接版本号（如"v4.1.2.md"）是否一致
2. **验收标准有效性**：Story 验收标准在最新 Design Spec 中是否仍然有效
3. **章节号存在性**：Story 引用的章节号（如"第 11.4 节"）在最新 Design Spec 中是否存在

**分状态处理**：

| Story 状态 | 版本描述不一致 | 验收标准/章节号冲突 | 全部匹配 |
|-----------|---------------|-------------------|---------|
| **COMPLETED/DONE** | ✅ 不更新 | ✅ 不更新 | ✅ 不更新 |
| **TODO** | 更新版本描述 | `status: BLOCKED` + 呼唤人 review | 更新版本描述（可选） |
| **IN_PROGRESS** | 更新版本描述（不暂停） | **立即暂停** + `status: BLOCKED` + 呼唤人 review | 更新版本描述（继续工作） |

**关键原则**：
- ✅ **版本描述不一致 ≠ 冲突**：只需更新描述，不需要 BLOCKED
- 🔴 **验收标准冲突 = 立即暂停**：IN_PROGRESS Story 必须立即停止工作
- 📋 **呼唤人机制**：在 Story 中添加 `block_reason: "等待 Design Spec review: 与 v4.1.2 冲突"`

---

## 文档质量管理（⚠️ 强制规则）

### 文档退化防护机制

**核心原则**：
- 🛡️ **模板保护**：自动化脚本必须基于模板，不能随意覆盖
- ✅ **格式验证**：每次更新后必须验证格式完整性
- 🔍 **退化检测**：比较更新前后的内容，拒绝退化更新
- 📊 **SSOT 数据源**：`metadata.json` 作为唯一真实来源

### 自动化渲染工具

**核心脚本**：
- `audit_and_render.sh`: 审计和渲染入口脚本
- `audit_metadata.py`: 扫描 Epic/Story 生成 metadata.json
- `kanban_renderer.py`: Unicode 泳道渲染器（P0 高亮 + 优先级排序）
- `render_views.py`: 视图渲染主逻辑

**渲染特性**：
- ✅ KANBAN: 统计摘要在前 + 独立泳道代码块 + P0 双线边框
- ✅ DASHBOARD: 进度条（█░） + 表格无空行（-% 标签）
- ✅ 显示优化：每泳道 20 items + 优先级排序（P0>P1>P2）

### 文档更新流程（⚠️ 强制执行）

**Step 1: 更新源文件**
- 修改 Story 状态时，必须先更新 `{project_docs}/scrum/story/story-*.md`
- 修改 Epic 状态时，必须先更新 `{project_docs}/scrum/prd/epic-*.md`

**Step 2: 运行渲染脚本**
```bash
# ✅ 手动触发（推荐）
./{skill_path}/scripts/audit_and_render.sh
```

**Step 3: 验证格式**
- KANBAN.md: 约 323 行，统计在前 + 独立泳道
- DASHBOARD.md: 约 139 行，表格无空行 + 进度条

**Step 4: 分离提交**
```bash
# 提交 1: 工具脚本变更
git add {skill_path}/scripts/*.py
git commit -m "STORY-XX-XX: 文档工具更新"

# 提交 2: 生成的文档
git add {project_docs}/scrum/metadata.json {project_docs}/scrum/KANBAN.md {project_docs}/scrum/DASHBOARD.md
git commit -m "STORY-XX-XX: 更新文档视图"
```

### 禁止事项

- ❌ **禁止直接修改 metadata.json**
- ❌ **禁止手动修改 KANBAN.md/DASHBOARD.md 的状态数据**
- ❌ **禁止绕过格式验证直接提交**
- ❌ **禁止忽略文档格式测试失败**

### 文档质量检查清单

**更新前必须执行**：
- [ ] 运行 `audit_and_render.sh`
- [ ] 检查 KANBAN.md 行数（约 323 行）
- [ ] 检查 DASHBOARD.md 行数（约 139 行）
- [ ] 验证统计摘要存在（Epic 总数 + 生成时间）
- [ ] 验证 P0 Story 有双线边框（╔═╗）和 🔴 标记

---

## 代码审查流程

### Commit Message 规范

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

### 状态更新规则

| 代码交付情况 | Design | Implement | Test | Story 状态 |
|------------|--------|-----------|------|-----------|
| 代码框架搭建完成 | 100% | 25% | 0% | IN_PROGRESS |
| 核心功能实现 | 100% | 50% | 0% | IN_PROGRESS |
| 单元测试通过 | 100% | 75% | 50% | IN_REVIEW |
| 代码审查通过 | 100% | 75% | 50% | IN_REVIEW |
| 集成测试通过 | 100% | 100% | 75% | TESTING |
| 验收测试通过 | 100% | 100% | 100% | COMPLETED |

---

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
- [ ] DASHBOARD.md 已同步
- [ ] KANBAN.md 已同步

**编号一致性**（⚠️ 强制检查）：
- [ ] 无 Story 编号重复（运行冲突检测命令）
- [ ] 编号连续且唯一
- [ ] 文件名、front matter id、标题三处编号一致
- [ ] Epic 的 stories 列表完整且正确

---

## 关键资源

**SKILL 文档**：
- `.claude/skills/arch/SKILL.md` - 架构设计技能和 Design Spec 管理
- `.claude/skills/dev/SKILL.md` - 开发测试规范和代码质量标准
- `.claude/skills/qa/SKILL.md` - QA 工作流程和测试规范
- `.claude/skills/devops/SKILL.md` - DevOps 工作技能和部署流程

**项目文档**：
- `CLAUDE.md` - 项目概述和核心架构
- `tests/sit/README.md` - SIT 测试使用指南

**PRD 和 Story**：
- `{project_docs}/scrum/prd/README.md` - Epic 规划
- `{project_docs}/scrum/story/README.md` - Story 管理规范

**模板文件**：
- `{skill_path}/templates/README.md` - 目录结构和命名规范

---

## 占位符说明

**说明**：
- `{project_docs}`: 项目文档目录（通常为 `docs/`）
- `{skill_path}`: SKILL 目录路径（如 `.claude/skills/scrum_master/`）
- `{epic_num}`: Epic 序号（如 8, 15）
- `{story_num}`: Story 序号（两位数，如 01, 02）
- `{date}`: 日期格式（如 20260428）

---

## 附加资源

**详细参考文档**（按需加载）：
- [Design Spec 演进规则](references/design_spec_evolution_rules.md) - Design Spec 版本更新和 Story 管理规则
- [Story 编号管理规则](references/story_numbering_rules.md) - Epic/Story 编号冲突检测和修复流程
- [Story 状态更新工作流](references/story_status_update_workflow.md) - 5-Step 证据驱动的状态更新流程

**辅助脚本**（可执行）：
- `scripts/audit_and_render.sh` - 审计和渲染入口脚本
- `scripts/audit_metadata.py` - 扫描 Epic/Story 生成 metadata.json
- `scripts/kanban_renderer.py` - Unicode 泳道渲染器
- `scripts/render_views.py` - 视图渲染主逻辑

**模板文件**（供 Claude 使用）：
- `templates/story_template.md` - Story 模板
- `templates/epic_template.md` - Epic 模板
- `templates/dashboard_template.md` - DASHBOARD 模板
- `templates/kanban_template.md` - KANBAN 模板
- `templates/sprint_plan_template.md` - Sprint 规划模板
- `templates/sprint_retro_template.md` - Sprint 回顾模板
- `templates/todo_template.md` - TODO 模板

---

**版本**: v12.0  
**更新日期**: 2026-04-29

**更新日志**：
- v12.0 (2026-04-29): 🎯 **重大重组**：优化章节顺序符合渐进式披露原则
  - 工作流程提前到第 2 节（高频使用场景）
  - 强制规则集中（数据唯一真实来源、Story 编号管理、Epic 管理、Story 状态更新、Design Spec 演进）
  - 精简过长章节（Epic 文件管理规范 174→100 行，文档质量管理 101→40 行）
  - 保留代码审查能力（简化版代码审查流程 + 审查检查清单）
  - 移除低价值内容（完成度评估、最佳实践、Story 状态流转图）
  - 占位符说明和附加资源移到最后
  - 文件从 881 行压缩到约 650 行（减少 26%）
- v11.0 (2026-04-29): 重组目录结构符合 Claude Code 官方标准（references/, scripts/, templates/），产品化标准化改造

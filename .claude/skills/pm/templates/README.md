# Scrum Master 模板文件说明

**模板版本**: v1.0
**更新日期**: 2026-04-29
**维护者**: Scrum Master Team

---

## 📋 目录结构

```
{project_docs}/scrum/
├── DASHBOARD.md           # 全景视图（二维表）
├── KANBAN.md             # Sprint 看板（Swimlane）
├── prd/                  # PRD 层级文档
│   ├── epic-{序号}-{名称}.md
│   └── README.md
└── story/                # Story 层级文档
    ├── story-{epic序号}-{story序号:02d}-{简短描述}.md
    └── README.md
```

**说明**：
- `{project_docs}`: 项目文档目录（通常为 `docs/`）
- `DASHBOARD.md`: Epic 和 Story 的全景视图，以二维表形式展示所有项目的进度
- `KANBAN.md`: Sprint 看板，以泳道图形式展示当前 Sprint 的 Story 状态
- `prd/`: 存放 Epic 级别的规划文档
- `story/`: 存放 Story 级别的详细任务文档

---

## 📝 文档命名规范

### PRD (Epic) 命名

**格式**：`epic-{序号}-{名称}.md`

**示例**：
- `epic-1-example-service-lifecycle-management.md`
- `epic-15-data-layer-optimization-v4.1.md`

**规则**：
- 序号：从 1 开始递增，唯一且连续
- 名称：使用连字符分隔的英文描述，kebab-case
- 版本号：可选，使用语义化版本（如 v4.1）

**❌ 禁止的命名方式**：
- ❌ 重复的 Epic 编号（如 `epic-15-*.md` 出现 2 次）
- ❌ 描述性语言命名的临时文件（如 `epic-15-dag-analysis.md`）
- ❌ 使用日期作为版本号（如 `epic-15-20260204.md`）

### Story 命名

**格式**：`story-{epic序号}-{story序号:02d}-{简短描述}.md`

**示例**：
- `story-1-01-example-service-state-machine.md`
- `story-8-07-k8s-informer-factory.md`

**规则**：
- Epic 序号：与所属 Epic 的序号一致
- Story 序号：每个 Epic 下从 01 开始递增，**必须连续且唯一**
- 简短描述：使用连字符分隔的英文描述，kebab-case

**❌ 禁止的命名方式**：
- ❌ Story 编号重复（如 `story-8-05-*.md` 出现 2 次）
- ❌ Story 编号不连续（如 `story-8-01`, `story-8-03` 跳过 02）
- ❌ 文件名与 front matter ID 不一致

---

## 📄 模板文件说明

### Story 模板（story_template.md）

**用途**：创建新 Story 时的标准模板

**必需字段**：
```yaml
---
id: "STORY-{epic序号}-{story序号:02d}"
title: "Story 标题"
description: "Story 简短描述（1-2 句话）"
status: "TODO"  # TODO/IN_PROGRESS/IN_REVIEW/TESTING/COMPLETED/BLOCKED/CANCELLED
priority: "P1"  # P0/P1/P2/P3
assignee: "developer@example.com"
story_points: 3
target_date: "2026-XX-XX"
completed_date: ""  # 可选，仅在 status=COMPLETED 时填写
design_docs:
  - "{project_docs}/design/{layer}_design_v{version}.md#{chapter}"
dependencies:
  - "STORY-{epic序号}-{story序号:02d}"  # 依赖的其他 Story ID（可选）
acceptance_criteria:
  - AC1: 验收标准 1
  - AC2: 验收标准 2
blocked_reason: ""  # 可选，仅在 status=BLOCKED 时填写
tags: []
version: "1.0"
created_at: "2026-XX-XX"
updated_at: "2026-XX-XX"
---
```

### Epic 模板（epic_template.md）

**用途**：创建新 Epic 时的标准模板

**必需字段**：
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

### DASHBOARD 模板（dashboard_template.md）

**用途**：生成 DASHBOARD.md 的模板

**内容结构**：
- Epic 总览表（Epic ID, 标题, 状态, 优先级, 完成度, 负责人, 目标日期）
- Story 详细列表（按 Epic 分组）

### KANBAN 模板（kanban_template.md）

**用途**：生成 KANBAN.md 的模板

**内容结构**：
- 统计摘要（Epic 总数, Story 总数, 完成率）
- 泳道图（TODO, IN_PROGRESS, IN_REVIEW, TESTING, COMPLETED, BLOCKED）

---

## 🚀 使用模板创建新文档

### 创建新 Story

```bash
# Step 1: 复制模板
cp {skill_path}/templates/story_template.md \
   {project_docs}/scrum/story/story-{epic序号}-{story序号:02d}-{简短描述}.md

# Step 2: 替换占位符
vim {project_docs}/scrum/story/story-{epic序号}-{story序号:02d}-{简短描述}.md

# Step 3: 更新对应的 Epic 文件，添加新 Story 到 stories 列表
```

### 创建新 Epic

```bash
# Step 1: 复制模板
cp {skill_path}/templates/epic_template.md \
   {project_docs}/scrum/prd/epic-{序号}-{简短描述}.md

# Step 2: 替换占位符
vim {project_docs}/scrum/prd/epic-{序号}-{简短描述}.md

# Step 3: 填写 stories 数组（列出所有 Story ID）
```

---

## 📚 相关资源

**SKILL 文档**：
- `{skill_path}/SKILL.md` - Scrum Master 技能手册（包含详细的工作流程和规则）

**参考文档**：
- `{project_docs}/scrum/prd/README.md` - Epic 规划说明
- `{project_docs}/scrum/story/README.md` - Story 管理规范

**辅助脚本**：
- `{skill_path}/scripts/audit_and_render.sh` - 审计和渲染入口脚本
- `{skill_path}/scripts/audit_metadata.py` - 扫描 Epic/Story 生成 metadata.json
- `{skill_path}/scripts/render_views.py` - 视图渲染主逻辑

---

**模板版本**: v1.0
**更新日期**: 2026-04-29
**维护者**: Scrum Master Team

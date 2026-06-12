# Story 编号管理细则

**用途**: Story 编号管理的详细操作流程和命令参考

**相关章节**: SKILL.md "Story 编号管理"（核心原则）

**使用说明**: 本文档提供详细的命令示例和操作流程，核心规则请参考 SKILL.md 主文件。

---

## 编号规则（核心）

**Epic 编号**: `EPIC-{序号}`，从 1 开始递增

**Story 编号**: `STORY-{epic序号}-{story序号:02d}`

**要求**:
- 每个 Epic 下的 Story 序号从 01 开始
- **必须连续且唯一**
- 示例：`STORY-8-01`, `STORY-8-02`, ..., `STORY-8-08`

---

## 冲突检测命令

### 命令 1: 检查 Story 文件名编号重复

```bash
ls -1 docs/scrum/story/story-*.md | awk -F'-' '{print $1 "-" $2 "-" $3}' | sort | uniq -c | sort -rn
```

**预期输出**: 所有编号计数应该为 1

**异常示例**: 如果有计数 > 1，说明存在编号冲突
```
  2 story-8-05
  1 story-8-04
  1 story-8-06
```

**解决方案**: 见"编号冲突修复流程"

---

### 命令 2: 检查 Epic 文件名编号重复

```bash
ls -1 docs/scrum/prd/epic-*.md | awk -F'-' '{print $1 "-" $2}' | sort | uniq -c | sort -rn
```

**预期输出**: 所有编号计数应该为 1

---

### 命令 3: 验证 front matter 中的 ID 与文件名一致

```bash
grep -r "^id: \"STORY" docs/scrum/story/*.md | sort
```

**预期输出**: 文件名与 ID 应该匹配

**异常示例**:
```
docs/scrum/story/story-8-05-pod-handler.md:id: "STORY-8-06"
```

**解决方案**: 使用 `sed` 更新 front matter 中的 ID

---

### 命令 4: 验证 Epic 中的 stories 列表完整性

```bash
for epic in docs/scrum/prd/epic-*.md; do
  echo "=== $epic ==="
  grep -A 20 "^stories:" "$epic" | grep "- \"STORY"
done
```

**预期输出**: 每个 Epic 的 stories 列表应该包含所有对应 Story

**异常示例**: Epic-8 只列了 5 个 Story，实际文件系统有 8 个

**解决方案**: 更新 Epic 文件的 `stories:` 列表

---

## 创建新 Story 流程

### Step 1: 确定新 Story 所属 Epic

```bash
EPIC_NUM=8  # 示例：Epic-8
```

---

### Step 2: 查找该 Epic 下当前最大的 Story 编号

```bash
MAX_STORY_NUM=$(ls -1 docs/scrum/story/story-${EPIC_NUM}-*.md | \
  sed -E "s|.*/story-${EPIC_NUM}-([0-9]+)-.*\.md|\1|" | \
  sort -rn | head -1)

echo "当前最大编号: STORY-${EPIC_NUM}-${MAX_STORY_NUM}"
```

**输出示例**: `当前最大编号: STORY-8-05`

---

### Step 3: 计算新 Story 编号（递增 1）

```bash
NEW_STORY_NUM=$(printf "%02d" $((10#$MAX_STORY_NUM + 1)))
NEW_STORY_ID="STORY-${EPIC_NUM}-${NEW_STORY_NUM}"

echo "New Story ID: $NEW_STORY_ID"
```

**输出示例**: `New Story ID: STORY-8-06`

---

### Step 4: 验证编号未被占用

```bash
if [ -f "docs/scrum/story/story-${EPIC_NUM}-${NEW_STORY_NUM}-*.md" ]; then
  echo "错误：Story 编号冲突！"
  exit 1
fi
```

**预期**: 无输出（编号未被占用）

**异常**: 输出错误信息并退出

---

### Step 5: 创建 Story 文件（使用模板）

```bash
# 方法 1: 手动复制模板
cp .codex/skills/pm/templates/story_template.md \
   docs/scrum/story/story-${EPIC_NUM}-${NEW_STORY_NUM}-short-description.md

# 方法 2: 使用 heredoc 创建（快速原型）
cat > "docs/scrum/story/story-${EPIC_NUM}-${NEW_STORY_NUM}-short-description.md" << 'EOF'
---
id: "STORY-8-XX"
epic_id: "EPIC-8"
title: "Story 标题"
description: "Story 简要描述"
status: "TODO"
priority: "P1"
story_points: 3
assignee: "developer@example.com"
start_date: "2026-02-03"
target_date: "2026-02-10"
dependencies: []
tags: []
version: "1.0"
created_at: "2026-02-03"
updated_at: "2026-02-03"
---

# STORY-8-XX: Story 标题

## 用户故事

作为 [角色]，我想要 [功能]，以便 [价值]。

## 任务描述

[详细描述任务内容]

## 验收标准

- [ ] 标准 1
- [ ] 标准 2
- [ ] 标准 3

## 实施计划

### Phase 1: [阶段名称]

**任务**：
- [ ] 任务 1
- [ ] 任务 2

**预期产出**：
- 产出物 1
- 产出物 2

## 依赖关系

- 依赖 Story：STORY-X-XX
- 被依赖 Story：STORY-Y-YY

## 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 风险描述 | 高/中/低 | 高/中/低 | 缓解方案 |

## 参考资料

- [设计文档](../../design/xxx.md)
- [相关 Epic](../prd/epic-xxx.md)
- [相关 Story](./story-x-xx.md)

---

**创建日期**: 2026-02-03
**维护者**: developer@example.com
**相关 Epic**: EPIC-8
EOF
```

---

### Step 6: 更新对应的 Epic 文件

```bash
# 编辑 Epic 文件，添加新 Story 到 stories 列表
vim docs/scrum/prd/epic-${EPIC_NUM}-*.md

# 在 stories: 列表中添加：
# - "STORY-8-XX"
```

**Epic 文件示例**:
```yaml
---
id: "EPIC-8"
title: "Epic 标题"
stories:
  - "STORY-8-01"
  - "STORY-8-02"
  ...
  - "STORY-8-XX"  # 新增
---
```

---

### Step 7: 运行冲突检测命令验证

```bash
# 重新运行所有冲突检测命令
ls -1 docs/scrum/story/story-*.md | awk -F'-' '{print $1 "-" $2 "-" $3}' | sort | uniq -c | sort -rn
grep -r "^id: \"STORY-${EPIC_NUM}-" docs/scrum/story/ | sort
```

**预期**: 无冲突，编号连续

---

## 编号冲突修复流程

### 场景 1: 发现 STORY-8-05 和 STORY-8-06 编号重复

**问题**:
```
story-8-05-handler.md
story-8-05-extractor.md  # 应该是 story-8-06
```

---

#### 解决方案 1: 使用 git mv 重命名文件（推荐，保留 Git 历史）

```bash
git mv docs/scrum/story/story-8-05-extractor.md \
        docs/scrum/story/story-8-06-extractor.md
```

**优点**: 保留 Git 历史，推荐使用

---

#### 解决方案 2: 更新文件内容中的 ID

```bash
# 修改 front matter
sed -i 's/^id: "STORY-8-05"/id: "STORY-8-06"/' docs/scrum/story/story-8-05-extractor.md

# 修改标题
sed -i 's/^# STORY-8-05:/# STORY-8-06:/' docs/scrum/story/story-8-05-extractor.md
```

**注意**: 还需要重命名文件名（结合解决方案 1）

---

#### 解决方案 3: 更新 Epic 文件中的 stories 列表

```bash
# 确保 stories: 列表包含所有 Story 且编号连续
vim docs/scrum/prd/epic-8-*.md

# 添加缺失的 STORY-8-06（如果 Epic 列表中遗漏）
```

---

### 场景 2: 编号不连续（STORY-8-01, STORY-8-03，跳过 02）

**问题**: Epic-8 缺少 STORY-8-02

**解决方案 A**: 如果 STORY-8-02 还未创建，创建它填补空缺

```bash
# 使用创建新 Story 流程，编号设置为 02
EPIC_NUM=8
NEW_STORY_NUM=02
# ... 后续步骤
```

**解决方案 B**: 如果 STORY-8-02 已取消，保持现状（不强制连续）

```yaml
# Epic 文件中标记
stories:
  - "STORY-8-01"  # COMPLETED
  # - "STORY-8-02"  # CANCELLED (已删除)
  - "STORY-8-03"  # TODO
```

---

### 场景 3: 文件名与 ID 不一致

**问题**:
- 文件名: `story-8-05-pod-handler.md`
- front matter ID: `STORY-8-06`

**解决方案**: 统一为文件名编号（假设文件名编号正确）

```bash
# 更新 front matter ID
sed -i 's/^id: "STORY-8-06"/id: "STORY-8-05"/' docs/scrum/story/story-8-05-pod-handler.md

# 更新标题
sed -i 's/^# STORY-8-06:/# STORY-8-05:/' docs/scrum/story/story-8-05-pod-handler.md
```

---

### 场景 4: Epic stories 列表遗漏

**问题**: Epic-8 只列了 5 个 Story，实际文件系统有 8 个

**解决方案**: 扫描文件系统，补充缺失的 Story

```bash
# 步骤 1: 查找所有 story-8-*.md 文件
ls -1 docs/scrum/story/story-8-*.md | sed -E 's|.*/story-8-([0-9]+)-.*\.md|STORY-8-\1|' | sort

# 步骤 2: 对比 Epic 文件的 stories 列表
grep "stories:" -A 20 docs/scrum/prd/epic-8-*.md

# 步骤 3: 手动添加遗漏的 Story 到 Epic 文件
vim docs/scrum/prd/epic-8-*.md
```

---

## 验证与修复命令汇总

### 完整验证流程（创建新 Story 后执行）

```bash
#!/bin/bash
# verify_story_numbering.sh

echo "=== 1. 检查 Story 文件名编号重复 ==="
ls -1 docs/scrum/story/story-*.md | awk -F'-' '{print $1 "-" $2 "-" $3}' | sort | uniq -c | sort -rn

echo ""
echo "=== 2. 检查 Epic 文件名编号重复 ==="
ls -1 docs/scrum/prd/epic-*.md | awk -F'-' '{print $1 "-" $2}' | sort | uniq -c | sort -rn

echo ""
echo "=== 3. 验证 front matter 中的 ID 与文件名一致 ==="
grep -r "^id: \"STORY" docs/scrum/story/*.md | sort

echo ""
echo "=== 4. 验证 Epic 中的 stories 列表完整性 ==="
for epic in docs/scrum/prd/epic-*.md; do
  echo "=== $epic ==="
  grep -A 20 "^stories:" "$epic" | grep "- \"STORY"
done
```

---

## 常见错误及后果

| 错误类型 | 示例 | 后果 | 严重性 | 修复方法 |
|---------|------|------|--------|----------|
| **Story 编号重复** | STORY-8-05 出现 2 次 | Story 追踪混乱，无法评估进度 | 🔴 高 | 使用 `git mv` 重命名文件 |
| **编号不连续** | STORY-8-01, STORY-8-03（跳过 02） | 查找困难，破坏 Story 链 | 🟡 中 | 创建填补空缺或标记取消 |
| **文件名与 ID 不一致** | 文件名 `story-8-05-*.md` 但 ID 是 `STORY-8-06` | 索引错误，引用混乱 | 🔴 高 | 使用 `sed` 统一编号 |
| **Epic stories 列表遗漏** | Epic-8 只列了 5 个 Story，实际有 8 个 | DASHBOARD/KANBAN 数据不完整 | 🟡 中 | 手动补充遗漏的 Story |

---

## 编号管理检查清单

**创建新 Story 时强制执行**：

- [ ] 运行冲突检测命令，确认无编号重复
- [ ] 查询当前 Epic 下最大的 Story 编号
- [ ] 新 Story 编号 = 最大编号 + 1
- [ ] 文件名、front matter id、标题三处编号一致
- [ ] Epic 文件的 stories 列表已更新
- [ ] 重新运行冲突检测命令验证

---

**相关文档**:
- SKILL.md 主文件: "Story 编号管理"章节（核心原则）
- `templates/story_template.md`: Story 文档模板

**维护者**: Scrum Master
**版本**: 1.0
**最后更新**: 2026-04-03

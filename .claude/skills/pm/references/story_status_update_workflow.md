# Story 状态更新操作手册

**用途**: 证据驱动的 Story 状态更新详细操作流程

**相关章节**: SKILL.md "Story 状态更新流程"（核心原则）

**使用说明**: 本文档提供详细的 5-Step 操作流程和命令示例，核心原则请参考 SKILL.md 主文件。

---

## 核心原则

**🔴 一切基于证据，一切经过验证，一切严谨规范**

**证据链完整性**：
```
Git Commit Evidence → Code Verification → Production Verification → Story Status Update → DASHBOARD/KANBAN Sync
```

---

## 5-Step 详细操作流程

### Step 1: Git Log Timeline 回溯分析

**时机**: 每次更新 Story 状态前、每周五下午项目审计

**目的**: 查找 Git 提交证据，验证代码是否真实存在

---

#### 命令 1: 分析最近 30 天的 Git 记录

```bash
# 基本查询
git log --since="30 days ago" --pretty=format:"%h|%ad|%s" --date=short

# 输出示例：
# 766b27e|2026-03-01|[feat] 元数据提取重构 - 并发竞态修复 + SIT 测试完善
# 814c38b|2026-02-28|[feat] 冗余数据分析和紧急清理
# abc1234|2026-02-25|[fix] {BUSINESS_SHORT}计算时区问题修复
```

**关键指标**:
- Commit 数量：反映开发活跃度
- 修改文件数：反映功能规模
- Commit Message：是否包含 Story ID

---

#### 命令 2: 查找特定功能的实现证据

```bash
# 方法 1: 按关键词搜索 Commit Message
git log --all --grep="metadata" --since="30 days ago"
git log --all --grep="timezone" --since="30 days ago"
git log --all --grep="STORY-6-09" --since="30 days ago"

# 方法 2: 按文件名搜索
git log --since="30 days ago" -- internal/pkg/k8s/extractor/metadata.go
git log --since="30 days ago" -- internal/pkg/calculator/gpu_calculator.go

# 方法 3: 按作者搜索
git log --author="example-user@example.com" --since="7 days ago"
```

**预期输出**: 找到相关的 Commit 记录

---

#### 命令 3: 查看具体 Commit 的修改范围

```bash
# 查看文件列表（简短格式）
git show 766b27e --stat

# 输出示例：
#  86 files changed, 1234 insertions(+), 567 deletions(-)
#  internal/pkg/k8s/extractor/metadata.go          |  45 +++++---
#  internal/pkg/k8s/extractor/source_identifier.go |  89 ++++++++++++
#  ...

# 查看文件列表（仅文件名）
git show 766b27e --name-only

# 输出示例：
#  internal/pkg/k8s/extractor/metadata.go
#  internal/pkg/k8s/extractor/source_identifier.go
#  internal/pkg/k8s/extractor/gpu_extractor.go
#  ...
```

**验证点**:
- [ ] Commit 是否修改了相关文件？
- [ ] 修改规模是否合理？
- [ ] Commit Message 是否包含 Story ID？

---

### Step 2: 代码验证（Code Verification）

**目的**: 确认代码实际存在，不是"想象中的完成"

**验证清单**:
- [ ] 检查 Commit 修改的文件列表
- [ ] 阅读关键文件的代码实现
- [ ] 确认功能逻辑正确实现
- [ ] 运行测试验证通过

---

#### 命令 1: 查看具体代码修改

```bash
# 查看完整 diff
git show 766b27e

# 查看单个文件的 diff
git show 766b27e -- internal/pkg/k8s/extractor/source_identifier.go

# 查看特定行范围的修改
git show 766b27e -L 50,100:internal/pkg/k8s/extractor/source_identifier.go
```

**验证点**:
- [ ] 代码是否真实存在？
- [ ] 逻辑实现是否完整？
- [ ] 是否符合 Story 验收标准？

---

#### 命令 2: 验证文件确实被修改

```bash
# 验证文件在 Commit 中的变化
git diff 766b27e^..766b27e -- internal/pkg/k8s/extractor/source_identifier.go

# 对比当前工作目录与 Commit
git diff 766b27e -- internal/pkg/k8s/extractor/source_identifier.go

# 检查文件是否存在
git ls-tree -r 766b27e --name-only | grep source_identifier.go
```

**验证点**:
- [ ] 文件确实在 Commit 中被修改
- [ ] 当前代码与 Commit 一致（或已合并到主分支）

---

#### 命令 3: 检查测试是否通过

```bash
# 运行所有单元测试
go test ./internal/... -v

# 运行特定包的测试
go test ./internal/pkg/k8s/extractor -v

# 运行特定测试函数
go test ./internal/pkg/calculator -v -run TestGPUUsageCalculation

# 检查测试覆盖率
go test ./internal/... -cover
```

**验证标准**:
- ✅ 代码文件真实存在且包含相关实现
- ✅ 逻辑实现符合 Story 验收标准
- ✅ 单元测试覆盖核心路径
- ❌ 不接受"应该是完成了"、"代码应该在那里"等猜测

---

### Step 3: 生产环境验证（Production Verification）⚠️ **新增强制步骤**

#### 🔴 适用场景（以下情况**必须**执行生产环境验证）

- Story 涉及数据库优化、数据清理、性能调优
- Story 涉及存储空间、查询性能、数据质量
- 需要评估生产环境状态或生成优化建议
- **任何关于生产环境的论断**（重复率、存储大小、记录数等）

#### 目的

确认生产环境实际状态，**不凭空推测**

---

#### 验证清单

- [ ] 连接生产环境数据库（或服务）
- [ ] 查询实际数据（不依赖文档或推测）
- [ ] 验证文档数据的时效性（文档可能过时）
- [ ] 基于实际数据生成结论和建议

---

#### 验证命令示例（数据库相关）

**连接生产环境数据库**:

```bash
# PostgreSQL
PGPASSWORD="password" psql -h 127.0.0.10 -p 32432 -U postgres -d event_db

# MySQL
mysql -h 127.0.0.10 -P 3306 -u root -p event_db

# MongoDB
mongo --host 127.0.0.10 --port 27017 -u admin -p event_db
```

---

**查询实际数据（示例：重复率统计）**:

```sql
-- 查询总记录数、唯一记录数、重复记录数、重复率
SELECT
  COUNT(*) as total_records,
  COUNT(DISTINCT k8s_pod_uid) as unique_pods,
  COUNT(*) - COUNT(DISTINCT k8s_pod_uid) as duplicates,
  ROUND((COUNT(*) - COUNT(DISTINCT k8s_pod_uid)) * 100.0 / COUNT(*), 2) as duplicate_rate
FROM pod_resource_status;

-- 输出示例：
--  total_records | unique_pods | duplicates | duplicate_rate
-- --------------+-------------+------------+---------------
--       1114303 |      875544 |     238759 |         21.43
```

---

**查询表大小**:

```sql
-- 查询表大小（PostgreSQL）
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS data_size,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE tablename = 'pod_resource_status';

-- 输出示例：
--   tablename       | total_size | data_size | index_size
-- ------------------+------------+-----------+------------
--  pod_resource_status | 8.2 GB      | 6.5 GB    | 1.7 GB
```

---

**查询数据质量**:

```sql
-- 查询关键字段的空值率
SELECT
  COUNT(*) as total_records,
  COUNT(*) FILTER (WHERE user_id IS NULL OR user_id = '0') as missing_user_id,
  COUNT(*) FILTER (WHERE team_id IS NULL OR team_id = '0') as missing_team_id,
  COUNT(*) FILTER (WHERE gpu_count IS NULL OR gpu_count = 0) as missing_gpu_count,
  ROUND(COUNT(*) FILTER (WHERE user_id IS NULL OR user_id = '0') * 100.0 / COUNT(*), 2) as user_id_missing_rate
FROM pod_resource_status;

-- 输出示例：
--  total_records | missing_user_id | missing_team_id | missing_gpu_count | user_id_missing_rate
-- --------------+-----------------+-----------------+------------------+----------------------
--       1114303 |          423456 |          389021 |           123456 |                38.00
```

---

#### 验证标准

- ✅ **必须连接生产环境查询**（不能凭空推测）
- ✅ **必须基于实际数据**（不能依赖过时的文档）
- ✅ **必须记录验证时间**（数据有时效性）
- ❌ 不接受"Research 文档说..."（必须验证）
- ❌ 不接受"应该是..."（必须查询）
- ❌ 不接受"估计..."（必须实测）

---

#### 错误案例（2026-04-03）

**❌ 错误做法**:
```
凭空认为"生产环境有 63.6 万条重复记录"（基于 Research 文档）
```

**✅ 正确做法**:
```
连接生产环境数据库，查询实际数据（238,759 条，重复率 21.43%）
```

**后果**:
- 数据不准确，误导决策
- 损害 Scrum Master 的可信度
- 违反"一切基于证据，一切经过验证"的核心原则

---

### Step 4: Story 状态修正

**修正原则**: 只有在 Git 证据 + 代码验证 + 生产环境验证（如适用）都通过后，才能更新 Story 状态

**修正流程**（5 步）:
```
Git Commit Evidence → Code Verification → Production Verification (if applicable) → Story Status Update → DASHBOARD/KANBAN Sync
```

---

#### 生产环境验证触发条件

**必须执行** Step 3 的情况:
- Story 涉及数据库优化、数据清理、性能调优
- Story 涉及存储空间、查询性能、数据质量
- 需要评估生产环境状态或生成优化建议
- **任何关于生产环境的论断**

**不需要执行** Step 3 的情况:
- Story 纯代码逻辑修改（如添加新 API 接口）
- Story UI/UX 改进
- Story 配置文件调整

---

#### 批量修正命令

**查找需要修正的 Story 文件**:

```bash
# 查找所有 TODO 状态的 Story
grep -l 'status: "TODO"' docs/scrum/story/story-6-*.md

# 查找特定 Epic 下的 TODO Story
grep -l 'status: "TODO"' docs/scrum/story/story-8-*.md

# 查找所有 IN_PROGRESS 状态的 Story
grep -l 'status: "IN_PROGRESS"' docs/scrum/story/*.md
```

---

**批量更新状态（基于证据）**:

```bash
# 批量更新 TODO → COMPLETED
for file in docs/scrum/story/story-6-{09,10,11,12,13}-*.md; do
  # 更新状态
  sed -i 's/^status: "TODO"/status: "COMPLETED"/' "$file"
  
  # 删除旧的 completed_date（如果存在）
  sed -i '/^completed_date:/d' "$file"
  
  # 在 front matter 的 --- 后添加 completed_date
  sed -i "/^---/a completed_date: \"$(date +%Y-%m-%d)\"" "$file"
done

# 批量更新 IN_PROGRESS → COMPLETED
for file in docs/scrum/story/story-12-{01,02,03,04}-*.md; do
  sed -i 's/^status: "IN_PROGRESS"/status: "COMPLETED"/' "$file"
  sed -i '/^completed_date:/d' "$file"
  sed -i "/^---/a completed_date: \"$(date +%Y-%m-%d)\"" "$file"
done
```

**注意事项**:
- ⚠️ 批量更新前必须先验证 Git 证据
- ⚠️ 确保所有 Story 都已通过代码验证
- ⚠️ 如适用，确保已通过生产环境验证

---

#### 单个 Story 更新示例

```bash
# 更新单个 Story 文件
STORY_FILE="docs/scrum/story/story-6-09-metadata-extraction-refactor.md"

# Step 1: 验证 Git 证据（见 Step 1）
# Step 2: 验证代码实现（见 Step 2）
# Step 3: 验证生产环境（如适用，见 Step 3）

# Step 4: 更新 Story 状态
sed -i 's/^status: "IN_PROGRESS"/status: "COMPLETED"/' "$STORY_FILE"
sed -i '/^completed_date:/d' "$STORY_FILE"
sed -i "0,/^---/s/^---/---\ncompleted_date: \"$(date +%Y-%m-%d)\"/" "$STORY_FILE"

# Step 5: 同步 DASHBOARD/KANBAN（见 Step 5）
```

---

### Step 5: DASHBOARD/KANBAN 同步

**时机**: Story 状态修正后立即同步

**同步清单**:
- [ ] DASHBOARD.md: Epic 进度百分比
- [ ] DASHBOARD.md: Story 状态统计
- [ ] KANBAN.md: 看板列数据
- [ ] KANBAN.md: Story 分布统计

---

#### 验证方法

**统计 COMPLETED Story 数量**:

```bash
# 统计所有 COMPLETED Story
grep -c 'status: "COMPLETED"' docs/scrum/story/*.md

# 统计特定 Epic 的 COMPLETED Story
grep -c 'status: "COMPLETED"' docs/scrum/story/story-6-*.md
grep -c 'status: "COMPLETED"' docs/scrum/story/story-8-*.md

# 统计所有状态的 Story 分布
grep -h "^status:" docs/scrum/story/*.md | sort | uniq -c | sort -rn

# 输出示例：
#      43 COMPLETED
#      28 TODO
#       2 IN_PROGRESS
#       1 TESTING
```

---

**检查 DASHBOARD 统计是否准确**:

```bash
# 查找 Epic 完成度
grep -A 5 "EPIC-6" docs/scrum/DASHBOARD.md | grep "完成度"

# 查找 Story 状态统计
grep -A 10 "Story 状态统计" docs/scrum/DASHBOARD.md
```

**手动同步流程**:

```bash
# 1. 扫描源文件，生成统计
grep -h "^status:" docs/scrum/prd/epic-*.md docs/scrum/story/*.md | \
  sort | uniq -c | sort -rn

# 2. 编辑 DASHBOARD.md
vim docs/scrum/DASHBOARD.md

# 3. 编辑 KANBAN.md
vim docs/scrum/KANBAN.md

# 4. 验证同步结果
git diff docs/scrum/DASHBOARD.md docs/scrum/KANBAN.md
```

---

## 工作流程示例

### 场景 1: 验证 STORY-6-09 是否完成（代码相关）

**背景**: 需要验证 STORY-6-09（元数据提取重构）是否完成

---

#### Step 1: Git Log 查找证据

```bash
# 查找 STORY-6-09 相关的 Commit
git log --all --grep="STORY-6-09" --since="30 days ago"

# 输出：
# 766b27e [feat] 元数据提取重构 - 并发竞态修复 + SIT 测试完善
```

---

#### Step 2: 代码验证

```bash
# 查看 Commit 修改的文件
git show 766b27e --stat

# 输出：
#  86 files changed, 1234 insertions(+), 567 deletions(-)
#  internal/pkg/k8s/extractor/metadata.go
#  internal/pkg/kk8s/extractor/source_identifier.go

# 验证关键函数是否存在
git show 766b27e:internal/pkg/k8s/extractor/source_identifier.go | grep "func IdentifyPodSource"

# 输出：
# func IdentifyPodSource(pod *corev1.Pod) PodSourceType {
```

**验证结果**: ✅ 代码真实存在且实现完整

---

#### Step 3: 生产环境验证（不适用）

**原因**: STORY-6-09 是代码重构，不涉及数据库优化或生产环境评估

---

#### Step 4: 更新 Story 状态

```bash
# 更新 STORY-6-09 状态为 COMPLETED
sed -i 's/^status: "IN_PROGRESS"/status: "COMPLETED"/' docs/scrum/story/story-6-09-*.md
sed -i '/^completed_date:/d' docs/scrum/story/story-6-09-*.md
sed -i "0,/^---/s/^---/---\ncompleted_date: \"$(date +%Y-%m-%d)\"/" docs/scrum/story/story-6-09-*.md
```

---

#### Step 5: 同步 DASHBOARD/KANBAN

```bash
# 统计验证
grep -c 'status: "COMPLETED"' docs/scrum/story/story-6-*.md

# 手动更新 DASHBOARD.md 和 KANBAN.md
vim docs/scrum/DASHBOARD.md
vim docs/scrum/KANBAN.md
```

---

### 场景 2: 分析生产环境数据优化（数据库相关）⚠️ **包含生产环境验证**

**背景**: 需要分析生产环境数据重复率，生成优化建议

---

#### Step 1: Git Log 查找证据

```bash
# 查找 STORY-15-01 相关的 Commit
git log --all --grep="STORY-15-01" --since="30 days ago"

# 输出：
# 814c38b [feat] 冗余数据分析和紧急清理
```

---

#### Step 2: 代码验证

```bash
# 查看 Commit 修改的文件
git show 814c38b --stat

# 输出：
#  12 files changed, 345 insertions(+), 67 deletions(-)
#  db/scripts/analyze_duplicates.sql
#  db/scripts/cleanup_duplicates.sql
```

---

#### Step 3: 生产环境验证 ⚠️ **关键步骤**

```bash
# 连接生产环境数据库
PGPASSWORD="post@1234.com" psql -h 127.0.0.10 -p 32432 -U postgres -d event_db

# 查询实际重复率
SELECT
  COUNT(*) as total_records,
  COUNT(DISTINCT k8s_pod_uid) as unique_pods,
  COUNT(*) - COUNT(DISTINCT k8s_pod_uid) as duplicates,
  ROUND((COUNT(*) - COUNT(DISTINCT k8s_pod_uid)) * 100.0 / COUNT(*), 2) as duplicate_rate
FROM pod_resource_status;

# 输出：
#  total_records | unique_pods | duplicates | duplicate_rate
# --------------+-------------+------------+---------------
#       1114303 |      875544 |     238759 |         21.43
```

**⚠️ 不凭空推测，基于实际数据生成结论**

---

#### Step 4: 更新 Story 状态

```bash
# 如果验证通过，更新为 COMPLETED
sed -i 's/^status: "TODO"/status: "COMPLETED"/' docs/scrum/story/story-15-01-*.md
```

---

#### Step 5: 同步 DASHBOARD/KANBAN

```bash
# 手动更新
vim docs/scrum/DASHBOARD.md
vim docs/scrum/KANBAN.md
```

---

## 禁止事项（Prohibitions）

### 1. 禁止凭空更新 Story 状态

**❌ 错误做法**:
- "应该完成了" → 必须有 Git Commit 证据
- "代码应该在那里" → 必须验证文件真实存在
- "测试应该通过了" → 必须运行测试确认

**✅ 正确做法**:
- Git Log Timeline 回溯 → 代码验证 → 状态更新

---

### 2. 禁止凭空 Code Review

**❌ 错误做法**:
- 只看 Bug 报告不看代码
- 不回溯 Git Log Timeline
- 不验证实际代码实现

**✅ 正确做法**:
- 查看 Git Commit 修改
- 阅读代码实现
- 验证功能逻辑

---

### 3. 禁止凭空推测生产环境状态 ⚠️ **新增强制规则**

**❌ 错误做法**:
- "Research 文档说生产环境有 X 条记录" → **必须连接数据库验证**
- "生产环境应该是..." → **必须查询实际数据**
- "估计生产环境..." → **必须实测验证**
- "基于文档数据..." → **文档可能过时，必须验证**

**✅ 正确做法**:
- 连接生产环境数据库
- 查询实际数据
- 基于实际数据生成结论

**🔴 严重后果**:
- 违反 → **立即更正，公开承认错误**
- 重复违反 → **重新培训，暂停 Scrum Master 权限**

---

### 4. 禁止优先级设置不确认

**❌ 错误做法**:
- P0/P1 优先级不与用户确认
- 不理解业务价值就设置优先级
- 例：Node Informer 设置为 P2（应该是 P0）

**✅ 正确做法**:
- P0/P1 必须与用户确认
- 理解业务价值后再设置优先级

---

### 5. 禁止冗余文件堆积

**❌ 错误做法**:
- 创建多个版本的同一文件（如 sprint-5-plan-final.md）
- 不清理过时的临时文件
- 违反单一数据源原则

**✅ 正确做法**:
- 使用 Git 版本控制，不创建多版本文件
- 定期清理临时文件到 test_reports/

---

## 每周项目审计（Weekly Project Audit）

**时间**: 每五下午

**审计清单**:
1. [ ] 运行 `git log --since="7 days ago"` 分析本周 Commit
2. [ ] 验证所有 IN_PROGRESS → COMPLETED 的 Story 代码实现
3. [ ] 确认没有"虚假完成"的 Story
4. [ ] 更新 DASHBOARD/KANBAN 反映真实进度
5. [ ] 清理冗余文件（test_reports/, 临时分析报告）

**审计报告模板**:

```markdown
# 严谨的项目开发排期执行报告

**执行日期**: YYYY-MM-DD
**执行方法**: Git Log Timeline 回溯 + 代码验证 + Story 状态审计
**执行标准**: 一切基于证据，一切经过验证，一切严谨规范

## 执行总结

### Step 1: Git Log Timeline 分析 ✅
- 分析范围: YYYY-MM-DD 至 YYYY-MM-DD（N天）
- 关键发现:
  - N commits
  - M 个功能相关 commits (feat/fix/refactor)
  - 关键功能: XXX 已完成（commit abc1234）

### Step 2: 代码验证 ✅
- 验证方法: 检查 Git commit → 查看代码文件 → 运行测试
- 关键验证:
  - ✅ 功能 A: N 个文件被修改
  - ✅ 功能 B: M 个文件被修改
  - ❌ 功能 C: 未找到实现代码

### Step 3: Story 状态修正 ✅
- 修正数量: N 个 Story
- 修正列表: [Story ID | 修正前 | 修正后 | 证据]

### Step 4: DASHBOARD/KANBAN 同步 ✅
- DASHBOARD.md: 已更新
- KANBAN.md: 已更新

### Step 5: 文件清理 ✅
- 删除冗余文件: N 个
- 清理列表: [file1, file2, ...]

## 修正后的项目状态

- 修正前进度: X%
- 修正后进度: Y%
- 提升: Z%
```

---

## 总结

### 核心要点

1. **一切基于证据**
   - Git Commit 证据
   - 代码实现验证
   - 生产环境实测（如适用）

2. **5-Step 流程**
   - Git Log Timeline 回溯
   - Code Verification
   - Production Verification（条件触发）
   - Story Status Update
   - DASHBOARD/KANBAN Sync

3. **禁止事项**
   - 禁止凭空更新状态
   - 禁止凭空推测生产环境状态
   - 禁止优先级设置不确认
   - 禁止冗余文件堆积

### 快速检查清单

**更新 Story 状态前**:
- [ ] 运行 Git Log 查找证据
- [ ] 验证代码真实存在
- [ ] 验证生产环境（如适用）
- [ ] 更新 Story 状态
- [ ] 同步 DASHBOARD/KANBAN

---

**相关文档**:
- SKILL.md 主文件: "Story 状态更新流程"章节（核心原则）
- `story_numbering_rules.md`: Story 编号管理细则
- `design_spec_evolution_rules.md`: Design Spec 演进规则细则

**维护者**: Scrum Master
**版本**: 1.0
**最后更新**: 2026-04-03

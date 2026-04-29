#!/bin/bash
#
# Epic-Story 一致性检查脚本
# 用途：验证 Epic 文件的 stories 数组与实际 Story 文件数量一致
#
# 使用方法：
#   bash .claude/skills/pm/epic_story_consistency_check.sh
#

set -e

echo "=== Epic-Story 一致性检查 ==="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error_count=0

# 1. 检查 Epic stories 数量是否与实际 Story 文件数量一致
echo "1️⃣ 检查 Epic stories 数量 vs 实际文件数量:"
for epic_file in docs/scrum/prd/epic-*.md; do
  epic_num=$(basename "$epic_file" | sed -E 's/epic-([0-9]+)-.*/\1/')

  # 检查 Epic 是否有 stories 数组
  if ! grep -q "^stories:" "$epic_file"; then
    echo -e "${RED}❌ Epic-$epic_num: 缺少 stories 数组${NC}"
    ((error_count++))
    continue
  fi

  # 准确统计：只统计以 "- "STORY-${epic_num}-" 开头的行
  epic_stories=$(grep "^  - \"STORY-${epic_num}-" "$epic_file" | wc -l)
  actual_stories=$(ls -1 docs/scrum/story/story-${epic_num}-*.md 2>/dev/null | wc -l)

  if [ "$epic_stories" -ne "$actual_stories" ]; then
    echo -e "${RED}❌ Epic-$epic_num: stories 列表 $epic_stories != 实际文件 $actual_stories${NC}"
    ((error_count++))
  else
    echo -e "${GREEN}✅ Epic-$epic_num: $epic_stories = $actual_stories${NC}"
  fi
done

echo ""
echo "2️⃣ 检查 Story ID 是否在 Epic stories 列表中:"
for story_file in docs/scrum/story/story-*.md; do
  story_id=$(grep "^id: \"" "$story_file" | sed 's/id: "\(.*\)"/\1/')
  epic_num=$(echo "$story_id" | cut -d'-' -f2)
  epic_file=$(ls docs/scrum/prd/epic-${epic_num}-*.md 2>/dev/null)

  if [ -z "$epic_file" ]; then
    echo -e "${RED}❌ $story_id: 找不到对应的 Epic-$epic_num 文件${NC}"
    ((error_count++))
    continue
  fi

  # 检查 Epic 是否有 stories 数组
  if ! grep -q "^stories:" "$epic_file"; then
    echo -e "${YELLOW}⚠️  $story_id: Epic-$epic_num 缺少 stories 数组${NC}"
    ((error_count++))
    continue
  fi

  if ! grep -q "$story_id" "$epic_file"; then
    echo -e "${RED}❌ $story_id: 未在 Epic-$epic_num 的 stories 列表中${NC}"
    ((error_count++))
  fi
done

if [ $error_count -eq 0 ]; then
  echo -e "${GREEN}✅ 所有 Story ID 都在对应的 Epic stories 列表中${NC}"
fi

echo ""
echo "3️⃣ 检查 Epic metadata 完整性:"
missing_fields_count=0
for epic_file in docs/scrum/prd/epic-*.md; do
  epic_num=$(basename "$epic_file" | sed -E 's/epic-([0-9]+)-.*/\1/')

  missing_fields=()

  # 检查必需字段（只检查顶层 YAML front matter）
  if ! grep -q "^id: " "$epic_file"; then missing_fields+=("id"); fi
  if ! grep -q "^title: " "$epic_file"; then missing_fields+=("title"); fi
  if ! grep -q "^description: " "$epic_file"; then missing_fields+=("description"); fi
  if ! grep -q "^status: " "$epic_file"; then missing_fields+=("status"); fi
  if ! grep -q "^priority: " "$epic_file"; then missing_fields+=("priority"); fi
  if ! grep -q "^layer: " "$epic_file"; then missing_fields+=("layer"); fi
  if ! grep -q "^stories:" "$epic_file"; then missing_fields+=("stories"); fi

  if [ ${#missing_fields[@]} -gt 0 ]; then
    echo -e "${RED}❌ Epic-$epic_num: 缺少字段 ${missing_fields[@]}${NC}"
    ((missing_fields_count++))
  else
    echo -e "${GREEN}✅ Epic-$epic_num: metadata 完整${NC}"
  fi
done

echo ""
echo "=== 检查汇总 ==="
if [ $error_count -eq 0 ] && [ $missing_fields_count -eq 0 ]; then
  echo -e "${GREEN}✅ 所有 Epic-Story 一致性检查通过！${NC}"
  exit 0
else
  echo -e "${RED}❌ 发现 $error_count 个一致性问题，$missing_fields_count 个 metadata 缺失问题${NC}"
  exit 1
fi

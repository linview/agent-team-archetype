#!/bin/bash
# Git Workflow Skill for Developer
# File: .codex/skills/developer/git-workflow.skill.sh
# Version: v1.1
# Last Updated: 2026-02-02
#
# Description:
#   Git Worktree 工作流辅助脚本，简化分支管理和 worktree 操作
#   完全通用化，适用于任何 Git 项目
#
# Features:
#   ✅ 自动检测 Git 仓库根目录和项目名称
#   ✅ 使用相对路径，不依赖硬编码路径
#   ✅ 支持 master/main 分支自动切换
#   ✅ 彩色输出（info/success/warning/error）
#
# Usage:
#   source /path/to/git-workflow.skill.sh
#   git-workflow.feature.start story-06-01 "pod handler"
#   git-workflow.feature.sync
#   git-workflow.feature.submit
#   git-workflow.feature.finish story-06-01
#   git-workflow.worktree.list
#
# Installation:
#   Add to ~/.bashrc or ~/.zshrc:
#     source /path/to/your/project/.codex/skills/developer/git-workflow.skill.sh
#
# Environment Variables:
#   WORKTREE_ROOT_OVERRIDE   覆盖 worktree 根目录路径
#   GIT_WORKFLOW_DEBUG=1     启用调试输出

set -e

# ============================================
# Configuration
# ============================================

# 自动检测 Git 仓库根目录
PROJ_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$PROJ_ROOT" ]; then
  echo "❌ 错误：当前不在 Git 仓库中"
  exit 1
fi

# 自动检测项目名称
PROJECT_NAME=$(basename "$PROJ_ROOT")

# Worktree 根目录（与主仓库同级）
# 可通过环境变量 WORKTREE_ROOT_OVERRIDE 覆盖
WORKTREE_ROOT=${WORKTREE_ROOT_OVERRIDE:-$(dirname "$PROJ_ROOT")/${PROJECT_NAME}-worktrees}

# 调试信息（可通过 GIT_WORKFLOW_DEBUG=1 启用）
if [ "$GIT_WORKFLOW_DEBUG" = "1" ]; then
  echo "🔧 Debug Info:"
  echo "   PROJ_ROOT: $PROJ_ROOT"
  echo "   PROJECT_NAME: $PROJECT_NAME"
  echo "   WORKTREE_ROOT: $WORKTREE_ROOT"
  echo ""
fi

# ============================================
# Helper Functions
# ============================================

# 打印信息（带颜色）
info() {
  echo "\033[0;34mℹ️  $*\033[0m"
}

success() {
  echo "\033[0;32m✅ $*\033[0m"
}

warning() {
  echo "\033[0;33m⚠️  $*\033[0m"
}

error() {
  echo "\033[0;31m❌ $*\033[0m"
}

# 检查是否在主仓库目录
check_in_main_repo() {
  if [ ! -d "$PROJ_ROOT/.git" ]; then
    error "主仓库不存在: $PROJ_ROOT"
    exit 1
  fi
}

# 检查是否在 worktree 目录
check_in_worktree() {
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  if [ -z "$CURRENT_BRANCH" ]; then
    error "当前不在 Git 仓库中"
    exit 1
  fi
}

# 切换到主仓库目录
cd_to_main_repo() {
  check_in_main_repo
  cd "$PROJ_ROOT"
}

# ============================================
# Git Workflow Functions
# ============================================

# git-workflow.feature.start <story_id> <summary>
# 创建功能分支 worktree
git-workflow.feature.start() {
  if [ $# -lt 2 ]; then
    error "用法: git-workflow.feature.start <story_id> <summary>"
    echo ""
    echo "示例:"
    echo "  git-workflow.feature.start story-06-01 \"pod handler\""
    echo "  → 创建分支: feat/story-06-01-pod-handler"
    echo "  → 创建 worktree: ../${PROJECT_NAME}-worktrees/story-06-01-pod-handler/"
    exit 1
  fi

  STORY_ID="$1"
  SUMMARY="$2"

  # 构建分支名和 worktree 目录名
  BRANCH_NAME="feat/$STORY_ID-$SUMMARY"
  WORKTREE_NAME="$STORY_ID-$SUMMARY"
  WORKTREE_PATH="$WORKTREE_ROOT/$WORKTREE_NAME"

  # 检查 worktree 是否已存在
  if [ -d "$WORKTREE_PATH" ]; then
    error "Worktree 已存在: $WORKTREE_PATH"
    exit 1
  fi

  # 创建 worktree 根目录（如果不存在）
  mkdir -p "$WORKTREE_ROOT"

  # 在主工作树中操作
  cd_to_main_repo

  # 拉取最新代码
  info "拉取最新代码..."
  git fetch origin
  git checkout master 2>/dev/null || git checkout main
  git pull origin master 2>/dev/null || git pull origin main

  # 创建新分支
  info "创建新分支: $BRANCH_NAME"
  git checkout -b "$BRANCH_NAME"

  # 创建 worktree
  info "创建 worktree: $WORKTREE_PATH"
  git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"

  echo ""
  success "Worktree 创建成功！"
  echo "   项目: $PROJECT_NAME"
  echo "   Worktree 路径: $WORKTREE_PATH"
  echo "   分支名: $BRANCH_NAME"
  echo ""
  echo "下一步:"
  echo "  cd $WORKTREE_PATH"
  echo "  claude-code"
}

# git-workflow.feature.sync
# 同步上游 master
git-workflow.feature.sync() {
  check_in_worktree

  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

  if [ "$CURRENT_BRANCH" = "master" ]; then
    error "当前在 master 分支，无需同步"
    exit 1
  fi

  info "同步上游 master..."
  echo "   当前分支: $CURRENT_BRANCH"

  # 拉取最新代码
  git fetch origin

  # 合并 origin/master
  info "合并 origin/master..."
  git merge origin/master

  success "同步完成"
  echo ""
  echo "下一步:"
  echo "  git push origin $CURRENT_BRANCH"
}

# git-workflow.feature.submit
# 推送到远程并创建 MR
git-workflow.feature.submit() {
  check_in_worktree

  # 获取当前 worktree 分支
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

  if [ "$CURRENT_BRANCH" = "master" ]; then
    error "当前在 master 分支，不能创建 MR"
    exit 1
  fi

  info "提交 MR..."
  echo "   当前分支: $CURRENT_BRANCH"

  # 推送到远程
  info "推送到远程..."
  git push origin "$CURRENT_BRANCH"

  # 创建 MR（使用 glab）
  if command -v glab &> /dev/null; then
    echo ""
    info "创建 GitLab MR..."

    # 从分支名提取 story_id 和 summary
    STORY_ID=$(echo "$CURRENT_BRANCH" | sed 's/feat\///' | cut -d'-' -f1-2)
    SUMMARY=$(echo "$CURRENT_BRANCH" | sed "s/feat/$STORY_ID-//" | sed 's/^-//')

    glab mr create \
      --title "feat($STORY_ID): $SUMMARY" \
      --description "Closes $STORY_ID

## 实现内容

<!-- TODO: 填写实现内容 -->

## 测试

- [ ] 单元测试通过
- [ ] SIT 测试通过

## 相关文档

- Story 文档: docs/scrum/story/$STORY_ID-*.md" \
      --target-branch master \
      --source-branch "$CURRENT_BRANCH" \
      --web

    success "MR 已创建（浏览器已打开）"
  else
    echo ""
    warning "glab CLI 未安装，无法自动创建 MR"
    echo "请手动在 GitLab Web UI 创建 MR:"
    echo "  https://git.example.com/<YOUR_USERNAME>/{PROJECT_NAME}/-/merge_requests/new"
  fi
}

# git-workflow.feature.finish <story_id>
# 清理 worktree
git-workflow.feature.finish() {
  if [ $# -lt 1 ]; then
    error "用法: git-workflow.feature.finish <story_id>"
    echo ""
    echo "示例:"
    echo "  git-workflow.feature.finish story-06-01"
    exit 1
  fi

  STORY_ID="$1"

  # 获取当前分支名
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  WORKTREE_NAME=$(echo "$CURRENT_BRANCH" | sed "s/feat\///")

  # 从分支名提取 worktree 路径
  WORKTREE_PATH="$WORKTREE_ROOT/$WORKTREE_NAME"

  # 检查 worktree 是否存在
  if [ ! -d "$WORKTREE_PATH" ]; then
    error "Worktree 不存在: $WORKTREE_PATH"
    exit 1
  fi

  # 检查是否有未提交的更改
  cd "$WORKTREE_PATH"
  uncommitted=$(git status --short | wc -l)
  if [ "$uncommitted" -gt 0 ]; then
    warning "Worktree 有 $uncommitted 个未提交的文件"
    echo "请先提交或暂存更改"
    exit 1
  fi

  # 切换到主仓库
  cd_to_main_repo

  # 删除 worktree
  info "删除 worktree: $WORKTREE_PATH"
  git worktree remove "$WORKTREE_PATH"

  # 询问是否删除分支
  echo ""
  read -p "是否同时删除分支 '$CURRENT_BRANCH'? [y/N] " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    git branch -d "$CURRENT_BRANCH"
    success "分支已删除: $CURRENT_BRANCH"
  fi

  success "Worktree 已清理"
}

# git-workflow.worktree.list
# 列出所有 worktree 及其状态
git-workflow.worktree.list() {
  cd_to_main_repo

  echo "📋 Git Worktree 列表"
  echo "===================="
  echo "项目: $PROJECT_NAME"
  echo "主仓库: $PROJ_ROOT"
  echo "Worktree 根目录: $WORKTREE_ROOT"
  echo ""
  git worktree list
  echo ""

  # 显示分支状态
  echo "🔍 分支状态"
  echo "=========="
  git worktree list | while read -r line; do
    path=$(echo "$line" | awk '{print $1}')
    commit=$(echo "$line" | awk '{print $2}')
    branch=$(echo "$line" | awk '{print $3}' | sed 's/[\[\]]//g')

    if [ -n "$branch" ]; then
      cd "$path"
      status=$(git status --short | wc -l)
      if [ "$status" -eq 0 ]; then
        echo "✅ $branch (干净)"
      else
        echo "🟡 $branch ($status 个文件未提交)"
      fi
    fi
  done
}

# ============================================
# Help
# ============================================

git-workflow.help() {
  cat << 'EOF'
Git Workflow Skill - 使用说明
=============================

功能分支管理:
  git-workflow.feature.start <story_id> <summary>   创建功能分支 worktree
  git-workflow.feature.sync                          同步上游 master/main
  git-workflow.feature.submit                        推送并创建 MR
  git-workflow.feature.finish <story_id>             清理 worktree

Worktree 管理:
  git-workflow.worktree.list                         列出所有 worktree

帮助:
  git-workflow.help                                   显示此帮助信息

环境变量:
  WORKTREE_ROOT_OVERRIDE   覆盖 worktree 根目录路径
  GIT_WORKFLOW_DEBUG=1     启用调试输出

示例:
  # 创建功能分支
  git-workflow.feature.start story-06-01 "pod handler"

  # 在 worktree 中开发
  cd ../project-name-worktrees/story-06-01-pod-handler
  # ... 开发代码 ...
  git add .
  git commit -m "feat: implement pod handler"

  # 同步上游 master/main
  git-workflow.feature.sync

  # 提交 MR
  git-workflow.feature.submit

  # MR 合并后清理
  cd ../project-name
  git-workflow.feature.finish story-06-01

特性:
  ✅ 自动检测 Git 仓库根目录
  ✅ 自动检测项目名称
  ✅ 适用于任何 Git 项目
  ✅ 支持 master/main 分支
  ✅ 彩色输出（info/success/warning/error）

文档:
  Developer SKILL: .codex/skills/developer/SKILL.md
  项目工作流指南: docs/guides/git-workflow.md
EOF
}

# ============================================
# Main Entry Point
# ============================================

# 如果直接执行此脚本（而非 source），显示帮助
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  git-workflow.help "$@"
fi

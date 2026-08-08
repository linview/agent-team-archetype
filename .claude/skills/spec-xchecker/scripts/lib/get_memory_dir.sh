#!/bin/bash
# .claude/skills/spec-xchecker/utils/get_memory_dir.sh
#
# 获取项目的 Claude Code memory 目录路径
#
# 用法:
#   source utils/get_memory_dir.sh
#   MEMORY_DIR=$(get_memory_dir)
#   或
#   bash utils/get_memory_dir.sh /path/to/project

get_memory_dir() {
    local project_dir="${1:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"

    # 将项目路径转换为 Claude memory 目录路径
    # /home/user/Proj/{PROJECT_NAME}
    # → ~/.claude/projects/-home-user-Proj-{PROJECT_NAME}/memory

    # 去掉开头的 /
    local encoded_path="${project_dir#/}"
    # 替换所有 / 为 -
    encoded_path="-${encoded_path//\//-}"

    echo "${HOME}/.claude/projects/${encoded_path}/memory"
}

# 测试
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    get_memory_dir "$@"
fi

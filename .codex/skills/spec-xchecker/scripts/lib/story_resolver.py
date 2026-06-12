#!/usr/bin/env python3
"""
Story ID 提取与 Design Spec 加载器

功能:
1. 从 Git 分支名提取 Story ID
2. 从 Commit Message 提取 Story ID
3. 加载对应的 Design Spec 文档
4. 多层回退机制
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def extract_story_id_from_branch(branch_name: str) -> Optional[str]:
    """
    从 Git 分支名提取 Story ID

    支持的格式:
    - feat/story-15-23-fix-{BUSINESS_DOMAIN} → 15-23
    - story-15-13-spec-xchecker → 15-13
    - STORY-15-10 → 15-10

    Args:
        branch_name: Git 分支名

    Returns:
        Story ID (例如: "15-23") 或 None
    """
    # 匹配 story-{数字}-{数字} 模式（不区分大小写）
    pattern = r'story[-_]?(\d+[-_]\d+)'
    match = re.search(pattern, branch_name, re.IGNORECASE)

    if match:
        # 统一格式为 15-23（用横杠）
        return match.group(1).replace('_', '-')

    return None


def extract_story_id_from_commit(commit_message: str) -> Optional[str]:
    """
    从 Commit Message 提取 Story ID

    支持的格式:
    - STORY-15-13: 添加 Stop Hook → 15-13
    - story-15-23: 修复 bug → 15-23

    Args:
        commit_message: Git commit message

    Returns:
        Story ID (例如: "15-23") 或 None
    """
    # 匹配 STORY-{数字}-{数字}: 模式（不区分大小写）
    pattern = r'STORY[-_]?(\d+[-_]\d+)\s*:'
    match = re.search(pattern, commit_message, re.IGNORECASE)

    if match:
        return match.group(1).replace('_', '-')

    return None


def get_current_story_id(project_dir: str) -> Optional[str]:
    """
    获取当前 Story ID（多层回退机制）

    回退顺序:
    1. 从当前 Git 分支名提取
    2. 从最新 Commit Message 提取
    3. 返回 None（无法识别）

    Args:
        project_dir: 项目根目录

    Returns:
        Story ID (例如: "15-23") 或 None
    """
    # 方法 1: 从分支名提取
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=True
        )
        branch_name = result.stdout.strip()
        story_id = extract_story_id_from_branch(branch_name)
        if story_id:
            return story_id
    except subprocess.CalledProcessError:
        pass

    # 方法 2: 从最新 Commit Message 提取
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=True
        )
        commit_message = result.stdout.strip()
        story_id = extract_story_id_from_commit(commit_message)
        if story_id:
            return story_id
    except subprocess.CalledProcessError:
        pass

    # 无法识别
    return None


def find_story_document(story_id: str, project_dir: str) -> Optional[Path]:
    """
    查找 Story 文档

    搜索路径:
    1. docs/scrum/story/story-{story_id}-*.md
    2. docs/scrum/story/story-13-{story_id}-*.md (如果是 15-23，搜索 story-13-15-23)

    Args:
        story_id: Story ID (例如: "15-23")
        project_dir: 项目根目录

    Returns:
        Story 文档路径 或 None
    """
    story_dir = Path(project_dir) / 'docs' / 'scrum' / 'story'

    # 模式 1: story-{story_id}-*.md
    pattern1 = f'story-{story_id}-*.md'
    matches = list(story_dir.glob(pattern1))
    if matches:
        return matches[0]  # 返回第一个匹配

    # 模式 2: story-13-{story_id}-*.md (兼容 15-23 的命名)
    story_num = story_id.split('-')[0]
    pattern2 = f'story-13-{story_id}-*.md'
    matches = list(story_dir.glob(pattern2))
    if matches:
        return matches[0]

    return None


def load_design_spec(story_id: str, project_dir: str) -> Optional[str]:
    """
    加载 Design Spec 文档

    流程:
    1. 查找 Story 文档
    2. 从 Story 文档中提取 Design Spec 引用
    3. 读取 Design Spec 内容

    Args:
        story_id: Story ID (例如: "15-23")
        project_dir: 项目根目录

    Returns:
        Design Spec 内容 或 None
    """
    # 1. 查找 Story 文档
    story_doc = find_story_document(story_id, project_dir)
    if not story_doc:
        return None

    # 2. 读取 Story 文档内容
    try:
        story_content = story_doc.read_text(encoding='utf-8')
    except Exception:
        return None

    # 3. 提取 Design Spec 引用（支持多种格式）
    design_spec_ref = None

    # 格式 1: frontmatter 中的 design_docs 字段（v2.6 修复）
    yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    yaml_match = re.search(yaml_pattern, story_content, re.MULTILINE | re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        if 'design_docs:' in yaml_content:
            # 提取 design_docs 列表
            pattern = r'design_docs:\s*\n\s*-\s*"([^"]+\.md)"'
            match = re.search(pattern, yaml_content)
            if match:
                design_spec_ref = match.group(1).strip()
                # 移除锚点（#xxx）
                design_spec_ref = re.sub(r'#.*$', '', design_spec_ref)

    # 格式 2: Markdown 链接格式 [文本](路径.md)（v2.6 修复）
    if not design_spec_ref:
        link_pattern = r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)'
        link_matches = re.findall(link_pattern, story_content)
        for link_text, link_path in link_matches:
            if 'Design Spec' in link_text or '设计' in link_text:
                design_spec_ref = link_path
                # 移除锚点
                design_spec_ref = re.sub(r'#.*$', '', design_spec_ref)
                break

    # 格式 3: "Design Spec: xxx.md" 或 "Design Spec 参考: xxx"（原有格式）
    if not design_spec_ref:
        pattern = r'Design\s+Spec\s*[:：]\s*([^\n]+\.md)'
        match = re.search(pattern, story_content, re.IGNORECASE)
        if match:
            design_spec_ref = match.group(1).strip()

    if not design_spec_ref:
        return None

    # 4. 解析路径（相对路径或绝对路径）
    if design_spec_ref.startswith('../'):
        # 相对路径（从 Story 文档目录）
        design_spec_path = (story_doc.parent / design_spec_ref).resolve()
    elif design_spec_ref.startswith('../../'):
        # 相对路径（从 Story 文档目录向上两层）
        design_spec_path = (story_doc.parent.parent / design_spec_ref[6:]).resolve()
    elif design_spec_ref.startswith('/'):
        # 绝对路径
        design_spec_path = Path(design_spec_ref)
    elif design_spec_ref.startswith('docs/'):
        # 相对项目根目录
        design_spec_path = Path(project_dir) / design_spec_ref
    else:
        # 相对项目根目录的 docs/design/
        design_spec_path = Path(project_dir) / 'docs' / 'design' / design_spec_ref

    # 5. 读取 Design Spec 内容
    try:
        return design_spec_path.read_text(encoding='utf-8')
    except Exception:
        return None


def extract_acceptance_criteria(story_content: str) -> list[str]:
    """
    从 Story 文档提取 Acceptance Criteria (AC)

    支持的格式:
    - YAML frontmatter: acceptance_criteria: ["AC-1: xxx", "AC-2: yyy"]
    - ## AC / ## Acceptance Criteria
    - ### AC-01, AC-02, ...
    - - [ ] AC 文本列表

    Args:
        story_content: Story 文档内容

    Returns:
        AC 列表 (例如: ["AC-01: 验证...", "AC-02: 检查..."])
    """
    ac_list = []

    # 优先级 1: 从 YAML frontmatter 中提取（v2.4 修复）
    yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    yaml_match = re.search(yaml_pattern, story_content, re.MULTILINE | re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        if 'acceptance_criteria:' in yaml_content:
            # 提取 AC 列表（支持两种格式）
            # 格式 1: - "AC-1: xxx"
            pattern1 = r'^\s*-\s*"([^"]+)"'
            matches = re.findall(pattern1, yaml_content, re.MULTILINE)
            if matches:
                return matches

            # 格式 2: - AC-1: xxx（无引号）
            pattern2 = r'^\s*-\s*(AC[-_]?\d+[:：]\s*.+)'
            matches = re.findall(pattern2, yaml_content, re.MULTILINE)
            if matches:
                return matches

    # 优先级 2: 从 Markdown ## AC 章节提取（fallback）
    ac_section_pattern = r'##\s*(AC|Acceptance Criteria|验收标准)(.*?)^(##\s*)'
    match = re.search(ac_section_pattern, story_content, re.MULTILINE | re.DOTALL | re.IGNORECASE)

    if not match:
        return ac_list

    ac_section = match.group(2)

    # 提取 AC 列表
    # 格式 1: - [ ] AC-01: xxx
    pattern1 = r'-\s*\[\s*\]\s*(AC[-_]?\d*[:：]\s*.*?)(?=\n|$)'
    matches = re.findall(pattern1, ac_section, re.MULTILINE)
    ac_list.extend(matches)

    # 格式 2: ### AC-01 / AC-02
    if not matches:
        pattern2 = r'###\s*(AC[-_]?\d+[:：]\s*.*?)(?=\n|$)'
        matches = re.findall(pattern2, ac_section, re.MULTILINE)
        ac_list.extend(matches)

    # 格式 3: - xxx (没有 AC 前缀)
    if not matches:
        pattern3 = r'[-*]\s*(.*?)(?=\n|$)'
        matches = re.findall(pattern3, ac_section, re.MULTILINE)
        # 过滤掉空行和非 AC 内容
        ac_list.extend([m for m in matches if m.strip() and len(m.strip()) > 10])

    # Fallback: 如果未找到 AC 章节，尝试从全文解析
    if not ac_list:
        # 匹配 AC 标题（例如：### AC-1: DDL 变更记录完整）
        pattern_full = r'^###\s+AC[-_]?\d+[:：]\s*(.+?)$'
        matches = re.findall(pattern_full, story_content, re.MULTILINE)
        if matches:
            ac_list = [f"AC-{i+1}: {title}" for i, title in enumerate(matches)]

    return ac_list


# CLI 测试接口
if __name__ == '__main__':
    import sys

    project_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    print(f"项目目录: {project_dir}")
    print()

    # 测试 Story ID 提取
    story_id = get_current_story_id(project_dir)
    print(f"Story ID: {story_id or '无法识别'}")
    print()

    if story_id:
        # 测试 Story 文档查找
        story_doc = find_story_document(story_id, project_dir)
        print(f"Story 文档: {story_doc or '未找到'}")
        print()

        # 测试 Design Spec 加载
        design_spec = load_design_spec(story_id, project_dir)
        if design_spec:
            print(f"Design Spec: 已加载 ({len(design_spec)} 字符)")
            print(f"前 200 字符:")
            print(design_spec[:200])
            print()
        else:
            print("Design Spec: 未找到")
            print()

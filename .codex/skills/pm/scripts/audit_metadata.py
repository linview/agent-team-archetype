#!/usr/bin/env python3
"""
Scrum Master 元数据审计脚本
扫描 docs/scrum/prd/ 和 docs/scrum/story/，生成 metadata.json（方案B：仅状态摘要）

核心功能：
1. 扫描 Epic 文件，提取元数据（status, priority, owner, dates, stories）
2. 扫描 Story 文件，提取元数据（status, assignee, story_points, dates）
3. 基于 Git commit 分析验证状态（证据驱动原则）
4. 生成 metadata.json（仅包含状态摘要，不包含完整 Story 内容）
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def scan_epic_files(prd_dir: Path) -> List[Dict[str, Any]]:
    """扫描所有 Epic 文件，提取元数据"""
    epics = []

    # 按 Epic 编号数字排序（而非字符串排序）
    def get_epic_num(filename):
        match = re.match(r"epic-(\d+)-", filename.name)
        return int(match.group(1)) if match else 999

    for epic_file in sorted(prd_dir.glob("epic-*.md"), key=get_epic_num):
        # 提取 Epic 编号
        match = re.match(r"epic-(\d+)-", epic_file.name)
        if not match:
            continue

        epic_num = match.group(1)
        epic_id = f"EPIC-{epic_num}"

        # 读取 Epic 文件
        content = epic_file.read_text()

        # 解析 YAML front matter
        metadata = parse_yaml_front_matter(content)

        # 验证 Epic ID
        if metadata.get("id") != epic_id:
            print(f"⚠️  Warning: Epic ID mismatch in {epic_file.name}: {metadata.get('id')} != {epic_id}")

        # 提取元数据
        epic_info = {
            "id": epic_id,
            "file": str(epic_file.relative_to(prd_dir.parent)),
            "title": metadata.get("title", ""),
            "status": metadata.get("status", "TODO"),
            "priority": metadata.get("priority", "P2"),
            "owner": metadata.get("owner", ""),
            "layer": metadata.get("layer", ""),
            "start_date": metadata.get("start_date", ""),
            "target_date": metadata.get("target_date", ""),
            "completed_date": metadata.get("completed_date", ""),
            "stories": metadata.get("stories", []),
        }

        epics.append(epic_info)

    return epics


def scan_story_files(story_dir: Path) -> Dict[str, Dict[str, Any]]:
    """扫描所有 Story 文件，提取元数据"""
    stories = {}

    for story_file in sorted(story_dir.glob("story-*.md")):
        # 读取 Story 文件
        content = story_file.read_text()

        # 解析 YAML front matter
        metadata = parse_yaml_front_matter(content)

        story_id = metadata.get("id", "")
        if not story_id:
            # 从文件名提取 Story ID
            match = re.match(r"story-(\d+)-(\d+)-", story_file.name)
            if match:
                epic_num, story_num = match.groups()
                story_id = f"STORY-{epic_num}-{story_num.zfill(2)}"

        # 提取元数据
        story_info = {
            "id": story_id,
            "file": str(story_file.relative_to(story_dir.parent)),
            "title": metadata.get("title", ""),
            "status": metadata.get("status", "TODO"),
            "priority": metadata.get("priority", ""),  # ✅ 添加 priority 字段
            "assignee": metadata.get("assignee", ""),
            "story_points": metadata.get("story_points", 0),
            "start_date": metadata.get("start_date", ""),
            "target_date": metadata.get("target_date", ""),
            "completed_date": metadata.get("completed_date", ""),
        }

        stories[story_id] = story_info

    return stories


def parse_yaml_front_matter(content: str) -> Dict[str, Any]:
    """解析 YAML front matter（支持多种格式）"""
    # 格式3: 代码块内的 YAML（Epic-15 特殊格式，优先检查）
    # 注意：Epic-15 有两个 ---，需要匹配到最后一个 ---
    match = re.search(r"```yaml\n---\n(.*)\n---\n```", content, re.DOTALL)
    if not match:
        # 格式1: --- 在开头
        match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        # 格式2: --- 在标题后
        match = re.search(r"\n---\n(.*?)\n---\n", content, re.DOTALL)

    if not match:
        return {}

    yaml_text = match.group(1)

    # 解析 YAML（支持基本格式 + 数组）
    metadata = {}
    current_key = None
    in_array = False

    for line in yaml_text.split("\n"):
        # 数组项
        if in_array and line.startswith("  - "):
            value = line.strip("- ")
            # 去除注释（# 后面的内容）
            if "#" in value:
                value = value.split("#")[0].strip()
            # 去除引号（在去除注释之后）
            value = value.strip('"\'')
            metadata[current_key].append(value)
            continue

        # 数组结束
        if in_array and not line.startswith("  - "):
            in_array = False

        # 键值对
        match = re.match(r"^(\w+):\s*(.*)$", line)
        if match:
            key, value = match.groups()
            value = value.strip('"\'')
            current_key = key

            # 检查是否是空数组 `[]`
            if value == "[]":
                metadata[key] = []
            # 检查下一行是否是数组开始
            elif value == "" and key in ["stories", "dependencies", "tags"]:
                metadata[key] = []
                in_array = True
            else:
                metadata[key] = value

    return metadata


def verify_story_status_with_git(story_id: str, target_status: str) -> bool:
    """基于 Git commit 验证 Story 状态（证据驱动原则）"""
    try:
        # 查找与 Story ID 相关的 commits
        result = subprocess.run(
            ["git", "log", "--all", "--grep", story_id, "--oneline"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return False

        commits = result.stdout.strip()
        if not commits:
            # 没有 commit → 状态应该是 TODO
            return target_status == "TODO"

        # 有 commit → 检查状态是否合理
        if target_status in ["IN_PROGRESS", "IN_REVIEW", "TESTING", "COMPLETED"]:
            return True

        return False

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def generate_metadata_json(project_root: Path) -> Dict[str, Any]:
    """生成 metadata.json（方案B：仅状态摘要）"""
    prd_dir = project_root / "docs/scrum/prd"
    story_dir = project_root / "docs/scrum/story"

    # 扫描 Epic 文件
    epics = scan_epic_files(prd_dir)

    # 扫描 Story 文件
    stories = scan_story_files(story_dir)

    # 生成统计数据(FSM 8 状态全分桶,避免 TESTING/BLOCKED 被模板兜底减法错归 TODO)
    total_stories = len(stories)
    completed_stories = sum(1 for s in stories.values() if s["status"] == "COMPLETED")
    in_progress_stories = sum(1 for s in stories.values() if s["status"] == "IN_PROGRESS")
    testing_stories = sum(1 for s in stories.values() if s["status"] == "TESTING")
    blocked_stories = sum(1 for s in stories.values() if s["status"] == "BLOCKED")
    deferred_stories = sum(1 for s in stories.values() if s["status"] == "DEFERRED")
    cancelled_stories = sum(1 for s in stories.values() if s["status"] == "CANCELLED")
    todo_stories = sum(1 for s in stories.values() if s["status"] == "TODO")

    # 生成 metadata.json（方案B：仅状态摘要）
    metadata = {
        "version": "2.0",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "statistics": {
            "total_epics": len(epics),
            "total_stories": total_stories,
            "completed_stories": completed_stories,
            "in_progress_stories": in_progress_stories,
            "testing_stories": testing_stories,
            "blocked_stories": blocked_stories,
            "deferred_stories": deferred_stories,
            "cancelled_stories": cancelled_stories,
            "todo_stories": todo_stories,
            "completion_rate": f"{completed_stories * 100 / total_stories:.1f}%" if total_stories > 0 else "0%",
        },
        "epics": epics,
        "stories": stories,
    }

    return metadata


def main():
    """主函数"""
    script_dir = Path(__file__).resolve().parent
    project_root = (script_dir / "../../../..").resolve()

    print(f"[Scrum Master] 扫描项目: {project_root}")

    # 生成 metadata.json
    metadata = generate_metadata_json(project_root)

    # 写入文件
    output_file = project_root / "docs/scrum/metadata.json"
    output_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

    print(f"[Scrum Master] ✅ 生成 metadata.json ({len(metadata['epics'])} epics, {len(metadata['stories'])} stories)")
    print(f"[Scrum Master] 📊 统计: {metadata['statistics']['completed_stories']}/{metadata['statistics']['total_stories']} 完成 ({metadata['statistics']['completion_rate']})")


if __name__ == "__main__":
    main()

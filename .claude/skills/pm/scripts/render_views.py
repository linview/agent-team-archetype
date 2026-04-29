#!/usr/bin/env python3
"""
Scrum Master 视图渲染脚本
从 metadata.json 渲染 KANBAN.md 和 DASHBOARD.md（基于 Jinja2 模板）

核心功能：
1. 读取 metadata.json（状态摘要）
2. 基于 Jinja2 模板渲染 KANBAN.md
3. 基于 Jinja2 模板渲染 DASHBOARD.md
4. 验证格式完整性（防止文档退化）
"""

import os
import json
from pathlib import Path
from datetime import datetime
from jinja2 import Template


def load_metadata(project_root: Path) -> dict:
    """加载 metadata.json"""
    metadata_file = project_root / "docs/scrum/metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"metadata.json 不存在: {metadata_file}")

    with open(metadata_file) as f:
        return json.load(f)


def group_stories_by_status(metadata: dict) -> dict:
    """按状态分组 Story"""
    grouped = {
        "TODO": [],
        "IN_PROGRESS": [],
        "IN_REVIEW": [],
        "TESTING": [],
        "COMPLETED": [],
        "BLOCKED": [],
        "CANCELLED": [],
    }

    for story_id, story_info in metadata["stories"].items():
        status = story_info.get("status", "TODO")
        if status in grouped:
            grouped[status].append({**story_info, "id": story_id})

    return grouped


def render_kanban_md(metadata: dict) -> str:
    """渲染 KANBAN.md（使用 Unicode 泳道图）"""
    # 导入 Unicode 渲染器
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from kanban_renderer import render_kanban_unicode

    return render_kanban_unicode(metadata)


def render_dashboard_md(metadata: dict, template_str: str) -> str:
    """渲染 DASHBOARD.md（Jinja2 模板）"""
    # 预先计算每个 Epic 的完成统计
    for epic in metadata["epics"]:
        completed_count = 0
        for story_id in epic.get("stories", []):
            story = metadata["stories"].get(story_id)
            if story and story.get("status") == "COMPLETED":
                completed_count += 1

        total_count = len(epic.get("stories", []))
        completion_rate = (completed_count * 100 // total_count) if total_count > 0 else 0

        epic["completed_count"] = completed_count
        epic["total_count"] = total_count
        epic["completion_rate"] = completion_rate

    # 准备模板数据
    template_data = {
        "update_time": metadata["generated_at"],
        "statistics": metadata["statistics"],
        "epics": metadata["epics"],
        "stories": metadata["stories"],
    }

    # 渲染模板
    template = Template(template_str)
    return template.render(**template_data)


def validate_kanban_format(content: str) -> bool:
    """验证 KANBAN.md 格式完整性（防止文档退化）"""
    # Unicode 泳道图格式验证
    required_elements = [
        "```text",  # 代码块
        "┌─",  # Unicode box-drawing 字符
        "📋 待办",  # 待办泳道
        "🚧 进行中",  # 进行中泳道
        "✅ 已完成",  # 已完成泳道
    ]

    for element in required_elements:
        if element not in content:
            print(f"❌ 缺少元素: {element}")
            return False

    # 验证行数（防止内容丢失）
    lines = content.split("\n")
    if len(lines) < 100:
        print(f"❌ KANBAN.md 行数过少: {len(lines)} < 100")
        return False

    print(f"✅ KANBAN.md 格式验证通过 ({len(lines)} 行)")
    return True


def validate_dashboard_format(content: str) -> bool:
    """验证 DASHBOARD.md 格式完整性（防止文档退化）"""
    required_sections = [
        "## 📊 Epic 进度总览",
        "## 📈 Story 统计",
    ]

    for section in required_sections:
        if section not in content:
            print(f"❌ 缺少章节: {section}")
            return False

    # 验证行数（防止内容丢失）
    lines = content.split("\n")
    if len(lines) < 80:
        print(f"❌ DASHBOARD.md 行数过少: {len(lines)} < 80")
        return False

    print(f"✅ DASHBOARD.md 格式验证通过 ({len(lines)} 行)")
    return True


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent.parent

    print(f"[Scrum Master] 渲染视图: {project_root}")

    # 加载 metadata.json
    metadata = load_metadata(project_root)

    # 渲染 KANBAN.md（Unicode 泳道图）
    kanban_content = render_kanban_md(metadata)
    if not validate_kanban_format(kanban_content):
        print("❌ KANBAN.md 格式验证失败，拒绝写入")
        return

    kanban_output = project_root / "docs/scrum/KANBAN.md"
    kanban_output.write_text(kanban_content)
    print(f"✅ KANBAN.md 已更新 ({len(kanban_content.split(chr(10)))} 行)")

    # 渲染 DASHBOARD.md（Jinja2 模板）
    template_dir = project_root / ".claude/skills/pm/templates"
    dashboard_template_file = template_dir / "dashboard_template.md.j2"

    if not dashboard_template_file.exists():
        print(f"❌ DASHBOARD 模板不存在: {dashboard_template_file}")
        return

    dashboard_template_str = dashboard_template_file.read_text()
    dashboard_content = render_dashboard_md(metadata, dashboard_template_str)
    if not validate_dashboard_format(dashboard_content):
        print("❌ DASHBOARD.md 格式验证失败，拒绝写入")
        return

    dashboard_output = project_root / "docs/scrum/DASHBOARD.md"
    dashboard_output.write_text(dashboard_content)
    print(f"✅ DASHBOARD.md 已更新 ({len(dashboard_content.split(chr(10)))} 行)")


if __name__ == "__main__":
    main()

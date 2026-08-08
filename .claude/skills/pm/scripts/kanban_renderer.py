#!/usr/bin/env python3
"""
KANBAN Unicode 泳道图渲染器
使用 Unicode box-drawing 字符绘制真正的泳道图
"""

from typing import List, Dict, Any


def render_story_card(story: Dict[str, Any], width: int = 72) -> List[str]:
    """渲染单个 Story 卡片"""
    lines = []
    priority = story.get('priority', '')

    # P0 Story 高亮显示（添加 🔴 标记）
    priority_mark = " 🔴" if priority == 'P0' else ""

    # 卡片顶部边框（P0 使用双线边框）
    if priority == 'P0':
        lines.append("╔═" + "═" * (width - 4) + "╗")
    else:
        lines.append("┌─" + "─" * (width - 4) + "┐")

    # Story ID 和标题
    id_title = f"{story['id']}: {story['title']}"
    sp_text = f"({story.get('story_points', 0)} SP)"
    line1 = f"│ {id_title} {sp_text}{priority_mark}"

    # 填充到固定宽度
    padding = width - len(line1) - 1
    line1 += " " * padding + "│"
    lines.append(line1)

    # 负责人
    assignee = story.get('assignee') or 'TBD'
    line2 = f"│ 👤 {assignee}"
    padding = width - len(line2) - 1
    line2 += " " * padding + "│"
    lines.append(line2)

    # 日期
    start_date = story.get('start_date') or 'TBD'
    target_date = story.get('target_date') or 'TBD'
    line3 = f"│ 📅 {start_date} ~ {target_date}"
    padding = width - len(line3) - 1
    line3 += " " * padding + "│"
    lines.append(line3)

    # 卡片底部边框（P0 使用双线边框）
    if priority == 'P0':
        lines.append("╚" + "═" * (width - 2) + "╝")
    else:
        lines.append("└" + "─" * (width - 2) + "┘")

    return lines


def get_priority_value(story: Dict[str, Any]) -> int:
    """获取优先级数值（P0=0, P1=1, P2=2, 无=3）"""
    priority = story.get('priority', '')
    if priority == 'P0':
        return 0
    elif priority == 'P1':
        return 1
    elif priority == 'P2':
        return 2
    else:
        return 3  # 无优先级排在最后


def render_swimlane(title: str, icon: str, stories: List[Dict[str, Any]], width: int = 80) -> List[str]:
    """渲染单个泳道"""
    lines = []
    count = len(stories)

    # 泳道顶部边框
    lines.append("┌" + "─" * (width - 2) + "┐")

    # 泳道标题
    header = f"{icon} {title} ({count})"
    padding = width - len(header) - 1
    header_line = "│ " + header + " " * padding + "│"
    lines.append(header_line)

    # 分隔线
    lines.append("├" + "─" * (width - 2) + "┤")

    # Story 卡片
    if stories:
        # 按优先级排序（P0 > P1 > P2 > 无）
        sorted_stories = sorted(stories, key=get_priority_value)

        # 最多显示 20 个 Story（用户需求）
        display_stories = sorted_stories[:20]
        for story in display_stories:
            card_lines = render_story_card(story, width - 2)
            for card_line in card_lines:
                lines.append("│ " + card_line + " │")

            # 卡片间分隔
            if story != display_stories[-1]:
                lines.append("│" + " " * (width - 2) + "│")

        # 如果还有更多 Story
        if len(stories) > 10:
            remaining = len(stories) - 10
            more_line = f"│ ... 还有 {remaining} 个 Story"
            padding = width - len(more_line) - 1
            more_line += " " * padding + "│"
            lines.append(more_line)
    else:
        empty_line = "│ _暂无 Story_"
        padding = width - len(empty_line) - 1
        empty_line += " " * padding + "│"
        lines.append(empty_line)

    # 泳道底部边框
    lines.append("└" + "─" * (width - 2) + "┘")
    lines.append("")  # 空行分隔

    return lines


def render_kanban_unicode(metadata: Dict[str, Any]) -> str:
    """渲染完整的 Unicode KANBAN"""
    lines = []

    # 标题
    lines.append("# Sprint 看板（泳道图）")
    lines.append(f"**更新时间**: {metadata['generated_at']}")
    lines.append("**说明**: 使用 Unicode 字符绘制的状态泳道图")
    lines.append("")

    # 统计摘要（放在最前面）
    stats = metadata["statistics"]
    total = stats["total_stories"]
    completed = stats["completed_stories"]
    in_progress = stats["in_progress_stories"]
    deferred = stats.get("deferred_stories", 0)
    todo = total - completed - in_progress - deferred

    lines.append("## 📊 统计摘要")
    lines.append("")
    lines.append("| 状态 | 数量 | 占比 |")
    lines.append("|------|------|------|")
    lines.append(f"| 📋 待办 | {todo} | {todo * 100 // total}% |")
    lines.append(f"| 🚧 进行中 | {in_progress} | {in_progress * 100 // total}% |")
    lines.append(f"| ✅ 已完成 | {completed} | {stats['completion_rate']} |")
    lines.append(f"| ⏸️ 已延迟 | {deferred} | {deferred * 100 // total}% |")
    lines.append(f"| **总计** | **{total}** | **100%** |")
    lines.append("")
    lines.append(f"**Epic 总数**: {stats['total_epics']}")
    lines.append(f"**生成时间**: {metadata['generated_at']}")
    lines.append("")

    # 分隔符
    lines.append("---")
    lines.append("")

    # 按状态分组 Story
    grouped_stories = {
        "TODO": [],
        "IN_PROGRESS": [],
        "IN_REVIEW": [],
        "TESTING": [],
        "COMPLETED": [],
        "BLOCKED": [],
        "DEFERRED": [],
        "CANCELLED": [],
    }

    for story_id, story_info in metadata["stories"].items():
        status = story_info.get("status", "TODO")
        if status in grouped_stories:
            grouped_stories[status].append({**story_info, "id": story_id})

    # 渲染各泳道（每个泳道独立代码块）
    swimlanes = [
        ("待办", "📋", grouped_stories["TODO"]),
        ("进行中", "🚧", grouped_stories["IN_PROGRESS"]),
        ("审查中", "👀", grouped_stories["IN_REVIEW"]),
        ("测试中", "🧪", grouped_stories["TESTING"]),
        ("已完成", "✅", grouped_stories["COMPLETED"]),
        ("阻塞", "🚫", grouped_stories["BLOCKED"]),
        ("已延迟", "⏸️", grouped_stories["DEFERRED"]),
        ("已取消", "❌", grouped_stories["CANCELLED"]),
    ]

    swimlanes_rendered = []
    for title, icon, stories in swimlanes:
        if stories:  # 只渲染非空泳道
            swimlane_lines = render_swimlane(title, icon, stories)
            swimlane_text = "\n".join(swimlane_lines)
            swimlanes_rendered.append(swimlane_text)

    # 将每个泳道作为独立代码块，用 --- 分隔
    for i, swimlane in enumerate(swimlanes_rendered):
        lines.append("```text")
        lines.append(swimlane)
        lines.append("```")

        # 泳道之间添加分隔符（最后一个泳道不加）
        if i < len(swimlanes_rendered) - 1:
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def main():
    """测试函数"""
    import json
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent.parent
    metadata_file = project_root / "docs/scrum/metadata.json"

    with open(metadata_file) as f:
        metadata = json.load(f)

    kanban_content = render_kanban_unicode(metadata)

    # 写入文件
    output_file = project_root / "docs/scrum/KANBAN.md"
    output_file.write_text(kanban_content)

    print(f"✅ KANBAN.md 已更新（Unicode 泳道图）: {len(kanban_content.split(chr(10)))} 行")


if __name__ == "__main__":
    main()

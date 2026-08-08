#!/usr/bin/env python3
"""
Spec-XChecker 报告生成器

生成 Markdown/JSON 格式的审查报告
"""

import json
from datetime import datetime
from pathlib import Path

def generate_markdown_report(results, output_path):
    """生成 Markdown 报告"""
    summary = results.get('summary', {})
    strategy = results.get('strategy')

    # 构建报告头部
    report = f"""# Spec-XChecker 审查报告

**Story**: {results.get('story_id', 'Unknown')}
**模式**: {results.get('mode', 'MEDIUM').upper()}
**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # 添加检查策略章节（v2.4 POC）
    if strategy:
        report += f"""
## 检查策略（v2.4 动态策略）

**Story 类型**: {strategy.get('story_type', 'Unknown')}
**检测到的 AC 类型**: {', '.join(strategy.get('detected_ac_types', []))}
**置信度**: {strategy.get('confidence', 0.0):.1f}%

**策略说明**: {strategy.get('reasoning', '无')}

**执行的检查项** ({len(strategy.get('final_checks', []))} 个):
{chr(10).join(f"- {check}" for check in strategy.get('final_checks', []))}

---

"""

    # 添加执行摘要
    # 先提取通过的检查项
    checks = results.get('checks', [])
    passed_checks = [check for check in checks if check.get('passed', True)]
    passed_check_ids = [check.get('check_id') for check in passed_checks]

    report += f"""
## 执行摘要

- **检查项目**: {summary.get('total_checks', 21)}
- **通过**: {summary.get('passed', 0)} ({', '.join(passed_check_ids) if passed_check_ids else '无'})
- **失败**: {summary.get('failed', 0)} (P0: {summary.get('p0_issues', 0)}, P1: {summary.get('p1_issues', 0)}, P2: {summary.get('p2_issues', 0)})
"""

    # 添加问题清单（从 results['checks'] 中过滤）
    checks = results.get('checks', [])
    p0_issues = [check for check in checks if not check.get('passed', True) and check.get('severity') == 'P0']
    p1_issues = [check for check in checks if not check.get('passed', True) and check.get('severity') == 'P1']
    p2_issues = [check for check in checks if not check.get('passed', True) and check.get('severity') == 'P2']

    report += f"""
## 问题清单

### 🔴 P0 问题（{len(p0_issues)} 个）
"""
    if not p0_issues:
        report += "(无问题)\n"
    else:
        for issue in p0_issues:
            report += f"- **{issue.get('check_id')}**: {issue.get('description')}\n"
            report += f"  {issue.get('message', '')}\n\n"

    report += f"""
### 🟡 P1 问题（{len(p1_issues)} 个）
"""
    if not p1_issues:
        report += "(无问题)\n"
    else:
        for issue in p1_issues:
            report += f"- **{issue.get('check_id')}**: {issue.get('description')}\n"
            report += f"  {issue.get('message', '')}\n\n"

    report += f"""
### ⚪ P2 问题（{len(p2_issues)} 个）
"""
    if not p2_issues:
        report += "(无问题)\n"
    else:
        for issue in p2_issues:
            report += f"- **{issue.get('check_id')}**: {issue.get('description')}\n"
            report += f"  {issue.get('message', '')}\n\n"

    # 添加通过的检查项（增强详情）
    passed_checks = [check for check in checks if check.get('passed', True)]

    report += f"""
## ✅ 检查通过项（{len(passed_checks)} 个）

"""
    if not passed_checks:
        report += "(无通过的检查项)\n\n"
    else:
        # 按严重程度分组（通过的检查通常没有 severity，但为了保持一致）
        for check in passed_checks:
            report += f"### ✅ {check.get('check_id')}: {check.get('description')}\n\n"

            # 详细信息（如果有）
            if check.get('message'):
                # 将多行消息格式化
                message = check.get('message')
                if '\n' in message:
                    # 多行消息，逐行显示
                    for line in message.split('\n'):
                        line = line.strip()
                        if line:
                            report += f"  {line}\n"
                else:
                    # 单行消息
                    report += f"  **结果**: {message}\n"

            # 检查统计（如果有 details 字段）
            if check.get('details'):
                report += f"\n  **检查详情**:\n"
                details = check.get('details')
                if isinstance(details, dict):
                    for key, value in details.items():
                        report += f"  - {key}: {value}\n"
                elif isinstance(details, str):
                    report += f"  {details}\n"

            report += "\n"

        # 添加通过率统计
        total_checks = len(checks)
        pass_rate = (len(passed_checks) / total_checks * 100) if total_checks > 0 else 0
        report += f"**通过率**: {len(passed_checks)}/{total_checks} ({pass_rate:.1f}%)\n\n"

    report += f"""

---

**生成时间**: {datetime.now().isoformat()}
"""

    Path(output_path).write_text(report, encoding='utf-8')
    print(f"✅ Markdown 报告已生成: {output_path}")

def generate_json_report(results, output_path):
    """生成 JSON 报告"""
    summary = results.get('summary', {})
    strategy = results.get('strategy')

    # 提取问题列表（从 checks 中过滤出未通过的项）
    checks = results.get('checks', [])
    issues = [check for check in checks if not check.get('passed', True)]

    report = {
        "story_id": results.get('story_id'),
        "mode": results.get('mode'),
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_checks": summary.get('total_checks', 21),
            "passed": summary.get('passed', 0),
            "failed": summary.get('failed', 0),
            "p0_issues": summary.get('p0_issues', 0),
            "p1_issues": summary.get('p1_issues', 0),
            "p2_issues": summary.get('p2_issues', 0),
        },
        "issues": issues
    }

    # 添加策略信息（v2.4 POC）
    if strategy:
        report["strategy"] = strategy

    Path(output_path).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ JSON 报告已生成: {output_path}")

if __name__ == '__main__':
    # 简单测试
    results = {
        "story_id": "15-23",
        "mode": "medium",
        "strategy": {
            "story_type": "HYBRID_DB_TESTING_ARCH",
            "detected_ac_types": ["ddl", "sit_test", "architecture"],
            "checks": ["DS-01", "DS-02", "SC-06", "ST-01", "ST-02", "ST-03", "ST-05"],
            "skips": ["CT-01", "CT-02", "CT-03", "CT-04", "CT-05"],
            "reasoning": "检测到 AC 类型: DDL 变更, SIT 测试, 架构设计",
            "confidence": 0.9
        },
        "summary": {
            "total_checks": 7,
            "passed": 5,
            "failed": 2,
            "p0_issues": 0,
            "p1_issues": 1,
            "p2_issues": 1,
        },
        "checks": [],
        "issues": []
    }

    generate_markdown_report(results, "/tmp/test_report.md")
    generate_json_report(results, "/tmp/test_report.json")

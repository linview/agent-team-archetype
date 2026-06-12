#!/usr/bin/env python3
"""
Spec-XChecker 主入口

Usage:
    python3 spec-xchecker.py --story 15-23 --mode medium
    python3 spec-xchecker.py --auto-mode --format json
"""

import os
import sys
import json
import argparse
import dataclasses
from pathlib import Path
from datetime import datetime

# 导入 checker 模块
from scripts.lib.story_resolver import (
    get_current_story_id,
    find_story_document,
    load_design_spec,
    extract_acceptance_criteria
)
from scripts.checkers.checker_design import DesignChecker
from scripts.checkers.checker_code import CodeChecker
from scripts.checkers.checker_test import TestChecker
from scripts.checkers.checker_scenario import ScenarioChecker
from scripts.checkers.strategy_generator import ACBasedStrategyGenerator
from scripts.report_generator import generate_markdown_report, generate_json_report


def get_code_files(project_dir: str, scope: str = 'all') -> list[Path]:
    """
    获取要检查的代码文件

    Args:
        project_dir: 项目根目录
        scope: 检查范围 ('all', 'go', 'python', 'internal')

    Returns:
        代码文件列表
    """
    project_path = Path(project_dir)
    code_files = []

    # Go 文件
    if scope in ['all', 'go']:
        code_files.extend(project_path.rglob('*.go'))

    # Python 文件
    if scope in ['all', 'python']:
        code_files.extend(project_path.rglob('*.py'))

    # 过滤掉 vendor、node_modules 等
    code_files = [
        f for f in code_files
        if 'vendor' not in f.parts
        and 'node_modules' not in f.parts
        and '.git' not in f.parts
        and '__pycache__' not in f.parts
    ]

    # 限制文件数量（避免检查太多文件）
    if len(code_files) > 100:
        code_files = code_files[:100]

    return code_files


def run_checks(project_dir: str, story_id: str, mode: str, scope: str, enable_dynamic_strategy: bool = True) -> dict:
    """
    运行所有检查（遵循检查顺序铁律：DS → SC → CT → ST）

    ⚠️ 检查顺序铁律（不可改变）：
        1. DS 层（设计域内部一致性）：验证详细设计是否有概要设计依据
        2. SC 层（设计 → 代码）：验证代码是否实现详细设计
        3. CT 层（代码 → 测试）：验证代码是否有测试覆盖
        4. ST 层（设计 → 测试）：验证测试是否覆盖详细设计

    Args:
        project_dir: 项目根目录
        story_id: Story ID
        mode: 检查模式 ('quick', 'medium', 'deep')
        scope: 检查范围
        enable_dynamic_strategy: 是否启用动态策略（v2.4 POC）

    Returns:
        检查结果字典
    """
    results = {
        'story_id': story_id,
        'mode': mode,
        'timestamp': datetime.now().isoformat(),
        'checks': [],
        'summary': {
            'total_checks': 0,
            'passed': 0,
            'failed': 0,
            'p0_issues': 0,
            'p1_issues': 0,
            'p2_issues': 0
        },
        'strategy': None  # 将在后面填充
    }

    # 1. 加载 Story 文档
    story_doc = find_story_document(story_id, project_dir)
    if not story_doc:
        results['checks'].append({
            'check_id': 'LOAD_STORY',
            'description': '加载 Story 文档',
            'passed': False,
            'severity': 'P0',
            'message': f'Story 文档未找到: {story_id}',
            'details': '建议: 创建 docs/scrum/story/story-13-{story_id}-*.md'
        })
        results['summary']['total_checks'] = 1
        results['summary']['failed'] = 1
        results['summary']['p0_issues'] = 1
        return results

    story_content = story_doc.read_text(encoding='utf-8')

    # 2. 加载 Design Spec（可选）
    design_spec_content = load_design_spec(story_id, project_dir)

    # 3. 提取 AC 列表
    ac_list = extract_acceptance_criteria(story_content)

    # 3.5. 生成动态检查策略（v2.4 POC）
    strategy = None
    if enable_dynamic_strategy:
        try:
            generator = ACBasedStrategyGenerator(project_dir)

            # 尝试从 AC 列表生成策略
            if ac_list:
                story_metadata = {
                    'acceptance_criteria': ac_list,
                    'content': story_content,
                }
                strategy = generator.generate(story_metadata, mode)
            else:
                # AC 列表为空，尝试从全文直接解析
                story_metadata = {
                    'content': story_content,
                }
                strategy = generator.generate(story_metadata, mode)

            results['strategy'] = dataclasses.asdict(strategy)

            # 打印策略摘要
            if strategy.detected_ac_types:
                print(f"[spec-xchecker] 🎯 检测到 AC 类型: {', '.join(strategy.detected_ac_types)}")
                print(f"[spec-xchecker] 📋 Story 类型: {strategy.story_type}")
                print(f"[spec-xchecker] ✅ 执行检查项: {len(strategy.checks)} 个")
            else:
                print(f"[spec-xchecker] ⚠️  未检测到已知 AC 类型，使用默认策略")
        except Exception as e:
            # 策略生成失败，使用默认策略
            print(f"[spec-xchecker] ⚠️  动态策略生成失败: {e}")
            print(f"[spec-xchecker] 📋 使用默认检查策略")
            strategy = None

    # 4. 获取代码文件
    code_files = get_code_files(project_dir, scope)

    # === 检查顺序铁律：DS → SC → CT → ST ===
    # v2.4 修复：由动态策略决定检查哪些项，而不是由模式决定

    # 准备所有检查器
    design_checker = DesignChecker(story_content, design_spec_content)
    code_checker = CodeChecker(project_dir, ac_list, code_files)
    test_checker = TestChecker(project_dir, code_files)
    scenario_checker = ScenarioChecker(project_dir, ac_list)

    # 获取策略指定的检查列表
    strategy_checks = strategy.checks if strategy else []

    # DS 层检查（Design Spec ↔ Scrum）
    if 'DS-01' in strategy_checks:
        results['checks'].append(dataclasses.asdict(design_checker.check_ds01_story_references_design_spec()))
    if 'DS-02' in strategy_checks:
        results['checks'].append(dataclasses.asdict(design_checker.check_ds02_ac_matches_design_spec(ac_list)))
    if 'DS-03' in strategy_checks:
        results['checks'].append(dataclasses.asdict(design_checker.check_ds03_design_spec_reference_valid(project_dir)))
    if 'DS-04' in strategy_checks:
        results['checks'].append(dataclasses.asdict(design_checker.check_ds04_epic_matches_design_spec()))

    # SC 层检查（Scrum ↔ Code）
    if 'SC-01' in strategy_checks and ac_list:
        results['checks'].append(dataclasses.asdict(code_checker.check_sc01_ac_has_code_implementation()))
    if 'SC-02' in strategy_checks and ac_list:
        results['checks'].append(dataclasses.asdict(code_checker.check_sc02_code_logic_matches_ac()))
    if 'SC-03' in strategy_checks:
        results['checks'].append(dataclasses.asdict(code_checker.check_sc03_correct_table_field_references()))
    if 'SC-04' in strategy_checks:
        results['checks'].append(dataclasses.asdict(code_checker.check_sc04_error_handling_coverage()))
    if 'SC-05' in strategy_checks:
        results['checks'].append(dataclasses.asdict(code_checker.check_sc05_logging_standards()))
    if 'SC-06' in strategy_checks:
        results['checks'].append(dataclasses.asdict(code_checker.check_sc06_commit_message_format()))

    # CT 层检查（Code ↔ Tests）
    if 'CT-01' in strategy_checks:
        results['checks'].append(dataclasses.asdict(test_checker.check_ct01_ut_functions_have_tests()))
    if 'CT-02' in strategy_checks:
        results['checks'].append(dataclasses.asdict(test_checker.check_ct02_api_has_tests()))
    if 'CT-03' in strategy_checks:
        results['checks'].append(dataclasses.asdict(test_checker.check_ct03_ut_coverage_meets_threshold()))
    if 'CT-04' in strategy_checks:
        results['checks'].append(dataclasses.asdict(test_checker.check_ct04_api_coverage_meets_threshold()))
    if 'CT-05' in strategy_checks:
        results['checks'].append(dataclasses.asdict(test_checker.check_ct05_mock_usage_reasonable()))

    # ST 层检查（Scrum ↔ Tests）
    if 'ST-01' in strategy_checks and ac_list:
        results['checks'].append(dataclasses.asdict(scenario_checker.check_st01_ac_has_sit_test()))
    if 'ST-02' in strategy_checks:
        results['checks'].append(dataclasses.asdict(scenario_checker.check_st02_sit_tests_check_correct_objects()))
    if 'ST-03' in strategy_checks:
        results['checks'].append(dataclasses.asdict(scenario_checker.check_st03_sit_covers_exception_paths()))
    if 'ST-04' in strategy_checks:
        results['checks'].append(dataclasses.asdict(scenario_checker.check_st04_uat_covers_user_scenarios()))
    if 'ST-05' in strategy_checks:
        results['checks'].append(dataclasses.asdict(scenario_checker.check_st05_test_data_quality_score()))
    if 'ST-06' in strategy_checks:
        results['checks'].append(dataclasses.asdict(scenario_checker.check_st06_sit_coverage_meets_requirement()))

    # 9. 汇总统计（根据策略过滤检查项）
    for check in results['checks']:
        check_id = check.get('check_id', '')

        # 如果有策略，只统计策略中指定的检查
        if strategy is not None:
            if check_id not in strategy.checks:
                # 不在策略中的检查，不计入统计
                continue

        results['summary']['total_checks'] += 1
        if check['passed']:
            results['summary']['passed'] += 1
        else:
            results['summary']['failed'] += 1
            severity = check.get('severity', 'P2')
            if severity == 'P0':
                results['summary']['p0_issues'] += 1
            elif severity == 'P1':
                results['summary']['p1_issues'] += 1
            elif severity == 'P2':
                results['summary']['p2_issues'] += 1

    return results


def update_state(status: str, state_file: str, **kwargs):
    """更新状态文件"""
    state = {}
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)

    state['status'] = status
    state.update(kwargs)

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Spec-XChecker: 四路交叉验证工具')
    parser.add_argument('--story', type=str, help='Story ID (例如: 15-23)')
    parser.add_argument('--auto-mode', action='store_true', help='自动检测当前 Story')
    parser.add_argument('--mode', type=str, default='medium', choices=['quick', 'medium', 'deep'],
                        help='检查模式')
    parser.add_argument('--format', type=str, default='markdown', choices=['markdown', 'json'],
                        help='输出格式')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--scope', type=str, default='all', choices=['all', 'go', 'python', 'internal'],
                        help='检查范围（代码文件类型）')
    parser.add_argument('--project-dir', type=str, default=os.getcwd(), help='项目根目录')

    args = parser.parse_args()

    # 配置输出目录和报告文件
    if args.output:
        # 用户指定了输出路径，直接使用
        report_file = args.output
        # 创建临时目录用于 state.json
        TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
        OUTPUT_DIR = f"/tmp/xchecker/{TIMESTAMP}"
        STATE_FILE = f"{OUTPUT_DIR}/state.json"
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    else:
        # 用户未指定，创建时间戳目录
        TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
        OUTPUT_DIR = f"/tmp/xchecker/{TIMESTAMP}"
        STATE_FILE = f"{OUTPUT_DIR}/state.json"
        report_file = None  # 稍后设置默认值
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 检查是否从 Hook 触发（通过 STATE_FILE 判断）
    hook_triggered = os.path.exists(STATE_FILE)

    if hook_triggered:
        # 从 state.json 读取配置
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        story_id = state.get('story_id') or args.story
        args.project_dir = state.get('project_dir', args.project_dir)
    else:
        story_id = args.story

    # 自动检测 Story ID
    if args.auto_mode or not story_id:
        story_id = get_current_story_id(args.project_dir)
        if not story_id:
            print(f"[spec-xchecker] ❌ 无法识别 Story ID")
            print(f"  请使用 --story 指定，或确保当前 Git 分支名包含 Story ID")
            return 1

    print(f"[spec-xchecker] 启动检查")
    print(f"  Story: {story_id}")
    print(f"  模式: {args.mode.upper()}")
    print(f"  范围: {args.scope}")
    print(f"  输出: {args.format}")
    print(f"  目录: {OUTPUT_DIR}")
    print()

    # 执行开始
    update_state("running", STATE_FILE,
                 story_id=story_id,
                 start_time=datetime.now().isoformat(),
                 project_dir=args.project_dir,
                 mode=args.mode,
                 scope=args.scope,
                 output_format=args.format)

    # 运行检查
    try:
        results = run_checks(args.project_dir, story_id, args.mode, args.scope)
    except Exception as e:
        # 执行失败
        update_state("failed", STATE_FILE,
                     end_time=datetime.now().isoformat(),
                     error=str(e))
        print(f"[spec-xchecker] ❌ 检查失败: {e}")
        return 1

    # 执行完成
    update_state("completed", STATE_FILE,
                 end_time=datetime.now().isoformat(),
                 exit_code=0,
                 total_checks=results['summary']['total_checks'],
                 passed=results['summary']['passed'],
                 failed=results['summary']['failed'])

    # 生成报告
    if args.format == 'markdown':
        report_file = report_file or f"{OUTPUT_DIR}/report.md"
        generate_markdown_report(results, report_file)
    else:  # json
        report_file = report_file or f"{OUTPUT_DIR}/report.json"
        generate_json_report(results, report_file)

    # 打印摘要
    print(f"[spec-xchecker] ✅ 检查完成！")
    print(f"  总检查项: {results['summary']['total_checks']}")
    print(f"  通过: {results['summary']['passed']}")
    print(f"  失败: {results['summary']['failed']} (P0: {results['summary']['p0_issues']}, P1: {results['summary']['p1_issues']}, P2: {results['summary']['p2_issues']})")
    print(f"  报告: {report_file}")

    # 如果 Hook 触发，更新 memory 目录中的索引文件
    if hook_triggered:
        memory_dir = state.get('memory_dir')
        if memory_dir:
            index_file = f"{memory_dir}/spec-xchecker/reports_index.json"
            timestamp = state['timestamp']

            # 更新索引文件
            if os.path.exists(index_file):
                with open(index_file, 'r') as f:
                    index = json.load(f)

                for report in index['reports']:
                    if report['timestamp'] == timestamp:
                        report['status'] = 'completed'
                        report['exit_code'] = 0
                        break

                with open(index_file, 'w') as f:
                    json.dump(index, f, indent=2)

    return 0 if results['summary']['p0_issues'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

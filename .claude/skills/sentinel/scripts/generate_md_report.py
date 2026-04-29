#!/usr/bin/env python3
"""
生成 Markdown 格式的巡检报告
从 JUnit XML 文件读取测试结果并生成详细的 Markdown 报告
"""

import sys
import os
from datetime import datetime
from pathlib import Path
try:
    import xml.etree.ElementTree as ET
except ImportError:
    print("错误: 需要 xml.etree.ElementTree 模块")
    sys.exit(1)


def parse_junit_xml(xml_file):
    """解析 JUnit XML 文件"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    results = {
        'tests': 0,
        'failures': 0,
        'errors': 0,
        'skipped': 0,
        'time': 0.0,
        'testcases': []
    }

    # 解析测试套件
    for testsuite in root.findall('.//testsuite'):
        results['tests'] += int(testsuite.get('tests', 0))
        results['failures'] += int(testsuite.get('failures', 0))
        results['errors'] += int(testsuite.get('errors', 0))
        results['skipped'] += int(testsuite.get('skipped', 0))
        results['time'] += float(testsuite.get('time', 0))

        # 解析测试用例
        for testcase in testsuite.findall('testcase'):
            case_info = {
                'name': testcase.get('name'),
                'classname': testcase.get('classname'),
                'time': float(testcase.get('time', 0)),
                'status': 'PASSED',
                'failure': None,
                'error': None,
                'skipped': False
            }

            # 检查失败
            failure = testcase.find('failure')
            if failure is not None:
                case_info['status'] = 'FAILED'
                case_info['failure'] = {
                    'message': failure.get('message'),
                    'text': failure.text
                }

            # 检查错误
            error = testcase.find('error')
            if error is not None:
                case_info['status'] = 'ERROR'
                case_info['error'] = {
                    'message': error.get('message'),
                    'text': error.text
                }

            # 检查跳过
            skipped = testcase.find('skipped')
            if skipped is not None:
                case_info['status'] = 'SKIPPED'
                case_info['skipped'] = True

            results['testcases'].append(case_info)

    return results


def generate_markdown_report(results, output_file, env, level, api_url, db_info, duration):
    """生成 Markdown 报告"""

    # 计算通过率
    total = results['tests']
    passed = total - results['failures'] - results['errors']
    pass_rate = (passed / total * 100) if total > 0 else 0

    # 生成报告内容
    report_lines = [
        "# Resource Meter 定期巡检报告\n",
        f"**环境**: {env}",
        f"**级别**: {level}",
        f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**结果**: {'✅ 通过' if results['failures'] == 0 and results['errors'] == 0 else '❌ 失败'}",
        f"**耗时**: {duration} 秒",
        "",
        "---\n",
        "## 📊 测试结果摘要\n",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| **总测试数** | {total} |",
        f"| **通过数** | {passed} |",
        f"| **失败数** | {results['failures']} |",
        f"| **错误数** | {results['errors']} |",
        f"| **跳过数** | {results['skipped']} |",
        f"| **通过率** | {pass_rate:.1f}% |",
        f"| **执行时间** | {results['time']:.2f} 秒 |",
        "",
    ]

    # 添加环境信息
    report_lines.extend([
        "## 🔧 环境信息\n",
        f"- **API URL**: {api_url}",
        f"- **数据库**: {db_info}",
        "",
    ])

    # 添加测试套件统计
    test_suites = {}
    for case in results['testcases']:
        classname = case['classname']
        if classname not in test_suites:
            test_suites[classname] = {'total': 0, 'failed': 0, 'passed': 0}
        test_suites[classname]['total'] += 1
        if case['status'] == 'PASSED':
            test_suites[classname]['passed'] += 1
        else:
            test_suites[classname]['failed'] += 1

    report_lines.extend([
        "## 📋 测试套件详情\n",
        "| 测试套件 | 总数 | 通过 | 失败 | 通过率 |",
        "|----------|------|------|------|--------|",
    ])

    for suite_name, stats in sorted(test_suites.items()):
        suite_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        short_name = suite_name.split('.')[-1] if '.' in suite_name else suite_name
        status_icon = "✅" if stats['failed'] == 0 else "❌"
        report_lines.append(
            f"| {status_icon} {short_name} | {stats['total']} | {stats['passed']} | {stats['failed']} | {suite_rate:.1f}% |"
        )

    report_lines.append("")

    # 添加失败的测试详情
    failed_cases = [case for case in results['testcases']
                   if case['status'] in ['FAILED', 'ERROR']]

    if failed_cases:
        report_lines.extend([
            "## ❌ 失败测试详情\n",
        ])

        for i, case in enumerate(failed_cases, 1):
            case_name = case['name']
            classname = case['classname']
            short_class = classname.split('.')[-1] if '.' in classname else classname

            report_lines.extend([
                f"### {i}. {short_class}.{case_name}\n",
                f"**状态**: {case['status']}",
                f"**耗时**: {case['time']:.3f} 秒",
                "",
            ])

            # 添加失败信息
            if case.get('failure'):
                failure = case['failure']
                report_lines.extend([
                    "**失败原因**:",
                    "```",
                    failure.get('message', 'Unknown error'),
                    "```",
                    "",
                ])

                if failure.get('text'):
                    # 限制输出长度
                    error_text = failure['text']
                    if len(error_text) > 1000:
                        error_text = error_text[:1000] + "\n... (已截断)"
                    report_lines.extend([
                        "**详细信息**:",
                        "```",
                        error_text,
                        "```",
                        "",
                    ])

            # 添加错误信息
            if case.get('error'):
                error = case['error']
                report_lines.extend([
                    "**错误原因**:",
                    "```",
                    error.get('message', 'Unknown error'),
                    "```",
                    "",
                ])

                if error.get('text'):
                    error_text = error['text']
                    if len(error_text) > 1000:
                        error_text = error_text[:1000] + "\n... (已截断)"
                    report_lines.extend([
                        "**详细信息**:",
                        "```",
                        error_text,
                        "```",
                        "",
                    ])

    # 添加通过测试列表（如果通过率 < 100%）
    if pass_rate < 100:
        passed_cases = [case for case in results['testcases'] if case['status'] == 'PASSED']
        report_lines.extend([
            "## ✅ 通过测试列表\n",
            f"共 {len(passed_cases)} 个测试通过\n",
        ])

        # 按测试套件分组
        passed_by_suite = {}
        for case in passed_cases:
            classname = case['classname']
            if classname not in passed_by_suite:
                passed_by_suite[classname] = []
            passed_by_suite[classname].append(case['name'])

        for suite_name in sorted(passed_by_suite.keys()):
            short_name = suite_name.split('.')[-1] if '.' in suite_name else suite_name
            report_lines.append(f"\n### {short_name}")
            for case_name in passed_by_suite[suite_name]:
                report_lines.append(f"- ✅ {case_name}")

        report_lines.append("")

    # 添加报告生成信息
    report_lines.extend([
        "---\n",
        f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**巡检级别**: {level}",
        f"**环境**: {env}",
    ])

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"✅ Markdown 报告已生成: {output_file}")

    # 复制报告到 test_reports/regression/ 目录（用于自动循环任务）
    import shutil
    regression_dir = "test_reports/regression"
    os.makedirs(regression_dir, exist_ok=True)
    regression_report = os.path.join(regression_dir, os.path.basename(output_file))
    shutil.copy2(output_file, regression_report)
    print(f"📁 报告已复制到 {regression_report}")

    return pass_rate


def main():
    if len(sys.argv) < 6:
        print("用法: generate_md_report.py <junit_xml> <output_md> <env> <level> <api_url> <db_info> <duration>")
        sys.exit(1)

    junit_xml = sys.argv[1]
    output_md = sys.argv[2]
    env = sys.argv[3]
    level = sys.argv[4]
    api_url = sys.argv[5]
    db_info = sys.argv[6]
    duration = sys.argv[7]

    if not os.path.exists(junit_xml):
        print(f"错误: JUnit XML 文件不存在: {junit_xml}")
        sys.exit(1)

    # 解析 JUnit XML
    print(f"📖 解析 JUnit XML: {junit_xml}")
    results = parse_junit_xml(junit_xml)

    # 生成 Markdown 报告
    print(f"📝 生成 Markdown 报告: {output_md}")
    pass_rate = generate_markdown_report(results, output_md, env, level, api_url, db_info, duration)

    # 输出摘要
    print(f"\n📊 测试结果摘要:")
    print(f"  总数: {results['tests']}")
    print(f"  通过: {results['tests'] - results['failures'] - results['errors']}")
    print(f"  失败: {results['failures']}")
    print(f"  错误: {results['errors']}")
    print(f"  通过率: {pass_rate:.1f}%")

    # 返回退出码
    if results['failures'] > 0 or results['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

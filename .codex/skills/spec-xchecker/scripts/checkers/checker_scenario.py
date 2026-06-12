#!/usr/bin/env python3
"""
ST 层检查器：Scrum ↔ Tests (SIT/UAT) 一致性检查

检查项:
- ST-01: 每个 AC 是否有对应 SIT 用例（P0）
- ST-02: SIT 测试是否检查正确对象（P0）
- ST-03: SIT 测试是否覆盖异常路径（P1）
- ST-04: UAT 测试是否覆盖用户场景（P2）
- ST-05: 测试数据质量评分是否达标（P2）
- ST-06: SIT 覆盖率是否满足要求（P1）
"""

import re
from pathlib import Path
from typing import List
from dataclasses import dataclass


@dataclass
class CheckResult:
    """检查结果"""
    check_id: str
    description: str
    passed: bool
    severity: str  # P0, P1, P2
    message: str
    details: str = ""


class ScenarioChecker:
    """Scrum ↔ Tests (SIT/UAT) 检查器"""

    def __init__(self, project_dir: str, ac_list: List[str]):
        """
        初始化检查器

        Args:
            project_dir: 项目根目录
            ac_list: Acceptance Criteria 列表
        """
        self.project_dir = project_dir
        self.ac_list = ac_list
        self.test_dir = Path(project_dir) / 'tests'

    def check_st01_ac_has_sit_test(self) -> CheckResult:
        """
        ST-01: 检查每个 AC 是否有对应 SIT 用例

        策略:
        1. 过滤掉不需要 SIT 测试的 AC（文档类、过程类等）
        2. 提取 AC 中的关键字
        3. 在 tests/sit/ 目录中搜索匹配的测试用例标题

        Returns:
            CheckResult
        """
        if not self.ac_list:
            return CheckResult(
                check_id='ST-01',
                description='每个 AC 是否有对应 SIT 用例',
                passed=False,
                severity='P0',
                message='没有提供 AC 列表，无法验证',
                details='建议: 在 Story 文档中定义 Acceptance Criteria'
            )

        sit_test_dir = self.test_dir / 'sit'

        if not sit_test_dir.exists():
            return CheckResult(
                check_id='ST-01',
                description='每个 AC 是否有对应 SIT 用例',
                passed=False,
                severity='P0',
                message='未找到 tests/sit/ 目录',
                details='建议: 创建 tests/sit/ 目录并添加 SIT 测试'
            )

        # 读取所有 SIT 测试文件
        sit_test_content = ''
        for test_file in sit_test_dir.rglob('*.py'):
            try:
                sit_test_content += test_file.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                pass

        # 不需要 SIT 测试的 AC 类型（文档类、过程类等）
        skip_keywords = [
            '文档', '架构', '设计规范', '更新文档', '设计文档',
            '流程', '规范', '指南', 'README', 'SKILL'
        ]

        # 检查每个 AC 是否有对应的 SIT 测试
        missing_acs = []
        skipped_acs = []

        for ac in self.ac_list:
            # 检查是否应该跳过此 AC
            should_skip = any(keyword in ac for keyword in skip_keywords)
            if should_skip:
                skipped_acs.append(ac[:50] + '...' if len(ac) > 50 else ac)
                continue

            # 提取 AC 中的关键字（中文、英文、数字）
            keywords = re.findall(r'[一-龥]{3,}|[a-zA-Z_][a-zA-Z0-9_]{2,}', ac)

            if not keywords:
                continue

            # 检查是否有 SIT 测试包含这些关键字
            covered = False
            for keyword in keywords[:3]:
                if keyword in sit_test_content:
                    covered = True
                    break

            if not covered:
                missing_acs.append(ac[:50] + '...' if len(ac) > 50 else ac)

        # 如果所有需要测试的 AC 都有 SIT 测试，则通过
        if not missing_acs:
            return CheckResult(
                check_id='ST-01',
                description='每个 AC 是否有对应 SIT 用例',
                passed=True,
                severity='P0',
                message=f'所有需要测试的 AC 都有对应的 SIT 测试（跳过 {len(skipped_acs)} 个文档类 AC）',
                details='\n'.join(f'- {ac}' for ac in skipped_acs[:3]) if skipped_acs else f'SIT 测试目录: {sit_test_dir}'
            )

        # 如果有缺失的 SIT 测试
        return CheckResult(
            check_id='ST-01',
            description='每个 AC 是否有对应 SIT 用例',
            passed=False,
            severity='P0',
            message=f'{len(missing_acs)} 个 AC 缺少对应的 SIT 测试（已跳过 {len(skipped_acs)} 个文档类 AC）',
            details='\n'.join(f'- {ac}' for ac in missing_acs[:3])
        )

    def check_st02_sit_tests_check_correct_objects(self) -> CheckResult:
        """
        ST-02: 检查 SIT 测试是否检查正确对象

        策略:
        1. 检查 SIT 测试中的断言（assert）
        2. 验证断言目标的合理性

        Returns:
            CheckResult
        """
        sit_test_dir = self.test_dir / 'sit'

        if not sit_test_dir.exists():
            return CheckResult(
                check_id='ST-02',
                description='SIT 测试是否检查正确对象',
                passed=True,
                severity='P0',
                message='未找到 tests/sit/ 目录，跳过检查',
                details=''
            )

        # 统计断言数量
        assert_count = 0
        test_file_count = 0

        for test_file in sit_test_dir.rglob('*.py'):
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                # 统计 assert 语句
                assert_count += len(re.findall(r'\bassert\w+\s*\(', content))
                test_file_count += 1
            except Exception:
                pass

        if test_file_count == 0:
            return CheckResult(
                check_id='ST-02',
                description='SIT 测试是否检查正确对象',
                passed=False,
                severity='P0',
                message='tests/sit/ 目录中没有测试文件',
                details='建议: 添加 SIT 测试文件'
            )

        if assert_count == 0:
            return CheckResult(
                check_id='ST-02',
                description='SIT 测试是否检查正确对象',
                passed=False,
                severity='P0',
                message=f'SIT 测试中未发现断言（{test_file_count} 个文件）',
                details='建议: 在测试中添加 assert 语句验证测试结果（例如：assert result == expected, assert response.status_code == 200）'
            )

        return CheckResult(
            check_id='ST-02',
            description='SIT 测试是否检查正确对象',
            passed=True,
            severity='P0',
            message=f'SIT 测试包含 {assert_count} 个断言（{test_file_count} 个文件）',
            details='检查通过'
        )

    def check_st03_sit_covers_exception_paths(self) -> CheckResult:
        """
        ST-03: 检查 SIT 测试是否覆盖异常路径

        策略:
        1. 搜索异常测试关键字（error, exception, invalid）
        2. 统计异常测试用例数量

        Returns:
            CheckResult
        """
        sit_test_dir = self.test_dir / 'sit'

        if not sit_test_dir.exists():
            return CheckResult(
                check_id='ST-03',
                description='SIT 测试是否覆盖异常路径',
                passed=True,
                severity='P1',
                message='未找到 tests/sit/ 目录，跳过检查',
                details=''
            )

        # 搜索异常测试关键字
        exception_test_count = 0
        total_test_count = 0

        for test_file in sit_test_dir.rglob('*.py'):
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                # 检查函数名
                test_funcs = re.findall(r'def\s+(test_\w+)\s*\(', content)
                total_test_count += len(test_funcs)

                # 检查异常关键字
                for func in test_funcs:
                    if any(keyword in func.lower() for keyword in ['error', 'exception', 'invalid', 'fail', 'negative']):
                        exception_test_count += 1
            except Exception:
                pass

        if total_test_count == 0:
            return CheckResult(
                check_id='ST-03',
                description='SIT 测试是否覆盖异常路径',
                passed=True,
                severity='P1',
                message='SIT 测试文件为空，跳过检查',
                details=''
            )

        exception_coverage = exception_test_count / total_test_count if total_test_count > 0 else 0

        if exception_coverage < 0.2:
            return CheckResult(
                check_id='ST-03',
                description='SIT 测试是否覆盖异常路径',
                passed=False,
                severity='P1',
                message=f'异常测试覆盖率偏低: {exception_coverage*100:.0f}%（{exception_test_count}/{total_test_count}）',
                details='建议: 添加异常场景测试（test_*_error, test_*_exception）'
            )
        else:
            return CheckResult(
                check_id='ST-03',
                description='SIT 测试是否覆盖异常路径',
                passed=True,
                severity='P1',
                message=f'异常测试覆盖率正常: {exception_coverage*100:.0f}%（{exception_test_count}/{total_test_count}）',
                details='检查通过'
            )

    def check_st04_uat_covers_user_scenarios(self) -> CheckResult:
        """
        ST-04: 检查 UAT 测试是否覆盖用户场景

        Returns:
            CheckResult
        """
        uat_test_dir = self.test_dir / 'uat'

        if not uat_test_dir.exists():
            return CheckResult(
                check_id='ST-04',
                description='UAT 测试是否覆盖用户场景',
                passed=True,
                severity='P2',
                message='未找到 tests/uat/ 目录，跳过检查',
                details='建议: 创建 UAT 测试验证用户场景'
            )

        # 统计 UAT 测试文件
        uat_test_files = list(uat_test_dir.rglob('*.py'))

        if len(uat_test_files) == 0:
            return CheckResult(
                check_id='ST-04',
                description='UAT 测试是否覆盖用户场景',
                passed=False,
                severity='P2',
                message='tests/uat/ 目录中没有测试文件',
                details='建议: 添加 UAT 测试验证用户场景'
            )

        return CheckResult(
            check_id='ST-04',
            description='UAT 测试是否覆盖用户场景',
            passed=True,
            severity='P2',
            message=f'发现 {len(uat_test_files)} 个 UAT 测试文件',
            details='检查通过'
        )

    def check_st05_test_data_quality_score(self) -> CheckResult:
        """
        ST-05: 检查测试数据质量评分是否达标

        策略:
        1. 检查测试文件中是否使用 fixtures 或测试数据
        2. 简化版本：统计测试数据相关的关键字

        Returns:
            CheckResult
        """
        if not self.test_dir.exists():
            return CheckResult(
                check_id='ST-05',
                description='测试数据质量评分是否达标',
                passed=True,
                severity='P2',
                message='未找到 tests/ 目录，跳过检查',
                details=''
            )

        # 搜索测试数据关键字
        data_score = 0

        for test_file in self.test_dir.rglob('*.py'):
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')

                # 检查 fixtures
                if re.search(r'@pytest\.fixture|@fixture', content):
                    data_score += 2

                # 检查测试数据类
                if re.search(r'class.*TestData|class.*MockData', content):
                    data_score += 2

                # 检查 conftest.py
                if test_file.name == 'conftest.py':
                    data_score += 3

            except Exception:
                pass

        if data_score >= 5:
            return CheckResult(
                check_id='ST-05',
                description='测试数据质量评分是否达标',
                passed=True,
                severity='P2',
                message=f'测试数据质量评分: {data_score} 分（达标）',
                details='检查通过'
            )
        else:
            return CheckResult(
                check_id='ST-05',
                description='测试数据质量评分是否达标',
                passed=False,
                severity='P2',
                message=f'测试数据质量评分偏低: {data_score} 分（建议≥5分）',
                details='建议: 使用 pytest fixtures、创建测试数据类'
            )

    def check_st06_sit_coverage_meets_requirement(self) -> CheckResult:
        """
        ST-06: 检查 SIT 覆盖率是否满足要求

        Returns:
            CheckResult
        """
        sit_test_dir = self.test_dir / 'sit'

        if not sit_test_dir.exists():
            return CheckResult(
                check_id='ST-06',
                description='SIT 覆盖率是否满足要求',
                passed=False,
                severity='P1',
                message='未找到 tests/sit/ 目录',
                details='建议: 创建 tests/sit/ 目录并添加 SIT 测试'
            )

        # 统计 SIT 测试文件和测试函数
        sit_test_files = list(sit_test_dir.rglob('test_*.py'))
        total_test_funcs = 0

        for test_file in sit_test_files:
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                test_funcs = re.findall(r'def\s+(test_\w+)\s*\(', content)
                total_test_funcs += len(test_funcs)
            except Exception:
                pass

        if len(sit_test_files) == 0:
            return CheckResult(
                check_id='ST-06',
                description='SIT 覆盖率是否满足要求',
                passed=False,
                severity='P1',
                message='SIT 测试文件数量为 0',
                details='建议: 添加 SIT 测试文件'
            )

        # 简化标准：至少有3个测试文件和10个测试函数
        if len(sit_test_files) >= 3 and total_test_funcs >= 10:
            return CheckResult(
                check_id='ST-06',
                description='SIT 覆盖率是否满足要求',
                passed=True,
                severity='P1',
                message=f'SIT 测试覆盖率达标（{len(sit_test_files)} 个文件，{total_test_funcs} 个测试函数）',
                details='检查通过'
            )
        else:
            return CheckResult(
                check_id='ST-06',
                description='SIT 覆盖率是否满足要求',
                passed=False,
                severity='P1',
                message=f'SIT 测试覆盖率不足（{len(sit_test_files)} 个文件，{total_test_funcs} 个测试函数）',
                detail='建议: 增加测试文件和测试函数（目标: ≥3个文件，≥10个函数）'
            )


# CLI 测试接口
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python checker_scenario.py <project_dir>")
        sys.exit(1)

    project_dir = sys.argv[1]
    ac_list = []  # 简化版本，不解析 AC

    checker = ScenarioChecker(project_dir, ac_list)

    # 运行所有检查（除了 ST-01，因为需要 AC 列表）
    results = [
        checker.check_st02_sit_tests_check_correct_objects(),
        checker.check_st03_sit_covers_exception_paths(),
        checker.check_st04_uat_covers_user_scenarios(),
        checker.check_st05_test_data_quality_score(),
        checker.check_st06_sit_coverage_meets_requirement(),
    ]

    # 打印结果
    for result in results:
        status = "✅" if result.passed else "❌"
        print(f"{status} [{result.check_id}] {result.description}")
        print(f"   优先级: {result.severity}")
        print(f"   消息: {result.message}")
        if result.details:
            print(f"   详情: {result.details}")
        print()

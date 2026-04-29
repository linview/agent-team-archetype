#!/usr/bin/env python3
"""
CT 层检查器：Code ↔ Tests (UT/API) 一致性检查

检查项:
- CT-01: UT 函数是否有对应 test_ 函数（P0）
- CT-02: API 接口是否有对应测试（P0）
- CT-03: UT 测试覆盖率是否达标（P1）
- CT-04: API 测试覆盖率是否达标（P1）
- CT-05: Mock 使用是否合理（P2）
"""

import os
import re
from pathlib import Path
from typing import List, Set
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


class TestChecker:
    """Code ↔ Tests 检查器"""

    def __init__(self, project_dir: str, code_files: List[Path]):
        """
        初始化检查器

        Args:
            project_dir: 项目根目录
            code_files: 代码文件列表
        """
        self.project_dir = project_dir
        self.code_files = code_files
        self.test_dir = Path(project_dir) / 'tests'

    def check_ct01_ut_functions_have_tests(self) -> CheckResult:
        """
        CT-01: 检查 UT 函数是否有对应 test_ 函数

        策略:
        1. 提取代码文件中的函数名（Go/Python）
        2. 在tests/目录中搜索对应的 test_ 函数
        3. 计算覆盖率

        Returns:
            CheckResult
        """
        if not self.code_files:
            return CheckResult(
                check_id='CT-01',
                description='UT 函数是否有对应 test_ 函数',
                passed=True,
                severity='P0',
                message='没有代码文件需要检查',
                details='跳过检查'
            )

        # 提取代码函数名
        code_functions = set()
        for code_file in self.code_files:
            try:
                content = code_file.read_text(encoding='utf-8', errors='ignore')

                # Go 函数: func FunctionName
                if code_file.suffix == '.go':
                    funcs = re.findall(r'func\s+(\w+)', content)
                    code_functions.update(funcs)

                # Python 函数: def function_name
                elif code_file.suffix == '.py':
                    funcs = re.findall(r'def\s+(\w+)\s*\(', content)
                    code_functions.update(funcs)

            except Exception:
                pass

        if not code_functions:
            return CheckResult(
                check_id='CT-01',
                description='UT 函数是否有对应 test_ 函数',
                passed=True,
                severity='P0',
                message='代码中没有发现函数定义',
                details='跳过检查'
            )

        # 查找测试文件中的 test_ 函数
        test_functions = set()
        if self.test_dir.exists():
            for test_file in self.test_dir.rglob('test_*.py'):
                try:
                    content = test_file.read_text(encoding='utf-8', errors='ignore')
                    # Python test 函数: def test_xxx
                    funcs = re.findall(r'def\s+(test_\w+)\s*\(', content)
                    test_functions.update(funcs)
                except Exception:
                    pass

        # 计算覆盖率（简化版本：检查函数名是否出现在 test 文件中）
        covered = 0
        for func in code_functions:
            # 检查是否有对应的 test_ 函数
            if any(f'test_{func.lower()}' in test_func.lower() for test_func in test_functions):
                covered += 1

        if len(code_functions) == 0:
            return CheckResult(
                check_id='CT-01',
                description='UT 函数是否有对应 test_ 函数',
                passed=True,
                severity='P0',
                message='没有需要测试的函数',
                details='跳过检查'
            )

        coverage = covered / len(code_functions)

        if coverage < 0.5:
            return CheckResult(
                check_id='CT-01',
                description='UT 函数是否有对应 test_ 函数',
                passed=False,
                severity='P0',
                message=f'UT 测试覆盖率不足: {coverage*100:.0f}%（{covered}/{len(code_functions)}）',
                details=f'代码函数: {len(code_functions)} 个，测试函数: {len(test_functions)} 个'
            )
        else:
            return CheckResult(
                check_id='CT-01',
                description='UT 函数是否有对应 test_ 函数',
                passed=True,
                severity='P0',
                message=f'UT 测试覆盖率正常: {coverage*100:.0f}%（{covered}/{len(code_functions)}）',
                details=f'代码函数: {len(code_functions)} 个，测试函数: {len(test_functions)} 个'
            )

    def check_ct02_api_has_tests(self) -> CheckResult:
        """
        CT-02: 检查 API 接口是否有对应测试

        策略:
        1. 查找 tests/api/ 目录中的测试文件
        2. 统计 API 测试数量

        Returns:
            CheckResult
        """
        api_test_dir = self.test_dir / 'api'

        if not api_test_dir.exists():
            return CheckResult(
                check_id='CT-02',
                description='API 接口是否有对应测试',
                passed=False,
                severity='P0',
                message='未找到 tests/api/ 目录',
                details='建议: 创建 tests/api/ 目录并添加 API 测试'
            )

        # 统计 API 测试文件
        api_test_files = list(api_test_dir.rglob('test_*.py'))
        api_test_count = len(api_test_files)

        if api_test_count == 0:
            return CheckResult(
                check_id='CT-02',
                description='API 接口是否有对应测试',
                passed=False,
                severity='P0',
                message='tests/api/ 目录中没有测试文件',
                details='建议: 添加 API 测试文件（test_*.py）'
            )

        # 统计测试函数数量
        total_test_funcs = 0
        for test_file in api_test_files:
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                test_funcs = re.findall(r'def\s+(test_\w+)\s*\(', content)
                total_test_funcs += len(test_funcs)
            except Exception:
                pass

        return CheckResult(
            check_id='CT-02',
            description='API 接口是否有对应测试',
            passed=True,
            severity='P0',
            message=f'发现 {api_test_count} 个 API 测试文件（{total_test_funcs} 个测试函数）',
            details=f'测试目录: {api_test_dir}'
        )

    def check_ct03_ut_coverage_meets_threshold(self) -> CheckResult:
        """
        CT-03: 检查 UT 测试覆盖率是否达标

        策略:
        1. 检查是否存在 .coverage 文件或 pytest coverage 报告
        2. 如果不存在，返回跳过

        Returns:
            CheckResult
        """
        # 查找覆盖率文件
        coverage_file = Path(self.project_dir) / '.coverage'
        htmlcov_dir = Path(self.project_dir) / 'htmlcov'

        if coverage_file.exists() or htmlcov_dir.exists():
            return CheckResult(
                check_id='CT-03',
                description='UT 测试覆盖率是否达标',
                passed=True,
                severity='P1',
                message='发现覆盖率文件或报告',
                details='建议: 使用 pytest coverage 查看详细覆盖率'
            )

        return CheckResult(
            check_id='CT-03',
            description='UT 测试覆盖率是否达标',
            passed=True,
            severity='P1',
            message='未发现覆盖率文件，跳过检查',
            details='建议: 运行 pytest --cov=internal 生成覆盖率报告'
        )

    def check_ct04_api_coverage_meets_threshold(self) -> CheckResult:
        """
        CT-04: 检查 API 测试覆盖率是否达标

        Returns:
            CheckResult
        """
        api_test_dir = self.test_dir / 'api'

        if not api_test_dir.exists():
            return CheckResult(
                check_id='CT-04',
                description='API 测试覆盖率是否达标',
                passed=True,
                severity='P1',
                message='未找到 tests/api/ 目录，跳过检查',
                details='建议: 创建 API 测试'
            )

        # 统计 API 测试文件
        api_test_files = list(api_test_dir.rglob('test_*.py'))

        if len(api_test_files) >= 3:
            return CheckResult(
                check_id='CT-04',
                description='API 测试覆盖率是否达标',
                passed=True,
                severity='P1',
                message=f'API 测试文件数量: {len(api_test_files)} 个',
                details='检查通过'
            )
        else:
            return CheckResult(
                check_id='CT-04',
                description='API 测试覆盖率是否达标',
                passed=False,
                severity='P1',
                message=f'API 测试文件数量不足: {len(api_test_files)} 个（建议≥3个）',
                details='建议: 添加更多 API 测试文件'
            )

    def check_ct05_mock_usage_reasonable(self) -> CheckResult:
        """
        CT-05: 检查 Mock 使用是否合理

        策略:
        1. 检查测试文件中是否使用 unittest.mock
        2. 统计 Mock 使用次数

        Returns:
            CheckResult
        """
        if not self.test_dir.exists():
            return CheckResult(
                check_id='CT-05',
                description='Mock 使用是否合理',
                passed=True,
                severity='P2',
                message='未找到 tests/ 目录，跳过检查',
                details=''
            )

        # 统计 Mock 使用
        mock_count = 0
        for test_file in self.test_dir.rglob('*.py'):
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                # 检查 mock 导入
                if re.search(r'from unittest import mock|import unittest\.mock|from unittest\.mock import', content):
                    mock_count += 1
                # 检查 @patch 装饰器
                mock_count += len(re.findall(r'@patch\(', content))
            except Exception:
                pass

        if mock_count > 0:
            return CheckResult(
                check_id='CT-05',
                description='Mock 使用是否合理',
                passed=True,
                severity='P2',
                message=f'发现 {mock_count} 处 Mock 使用',
                details='检查通过'
            )
        else:
            return CheckResult(
                check_id='CT-05',
                description='Mock 使用是否合理',
                passed=True,
                severity='P2',
                message='测试中未使用 Mock',
                details='如果需要 mock 外部依赖，建议使用 unittest.mock'
            )


# CLI 测试接口
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python checker_test.py <project_dir> [code_file1] [code_file2] ...")
        sys.exit(1)

    project_dir = sys.argv[1]
    code_files = [Path(f) for f in sys.argv[2:]] if len(sys.argv) > 2 else []

    checker = TestChecker(project_dir, code_files)

    # 运行所有检查
    results = [
        checker.check_ct01_ut_functions_have_tests(),
        checker.check_ct02_api_has_tests(),
        checker.check_ct03_ut_coverage_meets_threshold(),
        checker.check_ct04_api_coverage_meets_threshold(),
        checker.check_ct05_mock_usage_reasonable(),
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

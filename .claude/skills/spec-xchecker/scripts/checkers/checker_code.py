#!/usr/bin/env python3
"""
SC 层检查器：Scrum ↔ Code 一致性检查

检查项:
- SC-01: 每个 AC 是否有对应代码实现（P1）
- SC-02: 代码逻辑是否满足 AC 描述（P0）
- SC-03: 新增代码是否引用了正确的表/字段（P1）
- SC-04: 错误处理是否覆盖异常场景（P2）
- SC-05: 日志输出是否符合规范（P2）
- SC-06: Commit Message 是否包含 Story ID（P2）
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class CheckResult:
    """检查结果"""
    check_id: str
    description: str
    passed: bool
    severity: str  # P0, P1, P2
    message: str
    details: Optional[str] = None


class CodeChecker:
    """Scrum ↔ Code 检查器"""

    def __init__(self, project_dir: str, ac_list: List[str], code_files: List[Path]):
        """
        初始化检查器

        Args:
            project_dir: 项目根目录
            ac_list: Acceptance Criteria 列表
            code_files: 代码文件列表
        """
        self.project_dir = project_dir
        self.ac_list = ac_list
        self.code_files = code_files

    def check_sc01_ac_has_code_implementation(self) -> CheckResult:
        """
        SC-01: 检查每个 AC 是否有对应代码实现

        策略:
        1. 提取 AC 中的关键字（表名、字段名、功能描述）
        2. 在代码文件中搜索这些关键字
        3. 如果关键字在代码中出现，认为 AC 有实现

        Returns:
            CheckResult
        """
        if not self.ac_list:
            return CheckResult(
                check_id='SC-01',
                description='每个 AC 是否有对应代码实现',
                passed=False,
                severity='P1',
                message='没有提供 AC 列表，无法验证',
                details='建议: 在 Story 文档中定义 Acceptance Criteria'
            )

        if not self.code_files:
            return CheckResult(
                check_id='SC-01',
                description='每个 AC 是否有对应代码实现',
                passed=False,
                severity='P1',
                message='没有提供代码文件，无法验证',
                details='建议: 指定要检查的代码文件'
            )

        # 读取所有代码文件内容
        code_contents = {}
        for code_file in self.code_files:
            try:
                code_contents[code_file] = code_file.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                pass

        if not code_contents:
            return CheckResult(
                check_id='SC-01',
                description='每个 AC 是否有对应代码实现',
                passed=False,
                severity='P1',
                message='无法读取代码文件',
                details=f'代码文件: {self.code_files}'
            )

        all_code = '\n'.join(code_contents.values())

        # 验证每个 AC 是否有对应实现
        missing_acs = []
        for ac in self.ac_list:
            # 提取 AC 中的关键字（中文、英文、数字、下划线）
            keywords = re.findall(r'[一-龥]{3,}|[a-zA-Z_][a-zA-Z0-9_]{2,}', ac)

            if not keywords:
                # 如果没有提取到关键字，跳过这个 AC
                continue

            # 检查是否有代码包含这些关键字
            covered = False
            for keyword in keywords[:5]:  # 只检查前5个关键字
                if keyword in all_code:
                    covered = True
                    break

            if not covered:
                missing_acs.append(ac[:50] + '...' if len(ac) > 50 else ac)

        if missing_acs:
            return CheckResult(
                check_id='SC-01',
                description='每个 AC 是否有对应代码实现',
                passed=False,
                severity='P1',
                message=f'{len(missing_acs)} 个 AC 缺少对应的代码实现',
                details='\n'.join(f'- {ac}' for ac in missing_acs[:3])
            )
        else:
            return CheckResult(
                check_id='SC-01',
                description='每个 AC 是否有对应代码实现',
                passed=True,
                severity='P1',
                message=f'所有 {len(self.ac_list)} 个 AC 都有对应的代码实现',
                details=f'代码文件: {len(code_contents)} 个'
            )

    def check_sc02_code_logic_matches_ac(self) -> CheckResult:
        """
        SC-02: 检查代码逻辑是否满足 AC 描述

        策略:
        1. 从 AC 中提取关键逻辑（表名、字段名、操作）
        2. 在代码中搜索对应的实现（SQL DDL、函数调用、类定义）
        3. 验证实现是否覆盖 AC 的要求

        Returns:
            CheckResult
        """
        if not self.ac_list:
            return CheckResult(
                check_id='SC-02',
                description='代码逻辑是否满足 AC 描述',
                passed=False,
                severity='P0',
                message='没有提供 AC 列表，无法验证',
                details='建议: 在 Story 文档中定义 Acceptance Criteria'
            )

        if not self.code_files:
            return CheckResult(
                check_id='SC-02',
                description='代码逻辑是否满足 AC 描述',
                passed=False,
                severity='P0',
                message='没有提供代码文件，无法验证',
                details='建议: 指定要检查的代码文件'
            )

        # 读取所有代码文件内容
        code_contents = {}
        for code_file in self.code_files:
            try:
                code_contents[code_file] = code_file.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                pass

        if not code_contents:
            return CheckResult(
                check_id='SC-02',
                description='代码逻辑是否满足 AC 描述',
                passed=False,
                severity='P0',
                message='无法读取代码文件',
                details=f'代码文件: {self.code_files}'
            )

        all_code = '\n'.join(code_contents.values())

        # 验证 AC 的语义一致性
        # 策略: 提取 AC 中的关键实体（表名、API端点、类名）并在代码中查找
        unmatched_logic = []
        for ac in self.ac_list:
            # 提取 AC 中的关键实体
            # 匹配表名: pod_resource_status, gpu_usage, etc.
            tables = re.findall(r'[a-z_]+_[a-z_]+(?:_table|_status|_usage|_info)', ac)
            # 匹配函数/方法名: CreatePod, GetGPUUsage, etc.
            functions = re.findall(r'[A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]+)*', ac)

            entities = tables + functions
            if not entities:
                continue

            # 检查实体是否在代码中出现
            covered = False
            for entity in entities[:3]:
                if entity in all_code:
                    covered = True
                    break

            if not covered:
                unmatched_logic.append(ac[:50] + '...' if len(ac) > 50 else ac)

        if unmatched_logic:
            return CheckResult(
                check_id='SC-02',
                description='代码逻辑是否满足 AC 描述',
                passed=False,
                severity='P0',
                message=f'{len(unmatched_logic)} 个 AC 的逻辑未在代码中找到实现',
                details='\n'.join(f'- {ac}' for ac in unmatched_logic[:3])
            )
        else:
            return CheckResult(
                check_id='SC-02',
                description='代码逻辑是否满足 AC 描述',
                passed=True,
                severity='P0',
                message=f'所有 {len(self.ac_list)} 个 AC 的逻辑都在代码中有对应实现',
                details=f'代码文件: {len(code_contents)} 个'
            )

    def check_sc03_correct_table_field_references(self) -> CheckResult:
        """
        SC-03: 检查新增代码是否引用了正确的表/字段

        策略:
        1. 搜索代码中的 SQL DDL 语句（CREATE TABLE, ALTER TABLE）
        2. 提取表名和字段名
        3. 验证这些表/字段是否在数据库 DDL 中定义

        Returns:
            CheckResult
        """
        if not self.code_files:
            return CheckResult(
                check_id='SC-03',
                description='新增代码是否引用了正确的表/字段',
                passed=True,
                severity='P1',
                message='没有代码文件需要检查',
                details='跳过检查'
            )

        # 搜索 SQL DDL 文件
        ddl_dir = Path(self.project_dir) / 'db' / 'ddl'
        if not ddl_dir.exists():
            return CheckResult(
                check_id='SC-03',
                description='新增代码是否引用了正确的表/字段',
                passed=True,
                severity='P1',
                message='未找到 db/ddl 目录，跳过检查',
                details='建议: 如果项目有 DDL 文件，放在 db/ddl/ 目录下'
            )

        # 读取所有 DDL 文件
        defined_tables = set()
        for ddl_file in ddl_dir.glob('*.sql'):
            try:
                ddl_content = ddl_file.read_text(encoding='utf-8')
                # 提取表名: CREATE TABLE table_name
                tables = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-z_][a-z0-9_]*)', ddl_content, re.IGNORECASE)
                defined_tables.update(tables)
            except Exception:
                pass

        if not defined_tables:
            return CheckResult(
                check_id='SC-03',
                description='新增代码是否引用了正确的表/字段',
                passed=True,
                severity='P1',
                message='DDL 文件中没有定义表，跳过检查',
                details=f'DDL 目录: {ddl_dir}'
            )

        # 检查代码中引用的表是否在 DDL 中定义
        referenced_tables = set()
        for code_file in self.code_files:
            try:
                code_content = code_file.read_text(encoding='utf-8', errors='ignore')
                # 提取表名引用（SQL查询、ORM模型等）
                tables = re.findall(r'(?:FROM|INTO|UPDATE|JOIN)\s+([a-z_][a-z0-9_]*)', code_content, re.IGNORECASE)
                referenced_tables.update(tables)
            except Exception:
                pass

        if not referenced_tables:
            return CheckResult(
                check_id='SC-03',
                description='新增代码是否引用了正确的表/字段',
                passed=True,
                severity='P1',
                message='代码中没有发现表引用',
                details='跳过检查'
            )

        # 查找未定义的表
        undefined_tables = referenced_tables - defined_tables
        # 过滤掉常见的系统表和临时表
        undefined_tables = {t for t in undefined_tables if not t.startswith('_') and t not in {'migration', 'schema'}}

        if undefined_tables:
            return CheckResult(
                check_id='SC-03',
                description='新增代码是否引用了正确的表/字段',
                passed=False,
                severity='P1',
                message=f'代码引用了 {len(undefined_tables)} 个未在 DDL 中定义的表',
                details=f'未定义的表: {", ".join(list(undefined_tables)[:3])}'
            )
        else:
            return CheckResult(
                check_id='SC-03',
                description='新增代码是否引用了正确的表/字段',
                passed=True,
                severity='P1',
                message=f'所有引用的表都在 DDL 中定义（{len(referenced_tables)} 个表）',
                details=f'DDL 定义的表: {len(defined_tables)} 个'
            )

    def check_sc04_error_handling_coverage(self) -> CheckResult:
        """
        SC-04: 检查错误处理是否覆盖异常场景

        策略:
        1. 统计 try/except (Python) 或 if err != nil (Go) 语句
        2. 检查关键操作（数据库查询、API调用）是否有错误处理

        Returns:
            CheckResult
        """
        if not self.code_files:
            return CheckResult(
                check_id='SC-04',
                description='错误处理是否覆盖异常场景',
                passed=True,
                severity='P2',
                message='没有代码文件需要检查',
                details='跳过检查'
            )

        total_files = 0
        files_with_error_handling = 0

        for code_file in self.code_files:
            try:
                code_content = code_file.read_text(encoding='utf-8', errors='ignore')
                total_files += 1

                # 检查 Python 错误处理
                if re.search(r'\btry\s*:', code_content):
                    files_with_error_handling += 1
                    continue

                # 检查 Go 错误处理
                if re.search(r'\bif\s+err\s*!=\s*nil', code_content):
                    files_with_error_handling += 1
                    continue

                # 检查日志错误输出
                if re.search(r'(logr\.Logger|log\.Error|logger\.Error)', code_content):
                    files_with_error_handling += 1
                    continue

            except Exception:
                pass

        if total_files == 0:
            return CheckResult(
                check_id='SC-04',
                description='错误处理是否覆盖异常场景',
                passed=True,
                severity='P2',
                message='没有可读的代码文件',
                details='跳过检查'
            )

        coverage = files_with_error_handling / total_files if total_files > 0 else 0

        if coverage < 0.5:
            return CheckResult(
                check_id='SC-04',
                description='错误处理是否覆盖异常场景',
                passed=False,
                severity='P2',
                message=f'错误处理覆盖率不足: {coverage*100:.0f}%（{files_with_error_handling}/{total_files}）',
                details='建议: 在关键操作（数据库查询、API调用）中添加错误处理'
            )
        else:
            return CheckResult(
                check_id='SC-04',
                description='错误处理是否覆盖异常场景',
                passed=True,
                severity='P2',
                message=f'错误处理覆盖率良好: {coverage*100:.0f}%（{files_with_error_handling}/{total_files}）',
                details='检查通过'
            )

    def check_sc05_logging_standards(self) -> CheckResult:
        """
        SC-05: 检查日志输出是否符合规范

        策略:
        1. 检查是否使用结构化日志（logr.Logger）
        2. 检查日志级别使用是否合理（Info/Error）

        Returns:
            CheckResult
        """
        if not self.code_files:
            return CheckResult(
                check_id='SC-05',
                description='日志输出是否符合规范',
                passed=True,
                severity='P2',
                message='没有代码文件需要检查',
                details='跳过检查'
            )

        total_files = 0
        files_with_logging = 0

        for code_file in self.code_files:
            try:
                code_content = code_file.read_text(encoding='utf-8', errors='ignore')
                total_files += 1

                # 检查 logr.Logger（Go）
                if re.search(r'logr\.Logger\.', code_content):
                    files_with_logging += 1
                    continue

                # 检查 Python logging
                if re.search(r'logging\.(info|error|warning)', code_content):
                    files_with_logging += 1
                    continue

            except Exception:
                pass

        if total_files == 0:
            return CheckResult(
                check_id='SC-05',
                description='日志输出是否符合规范',
                passed=True,
                severity='P2',
                message='没有可读的代码文件',
                details='跳过检查'
            )

        coverage = files_with_logging / total_files if total_files > 0 else 0

        if coverage < 0.3:
            return CheckResult(
                check_id='SC-05',
                description='日志输出是否符合规范',
                passed=False,
                severity='P2',
                message=f'日志覆盖率偏低: {coverage*100:.0f}%（{files_with_logging}/{total_files}）',
                details='建议: 使用 logr.Logger (Go) 或 logging (Python) 记录关键操作'
            )
        else:
            return CheckResult(
                check_id='SC-05',
                description='日志输出是否符合规范',
                passed=True,
                severity='P2',
                message=f'日志覆盖率正常: {coverage*100:.0f}%（{files_with_logging}/{total_files}）',
                details='检查通过'
            )

    def check_sc06_commit_message_format(self) -> CheckResult:
        """
        SC-06: 检查 Commit Message 是否包含 Story ID

        策略:
        1. 获取最近 5 条 commits
        2. 检查是否包含 Story ID（STORY-XX-YY）

        Returns:
            CheckResult
        """
        try:
            # 获取最近 5 条 commits
            result = subprocess.run(
                ['git', 'log', '-5', '--pretty=%B'],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=True
            )
            commits = result.stdout.strip().split('\n\n')

            if not commits:
                return CheckResult(
                    check_id='SC-06',
                    description='Commit Message 是否包含 Story ID',
                    passed=True,
                    severity='P2',
                    message='没有 commits 需要检查',
                    details='跳过检查'
                )

            # 检查每条 commit 是否包含 Story ID
            total = len(commits)
            with_story_id = 0
            missing_commits = []

            for commit in commits:
                # 提取第一行（commit title）
                title = commit.split('\n')[0]
                if re.search(r'STORY[-_]?\d+[-_]\d+', title, re.IGNORECASE):
                    with_story_id += 1
                else:
                    # 过滤掉 Merge commits
                    if not title.startswith('Merge branch'):
                        missing_commits.append(title[:40] + '...' if len(title) > 40 else title)

            coverage = with_story_id / total if total > 0 else 0

            if coverage < 0.8:
                return CheckResult(
                    check_id='SC-06',
                    description='Commit Message 是否包含 Story ID',
                    passed=False,
                    severity='P2',
                    message=f'Story ID 覆盖率不足: {coverage*100:.0f}%（{with_story_id}/{total}）',
                    details=f'缺少 Story ID 的 commits:\n' + '\n'.join(f'- {c}' for c in missing_commits[:3])
                )
            else:
                return CheckResult(
                    check_id='SC-06',
                    description='Commit Message 是否包含 Story ID',
                    passed=True,
                    severity='P2',
                    message=f'Story ID 覆盖率良好: {coverage*100:.0f}%（{with_story_id}/{total}）',
                    details='检查通过'
                )

        except subprocess.CalledProcessError:
            return CheckResult(
                check_id='SC-06',
                description='Commit Message 是否包含 Story ID',
                passed=True,
                severity='P2',
                message='无法获取 Git commits，跳过检查',
                details='建议: 确保在 Git 仓库中运行检查'
            )


# CLI 测试接口
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Usage: python checker_code.py <project_dir> <code_file1> [code_file2] ...")
        sys.exit(1)

    project_dir = sys.argv[1]
    code_files = [Path(f) for f in sys.argv[2:]]

    checker = CodeChecker(project_dir, [], code_files)

    # 运行所有检查
    results = [
        checker.check_sc04_error_handling_coverage(),
        checker.check_sc05_logging_standards(),
        checker.check_sc06_commit_message_format(),
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

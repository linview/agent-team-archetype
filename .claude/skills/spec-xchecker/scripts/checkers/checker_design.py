#!/usr/bin/env python3
"""
DS 层检查器：Design Spec ↔ Scrum 文档一致性检查

检查项:
- DS-01: Story 是否引用 Design Spec（P1）
- DS-02: AC 是否与 Design Spec 一致（P0）
- DS-03: Design Spec 引用是否正确（P2）
- DS-04: Epic 规划是否与 Design Spec 一致（P2）

降级语义（v4.2.1，ISSUE-20261124-003 fail-open 盲区修复）:
机械启发式的强项是「有明确命中模式的检查」——提取失败/模式未命中不代表通过。
CheckResult.status 区分三种结论，避免「未命中即 PASS」把未覆盖伪装成机械全绿:
- None（默认）: 按 passed 推导（True→真实通过 / False→真实失败）
- 'SKIP': 检查未覆盖（提取失败/章节未识别），不计入失败统计，报告展示覆盖率说明
- 'WARN': 通过项附带降级提示（部分校验未执行/无法完整对账）
"""

import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Design Spec 版本号识别（v4.2.1 扩展: 原只认中文键「版本：vX.Y」→ 中文/英文键 + v 前缀可选
# + YAML 引号形态可选，覆盖 frontmatter `version: v2.1` / `version: "v2.1"` / `version: 2.1` /
# `Version: v2.1` 等形态；ds05_fixture 带引号 frontmatter 即真实素材中抓到的第四形态）
VERSION_PATTERN = re.compile(r'(?:版本|Version)\s*[:：]?\s*["\']?v?(\d+\.\d+)["\']?', re.IGNORECASE)


@dataclass
class CheckResult:
    """检查结果"""
    check_id: str
    description: str
    passed: bool
    severity: str  # P0, P1, P2
    message: str
    details: Optional[str] = None
    status: Optional[str] = None  # None / 'SKIP' / 'WARN'（降级语义，见模块 docstring）


class DesignChecker:
    """Design Spec ↔ Scrum 检查器"""

    def __init__(self, story_content: str, design_spec_content: Optional[str] = None):
        """
        初始化检查器

        Args:
            story_content: Story 文档内容
            design_spec_content: Design Spec 文档内容（可选）
        """
        self.story_content = story_content
        self.design_spec_content = design_spec_content or ''

    def check_ds01_story_references_design_spec(self) -> CheckResult:
        """
        DS-01: 检查 Story 是否引用 Design Spec

        Returns:
            CheckResult
        """
        # 最强证据：Design Spec 已成功加载（load_design_spec 支持 frontmatter design_docs/design_refs + 正文两种格式，v2.7 修复，v4.1.3 扩展）
        # 避免误报 frontmatter design_docs/design_refs 引用（DS-01 原只认正文 "Design Spec:" 行）
        if self.design_spec_content:
            return CheckResult(
                check_id='DS-01',
                description='Story 是否引用 Design Spec',
                passed=True,
                severity='P1',
                message='Story 引用了 Design Spec（已成功加载内容）',
                details='引用来源: frontmatter design_docs/design_refs 或正文 Design Spec 行（由 load_design_spec 解析）'
            )

        # 检查 Story 文档中是否有 Design Spec 引用
        # 支持格式：Design Spec:, **Design Spec**:, **Design Spec v4.2**：
        pattern = r'\*{0,2}Design[^\n]*?Spec\*{0,2}[^:\n]*?[:：]'
        match = re.search(pattern, self.story_content, re.IGNORECASE)

        if match:
            # 进一步检查引用路径是否存在
            ref_pattern = r'\*{0,2}Design[^\n]*?Spec\*{0,2}[^:\n]*?[:：]\s*\[([^\]]+\.md)'
            ref_match = re.search(ref_pattern, self.story_content, re.IGNORECASE)

            if ref_match:
                ref_path = ref_match.group(1).strip()
                return CheckResult(
                    check_id='DS-01',
                    description='Story 是否引用 Design Spec',
                    passed=True,
                    severity='P1',
                    message=f'Story 引用了 Design Spec: {ref_path}',
                    details=f'引用路径: {ref_path}'
                )
            else:
                return CheckResult(
                    check_id='DS-01',
                    description='Story 是否引用 Design Spec',
                    passed=True,
                    severity='P1',
                    message='Story 提到了 Design Spec，但没有明确的文件引用',
                    details='建议: 添加明确的 Design Spec 文件路径'
                )
        else:
            return CheckResult(
                check_id='DS-01',
                description='Story 是否引用 Design Spec',
                passed=False,
                severity='P1',
                message='Story 文档未引用 Design Spec',
                details='建议: 在 Story 文档中添加 "Design Spec: ../design/xxx.md"'
            )

    def check_ds02_ac_matches_design_spec(self, ac_list: list[str]) -> CheckResult:
        """
        DS-02: 检查 AC 是否与 Design Spec 一致

        策略:
        1. 如果没有 Design Spec，跳过检查（无法验证）
        2. 提取 Design Spec 中的关键需求
        3. 验证 AC 是否覆盖了这些需求

        Args:
            ac_list: Acceptance Criteria 列表

        Returns:
            CheckResult
        """
        if not self.design_spec_content:
            return CheckResult(
                check_id='DS-02',
                description='AC 是否与 Design Spec 一致',
                passed=False,
                severity='P0',
                message='Story 文档中未找到 Design Spec 引用',
                details='建议: 在 Story 文档中添加 Design Spec 引用（例如：Design Spec: ../design/xxx.md）'
            )

        # 提取 Design Spec 中的关键需求
        # 查找 "需求"、"Requirements"、"功能" 等章节
        requirement_patterns = [
            r'##\s*(需求|Requirements|功能需求)(.*?)^(##\s*)',
            r'##\s*(功能|Features|核心功能)(.*?)^(##\s*)',
        ]

        spec_requirements = []
        for pattern in requirement_patterns:
            match = re.search(pattern, self.design_spec_content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            if match:
                section = match.group(2)
                # 提取列表项
                items = re.findall(r'[-*]\s*(.*?)(?=\n|$)', section, re.MULTILINE)
                spec_requirements.extend([item.strip() for item in items if len(item.strip()) > 10])
                break

        if not spec_requirements:
            # fail-open 盲区修复（ISSUE-20261124-003）：提取失败 ≠ 真实通过。
            # 需求章节未识别时 DS-02 未覆盖——返回 SKIP 而非 passed=True 假绿，
            # 无需求章节（如表格型设计文档）不应获得与合规文档一致的机械全绿
            return CheckResult(
                check_id='DS-02',
                description='AC 是否与 Design Spec 一致',
                passed=False,
                severity='P0',
                message='DS-02 未覆盖：Design Spec 未识别出需求章节（SKIP，不计入失败）',
                details=f'找到 {len(ac_list)} 个 AC；建议: Design Spec 补充「需求/Requirements」章节（列表项）以启用 AC 一致性校验',
                status='SKIP'
            )

        # 验证 AC 是否覆盖了 Design Spec 的关键需求
        # 简化策略: 检查关键字覆盖度
        missing_requirements = []
        for req in spec_requirements:
            # 提取关键字（前5个字符）
            keywords = re.findall(r'[一-龥]+|[a-zA-Z]+', req)[:5]
            keyword_pattern = '|'.join(keywords)

            # 检查是否有 AC 包含这些关键字
            covered = False
            for ac in ac_list:
                if re.search(keyword_pattern, ac, re.IGNORECASE):
                    covered = True
                    break

            if not covered:
                missing_requirements.append(req)

        if missing_requirements:
            return CheckResult(
                check_id='DS-02',
                description='AC 是否与 Design Spec 一致',
                passed=False,
                severity='P0',
                message=f'AC 未完全覆盖 Design Spec 需求（缺少 {len(missing_requirements)} 项）',
                details=f'缺失需求:\n' + '\n'.join(f'- {req}' for req in missing_requirements[:3])
            )
        else:
            return CheckResult(
                check_id='DS-02',
                description='AC 是否与 Design Spec 一致',
                passed=True,
                severity='P0',
                message=f'AC 已覆盖 Design Spec 中的所有关键需求（{len(spec_requirements)} 项）',
                details=f'AC 数量: {len(ac_list)}'
            )

    def check_ds03_design_spec_reference_valid(self, project_dir: str) -> CheckResult:
        """
        DS-03: 检查 Design Spec 引用是否正确

        验证:
        1. Design Spec 文件是否存在
        2. Design Spec 版本号格式是否正确

        Args:
            project_dir: 项目根目录

        Returns:
            CheckResult
        """
        # 最强证据：Design Spec 已成功加载即证明引用路径有效（v2.7 修复：支持 frontmatter design_docs）
        # 避免误报 frontmatter design_docs 引用（DS-03 原只认正文 "Design Spec:" 行）
        if self.design_spec_content:
            version_match = VERSION_PATTERN.search(self.design_spec_content)
            if version_match:
                version = version_match.group(1)
                return CheckResult(
                    check_id='DS-03',
                    description='Design Spec 引用是否正确',
                    passed=True,
                    severity='P2',
                    message=f'Design Spec 引用正确（版本 v{version}）',
                    details='引用路径已验证（load_design_spec 成功加载）'
                )
            # fail-open 盲区修复（ISSUE-20261124-003）：引用有效性已真实通过（加载成功），
            # 但版本号未识别 = 版本校验未执行——WARN 显性化，不再静默跳过
            return CheckResult(
                check_id='DS-03',
                description='Design Spec 引用是否正确',
                passed=True,
                severity='P2',
                message='Design Spec 引用正确（已成功加载）——版本号未识别，版本校验未覆盖（WARN）',
                details='引用路径已验证（load_design_spec 成功加载）；版本校验未执行: 未匹配到「版本/Version」键'
                        '（支持中文键「版本：vX.Y」与英文键「version: vX.Y / X.Y」及 frontmatter 形态）',
                status='WARN'
            )

        # 提取 Design Spec 引用路径
        ref_pattern = r'Design\s+Spec\s*[:：]\s*([^\n]+\.md)'
        match = re.search(ref_pattern, self.story_content, re.IGNORECASE)

        if not match:
            return CheckResult(
                check_id='DS-03',
                description='Design Spec 引用是否正确',
                passed=False,
                severity='P2',
                message='Story 文档中未找到 Design Spec 引用',
                details='建议: 添加 "Design Spec: ../design/xxx.md"'
            )

        ref_path = match.group(1).strip()

        # 解析路径
        if ref_path.startswith('../'):
            # 相对路径（从 docs/scrum/story/）
            design_spec_path = Path(project_dir) / 'docs' / 'scrum' / 'story' / ref_path
        elif ref_path.startswith('/'):
            # 绝对路径
            design_spec_path = Path(ref_path)
        else:
            # 相对项目根目录
            design_spec_path = Path(project_dir) / 'docs' / 'design' / ref_path

        # 检查文件是否存在
        if not design_spec_path.exists():
            return CheckResult(
                check_id='DS-03',
                description='Design Spec 引用是否正确',
                passed=False,
                severity='P2',
                message=f'Design Spec 文件不存在: {ref_path}',
                details=f'预期路径: {design_spec_path}'
            )

        # 检查版本号格式（如果有的话）
        if self.design_spec_content:
            # 匹配版本号: v1.0, v2.1, version: v2.1, 版本: 2.1, etc.（v4.2.1 同步 VERSION_PATTERN）
            version_match = VERSION_PATTERN.search(self.design_spec_content)

            if version_match:
                version = version_match.group(1)
                return CheckResult(
                    check_id='DS-03',
                    description='Design Spec 引用是否正确',
                    passed=True,
                    severity='P2',
                    message=f'Design Spec 引用正确（版本: v{version}）',
                    details=f'文件路径: {design_spec_path}'
                )

        return CheckResult(
            check_id='DS-03',
            description='Design Spec 引用是否正确',
            passed=True,
            severity='P2',
            message=f'Design Spec 引用正确',
            details=f'文件路径: {design_spec_path}'
        )

    def check_ds04_epic_matches_design_spec(self) -> CheckResult:
        """
        DS-04: 检查 Epic 规划是否与 Design Spec 一致

        验证:
        1. Story 文档中的 Epic 引用
        2. Design Spec 中的 Epic 规划

        Returns:
            CheckResult
        """
        # 提取 Story 中的 Epic 引用
        epic_pattern = r'Epic[-_]?\s*[\d:：]+|epic[-_]?\s*[\d:：]+'
        story_epics = re.findall(epic_pattern, self.story_content, re.IGNORECASE)

        if not story_epics:
            # fail-open 盲区修复（ISSUE-20261124-003）：无 Epic 引用 = DS-04 未覆盖。
            # passed 保留 True（非 Epic 拆分属合法场景，不判失败），但 WARN 显性化——
            # 不再以「Epic 引用检查通过」的形态静默放行
            return CheckResult(
                check_id='DS-04',
                description='Epic 规划是否与 Design Spec 一致',
                passed=True,
                severity='P2',
                message='Story 文档中未找到 Epic 引用，DS-04 未覆盖（无法执行 Epic 对账）',
                details='建议: 如果属于某个 Epic，在 Story 中明确说明',
                status='WARN'
            )

        # 最强证据（v4.1.3）：Design Spec 显式指派本 Story（「实装归 STORY-x-xx」类反向追踪）——
        # 一份 guide 跨 Epic 承载多个 Story（不同章节归不同 Epic）时 Epic 编号无交集
        # 属常态而非不一致；Story 级指派优先于 Epic 编号交集判定
        if self.design_spec_content:
            id_match = re.search(r'^id:\s*"?STORY-([\d-]+)"?', self.story_content, re.MULTILINE)
            if id_match:
                sid = id_match.group(1)
                if f'STORY-{sid}' in self.design_spec_content or f'story-{sid}' in self.design_spec_content:
                    return CheckResult(
                        check_id='DS-04',
                        description='Epic 规划是否与 Design Spec 一致',
                        passed=True,
                        severity='P2',
                        message=f'Design Spec 显式指派本 Story（STORY-{sid}），双向追踪成立',
                        details='Story 级指派（实装归 STORY-x-xx）优先于 Epic 编号交集：'
                                '跨 Epic 服务型 guide 中 Epic 编号无交集属常态'
                    )

        # 如果有 Design Spec，检查是否提到了相同的 Epic
        if self.design_spec_content:
            spec_epics = re.findall(epic_pattern, self.design_spec_content, re.IGNORECASE)

            # 标准化 Epic 编号（Epic-15, epic-15, EPIC_15 → 15）
            def normalize_epic(epic_str):
                return re.findall(r'\d+', epic_str)[0] if re.findall(r'\d+', epic_str) else None

            story_epic_nums = set(filter(None, (normalize_epic(e) for e in story_epics)))
            spec_epic_nums = set(filter(None, (normalize_epic(e) for e in spec_epics)))

            if story_epic_nums and spec_epic_nums:
                # 检查是否有交集
                if story_epic_nums & spec_epic_nums:
                    return CheckResult(
                        check_id='DS-04',
                        description='Epic 规划是否与 Design Spec 一致',
                        passed=True,
                        severity='P2',
                        message=f'Epic 引用一致: Epic-{list(story_epic_nums)[0]}',
                        details=f'Story Epic: {story_epics}, Design Spec Epic: {spec_epics}'
                    )
                else:
                    return CheckResult(
                        check_id='DS-04',
                        description='Epic 规划是否与 Design Spec 一致',
                        passed=False,
                        severity='P2',
                        message=f'Epic 引用不一致: Story 提到 {story_epics}，Design Spec 提到 {spec_epics}',
                        details='建议: 确保 Story 和 Design Spec 中的 Epic 引用一致'
                    )

        # 兜底（v4.2.1 未覆盖显性化）：快速通道与交集判定均未命中——Design Spec 未加载
        # 或 Spec 中无 Epic 规划引用，对账无法完成。passed 保留 True（不吞既有语义），
        # WARN 显性化未覆盖，不再伪装成「检查通过」（ISSUE-20261124-003）
        if not self.design_spec_content:
            reason = 'Design Spec 未加载，Epic 对账无法执行'
        else:
            reason = 'Design Spec 中未找到 Epic 规划引用，Epic 对账无法完成'
        return CheckResult(
            check_id='DS-04',
            description='Epic 规划是否与 Design Spec 一致',
            passed=True,
            severity='P2',
            message=f'DS-04 未覆盖：{reason}（WARN）',
            details=f'Story Epic: {story_epics}',
            status='WARN'
        )


# CLI 测试接口
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python checker_design.py <story_file> [design_spec_file]")
        sys.exit(1)

    story_file = Path(sys.argv[1])
    design_spec_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    story_content = story_file.read_text(encoding='utf-8')
    design_spec_content = design_spec_file.read_text(encoding='utf-8') if design_spec_file else None

    checker = DesignChecker(story_content, design_spec_content)

    # 运行所有检查
    results = [
        checker.check_ds01_story_references_design_spec(),
        checker.check_ds03_design_spec_reference_valid(str(story_file.parent.parent.parent.parent)),
    ]

    if design_spec_content:
        results.append(checker.check_ds02_ac_matches_design_spec([]))
        results.append(checker.check_ds04_epic_matches_design_spec())

    # 打印结果（v4.2.1: 降级语义区分展示——SKIP 未覆盖 / WARN 降级提示）
    for result in results:
        if result.status == 'SKIP':
            status = "⏭️ SKIP"
        elif result.status == 'WARN':
            status = "⚠️ WARN"
        else:
            status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"{status} [{result.check_id}] {result.description}")
        print(f"   优先级: {result.severity}")
        print(f"   消息: {result.message}")
        if result.details:
            print(f"   详情: {result.details}")
        print()

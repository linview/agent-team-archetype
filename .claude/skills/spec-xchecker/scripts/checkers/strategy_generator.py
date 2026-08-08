#!/usr/bin/env python3
"""
AC 驱动的智能检查策略生成器（v2.5）

核心功能：
1. 检测 Story 的 AC 类型（10 种类型）
2. 映射到检查策略（正向 + 负向规则）
3. 动态计算置信度
4. 生成最终的检查项列表

作者: maintainer@example.com
版本: v2.5
日期: 2026-04-25
"""

import re
from typing import Dict, List, Set, Tuple


class ACBasedStrategyGenerator:
    """
    AC 驱动的智能检查策略生成器（v2.5）

    核心改进：
    - Level 1: 扩展 AC 类型映射表（10 种类型）
    - Level 2: 负向规则引擎（positive_checks + negative_checks）
    - Level 3: 动态置信度计算
    """

    def __init__(self, story_content: str, ac_list: List[Dict]):
        """
        初始化策略生成器

        Args:
            story_content: Story 文档内容
            ac_list: AC 列表（格式：[{"title": "...", "description": "..."}, ...]）
        """
        self.story_content = story_content
        self.ac_list = ac_list

    # ============================================================
    # AC 类型关键词匹配模式（v2.5 扩展版）
    # ============================================================

    AC_TYPE_PATTERNS = {
        # ===== v2.3 原有 5 种类型 =====
        "ddl": [
            r"DDL", r"ALTER\s+TABLE", r"CREATE\s+TABLE", r"DROP\s+TABLE",
            r"数据库迁移", r"数据库\s+DDL", r"表结构\s+变更"
        ],
        "sit_test": [
            r"SIT\s+测试", r"test_sit", r"修复\s+用例", r"集成测试",
            r"test_bug_\d+", r"场景\s+测试"
        ],
        "uat_test": [
            r"UAT\s+测试", r"test_uat", r"用户\s+验收", r"验收\s+测试"
        ],
        "go_code": [
            r"internal/pkg", r"\.go\s+文件", r"\.go\b", r"Go\s+代码",
            r"Golang", r"go\s+build", r"go\s+test", r"go\s+mod"
        ],
        "architecture": [
            r"架构\s+设计", r"设计\s+原则", r"SKILL", r"设计\s+文档",
            r"系统\s+架构"
        ],

        # ===== v2.5 新增 5 种类型 =====
        "monitoring": [
            r"Prometheus\s+指标", r"Grafana\s+Dashboard", r"告警\s+规则",
            r"监控\s+告警", r"Alert\s+配置", r"Metrics?", r"监控\s+指标"
        ],
        "documentation": [
            r"Design\s+Spec\s+更新", r"运维\s+手册", r"决策\s+记录",
            r"README\s+更新", r"文档\s+更新", r"更新\s+文档"
        ],
        "database_feature": [
            r"TTL\s+自动清理", r"Trigger\s+触发器", r"存储\s+过程",
            r"PostgreSQL\s+特性", r"分区\s+表", r"数据库\s+特性",
            r"Vacuum", r"自动\s+清理"
        ],
        "data_evaluation": [
            r"数据\s+评估", r"覆盖率\s+统计", r"质量\s+检查",
            r"sanity\s+check", r"数据\s+分析", r"数据\s+质量",
            r"覆盖率\s+检查"
        ],
        "bugfix_p2": [
            r"P2\s+优先级", r"监控\s+缓解", r"文档\s+记录",
            r"降级\s+处理", r"缓解\s+措施", r"已知\s+限制",
            r"Bug\s+修复", r"race\s+condition"
        ]
    }

    # ============================================================
    # AC 类型映射表（v2.5 扩展版：10 种类型）
    # ============================================================

    AC_TYPE_MAPPING = {
        # ===== v2.3 原有 5 种类型 =====
        "ddl": {
            "positive_checks": ["DS-01", "DS-02", "SC-06"],
            "negative_checks": ["SC-01", "SC-02", "SC-03", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05",
                              "ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06"],
            "reasoning": "DDL 变更（数据库迁移）不需要代码/测试检查，重点在 Design Spec 引用"
        },
        "sit_test": {
            "positive_checks": ["DS-01", "DS-02", "ST-01", "ST-02", "ST-03", "ST-05"],
            "negative_checks": ["SC-01", "SC-02", "SC-03", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05"],
            "reasoning": "SIT 测试用例修复重点在 SIT 测试检查，不需要代码/单元测试检查"
        },
        "uat_test": {
            "positive_checks": ["DS-01", "DS-02", "ST-01", "ST-02", "ST-04"],
            "negative_checks": ["SC-01", "SC-02", "SC-03", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05"],
            "reasoning": "UAT 测试重点在用户场景覆盖，不需要代码/单元测试检查"
        },
        "go_code": {
            "positive_checks": ["DS-01", "DS-02", "DS-03", "DS-04",
                              "SC-01", "SC-02", "SC-03", "SC-04", "SC-05", "SC-06",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05",
                              "ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06"],
            "negative_checks": [],
            "reasoning": "Go 代码开发需要完整的四路验证（DS + SC + CT + ST）"
        },
        "architecture": {
            "positive_checks": ["DS-01", "DS-02", "SC-06"],
            "negative_checks": ["SC-01", "SC-02", "SC-03", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05",
                              "ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06"],
            "reasoning": "架构设计重点在 Design Spec，不需要代码/测试检查"
        },

        # ===== v2.5 新增 5 种类型 =====
        "monitoring": {
            "positive_checks": ["DS-01", "SC-06"],
            "negative_checks": ["SC-01", "SC-02", "SC-03", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05",
                              "ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06"],
            "reasoning": "监控告警（Prometheus/Grafana）重点在 Design Spec 和 Commit Message，不需要代码/测试检查"
        },
        "documentation": {
            "positive_checks": ["DS-01", "SC-06"],
            "negative_checks": ["SC-01", "SC-02", "SC-03", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05",
                              "ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06"],
            "reasoning": "文档更新重点在 Design Spec 和 Commit Message，不需要代码/测试检查"
        },
        "database_feature": {
            "positive_checks": ["DS-01", "DS-02", "DS-03", "DS-04",
                              "SC-03", "SC-06",
                              "ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06"],
            "negative_checks": ["SC-01", "SC-02", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05"],
            "reasoning": "数据库特性实现（TTL/Trigger/存储过程）不需要单元测试，重点在 SIT 测试验证功能正确性"
        },
        "data_evaluation": {
            "positive_checks": ["DS-01", "SC-06"],
            "negative_checks": ["SC-01", "SC-02", "SC-03", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05",
                              "ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06"],
            "reasoning": "数据评估（质量检查/覆盖率统计）重点在 Design Spec，不需要代码/测试检查"
        },
        "bugfix_p2": {
            "positive_checks": ["DS-01", "SC-06"],
            "negative_checks": ["SC-01", "SC-02", "SC-03", "SC-04", "SC-05",
                              "CT-01", "CT-02", "CT-03", "CT-04", "CT-05",
                              "ST-01", "ST-02", "ST-03", "ST-04", "ST-05", "ST-06"],
            "reasoning": "P2 Bug 修复（监控+文档缓解措施）不需要代码/测试检查，重点在 Design Spec 引用和 Commit Message 规范"
        }
    }

    # ============================================================
    # 公共方法：生成智能检查策略
    # ============================================================

    def generate_strategy(self) -> Dict:
        """
        生成智能检查策略

        Returns:
            dict: {
                "story_type": "DATABASE_FEATURE_WITH_SIT_TESTING",
                "detected_ac_types": ["database_feature", "sit_test"],
                "positive_checks": ["DS-01", ...],
                "negative_checks": ["CT-01", ...],
                "final_checks": ["DS-01", ...],
                "confidence": 88.0,
                "reasoning": "检测到 AC 类型: database_feature, sit_test"
            }
        """
        # Step 1: 检测 AC 类型
        detected_types = self._detect_ac_types()

        # Step 2: 映射到检查策略（正向 + 负向）
        positive_checks, negative_checks, reasoning_parts = self._map_to_strategies(detected_types)

        # Step 3: 计算最终检查项
        final_checks = set(positive_checks) - set(negative_checks)

        # Step 4: 计算置信度
        confidence = self._calculate_confidence(detected_types, len(self.ac_list))

        # Step 5: 生成 Story 类型描述
        story_type = self._generate_story_type_description(detected_types)

        return {
            "story_type": story_type,
            "detected_ac_types": detected_types,
            "positive_checks": sorted(positive_checks),
            "negative_checks": sorted(negative_checks),
            "final_checks": sorted(final_checks),
            "confidence": round(confidence, 1),
            "reasoning": f"检测到 AC 类型: {', '.join(reasoning_parts)}"
        }

    # ============================================================
    # 内部方法：AC 类型检测
    # ============================================================

    def _detect_ac_types(self) -> List[str]:
        """
        检测 AC 类型

        Returns:
            List[str]: 检测到的 AC 类型列表
        """
        detected = []

        for ac_type, patterns in self.AC_TYPE_PATTERNS.items():
            for pattern in patterns:
                # 检查 AC 标题 + AC 描述 + Story 整体内容
                if self._check_pattern_in_content(pattern):
                    if ac_type not in detected:
                        detected.append(ac_type)
                    break

        return detected

    def _check_pattern_in_content(self, pattern: str) -> bool:
        """
        检查正则模式是否匹配内容

        Args:
            pattern: 正则表达式

        Returns:
            bool: 是否匹配
        """
        # 检查 AC 列表（元素可能是 str 或 dict，兼容 extract_acceptance_criteria 的 List[str] 约定）
        for ac in self.ac_list:
            if isinstance(ac, dict):
                ac_text = f"{ac.get('title', '')} {ac.get('description', '')}"
            else:
                ac_text = str(ac)

            if re.search(pattern, ac_text, re.IGNORECASE):
                return True

        # 检查 Story 整体内容
        if re.search(pattern, self.story_content, re.IGNORECASE):
            return True

        return False

    # ============================================================
    # 内部方法：策略映射
    # ============================================================

    def _map_to_strategies(self, detected_types: List[str]) -> Tuple[Set[str], Set[str], List[str]]:
        """
        映射到检查策略

        Args:
            detected_types: 检测到的 AC 类型列表

        Returns:
            Tuple[Set[str], Set[str], List[str]]: (positive_checks, negative_checks, reasoning_parts)
        """
        all_positive = set()
        all_negative = set()
        reasoning_parts = []

        for ac_type in detected_types:
            if ac_type in self.AC_TYPE_MAPPING:
                mapping = self.AC_TYPE_MAPPING[ac_type]
                all_positive.update(mapping["positive_checks"])
                all_negative.update(mapping["negative_checks"])

                # 添加类型描述
                type_descriptions = {
                    "ddl": "DDL 变更",
                    "sit_test": "SIT 测试",
                    "uat_test": "UAT 测试",
                    "go_code": "Go 代码开发",
                    "architecture": "架构设计",
                    "monitoring": "监控告警",
                    "documentation": "文档更新",
                    "database_feature": "数据库特性",
                    "data_evaluation": "数据评估",
                    "bugfix_p2": "P2 Bug 修复"
                }
                reasoning_parts.append(type_descriptions.get(ac_type, ac_type))

        return all_positive, all_negative, reasoning_parts

    # ============================================================
    # 内部方法：置信度计算
    # ============================================================

    def _calculate_confidence(self, detected_types: List[str], ac_size: int) -> float:
        """
        动态计算置信度

        算法：
        1. 单一类型：高置信度（95%）
        2. 双类型混合：中高置信度（88%）
        3. 三类型及以上：中等置信度（80%）
        4. 无法分类：低置信度（60%）
        5. AC 数量修正：AC 越多，置信度越高（最多 +3%）

        Args:
            detected_types: 检测到的 AC 类型列表
            ac_size: AC 数量

        Returns:
            float: 置信度（0-100）
        """
        base_confidence = 90.0
        num_types = len(detected_types)

        # 类型数量惩罚
        if num_types == 0:
            return 60.0  # 无法分类
        elif num_types == 1:
            confidence = base_confidence + 5.0  # 95%
        elif num_types == 2:
            confidence = base_confidence - 2.0  # 88%
        else:  # >= 3
            confidence = base_confidence - 10.0  # 80%

        # AC 数量奖励（最多 +3%）
        ac_bonus = min(ac_size * 0.5, 3.0)
        confidence += ac_bonus

        return min(confidence, 98.0)  # 最高 98%

    # ============================================================
    # 内部方法：Story 类型描述生成
    # ============================================================

    def _generate_story_type_description(self, detected_types: List[str]) -> str:
        """
        生成 Story 类型描述

        Args:
            detected_types: 检测到的 AC 类型列表

        Returns:
            str: Story 类型描述
        """
        type_mapping = {
            "ddl": "DATABASE_DDL",
            "go_code": "GO_CODE_DEVELOPMENT",
            "sit_test": "SIT_TESTING",
            "uat_test": "UAT_TESTING",
            "architecture": "ARCHITECTURE_DESIGN",
            "monitoring": "MONITORING_SETUP",
            "documentation": "DOCUMENTATION_UPDATE",
            "database_feature": "DATABASE_FEATURE",
            "data_evaluation": "DATA_EVALUATION",
            "bugfix_p2": "BUGFIX_P2",
        }

        if len(detected_types) == 0:
            return "UNKNOWN"
        elif len(detected_types) == 1:
            return type_mapping.get(detected_types[0], "MIXED")
        else:
            # 混合类型：HYBRID_TYPE1_AND_TYPE2
            types_str = "_AND_".join([type_mapping.get(t, t.upper()) for t in detected_types[:3]])
            return f"HYBRID_{types_str}"


# ============================================================
# 测试代码
# ============================================================

if __name__ == "__main__":
    # 测试用例：STORY-15-22（TTL 自动清理）
    story_content = """
    TTL 自动清理实现
    - PostgreSQL TTL 特性
    - SIT 测试验证
    """

    ac_list = [
        {"title": "AC-1: TTL 特性实现", "description": "实现 PostgreSQL TTL 自动清理"},
        {"title": "AC-2: SIT 测试", "description": "编写 SIT 测试用例"}
    ]

    generator = ACBasedStrategyGenerator(story_content, ac_list)
    strategy = generator.generate_strategy()

    print(f"Story 类型: {strategy['story_type']}")
    print(f"检测到的 AC 类型: {strategy['detected_ac_types']}")
    print(f"置信度: {strategy['confidence']}%")
    print(f"执行的检查项: {len(strategy['final_checks'])} 个")
    print(f"跳过的检查项: {len(strategy['negative_checks'])} 个")
    print(f"说明: {strategy['reasoning']}")

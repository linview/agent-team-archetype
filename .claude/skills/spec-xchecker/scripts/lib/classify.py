#!/usr/bin/env python3
"""
文件分类工具

功能:
- 分类变更文件类型（Code/Doc/Test）
- 支持 Go/Python 文件
"""

import re
from pathlib import Path
from typing import List, Dict
from enum import Enum


class FileType(Enum):
    """文件类型枚举"""
    CODE = "code"
    DOC = "doc"
    TEST = "test"
    CONFIG = "config"
    UNKNOWN = "unknown"


def classify_files(files: List[Path]) -> Dict[FileType, List[Path]]:
    """
    分类文件

    Args:
        files: 文件列表

    Returns:
        分类结果字典 {FileType: [文件列表]}
    """
    result = {
        FileType.CODE: [],
        FileType.DOC: [],
        FileType.TEST: [],
        FileType.CONFIG: [],
        FileType.UNKNOWN: [],
    }

    for file in files:
        file_type = _classify_single_file(file)
        result[file_type].append(file)

    return result


def _classify_single_file(file: Path) -> FileType:
    """
    分类单个文件

    Args:
        file: 文件路径

    Returns:
        文件类型
    """
    # 检查文件扩展名
    ext = file.suffix.lower()

    # 测试文件
    if _is_test_file(file):
        return FileType.TEST

    # 文档文件
    if _is_doc_file(file):
        return FileType.DOC

    # 配置文件
    if _is_config_file(file):
        return FileType.CONFIG

    # 代码文件
    if _is_code_file(file):
        return FileType.CODE

    return FileType.UNKNOWN


def _is_test_file(file: Path) -> bool:
    """判断是否为测试文件"""
    # 检查文件路径
    path_str = str(file)
    if '/tests/' in path_str or '\\tests\\' in path_str:
        return True

    # 检查文件名
    if file.name.startswith('test_') or file.name.endswith('_test.py'):
        return True

    # 检查扩展名
    if file.suffix in ['.py']:
        # 检查内容中是否包含测试关键字
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            if re.search(r'(unittest|pytest|test_\w+)', content):
                return True
        except Exception:
            pass

    return False


def _is_doc_file(file: Path) -> bool:
    """判断是否为文档文件"""
    doc_extensions = {
        '.md', '.txt', '.rst',
        '.pdf', '.doc', '.docx',
        '.wiki',
    }

    return file.suffix.lower() in doc_extensions


def _is_config_file(file: Path) -> bool:
    """判断是否为配置文件"""
    config_extensions = {
        '.yaml', '.yml', '.json', '.toml',
        '.ini', '.cfg', '.conf',
        '.xml', '.sh', '.bash',
    }

    # 检查常见配置文件名
    config_filenames = {
        'dockerfile', 'makefile', 'gitignore',
        'docker-compose.yml', 'docker-compose.yaml',
    }

    return (
        file.suffix.lower() in config_extensions or
        file.name.lower() in config_filenames
    )


def _is_code_file(file: Path) -> bool:
    """判断是否为代码文件"""
    code_extensions = {
        '.go', '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
        '.cs', '.php', '.rb', '.swift', '.kt', '.rs',
    }

    return file.suffix.lower() in code_extensions


# CLI 测试接口
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python classify.py <file1> [file2] ...")
        sys.exit(1)

    files = [Path(f) for f in sys.argv[1:]]
    result = classify_files(files)

    print("文件分类结果:")
    print(f"  代码文件 ({FileType.CODE.value}): {len(result[FileType.CODE])} 个")
    print(f"  文档文件 ({FileType.DOC.value}): {len(result[FileType.DOC])} 个")
    print(f"  测试文件 ({FileType.TEST.value}): {len(result[FileType.TEST])} 个")
    print(f"  配置文件 ({FileType.CONFIG.value}): {len(result[FileType.CONFIG])} 个")
    print(f"  未知文件 ({FileType.UNKNOWN.value}): {len(result[FileType.UNKNOWN])} 个")
    print()

    # 打印详细列表
    for file_type, files in result.items():
        if files:
            print(f"{file_type.value.upper()} 文件:")
            for file in files:
                print(f"  - {file}")
            print()

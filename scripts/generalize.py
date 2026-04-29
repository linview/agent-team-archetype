#!/usr/bin/env python3
"""
通用化处理脚本
批量替换项目特定内容为通用占位符
"""

import os
import re
from pathlib import Path

def replace_in_file(file_path, replacements):
    """在文件中执行批量替换"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    # 定义替换规则
    replacements = {
        '{PROJECT_NAME}': '{PROJECT_NAME}',
        '{PROJECT_NAME}': '{PROJECT_NAME}',
        '{BUSINESS_DOMAIN}': '{BUSINESS_DOMAIN}',
        '{BUSINESS_DESCRIPTION}': '{BUSINESS_DESCRIPTION}',
        '{BUSINESS_SHORT}': '{BUSINESS_SHORT}',
    }

    # 支持的文件类型
    extensions = ['.md', '.yml', '.yaml', '.toml', '.go', '.sh', '.py']

    # 查找所有文件
    root_dir = Path('.')
    files_processed = 0
    files_modified = 0

    for ext in extensions:
        for file_path in root_dir.rglob(f'*{ext}'):
            files_processed += 1
            if replace_in_file(file_path, replacements):
                files_modified += 1
                print(f"✓ Modified: {file_path}")

    print(f"\n📊 处理完成:")
    print(f"  - 扫描文件: {files_processed}")
    print(f"  - 修改文件: {files_modified}")

if __name__ == '__main__':
    main()

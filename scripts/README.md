# scripts 目录说明

## 目录用途

**scripts** 目录用于存放工程化工具、构建脚本、临时性工具和便利功能。

**原型工程说明**：此目录只保留框架脚本，不包含具体的构建实现。

---

## 📂 目录用途

### 1. 构建脚本

**用途**: 自动化构建流程

**示例**:
- `build.sh` - 编译和打包应用
- `test.sh` - 运行测试套件
- `deploy.sh` - 部署到环境

**原型工程**: 只保留脚本框架，使用占位符

---

### 2. 临时性工具

**用途**: 一次性使用的工具脚本

**示例**:
- 数据迁移脚本
- 数据修复脚本
- 批量处理脚本

**特点**:
- 完成任务后可删除
- 不纳入版本管理的核心代码
- 记录在 test_reports/ 或 docs/research/

---

### 3. 执行工具

**用途**: 日常开发中频繁使用的工具

**示例**:
- 代码格式化工具
- 静态分析工具
- 依赖管理工具

**特点**:
- 可执行文件
- 命令行接口
- 提供帮助文档

---

### 4. 便利功能

**用途**: 提升开发效率的辅助工具

**示例**:
- 快速启动本地环境
- 快速生成代码模板
- 快速查看日志

**特点**:
- 简化常见操作
- 减少重复劳动
- 提高开发体验

---

## 🎯 脚本编写规范

### Shebang 声明

**必须包含**：可执行文件必须包含 shebang 声明

```bash
#!/bin/bash
#!/usr/bin/env python3
#!/usr/bin/env bash
```

### 错误处理

**必须包含**：脚本必须包含错误处理

```bash
set -euo pipefail  # 遇到错误立即退出

# 或者
trap 'echo "Error on line $LINENO"; exit 1' ERR
```

### 参数验证

**必须包含**：验证必需参数

```bash
if [ $# -lt 1 ]; then
    echo "Usage: $0 <arg1> [arg2]" >&2
    exit 1
fi
```

### 帮助文档

**必须包含**：提供使用说明

```bash
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Verbose output"
    echo ""
    echo "Example:"
    echo "  $0 --env dev"
}
```

---

## 📝 示例脚本框架

### 1. 构建脚本

```bash
#!/bin/bash
set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# 主函数
main() {
    log_info "开始构建..."
    
    # 编译
    log_info "编译 Go 代码..."
    go build -o bin/app ./...
    
    # 运行测试
    log_info "运行测试..."
    go test ./...
    
    log_info "构建完成！"
}

main "$@"
```

### 2. 部署脚本

```bash
#!/bin/bash
set -euo pipefail

# 环境变量
ENVIRONMENT="${1:-dev}"
PROJECT_NAME="{PROJECT_NAME}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# 验证环境
if [[ ! "$ENVIRONMENT" =~ ^(dev|test|prod)$ ]]; then
    echo "Error: ENVIRONMENT must be 'dev', 'test', or 'prod'"
    exit 1
fi

# 部署
echo "Deploying to $ENVIRONMENT..."
docker compose -f deploy/docker-compose.yaml up -d
```

### 3. 数据迁移脚本

```bash
#!/bin/bash
set -euo pipefail

# 数据库连接
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-mydb}"
DB_USER="${DB_USER:-postgres}"

# 执行迁移
echo "Running migration on $DB_HOST:$DB_PORT/$DB_NAME..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f scripts/migration.sql
```

---

## 🚀 使用方法

### 1. 创建新脚本

```bash
# 在 scripts/ 目录下创建脚本
cat > scripts/my_tool.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# 脚本内容
echo "Hello from my_tool.sh"

---

## 🛠️ 现有工具

### generalize.py

**用途**: 批量通用化处理脚本

**功能**: 将项目特定内容替换为通用占位符

**使用方法**:
```bash
# 显示帮助
python3 scripts/generalize.py --help

# 执行通用化
python3 scripts/generalize.py --path . --dry-run
python3 scripts/generalize.py --path . --execute
```

**支持的替换类型**:
- 项目名称 → `{PROJECT_NAME}`
- 数据库名称 → `{DB_NAME}`
- 服务端口 → `{SERVER_PORT}`
- 其他项目特定内容 → 通用占位符

**注意**: 此脚本用于原型工程改造，实际项目中可能不需要。

---

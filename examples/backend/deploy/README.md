# 部署文档

## 原型工程说明

此目录包含 **AI-native Project** 的部署配置模板，用于展示容器化部署的最佳实践。

**注意**：这是一个原型工程，只保留模板文件，不包含实际的部署配置。

---

## 📂 目录结构

```
deploy/
├── README.md                      # 部署说明（本文件）
├── templates/                     # 部署模板目录
│   ├── README.md                  # 模板使用说明
│   ├── Dockerfile.template        # Dockerfile 模板
│   └── docker-compose.yaml.template  # docker-compose 模板
└── k8s/
    └── helm/
        └── project-template/      # Helm Chart 模板
            └── .gitkeep           # 空目录占位符
```

---

## 🎯 部署模板说明

### 1. Dockerfile.template

**用途**: 定义 Docker 镜像构建过程

**特点**:
- 多阶段构建（分离构建和运行环境）
- 使用非 root 用户（提高安全性）
- 健康检查（监控服务状态）
- 使用占位符（易于适配到不同项目）

**使用方法**:
```bash
# 复制模板
cp deploy/templates/Dockerfile.template deploy/Dockerfile

# 替换占位符
sed -i 's/{BINARY_NAME}/my-app/g' deploy/Dockerfile
sed -i 's/{EXPOSE_PORT}/8080/g' deploy/Dockerfile

# 构建镜像
docker build -f deploy/Dockerfile -t my-app:latest .
```

---

### 2. docker-compose.yaml.template

**用途**: 定义本地集成测试环境

**特点**:
- 包含 PostgreSQL 数据库
- 包含 Redis 缓存（可选）
- 包含应用服务
- 服务依赖和健康检查
- 使用占位符（易于适配到不同项目）

**使用方法**:
```bash
# 复制模板
cp deploy/templates/docker-compose.yaml.template deploy/docker-compose.yaml

# 替换占位符
sed -i 's/{PROJECT_NAME}/my-app/g' deploy/docker-compose.yaml
sed -i 's/{SERVER_PORT}/8080/g' deploy/docker-compose.yaml

# 启动环境
docker compose -f deploy/docker-compose.yaml up -d
```

---

## 🚀 快速开始

### 步骤 1: 复制模板

```bash
cp deploy/templates/Dockerfile.template deploy/Dockerfile
cp deploy/templates/docker-compose.yaml.template deploy/docker-compose.yaml
```

### 步骤 2: 替换占位符

**方法 1: 使用 sed（批量替换）**
```bash
PROJECT_NAME="my-app"
BINARY_NAME="my-app"
SERVER_PORT="8080"

sed -i "s/{PROJECT_NAME}/$PROJECT_NAME/g" deploy/Dockerfile deploy/docker-compose.yaml
sed -i "s/{BINARY_NAME}/$BINARY_NAME/g" deploy/Dockerfile deploy/docker-compose.yaml
sed -i "s/{SERVER_PORT}/$SERVER_PORT/g" deploy/Dockerfile deploy/docker-compose.yaml
```

**方法 2: 使用 envsubst**
```bash
export PROJECT_NAME="my-app"
export BINARY_NAME="my-app"
export SERVER_PORT="8080"

envsubst < deploy/templates/Dockerfile.template > deploy/Dockerfile
envsubst < deploy/templates/docker-compose.yaml.template > deploy/docker-compose.yaml
```

### 步骤 3: 构建和运行

```bash
# 构建镜像
docker compose -f deploy/docker-compose.yaml build

# 启动服务
docker compose -f deploy/docker-compose.yaml up -d

# 查看日志
docker compose -f deploy/docker-compose.yaml logs -f

# 停止服务
docker compose -f deploy/docker-compose.yaml down
```

---

## 📖 占位符说明

### Dockerfile 占位符

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{BASE_IMAGE}` | 基础镜像 | `golang:1.24-alpine` |
| `{RUNTIME_IMAGE}` | 运行时镜像 | `alpine:3.21` |
| `{BINARY_NAME}` | 二进制文件名 | `my-app` |
| `{EXPOSE_PORT}` | 暴露端口 | `8080` |

### docker-compose 占位符

| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{PROJECT_NAME}` | 项目名称 | `my-app` |
| `{DB_NAME}` | 数据库名 | `mydb` |
| `{SERVER_PORT}` | 服务端口 | `8080` |
| `{API_PORT_EXTERNAL}` | API 外部端口 | `8080` |

**完整占位符列表**: 请参考 `deploy/templates/README.md`

---

## ⚠️ 注意事项

### 原型工程限制

- ❌ 不包含实际的部署配置
- ❌ 不包含具体的环境变量值
- ❌ 不能直接运行（需要替换占位符）
- ✅ 只展示部署配置模板
- ✅ 展示容器化部署最佳实践
- ✅ 展示本地集成测试环境搭建

### 适配到新项目

1. 复制模板文件到项目根目录
2. 根据项目实际情况替换占位符
3. 调整配置参数（端口、环境变量等）
4. 添加必要的初始化脚本
5. 测试构建和运行

---

## 🔗 相关资源

- **模板详细说明**: `deploy/templates/README.md`
- **Docker 官方文档**: https://docs.docker.com/
- **Docker Compose 文档**: https://docs.docker.com/compose/
- **最佳实践**: https://docs.docker.com/develop/dev-best-practices/

---

**版本**: v1.0
**更新日期**: 2026-04-28
**维护者**: DevOps Team

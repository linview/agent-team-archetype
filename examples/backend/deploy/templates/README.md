# 部署模板说明

## 模板文件说明

此目录包含 **AI-native Project** 的部署配置模板，用于展示容器化部署的最佳实践。

**注意**：这是一个原型工程，模板文件使用占位符，需要根据实际项目进行调整。

---

## 📁 模板文件

### 1. Dockerfile.template

**用途**: 定义 Docker 镜像构建过程

**占位符说明**:
- `{BASE_IMAGE}`: 基础镜像（如 `golang:1.24-alpine`）
- `{RUNTIME_IMAGE}`: 运行时镜像（如 `alpine:3.21`）
- `{DEPENDENCY_FILES}`: 依赖文件列表（如 `go.mod go.sum`）
- `{DOWNLOAD_COMMAND}`: 下载依赖命令（如 `go mod download`）
- `{BUILD_COMMAND}`: 构建命令（如 `CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o app .`）
- `{BINARY_NAME}`: 二进制文件名（如 `example-service`）
- `{CONFIG_FILES}`: 配置文件列表（如 `etc/config/*.yaml`）
- `{EXPOSE_PORT}`: 暴露端口（如 `8080`）
- `{HEALTHCHECK_COMMAND}`: 健康检查命令（如 `wget --no-verbose --tries=1 --spider http://localhost:8080/healthz || exit 1`）

**使用示例**:
```bash
# 复制模板
cp deploy/templates/Dockerfile.template deploy/Dockerfile

# 替换占位符
sed -i 's/{BASE_IMAGE}/golang:1.24-alpine/g' deploy/Dockerfile
sed -i 's/{BINARY_NAME}/my-app/g' deploy/Dockerfile
sed -i 's/{EXPOSE_PORT}/8080/g' deploy/Dockerfile

# 构建镜像
docker build -f deploy/Dockerfile -t my-app:latest .
```

---

### 2. docker-compose.yaml.template

**用途**: 定义本地集成测试环境

**占位符说明**:
- `{PROJECT_NAME}`: 项目名称（如 `example-service`）
- `{POSTGRES_IMAGE}`: PostgreSQL 镜像（如 `postgres:14-alpine`）
- `{DB_NAME}`: 数据库名（如 `event_db`）
- `{DB_USER}`: 数据库用户（如 `postgres`）
- `{DB_PASSWORD}`: 数据库密码（如 `postgres`）
- `{DB_PORT_EXTERNAL}`: 数据库外部端口（如 `5433`）
- `{REDIS_IMAGE}`: Redis 镜像（如 `redis:7-alpine`）
- `{REDIS_PORT_EXTERNAL}`: Redis 外部端口（如 `6380`）
- `{PROJECT_ROOT}`: 项目根目录（如 `../..`）
- `{DOCKERFILE_PATH}`: Dockerfile 路径（如 `deploy/Dockerfile`）
- `{IMAGE_NAME}`: 镜像名称（如 `my-app`）
- `{IMAGE_TAG}`: 镜像标签（如 `latest`）
- `{SERVER_PORT}`: 服务端口（如 `8080`）
- `{API_PORT_EXTERNAL}`: API 外部端口（如 `8080`）
- `{LOG_LEVEL}`: 日志级别（如 `info`）
- `{DB_INIT_PATH}`: 数据库初始化脚本路径（如 `../../scripts/database/init`）

**使用示例**:
```bash
# 复制模板
cp deploy/templates/docker-compose.yaml.template deploy/docker-compose.yaml

# 替换占位符
sed -i 's/{PROJECT_NAME}/my-app/g' deploy/docker-compose.yaml
sed -i 's/{DB_NAME}/mydb/g' deploy/docker-compose.yaml
sed -i 's/{SERVER_PORT}/8080/g' deploy/docker-compose.yaml

# 启动环境
docker compose -f deploy/docker-compose.yaml up -d
```

---

## 🚀 快速开始

### 1. 复制模板到项目

```bash
# 复制 Dockerfile 模板
cp deploy/templates/Dockerfile.template deploy/Dockerfile

# 复制 docker-compose 模板
cp deploy/templates/docker-compose.yaml.template deploy/docker-compose.yaml
```

### 2. 替换占位符

**方法 1: 使用 sed（批量替换）**
```bash
# 定义变量
PROJECT_NAME="my-app"
BASE_IMAGE="golang:1.24-alpine"
BINARY_NAME="my-app"
SERVER_PORT="8080"

# 替换占位符
sed -i "s/{PROJECT_NAME}/$PROJECT_NAME/g" deploy/Dockerfile deploy/docker-compose.yaml
sed -i "s/{BASE_IMAGE}/$BASE_IMAGE/g" deploy/Dockerfile
sed -i "s/{BINARY_NAME}/$BINARY_NAME/g" deploy/Dockerfile deploy/docker-compose.yaml
sed -i "s/{SERVER_PORT}/$SERVER_PORT/g" deploy/Dockerfile deploy/docker-compose.yaml
```

**方法 2: 使用 envsubst（环境变量替换）**
```bash
# 导出环境变量
export PROJECT_NAME="my-app"
export BASE_IMAGE="golang:1.24-alpine"
export BINARY_NAME="my-app"
export SERVER_PORT="8080"

# 替换占位符
envsubst < deploy/templates/Dockerfile.template > deploy/Dockerfile
envsubst < deploy/templates/docker-compose.yaml.template > deploy/docker-compose.yaml
```

**方法 3: 手动编辑**
```bash
# 使用编辑器手动替换
vim deploy/Dockerfile
vim deploy/docker-compose.yaml
```

### 3. 构建和运行

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

## 🎯 最佳实践

### Dockerfile 优化

1. **多阶段构建**
   - 分离构建和运行环境
   - 减小最终镜像大小

2. **使用非 root 用户**
   - 提高安全性
   - 遵循最小权限原则

3. **健康检查**
   - 监控服务状态
   - 自动重启失败容器

### docker-compose.yaml 优化

1. **服务依赖**
   - 使用 `depends_on` 和健康检查
   - 确保服务启动顺序

2. **数据持久化**
   - 使用 volumes 持久化数据
   - 避免数据丢失

3. **网络隔离**
   - 使用自定义网络
   - 服务间通过服务名通信

---

## 📊 常见配置

### Go 应用示例

**Dockerfile**:
```dockerfile
FROM golang:1.24-alpine AS builder
RUN apk add --no-cache git make
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o my-app .

FROM alpine:3.21
RUN apk --no-cache add ca-certificates
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser
WORKDIR /app
COPY --from=builder /build/my-app .
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/healthz || exit 1
CMD ["./my-app"]
```

**docker-compose.yaml**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    image: my-app:latest
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_NAME: mydb
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
```

---

## 🔗 相关资源

- **Docker 官方文档**: https://docs.docker.com/
- **Docker Compose 文档**: https://docs.docker.com/compose/
- **最佳实践**: https://docs.docker.com/develop/dev-best-practices/

---

**版本**: v1.0
**更新日期**: 2026-04-28
**维护者**: DevOps Team

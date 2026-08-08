.PHONY: all test fmt lint tools build build-linux build-win build-mac docker publish-docker run clean help

# 变量定义
PROJECT_NAME := example-service
BINARY_NAME := $(PROJECT_NAME)_api
VERSION := V0.1
DOCKER_REGISTRY := registry.example.com
DOCKER_IMAGE := $(DOCKER_REGISTRY)/example-org/$(PROJECT_NAME)

# 目录定义
BUILD_DIR := build
LOG_DIR := log

# Go 变量
GOCMD := go
GOBUILD := $(GOCMD) build
GOTEST := $(GOCMD) test
GOFMT := gofmt
GOLINT := golangci-lint

# 默认目标
all: test build

# 测试
test:
	@echo "Running tests..."
	$(GOTEST) -v --cover ./internal/...

# 格式化代码
fmt:
	@echo "Formatting code..."
	$(GOFMT) -s -w .

# Lint 检查
lint:
	@echo "Running linter..."
	$(GOLINT) run --exclude-dir=pb --exclude=staticcheck ./...

# 安装工具
tools:
	@echo "Installing tools..."
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install github.com/zeromicro/go-zero/tools/goctl@latest

# API 代码生成(需先准备 .api 定义文件,例如 ./desc/example-service-v1.0.api)
# gen-api:
#	@echo "Generating API code..."
#	goctl api go --api ./desc/example-service-v1.0.api --dir ./ --style=go_zero

# 构建 Linux 二进制
build-linux:
	@echo "Building Linux binary..."
	@mkdir -p $(BUILD_DIR)
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 $(GOBUILD) -ldflags="-s -w" -o $(BUILD_DIR)/$(BINARY_NAME) .

# 构建 Windows 二进制
build-win:
	@echo "Building Windows binary..."
	@mkdir -p $(BUILD_DIR)
	CGO_ENABLED=0 GOOS=windows GOARCH=amd64 $(GOBUILD) -ldflags="-s -w" -o $(BUILD_DIR)/$(BINARY_NAME).exe .

# 构建 macOS 二进制
build-mac:
	@echo "Building macOS binary..."
	@mkdir -p $(BUILD_DIR)
	CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 $(GOBUILD) -ldflags="-s -w" -o $(BUILD_DIR)/$(BINARY_NAME)_mac .

# 构建（默认）
build: build-linux

# Docker 镜像构建
docker:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE):$(VERSION)-$(GIT_COMMIT) -f deploy/docker/Dockerfile.dev .

# 发布 Docker 镜像
publish-docker: docker
	@echo "Publishing Docker image..."
	docker push $(DOCKER_IMAGE):$(VERSION)-$(GIT_COMMIT)

# 运行服务
run:
	@echo "Running service..."
	@mkdir -p $(LOG_DIR)
	$(GOCMD) run main.go -f etc/config/config.yaml

# 清理
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	@echo "Build artifacts cleaned successfully"

# 帮助
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@echo "  all              - Run tests and build (default)"
	@echo "  test             - Run tests"
	@echo "  fmt              - Format code"
	@echo "  lint             - Run linter"
	@echo "  tools            - Install development tools"
	@echo "  gen-api          - Generate API code"
	@echo "  build-linux      - Build Linux binary"
	@echo "  build-win        - Build Windows binary"
	@echo "  build-mac        - Build macOS binary"
	@echo "  build            - Build binary (default: Linux)"
	@echo "  docker           - Build Docker image"
	@echo "  publish-docker   - Publish Docker image"
	@echo "  run              - Run service"
	@echo "  clean            - Clean build artifacts"
	@echo "  help             - Show this help message"

# Git commit hash
GIT_COMMIT := $(shell git rev-parse --short HEAD)

# 内审检查清单

## 检查项

### 1. 敏感信息检查

检查以下模式是否存在于代码变更中：

- `password.*=` - 密码
- `api[_-]?key.*=` - API 密钥
- `secret.*=` - 密钥
- IP 地址格式

### 2. 测试覆盖检查

- 检查变更中是否包含测试文件（文件名包含 `test` 或 `spec`）
- 如果有源代码变更但没有测试文件变更，发出警告

### 3. 文档更新检查

- 检查是否有源代码变更但没有文档更新
- 如果项目中存在 `README.md`，会提示检查是否需要更新

## 使用方式

### 手动执行检查

```bash
# 执行所有检查
./scripts/audit-checker.sh check-all

# 仅检查敏感信息
./scripts/audit-checker.sh check-sensitive
```

### 作为 Pre-commit Hook

```bash
# 安装 hook
./scripts/audit-checker.sh install-hooks

# 提交时自动执行
git commit -m "your message"
```

### 跳过 Pre-commit 检查

```bash
git commit --no-verify -m "your message"
```

---
name: sentinel
description: |
  线上服务哨兵 - 定期巡检、功能回归测试、数据质量验证和根因分析（RCA）。当用户明确提到"巡检"、"回归测试"、"健康检查"、"线上分析"、"RCA"或需要验证生产环境服务健康时使用。

  **仅在以下场景触发**：
  - 用户明确说"执行巡检"、"运行回归测试"
  - 提到"健康检查"、"服务可用性验证"
  - 需要进行线上数据质量分析
  - 生产环境问题诊断和根因分析
  - 定期监控和预防性检查

  **注意**：如果用户只是说"测试"、"检查"等泛化词汇，不应该触发此技能，除非明确提到巡检、回归或健康检查。
---

# Sentinel - 线上服务哨兵

## 核心职责

Sentinel 是线上服务的守护者，负责：
- 🛡️ **定期巡检** - Smoke/Sanity/Full 三级巡检
- ✅ **功能回归测试** - API 测试和数据质量验证
- 🔍 **健康分析** - 服务可用性和数据完整性检查
- 🎯 **根因分析** - 问题诊断和 RCA（Root Cause Analysis）

## 快速开始

### 一键执行（推荐）

```bash
# 健全性测试生产环境
./.codex/skills/sentinel/scripts/inspect sanity prod

# 冒烟测试测试环境
./.codex/skills/sentinel/scripts/inspect smoke test

# 完整测试生产数据
./.codex/skills/sentinel/scripts/inspect full prod
```

**参数说明**：
- `LEVEL`：巡检级别（smoke / sanity / full）
- `ENV`：环境（dev / test / prod）
- **默认值**：`sanity test`

**中文支持**：
```bash
./.codex/skills/sentinel/scripts/inspect 健全 生产
./.codex/skills/sentinel/scripts/inspect 冒烟 测试环境
./.codex/skills/sentinel/scripts/inspect 完整 生产
```

## 巡检级别

> 回归测试覆盖度：**smoke < sanity < full**

### Smoke（每小时）
- **执行时间**：< 30 秒
- **覆盖范围**：
  - API 健康检查（/healthz）
  - 资源查询（空结果、带条件、分页）
  - 错误场景处理（无效时间范围、无效 Pod 名称）

### Sanity（每天）
- **执行时间**：< 5 分钟
- **覆盖范围**：
  - 所有 Smoke 测试
  - 时区一致性验证
  - 元数据完整性验证
  - 数据质量评分（>= 70%）
  - 索引完整性和数据一致性

### Full（每周）
- **执行时间**：< 10 分钟
- **覆盖范围**：
  - 所有 Sanity 测试
  - 计算准确性验证（误差 < 1%）
  - 多次启停周期验证
  - 维度覆盖率验证

## 巡检报告

**存储位置**：`test_reports/inspection/`

**文件命名**：`inspection_smoke_dev_YYYYMMDD_HHMMSS.md`

**报告格式**：纯 Markdown（易于阅读、分享和版本管理）

**报告内容**：
- 📊 测试结果摘要（总数、通过、失败、错误、跳过、通过率）
- 🔧 环境信息（API URL、数据库连接）
- 📋 测试套件详情
- ❌ 失败测试详情（失败原因和详细错误）
- ✅ 通过测试列表

## 验收标准

### Smoke 巡检
- [ ] 所有 API Smoke Tests 通过
- [ ] API 响应时间 < 2 秒

### Sanity 巡检
- [ ] 数据质量评分 >= 70%
- [ ] 无严重 Bug（时区错误、GPU 负值）
- [ ] 索引完整

### Full 巡检
- [ ] GPU 计算误差 < 1%
- [ ] 维度覆盖率 >= 95%

## 故障排查

### 数据库连接失败
```bash
# 检查环境变量
echo $DB_HOST
echo $DB_PORT

# 手动测试连接
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
```

### API 请求失败
```bash
# 检查 API URL
echo $SERVICE_API_URL

# 手动测试 API
curl $SERVICE_API_URL/healthz
```

## GitLab CI 集成

本技能可以通过 GitLab CI Scheduled Pipeline 定期执行。

**定时任务**：
- **冒烟测试**：每小时（Cron: `0 * * * *`）
- **健全性测试**：每天凌晨 2 点（Cron: `0 2 * * *`）
- **完整测试**：每周日凌晨 2 点（Cron: `0 2 * * 0`）

## 配置管理

### 使用 .env.skill（推荐 ✨）

**配置文件**：项目根目录的 `.env.skill`

**优势**：
- ✅ 最安全：敏感信息与代码分离
- ✅ 已在 `.gitignore` 中，不会被提交到 Git
- ✅ 统一管理：所有环境变量集中存储
- ✅ 项目级配置：所有技能共享

**首次配置**：
```bash
# 在项目根目录创建 .env.skill
cat > .env.skill << 'EOF'
# Sentinel 配置 - 测试环境
export TEST_API_URL="http://<YOUR_TEST_API_HOST>:<PORT>/api/v1"
export TEST_DB_HOST="<YOUR_TEST_DB_HOST>"
export TEST_DB_PORT="32032"
export TEST_DB_NAME="app_db"
export TEST_DB_USER="postgres"
export TEST_DB_PASSWORD="your-password"
export TEST_KUBECONFIG="/path/to/kubeconfig"

# Sentinel 配置 - 生产环境
export PROD_API_URL="http://<YOUR_PROD_API_HOST>:<PORT>/api/v1"
export PROD_DB_HOST="<YOUR_PROD_DB_HOST>"
export PROD_DB_PORT="32032"
export PROD_DB_NAME="app_db"
export PROD_DB_USER="postgres"
export PROD_DB_PASSWORD="your-password"
export PROD_KUBECONFIG="/path/to/kubeconfig"
EOF

# 设置权限（仅当前用户可读写）
chmod 600 .env.skill
```

**验证配置**：
```bash
# 检查环境变量是否正确加载
source .env.skill
echo $TEST_API_URL
echo $TEST_DB_HOST

# 执行巡检
./.codex/skills/sentinel/scripts/inspect sanity test
```

### KUBECONFIG 控制

```bash
# 默认：从 .env.skill 读取
./.codex/skills/sentinel/scripts/inspect sanity test

# 禁用 KUBECONFIG（跳过所有需要 K8s 的测试）
KUBECONFIG="DISABLED" ./.codex/skills/sentinel/scripts/inspect sanity prod

# 自定义 KUBECONFIG 路径
KUBECONFIG="/custom/path/kubeconfig" ./.codex/skills/sentinel/scripts/inspect sanity test
```

### 配置参考

配置模板位于：`.codex/skills/sentinel/config/inspection_config.yaml.template`

如需查看完整的配置结构和说明，请参考模板文件。

## 架构说明

Service Monitor 采用**服务和数据库分离部署**架构：
- **服务部署**：在 prod K8s 集群，通过 NodePort Service 暴露
- **数据库部署**：在 test K8s 集群，测试环境和生产环境共享同一个数据库实例

## 更多资源

### 脚本说明
- `scripts/inspect` - 主执行脚本（简化命令）
- `scripts/run_inspection.sh` - 完整巡检脚本
- `scripts/generate_md_report.py` - Markdown 报告生成器
- `scripts/load_config.sh` - 配置加载脚本（从 .env.skill）

### 配置文件
- `config/inspection_config.yaml.template` - 配置模板（参考文档）
- `.env.skill` - 实际配置文件（项目根目录，需本地创建）

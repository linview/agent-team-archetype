# 问题排查与环境一致性

**版本**: v1.0
**创建日期**: 2026-06-01

## 问题排查方法论（铁律）

### 核心原则：代码优先

"代码是唯一的真实来源"：
1. 遇到问题先阅读代码，理解逻辑
2. 再检查配置，是否符合代码预期
3. 最后修改配置，而不是"试错"

### 三步法

**Step 1：阅读代码，理解逻辑**
```bash
# 理解配置优先级、处理逻辑
vim {source_code_path}
```

**Step 2：检查配置，是否符合预期**
```bash
cat {config_path} | grep -A 5 "{key}"
# 对比代码逻辑，判断配置是否正确
```

**Step 3：修改配置，一次到位**
```bash
vim {config_path}
{compose_command} up -d --build
```

### ❌ 错误做法：试错式修改

```bash
# ❌ 反复修改配置试错
# ✅ 阅读代码 → 理解逻辑 → 一次修改到位
```

---

## 开发与测试环境一致性（铁律）

### 🔴 致命错误案例

在主仓库 master 分支测试 worktree 的代码 → 测试的是旧代码 → CI 失败。

### 强制规则

**规则 1：开发和测试必须在同一环境**
```bash
# ✅ 在 worktree 中开发和测试
cd /path/to/worktree/{worktree_name}
pwd && git branch --show-current
{test_command} && {fmt_command} && {build_command}
```

**规则 2：严禁跨环境测试**

| 环境 | 用途 | 测试范围 |
|------|------|---------|
| **主仓库** | 仅用于 master 分支 | 仅测试 master 代码 |
| **Worktree** | 功能开发 | 测试 feature 代码 |

**规则 3：MR 前强制检查**
```bash
pwd  # 确认在 worktree 中
git branch --show-current  # 确认分支
{test_command} && {fmt_command} && {build_command}
```

**铁律记忆法**：**Where you code = Where you test**（哪里开发 = 哪里测试）

---

## 重构测试标准化流程（铁律）

### 核心原则：基线对比法

1. 先验证环境可用
2. 建立测试基线
3. 执行重构
4. 回归测试对比
5. 判断问题来源（环境 vs 重构）

### 四阶段流程

**阶段 1：重构前准备**
```bash
cd {deploy_path} && {compose_command} up -d --build
{test_runner} tests/ -v --html=test_reports/baseline.html
```

**阶段 2：执行重构**
```bash
git mv old_path new_path
# 更新 import 路径...
git commit -m "refactor: xxx"
```

**阶段 3：回归测试**
```bash
cd {deploy_path} && {compose_command} up -d --build
{test_runner} tests/ -v --html=test_reports/refactor.html
```

**阶段 4：问题诊断**
```bash
if [ 重构后测试失败 ]; then
    if [ 基线测试也失败 ]; then
        echo "环境问题"
    else
        echo "重构问题"
    fi
fi
```

---

## 测试环境规范

### 黄金规则

执行测试前，必须确保测试环境运行的是最新代码。

### 容器化环境

```bash
# ✅ 重新构建并启动
cd {deploy_path}
{compose_command} up -d --build

# ❌ 常见陷阱：只用 restart 不会应用新代码
{compose_command} restart {service_name}
```

### 验证新代码已生效

```bash
# 检查容器内二进制文件时间戳
{exec_command} ls -lh {app_path}/{binary_name}
# 应该显示最近的时间（几分钟内）
```

### 检查清单

- [ ] 基线建立：重构前先运行测试并记录结果
- [ ] 环境验证：确认容器运行最新代码（`--build`）
- [ ] 数据库清理：测试前清理数据库
- [ ] 完整测试：不使用 `--maxfail`，执行所有测试用例
- [ ] 结果对比：基线 vs 重构后，通过率差异 ≤5%
- [ ] 问题归因：明确区分"环境问题"和"重构问题"

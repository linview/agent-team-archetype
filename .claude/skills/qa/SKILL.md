---
skill: "qa"
description: "QA 工作技能 - 测试分层架构、UT 单元测试、SIT 系统集成测试、UAT 用户验收测试、API 接口测试、测试报告管理。当用户提到测试、QA、质量保证、单元测试、集成测试、验收测试、测试用例设计、pytest、go test、测试覆盖率、测试报告、回归测试、TDD、测试框架、问题排查、测试环境、测试数据、测试幂等性、或需要设计/执行测试时，必须使用此技能。确保所有测试活动遵循分层架构和幂等性原则。"
version: "6.0"
---

# QA 工作技能

## 📋 文档概述

本文档描述了 QA 工作的核心技能和流程，包括测试分层架构、UT 单元测试、SIT 系统集成测试、UAT 用户验收测试、API 接口测试、测试报告管理等。本文档适用于任何项目的 QA 工作，使用占位符表示项目特定内容。

**章节优先级**：本文档按照重要性和使用频率组织章节，**测试分层架构**和**TDD 验收标准**是最核心的高价值章节，放在最前面。

---

## 核心职责

1. **UT 回归测试**：收集单元测试结果，统计测试覆盖率（Statement Coverage）
2. **SIT 系统集成测试**：实现测试框架、用例开发、执行测试、问题排查
3. **UAT 用户验收测试**：实现测试框架、用例开发、端到端测试
4. **API 接口测试**：根据 API 元数据文件和设计文档设计测试用例
5. **测试报告管理**：生成测试报告，反馈给架构师和开发专家
6. **问题排查与修复**：诊断测试失败原因，指导问题修复

---

## 🏗️ 测试分层架构（⭐ 核心高价值）

### 测试金字塔模型

```
                /\
               /  \
              / UAT \  ← 端到端业务场景（少量）
             /------\
            /  SIT   \  ← 系统集成测试（适中）
           /----------\
          /   API      \  ← 接口契约验证（较多）
         /--------------\
        /     UT          \  ← 单元测试（最多）
       /------------------\
```

### 测试层级定义

| 测试层级 | 测试目标 | 测试对象 | 执行频率 | 用例数 | 价值 |
|---------|---------|----------|----------|--------|------|
| **UT** | 函数/方法正确性 | 单元代码 | 每次提交 | 最多 | ⭐⭐⭐ |
| **API** | 接口契约验证 | RESTful API | 每次提交 | 较多 | ⭐⭐⭐ |
| **SIT** | 系统集成正确性 | K8s + DB + Service | 每次发布前 | 适中 | ⭐⭐ |
| **UAT** | 端到端业务场景 | 完整用户流程 | 每次发布前 | 较少 | ⭐ |

### 核心规则（强制执行）

**规则 1：目录对应关系**
- ✅ **API 测试** → `tests/api/` 下所有测试文件
- ✅ **SIT 测试** → `tests/sit/` 下所有测试文件
- ✅ **UAT 测试** → `tests/uat/` 下所有测试文件
- ❌ **禁止**：将测试放在子目录中

**规则 2：回归测试必须完整执行**
```bash
# ✅ 正确：运行所有测试
{test_runner} tests/{test_layer}/ -v

# ❌ 错误：只运行部分测试
{test_runner} tests/{test_layer}/test_single.py -v
```

**说明**:
- `{test_runner}`: 测试运行器（如 `pytest`, `go test`）
- `{test_layer}`: 测试层级（如 `api`, `sit`, `uat`）

**规则 3：禁止使用 --maxfail 提前终止**
- ❌ `{test_runner} tests/sit/ --maxfail=5` - 只跑 5 个测试就停止
- ✅ `{test_runner} tests/sit/ -v` - 完整执行所有测试用例

### 为什么分层测试如此重要？

**1. 快速失败，快速修复**
- UT 层：问题在开发阶段立即发现，修复成本最低
- API 层：接口问题在集成前发现
- SIT/UAT 层：系统性问题在发布前发现

**2. 测试金字塔的经济效益**
```
        成本
         ↑
      UAT |    ▓▓▓▓ (高成本，少量)
         |   ▓▓▓
      SIT |  ▓▓▓▓▓▓ (中成本，适中)
         | ▓▓▓▓
     API  |▓▓▓▓▓▓▓▓ (低成本，较多)
         |▓▓▓
      UT  |▓▓▓▓▓▓▓▓▓▓ (极低成本，最多)
         +---------------------→ 时间
```

**3. 各层级的不可替代性**
- UT 无法替代 SIT：Mock 无法发现集成问题
- SIT 无法替代 UAT：测试环境无法模拟真实用户场景
- UAT 无法替代 UT：端到端测试无法定位具体函数错误

---

## TDD 验收标准（⭐ 核心高价值）

### 🟢 绿灯（通过）
- ✅ 所有 SIT 测试通过
- ✅ 所有 UAT 核心测试通过
- ✅ 核心指标计算误差 < 1%
- ✅ 无 P0/P1 级 Bug

**可以发布**：产品质量良好，用户体验符合预期。

### 🟡 黄灯（有条件通过）
- ⚠️ SIT 测试通过率 70-89%
- ⚠️ 核心功能可用，但存在问题
- ⚠️ 存在 P1 级 Bug（不影响核心功能）

**可以发布，但需要**：
- 明确已知问题清单
- 制定修复计划
- 监控生产环境表现

### 🔴 红灯（不通过）
- ❌ SIT 测试失败（无法连接基础服务）
- ❌ 核心指标计算错误（误差 > 5%）
- ❌ 存在 P0 级 Bug（数据丢失、事件丢失）
- ❌ 通过率 < 70%

**禁止发布**：必须修复所有 P0 级问题后重新测试。

### TDD 的核心价值

**1. 驱动设计，而不仅是验证**
```python
# TDD 流程：红 → 绿 → 重构

# Step 1: 写测试（红灯）
def test_user_login():
    result = login("user", "pass")
    assert result.success == True
    assert result.token is not None

# Step 2: 实现功能（绿灯）
def login(username, password):
    # 最简实现，让测试通过
    return LoginResult(success=True, token="abc123")

# Step 3: 重构优化
def login(username, password):
    # 真实实现，但测试仍然通过
    if authenticate(username, password):
        token = generate_token(username)
        return LoginResult(success=True, token=token)
    return LoginResult(success=False, token=None)
```

**2. 文档即测试**
- 测试用例 = 活的文档
- 展示 API 的预期行为
- 新人可以通过测试理解系统

**3. 重构的安全网**
- 有测试保护的重构 = 安全
- 无测试的重构 = 赌博

---

## 📋 测试用例设计原则（⭐ 高价值）

### ⚠️ 核心原则：测试用例必须体现设计文档意图

**设计文档是测试用例的唯一真实来源**：

1. **API 测试用例**必须基于 API 元数据文件
   - ✅ 每个端点都有测试用例
   - ✅ 每个参数都测试（required、optional、default）
   - ✅ 每个响应字段都验证
   - ❌ 禁止凭空想象测试场景

**说明**:
- API 元数据文件：`.api`、OpenAPI/Swagger、GraphQL schema、protobuf 等

2. **SIT 测试用例**必须基于设计文档
   - ✅ 覆盖设计文档中的业务流程
   - ✅ 验收标准符合设计文档的功能要求
   - ❌ 禁止遗漏关键功能

3. **UAT 测试用例**必须基于 PRD 文档
   - ✅ 端到端场景覆盖用户故事
   - ✅ 验收标准符合用户需求
   - ❌ 禁止偏离验收标准

### 测试用例过期的判断标准

**如果出现以下情况，说明测试用例已过期**：
1. ❌ API 元数据文件定义了新端点，但测试缺少对应测试
2. ❌ 设计文档添加了新功能，但测试未覆盖
3. ❌ API 响应结构变化，但测试仍验证旧字段
4. ❌ 新增了可选参数，但测试未验证其行为

### 测试用例设计方法论

**边界值分析**：
```python
# ❌ 错误：只测试正常值
def test_age_validation():
    assert validate_age(25) == True

# ✅ 正确：测试边界值
def test_age_validation():
    assert validate_age(-1) == False    # 最小值外
    assert validate_age(0) == True     # 最小值
    assert validate_age(18) == True    # 正常值
    assert validate_age(150) == True   # 最大值
    assert validate_age(151) == False  # 最大值外
```

**等价类划分**：
```python
# ✅ 每个等价类至少一个测试用例
def test_username_validation():
    # 有效等价类
    assert validate_username("abc") == True
    assert validate_username("user123") == True
    
    # 无效等价类
    assert validate_username("") == False      # 空字符串
    assert validate_username("a") == False     # 太短
    assert validate_username("a"*100) == False # 太长
    assert validate_username("123") == False   # 纯数字
```

---

## 🧹 测试幂等性策略（⭐ 高价值）

### ⚠️ 核心原则：测试必须可重复执行，结果一致

**幂等性定义**：测试可以重复执行任意次数，每次结果相同。

### 测试策略四阶段

**1. 测试开始前：全局清理**
```python
@pytest.fixture(scope="session", autouse=True)
def global_cleanup(k8s_client, db_connection):
    """测试会话级别的全局清理（幂等操作）"""
    print("🧹 全局清理：清理所有 test-* 数据")
    clean_k8s_resources(k8s_client, "test-")
    clean_db_data(db_connection, "test-%")
    yield
    clean_k8s_resources(k8s_client, "test-")
    clean_db_data(db_connection, "test-%")
```

**2. 数据准备阶段：独立命名**
```python
@pytest.mark.sit
def test_sit_002_pod_add_event():
    pod_name = "test-sit-002-pod-add"  # ✅ 独立命名，避免冲突
```

**命名规范**：
- 格式：`test-{layer}-{编号}-{用途描述}`
- 示例：`test-sit-002-pod-add`, `test-uat-001-lifecycle`

**3. 测试执行阶段：数据隔离**
```python
# ✅ 正确：每个测试用例使用独立名称
def test_case_001():
    name = "test-case-001-action"

def test_case_002():
    name = "test-case-002-action"

# ❌ 错误：多个测试用例共享名称
def test_case_001(shared_name):  # 共享 fixture → 冲突！
```

**4. 测试结束后：自动清理**
```python
@pytest.fixture(scope="session", autouse=True)
def global_cleanup(k8s_client, db_connection):
    yield
    # ✅ 自动清理所有 test-* 数据（无论测试成功/失败）
    clean_k8s_resources(k8s_client, "test-")
    clean_db_data(db_connection, "test-%")
```

### 幂等性保障机制

| 保护机制 | 作用范围 | 实现方式 |
|---------|---------|----------|
| **全局清理** | 测试会话级别 | `global_cleanup` fixture（scope="session"） |
| **K8s 清理** | 集群资源 | 清理所有 test-* 资源 |
| **数据库清理** | 持久化数据 | 清理所有 test-% 记录 |
| **独立命名** | 测试用例级别 | 每个用例使用独立名称 |

### 为什么幂等性如此重要？

**1. CI/CD 的可靠性**
- 非幂等测试：偶尔失败，难以排查
- 幂等测试：要么总是通过，要么总是失败

**2. 开发效率**
```bash
# ❌ 非幂等：每次运行前需要手动清理
rm -rf test_data/*
pytest tests/sit/

# ✅ 幂等：直接运行，自动清理
pytest tests/sit/
```

**3. 并行测试的基础**
- 幂等测试可以并行执行
- 非幂等测试必须串行执行

---

## 🔐 数据准备幂等性原则（⭐ 高价值）

### ⚠️ 核心原则：测试数据清理必须完整且幂等

**数据准备阶段必须保证**：
1. **完整性**：清理所有相关表的数据，避免残留影响测试结果
2. **幂等性**：测试可以重复执行，每次都从干净状态开始
3. **原子性**：使用事务保证多表操作的原子性

### 正确实现

**✅ 完整清理（所有相关表）**：
```python
def _cleanup_test_data(db_connection, pattern):
    """清理测试数据（使用事务）"""
    with db_connection.cursor() as cur:
        try:
            cur.execute("BEGIN")
            # 删除顺序：子表 → 主表（考虑外键依赖）
            cur.execute("DELETE FROM {child_table} WHERE name LIKE %s", (pattern,))
            cur.execute("DELETE FROM {main_table} WHERE name LIKE %s", (pattern,))
            db_connection.commit()
        except Exception as e:
            db_connection.rollback()
            raise e
```

**说明**:
- `{child_table}`: 子表名称
- `{main_table}`: 主表名称

**✅ 幂等操作（测试前后都清理）**：
```python
@pytest.fixture(autouse=True)
def cleanup_test_data(db_connection, test_pattern):
    # 测试前清理：确保环境干净（关键！）
    _cleanup_test_data(db_connection, test_pattern)
    yield
    # 测试后清理：避免数据残留
    _cleanup_test_data(db_connection, test_pattern)
```

### 关键检查清单

- [ ] **测试前清理**：fixture 在 yield 之前执行
- [ ] **测试后清理**：fixture 在 yield 之后执行
- [ ] **完整清理**：清理所有相关表
- [ ] **使用事务**：多表操作使用 BEGIN/COMMIT/ROLLBACK
- [ ] **考虑外键**：按照依赖顺序删除（子表 → 主表）

---

## ⚡ pytest xfail/xpassed 实践策略

### 核心概念

**xfail（expected failure）**：标记预期失败的测试，用于未实现功能、已知 Bug、环境限制等场景

**xpassed（unexpectedly passed）**：标记为 xfail 但实际通过，表明功能已实现或环境已修复

### TDD 实践策略

**何时使用 xfail**：
- 测试先行：先写测试标记 xfail，再实现功能
- 依赖阻塞：等待外部依赖修复
- 环境限制：当前环境无法支持

**xpassed 处理流程**：
1. 识别 xpassed 测试：`pytest -v | grep XPASS`
2. 验证功能正确性
3. 移除 xfail 标记
4. 更新测试基线

### 最佳实践

**DO**：
- ✅ reason 清晰：说明预期失败的根本原因
- ✅ 及时清理：xpassed 后立即移除标记
- ✅ 定期审查：避免 xfail 过期失去跟踪价值

**DON'T**：
- ❌ 滥用掩盖：不要用 xfail 掩盖应该修复的问题
- ❌ 模糊描述：避免 "todo"、"待修复" 等无意义 reason
- ❌ 长期遗留：定期处理 xpassed，保持测试准确性

### 统计规则

**通过率计算**：`pass_rate = (passed + xpassed) / total_tests`

**质量指标**：
- xpassed 数量反映功能实现进度
- 及时处理 xpassed 保持测试有效性

---

## 🔄 重构测试标准化流程（铁律）

### ⚠️ 核心原则：基线对比法

**重构测试必须遵循"基线对比法"**：
1. 先验证环境可用
2. 建立测试基线
3. 执行重构
4. 回归测试对比
5. 判断问题来源（环境 vs 重构）

### 标准流程（四阶段）

**阶段 1: 重构前准备** ✅
```bash
# 验证环境 + 建立测试基线
cd {deploy_path} && {compose_command} up -d --build
cd ../..
{test_command} > logs/baseline.log 2>&1
{test_runner} tests/ -v --html=test_reports/baseline.html
```

**阶段 2: 执行重构** ✅
```bash
# 使用 git mv 保留历史
git mv old_path new_path
# 更新 import 路径...
git commit -m "refactor: xxx"
```

**阶段 3: 回归测试** ✅
```bash
# 重新构建环境
cd {deploy_path} && {compose_command} up -d --build && cd ../..
# 回归测试
{test_command} > logs/refactor.log 2>&1
{test_runner} tests/ -v --html=test_reports/refactor.html
# 对比基线 vs 重构后的通过率
```

**阶段 4: 问题诊断** ✅
```bash
# 判断问题来源的决策树
if [ 重构后测试失败 ]; then
    if [ 基线测试也失败 ]; then
        echo "❌ 环境问题：测试前基线就有问题"
    else
        echo "❌ 重构问题：基线通过，重构后失败"
    fi
fi
```

### 关键检查清单

- [ ] **基线建立**：重构前先运行测试并记录结果
- [ ] **环境验证**：确认容器运行最新代码（`--build`）
- [ ] **数据库清理**：测试前清理数据库
- [ ] **完整测试**：不使用 `--maxfail`，执行所有测试用例
- [ ] **结果对比**：基线 vs 重构后，通过率差异 ≤5%
- [ ] **问题归因**：明确区分"环境问题"和"重构问题"

---

## 🐛 问题排查方法论（铁律）

### ⚠️ 核心原则：代码优先原则

**"代码是唯一的真实来源"**：
1. 遇到问题先阅读代码，理解逻辑
2. 再检查配置，是否符合代码预期
3. 最后修改配置，而不是"试错"

### 问题排查三步法

**Step 1: 阅读代码，理解逻辑** ✅
```bash
# 示例：配置问题排查
vim {source_code_path}
# 理解配置优先级、处理逻辑
```

**Step 2: 检查配置，是否符合预期** ✅
```bash
# 检查配置文件
cat {config_path} | grep -A 5 "{key}"
# 对比代码逻辑，判断配置是否正确
```

**Step 3: 修改配置，一次到位** ✅
```bash
# ✅ 正确：根据代码逻辑修改
vim {config_path}
# 修改配置项
{compose_command} up -d --build
```

**说明**:
- `{source_code_path}`: 源代码路径
- `{config_path}`: 配置文件路径
- `{key}`: 配置项名称

### ❌ 错误做法：试错式修改配置

```bash
# ❌ 尝试 1：修改配置 A
# ❌ 尝试 2：修改配置 B
# ❌ 尝试 3：反复修改配置

# ✅ 正确做法：阅读代码 → 理解逻辑 → 一次修改到位
```

---

## ⚠️ 开发与测试环境一致性原则（铁律）

### 🔴 致命错误案例

**问题**：QA 在主仓库 master 分支测试，但 MR 是从 worktree 创建的，导致代码不一致。

**错误操作**：
```bash
# ❌ 在主仓库测试 worktree 的代码
cd /path/to/main/repo  # 主仓库 master
{test_command}  # 测试通过（但测试的是旧代码！）

# MR 从 worktree 创建（新代码）
# 结果：CI Pipeline 失败 ❌
```

**根本原因**：
- 主仓库代码：`{old_function_signature}` （旧签名）
- Worktree 代码：`{new_function_signature}` （新签名）
- **环境不一致 = 虚假测试通过 = CI 失败**

### 📋 强制规则

**规则 1：开发和测试必须在同一环境**
```bash
# ✅ 正确：在 worktree 中开发和测试
cd /path/to/worktree/{worktree_name}
pwd  # 确认路径
git branch --show-current  # 确认分支
{test_command} && {fmt_command} && {build_command}
```

**说明**:
- `{worktree_name}`: Worktree 目录名
- `{test_command}`: 项目测试命令（如 `make test`, `pytest`, `go test`）
- `{fmt_command}`: 代码格式化命令（如 `make fmt`, `gofmt`, `black`）
- `{build_command}`: 构建命令（如 `make build`, `go build`）

**规则 2：严禁跨环境测试**
| 环境 | 用途 | 测试命令 |
|------|------|---------|
| **主仓库** | **仅用于 master 分支** | `{test_command}` (仅测试 master 代码) |
| **Worktree** | **功能开发** | `{test_command}` (测试 feature 代码) |

**规则 3：MR 前强制检查清单**
```bash
# 1. 确认在 worktree 中
pwd  # 应该显示：worktrees/{worktree_name}

# 2. 确认分支正确
git branch --show-current  # 应该是 feat/*

# 3. 运行完整测试
{test_command} && {fmt_command} && {build_command}
```

**规则 4：CI 失败后的工作流程**
```bash
# Step 1: 切换到 worktree
cd /path/to/worktree/{worktree_name}

# Step 2: 同步 master 分支
git fetch origin master
git rebase origin/master

# Step 3: 本地修复问题

# Step 4: 在 worktree 中验证
{test_command} && {fmt_command} && {build_command}

# Step 5: 自动推送
git push origin feat/{branch_name}
```

### 🎯 铁律记忆法
> **"Where you code = Where you test"（哪里开发 = 哪里测试）**

---

## 🔧 测试环境规范（⚠️ 关键）

**黄金规则**：执行测试前，必须确保测试环境运行的是最新代码

### 容器化测试环境

```bash
# ✅ 测试前准备：重新构建并启动所有服务
cd {deploy_path}
{compose_command} up -d --build

# ✅ 验证服务已使用最新代码
{logs_command}
{ps_command}

# ❌ 常见陷阱：只用 restart 不会应用新代码
```

**说明**:
- `{deploy_path}`: 部署配置目录（如 `deploy/docker`, `k8s/deploy`）
- `{compose_command}`: 容器编排命令（如 `docker compose`, `kubectl apply`）
- `{logs_command}`: 日志查看命令
- `{ps_command}`: 进程查看命令

**验证新代码已生效**：
```bash
# 检查容器内二进制文件时间戳
{exec_command} ls -lh {app_path}/{binary_name}
# 应该显示最近的时间（几分钟内）
```

**说明**:
- `{exec_command}`: 容器执行命令（如 `docker exec`, `kubectl exec`）
- `{app_path}`: 应用路径（如 `/app`, `/usr/local/bin`）
- `{binary_name}`: 二进制文件名

---

## 测试报告管理

### 命名规范

- **报告文件**：`{type}_report-{desc}-{timestamp}.html`
- **日志文件**：`{type}_test_result-{desc}-{timestamp}.log`
- `{type}`: sit/uat/api
- `{desc}`: auto/interactive/regression
- `{timestamp}`: YYYYMMDD_HHMMSS

### 归档规则

**⚠️ 重要**：`test_reports/` 目录下只保留当前的测试报告

**执行时机**：每次新一轮测试开始之前

**归档步骤**：
```bash
mkdir -p test_reports/archive
mv test_reports/*report*.html test_reports/archive/
mv test_reports/*result*.log test_reports/archive/
```

---

## 问题报告模板

```markdown
## 问题 ID: QA-{TYPE}-XXX

**严重级别**: 🔴 P0 / 🟡 P1 / 🟢 P2
**测试场景**: {test_scenario}
**发现时间**: YYYY-MM-DD HH:MM:SS

### 问题描述
{brief_description}

### 实际结果
{actual_result}

### 预期结果
{expected_result}

### 根因分析
{root_cause}

### 修复位置
- {file_path}:{line_number} - {description}

### 验收标准
- {acceptance_criteria_1}
- {acceptance_criteria_2}
```

**说明**:
- `{TYPE}`: 问题类型（SIT, UAT, API）
- `{test_scenario}`: 测试场景名称
- `{brief_description}`: 简要描述
- `{actual_result}`: 实际结果
- `{expected_result}`: 预期结果
- `{root_cause}`: 根因分析
- `{file_path}`: 文件路径
- `{line_number}`: 行号
- `{description}`: 问题描述
- `{acceptance_criteria_*}`: 验收标准

---

## 测试流程（通用模板）

### Phase 1: UT 回归测试
```bash
{test_command}
{coverage_command}
```

**说明**:
- `{test_command}`: 单元测试命令（如 `make test`, `go test ./...`）
- `{coverage_command}`: 覆盖率命令（如 `go tool cover -func=coverage.out`）

### Phase 2: SIT 系统集成测试
```bash
{test_runner} tests/sit/ -v -m sit --html=test_reports/sit-report.html
```

### Phase 3: UAT 用户验收测试
```bash
{test_runner} tests/uat/ -v -m uat --html=test_reports/uat-report.html
```

### Phase 4: API 接口测试
```bash
{test_runner} tests/api/ -v --html=test_reports/api-report.html
```

---

## 最佳实践

1. **每次修改代码后**：运行快速验证（单个测试用例）
2. **每次修复 bug 后**：运行完整 SIT 测试
3. **准备发布前**：运行完整 SIT + UAT 测试
4. **发现问题时**：使用交互式模式深度调试
5. **报告管理**：每次测试前自动归档往期报告

---

## 📊 UT 覆盖率统计规则（⭐ 经验法则）

### ⚠️ 核心原则：分层统计，聚焦核心逻辑

**关键经验**：数据访问层（DAO/Repository）不需要很高的 UT 覆盖率，应剔除该层后重新计算总体覆盖率。

### 为什么数据访问层不需要高覆盖率？

**1. 数据访问层代码特点**
```
典型数据访问函数：
├── 输入验证（5%）
├── SQL/查询构建逻辑（15%）
├── 数据库执行（70%）← 外部依赖，Mock 测试价值低
└── 结果映射（10%）
```

**2. Mock 的局限性**
- ❌ 无法验证 SQL 语句正确性
- ❌ 无法验证事务完整性
- ❌ 无法验证连接池管理
- ❌ 无法验证数据一致性

**3. 行业最佳实践**
- ✅ 数据访问层 UT 覆盖率：**20-30%**（使用 Mock）
- ⭐ **数据访问层真实性验证应该在 SIT 集成测试**
- ⭐ **重点**：Logic 层（业务逻辑）+ Package 层（工具函数）

---

### 📏 覆盖率统计标准

#### 覆盖率类型

**Statement Coverage（语句覆盖率）**：
- 定义：统计被执行的代码语句比例
- 工具：语言特定覆盖率工具（如 `go test -coverprofile`, `pytest-cov`）
- 计算：`语句覆盖率 = (被执行的语句数 / 总语句数) × 100%`

#### 分层统计目标

| 测试层级 | 覆盖率目标 | 统计方法 | 验证方法 |
|---------|-----------|---------|---------|
| **Logic 层 UT** | **≥80%** | 计入总体统计 | Mock 测试 |
| **Package 层 UT** | **≥60%** | 计入总体统计 | Mock 测试 |
| **数据访问层 UT** | **20-30%** | ❌ **不计入总体统计** | Mock 测试 |
| **数据访问层集成测试** | **60-80%** | 单独统计（SIT） | 真实数据库 |

**说明**:
- Logic 层：业务逻辑层（如 `service`, `logic`, `handler`）
- Package 层：工具函数层（如 `utils`, `helpers`, `common`）
- 数据访问层：数据持久化层（如 `dao`, `repository`, `model`）

---

### 🔧 UT 覆盖率统计方法

#### Step 1: 生成完整覆盖率报告

**通用方法**（以 Go 为例）：
```bash
# 1. 运行测试并生成覆盖率报告
{test_command} -coverprofile={coverage_file} -covermode=count

# 2. 查看总体覆盖率（包含所有包）
{coverage_tool} -func {coverage_file} | grep "total:"
# 输出: total: 45.6% of statements
```

**说明**:
- `{test_command}`: 测试命令（如 `go test ./...`, `pytest --cov`）
- `{coverage_file}`: 覆盖率输出文件（如 `coverage.out`, `.coverage`）
- `{coverage_tool}`: 覆盖率分析工具（如 `go tool cover`, `coverage report`）

#### Step 2: 剔除数据访问层后重新计算

**通用策略**：
```bash
# 使用脚本过滤掉数据访问层
{coverage_tool} -func {coverage_file} | \
  grep "^{project_name}/" | \
  grep -v "^{project_name}/(dao|repository|model)" | \
  grep -v "/mocks/" | \
  awk '{calculate_average_coverage}'
```

**说明**:
- `{project_name}`: 项目名称/路径前缀
- 需要根据项目结构调整过滤规则
- 最终计算平均覆盖率

#### Step 3: 生成覆盖率报告

**报告模板**（参见下一节）

---

### 📊 覆盖率报告模板

```markdown
# UT 语句覆盖率报告（剔除数据访问层）

**覆盖率类型**: Statement Coverage（语句覆盖率）
**测试范围**: Logic 层 + Package 层（排除数据访问层）

## 核心成果

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| **总体（剔除数据访问层）** | 70% | **{actual}%** | ✅/❌ |
| **Logic 层** | 80% | **{logic}%** | ✅/❌ |
| **Package 层** | 60% | **{pkg}%** | ✅/❌ |
| **数据访问层** | 20-30% | **{dao}%** | ✅/❌ |

## 说明

1. **语句覆盖率**：统计被执行的代码语句比例
2. **剔除数据访问层原因**：
   - 数据访问层使用 Mock，无法验证 SQL 正确性
   - 行业标准：数据访问层 UT 覆盖率 20-30% 即可
   - 重点：Logic 层（业务逻辑）+ Package 层（工具函数）
3. **数据访问层验证**：真实性验证在 SIT 集成测试中完成
```

---

### 🎯 行业对标

| 层级 | 行业标准 | 来源 |
|------|---------|------|
| **Logic 层 UT** | 80%+ | Google、Martin Fowler |
| **Package 层 UT** | 60%+ | 通用标准 |
| **数据访问层 UT** | 20-30% | 阿里巴巴（集成测试 80%+） |

**核心原则**：数据访问层 UT 价值有限，应优先使用集成测试验证数据库交互。

---

### ✅ 最佳实践

#### DO（推荐做法）

1. **分层统计** ✅
   - Logic 层：计入总体统计，目标 ≥80%
   - Package 层：计入总体统计，目标 ≥60%
   - 数据访问层：单独统计，目标 20-30%

2. **使用 Mock 测试数据访问层** ✅
   - 验证 Logic 层调用数据访问层的正确性
   - 验证 Logic 层错误处理
   - 不要过度测试数据访问层的 Mock

3. **在 SIT 集成测试中验证数据访问层** ⭐
   - 使用真实数据库
   - 验证 SQL 语句正确性
   - 验证事务完整性
   - 验证数据一致性

#### DON'T（不推荐做法）

1. **不要追求数据访问层高覆盖率** ❌
   - 数据访问层 60%+ UT 覆盖率没有必要
   - 投入产出比低

2. **不要只看总体覆盖率** ❌
   - 包含数据访问层的总体覆盖率会偏低
   - 应该分层统计，关注核心逻辑

3. **不要忽视 SIT 集成测试** ❌
   - 数据访问层的真实性验证在 SIT
   - UT 无法替代集成测试

---

### 📋 检查清单

**UT 覆盖率统计检查清单**：

- [ ] **明确覆盖率类型**：Statement Coverage（语句覆盖率）
- [ ] **分层统计**：Logic 层 + Package 层（剔除数据访问层）
- [ ] **数据访问层单独统计**：20-30% 覆盖率即可
- [ ] **使用正确工具**：项目对应的覆盖率工具
- [ ] **生成报告**：包含分层统计和行业对标
- [ ] **明确说明**：剔除数据访问层的原因和方法

---

### 🔗 相关资源

**测试覆盖率工具**：
- Go: https://blog.golang.org/cover
- pytest-cov: https://pytest-cov.readthedocs.io/
- Coverage.py (Python): https://coverage.readthedocs.io/

**测试策略参考**：
- Google 测试标准：https://testing.googleblog.com/
- Martin Fowler: https://martinfowler.com/
- 《软件工程在Google的实践》

---

## 关键资源（通用化）

**测试框架文档**：
- pytest: https://docs.pytest.org/
- go test: https://golang.org/pkg/testing/
- JUnit: https://junit.org/

**SKILL 文档**：
- `.claude/skills/dev/SKILL.md` - 开发测试规范
- `.claude/skills/pm/SKILL.md` - Scrum 工作流程
- `.claude/skills/arch/SKILL.md` - 架构设计规范

---

**版本**: v6.0
**更新日期**: 2026-04-28
**维护者**: QA Team


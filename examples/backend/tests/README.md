# 测试框架说明

## 原型工程说明

此目录包含 **AI-native Project** 的测试框架示例，展示测试分层和 pytest fixtures 设计。

**注意**：这是一个原型工程，只保留框架代码，不包含具体的测试用例实现。

---

## 📂 目录结构

```
tests/
├── conftest.py                # 主测试框架（全局 fixtures）
├── pytest.ini                 # pytest 配置文件
├── api/                       # API 测试层
│   └── conftest.py            # API 测试 fixtures
├── sit/                       # 系统集成测试层（SIT）
│   └── conftest.py            # SIT 测试 fixtures
├── uat/                       # 用户验收测试层（UAT）
│   └── conftest.py            # UAT 测试 fixtures
└── regression/                # 回归测试层
    └── .gitkeep               # 空目录占位符
```

---

## 🎯 测试分层说明

### 1. API 测试（tests/api/）

**目标**：测试 API 接口的功能和正确性

**特点**：
- 不依赖外部服务（使用 mock）
- 快速执行
- 覆盖各种输入和边界条件

**示例 fixture**：
```python
@pytest.fixture(scope="session")
def api_client():
    """API 客户端"""
    class APIClient:
        def __init__(self):
            self.base_url = "http://localhost:8080"
        
        def get(self, path):
            # 发送 GET 请求
            pass
    
    return APIClient()
```

---

### 2. SIT 测试（tests/sit/）

**目标**：测试系统集成后的整体功能

**特点**：
- 依赖外部服务（数据库、K8s）
- 真实环境测试
- 测试服务间交互

**示例 fixture**：
```python
@pytest.fixture(scope="session")
def k8s_client():
    """K8s 客户端"""
    from kubernetes import client, config
    
    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    return v1

@pytest.fixture(scope="session")
def db_connection():
    """数据库连接"""
    import psycopg2
    
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="test_db",
        user="test_user",
        password="test_password"
    )
    
    yield conn
    
    conn.close()
```

---

### 3. UAT 测试（tests/uat/）

**目标**：从用户角度验证系统功能

**特点**：
- 端到端测试
- 模拟真实用户操作
- 验证业务流程

**示例 fixture**：
```python
@pytest.fixture(scope="session")
def user_session():
    """用户会话"""
    class UserSession:
        def __init__(self):
            self.username = "test_user"
            self.token = None
        
        def login(self):
            # 模拟登录
            self.token = "mock_token"
        
        def logout(self):
            # 模拟登出
            self.token = None
    
    session = UserSession()
    session.login()
    
    yield session
    
    session.logout()
```

---

### 4. 回归测试（tests/regression/）

**目标**：验证历史 bug 不再出现

**特点**：
- 针对已知问题的测试用例
- 持续执行，防止回归
- 可以跨所有测试层级

**示例**：
```python
def test_regression_gpu_usage_negative():
    """验证 GPU 使用率不会出现负值（历史问题）"""
    # 测试代码
    pass
```

---

## 🚀 使用方法

### 运行所有测试

```bash
# 运行所有测试
pytest tests/

# 运行所有测试并生成覆盖率报告
pytest tests/ --cov=internal --cov-report=html
```

### 运行特定层级的测试

```bash
# 只运行 API 测试
pytest tests/api/

# 只运行 SIT 测试
pytest tests/sit/

# 只运行 UAT 测试
pytest tests/uat/

# 只运行回归测试
pytest tests/regression/
```

### 运行特定测试文件

```bash
# 运行单个测试文件
pytest tests/api/test_example.py

# 运行单个测试函数
pytest tests/api/test_example.py::test_function_name

# 运行包含特定标记的测试
pytest tests/ -m "smoke"
```

### 查看测试输出

```bash
# 详细输出
pytest tests/ -v

# 更详细的输出（包含 print）
pytest tests/ -vv -s

# 显示测试耗时
pytest tests/ --durations=10
```

---

## 🔧 pytest 配置

**pytest.ini**：
```ini
[pytest]
minversion = 7.0
addopts = 
    -ra
    -q
    --strict-markers
    --disable-warnings
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    smoke: 冒烟测试
    regression: 回归测试
    slow: 慢速测试
    integration: 集成测试
```

---

## 📝 编写测试用例

### 测试文件命名

- 文件名：`test_<module>.py`
- 类名：`Test<ClassName>`
- 函数名：`test_<function_name>`

### 示例测试用例

```python
# tests/api/test_gpu_usage.py

import pytest

class TestGpuUsageAPI:
    """GPU 使用率 API 测试"""
    
    def test_get_gpu_usage_success(self, api_client):
        """测试成功获取 GPU 使用率"""
        response = api_client.get("/api/gpu/usage")
        
        assert response.status_code == 200
        assert "gpu_usage" in response.json()
    
    def test_get_gpu_usage_invalid_params(self, api_client):
        """测试无效参数"""
        response = api_client.get("/api/gpu/usage?invalid_param=value")
        
        assert response.status_code == 400
```

---

## 🎯 Fixtures 设计原则

### Fixture 作用域

| 作用域 | 说明 | 使用场景 |
|--------|------|---------|
| `function` | 每个测试函数执行一次 | 独立的数据准备 |
| `class` | 每个测试类执行一次 | 类级别的共享资源 |
| `module` | 每个模块执行一次 | 模块级别的共享资源 |
| `session` | 整个测试会话执行一次 | 全局共享资源（如数据库连接） |

### Fixture 最佳实践

1. **使用明确的 fixture 名称**
   ```python
   @pytest.fixture
   def gpu_usage_data():  # ✅ 清晰
       pass
   
   @pytest.fixture
   def data():  # ❌ 不清晰
       pass
   ```

2. **使用 yield 进行清理**
   ```python
   @pytest.fixture
   def db_connection():
       conn = create_connection()
       yield conn
       conn.close()  # 清理资源
   ```

3. **使用 params 参数化**
   ```python
   @pytest.fixture(params=["dev", "test", "prod"])
   def environment(request):
       return request.param
   ```

---

## 📊 测试覆盖率

### 生成覆盖率报告

```bash
# 生成 HTML 报告
pytest tests/ --cov=internal --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 覆盖率目标

| 类型 | 目标覆盖率 |
|------|-----------|
| 核心业务逻辑 | > 90% |
| 一般功能模块 | > 80% |
| 工具函数 | > 70% |

---

## ⚠️ 注意事项

### 原型工程限制

- ❌ 不包含具体的测试用例实现
- ❌ 不包含真实的测试数据
- ❌ 不能直接运行（需要配置环境）
- ✅ 只展示测试框架设计
- ✅ 展示 fixtures 设计模式
- ✅ 展示测试分层结构

### 适配到新项目

1. 根据项目需求修改 `conftest.py` 中的 fixtures
2. 实现具体的测试用例
3. 配置测试环境和数据
4. 调整 `pytest.ini` 配置

---

## 🔗 相关资源

- **pytest 官方文档**: https://docs.pytest.org/
- **pytest-fixtures 文档**: https://docs.pytest.org/en/stable/fixture.html
- **设计文档**: `docs/design/sit_testing_design_v1.0.md`
- **项目文档**: `docs/scrum/story/story-8-04-sit-pytest.md`

---

**版本**: v1.0
**更新日期**: 2026-04-28
**维护者**: Development Team

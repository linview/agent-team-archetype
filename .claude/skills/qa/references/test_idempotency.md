# 测试幂等性策略

**版本**: v1.0
**创建日期**: 2026-06-01

## 核心原则

测试可以重复执行任意次数，每次结果相同。

## 四阶段策略

### 阶段 1：测试开始前 — 全局清理

```python
@pytest.fixture(scope="session", autouse=True)
def global_cleanup(k8s_client, db_connection):
    """测试会话级别的全局清理（幂等操作）"""
    clean_k8s_resources(k8s_client, "test-")
    clean_db_data(db_connection, "test-%")
    yield
    clean_k8s_resources(k8s_client, "test-")
    clean_db_data(db_connection, "test-%")
```

### 阶段 2：数据准备 — 独立命名

```python
# ✅ 独立命名，避免冲突
def test_sit_002_pod_add_event():
    pod_name = "test-sit-002-pod-add"

# ❌ 共享 fixture → 冲突
def test_case_001(shared_name):
```

命名规范：`test-{layer}-{编号}-{用途描述}`

### 阶段 3：测试执行 — 数据隔离

每个测试用例使用独立名称，避免数据交叉。

### 阶段 4：测试结束后 — 自动清理

```python
@pytest.fixture(autouse=True)
def cleanup_test_data(db_connection, test_pattern):
    # 测试前清理：确保环境干净
    _cleanup_test_data(db_connection, test_pattern)
    yield
    # 测试后清理：避免数据残留
    _cleanup_test_data(db_connection, test_pattern)
```

## 数据准备幂等性原则

### 完整清理（所有相关表）

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

### 检查清单

- [ ] 测试前清理：fixture 在 yield 之前执行
- [ ] 测试后清理：fixture 在 yield 之后执行
- [ ] 完整清理：清理所有相关表
- [ ] 使用事务：多表操作使用 BEGIN/COMMIT/ROLLBACK
- [ ] 考虑外键：按照依赖顺序删除（子表 → 主表）

## 保障机制

| 保护机制 | 作用范围 | 实现方式 |
|---------|---------|----------|
| 全局清理 | 测试会话级别 | `global_cleanup` fixture（scope="session"） |
| 独立命名 | 测试用例级别 | 每个用例使用 `test-{layer}-{id}-{desc}` 命名 |
| 数据隔离 | 测试用例级别 | 每个用例使用独立名称 |
| 自动清理 | 测试用例级别 | fixture yield 前后执行清理 |

## 为什么幂等性如此重要

1. **CI/CD 可靠性**：幂等测试要么总是通过，要么总是失败，不会偶发失败
2. **开发效率**：无需手动清理即可重复运行
3. **并行测试基础**：幂等测试可以并行执行

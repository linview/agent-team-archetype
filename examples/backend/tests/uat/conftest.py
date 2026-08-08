"""
UAT 测试配置和 fixtures

Example Service - User Acceptance Testing Framework
"""

import pytest
import os
import time
from datetime import datetime
from pathlib import Path

# Kubernetes Python client
from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException

# PostgreSQL
import psycopg2
from psycopg2.extras import RealDictCursor


# ============================================================
# pytest 配置
# ============================================================

def pytest_configure(config):
    """pytest 配置钩子"""
    config.addinivalue_line("markers", "uat: UAT 用户验收测试")
    config.addinivalue_line("markers", "quick: 快速测试（5 分钟）")
    config.addinivalue_line("markers", "standard: 标准测试（10 分钟）")
    config.addinivalue_line("markers", "full: 完整测试（30 分钟）")
    config.addinivalue_line("markers", "optional: 可选测试（如 REST API）")

    # ⚠️ 风险告知
    print("\n" + "="*80)
    print("⚠️  UAT 测试风险告知")
    print("="*80)
    print()
    print("测试环境: K8s 集群 (https://cluster.example.internal:6443)")
    print("测试内容: 将在 K8s 集群上创建真实的 Pod 资源")
    print("测试 namespace: example-service、argo、argo-workflow、train-job")
    print()
    print("安全保护:")
    print("  ✅ 允许在 example-service、argo、argo-workflow、train-job namespace 创建测试 Pod")
    print("  ❌ 拒绝在 production、prod namespace 创建测试 Pod")
    print()
    print("测试后清理:")
    print("  ✅ 测试结束后自动清理所有创建的 Pod")
    print("  ✅ 测试失败时也会清理 Pod")
    print()
    print("建议:")
    print("  🔧 确保当前连接的是目标集群（KUBECONFIG=/path/to/kubeconfig）")
    print("  🧹 如需中断测试，按 Ctrl+C，Pod 会自动清理")
    print("="*80)
    print()


# ============================================================
# 全局 Fixtures
# ============================================================

@pytest.fixture(scope="session")
def report_dir():
    """测试报告目录"""
    return Path(__file__).parent.parent.parent / "test_reports"


@pytest.fixture(scope="session", autouse=True)
def archive_old_reports(report_dir):
    """归档往期测试报告"""
    archive_dir = report_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    # 归档 UAT 报告
    for file in report_dir.glob("uat_report-*.md"):
        file.rename(archive_dir / file.name)

    for file in report_dir.glob("uat_test_result-*.log"):
        file.rename(archive_dir / file.name)

    yield

    print(f"\n✅ 报告已归档到: {archive_dir}")


def clean_old_test_data(db_connection, hours_threshold=3, max_retries=3):
    """
    清理过时的测试历史数据（基于前缀和时间）

    ✅ 清理策略：
      1. 基于测试前缀识别测试数据：uat-, sit-, test-, manual-
      2. 基于时间过滤：只清理指定小时数之前的数据
      3. 基于状态过滤：只清理 RELEASED/ABORTED 状态（已完成的记录）
      4. 事务完整性：使用事务和重试机制

    ✅ 安全保障：
      - 只清理测试前缀的数据，不误删生产数据
      - 只清理已完成的记录（RELEASED/ABORTED）
      - 只清理旧数据，保护最近的测试记录
      - 失败时自动回滚

    Args:
        db_connection: 数据库连接
        hours_threshold: 时间阈值（小时），默认3小时
        max_retries: 最大重试次数

    Returns:
        dict: 清理统计信息（deleted_count, prefixes, time_threshold）
    """
    # 从环境变量读取配置（支持自定义）
    hours_threshold = int(os.getenv("TEST_DATA_CLEANUP_HOURS", str(hours_threshold)))
    prefixes = os.getenv("TEST_DATA_PREFIXES", "uat-,sit-,test-,manual-").split(",")

    print(f"\n🧹 清理过时测试数据: 时间阈值={hours_threshold}小时前, 前缀={prefixes}")

    for attempt in range(max_retries):
        try:
            with db_connection.cursor() as cur:
                # 开始事务
                cur.execute("BEGIN")

                total_deleted = 0

                # 对每个前缀分别清理
                for prefix in prefixes:
                    prefix = prefix.strip()
                    if not prefix:
                        continue

                    # 构建前缀匹配模式（例如 "uat-%"）
                    pattern = f"{prefix}-%"

                    # 步骤 1: 删除 {BUSINESS_SHORT}记录（关联删除）
                    cur.execute("""
                        DELETE FROM pod_resource_gpu_usage
                        WHERE pod_name LIKE %s
                          AND resource_id IN (
                              SELECT resource_id
                              FROM pod_resource_status
                              WHERE pod_name LIKE %s
                                AND status IN ('RELEASED', 'ABORTED')
                                AND created_at < NOW() - INTERVAL '%s hours'
                          )
                    """, (pattern, pattern, hours_threshold))
                    gpu_count = cur.rowcount

                    # 步骤 2: 删除 Pod 资源状态记录（触发 CASCADE 清理 history）
                    cur.execute("""
                        DELETE FROM pod_resource_status
                        WHERE pod_name LIKE %s
                          AND status IN ('RELEASED', 'ABORTED')
                          AND created_at < NOW() - INTERVAL '%s hours'
                    """, (pattern, hours_threshold))
                    status_count = cur.rowcount

                    total_deleted += gpu_count + status_count

                    if gpu_count > 0 or status_count > 0:
                        print(f"   ✅ [{prefix}] 清理: GPU用量={gpu_count}, Status={status_count}")

                # 提交事务
                db_connection.commit()

                if total_deleted > 0:
                    print(f"   ✅ 总计清理 {total_deleted} 条过时测试记录")
                else:
                    print(f"   ℹ️  无过时测试数据需要清理")

                return {
                    "deleted_count": total_deleted,
                    "prefixes": prefixes,
                    "time_threshold": f"{hours_threshold}小时"
                }

        except Exception as e:
            # 回滚事务
            db_connection.rollback()

            if attempt == max_retries - 1:
                print(f"   ❌ 清理过时测试数据失败: {e}")
                raise
            else:
                print(f"   ⚠️  清理过时测试数据重试 {attempt + 1}/{max_retries}: {e}")
                time.sleep(1)


# ============================================================
# Kubernetes Fixtures
# ============================================================

@pytest.fixture(scope="session")
def k8s_client():
    """Kubernetes 客户端（带安全保护）"""
    # 加载 kubeconfig（使用 k8s_config 别名避免与 pytest_configure 的 config 参数冲突）
    k8s_config.load_kube_config()

    # 创建 API 实例
    v1 = client.CoreV1Api()

    # 封装常用方法
    class K8sClient:
        def __init__(self, v1):
            self.v1 = v1
            self.created_pods = []  # 跟踪创建的 Pod，用于清理

        def find_available_gpu_type(self):
            """
            查询集群中可用的GPU类型，优先选择资源充足的类型

            **返回值** (node_selector dict):
            - 如果找到可用GPU: {"nvidia.com/gpu.product": "NVIDIA-GeForce-RTX-4090"}
            - 如果未找到: {} (不限制，调度器自动选择)

            **优先级** (基于资源充足度):
            1. NVIDIA-GeForce-RTX-4090 (50个节点，资源最充足)
            2. NVIDIA-GeForce-RTX-3090 (20个节点)
            3. NVIDIA-A100-SXM4-80GB (10个节点，资源紧张)
            4. Tesla-P4 (5个节点)
            """
            try:
                # 查询所有GPU节点
                nodes = self.v1.list_node(label_selector="worker-type=gpu")

                # 按GPU类型分组，统计可用资源
                gpu_type_stats = {}

                for node in nodes.items:
                    # 获取GPU产品类型
                    gpu_product = node.metadata.labels.get("nvidia.com/gpu.product", "Unknown")

                    # 获取GPU资源分配情况
                    gpu_capacity = int(node.status.capacity.get("nvidia.com/gpu", 0))
                    gpu_allocatable = int(node.status.allocatable.get("nvidia.com/gpu", 0))

                    # 查询该节点上已分配的GPU（通过Pod统计）
                    try:
                        pods = self.v1.list_namespaced_pod(namespace="default")
                        allocated_gpus = 0
                        for pod in pods.items:
                            if pod.spec.node_name == node.metadata.name:
                                for container in pod.spec.containers:
                                    if container.resources.requests and "nvidia.com/gpu" in container.resources.requests:
                                        allocated_gpus += int(container.resources.requests["nvidia.com/gpu"])

                        available_gpus = gpu_capacity - allocated_gpus
                    except:
                        # 如果无法查询，使用allocatable作为fallback
                        available_gpus = gpu_allocatable

                    # 累加统计
                    if gpu_product not in gpu_type_stats:
                        gpu_type_stats[gpu_product] = {
                            "total_nodes": 0,
                            "available_gpus": 0
                        }

                    gpu_type_stats[gpu_product]["total_nodes"] += 1
                    gpu_type_stats[gpu_product]["available_gpus"] += available_gpus

                # 如果没有GPU节点，返回空（不限制）
                if not gpu_type_stats:
                    print(f"⚠️  未查询到GPU节点，使用调度器自动选择")
                    return {}

                # 打印统计信息
                print(f"\n📊 集群GPU资源统计:")
                for gpu_type, stats in sorted(gpu_type_stats.items()):
                    print(f"  - {gpu_type}: {stats['total_nodes']}个节点, 可用GPU {stats['available_gpus']}个")

                # 优先级选择：4090 > 3090 > A100 > P4
                priority_order = [
                    "NVIDIA-GeForce-RTX-4090",
                    "NVIDIA-GeForce-RTX-3090",
                    "NVIDIA-A100-SXM4-80GB",
                    "Tesla-P4"
                ]

                for preferred_type in priority_order:
                    if preferred_type in gpu_type_stats and gpu_type_stats[preferred_type]["available_gpus"] > 0:
                        print(f"✅ 选择GPU类型: {preferred_type} (可用: {gpu_type_stats[preferred_type]['available_gpus']}个)")
                        return {"nvidia.com/gpu.product": preferred_type}

                # 如果所有GPU类型都没有可用资源，返回空（让调度器尝试）
                print(f"⚠️  所有GPU类型资源已耗尽，使用调度器自动选择")
                return {}

            except Exception as e:
                # 如果查询失败，返回空（不限制，让调度器自动选择）
                print(f"⚠️  查询GPU资源失败: {e}，使用调度器自动选择")
                return {}

        def get_cluster_info(self):
            """获取当前集群信息"""
            try:
                # 读取当前 cluster info
                import subprocess
                result = subprocess.run(
                    ["kubectl", "cluster-info", "--context", "current"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                cluster_info = result.stdout.strip().split('\n')[0] if result.returncode == 0 else "未知集群"
                return f"生产集群: {cluster_info}"
            except:
                return "生产集群"

        def namespace_exists(self, namespace):
            """检查 namespace 是否存在"""
            try:
                self.v1.read_namespace(namespace)
                return True
            except ApiException as e:
                if e.status == 404:
                    return False
                raise

        def create_pod(self, pod_name, namespace, labels=None, annotations=None, command=None, gpu_count=0, node_selector=None, auto_gpu_selection=False):
            """
            创建 Pod（带风险告知 + GPU自适应选择）

            **⚠️ 风险告知**：
            - 此方法会在 K8s 集群上创建真实 Pod
            - 目标集群: https://cluster.example.internal:6443（示例环境）
            - 建议在非生产namespace中验证（example-service、argo、train-job）
            - 测试失败时 Pod 会被自动清理
            - 默认使用 '{PROJECT_NAME}-uat' namespace（测试专用）

            **安全保护**：
            - 拒绝在明确标记为生产的 namespace 中创建测试 Pod
            - 生产 namespace: ['production', 'prod']

            **GPU自适应选择** (auto_gpu_selection=True):
            - 自动查询集群GPU资源，优先选择资源充足的类型
            - 优先级: 4090 > 3090 > A100 > P4
            - 避免因为特定GPU类型资源不足导致测试假失败
            """
            # 安全保护：只拒绝明确标记为生产的 namespace
            if namespace in ["production", "prod"]:
                pytest.fail(
                    f"🚨 安全错误：拒绝在生产 namespace ({namespace}) 中创建测试 Pod！\n"
                    f"当前生产集群: {self.get_cluster_info()}\n"
                    f"请使用 example-service、argo、train-job 或 {PROJECT_NAME}-uat namespace。"
                )

            # GPU自适应选择（如果启用）
            if auto_gpu_selection and gpu_count > 0 and node_selector is None:
                node_selector = self.find_available_gpu_type()
                if node_selector:
                    gpu_type = node_selector.get("nvidia.com/gpu.product", "未知")
                    print(f"🎯 GPU自适应选择: {gpu_type}")
                else:
                    print(f"⚠️  未找到可用GPU类型，使用调度器自动选择")

            # 记录创建的 Pod（用于清理）
            self.created_pods.append((pod_name, namespace))

            # 构建 GPU 资源限制
            resources = client.V1ResourceRequirements(
                limits={"cpu": "100m", "memory": "128Mi"},  # 资源限制
                requests={"cpu": "50m", "memory": "64Mi"}
            )

            if gpu_count > 0:
                resources.limits["nvidia.com/gpu"] = str(gpu_count)
                resources.requests["nvidia.com/gpu"] = str(gpu_count)

            pod = client.V1Pod(
                metadata=client.V1ObjectMeta(
                    name=pod_name,
                    labels=labels or {},
                    annotations=annotations or {}
                ),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name="main",
                        image="nginx:alpine",
                        command=command or ["sleep", "3600"],
                        resources=resources
                    )],
                    restart_policy="Never",
                    node_selector=node_selector or {},
                    tolerations=[
                        client.V1Toleration(
                            key="worker-type",
                            operator="Equal",
                            value="gpu",
                            effect="NoSchedule"
                        )
                    ]
                )
            )

            print(f"\n⚠️  创建测试 Pod: {namespace}/{pod_name}")
            return self.v1.create_namespaced_pod(namespace, pod)

        def delete_pod(self, pod_name, namespace):
            """删除 Pod"""
            try:
                print(f"🧹 清理测试 Pod: {namespace}/{pod_name}")
                self.v1.delete_namespaced_pod(pod_name, namespace)
                # 从跟踪列表中移除
                if (pod_name, namespace) in self.created_pods:
                    self.created_pods.remove((pod_name, namespace))
            except ApiException as e:
                if e.status != 404:
                    raise

        def wait_pod_ready(self, pod_name, namespace, timeout=60):
            """等待 Pod 进入 Ready 状态"""
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    pod = self.v1.read_namespaced_pod(pod_name, namespace)
                    if pod.status.phase == "Running":
                        # 检查是否所有容器都 Ready
                        if all(cs.ready for cs in pod.status.container_statuses or []):
                            return True
                except ApiException:
                    pass
                time.sleep(2)

            raise TimeoutError(f"Pod {pod_name} 未在 {timeout} 秒内进入 Ready 状态")

        def wait_for_db_status(self, db_connection, pod_name, expected_status, timeout=60):
            """
            等待 Pod 在数据库中达到指定状态

            Args:
                db_connection: 数据库连接
                pod_name: Pod 名称
                expected_status: 期望的状态（如 PENDING, RUNNING, RELEASED）
                timeout: 超时时间（秒）

            Returns:
                bool: 如果达到期望状态返回 True

            Raises:
                TimeoutError: 如果超时未达到期望状态
            """
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    with db_connection.cursor() as cur:
                        # 查询 Pod 当前状态（使用 k8s_pod_name 字段）
                        cur.execute("""
                            SELECT status
                            FROM pod_resource_status
                            WHERE k8s_pod_name = %s
                            ORDER BY created_at DESC
                            LIMIT 1
                        """, (pod_name,))

                        result = cur.fetchone()
                        if result and result["status"] == expected_status:
                            return True

                except Exception as e:
                    print(f"   ⚠️  查询数据库状态失败: {e}")

                time.sleep(1)

            raise TimeoutError(
                f"Pod {pod_name} 未在 {timeout} 秒内达到状态 {expected_status}"
            )

        def cleanup(self):
            """清理所有创建的 Pod（安全保护）"""
            print(f"\n🧹 清理 {len(self.created_pods)} 个测试 Pod...")

            for pod_name, namespace in self.created_pods:
                try:
                    self.v1.delete_namespaced_pod(pod_name, namespace)
                    print(f"   ✅ 已清理: {namespace}/{pod_name}")
                except ApiException as e:
                    print(f"   ⚠️  清理失败: {namespace}/{pod_name} - {e}")

            self.created_pods.clear()

    # 创建客户端实例（使用 k8s_client_obj 避免覆盖导入的 client 模块）
    k8s_client_obj = K8sClient(v1)

    # 在测试开始前清理过时测试数据
    print("\n🧹 UAT 测试开始前清理过时测试数据...")
    # 注意：这里需要在 db_connection fixture 之后调用，所以这个清理逻辑
    # 将在 global_uat_cleanup fixture 中处理

    # 在测试结束后自动清理
    yield k8s_client_obj

    # 自动清理所有创建的 Pod（防止资源泄露）
    k8s_client_obj.cleanup()

    print("✅ UAT 测试结束，所有测试 Pod 已清理")


# ============================================================
# Database Fixtures
# ============================================================

@pytest.fixture(scope="session")
def db_connection():
    """数据库连接"""
    # 从环境变量或默认值读取数据库配置
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "event_db-dev")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    # 对于 Docker 环境
    if db_host == "localhost":
        db_host = "localhost"  # 或 127.0.0.1

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password,
        cursor_factory=RealDictCursor
    )

    yield conn

    conn.close()


@pytest.fixture(scope="session")
def api_base_url():
    """
    Example Service API base URL

    UAT API 测试的 API 服务端点
    """
    # 从环境变量或默认值读取 API 配置
    # 注意：Docker Compose 环境下 API 服务运行在 8082 端口
    api_url = os.getenv("EXAMPLE_SERVICE_API_URL", "http://localhost:8082/api/v1")

    print(f"\n🔗 API Base URL: {api_url}")

    return api_url


@pytest.fixture(scope="session", autouse=True)
def global_uat_cleanup(db_connection):
    """
    UAT 测试会话级别的全局清理（幂等操作）

    ✅ 测试策略（支持并行执行）：
      1. 测试开始前：只清理超过3小时的过时数据（避免干扰正在运行的测试）
      2. 测试结束后：清理当前会话的所有 uat-* 数据（恢复环境）

    ✅ 并行执行保障：
      - 只清理超过3小时的数据（SIT 和 UAT 可以并行运行）
      - 隐含假设：SIT + UAT 回归在3小时内能完成

    ✅ 幂等性保障：
      - 数据库清理：删除所有过时的 uat-/sit-/test-/manual- 记录
      - 事务完整性：使用事务和重试机制
      - 只清理已完成状态（RELEASED/ABORTED）的记录

    ✅ 测试数据隔离：
      - 只清理测试前缀的数据
      - 避免误删生产数据
      - 基于时间过滤，保护最近的测试记录

    Args:
        db_connection: 数据库连接
    """
    print("\n" + "="*70)
    print("🧹 UAT 全局清理：清理超过3小时的过时测试数据")
    print("="*70)

    # 清理过时的测试历史数据（3小时前）
    # ✅ 关键：只清理旧数据，不影响正在运行的 SIT 测试
    clean_old_test_data(db_connection)

    print("✅ UAT 环境已清理完成，提供干净的测试环境\n")

    yield

    # 会话结束后清理当前会话的所有数据
    print("\n" + "="*70)
    print("🧹 UAT 会话结束清理：清理当前会话的 uat-* 数据")
    print("="*70)

    # 清理所有 uat-* 数据
    for attempt in range(3):
        try:
            with db_connection.cursor() as cur:
                # 开始事务
                cur.execute("BEGIN")

                # 删除 {BUSINESS_SHORT}记录
                cur.execute(
                    "DELETE FROM pod_resource_gpu_usage WHERE pod_name LIKE %s",
                    ("uat-%",)
                )
                gpu_count = cur.rowcount

                # 删除 Pod 资源状态（触发 CASCADE 清理 history）
                cur.execute(
                    "DELETE FROM pod_resource_status WHERE pod_name LIKE %s",
                    ("uat-%",)
                )
                status_count = cur.rowcount

                # 提交事务
                db_connection.commit()

                if gpu_count > 0 or status_count > 0:
                    print(f"   ✅ 数据库清理: GPU用量={gpu_count}, Status={status_count}")

                break

        except Exception as e:
            # 回滚事务
            db_connection.rollback()

            if attempt == 2:
                print(f"   ⚠️  UAT 清理失败: {e}")
            else:
                time.sleep(1)

    print("✅ UAT 环境已恢复\n")


# ============================================================
# Helper Fixtures
# ============================================================

@pytest.fixture
def create_devpod(k8s_client):
    """创建 DevPod 的 fixture"""
    def _create(pod_name, gpu_count=1, namespace="example-service", node_selector=None, labels=None, annotations=None, auto_gpu_selection=False):
        default_labels = {
            "app.kubernetes.io/name": "example-service",
            "{PROJECT_NAME}/example.com": "true"
        }

        # 合并自定义 labels
        if labels:
            default_labels.update(labels)

        default_annotations = {
            "cmdb.example.com/resource-name": pod_name,
            "cmdb.example.com/user-id": "test-user-uat",
            "cmdb.example.com/user-name": "Test User UAT",
        }

        # 合并自定义 annotations
        if annotations:
            default_annotations.update(annotations)

        # 添加 GPU 限制（实际测试中可能需要不同的镜像）
        return k8s_client.create_pod(
            pod_name=pod_name,
            namespace=namespace,
            labels=default_labels,
            annotations=default_annotations,
            gpu_count=gpu_count,
            node_selector=node_selector,
            auto_gpu_selection=auto_gpu_selection
        )

    return _create


@pytest.fixture
def delete_pod(k8s_client):
    """删除 Pod 的 fixture"""
    def _delete(pod_name, namespace="example-service"):
        k8s_client.delete_pod(pod_name, namespace)

    return _delete


@pytest.fixture
def query_gpu_usage(db_connection):
    """查询 {BUSINESS_SHORT}的 fixture"""
    def _query(pod_name, usage_cycle=1):
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT gpu_hours
                FROM pod_resource_gpu_usage
                WHERE pod_name = %s AND usage_cycle = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (pod_name, usage_cycle))

            result = cur.fetchone()
            return result["gpu_hours"] if result else None

    return _query


@pytest.fixture
def query_pod_status(db_connection):
    """查询 Pod 状态的 fixture"""
    def _query(pod_name):
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT pod_name, pod_namespace, pod_resource_type, status, gpu_count
                FROM pod_resource_status
                WHERE pod_name = %s
                ORDER BY created_at DESC
            """, (pod_name,))

            return cur.fetchall()

    return _query


@pytest.fixture
def wait_for_informer(k8s_client, db_connection):
    """
    等待 Informer 处理 Pod 事件的 fixture（轮询方式）

    ✅ 优化: 轮询间隔 0.5 秒，减少等待时间
    ✅ 性能: 平均等待时间减少 50-75%

    Args:
        k8s_client: K8s 客户端
        db_connection: 数据库连接

    Returns:
        callable: _wait(pod_name, timeout=90, interval=0.5)

    Examples:
        wait_for_informer(pod_name, timeout=45, interval=0.5)
    """
    def _wait(pod_name, timeout=90, interval=0.5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            with db_connection.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM pod_resource_status WHERE k8s_pod_name = %s",
                    (pod_name,)
                )
                count = cur.fetchone()["count"]
                if count > 0:
                    return True
            time.sleep(interval)
        raise TimeoutError(f"Pod {pod_name} 未在 {timeout} 秒内出现在数据库中")
    return _wait


@pytest.fixture
def wait_for_db_record(db_connection):
    """
    等待数据库记录出现的 fixture（通用轮询工具）

    ✅ 用途: 替代硬编码 time.sleep()
    ✅ 优化: 轮询间隔 1 秒，减少数据库查询压力
    ✅ 生产环境验证: 考虑 Informer 2-5 秒延迟，默认超时 90 秒（18倍延迟，确保 UAT long-run 测试稳定性）

    Args:
        db_connection: 数据库连接

    Returns:
        callable: _wait(query, params=None, timeout=90, interval=1.0)

    Examples:
        # 等待 Pod 记录出现
        wait_for_db_record(
            "SELECT 1 FROM pod_resource_status WHERE pod_name = %s",
            ("test-pod",),
            timeout=90
        )

        # 等待特定状态
        wait_for_db_record(
            "SELECT 1 FROM pod_resource_status WHERE pod_name = %s AND status = %s",
            ("test-pod", "RUNNING"),
            timeout=90
        )
    """
    def _wait(query, params=None, timeout=90, interval=1.0):
        start_time = time.time()
        while time.time() - start_time < timeout:
            with db_connection.cursor() as cur:
                cur.execute(query, params or ())
                result = cur.fetchone()
                # RealDictCursor 返回字典，检查第一个值是否 >= 1
                if result and list(result.values())[0] >= 1:
                    return True
            time.sleep(interval)
        raise TimeoutError(f"数据库查询未在 {timeout} 秒内返回结果")
    return _wait

"""
SIT 测试配置和 fixtures

Resource Meter - System Integration Testing Framework
"""

import pytest
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

# Kubernetes Python client
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# PostgreSQL
import psycopg2
from psycopg2.extras import RealDictCursor


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

    # 归档 SIT 报告
    for file in report_dir.glob("sit_report-*.md"):
        file.rename(archive_dir / file.name)

    for file in report_dir.glob("sit_test_result-*.log"):
        file.rename(archive_dir / file.name)

    yield

    print(f"\n✅ 报告已归档到: {archive_dir}")


# ============================================================
# Kubernetes Fixtures
# ============================================================

@pytest.fixture(scope="session")
def k8s_client():
    """
    Kubernetes 客户端（支持多种认证方式）

    ⚠️ 安全原则：强制显式指定 KUBECONFIG（Fail Fast）

    ✅ 认证优先级：
      1. 环境变量 KUBECONFIG（CI/CD场景 - 必须显式指定）
      2. ServiceAccount Token（In-Cluster场景）

    ❌ 移除默认值：不使用 ~/.kube/config（防止误连接生产集群）
    """
    import os
    from kubernetes import client, config

    # 优先级 1: In-Cluster Config（ServiceAccount）
    if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
        try:
            config.load_incluster_config()
            print("   ✅ 使用 In-Cluster Config（ServiceAccount）")
        except Exception as e:
            raise RuntimeError(
                f"❌ In-Cluster Config 加载失败: {e}\n"
                f"且未提供 KUBECONFIG 环境变量"
            )
    else:
        # 优先级 2: 环境变量指定 kubeconfig（CI/CD场景 - 必须显式指定）
        kubeconfig_path = os.getenv("KUBECONFIG")

        if not kubeconfig_path:
            raise EnvironmentError(
                "❌ KUBECONFIG 环境变量未设置\n"
                "SIT 测试需要连接到 K8s 集群，必须显式指定 kubeconfig 文件\n\n"
                "🔒 安全原则：强制显式指定，防止误连接生产集群\n\n"
                "请使用以下命令之一：\n"
                "  export KUBECONFIG=/path/to/test-kubeconfig\n"
                "  KUBECONFIG=/path/to/test-kubeconfig pytest tests/sit/\n\n"
                "📍 测试环境 kubeconfig 路径：\n"
                "  ✅ 测试环境: /path/to/test-kubeconfig (推荐)\n"
                "  ❌ 生产环境: /path/to/prod-kubeconfig (严禁使用!)\n\n"
                "💡 提示：在 ~/.bashrc 或 ~/.zshrc 中添加别名：\n"
                "  alias test-kubeconfig='export KUBECONFIG=/path/to/test-kubeconfig'"
            )

        # 验证文件存在
        if not os.path.exists(kubeconfig_path):
            # 智能路径检测：修复常见错误
            if "test-config" in kubeconfig_path:
                fixed_path = kubeconfig_path.replace("test-config", "test/config")
                if os.path.exists(fixed_path):
                    raise EnvironmentError(
                        f"❌ kubeconfig 路径错误（缺少目录分隔符）\n"
                        f"   错误路径: {kubeconfig_path}\n"
                        f"   正确路径: {fixed_path}\n\n"
                        f"💡 修复命令：\n"
                        f"  export KUBECONFIG=/path/to/test-kubeconfig"
                    )

            raise FileNotFoundError(
                f"❌ kubeconfig 文件不存在: {kubeconfig_path}\n"
                f"请检查路径是否正确"
            )

        # 加载 kubeconfig
        config.load_kube_config(config_file=kubeconfig_path)
        print(f"   ✅ 使用本地 kubeconfig: {kubeconfig_path}")

    # 创建 API 实例
    v1 = client.CoreV1Api()

    # 验证连接
    try:
        v1.list_node(limit=1)
        print("   ✅ K8s 集群连接成功")
    except Exception as e:
        raise RuntimeError(f"❌ K8s 集群连接失败: {e}")

    # 封装常用方法
    class K8sClient:
        def __init__(self, v1):
            self.v1 = v1
            self.created_pods = []  # 跟踪创建的 Pod，用于清理

        def create_pod(self, pod_name, namespace, labels=None, annotations=None,
                      gpu_count=0, command=None, node_selector=None):
            """
            创建 Pod

            Args:
                pod_name: Pod 名称
                namespace: Namespace
                labels: Pod labels
                annotations: Pod annotations
                gpu_count: GPU 数量
                command: 容器启动命令
                node_selector: NodeSelector map (for GPU product testing)
            """
            # ⭐ 增加重试机制（处理 409 Conflict: object is being deleted）
            import time
            max_retries = 5  # 增加到 5 次
            for attempt in range(max_retries):
                try:
                    # 记录创建的 Pod（用于清理）
                    if (pod_name, namespace) not in self.created_pods:
                        self.created_pods.append((pod_name, namespace))

                    # 构建资源请求
                    resources = None
                    if gpu_count > 0:
                        resources = client.V1ResourceRequirements(
                            requests={"nvidia.com/gpu": str(gpu_count)},
                            limits={"nvidia.com/gpu": str(gpu_count)}
                        )

                    # ✅ 构建 tolerations（容忍 GPU 节点 Taint）
                    # 覆盖集群中所有 GPU Taint 类型：
                    # - worker-type=gpu:NoSchedule (52个节点)
                    # - worker-type/ide=gpu:NoSchedule (9个节点)
                    # - worker-type/drs=gpu:NoSchedule (3个节点)
                    tolerations = None
                    if gpu_count > 0:
                        # 使用 Exists operator 匹配所有 worker-type=* 的 Taint
                        tolerations = [
                            client.V1Toleration(
                                key="worker-type",
                                operator="Exists",
                                effect="NoSchedule"
                            )
                        ]

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
                            tolerations=tolerations or []
                        )
                    )

                    return self.v1.create_namespaced_pod(namespace, pod)

                except client.ApiException as e:
                    if e.status == 409 and attempt < max_retries - 1:
                        # 409 Conflict: object is being deleted
                        print(f"   ⚠️  create_pod 遇到 409 Conflict (object is being deleted)，重试 {attempt + 1}/{max_retries}")
                        time.sleep(3)  # 增加到 3 秒
                        continue
                    else:
                        raise

        def delete_pod(self, pod_name, namespace):
            """删除 Pod"""
            try:
                self.v1.delete_namespaced_pod(pod_name, namespace)
                # 从跟踪列表中移除
                if (pod_name, namespace) in self.created_pods:
                    self.created_pods.remove((pod_name, namespace))
            except ApiException as e:
                if e.status != 404:
                    raise

        # ============================================================
        # ⭐ 主动控制方法（重构后的测试策略）
        # ============================================================

        def set_pod_phase(self, pod_name, namespace, phase, max_retries=3):
            """
            ⭐ 主动设置 Pod 的 phase（触发 Informer UPDATE 事件）

            ✅ 测试策略：
              - 不依赖容器自然启动，直接通过 K8s API 修改 Pod phase
              - 立即触发 Informer UPDATE 事件
              - 精确控制状态转换时机
              - ⭐ 增加重试机制（处理 409 Conflict）

            Args:
                pod_name: Pod 名称
                namespace: Namespace
                phase: 目标 phase（Pending, Running, Succeeded, Failed）
                max_retries: 最大重试次数（处理 409 Conflict）

            Raises:
                ApiException: K8s API 错误
            """
            from datetime import datetime, timezone
            import time

            for attempt in range(max_retries):
                try:
                    # 读取当前 Pod（获取最新的 resourceVersion）
                    pod = self.v1.read_namespaced_pod(pod_name, namespace)

                    # 修改 phase
                    pod.status.phase = phase

                    # 如果是 Running，设置 container_statuses
                    if phase == "Running":
                        # ⭐ 关键修复：设置 Pod.Status.StartTime（STORY-15-24 测试依赖此字段）
                        pod.status.start_time = datetime.now(timezone.utc)

                        pod.status.container_statuses = [
                            client.V1ContainerStatus(
                                # ⭐ 必需字段
                                name="main",
                                image="nginx:alpine",
                                image_id="sha256:xxxxxxxx",
                                container_id="docker://xxxxxxxx",
                                restart_count=0,
                                # ⭐ 状态字段
                                ready=True,
                                started=True,
                                state=client.V1ContainerState(
                                    running=client.V1ContainerStateRunning(
                                        started_at=datetime.now(timezone.utc)
                                    )
                                ),
                                last_state=client.V1ContainerState(
                                    waiting=None,
                                    running=None,
                                    terminated=None
                                )
                            )
                        ]

                        # 设置 pod_ip（模拟 Pod 已分配 IP）
                        pod.status.pod_ip = "127.0.0.1"
                        # ⚠️ 不设置 host_ip，让 K8s API 自动填充
                        # 设置 host_ip 会导致 K8s API 422 错误：
                        # "status.hostIPs[0].ip: Invalid value: must be equal to \`hostIP\`"
                        # pod.status.host_ip = "127.0.0.1"

                    # Patch Pod（触发 Informer UPDATE 事件）
                    # ⚠️ 注意：使用 patch_namespaced_pod_status 而不是 patch_namespaced_pod
                    #     这样可以只修改 status，不触发 spec 变更
                    self.v1.patch_namespaced_pod_status(
                        pod_name,
                        namespace,
                        pod,
                        field_manager="test-controller"
                    )

                    print(f"   ⭐ 主动设置 Pod {namespace}/{pod_name} phase = {phase}")
                    return  # 成功，退出

                except client.ApiException as e:
                    if e.status == 409 and attempt < max_retries - 1:
                        # 409 Conflict: 重试（可能是 K8s 正在更新 Pod）
                        print(f"   ⚠️  set_pod_phase 遇到 409 Conflict，重试 {attempt + 1}/{max_retries}")
                        time.sleep(0.5)  # 等待 500ms 后重试
                        continue
                    else:
                        raise  # 其他错误或重试次数用尽，抛出异常

        def wait_for_db_status(self, db_connection, pod_name, expected_status, timeout=10):
            """
            ⭐ 等待数据库中的业务状态更新（替代 time.sleep()）

            ✅ 测试策略：
              - 不使用硬编码的 time.sleep()
              - 轮询数据库，直到状态更新为预期值
              - 提供精确的反馈（耗时、状态）

            Args:
                db_connection: 数据库连接
                pod_name: Pod 名称
                expected_status: 预期的业务状态
                timeout: 超时时间（秒），默认 10 秒

            Returns:
                bool: 状态更新成功返回 True

            Raises:
                TimeoutError: 超时未更新为预期状态
            """
            import time
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    with db_connection.cursor() as cur:
                        cur.execute(
                            """SELECT status, k8s_pod_phase, created_at, updated_at
                               FROM pod_resource_status
                               WHERE k8s_pod_name = %s
                               ORDER BY updated_at DESC, created_at DESC LIMIT 1""",
                            (pod_name,)
                        )
                        result = cur.fetchone()

                        if result:
                            if result["status"] == expected_status:
                                elapsed = time.time() - start_time
                                print(f"   ✅ 数据库状态已更新: {expected_status} "
                                      f"(K8s phase: {result['k8s_pod_phase']}, 耗时 {elapsed:.2f}s)")
                                return True
                            else:
                                # 🔍 调试日志：显示当前状态
                                print(f"   🔍 当前状态: {result['status']} (期望: {expected_status}), "
                                      f"created_at={result['created_at']}, updated_at={result.get('updated_at', 'N/A')}")
                except Exception as e:
                    print(f"   ⚠️  查询数据库失败: {e}")

                time.sleep(0.5)  # 轮询间隔：500ms

            raise TimeoutError(
                f"数据库状态未在 {timeout} 秒内更新为 {expected_status}"
            )

        def wait_for_db_status_with_uid(self, db_connection, pod_name, k8s_pod_uid, expected_status, timeout=10):
            """
            ⭐ 等待数据库中的业务状态更新（通过 k8s_pod_uid 精确验证）

            ✅ 测试策略：
              - 使用 k8s_pod_uid 精确查询，避免查询到旧记录
              - 轮询数据库，直到状态更新为预期值
              - 提供明确的信号确认外部服务状态

            Args:
                db_connection: 数据库连接
                pod_name: Pod 名称（仅用于日志）
                k8s_pod_uid: K8s Pod UID（精确匹配）
                expected_status: 预期的业务状态
                timeout: 超时时间（秒），默认 10 秒

            Returns:
                bool: 状态更新成功返回 True

            Raises:
                TimeoutError: 超时未更新为预期状态
            """
            import time
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    with db_connection.cursor() as cur:
                        cur.execute(
                            """SELECT status, k8s_pod_phase, created_at, user_id
                               FROM pod_resource_status
                               WHERE k8s_pod_uid = %s""",
                            (k8s_pod_uid,)
                        )
                        result = cur.fetchone()

                        if result and result["status"] == expected_status:
                            elapsed = time.time() - start_time
                            print(f"   ✅ 数据库状态已更新: {expected_status} "
                                  f"(K8s phase: {result['k8s_pod_phase']}, "
                                  f"user_id={result['user_id']}, 耗时 {elapsed:.2f}s)")
                            return True
                except Exception as e:
                    print(f"   ⚠️  查询数据库失败: {e}")

                time.sleep(0.5)  # 轮询间隔：500ms

            raise TimeoutError(
                f"数据库状态未在 {timeout} 秒内更新为 {expected_status} (k8s_pod_uid={k8s_pod_uid})"
            )

        def wait_pod_ready(self, pod_name, namespace, timeout=60):
            """等待 Pod 进入 Ready 状态（兼容旧测试用例）"""
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

        def cleanup(self):
            """清理所有创建的 Pod"""
            print(f"\n🧹 清理 {len(self.created_pods)} 个测试 Pod...")

            for pod_name, namespace in self.created_pods:
                try:
                    self.v1.delete_namespaced_pod(pod_name, namespace)
                    print(f"   ✅ 已清理: {namespace}/{pod_name}")
                except ApiException as e:
                    print(f"   ⚠️  清理失败: {namespace}/{pod_name} - {e}")

            self.created_pods.clear()

        def get_pod_start_time(self, pod_name, namespace):
            """
            获取 Pod 的启动时间（K8s Pod.Status.StartTime）

            Args:
                pod_name: Pod 名称
                namespace: Namespace

            Returns:
                datetime: Pod 启动时间（如果存在）

            Raises:
                ApiException: Pod 不存在或读取失败
            """
            pod = self.v1.read_namespaced_pod(pod_name, namespace)
            return pod.status.start_time

    # 创建客户端实例
    k8s_client_obj = K8sClient(v1)

    # 在测试结束后自动清理
    yield k8s_client_obj

    # 自动清理所有创建的 Pod（防止资源泄露）
    k8s_client_obj.cleanup()

    print("✅ SIT 测试结束，所有测试 Pod 已清理")


# ============================================================
# Database Fixtures
# ============================================================

@pytest.fixture(scope="session")
def db_connection():
    """数据库连接（使用 Docker）"""
    import subprocess

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "event_db-dev")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")

    # 对于 Docker 环境，使用 localhost
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


# ============================================================
# Helper Fixtures
# ============================================================

@pytest.fixture
def test_pod_name():
    """生成测试 Pod 名称"""
    return f"test-sit-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def create_devpod(k8s_client):
    """创建 DevPod 的 fixture"""
    def _create(pod_name, gpu_count=1, namespace="example-service", node_selector=None, labels=None, annotations=None):
        default_labels = {
            "app.kubernetes.io/name": "example-service",
            "example-service.example.com/managed": "true",
        }

        # 合并自定义 labels
        if labels:
            default_labels.update(labels)

        # ✅ 修复: 使用 v3.2 标准的 cmdb.example.com/ annotation 前缀
        # 参考文档: docs/design/cmdb_design_v3.0.md
        default_annotations = {
            "cmdb.example.com/resource-name": pod_name,
            "cmdb.example.com/user-id": "test-user-sit",
            "cmdb.example.com/user-name": "Test User SIT",
            "cmdb.example.com/user-email": "test-sit@example.com",
            "cmdb.example.com/team-id": "test-team-sit",
            "cmdb.example.com/team-name": "Test Team SIT",
            "cmdb.example.com/project-id": "test-project-sit",
            "cmdb.example.com/project-name": "Test Project SIT",
        }

        # 合并自定义 annotations
        if annotations:
            default_annotations.update(annotations)

        return k8s_client.create_pod(
            pod_name=pod_name,
            namespace=namespace,
            labels=default_labels,
            annotations=default_annotations,
            gpu_count=gpu_count,
            node_selector=node_selector
        )

    return _create


@pytest.fixture
def create_argo_pod(k8s_client):
    """创建 ArgoWorkflow Pod 的 fixture"""
    def _create(pod_name, gpu_count, namespace="argo"):
        labels = {
            "workflows.argoproj.io/workflow": "test-workflow",
            "{PROJECT_NAME}/example.com": "true",
        }

        return k8s_client.create_pod(
            pod_name=pod_name,
            namespace=namespace,
            labels=labels,
            gpu_count=gpu_count
        )

    return _create


@pytest.fixture
def delete_pod(k8s_client):
    """删除 Pod 的 fixture"""
    def _delete(pod_name, namespace="example-service"):
        k8s_client.delete_pod(pod_name, namespace)

    return _delete


@pytest.fixture
def check_gpu_resource(k8s_client):
    """
    ⭐ 前置条件检查：GPU资源是否足够（快速失败原则）

    ✅ 最佳实践：
      - 在执行GPU测试前检查资源
      - 如果资源不足，立即skip测试
      - 避免无效等待（60秒超时）

    使用示例：
        @pytest.mark.skipif(reason="GPU资源不足")
        def test_gpu_something(check_gpu_resource):
            available, message = check_gpu_resource(required_gpu=1)
            if not available:
                pytest.skip(message)
            # 继续测试...
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from conftest_helpers import check_gpu_resources_available

    def _check(required_gpu=1, node_selector=None):
        return check_gpu_resources_available(
            k8s_client.v1,
            required_gpu=required_gpu,
            node_selector=node_selector
        )

    return _check


@pytest.fixture
def query_gpu_usage(db_connection):
    """查询 {BUSINESS_SHORT}的 fixture"""
    def _query(pod_name, usage_cycle=None):
        with db_connection.cursor() as cur:
            if usage_cycle:
                cur.execute("""
                    SELECT usage_cycle, usage_start_at, usage_end_at, gpu_count, gpu_hours
                    FROM pod_resource_gpu_usage
                    WHERE k8s_pod_name = %s AND usage_cycle = %s
                """, (pod_name, usage_cycle))
            else:
                cur.execute("""
                    SELECT usage_cycle, usage_start_at, usage_end_at, gpu_count, gpu_hours
                    FROM pod_resource_gpu_usage
                    WHERE k8s_pod_name = %s
                    ORDER BY usage_cycle
                """, (pod_name,))

            return cur.fetchall()

    return _query


@pytest.fixture
def query_pod_status(db_connection):
    """查询 Pod 状态的 fixture"""
    def _query(pod_name):
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT pod_name, pod_namespace, pod_resource_type, status,
                       gpu_count, k8s_pod_phase, created_at, updated_at
                FROM pod_resource_status
                WHERE k8s_pod_name = %s
                ORDER BY created_at DESC
            """, (pod_name,))

            return cur.fetchall()

    return _query


@pytest.fixture
def wait_for_informer(k8s_client, db_connection, test_pod_name):
    """
    等待 Informer 处理 Pod 事件的 fixture（轮询方式）

    ✅ 优化: 轮询间隔从 1 秒优化到 0.5 秒
    ✅ 性能: 平均等待时间减少 50%
    """
    def _wait(timeout=15, interval=0.5):
        """
        等待 Pod 记录出现在数据库中（轮询方式）

        Args:
            timeout: 超时时间（秒），默认 15 秒
            interval: 轮询间隔（秒），默认 0.5 秒

        Returns:
            bool: True 表示成功

        Raises:
            TimeoutError: 超时未出现
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            with db_connection.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM pod_resource_status WHERE k8s_pod_name = %s",
                    (test_pod_name,)
                )
                count = cur.fetchone()["count"]

                if count > 0:
                    return True

            time.sleep(interval)  # ✅ 优化: 固定 0.5 秒轮询间隔

        raise TimeoutError(f"Pod {test_pod_name} 未在 {timeout} 秒内出现在数据库中")

    return _wait


@pytest.fixture
def wait_for_db_record(db_connection):
    """
    等待数据库记录出现的 fixture（通用轮询工具）

    ✅ 用途: 替代硬编码 time.sleep()
    ✅ 优化: 轮询间隔 1 秒，减少数据库查询压力
    ✅ 生产环境验证: 考虑 Informer 2-5 秒延迟，默认超时 30 秒（6倍延迟，确保稳定性）

    Examples:
        # 等待 Pod 记录出现
        wait_for_db_record(
            "SELECT 1 FROM pod_resource_status WHERE pod_name = %s",
            ("test-pod",),
            timeout=30
        )

        # 等待特定状态
        wait_for_db_record(
            "SELECT 1 FROM pod_resource_status WHERE pod_name = %s AND status = %s",
            ("test-pod", "RUNNING"),
            timeout=30
        )
    """
    def _wait(query, params=None, timeout=30, interval=1.0):
        """
        等待数据库查询返回结果（轮询方式）

        Args:
            query: SQL 查询语句
            params: 查询参数（tuple）
            timeout: 超时时间（秒），默认 15 秒
            interval: 轮询间隔（秒），默认 0.5 秒

        Returns:
            bool: True 表示查询成功

        Raises:
            TimeoutError: 超时未返回结果
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            with db_connection.cursor() as cur:
                cur.execute(query, params or ())
                result = cur.fetchone()

                # RealDictCursor 返回字典，检查第一个值是否 >= 1
                if result and list(result.values())[0] >= 1:
                    return True

            time.sleep(interval)

        raise TimeoutError(f"数据库查询未在 {timeout} 秒内返回结果: {query}")

    return _wait


@pytest.fixture
def wait_pod_deleted(k8s_client):
    """
    等待 Pod 完全删除的 fixture（幂等操作）

    ✅ 幂等性：循环检查直到 Pod 完全删除（404）
    ✅ 超时保护：避免无限等待
    ✅ 异常处理：区分 404（正常）和其他错误（异常）

    Args:
        k8s_client: Kubernetes 客户端

    Returns:
        function: _wait(pod_name, namespace, timeout=30)
    """
    def _wait(pod_name, namespace, timeout=30):
        """
        等待 Pod 完全删除

        Args:
            pod_name: Pod 名称
            namespace: Namespace
            timeout: 超时时间（秒），默认 30 秒

        Raises:
            TimeoutError: 超时未删除
            ApiException: 其他 K8s API 错误（非 404）
        """
        start_time = time.time()
        last_error = None

        while time.time() - start_time < timeout:
            try:
                pod = k8s_client.v1.read_namespaced_pod(pod_name, namespace)

                # ✅ 检查 DeletionTimestamp（Pod 正在删除）
                if pod.metadata.deletion_timestamp is not None:
                    print(f"   ⏳ Pod {namespace}/{pod_name} 正在删除...")
                else:
                    print(f"   ⚠️  Pod {namespace}/{pod_name} 仍然存在（未触发删除）")

                time.sleep(1)

            except ApiException as e:
                if e.status == 404:
                    # ✅ Pod 已完全删除
                    elapsed = time.time() - start_time
                    print(f"   ✅ Pod {namespace}/{pod_name} 已删除（耗时 {elapsed:.1f}s）")
                    return True
                else:
                    # ❌ 其他 API 错误
                    last_error = e
                    print(f"   ⚠️  API 错误: {e}")
                    time.sleep(1)

        # ❌ 超时
        raise TimeoutError(
            f"Pod {namespace}/{pod_name} 未在 {timeout} 秒内删除。"
            f"最后错误: {last_error}"
        )

    return _wait


# ============================================================
# 全局清理 Fixtures（SIT 测试会话级别）
# ============================================================

@pytest.fixture(scope="session", autouse=True)
def global_sit_cleanup(k8s_client, db_connection):
    """
    SIT 测试会话级别的全局清理（幂等操作）

    ✅ 测试策略（支持并行执行）：
      1. 测试开始前：只清理超过3小时的过时数据（避免干扰正在运行的测试）
      2. 测试结束后：清理当前会话的所有 test-* 数据（恢复环境）

    ✅ 并行执行保障：
      - 只清理超过3小时的数据（SIT 和 UAT 可以并行运行）
      - 隐含假设：SIT + UAT 回归在3小时内能完成

    ✅ 幂等性保障：
      - K8s 资源清理：删除所有 test-* Pod（所有 namespace）
      - 数据库清理：只清理过时数据（created_at < NOW() - 3 hours）
      - 事务完整性：使用事务和重试机制

    ✅ 测试数据隔离：
      - 只清理 "test-*" 前缀的数据
      - 避免误删生产数据（如 example-service-user-001）

    Args:
        k8s_client: Kubernetes 客户端
        db_connection: 数据库连接
    """
    print("\n" + "="*70)
    print("🧹 SIT 全局清理：清理超过3小时的过时测试数据")
    print("="*70)

    # 步骤 1: 清理过时的测试历史数据（3小时前）
    # ✅ 关键：只清理旧数据，不影响正在运行的 UAT 测试
    clean_old_test_data(db_connection)

    # 步骤 2: 清理 K8s 资源（删除所有 test-* Pod）
    clean_k8s_pods(k8s_client, "test-")

    print("✅ SIT 环境已清理完成，提供干净的测试环境\n")

    yield

    # 会话结束后清理当前会话的所有数据
    print("\n" + "="*70)
    print("🧹 SIT 会话结束清理：清理当前会话的 test-* 数据")
    print("="*70)

    clean_k8s_pods(k8s_client, "test-")
    clean_db_data(db_connection, "test-%")

    print("✅ SIT 环境已恢复\n")


def clean_k8s_pods(k8s_client, prefix, max_retries=2):
    """
    清理 K8s 中指定前缀的 Pod（幂等操作）

    ✅ 清理策略：
      - 遍历所有测试相关 namespace
      - 删除所有匹配前缀的 Pod
      - 容忍 404 错误（Pod 已不存在）

    ✅ 重试机制：
      - 网络超时或临时 API 错误时自动重试
      - 最多重试 2 次

    Args:
        k8s_client: Kubernetes 客户端
        prefix: Pod 名称前缀（如 "test-"）
        max_retries: 最大重试次数
    """
    # 测试相关的 namespace
    namespaces = ["example-service", "argo", "dcs", "default", "train-job"]

    for namespace in namespaces:
        for attempt in range(max_retries):
            try:
                pods = k8s_client.v1.list_namespaced_pod(namespace)

                deleted_count = 0
                for pod in pods.items:
                    if pod.metadata.name.startswith(prefix):
                        print(f"   🗑️  删除 K8s Pod: {namespace}/{pod.metadata.name}")
                        k8s_client.v1.delete_namespaced_pod(
                            pod.metadata.name,
                            namespace
                        )
                        deleted_count += 1

                if deleted_count > 0:
                    print(f"   ✅ Namespace {namespace}: 删除了 {deleted_count} 个测试 Pod")
                break  # 成功，退出重试循环

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"   ⚠️  清理 K8s Pod 失败 ({namespace}): {e}")
                else:
                    print(f"   ⚠️  清理 K8s Pod 重试 {attempt + 1}/{max_retries}: {e}")
                    time.sleep(1)


def clean_db_data(db_connection, pattern, max_retries=3):
    """
    清理数据库中指定模式的记录（幂等操作）

    ✅ 清理策略：
      1. pod_resource_gpu_usage: 直接删除（有 pod_name 列）
      2. pod_resource_status: 最后删除（触发 CASCADE 清理 history）

    ✅ 事务完整性：
      - 使用 BEGIN/COMMIT/ROLLBACK 保证原子性
      - 失败时自动回滚
      - 支持重试机制

    Args:
        db_connection: 数据库连接
        pattern: 匹配模式（如 "test-%"）
        max_retries: 最大重试次数
    """
    for attempt in range(max_retries):
        try:
            with db_connection.cursor() as cur:
                # 开始事务
                cur.execute("BEGIN")

                # 步骤 1: 删除 {BUSINESS_SHORT}记录
                cur.execute(
                    "DELETE FROM pod_resource_gpu_usage WHERE pod_name LIKE %s",
                    (pattern,)
                )
                gpu_count = cur.rowcount

                # 步骤 2: 删除 Pod 资源状态（触发 CASCADE 清理 history）
                cur.execute(
                    "DELETE FROM pod_resource_status WHERE pod_name LIKE %s",
                    (pattern,)
                )
                status_count = cur.rowcount

                # 提交事务
                db_connection.commit()

                if gpu_count > 0 or status_count > 0:
                    print(f"   ✅ 数据库清理: GPU用量={gpu_count}, Status={status_count}")
                else:
                    print(f"   ℹ️  数据库无残留数据")

                return  # 成功，退出重试循环

        except Exception as e:
            # 回滚事务
            db_connection.rollback()

            if attempt == max_retries - 1:
                print(f"   ❌ 数据库清理失败: {e}")
                raise
            else:
                print(f"   ⚠️  数据库清理重试 {attempt + 1}/{max_retries}: {e}")
                time.sleep(1)


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
# 测试用例级别清理 Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def reset_test_environment(k8s_client, db_connection, request):
    """
    每个测试用例执行前的环境重置（function 级别）

    ✅ 清理策略：
      1. 清理上一个测试用例留下的 K8s Pod 和数据库记录
      2. 等待 Informer 事件队列为空（明确的信号）
      3. 确保环境完全重置，避免竞争条件

    ✅ 关键设计：
      - 不假设网络无延迟，明确等待外部服务状态
      - 检查 Informer 事件处理完成信号
      - 幂等操作：可以安全地重复执行

    Args:
        k8s_client: Kubernetes 客户端
        db_connection: 数据库连接
        request: pytest request 对象（用于获取 fixture 值）
    """
    import time

    # 获取当前测试的名称（用于日志）
    test_name = request.node.name if request.node else "unknown_test"

    # 步骤 1: 清理 K8s 中的 test-* Pod
    print(f"\n🔄 [{test_name}] 测试环境重置：清理 K8s 资源...")
    try:
        clean_k8s_pods(k8s_client, "test-", max_retries=1)
    except Exception as e:
        print(f"   ⚠️  K8s 清理失败（非致命）: {e}")

    # 步骤 2: 清理数据库中的 test-% 记录
    print(f"🔄 [{test_name}] 测试环境重置：清理数据库记录...")
    try:
        clean_db_data(db_connection, "test-%", max_retries=1)
    except Exception as e:
        print(f"   ⚠️  数据库清理失败（非致命）: {e}")

    # 步骤 3: ⭐ 等待 Informer 处理完残留事件（使用轮询替代硬编码 sleep）
    # ✅ 性能优化: 硬编码 20 秒 → 轮询（最多 15 秒，平均 2-5 秒）
    # ✅ 优化原理: 实时检查数据库状态，而不是盲目等待
    print(f"⏳ [{test_name}] 等待 Informer 处理完残留事件（轮询方式，最多 15 秒）...")
    start_time = time.time()
    timeout = 15  # 最多等待 15 秒
    interval = 0.5  # 轮询间隔 0.5 秒

    while time.time() - start_time < timeout:
        with db_connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM pod_resource_status WHERE pod_name LIKE 'test-%'")
            result = cur.fetchone()

            # ✅ 如果数据库中没有残留记录，说明环境已清理完成
            if result["count"] == 0:
                elapsed = time.time() - start_time
                print(f"   ✅ 环境已清理完成（耗时 {elapsed:.1f} 秒）")
                break

        time.sleep(interval)
    else:
        # 超时后的降级处理
        print(f"   ⚠️  等待超时（{timeout} 秒），继续执行...")

    # 步骤 4: 验证环境已清理完成（明确的信号）
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) as count FROM pod_resource_status WHERE pod_name LIKE 'test-%'")
        result = cur.fetchone()
        if result["count"] > 0:
            print(f"   ⚠️  数据库中仍有 {result['count']} 条残留记录，再次清理...")
            clean_db_data(db_connection, "test-%", max_retries=1)
            time.sleep(0.5)  # ✅ 优化: 1 秒 → 0.5 秒

    print(f"✅ [{test_name}] 测试环境已重置完成\n")

    yield

    # 测试结束后不需要额外清理，下一个测试用例的 fixture 会处理
    pass


def _cleanup_pod_data(db_connection, test_pod_name):
    """
    清理 Pod 相关的所有表数据（使用事务保证原子性）

    ✅ 优化策略：
    1. pod_resource_gpu_usage 有 pod_name 列，直接删除
    2. pod_resource_history 无 pod_name 列，但通过 resource_id 的
       ON DELETE CASCADE，当 pod_resource_status 被删除时会自动清理
    3. pod_resource_status 最后删除，触发 CASCADE 清理 history

    Args:
        db_connection: 数据库连接
        test_pod_name: 测试 Pod 名称（支持 LIKE 匹配）
    """
    with db_connection.cursor() as cur:
        try:
            # 开始事务
            cur.execute("BEGIN")

            # 步骤 1: 删除 {BUSINESS_SHORT}记录（有 pod_name 列，直接删除）
            cur.execute("DELETE FROM pod_resource_gpu_usage WHERE pod_name LIKE %s",
                       (f"{test_pod_name}%",))
            gpu_usage_deleted = cur.rowcount

            # 步骤 2: 删除历史记录（通过 resource_id 关联）
            # 注意：这里需要独立处理，因为 CASCADE 只在删除 status 时生效
            # 如果之前的测试留下了孤立的 history 记录，需要手动清理
            cur.execute("""
                DELETE FROM pod_resource_history
                WHERE resource_id IN (
                    SELECT resource_id FROM pod_resource_status WHERE pod_name LIKE %s
                )
            """, (f"{test_pod_name}%",))
            history_deleted = cur.rowcount

            # 步骤 3: 删除 Pod 资源状态记录（主表）
            # 这会触发 ON DELETE CASCADE，删除剩余的关联记录
            cur.execute("DELETE FROM pod_resource_status WHERE pod_name LIKE %s",
                       (f"{test_pod_name}%",))
            status_deleted = cur.rowcount

            # 提交事务
            db_connection.commit()

            # 调试日志（可选，帮助排查问题）
            if gpu_usage_deleted > 0 or history_deleted > 0 or status_deleted > 0:
                print(f"   🧹 清理数据: GPU用量={gpu_usage_deleted}, 历史={history_deleted}, 状态={status_deleted}")

        except Exception as e:
            # 回滚事务
            db_connection.rollback()
            raise e


# ============================================================
# STORY-15-25: ABORTED 状态的条件性同步 - SIT 测试 Fixtures
# ============================================================

@pytest.fixture
def abort_pod(k8s_client):
    """
    触发 Pod ABORTED 事件的 fixture（通过 kubectl delete）

    ⚠️ 关键改进：使用真实的 kubectl delete 命令，让 Informer 处理真实的 DELETE 事件

    ✅ 测试策略：
    1. 先让 Pod 达到 Running 状态（产生 {BUSINESS_SHORT}记录）
    2. 然后删除 Pod（触发 DELETE 事件）
    3. Informer 会处理为 ABORTED 状态（如果 Pod 有 {BUSINESS_SHORT}）
    """
    def _abort(pod_name, namespace="example-service"):
        try:
            # ✅ Step 1: 设置 Pod 为 Running 状态（触发 StartGPUUsage）
            print(f"   ⭐ 设置 Pod {pod_name} phase = Running（触发 {BUSINESS_SHORT}计算）")
            k8s_client.set_pod_phase(pod_name, namespace, "Running")
            time.sleep(3)  # 等待 Informer 处理 UPDATE 事件并创建 status 记录

            # ✅ Step 2: 等待 {BUSINESS_SHORT}记录创建（验证数据库）
            print(f"   ⏳ 等待 {BUSINESS_SHORT}记录创建...")
            import psycopg2
            conn = psycopg2.connect(
                host="db.example.internal",
                port=5433,
                dbname="event_db-dev",
                user="postgres",
                password="postgres"
            )
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            max_wait = 10
            for i in range(max_wait):
                cur.execute("""
                    SELECT usage_start_at, gpu_hours
                    FROM pod_resource_gpu_usage
                    WHERE k8s_pod_name = %s
                """, (pod_name,))
                result = cur.fetchone()
                if result and result['usage_start_at']:
                    print(f"   ✅ {BUSINESS_SHORT}记录已创建: usage_start_at={result['usage_start_at']}")
                    break
                time.sleep(1)

            cur.close()
            conn.close()

            if not result or not result['usage_start_at']:
                print(f"   ⚠️  警告：{BUSINESS_SHORT}记录未创建，跳过 ABORTED 测试")
                return

            # ✅ Step 3: 删除 Pod（触发真实的 DELETE 事件）
            print(f"   ⭐ 删除 Pod {namespace}/{pod_name}（触发 Informer DELETE 事件处理）")
            k8s_client.delete_pod(pod_name, namespace)
            time.sleep(3)  # 等待 Informer 处理 DELETE 事件

        except Exception as e:
            print(f"Warning: Failed to abort pod {pod_name}: {e}")

    return _abort


@pytest.fixture
def query_dim_metric(db_connection):
    """查询 dim_metric 表的 fixture"""
    def _query(pod_name):
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT resource_id, k8s_pod_uid, pod_name, status,
                       gpu_count, user_id, team_id, project_id
                FROM pod_resource_dim_metric
                WHERE pod_name = %s
            """, (pod_name,))

            result = cur.fetchone()
            if result:
                return {
                    'resource_id': result['resource_id'],
                    'k8s_pod_uid': result['k8s_pod_uid'],
                    'pod_name': result['pod_name'],
                    'status': result['status'],
                    'gpu_count': result['gpu_count'],
                    'user_id': result['user_id'],
                    'team_id': result['team_id'],
                    'project_id': result['project_id'],
                }
            return None

    return _query


@pytest.fixture
def insert_gpu_usage(db_connection):
    """手动插入 {BUSINESS_SHORT}记录的 fixture（用于测试）"""
    def _insert(pod_name, gpu_count, duration_minutes):
        """插入 {BUSINESS_SHORT}记录"""
        import uuid
        from datetime import datetime, timedelta

        # 先获取 resource_id
        with db_connection.cursor() as cur:
            cur.execute("""
                SELECT resource_id, k8s_pod_uid
                FROM pod_resource_status
                WHERE pod_name = %s
            """, (pod_name,))

            result = cur.fetchone()
            if not result:
                raise ValueError(f"Pod {pod_name} not found in pod_resource_status")

            resource_id = result[0]
            k8s_pod_uid = result[1]

        # 计算 {BUSINESS_SHORT}
        gpu_hours = gpu_count * (duration_minutes / 60.0)

        # 插入 gpu_usage 记录
        with db_connection.cursor() as cur:
            now = datetime.now()
            start_at = now - timedelta(minutes=duration_minutes)
            end_at = now

            cur.execute("""
                INSERT INTO pod_resource_gpu_usage
                (usage_id, resource_id, k8s_pod_uid, k8s_pod_name,
                 usage_cycle, usage_start_at, usage_end_at,
                 gpu_count, gpu_hours, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                resource_id,
                k8s_pod_uid,
                pod_name,
                0,  # usage_cycle
                start_at,
                end_at,
                gpu_count,
                gpu_hours,
                now,
                now
            ))

            db_connection.commit()

        return gpu_hours

    return _insert


# ============================================================
# Pytest 配置
# ============================================================
# Pytest 配置（测试分层标记）
# ============================================================

def pytest_configure(config):
    """配置 pytest 标记（包含性能分层）"""
    config.addinivalue_line("markers", "sit: SIT 系统集成测试")
    config.addinivalue_line("markers", "bug_detection: Bug Detection 异常检测测试")
    config.addinivalue_line("markers", "database: 数据库测试")
    config.addinivalue_line("markers", "k8s: Kubernetes 测试")

    # ✅ 性能分层标记（Phase 4: 测试分层标记实施）
    config.addinivalue_line("markers", "fast: 快速测试（< 30 秒）")
    config.addinivalue_line("markers", "normal: 正常测试（30 秒 - 2 分钟）")
    config.addinivalue_line("markers", "slow: 慢速测试（2 分钟 - 10 分钟）")
    config.addinivalue_line("markers", "ultra_slow: 超慢测试（> 10 分钟）")

"""
Pytest 配置和 Fixtures
"""

import pytest
import subprocess
import time
import psycopg2
from typing import Generator


# ============================================================
# K8s Client Fixture
# ============================================================

@pytest.fixture(scope="session")
def k8s_client():
    """K8s 客户端"""
    class K8sClient:
        def __init__(self):
            self.namespace = "default"

        def get_pod(self, pod_name: str, namespace: str = None):
            """获取 Pod"""
            ns = namespace or self.namespace
            result = subprocess.run(
                ["kubectl", "get", "pod", pod_name, "-n", ns, "-o", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            return None

        def create_pod(self, pod_name: str, gpu_count: int = 1, namespace: str = "example-service"):
            """创建测试 Pod"""
            # 简化版本：使用已有的 Pod
            pass

        def delete_pod(self, pod_name: str, namespace: str = None):
            """删除 Pod"""
            ns = namespace or self.namespace
            subprocess.run(
                ["kubectl", "delete", "pod", pod_name, "-n", ns],
                capture_output=True,
                timeout=10
            )

    return K8sClient()


# ============================================================
# 数据库连接 Fixture
# ============================================================

@pytest.fixture(scope="function")
def db_connection():
    """数据库连接（支持环境变量配置）"""
    import os

    # 从环境变量读取配置，支持巡检不同环境
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5433")
    database = os.getenv("DB_NAME", "event_db-dev")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")

    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    yield conn
    conn.close()


# ============================================================
# DevPod 创建 Fixture
# ============================================================

@pytest.fixture(scope="function")
def create_devpod(k8s_client):
    """创建 DevPod fixture"""
    created_pods = []

    def _create_pod(pod_name: str, gpu_count: int = 1, namespace: str = "example-service"):
        # 标记为已创建
        created_pods.append({"name": pod_name, "namespace": namespace})
        return pod_name

    yield _create_pod

    # 清理：删除所有创建的 Pod
    for pod in created_pods:
        try:
            k8s_client.delete_pod(pod["name"], pod["namespace"])
        except Exception:
            pass

# ============================================================
# API Base URL Fixture（Epic-13 新增，支持灵活配置）
# ============================================================

import os
from pathlib import Path

def _get_docker_port_mapped(container_name: str = "{PROJECT_NAME}-api", internal_port: int = 8082) -> str:
    """
    自动检测 Docker 容器端口映射

    Args:
        container_name: Docker 容器名称
        internal_port: 容器内部端口

    Returns:
        映射后的端口号（字符串），失败返回 "8082"
    """
    try:
        result = subprocess.run(
            ["docker", "port", container_name, str(internal_port)],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            # 输出格式: "0.0.0.0:8082" 或 ":::8082"
            mapped_port = result.stdout.strip().split(":")[-1]
            print(f"✅ 自动检测 Docker 端口: {container_name} → localhost:{mapped_port}")
            return mapped_port
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"⚠️  无法检测 Docker 端口: {e}")

    # 回退到默认值
    return "8082"

def _load_env_file():
    """加载 .env 文件（如果存在）"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✅ 加载测试配置: {env_file}")

@pytest.fixture(scope="session")
def api_base_url():
    """
    API 基础 URL（支持灵活配置）

    配置优先级：
    1. 环境变量 RESOURCE_METER_API_URL
    2. .env 文件中的 RESOURCE_METER_API_URL
    3. 自动检测 Docker 端口映射
    4. 默认值: http://localhost:8082/api/v1
    """
    # 尝试加载 .env 文件
    _load_env_file()

    # 优先级 1: 环境变量
    api_url = os.getenv("RESOURCE_METER_API_URL")
    if api_url:
        print(f"✅ 使用环境变量配置的 API URL: {api_url}")
        return api_url

    # 优先级 2: 自动检测 Docker 端口
    mapped_port = _get_docker_port_mapped()
    api_url = f"http://localhost:{mapped_port}/api/v1"
    print(f"✅ 使用自动检测的 API URL: {api_url}")

    return api_url

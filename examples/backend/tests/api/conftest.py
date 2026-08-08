"""
API 测试环境配置（测试环境）

环境变量优先级：
  1. EXAMPLE_SERVICE_API_URL 环境变量（CI/CD 或自定义）
  2. 自动检测测试环境 API（开发模式便利性）
"""

import pytest
import os
import requests


@pytest.fixture(scope="session")
def api_base_url():
    """
    API Base URL（自动检测或环境变量）

    ✅ 开发模式：自动检测测试环境 API（NodePort 30882）
    🏢 CI/CD 模式：使用 EXAMPLE_SERVICE_API_URL 环境变量

    使用方法：
      # 开发模式（自动检测测试环境）
      pytest tests/api/ -v

      # CI/CD 模式（显式指定）
      export EXAMPLE_SERVICE_API_URL="http://custom-api:8082/api/v1" pytest tests/api/ -v
    """
    # 优先级 1: 环境变量显式指定
    if "EXAMPLE_SERVICE_API_URL" in os.environ:
        return os.environ["EXAMPLE_SERVICE_API_URL"]

    # 优先级 2: 自动检测测试环境 API（开发模式便利性）
    # 检测测试环境 NodePort 服务 (test-api.example.internal:30882)
    try:
        # 尝试连接测试环境健康检查端点
        test_api_url = "http://test-api.example.internal:30882/api/v1"
        response = requests.get(f"{test_api_url}/healthz", timeout=2)
        if response.status_code == 200:
            print(f"\n✅ 自动检测到测试环境 API: {test_api_url}")
            return test_api_url
    except Exception:
        pass

    # 优先级 3: 默认本地开发环境
    default_url = "http://localhost:8082/api/v1"
    print(f"\n⚠️  使用默认本地 API: {default_url}")
    print(f"💡 提示：可通过环境变量自定义 API 地址")
    print(f"   export EXAMPLE_SERVICE_API_URL=\"http://test-api.example.internal:30882/api/v1\"")
    return default_url

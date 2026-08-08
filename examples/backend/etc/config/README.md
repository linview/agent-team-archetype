# 本地开发配置文件说明

**更新日期**: 2026-02-04
**用途**: 本地开发和测试环境配置
**适用项目**: {PROJECT_NAME}

---

## 📁 目录结构

```
etc/config/                     # 本地开发配置
├── README.md                   # 本文档
├── config.yaml                 # 应用默认配置文件
├── config_dev.yaml             # 开发环境配置
├── config_sit.yaml             # SIT 环境配置
├── config_prod.yaml            # 生产环境配置
├── {PROJECT_NAME}.yaml         # 额外配置
├── bearer-token.txt            # K8s Bearer Token（需生成）
└── ca.crt                      # K8s CA 证书（需生成）

etc/helm/                       # K8s 部署配置（参见 etc/helm/{PROJECT_NAME}/README.md）
└── {PROJECT_NAME}/             # Helm Chart
```

---

## 🎯 使用场景

**本地开发和测试**：直接运行二进制文件时使用这些配置文件。

```bash
# 使用默认配置
./{PROJECT_NAME}

# 指定配置文件
./{PROJECT_NAME} -f etc/config/config_dev.yaml
```

**K8s 部署**：请参考 `etc/helm/{PROJECT_NAME}/README.md` 使用 Helm Chart。

---

## 🔑 K8s 认证配置说明

{PROJECT_NAME} 使用 **Bearer Token + CA 证书** 方式连接 Kubernetes 集群。

### 为什么需要 ca.crt？

- **CA 证书**用于验证 Kubernetes API Server 的身份
- 防止中间人攻击（MITM）
- 确保连接到正确的 K8s 集群

### 配置文件格式

**config.yaml**:
```yaml
Kubeconfig:
  K8sApiServerUrl: "https://k8s-api.example.internal:6443"   # API Server 地址
  K8sBearerToken: "eyJhbGci..."                  # Bearer Token
  K8sCaFilePath: "./etc/config/ca.crt"           # CA 证书路径
  DevPodNamespace: "example-service"                      # 监听的命名空间
```

---

## 📝 生成步骤

### Step 1: 生成 CA 证书

从本地 `~/.kube/config` 提取 K8s CA 证书：

```bash
# 从 kubeconfig 提取 CA 证书并解码
kubectl config view --raw --minify --flatten \
  -o jsonpath='{.clusters[].cluster.certificate-authority-data}' \
  | base64 -d > etc/ca.crt

# 验证 CA 证书已生成
ls -l etc/ca.crt

# 查看证书内容（可选）
cat etc/ca.crt
```

**预期输出**:
```
-----BEGIN CERTIFICATE-----
MIIDBTCCAe2gAwIBAgIIfen4JLV7glYwDQYJKoZIhvcNAQELBQAwFTETMBEGA1UE
...
-----END CERTIFICATE-----
```

### Step 2: 创建 Service Account

```bash
# 创建 Service Account（如果不存在）
kubectl create serviceaccount {PROJECT_NAME} -n example-service

# 验证 Service Account 已创建
kubectl get sa {PROJECT_NAME} -n example-service
```

**预期输出**:
```
NAME              SECRETS   AGE
{PROJECT_NAME}    0         10s
```

### Step 3: 生成 Bearer Token

```bash
# 生成有效期 10 年的 Bearer Token
kubectl create token {PROJECT_NAME} -n example-service --duration=87600h > etc/bearer-token.txt

# 验证 Token 已生成
ls -l etc/bearer-token.txt

# 查看 Token 内容（可选）
head -c 50 etc/bearer-token.txt
echo "..."  # Token 很长，显示前 50 个字符
```

**预期输出**:
```
eyJhbGciOiJSUzI1NiIsImtpZCI6ImpGRlg5NC00NG1tdGpTRH...
```

### Step 4: 更新配置文件

编辑 `etc/config/config.yaml`，填入正确的配置：

```yaml
Kubeconfig:
  K8sApiServerUrl: "https://<API-SERVER-IP>:6443"  # 修改为实际地址
  K8sBearerToken: "<BEARER-TOKEN>"                  # 替换为 etc/config/bearer-token.txt 的内容 的内容
  K8sCaFilePath: "./etc/ca.crt"
  DevPodNamespace: "example-service"
```

**获取 API Server 地址**:
```bash
kubectl config view --minify -o jsonpath='{.clusters[].cluster.server}'
```

**示例**:
```bash
# 1. 获取 API Server URL
API_SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[].cluster.server}')
echo "API Server: $API_SERVER"
# 输出: https://k8s-api.example.internal:6443

# 2. 获取 Bearer Token
BEARER_TOKEN=$(cat etc/config/bearer-token.txt)

# 3. 更新配置文件
cat > etc/config/config.yaml <<EOF
Name: ExampleService.api
Host: 0.0.0.0
Port: 8082

# ... 其他配置 ...

Kubeconfig:
  K8sApiServerUrl: "$API_SERVER"
  K8sBearerToken: "$BEARER_TOKEN"
  K8sCaFilePath: "./etc/ca.crt"
  DevPodNamespace: "example-service"
EOF
```

### Step 5: 创建 RBAC 权限

```bash
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: {PROJECT_NAME}-role
rules:
- apiGroups: [""]
  resources: ["pods", "nodes"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: {PROJECT_NAME}-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: {PROJECT_NAME}-role
subjects:
- kind: ServiceAccount
  name: {PROJECT_NAME}
  namespace: example-service
EOF
```

---

## ✅ 验证配置

### 1. 验证 CA 证书

```bash
# 检查证书文件是否存在
ls -l etc/ca.crt

# 查看证书详细信息
openssl x509 -in etc/ca.crt -text -noout | grep -E "Subject:|Issuer:|Not After"
```

### 2. 验证 Bearer Token

```bash
# 解码 JWT Token（查看 payload 部分）
cat etc/config/bearer-token.txt | awk -F. '{print $2}' | base64 -d | jq .

# 应该看到类似输出：
# {
#   "aud": ["https://kubernetes.default.svc.cluster.local"],
#   "sub": "system:serviceaccount:example-service:{PROJECT_NAME}",
#   ...
# }
```

### 3. 测试 K8s 连接

```bash
# 使用 curl 测试 API Server 连接
curl -k --cacert etc/ca.crt \
  -H "Authorization: Bearer $(cat etc/config/bearer-token.txt)" \
  https://k8s-api.example.internal:6443/api/v1/namespaces/example-service/pods \
  | jq '.items[] | {name: .metadata.name, phase: .status.phase}'
```

**预期输出**:
```json
{
  "name": "test-pod-1",
  "phase": "Running"
}
{
  "name": "test-pod-2",
  "phase": "Pending"
}
```

### 4. 启动应用验证

```bash
# 启动应用
./{PROJECT_NAME} -f etc/config/config.yaml

# 查看日志，应该看到：
# [INFO] Starting Kubernetes Informer...
# [INFO] Informer started and synced successfully
# [INFO] Pod Event Handler registered successfully
```

---

## 🔧 故障排查

### 问题 1: CA 证书不存在

**错误**:
```
stat ./etc/ca.crt: no such file or directory
```

**解决**: 运行 Step 1 生成 CA 证书

### 问题 2: Bearer Token 无效

**错误**:
```
Unauthorized: 401
```

**解决**:
1. 检查 Token 是否过期（有效期 10 年）
2. 重新生成 Token：`kubectl create token {PROJECT_NAME} -n example-service --duration=87600h > etc/bearer-token.txt`

### 问题 3: 权限不足

**错误**:
```
pods is forbidden: User "system:serviceaccount:example-service:{PROJECT_NAME}" cannot list resource "pods"
```

**解决**: 运行 Step 5 创建 RBAC 权限

### 问题 4: API Server 地址错误

**错误**:
```
dial tcp: lookup kubernetes.default.svc: no such host
```

**解决**:
1. 检查 `K8sApiServerUrl` 是否正确
2. 使用 `kubectl config view --minify -o jsonpath='{.clusters[].cluster.server}'` 获取正确的地址

### 问题 5: TLS 握手失败

**错误**:
```
x509: certificate signed by unknown authority
```

**解决**:
1. 检查 CA 证书文件路径是否正确
2. 重新生成 CA 证书（Step 1）

---

## 📚 参考文档

- **K8s 集成指南**: `docs/guides/k8s_cluster_integration_guide.md`
- **K8s 官方文档**: https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/
- **Service Account Tokens**: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#create-token

---

## 📋 快速命令清单

```bash
# === 生成 CA 证书 ===
kubectl config view --raw --minify --flatten \
  -o jsonpath='{.clusters[].cluster.certificate-authority-data}' \
  | base64 -d > etc/ca.crt

# === 创建 Service Account ===
kubectl create serviceaccount {PROJECT_NAME} -n example-service

# === 生成 Bearer Token ===
kubectl create token {PROJECT_NAME} -n example-service --duration=87600h > etc/bearer-token.txt

# === 获取 API Server URL ===
kubectl config view --minify -o jsonpath='{.clusters[].cluster.server}'

# === 创建 RBAC 权限 ===
kubectl apply -f rbac-{PROJECT_NAME}.yaml

# === 验证配置 ===
ls -l etc/ca.crt etc/bearer-token.txt
head -c 50 etc/bearer-token.txt
```

---

**最后更新**: 2026-02-01
**维护者**: Example Service 开发团队

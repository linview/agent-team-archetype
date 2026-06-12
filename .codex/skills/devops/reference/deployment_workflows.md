# 部署工作流程（详细）

> **本文档提供部署和故障排查的详细工作流程**。主 SKILL.md 中已包含核心流程，本文档提供详细步骤和命令。

---

## 部署前检查清单（详细）

- [ ] 阅读项目 CLAUDE.md 理解部署架构
- [ ] 定位并分析 CI/CD 配置文件
- [ ] 制定执行计划（环境信息、风险识别、执行步骤）
- [ ] 备份当前配置（Helm values/K8s manifests）
- [ ] 在测试环境验证变更
- [ ] 确认回滚策略可用

---

## 部署执行流程（详细步骤）

### 1. 环境准备

```bash
# 验证 K8s 集群连接
kubectl cluster-info

# 验证 Helm 版本
helm version

# 验证当前 context
kubectl config current-context

# 验证目标 namespace
kubectl get namespace <namespace>
```

### 2. 配置更新

```bash
# 更新 values.yaml
vim values-prod.yaml

# 提交到 Git
git add values-prod.yaml
git commit -m "feat: update config"
git push
```

### 3. 构建镜像

```bash
# CI/CD 自动构建并推送镜像
# 或手动构建（开发环境）
docker build -t app:v1.0.0 .
docker push registry.example.com/app:v1.0.0
```

### 4. 执行部署

```bash
# Helm 部署（推荐）
helm upgrade --install app ./chart -f values-prod.yaml \
  --namespace production \
  --wait \
  --timeout 5m \
  --history-max 10

# ArgoCD 自动同步（GitOps 模式）
# ArgoCD 会自动检测 Git 变更并同步
```

### 5. 验证部署

```bash
# 检查 Pod 状态
kubectl get pods -n production
kubectl get pods -n production -l app=myapp

# 检查部署状态
kubectl rollout status deployment/app -n production

# 检查日志
kubectl logs -f deployment/app -n production

# 检查服务端点
kubectl get endpoints -n production

# 端口转发（本地测试）
kubectl port-forward deployment/app 8080:8080 -n production
```

---

## 故障排查流程（详细步骤）

### 1. 问题定位

```bash
# 查看 Pod 状态
kubectl get pods -n <namespace>
kubectl describe pod <pod-name>

# 查看事件
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# 查看日志
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # 查看上一个容器的日志
kubectl logs -f <pod-name>  # 实时跟踪

# 查看所有容器日志
kubectl logs <pod-name> -c <container-name>

# 查看资源使用
kubectl top pods -n <namespace>
kubectl top nodes
```

### 2. 常见问题诊断

#### ImagePullBackOff（镜像拉取失败）

**原因**：镜像不存在或权限不足

**诊断**：
```bash
kubectl describe pod <pod-name> | grep -A 10 Events
```

**解决**：
- 检查镜像名称和标签是否正确
- 检查 imagePullSecrets 是否配置
- 验证镜像仓库权限

#### CrashLoopBackOff（容器启动失败）

**原因**：应用启动失败

**诊断**：
```bash
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
```

**解决**：
- 检查应用日志中的错误信息
- 检查环境变量和配置是否正确
- 验证依赖服务是否可用

#### OOMKilled（内存溢出）

**原因**：内存限制过小

**诊断**：
```bash
kubectl describe pod <pod-name> | grep -A 5 Limits
```

**解决**：
- 调整 resources.limits.memory
- 优化应用内存使用
- 检查是否有内存泄漏

#### Pod 无法启动（Pending 状态）

**原因**：配置错误或依赖服务不可用

**诊断**：
```bash
kubectl describe pod <pod-name>
```

**解决**：
- 检查资源配额是否充足
- 验证存储类是否可用
- 检查节点选择器和容忍度

### 3. 回滚操作

```bash
# Helm 回滚（推荐）
helm history myapp -n production
helm rollback myapp 2 -n production

# K8s Deployment 回滚
kubectl rollout history deployment/app -n production
kubectl rollout undo deployment/app -n production
kubectl rollout undo deployment/app --to-revision=2 -n production

# Git 回滚
git revert HEAD
git push

# ArgoCD 回滚（GitOps 模式）
git revert HEAD
# ArgoCD 会自动检测并回滚
```

### 4. 紧急修复流程

```bash
# 1. 立即回滚（如果影响服务）
helm rollback myapp -n production

# 2. 分析问题
kubectl logs <previous-pod> -n production > error.log

# 3. 修复代码/配置
vim <fix-file>

# 4. 重新部署
helm upgrade --install app ./chart -f values-prod.yaml -n production

# 5. 验证修复
kubectl get pods -n production
kubectl logs -f deployment/app -n production
```

---

## 高级故障排查

### 网络问题

```bash
# 检查网络策略
kubectl get networkpolicies -n <namespace>

# 检查服务
kubectl get svc -n <namespace>
kubectl describe svc <service-name> -n <namespace>

# 测试 Pod 间连通性
kubectl exec -it <pod-a> -n <namespace> -- ping <pod-b-ip>

# 检查 DNS
kubectl exec -it <pod> -n <namespace> -- nslookup kubernetes.default
```

### 存储问题

```bash
# 检查 PV/PVC
kubectl get pv,pvc -n <namespace>

# 检查存储类
kubectl get storageclass

# 检查挂载点
kubectl exec -it <pod> -n <namespace> -- df -h
```

### 性能问题

```bash
# 查看资源使用趋势
kubectl top pods -n <namespace> --containers

# 查看节点资源
kubectl top nodes

# 检查 HPA（自动扩缩容）
kubectl get hpa -n <namespace>
kubectl describe hpa <hpa-name> -n <namespace>
```

---

**文档版本**: v1.0
**创建日期**: 2026-04-29
**维护者**: DevOps Team

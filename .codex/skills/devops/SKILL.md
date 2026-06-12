---
name: "devops"
description: "DevOps 工作技能 - CI/CD 流程、容器化构建、Kubernetes 部署、基础设施即代码、监控告警。当用户提到部署、容器化、K8s、Helm、ArgoCD、CI/CD、监控、日志、或需要执行部署、排查线上问题时，必须使用此技能。"
metadata:
  original-skill: "devops"
  version: "2.0"
---

# DevOps 工作技能

## 核心职责

1. **CI/CD 流程管理**：设计、维护持续集成与持续部署流水线
2. **容器化构建**：Docker 镜像构建、优化与发布管理
3. **Kubernetes 部署**：应用容器编排、配置管理、滚动更新
4. **基础设施即代码**：使用 Terraform/Helm 管理基础设施
5. **监控与告警**：配置监控体系、日志聚合、健康检查
6. **安全最佳实践**：镜像扫描、Secret 管理、RBAC 权限控制

---

## ⚠️ 行为准则（铁律）

### 准则 1：配置即代码，必须版本化管理

- ✅ 所有配置文件纳入 Git 版本控制
- ✅ 环境特定配置使用独立的 values 文件
- ❌ 禁止在生产环境手动修改配置
- ❌ 禁止在配置文件中硬编码密码

### 准则 2：镜像标签必须可追溯

- ✅ 生产环境使用语义化版本标签（v1.0.0）
- ✅ CI/CD 使用 Git Commit SHA 作为标签
- ❌ 禁止在生产环境使用 latest 标签
- ❌ 禁止使用无意义的标签（如 test、temp）

### 准则 3：部署必须可回滚

- ✅ Helm 部署保留历史版本（`--history-max`）
- ✅ 配置文件变更前必须备份
- ✅ 数据库变更必须有回滚脚本
- ❌ 禁止执行无法回滚的变更

### 准则 4：生产环境部署必须有人工确认

- ✅ 生产环境部署使用手动触发（when: manual）
- ✅ 部署前通知相关人员
- ✅ 部署时必须有人值守监控
- ❌ 禁止自动部署到生产环境

### 准则 5：监控与告警必须覆盖关键指标

- ✅ 配置健康检查（liveness/readiness probe）
- ✅ 监控核心资源（CPU/Memory/磁盘）
- ✅ 配置告警规则（Pod Crash/内存泄漏/API 错误率）
- ✅ 日志集中收集（ELK/Loki）

### 准则 6：敏感信息必须加密存储

- ✅ 密码使用 Secret/External Secrets/Vault
- ✅ Git 仓库中禁止明文密码
- ✅ 生产环境密钥定期轮换
- ❌ 禁止在配置文件中明文存储密码

---

## ⚠️ 常见错误（铁律）

### ❌ 错误 1：直接修改生产环境配置

```bash
# ❌ 错误：直接在线上修改配置
kubectl edit configmap myapp -n production

# ✅ 正确：修改配置文件，通过 CI/CD 部署
vim values-prod.yaml
git add values-prod.yaml
git commit -m "feat: update config"
```

### ❌ 错误 2：使用 latest 标签部署生产环境

```bash
# ❌ 错误：无法追溯版本
docker pull registry.example.com/app:latest

# ✅ 正确：使用语义化版本
docker pull registry.example.com/app:v1.0.0
```

### ❌ 错误 3：配置文件中硬编码密码

```yaml
# ❌ 错误：明文密码
database:
  password: "my-secret-password"

# ✅ 正确：引用 Secret
database:
  password: {{ .Values.db.password | quote }}
```

### ❌ 错误 4：不制定执行计划直接操作

```bash
# ❌ 错误：直接执行 helm upgrade
helm upgrade --install app ./chart

# ✅ 正确：先制定计划，确认后执行
helm get values myapp
helm diff upgrade myapp ./chart
helm upgrade --install app ./chart
```

---

## 工作流程（通用模板）

### 部署前检查清单

- [ ] 阅读项目 CLAUDE.md 理解部署架构
- [ ] 定位并分析 CI/CD 配置文件
- [ ] 制定执行计划（环境信息、风险识别、执行步骤）
- [ ] 备份当前配置（Helm values/K8s manifests）
- [ ] 在测试环境验证变更
- [ ] 确认回滚策略可用

### 部署执行流程

1. **环境准备**
   ```bash
   kubectl cluster-info
   helm version
   ```

2. **配置更新**
   ```bash
   vim values-prod.yaml
   git add values-prod.yaml
   git commit -m "feat: update config"
   ```

3. **构建镜像**
   ```bash
   # CI/CD 自动构建并推送镜像
   # 或手动构建（开发环境）
   docker build -t app:v1.0.0 .
   ```

4. **执行部署**
   ```bash
   # Helm 部署
   helm upgrade --install app ./chart -f values-prod.yaml
   # 或 ArgoCD 自动同步（GitOps 模式）
   ```

5. **验证部署**
   ```bash
   kubectl get pods -n production
   kubectl logs -f deployment/app -n production
   ```

### 故障排查流程

1. **问题定位**
   ```bash
   kubectl get pods -n <namespace>
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

2. **常见问题**
   - **ImagePullBackOff**：镜像不存在或权限不足
   - **CrashLoopBackOff**：应用启动失败（查看日志）
   - **OOMKilled**：内存限制过小（调整 resources.limits）
   - **Pod 无法启动**：配置错误或依赖服务不可用

3. **回滚操作**
   ```bash
   # Helm 回滚
   helm rollback myapp 2
   # K8s 回滚
   kubectl rollout undo deployment/app
   ```

> **💡 详细工作流程**：参见 [reference/deployment_workflows.md](reference/deployment_workflows.md)

---

## ⚠️ 项目理解方法论（铁律）

### 核心原则：理解项目 → 适配工具 → 制定计划

**黄金法则**：
- ✅ **第一优先**：理解项目的 DevOps 技术选型
- ✅ **第二优先**：阅读项目 CLAUDE.md 理解部署架构
- ✅ **第三优先**：定位并分析项目配置文件
- ❌ **绝对禁止**：不经理解直接套用其他项目的配置

### 快速识别项目技术栈

| 工具类型 | 典型文件名 | 识别方式 |
|---------|-----------|---------|
| **CI 平台** | `.gitlab-ci.yml` / `.github/workflows/*.yml` / `Jenkinsfile` | Glob 搜索 |
| **容器化** | `Dockerfile` / `docker-compose.yml` | Glob 搜索 |
| **K8s 部署** | `**/helm/**/*.yaml` / `**/argocd/*.yaml` | Glob 搜索 |
| **IaC 工具** | `terraform/**` / `**/*.tf` | Glob 搜索 |

### 关键配置分析

**CI/CD 配置**：
- 识别流水线阶段（test → build → deploy）
- 分析 Job 依赖关系（needs/dependsOn）
- 检查环境变量安全（避免硬编码密码）

**Dockerfile 分析**：
- 是否使用多阶段构建（减小镜像体积）
- 基础镜像安全性（官方镜像、版本固定）
- 层缓存利用（频繁变化的指令放后面）

**Helm Chart 分析**：
- values.yaml 是否按环境分离
- 资源限制是否合理（防止资源耗尽）
- 健康检查是否配置（liveness/readiness probe）

> **💡 详细方法论**：参见 [reference/project_understanding.md](reference/project_understanding.md)

---

## 环境配置管理

**设计原则**:
- ✅ **SKILL.md**: 存储可移植的 DevOps 行为准则和最佳实践
- ✅ **.env.skill**: 存储项目特定环境配置（namespace, API Server, kubeconfig）
- ❌ **禁止**: 将具体环境配置值硬编码在 SKILL.md 中

**部署前验证**:
1. 读取项目根目录 `.env.skill` 文件获取环境配置
2. 验证 Kubeconfig、API Server、Namespace 匹配
3. 参考本文档的 "部署前检查清单" 执行验证

**注意**: `.env.skill` 已在 `.gitignore` 中，不应提交到 Git 仓库

---

## 最佳实践

### 1. 配置管理

- 使用 Helm Chart 管理 K8s 资源
- values.yaml 按环境分离（dev/staging/prod）
- 敏感信息使用 Secret/External Secrets
- 配置文件纳入 Git 版本控制

### 2. 镜像构建

- 使用多阶段构建减小镜像体积
- 利用层缓存加速构建
- 使用语义化版本标签
- 定期扫描镜像漏洞

### 3. CI/CD 流水线

- 阶段划分清晰（test → build → deploy）
- 生产环境部署使用手动触发
- 配置自动回滚机制
- 保留部署历史记录

### 4. 监控告警

- 配置健康检查（liveness/readiness probe）
- 监控核心指标（CPU/Memory/QPS/延迟）
- 配置告警规则（多渠道通知）
- 日志集中收集（ELK/Loki）

### 5. 安全加固

- 定期扫描镜像漏洞（Trivy/Snyk）
- 使用非 root 用户运行容器
- 配置 RBAC 最小权限原则
- 敏感信息使用 Vault/External Secrets

---

## 🤝 Agent Team 协作

DevOps 工作需要与其他角色密切协作。本 SKILL 专注于 DevOps 技术实践，相关职责请参考：

- **架构设计** → [arch SKILL](../arch/SKILL.md)
  - 系统架构设计、部署架构
  - 网络拓扑、安全设计
  - 参考：`docs/design/system_architecture_v*.md`

- **开发工作流** → [dev SKILL](../dev/SKILL.md)
  - 构建、测试、代码质量
  - CI/CD Pipeline 集成
  - 参考：`docs/scrum/story/` 中的 Story 文档

- **测试验证** → [qa SKILL](../qa/SKILL.md)
  - 测试分层架构、UT/SIT/UAT
  - API 测试、性能测试
  - 部署后验证标准

- **项目管理** → [pm SKILL](../pm/SKILL.md)
  - 部署排期、发布计划
  - 技术债务管理
  - 参考：`docs/scrum/prd/` 中的 Epic 文档

---

## 关键资源

### Reference 文档

- [项目理解方法论（详细）](reference/project_understanding.md) - 项目理解完整方法论
- [部署工作流程（详细）](reference/deployment_workflows.md) - 部署和故障排查详细流程

### 官方文档

- Docker: https://docs.docker.com/
- Kubernetes: https://kubernetes.io/docs/
- Helm: https://helm.sh/docs/
- ArgoCD: https://argoproj.github.io/argo-cd/
- Prometheus: https://prometheus.io/docs/
- Trivy: https://aquasecurity.github.io/trivy/

### SKILL 文档

- `.codex/skills/arch/SKILL.md` - 架构设计技能
- `.codex/skills/dev/SKILL.md` - 开发工作技能
- `.codex/skills/qa/SKILL.md` - 测试工作技能
- `.codex/skills/pm/SKILL.md` - 项目管理技能

### 项目文档

- `CLAUDE.md` - 项目概览和部署架构
- `docs/design/system_architecture_v*.md` - 系统架构设计

---

**版本**: v2.0
**创建日期**: 2026-03-25
**更新日期**: 2026-04-29
**维护者**: DevOps Team

**更新日志**:
- v2.0 (2026-04-29): 🎯 **重大更新**：渐进式披露优化
  - 调整章节顺序，高价值内容前置（行为准则、常见错误）
  - 精简主文档（449 行 → 283 行，减少 37%）
  - 提取详细内容到 reference/ 目录
  - 新增 Agent Team 协作章节
  - 更新 description，更"pushy"的触发描述
- v1.0 (2026-03-25): 初始版本

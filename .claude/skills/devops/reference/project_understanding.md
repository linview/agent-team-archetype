# 项目理解方法论（详细）

> **本文档提供项目理解的详细方法论**。主 SKILL.md 中已包含核心原则，本文档提供详细步骤和模板。

---

## 核心原则：理解项目 → 适配工具 → 制定计划

**黄金法则**：
- ✅ **第一优先**：理解项目的 DevOps 技术选型
- ✅ **第二优先**：阅读项目 CLAUDE.md 理解部署架构
- ✅ **第三优先**：定位并分析项目配置文件
- ❌ **绝对禁止**：不经理解直接套用其他项目的配置

---

## Step 1：识别项目 DevOps 技术栈

### 通过配置文件快速识别

| 工具类型 | 典型文件名 | 识别方式 |
|---------|-----------|---------|
| **CI 平台** | `.gitlab-ci.yml` / `.github/workflows/*.yml` / `Jenkinsfile` | Glob 搜索 |
| **容器化** | `Dockerfile` / `docker-compose.yml` | Glob 搜索 |
| **K8s 部署** | `**/helm/**/*.yaml` / `**/argocd/*.yaml` / `**/k8s/*.yaml` | Glob 搜索 |
| **IaC 工具** | `terraform/**` / `**/*.tf` | Glob 搜索 |
| **构建工具** | `Makefile` / `build.sh` / `package.json` | Glob 搜索 |

### 快速识别命令

```bash
# 使用 Glob 工具定位 DevOps 配置
.gitlab-ci.yml           # GitLab CI
**/Jenkinsfile          # Jenkins Pipeline
**/Dockerfile*          # Docker 镜像
**/docker-compose*.yml  # Docker Compose
**/helm/**/*.yaml       # Helm Chart
**/argocd/*.yaml        # ArgoCD 应用
```

---

## Step 2：阅读 CLAUDE.md 理解部署架构

### 关键信息提取

- **技术栈**：编程语言、框架、依赖服务
- **部署环境**：dev/test/staging/prod
- **基础设施**：云平台、K8s 版本、网络配置
- **核心命令**：构建、测试、启动命令
- **配置管理**：ConfigMap/Secret/环境变量策略

---

## Step 3：分析配置文件理解部署流程

### CI/CD 配置分析

- 识别流水线阶段（test → build → deploy）
- 分析 Job 依赖关系（needs/dependsOn）
- 检查环境变量安全（避免硬编码密码）
- 确认部署目标环境（dev/test/prod）

### Dockerfile 分析

- 是否使用多阶段构建（减小镜像体积）
- 基础镜像安全性（官方镜像、版本固定）
- 层缓存利用（频繁变化的指令放后面）
- 非 root 用户运行（安全最佳实践）

### Helm Chart 分析

- values.yaml 是否按环境分离
- 资源限制是否合理（防止资源耗尽）
- 敏感信息是否使用 Secret
- 健康检查是否配置（liveness/readiness probe）

---

## Step 4：制定执行计划

### 执行计划模板

```markdown
## DevOps 执行计划模板

### 环境信息收集
- K8s 集群: [集群名称/版本]
- 镜像仓库: [仓库地址]
- CI/CD 平台: [平台类型和版本]
- Helm 版本: [版本号]

### 配置文件定位
- CI 配置: [文件路径]
- Dockerfile: [文件路径]
- Helm Chart: [文件路径]
- ArgoCD 配置: [文件路径]

### 部署流程分析
- 流水线阶段: [列出所有阶段]
- 部署策略: [滚动更新/蓝绿部署/金丝雀]
- 环境配置: [dev/test/prod]

### 风险识别
- [ ] 回滚策略: [如何回滚？]
- [ ] 数据迁移: [是否需要数据库迁移？]
- [ ] 依赖服务: [依赖哪些外部服务？]
- [ ] 配置变更: [哪些配置会变更？]

### 执行步骤
1. [ ] 备份当前配置
2. [ ] 更新配置文件
3. [ ] 构建 Docker 镜像
4. [ ] 推送镜像到仓库
5. [ ] 更新 Helm values
6. [ ] 执行部署命令
7. [ ] 验证部署状态

### 验证标准
- [ ] Pod 状态: Running
- [ ] 健康检查: 通过
- [ ] 日志检查: 无错误
- [ ] API 测试: 通过
```

---

**文档版本**: v1.0
**创建日期**: 2026-04-29
**维护者**: DevOps Team

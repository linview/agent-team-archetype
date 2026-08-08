# etc/ 目录说明

**更新日期**: 2026-02-04
**适用项目**: {PROJECT_NAME}

---

## 📁 目录结构

```
etc/
├── README.md                      # 本文档
│
├── config/                        # 本地开发和测试配置
│   ├── README.md                  # 本地配置使用说明
│   ├── config.yaml                # 默认配置文件
│   ├── config_dev.yaml            # 开发环境配置
│   ├── config_sit.yaml            # SIT 环境配置
│   ├── config_prod.yaml           # 生产环境配置
│   ├── {PROJECT_NAME}.yaml        # 额外配置
│   ├── bearer-token.txt           # K8s Bearer Token
│   └── ca.crt                     # K8s CA 证书
│
└── helm/                          # K8s 部署配置
    └── {PROJECT_NAME}/            # Helm Chart
        ├── Chart.yaml
        ├── values*.yaml
        ├── templates/
        └── README.md
```

---

## 🎯 使用指南

### 1️⃣ 本地开发

直接使用 `etc/config/` 下的配置文件运行应用。

```bash
# 使用默认配置
./{PROJECT_NAME}

# 指定配置文件
./{PROJECT_NAME} -f etc/config/config_dev.yaml
```

**详细说明**: 参见 `etc/config/README.md`

---

### 2️⃣ K8s 部署

使用 Helm Chart 部署到 Kubernetes 集群。

```bash
# 部署到测试环境
./deploy/scripts/helm-install.sh sit

# 或直接使用 Helm
helm upgrade --install {PROJECT_NAME}-prod \
  etc/helm/{PROJECT_NAME} \
  -f etc/helm/{PROJECT_NAME}/values-prod.yaml
```

**详细说明**: 参见 `etc/helm/{PROJECT_NAME}/README.md`

---

## 📊 配置文件对照

| 本地开发 | K8s 部署 |
|---------|---------|
| `etc/config/config.yaml` | Helm Chart → ConfigMap |
| `etc/config/config_dev.yaml` | `values-dev.yaml` |
| `etc/config/config_sit.yaml` | `values-sit.yaml` |
| `etc/config/config_prod.yaml` | `values-prod.yaml` |

---

## 🔑 区别说明

### 本地配置 (`etc/config/`)

- **用途**: 本地开发和测试
- **加载方式**: 直接读取文件系统
- **配置方式**: 手动编辑 YAML 文件
- **适用场景**: 本地调试、单元测试

### Helm Chart (`etc/helm/`)

- **用途**: K8s 生产部署
- **加载方式**: ConfigMap 挂载到容器
- **配置方式**: Helm values + 模板渲染
- **适用场景**: ArgoCD GitOps、生产环境

---

## 📚 相关文档

- **本地配置指南**: `etc/config/README.md`
- **Helm Chart 文档**: `etc/helm/{PROJECT_NAME}/README.md`
- **部署文档**: `deploy/README.md`
- **项目设计文档**: `docs/design/`

---

**最后更新**: 2026-02-04
**维护者**: Example Service 开发团队

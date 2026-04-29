# Spec-XChecker 详细使用指南

## 目录

- [直接运行 Python 脚本](#直接运行-python-脚本)
- [通过 Skill 调用](#通过-skill-调用推荐)
- [Hook 自动触发](#hook-自动触发)
- [报告位置](#报告位置)
- [故障排查](#故障排查)

---

## 直接运行（Python 脚本）

```bash
# 进入项目目录
cd /path/to/project

# 检查指定 Story
python3 .claude/skills/spec-xchecker/spec-xchecker.py --story 15-23 --mode medium

# 自动检测 Story ID
python3 .claude/skills/spec-xchecker/spec-xchecker.py --auto-mode --mode medium

# 指定输出格式
python3 .claude/skills/spec-xchecker/spec-xchecker.py --story 15-23 --mode medium --format json

# 只检查特定层
python3 .claude/skills/spec-xchecker/spec-xchecker.py --story 15-23 --mode medium --scope code,test
```

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--story` | Story ID（格式：15-23） | `--story 15-23` |
| `--auto-mode` | 自动检测当前 Story ID | `--auto-mode` |
| `--mode` | 检查模式（quick/medium/deep） | `--mode medium` |
| `--scope` | 检查范围（ds,sc,ct,st） | `--scope ds,sc` |
| `--format` | 输出格式（md/json） | `--format json` |
| `--output` | 输出文件路径 | `--output /tmp/report.md` |

---

## 通过 Skill 调用（推荐）

```bash
# Claude Code 会自动调用 spec-xchecker.py
/spec-xchecker --story 15-23 --mode medium
```

**优势**：
- ✅ 自动检测项目路径
- ✅ 自动加载 Story 文档
- ✅ 智能解析 AC 内容
- ✅ 动态生成检查策略

---

## Hook 自动触发

### Stop Hook（关闭 Claude 时触发）

**功能**：
- 自动检测到新的 git commit
- 启动独立 CC Session 执行检查
- 报告保存到 `/tmp/xchecker/{timestamp}/report.json`

**配置**：
```bash
# 在 ~/.claude/hooks/stop/ 目录创建触发脚本
# .claude/skills/spec-xchecker/trigger_check.sh
```

### SessionStart Hook（打开 Claude 时通知）

**功能**：
- 自动通知上次检查结果
- 显示报告摘要和文件路径

**配置**：
```bash
# 在 ~/.claude/hooks/sessionstart/ 目录创建通知脚本
# .claude/skills/spec-xchecker/notify_pending_reports.sh
```

---

## 报告位置

### 临时报告

**Markdown 报告**：`/tmp/xchecker/{timestamp}/report.md`

**JSON 报告**：`/tmp/xchecker/{timestamp}/report.json`

### Memory 索引

**索引文件**：`~/.claude/projects/-{encoded_path}/memory/spec-xchecker/reports_index.json`

**作用**：
- 记录所有历史检查报告
- 支持按 Story ID、时间范围查询
- 提供报告趋势分析

---

## 故障排查

### 问题 1：找不到 Story 文档

**症状**：
```
ERROR: Story document not found: docs/scrum/story/story-13-15-23-*.md
```

**解决方案**：
1. 检查 `docs/scrum/story/` 目录是否存在
2. 确认 Story ID 格式正确（例如：15-23）
3. 检查文件名匹配模式：`story-13-{story_id}-*.md`

### 问题 2：没有 Design Spec

**症状**：
```
WARNING: DS-01 FAILED: Story does not reference Design Spec
```

**解决方案**：
1. 在 Story 文档中添加 Design Spec 引用：
   ```markdown
   ## 设计文档
   - Design Spec: ../../design/data_layer_design_v2.0.md
   ```
2. 创建对应的 Design Spec 文档
3. 确保 Design Spec 文件路径正确

### 问题 3：检查通过但实际有问题

**可能原因**：
1. 使用了错误的检查模式（Quick 而不是 Deep）
2. AC 类型识别错误（混合类型 Story）
3. 静态检查无法发现动态问题

**解决方案**：
1. 使用 `--mode deep` 进行更深入的检查
2. 检查报告详情，查看具体是哪一项检查失败
3. 结合人工审查，不依赖单一工具

### 问题 4：Python 脚本执行失败

**常见错误**：
```
ModuleNotFoundError: No module named 'yaml'
```

**解决方案**：
```bash
# 安装依赖
pip install pyyaml

# 或使用项目虚拟环境
source venv/bin/activate
pip install -r requirements.txt
```

---

**相关文档**：
- [checklist.md](checklist.md) - 完整的 21 项检查清单
- [strategy_engine.md](strategy_engine.md) - 智能策略引擎详细说明
- [troubleshooting.md](troubleshooting.md) - 详细故障排查指南

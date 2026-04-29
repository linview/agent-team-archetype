# Spec-XChecker 故障排查指南

## 常见问题

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
1. 在 Story 文档中添加 Design Spec 引用
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

## 获取帮助

**反馈渠道**：chenhuazhong@example.com

**相关文档**：
- [usage_guide.md](usage_guide.md) - 详细使用指南
- [checklist.md](checklist.md) - 完整的 21 项检查清单
- [strategy_engine.md](strategy_engine.md) - 智能策略引擎

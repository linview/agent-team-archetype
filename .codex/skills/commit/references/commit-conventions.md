# Commit Conventions

## Commit Message 格式

本 skill **不强制** Conventional Commits 格式，commit message 可以自由编写。

## 自动生成规则

当使用 `--auto-generate` 时，系统会根据以下规则生成 commit message：

1. **文件类型识别**：
   - 测试文件：`test:`
   - 文档文件：`docs:`
   - 配置文件：`chore(config):`
   - 源代码文件：`feat:`

2. **摘要生成**：
   - 单文件：`Update <filename>`
   - 多文件：`Update <count> files`

3. **长度限制**：
   - 最大 50 字符
   - 超过则自动截断

## 项目风格匹配

- 系统会加载项目最近的 commits 匹配风格
- 如果存在 `CLAUDE.md`，会检查其中的提交约定

## 示例

```bash
# 自动生成
code-committer.sh commit --auto-generate

# 手动指定
code-committer.sh commit --message "Fix authentication bug in login module"
```

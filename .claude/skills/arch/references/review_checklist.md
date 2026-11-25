# 设计文档审查清单（arch 配套细则）

> 本文是 SKILL.md「文档审查清单」的完整清单：设计文档更新前后逐项过检。5 组按执行顺序排列；机械项由 `scripts/doc_structure_check.py` 自动拦截（exit ≠ 0 不得定稿），其余由 AI/审查者逐项判定。

## 1. 设计变更路径检查

- [ ] 已判定变更是否含未实证关键假设（假设驱动分级）
- [ ] 含关键假设时：analysis 文档 status 已至 proposal（必含最小假设表）、POC 已完成且结论全 pass（或按 fail 回路修订）
- [ ] POC 结论与关键证据已精选迁入 `{project_docs}/analysis/poc_{topic}/`（实验过程留 `test_reports/poc/{topic}/` 不入库；design doc 不引用 test_reports/）
- [ ] 采纳闭环完成：design/ 下另写正式方案（非 mv 搬运）+ analysis 文档转 adopted 并回填 adopted_by + design 版本说明反标出处

## 2. 版本更新检查

- [ ] 确定版本号增量（MAJOR/MINOR/PATCH）
- [ ] 已复制旧版本作为新版本基础
- [ ] 已更新文件名版本号（vX.Y → vX.Y+1）
- [ ] 已更新文档头部版本信息（版本号、日期、状态）
- [ ] 已更新版本说明和关键修正
- [ ] **验证版本号一致性**（文件名与头部版本号一致）

## 3. 归档和引用检查

- [ ] 已归档旧版本到 `docs/archive/`（带日期戳）
- [ ] **不要删除** `docs/design/` 下的往期版本文件
- [ ] 已更新其他文档中的引用链接
- [ ] 已验证文件存在性

## 4. 文档结构检查

- [ ] 头部为渐进式加载三段式（frontmatter → TOC → 正文，各段 `---` 分隔）
- [ ] 验证文档结构完整（必需章节齐全：frontmatter 元数据/TOC/概述/核心内容）
- [ ] 版本元数据已 frontmatter 化，正文不保留版本历史表
- [ ] **已运行成稿自检脚本** `scripts/doc_structure_check.py`（exit 0 才可定稿）
- [ ] **已执行语义 review 五问**（版本单一权威/编号一号一义/三面对账/引用现行/勘误无歧义）
- [ ] 黑话/隐喻均有直白同位语，代号全文唯一（去黑话铁律）
- [ ] 验证内部链接有效（锚点链接准确）
- [ ] 验证跨文档引用使用相对路径

## 5. 最终验证

- [ ] 提交版本控制
- [ ] 检查 Git 状态确保所有文件已暂存

---

**相关文档**：
- [文档可读性纪律指南](doc_readability_guide.md) - 渐进式加载结构、去黑话判例、语义五问详解、hook 挂载样例
- [设计变更三步流程 SOP 细则](design_iteration_sop.md) - analysis 三级状态、POC 路径、升版操作详解

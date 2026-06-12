# 交互流程文档模板

用于 Frame 阶段描述用户操作路径和状态变化。

## 模板

```markdown
## 交互流程：[功能名称]

### 前置条件
- 用户已登录
- [其他前置条件]

### 主流程

\`\`\`mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant B as 后端

    U->>F: 操作触发
    F->>B: API 请求
    B-->>F: 响应数据
    F->>U: 更新 UI
\`\`\`

### 状态变化

| 步骤 | 用户操作 | 前端状态变化 | API 调用 | UI 反馈 |
|------|---------|------------|---------|--------|
| 1 | [操作] | [状态变化] | [API] | [反馈] |

### 异常流程

| 异常场景 | 触发条件 | 前端处理 | 用户提示 |
|---------|---------|---------|---------|
| [场景] | [条件] | [处理] | [提示] |
```

## 示例：需求链路追踪

```markdown
## 交互流程：需求链路追踪

### 前置条件
- 用户在 Dashboard 页面
- 数据库中有飞书任务数据

### 主流程

| 步骤 | 用户操作 | 前端状态变化 | API 调用 | UI 反馈 |
|------|---------|------------|---------|--------|
| 1 | 页面加载 | `workItems=[]`, `selected=''` | `GET /work-items?page_size=100` | 下拉框加载选项 |
| 2 | 点击下拉框 | `loading=true` | — | 显示选项列表 |
| 3 | 输入搜索词 | `loading=true` | `GET /work-items?search=xxx` | 过滤选项列表 |
| 4 | 选择任务 | `selected='id'`, `chainData=null` | `GET /chain/full?work_item_id=id` | Sankey 区域 loading |
| 5 | 链路返回 | `chainData={nodes, edges}` | — | 渲染 Sankey 图 + 节点表 |

### 异常流程

| 异常场景 | 触发条件 | 前端处理 | 用户提示 |
|---------|---------|---------|---------|
| 无链路数据 | 任务未关联 MR | `chainData=null` | Sankey 区域显示"暂无链路数据" |
| API 超时 | 后端慢查询 | `error='timeout'` | Toast 提示"查询超时，请重试" |
| 搜索无结果 | 关键词不匹配 | `workItems=[]` | 下拉框显示"无匹配结果" |
```

# Wizard Onboarding 操作参照(使用者向)

> 本文件是 sentinel skill 的**运行时操作性参照**(读者=执行 wizard 的 agent/用户),自 wizard onboarding 设计方案提炼"怎么做"的操作步骤、选型标准与规避写法(不承载设计论证)。

## 何时进 wizard

| 场景 | 行为 |
|---|---|
| 项目首次呼唤 `/sentinel` 且 `.claude/sentinel.d/` 无 `*.yaml` | 自动启动 wizard |
| `/sentinel init` 或 `/sentinel wizard` | 显式启动(重配/新增哨兵) |
| 已有声明,直接 `/sentinel register <name>.yaml` | **不进** wizard,直接注册 |

**铁律**:wizard 只在 onboarding 跑一次,绝不进定时巡检链路;产出的声明由确定性引擎执行。

## 四步流程

```
① 识项目 → ② 选 SRE 模式 → ③ 选探针+设判据 → ④ 产声明+配凭据
```

### ① 识别项目类型(问 2-3 个问题)

问:有无 HTTP 入口?定时任务还是常驻服务?有无数据库?→ 映射下表模式。非三类(前端/纯编排等)诚实告知"暂未覆盖,可手写声明"。

### ② 选 SRE 模式

| 模式 | 适用 | 推荐探针 | 典型判据 | 凭据 |
|---|---|---|---|---|
| **A 后端 API health/RED** | 微服务/REST/gRPC | `http_probe`+`metrics_scrape` | `expect_in status_code [200]`、`expect_le error_rate max 0.01`、`expect_le latency_ms max 500` | `api_token`(常可免) |
| **B 数据-ETL liveness** | cron/Airflow/timer | `schedule_liveness`+`log_grep`+`api_query` | `expect_ge trigger_count min N`、`expect_eq count equals 0` | `ssh`(取日志) |
| **C 数据-DB integrity/USE** | PG/Redis/对象存储 | `db_query`+`metrics_scrape` | `expect_ge row0 min N`、`expect_le saturation max 0.85` | `db`(只读 DSN) |

### ③ 选探针 + 设判据(限定 5 原语)

对每个推荐探针:用户填 `target`(校验格式,如 `http://...`/`docker:<name>`)→ 展示该探针 signals → 用户选 signal 设阈值。

判据只允许 `expect_eq / expect_le / expect_ge / expect_in / expect_regex`,按缺口规避:

| 用户想要的 | 引导写法 |
|---|---|
| "须包含 X"(正极性) | `expect_ge match_count min 1` |
| "A 且 B"(合取) | 拆两个探针各一断言 |
| "L ≤ x < H"(范围) | `expect_ge` + `expect_le` 两探针 |

### ④ 产声明 + 配凭据

1. 落 `.claude/sentinel.d/<name>.yaml`(git-tracked,可 review)
2. 凭据:引导用户在项目根 `.env.skill` 对应 section 填值;声明里只写 `credentials: {ssh: <section名>}`——**凭据值绝不写进 yaml**
3. 输出 `sentinel register <name>.yaml` 指令,用户确认后注册 → wizard 退出

## 声明模板骨架

```yaml
# .claude/sentinel.d/<name>.yaml(wizard 产出物)
name: <哨兵名>
schedule: "<cron 表达式>"
probes:
  - name: <探针实例名>
    type: <http_probe|metrics_scrape|schedule_liveness|log_grep|api_query|db_query>
    target: <http://... | docker:<name> | ...>
    credentials: {ssh: <section>}   # 可选;只引 section 名
    asserts:
      - signal: <signal 名>
        op: <expect_eq|expect_le|expect_ge|expect_in|expect_regex>
        args: {...}
```

---
name: sentinel
description: 线上服务哨兵——定期巡检、功能回归测试、健康检查、数据质量验证和根因分析(RCA)。当用户提到"巡检"、"回归测试"、"健康检查"、"线上分析"、"RCA"、"服务可用性验证"、"数据质量"或需验证生产环境服务健康时使用本技能。注意:泛化的"测试/检查"除非明确含巡检/回归/健康检查语义,否则不应触发。
version: "1.6"
---

# Sentinel - 线上服务哨兵

## 何时触发

- 用户明确说"执行巡检"、"运行回归测试"、"线上健康检查"
- 需要验证服务可用性、数据完整性、口径一致性
- 生产环境问题诊断、根因分析(RCA)
- 定期/预防性监控,或首次为一个服务配置线上哨兵(`/sentinel init` 触发 wizard onboarding)

> 泛化的"测试"、"检查"(如单元测试、代码检查)不触发本技能,除非明确含巡检/回归/健康检查语义。

## 核心职责

Sentinel 是线上服务的守护者:

- 🛡️ **定期巡检** —— 声明驱动,周期性 fire 探针、断言、归因
- ✅ **功能回归** —— API 冒烟、数据质量、口径一致性验证
- 🔍 **健康分析** —— Golden Signals / RED / USE 框架
- 🎯 **根因分析** —— 异常自动落 md 报告,含探针/target/信号/判据

## 架构:声明驱动引擎

巡检逻辑由**确定性引擎**(`scripts/sentinel_engine/`)承担,LLM 与 CronCreate 只携带**薄 prompt** 触发——这是执行模型铁律(设计 §10.2):**判定逻辑零 LLM token**,可复现、可审计。

```
声明 yaml(声明"看什么/怎么判")
  → register(产薄 prompt + scheduled_tasks.json 唤醒载荷)
  → CronCreate 到点 fire(只带薄 prompt)
  → 引擎 run:resolve(纯)→ execute(唯一 IO)→ extract(纯)→ assert(5 原语)
  → 全 pass:一行 ok 静默(零扰);有 fail:落 md 报告归因
```

- **探针生命周期**(设计 §5.3/§6.1):`resolve`/`extract` 是纯函数,`execute` 是唯一 IO 副作用点。断言/报告由引擎统一处理,探针不自己断言。
- **5 断言原语**(设计 §7):`expect_eq`(equals)/`expect_le`(max)/`expect_ge`(min)/`expect_in`(in)/`expect_regex`(not_match)。
- **确定性**(设计 G6):同一声明两次执行 signals 完全一致。

## 快速开始

```bash
# 引擎自包含在 skill 内(PYTHONPATH 指向本 skill 的 scripts/)
export PYTHONPATH=.claude/skills/sentinel/scripts

# 跑声明:全 pass → 一行 ok 静默;有 fail → 落 test_reports/*.md 归因
python -m sentinel_engine run <声明.yaml>

# 注册:生成薄 prompt + scheduled_tasks.json(CronCreate 唤醒载荷)
# (产物默认落 test_reports/sentinel/,v1.6:过渡产物不污染项目根)
python -m sentinel_engine register <声明.yaml>
```

> 首次使用建议走 `/sentinel init` wizard onboarding,从 SRE 模式菜单生成声明,无需手写。

## 探针库(7 探针)

| 探针 | 观测对象 | 典型 signals | 典型判据 |
|---|---|---|---|
| `http_probe` | HTTP 单端点 | `status_code` / `latency_ms` | `expect_in status_code [200]` |
| `api_smoke` | HTTP 多端点冒烟 | `all_passed` / `pass_count` / `<key>_status` | `expect_eq all_passed equals true` |
| `metrics_scrape` | Prometheus `/metrics` | 各 query 名(RED/USE) | `expect_le error_count max N` |
| `log_grep` | 日志正则计数 | `match_count` | `expect_le match_count max 0` |
| `schedule_liveness` | 定时任务心跳 | `trigger_count` | `expect_ge trigger_count min N` |
| `api_query` | docker/k8s API 查询 | 声明 fields 路径 | `expect_eq status equals running` |
| `db_query` | 只读 SQL(§12.2 白名单) | 声明 columns | `expect_ge row_total min N` |

> 连接层(真实 K8s/PG/API/docker)由 **fetcher 子进程**承担(设计 §12.1),凭据经环境变量注入,引擎不内置任何连接逻辑——故可移植、不触碰真实环境。
>
> **自带真实 DB fetcher(v1.6)**:`scripts/sentinel_engine/tools/` 下提供 `pg_fetcher.py`(PostgreSQL/psql)与 `mysql_fetcher.py`(MySQL),供 `db_query` 探针直接引用:
>
> ```yaml
> # 声明 probes[].params.fetcher(或 env SENTINEL_DB_FETCHER)
> fetcher: .claude/skills/sentinel/scripts/sentinel_engine/tools/pg_fetcher.py
> ```
>
> 凭据经 `.env.skill` section 注入 env(`DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`,`DB_NAME` 必填无默认);双层只读保险 = 引擎 §12.2 白名单 + fetcher 只读账号。其他数据源(K8s/API/日志)的 fetcher 仍由项目自备。

## wizard onboarding(设计 §11.0)

wizard 是 `/sentinel` 的**首次配置引导**:把"声明从零手写"降为"从 SRE 模式菜单填值",低门槛个性化。

**铁律:wizard 绝不进定时巡检链路。** 它只在 onboarding 跑(可耗 token 的 LLM 交互引导),产出标准声明后退出;后续定时执行一律走确定性引擎。这把 LLM 的非确定性严格隔离在"首次配置"这一可复核边缘环节,不影响巡检判定的可复现性(G6)。wizard 是纯文档引导(SKILL.md 本节 + 模板),不是可执行代码,故"不进定时链路"天然成立。

**触发条件:**
- 首次呼唤:`.claude/sentinel.d/` 为空(无任何 `*.yaml`)时自动启动
- 主动触发:`/sentinel init` 或 `/sentinel wizard`(重新配置 / 新增哨兵)
- 跳过:已有声明且用户直接 `/sentinel register <name>.yaml`

**4 步引导(设计 §3):** ① 识别项目类型 → ② 选 SRE 模式 → ③ 选探针 + 设判据 → ④ 产声明 + 配凭据

- **设判据时主动规避已知缺口**(§7.1):正极性匹配("须含 X")→ 引导 `expect_ge match_count min 1`;合取("A 且 B")→ 拆两个探针各一断言;范围("L ≤ x < H")→ `expect_ge` + `expect_le` 两探针。
- **产出物**:`.claude/sentinel.d/<name>.yaml`(git-tracked,可 review)+ `.env.skill` section 引导(若需凭据)+ 一条 `sentinel register <name>.yaml` 指令。

**3 模式模板**(位于 `templates/wizard_templates/`,均已通过 schema 校验):

| 模板 | 适用 | 探针组合 | SRE 对齐 |
|---|---|---|---|
| `mode_a_backend_api.yaml` | 微服务 / REST / 有 HTTP 入口 | `http_probe` + `api_smoke` + `metrics_scrape` | Golden Signals / RED |
| `mode_b_data_etl.yaml` | cron / Airflow / 定时任务 | `schedule_liveness` + `log_grep` + `api_query` | cron heartbeat |
| `mode_c_data_db.yaml` | PG / Redis / 对象存储 | `db_query` + `metrics_scrape` | USE |

> 非首批类型(前端 / 纯编排 / 管道)诚实告知"v1.2 暂未覆盖,可手写声明或等后续版本"。

## 声明格式与凭据铁律

**声明结构**(设计 §9):

```yaml
schema_version: 1
sentinel: <哨兵名>
schedule: "*/10 * * * *"        # CronCreate 调度表达式
credentials: {ssh: <section>}   # 可选:引用 .env.skill toml section 名
probes:
  - type: http_probe
    target: http://host:port/healthz
    assert: {op: expect_in, value: status_code, in: [200]}
```

**凭据铁律(设计 §12.1):**
- 凭据**绝不内联进 yaml / prompt**,声明只写 `.env.skill` 的 **toml section 名**
- `.env.skill` 统一放**项目根**(git root),是全部 skill 共用的敏感配置唯一入口;已入 `.gitignore`,严禁提交
- 引擎 `run` 时定位 `.env.skill`:`SENTINEL_ENV_SKILL` 环境变量优先,否则从声明 yaml 向上找 git root(无 .git 取 cwd);按 section 注入环境变量,探针的 fetcher 子进程读取
- 防护:仓库根 `.gitignore` + skill 目录 `.gitignore` 双层

**只读铁律(设计 §12.2):** `db_query` 只接受 `SELECT`/`WITH`(白名单),写操作 fail-fast 不连库;凭据应最小权限(只读 DSN)。

## 安全警告

🚨 **未确认环境安全前,严禁触碰真实 K8s/PG/API:**
- 引擎不内置任何连接逻辑,一切外部访问经 **fetcher 子进程**(凭据/命令由环境变量注入,如 `SENTINEL_LOG_FETCHER`/`SENTINEL_DB_FETCHER`/`SENTINEL_API_FETCHER` 指向拉取工具)——配置 fetcher 时必须确认其指向安全目标,绝不配置连接真实 PG/K8s 的 fetcher
- 未确认环境安全前,不运行任何连真实环境的巡检/脚本

## 资源索引

- **Wizard 操作参照**:`references/wizard_onboarding.template.md`(onboarding 四步流程/模式选型/判据规避写法,agent 运行时查阅)
- **引擎代码**:`scripts/sentinel_engine/`(schema/runner/assertion/resolver/reporter/cli/register + 7 探针)
- **自带 fetcher**:`scripts/sentinel_engine/tools/`(`pg_fetcher.py`/`mysql_fetcher.py`,db_query 真实只读 DB 拉取;其余数据源 fetcher 项目自备)
- **声明模板**:`templates/wizard_templates/{mode_a_backend_api,mode_b_data_etl,mode_c_data_db}.yaml`(可直接 `run` 验证格式,或作 wizard 起点)
- **项目声明**:`.claude/sentinel.d/<name>.yaml`(项目自建,git-tracked;声明目录为**跨栈统一落点**——.codex 栈安装亦用本目录,引擎零硬编码,由调用方传入)

package config

import "github.com/zeromicro/go-zero/rest"

type Config struct {
	rest.RestConf
	RedisConf    RedisConf
	DatabaseConf DatabaseConf
	Kubeconfig   Kubeconfig
	LogConf      LogConf
	TimezoneConf TimezoneConf // 时区配置（服务层统一使用 UTC+8）
	CronConf     CronConf     // TTL 清理定时任务配置（STORY-15-22）
}

type RedisConf struct {
	Host    string
	Pass    string
	DB      int
	Enabled bool
}

type DatabaseConf struct {
	Type     string
	Host     string
	Port     int
	DBName   string
	Username string
	Password string
}

type Kubeconfig struct {
	K8sApiServerUrl    string
	K8sBearerToken     string // Deprecated: Use K8sBearerTokenPath with InitContainer
	K8sBearerTokenPath string // Path to bearer token file (auto-fetched by InitContainer)
	K8sCaFilePath      string
	K8sKubeconfigPath  string // Explicit path to kubeconfig file
	DevPodNamespace    string
}

type LogConf struct {
	K8sEventLogLevel string // K8s 事件日志级别 (debug, info)
	K8sEventLogPath  string // K8s 事件独立日志文件路径
}

// TimezoneConf 时区配置
type TimezoneConf struct {
	Timezone string // 时区名称，默认 "Asia/Shanghai" (UTC+8)
}

// CronConf TTL 清理定时任务配置（STORY-15-22）
// ⚠️ AC-15 (2026-04-14): TTL 阈值已可配置化，支持不同环境设置不同的 TTL
type CronConf struct {
	Enabled          bool   `json:",default=true"`          // 是否启用定时任务
	Timezone         string `json:",default=Asia/Shanghai"` // 时区配置
	CleanupHistory   string `json:",default=0 2 * * *"`     // history 表清理 cron 表达式（每天 2:00）
	CleanupStatus    string `json:",default=0 3 * * *"`     // status 表清理 cron 表达式（每天 3:00）
	CleanupDimMetric string `json:",default=0 4 * * *"`     // dim_metric 表清理 cron 表达式（每天 4:00）

	// ⭐ AC-15: TTL 阈值配置（支持不同环境设置不同的 TTL）
	// 格式: Postgres INTERVAL 语法，例如 "30 days", "90 days", "7 days"
	CleanupHistoryTTL   string `json:",default=30 days"` // history 表 TTL（测试环境可设置为 "7 days"）
	CleanupStatusTTL    string `json:",default=30 days"` // status 表 TTL（测试环境可设置为 "7 days"）
	CleanupDimMetricTTL string `json:",default=90 days"` // dim_metric 表 TTL（测试环境可设置为 "30 days"）
}

// ============================================================================
// 聚合模型定义 - Aggregation Model Definitions
// 版本: 1.0
// 创建日期: 2026-03-23
// 作者: Claude Code (Sonnet 4.6)
// Story: STORY-13-02
//
// 功能:
//   - 定义聚合维度常量
//   - 定义时间粒度常量
//   - 定义聚合查询配置结构
// ============================================================================

package model

import "time"

// 聚合维度常量
const (
	// AggregateDimensionNode 按 K8s 节点聚合
	AggregateDimensionNode = "node"

	// AggregateDimensionNamespace 按命名空间聚合
	AggregateDimensionNamespace = "namespace"

	// AggregateDimensionUser 按用户聚合
	AggregateDimensionUser = "user"

	// AggregateDimensionTeam 按团队聚合
	AggregateDimensionTeam = "team"

	// AggregateDimensionProject 按项目聚合
	AggregateDimensionProject = "project"
)

// 时间粒度常量
const (
	// TimeGranularityDay 按天聚合
	TimeGranularityDay = "day"

	// TimeGranularityHour 按小时聚合
	TimeGranularityHour = "hour"

	// TimeGranularityMinute 按分钟聚合
	TimeGranularityMinute = "minute"

	// TimeGranularityNone 不聚合（详细记录）
	TimeGranularityNone = "none"
)

// AggregateQueryConfig 聚合查询配置
type AggregateQueryConfig struct {
	// Dimensions 聚合维度（如 ["node"], ["node", "namespace"]）
	Dimensions []string

	// TimeGranularity 时间粒度（day, hour, minute, none）
	TimeGranularity string

	// StartTime 查询开始时间
	StartTime time.Time

	// EndTime 查询结束时间
	EndTime time.Time

	// Filters CMDB 维度过滤（可选）
	Filters *AggregateFilters
}

// AggregateFilters 聚合查询过滤器
type AggregateFilters struct {
	UserID       *string
	TeamID       *string
	ProjectID    *string
	PodName      *string
	ResourceType *string
}

// GPUUsageAggregateItem {BUSINESS_SHORT}聚合项（DAO 层使用）
type GPUUsageAggregateItem struct {
	// TimeBucket 时间桶（可选，RFC3339 格式）
	TimeBucket *string

	// Dimensions 动态维度（如 {"node_name": "k8s-node-1", "namespace": "train-job"}）
	Dimensions map[string]string

	// TotalGPUHours 总 {BUSINESS_SHORT}（小时）
	TotalGPUHours float64

	// RecordCount 记录数
	RecordCount int

	// UniquePods 唯一 Pod 数
	UniquePods int
}

// GetValidDimensions 获取有效的聚合维度白名单
func GetValidDimensions() map[string]bool {
	return map[string]bool{
		AggregateDimensionNode:      true,
		AggregateDimensionNamespace: true,
		AggregateDimensionUser:      true,
		AggregateDimensionTeam:      true,
		AggregateDimensionProject:   true,
	}
}

// IsValidDimension 验证维度是否有效
func IsValidDimension(dimension string) bool {
	validDimensions := GetValidDimensions()
	return validDimensions[dimension]
}

// GetDimensionDBMapping 获取维度到数据库字段的映射
func GetDimensionDBMapping() map[string]string {
	return map[string]string{
		AggregateDimensionNode:      "k8s_node_name",
		AggregateDimensionNamespace: "pod_namespace",
		AggregateDimensionUser:      "user_id",
		AggregateDimensionTeam:      "team_id",
		AggregateDimensionProject:   "project_id",
	}
}

// GetDimensionJSONMapping 获取维度到 JSON 字段的映射
func GetDimensionJSONMapping() map[string]string {
	return map[string]string{
		AggregateDimensionNode:      "node_name",
		AggregateDimensionNamespace: "namespace",
		AggregateDimensionUser:      "user_id",
		AggregateDimensionTeam:      "team_id",
		AggregateDimensionProject:   "project_id",
	}
}

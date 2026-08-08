package dao

import (
	"context"
	"time"

	"example-service/internal/model"
)

// PodResourceStatusDAOInterface defines the interface for Pod resource status data access
// This interface enables mocking for unit testing (Spec → Scenario → Mock Data alignment)
type PodResourceStatusDAOInterface interface {
	// Create creates a new Pod resource status record
	Create(ctx context.Context, pod *model.PodResourceStatus) error

	// GetByK8sUID retrieves a Pod resource by K8s UID (CRITICAL: prevents duplicate processing)
	// Returns (nil, nil) if not found
	GetByK8sUID(ctx context.Context, k8sUID string) (*model.PodResourceStatus, error)

	// GetByID retrieves a Pod resource by resource ID
	GetByID(ctx context.Context, resourceID string) (*model.PodResourceStatus, error)

	// Update updates a Pod resource status record
	Update(ctx context.Context, pod *model.PodResourceStatus) error

	// List retrieves Pod resources based on filter criteria
	List(ctx context.Context, filter *PodFilter) ([]*model.PodResourceStatus, error)

	// Ping checks database connectivity
	Ping(ctx context.Context) error
}

// PodResourceGPUUsageDAOInterface defines the interface for GPU usage data access
// This interface enables mocking for unit testing (Spec → Scenario → Mock Data alignment)
type PodResourceGPUUsageDAOInterface interface {
	// Create creates a new GPU usage record
	Create(ctx context.Context, usage *model.PodResourceGPUUsage) error

	// GetByK8sUID retrieves the latest GPU usage record for a Pod by K8s UID
	GetByK8sUID(ctx context.Context, k8sUID string) (*model.PodResourceGPUUsage, error)

	// GetByID retrieves a GPU usage record by usage ID
	GetByID(ctx context.Context, usageID int64) (*model.PodResourceGPUUsage, error)

	// EndUsage ends a GPU usage record and calculates GPU hours
	EndUsage(ctx context.Context, usageID int64, endTime time.Time, gpuHours float64) error

	// List retrieves GPU usage records for a resource
	List(ctx context.Context, resourceID string, limit int) ([]*model.PodResourceGPUUsage, error)

	// QueryByFilter queries GPU usage records with filter criteria
	QueryByFilter(ctx context.Context, filter *GPUUsageFilter) ([]*model.PodResourceGPUUsage, error)

	// ✅ STORY-13-05 新增：QueryByFilterWithPagination 分页查询 {BUSINESS_SHORT}记录
	// 支持分页参数（page, pageSize）
	// 返回记录列表、总数、错误
	QueryByFilterWithPagination(ctx context.Context, filter *GPUUsageFilter, page, pageSize int) ([]*model.PodResourceGPUUsage, int, error)

	// ✅ STORY-13-02 新增：QueryAggregate 查询聚合 {BUSINESS_SHORT}
	// 支持按维度聚合（node, namespace, user, team, project）
	// 支持时间聚合（day, hour, minute）
	// 返回聚合结果列表、总数、错误
	QueryAggregate(ctx context.Context, config *model.AggregateQueryConfig) ([]model.GPUUsageAggregateItem, int, error)

	// Ping checks database connectivity
	Ping(ctx context.Context) error
}

// PodResourceHistoryDAOInterface defines the interface for Pod resource history data access
// This interface enables mocking for unit testing (Spec → Scenario → Mock Data alignment)
type PodResourceHistoryDAOInterface interface {
	// Create creates a new history record
	Create(ctx context.Context, history *model.PodResourceHistory) error

	// List retrieves history records for a specific Pod
	List(ctx context.Context, resourceID string, limit int) ([]*model.PodResourceHistory, error)

	// ListByTimeRange retrieves history records within a time range
	ListByTimeRange(ctx context.Context, startTime, endTime time.Time, limit int) ([]*model.PodResourceHistory, error)
}

// PodResourceDimMetricDAOInterface defines the interface for Pod resource dim metric data access
// This interface enables mocking for unit testing (Spec → Scenario → Mock Data alignment)
// Spec: Design Spec v4.1 §4.2 (Dim Metric Table Design)
// Story: STORY-15-06 (PodResourceDimMetric 数据层完整实现)
type PodResourceDimMetricDAOInterface interface {
	// Create creates a new dim metric record
	Create(ctx context.Context, metric *model.PodResourceDimMetric) error

	// Upsert inserts or updates a record (based on k8s_pod_uid)
	// Uses ON CONFLICT DO UPDATE to avoid race conditions
	Upsert(ctx context.Context, metric *model.PodResourceDimMetric) error

	// GetByUID retrieves a dim metric record by k8s_pod_uid
	// Returns (nil, nil) if not found
	GetByUID(ctx context.Context, uid string) (*model.PodResourceDimMetric, error)

	// GetByResourceID retrieves a dim metric record by resource_id
	// Returns (nil, nil) if not found
	GetByResourceID(ctx context.Context, resourceID string) (*model.PodResourceDimMetric, error)

	// List retrieves dim metric records based on filter criteria
	// Supports filtering by: user_id, team_id, project_id, pod_resource_type, status, k8s_node_name, time range
	List(ctx context.Context, filter *DimMetricFilter) ([]*model.PodResourceDimMetric, error)

	// SyncBatch batch syncs records (used by 15-minute scheduled sync)
	// Uses transaction to ensure atomicity
	SyncBatch(ctx context.Context, metrics []*model.PodResourceDimMetric) error

	// Delete deletes a dim metric record by resource_id
	Delete(ctx context.Context, resourceID string) error

	// DeleteBeforeDate deletes dim metric records before a specific date (TTL cleanup)
	// Returns the number of rows deleted
	DeleteBeforeDate(ctx context.Context, date time.Time) (int64, error)

	// Ping checks database connectivity
	Ping(ctx context.Context) error
}

// NOTE: 具体的 DAO 实现类型（如 PodResourceStatusDAO）在本范例中省略。
// 实际项目中应在此文件或同包其他文件提供实现，并通过编译期断言确保满足接口，例如：
//
//	var _ PodResourceStatusDAOInterface = (*PodResourceStatusDAO)(nil)

// PodFilter provides filtering options for listing Pod resource status records
type PodFilter struct {
	UserID          *string
	TeamID          *string
	ProjectID       *string
	PodName         *string
	PodNamespace    *string
	PodResourceType *string
	Status          *string
	TimeStart       *time.Time
	TimeEnd         *time.Time
	Limit           int
	Offset          int
}

// GPUUsageFilter provides filtering options for querying GPU usage records
type GPUUsageFilter struct {
	UserID       *string
	TeamID       *string
	ProjectID    *string
	PodName      *string
	ResourceType *string
	UsageStart   *time.Time
	UsageEnd     *time.Time
	Limit        int
	Offset       int
}

// DimMetricFilter provides filtering options for listing dim metric records
// Spec: Design Spec v4.1 §4.2 (Query Filter Design)
type DimMetricFilter struct {
	UserID          *string
	TeamID          *string
	ProjectID       *string
	PodResourceType *string
	Status          *string
	K8sNodeName     *string
	TimeStart       *time.Time
	TimeEnd         *time.Time
	Limit           int
	Offset          int
}

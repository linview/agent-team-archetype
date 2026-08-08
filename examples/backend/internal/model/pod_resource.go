package model

import "time"

// PodResourceStatus represents the current status of a Pod resource
type PodResourceStatus struct {
	ResourceID      string `db:"resource_id"`
	PodName         string `db:"pod_name"`
	PodNamespace    string `db:"pod_namespace"`
	PodResourceType string `db:"pod_resource_type"`
	K8sPodUID       string `db:"k8s_pod_uid"` // Critical: prevents duplicate processing
	K8sPodName      string `db:"k8s_pod_name"`
	K8sPodPhase     string `db:"k8s_pod_phase"`
	K8sPodReason    string `db:"k8s_pod_reason"`
	K8sPodMessage   string `db:"k8s_pod_message"` // ✅ P0: Pod 状态详细信息

	// Business ownership (CMDB foreign keys)
	UserID      string `db:"user_id"`
	UserName    string `db:"user_name"`
	UserEmail   string `db:"user_email"`
	TeamID      string `db:"team_id"`
	TeamName    string `db:"team_name"` // ✅ ENHANCEMENT-001: 团队名称
	ProjectID   string `db:"project_id"`
	ProjectName string `db:"project_name"` // ✅ ENHANCEMENT-001: 项目名称

	// Resource specifications
	CPURequest    string `db:"cpu_request"`
	MemoryRequest string `db:"memory_request"`
	GPUCount      int    `db:"gpu_count"`
	GPUProduct    string `db:"gpu_product"`
	RDMAEnabled   bool   `db:"rdma_enabled"` // ✅ P1: RDMA 是否启用

	// Business status (simplified, hardcoded state machine)
	Status string `db:"status"` // PENDING, RUNNING, STOPPED, RELEASED

	// Timeline
	CreatedAt    time.Time  `db:"created_at"`
	PodStartedAt *time.Time `db:"pod_started_at"`
	StoppedAt    *time.Time `db:"stopped_at"`

	// Image information
	ImageName string `db:"image_name"`
	ImageTag  string `db:"image_tag"`

	// Business attributes (CMDB metadata from labels/annotations)
	BusinessAttributes map[string]string `db:"business_attributes"` // ✅ JSONB: Pod labels/annotations
}

// TableName returns the database table name for PodResourceStatus
func (PodResourceStatus) TableName() string {
	return "pod_resource_status"
}

// PodResourceGPUUsage represents GPU usage records (supports multiple restart cycles)
type PodResourceGPUUsage struct {
	UsageID         int64  `db:"usage_id"`
	ResourceID      string `db:"resource_id"`
	PodName         string `db:"pod_name"`
	PodResourceType string `db:"pod_resource_type"`

	// GPU information
	GPUCount   int    `db:"gpu_count"`
	GPUProduct string `db:"gpu_product"`

	// Usage period (supports multiple restart cycles)
	UsageCycle   int        `db:"usage_cycle"`
	UsageStartAt time.Time  `db:"usage_start_at"`
	UsageEndAt   *time.Time `db:"usage_end_at"`

	// K8s identifiers
	K8sPodUID   string `db:"k8s_pod_uid"`
	K8sPodName  string `db:"k8s_pod_name"` // ✅ FIX: 添加 K8sPodName 字段
	K8sNodeName string `db:"k8s_node_name"`

	// Calculation results (auto-computed by trigger)
	DurationSeconds *int     `db:"duration_seconds"`
	GPUHours        *float64 `db:"gpu_hours"`

	// ✅ v2.0: Real-time calculation fields (for active pods)
	GPUHoursCalculated *float64  `db:"gpu_hours_calculated"` // Real-time calculated GPU hours
	CalculatedAt       time.Time `db:"calculated_at"`        // Timestamp of calculation

	CreatedAt time.Time `db:"created_at"`
}

// TableName returns the database table name for PodResourceGPUUsage
func (PodResourceGPUUsage) TableName() string {
	return "pod_resource_gpu_usage"
}

// PodResourceHistory represents operation history for a Pod resource (v3.0 optimized)
// Only retains core audit fields, deleted 6 redundant fields to save 55% storage
type PodResourceHistory struct {
	HistoryID  int64  `db:"history_id"`
	ResourceID string `db:"resource_id"`

	// State change
	Action           string  `db:"action"` // CREATE, UPDATE, DELETE
	ActionFromStatus *string `db:"action_from_status"`
	ActionToStatus   string  `db:"action_to_status"`

	// K8s state change
	K8sPodPhaseFrom *string `db:"k8s_pod_phase_from"`
	K8sPodPhaseTo   string  `db:"k8s_pod_phase_to"`

	ActionAt time.Time `db:"action_at"`

	// ✅ v3.0 deleted redundant fields:
	// - PodName, PodResourceType: Can be obtained via JOIN pod_resource_status
	// - OperatorUserID, OperatorUsername: 100% fixed value "system"
	// - ActionDesc: Only 3 fixed values, already represented by action field
}

// TableName returns the database table name for PodResourceHistory
func (PodResourceHistory) TableName() string {
	return "pod_resource_history"
}

// PodResourceDimMetric represents GPU usage aggregation query dimension table (v4.1)
// This is a read-only table synchronized from pod_resource_status every 15 minutes
// Storage optimization: 90-day TTL with cascade deletion of gpu_usage records
// Spec: Design Spec v4.1 §4.2 (Dim Metric Table Design)
type PodResourceDimMetric struct {
	// Primary key and associations (2 fields)
	ResourceID string `db:"resource_id"` // Primary key (shared with status table)
	K8sPodUID  string `db:"k8s_pod_uid"` // UNIQUE constraint (prevents duplicates)

	// Pod basic information (3 fields)
	PodName         string `db:"pod_name"`
	PodNamespace    string `db:"pod_namespace"`
	PodResourceType string `db:"pod_resource_type"` // EXAMPLE_SERVICE, ARGO_WORKFLOW, RAY_JOB, TRAIN_JOB

	// CMDB core dimensions (GPU query required) (9 fields) ⚠️ v4.2.1: +team_name, +project_name (STORY-15-15 FIX)
	UserID    string  `db:"user_id"`     // User ID (CMDB dimension)
	UserName  *string `db:"user_name"`  // User name (CMDB dimension, nullable, STORY-13-08)
	UserEmail *string `db:"user_email"` // User email (CMDB dimension, nullable, STORY-13-08)
	TeamID    string  `db:"team_id"`    // Team ID (CMDB dimension)
	TeamName  *string `db:"team_name"`  // Team name (CMDB dimension, nullable, v4.2.1)
	ProjectID string  `db:"project_id"` // Project ID (CMDB dimension, optional)
	ProjectName *string `db:"project_name"` // Project name (CMDB dimension, nullable, v4.2.1)

	// GPU related (2 fields)
	GPUCount   int    `db:"gpu_count"`   // GPU count
	GPUProduct string `db:"gpu_product"` // GPU product model (e.g., A100, V100)

	// Node dimensions (2 fields)
	SSHHostIP   *string `db:"ssh_host_ip"`   // DevPod SSH login IP (user perspective, nullable)
	K8sNodeName *string `db:"k8s_node_name"` // K8s node name (operations perspective, nullable)

	// Status fields (5 fields)
	Status       string     `db:"status"` // PENDING, CREATED, RUNNING, STOPPED, RELEASED, ABORTED
	CreatedAt    time.Time  `db:"created_at"`
	ReleasedAt   *time.Time `db:"released_at"`
	PodStartedAt *time.Time `db:"pod_started_at"` // ⭐ GPU usage calculation key field
	StoppedAt    *time.Time `db:"stopped_at"`     // ⭐ GPU usage calculation key field

	// Sync metadata (1 field) ⚠️ v4.1 deleted: updated_at (redundant, read-only table)
	SyncedAt time.Time `db:"synced_at"` // Last sync time (15-minute scheduled sync from status table)
}

// TableName returns the database table name for PodResourceDimMetric
func (PodResourceDimMetric) TableName() string {
	return "pod_resource_dim_metric"
}

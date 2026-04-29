package model

import "time"

// User represents a CMDB user
type User struct {
	UserID      string    `db:"user_id"`
	Username    string    `db:"username"`
	DisplayName string    `db:"display_name"`
	Email       string    `db:"email"`
	EmployeeID  string    `db:"employee_id"`
	CreatedAt   time.Time `db:"created_at"`
}

// TableName returns the database table name for User
func (User) TableName() string {
	return "cmdb_users"
}

// Team represents a CMDB team (supports hierarchy)
type Team struct {
	TeamID       string    `db:"team_id"`
	TeamCode     string    `db:"team_code"`
	TeamName     string    `db:"team_name"`
	ParentTeamID *string   `db:"parent_team_id"`
	LeaderUserID *string   `db:"leader_user_id"`
	CreatedAt    time.Time `db:"created_at"`
}

// TableName returns the database table name for Team
func (Team) TableName() string {
	return "cmdb_teams"
}

// UserTeamMembership represents a user-team relationship
type UserTeamMembership struct {
	MembershipID int64      `db:"membership_id"`
	UserID       string     `db:"user_id"`
	TeamID       string     `db:"team_id"`
	Role         string     `db:"role"`
	JoinedAt     time.Time  `db:"joined_at"`
	LeftAt       *time.Time `db:"left_at"`
}

// TableName returns the database table name for UserTeamMembership
func (UserTeamMembership) TableName() string {
	return "cmdb_user_team_memberships"
}

// Project represents a CMDB project
type Project struct {
	ProjectID            string    `db:"project_id"`
	ProjectCode          string    `db:"project_code"`
	ProjectName          string    `db:"project_name"`
	OwnerTeamID          string    `db:"owner_team_id"`
	MonthlyGPUQuotaHours float64   `db:"monthly_gpu_quota_hours"`
	CreatedAt            time.Time `db:"created_at"`
}

// TableName returns the database table name for Project
func (Project) TableName() string {
	return "cmdb_projects"
}

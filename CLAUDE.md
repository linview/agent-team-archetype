# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a **prototype project (原型工程)** that demonstrates AI-native project architecture patterns. It is **NOT** a production application.

**Key Characteristics**:
- ✅ Reference template for architecture patterns
- ✅ Framework code (interface definitions, data models)
- ✅ Documentation of best practices
- ❌ No business logic implementations
- ❌ Not runnable as a production service

**Usage**: Copy this project structure as a starting point for new projects, then implement the interfaces defined in `internal/dao/interfaces.go`.

## Development Commands

### Go Development

```bash
# Run unit tests
make test
go test -v ./internal/...

# Format code
make fmt

# Run linter
make lint

# Build Linux binary
make build
# Or explicitly:
make build-linux

# Run service locally
make run
# Or:
go run main.go -f etc/config/config.yaml

# Install development tools
make tools
```

### Python Testing

```bash
# Activate virtual environment (if using uv)
source .venv/bin/activate

# Run API tests
pytest tests/api/ -v

# Run SIT tests (requires local K8s environment)
pytest tests/sit/ -v

# Run UAT tests
pytest tests/uat/ -v

# Generate HTML test report
pytest tests/ -v --html=test_reports/test_report.html
```

### Docker & Deployment

```bash
# Build Docker image
make docker

# Run local development environment
cd deploy/docker && docker-compose up -d

# Deploy to test environment (K8s)
./deploy/scripts/helm-upgrade.sh test snapshot-mr-30

# Deploy to production (K8s)
./deploy/scripts/helm-upgrade.sh prod V0.1-20260428153000-a1b2c3d
```

## Architecture Overview

### Layered Architecture

```
HTTP Request
    ↓
Handler (internal/handler/)  - HTTP request/response handling
    ↓
Logic (internal/logic/)      - Business logic
    ↓
DAO (internal/dao/)          - Data access abstraction (interface-based)
    ↓
Model (internal/model/)      - Data models (GORM entities)
```

**Key Principles**:
- **Interface-based DAO layer**: All data access goes through interfaces defined in `internal/dao/interfaces.go`
- **Dependency injection**: Components receive dependencies through constructors
- **Separation of concerns**: Each layer has distinct responsibilities

### Technology Stack

**Backend**:
- Go 1.24+
- go-zero framework (REST API)
- GORM (ORM)
- PostgreSQL (database)
- Kubernetes client-go (K8s integration)

**Testing**:
- Go testing (unit tests)
- Pytest (integration/SIT/UAT tests)
- K8s kind/minikube (SIT environment)

**DevOps**:
- Docker (containerization)
- Kubernetes (orchestration)
- Helm Charts (deployment)
- GitLab CI (CI/CD)

## Directory Structure

```
internal/
├── config/          # Configuration structure definitions
├── dao/             # Data access layer interfaces (no implementations)
├── handler/         # HTTP handlers (empty - only .gitkeep)
├── logic/           # Business logic (empty - only .gitkeep)
├── model/           # Data models (GORM entities)
├── middleware/      # HTTP middleware (empty - only .gitkeep)
├── pkg/             # Utility packages (empty - only .gitkeep)
├── svc/             # Service context (empty - only .gitkeep)
└── types/           # Common type definitions

tests/
├── conftest.py      # Main pytest configuration
├── api/             # Contract tests (API level)
├── sit/             # System integration tests
├── uat/             # User acceptance tests
└── regression/      # Regression tests

docs/
├── design/          # Architecture design documents
├── guides/          # Usage guides
└── scrum/           # Project management docs

deploy/
├── docker/          # Docker Compose (local development)
└── k8s/             # Kubernetes Helm Charts

etc/
└── config/          # Configuration files (framework only)
```

## Testing Strategy

This project uses a **four-layer testing pyramid**:

| Layer | Type       | Location            | Purpose                          |
|-------|------------|---------------------|----------------------------------|
| UT    | Unit tests | `internal/**/*_test.go` | Function-level testing          |
| API   | Contract   | `tests/api/`        | API contract validation         |
| SIT   | Integration| `tests/sit/`        | Business flow validation        |
| UAT   | Acceptance| `tests/uat/`        | User scenario validation        |

**Coverage Goals**:
- UT: ≥ 50%
- API: 100%
- SIT: ≥ 90%
- UAT: ≥ 85%

**Important**: Unit tests (`*_test.go`) are stored alongside code in `internal/`, while integration/SIT/UAT tests are in `tests/` directory.

## Configuration Management

### Configuration File Locations

**Runtime Configuration** (mutable):
- `etc/config-local.yaml` - Local development
- `etc/config-test.yaml` - Test environment
- `etc/config-prod.yaml` - Production environment

**Deployment Configuration** (immutable):
- `deploy/docker/docker-compose.yml` - Local development
- `deploy/k8s/helm/project-template/values-test.yaml` - Test environment
- `deploy/k8s/helm/project-template/values-prod.yaml` - Production environment

### Config Loading Priority

1. Command-line flag: `-f /path/to/config.yaml`
2. Environment variable: `CONFIG_FILE=/path/to/config.yaml`
3. Default: `etc/config/config.yaml`

## Key Design Documents

When implementing features based on this prototype, reference these documents:

- `docs/design/service_layer_architecture_v4.2.md` - Service layer design
- `docs/design/cmdb_design_v4.0.md` - Data layer design
- `docs/design/api_design_v1.3.md` - API design
- `GUIDE.md` - Engineering practices (testing strategy, deployment pipeline)

## When Working with This Codebase

### For Learning Architecture
- Read interface definitions in `internal/dao/interfaces.go`
- Study data models in `internal/model/`
- Review design documents in `docs/design/`

### For Creating New Projects
1. Copy this project structure
2. Implement DAO interfaces from `internal/dao/interfaces.go`
3. Add handlers in `internal/handler/`
4. Add business logic in `internal/logic/`
5. Fill in configuration values in `etc/config/`
6. Write tests following the four-layer strategy

### Important Constraints

- **DO NOT** add business logic implementations to this prototype project
- **DO NOT** modify framework code in `internal/` without understanding the architecture
- **DO** use this as a reference for understanding AI-native project patterns
- **DO** copy the structure when creating new projects

## Team Skills

The `.claude/skills/` directory contains team skill definitions for various roles:
- `arch/` - Architecture skills
- `commit/` - Git commit and MR creation
- `dev/` - Development workflow
- `devops/` - DevOps operations
- `qa/` - Testing strategy
- `pm/` - Project management

Use these skills with the `/skill` command when working on specific tasks.

## Version History

- **v2.0** (2026-04-28): De-implementation refactor - removed all business logic, kept only framework
- **v1.0** (2026-02-04): Initial version

# Monitoring Directory - Organized Structure

## 📁 Directory Structure

```
backend/monitoring/
├── interfaces/          # Abstractions (SOLID - DIP)
│   ├── metrics_interface.py
│   ├── logging_interface.py
│   └── health_interface.py
│
├── collectors/          # Metric collectors (SOLID - SRP)
│   ├── system_metrics_collector.py
│   ├── application_metrics_collector.py
│   └── ai_metrics_collector.py
│
├── exporters/           # Metric exporters (SOLID - OCP)
│   └── prometheus_exporter.py
│
├── loggers/             # Logging implementations (SOLID - LSP)
│   └── structured_logger.py
│
├── health/              # Health check components
│   └── health_checker.py
│
├── services/            # Business logic (Facade pattern)
│   └── monitoring_service.py
│
├── middleware/          # FastAPI middleware
│   └── metrics_middleware.py
│
├── config/              # Runtime configuration
│   └── logging_setup.py
│
├── configs/             # Static configuration files
│   ├── prometheus.yml
│   ├── alert_rules.yml
│   ├── alertmanager.yml
│   ├── grafana_dashboard.json
│   ├── grafana_datasources.yml
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── scripts/             # Utility scripts
│   ├── install.sh
│   ├── start.sh
│   ├── stop.sh
│   └── load_test.sh
│
├── docs/                # Documentation
│   ├── README.md
│   ├── SETUP_GUIDE.md
│   ├── QUICK_REFERENCE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── SOLID_ARCHITECTURE.md
│
├── deprecated/          # Old files (no longer used)
│   ├── logging_config.py
│   ├── metrics.py
│   └── alerts.py
│
├── __init__.py          # Public API
└── legacy_adapter.py    # Backward compatibility
```

## 🎯 Purpose of Each Directory

### **Core Components (SOLID Architecture)**

#### `interfaces/`
- **Purpose**: Define abstractions following Dependency Inversion Principle
- **Files**: 
  - `metrics_interface.py` - IMetricsCollector, IMetricsExporter
  - `logging_interface.py` - ILogger, IStructuredLogger
  - `health_interface.py` - IHealthChecker
- **Used by**: All other components depend on these abstractions

#### `collectors/`
- **Purpose**: Collect specific types of metrics (Single Responsibility)
- **Files**:
  - `system_metrics_collector.py` - CPU, memory, disk metrics
  - `application_metrics_collector.py` - HTTP requests, errors
  - `ai_metrics_collector.py` - AI inference, tokens
- **Used by**: MonitoringService, PrometheusExporter

#### `exporters/`
- **Purpose**: Export metrics to external systems (Open/Closed)
- **Files**:
  - `prometheus_exporter.py` - Prometheus format exporter
- **Used by**: MonitoringService, /metrics endpoint

#### `loggers/`
- **Purpose**: Logging implementations (Liskov Substitution)
- **Files**:
  - `structured_logger.py` - Structured logging with JSON support
- **Used by**: MonitoringService

#### `health/`
- **Purpose**: Health check implementations
- **Files**:
  - `health_checker.py` - Component health checkers
- **Used by**: MonitoringService, /api/health endpoint

#### `services/`
- **Purpose**: Business logic and facade
- **Files**:
  - `monitoring_service.py` - Unified monitoring interface (Facade pattern)
- **Used by**: app.py, all endpoints

#### `middleware/`
- **Purpose**: FastAPI middleware
- **Files**:
  - `metrics_middleware.py` - HTTP request tracking
- **Used by**: app.py (FastAPI application)

#### `config/`
- **Purpose**: Runtime configuration
- **Files**:
  - `logging_setup.py` - Initialize logging system
- **Used by**: app.py on startup

### **Supporting Components**

#### `configs/`
- **Purpose**: Static configuration files
- **Contents**:
  - `prometheus.yml` - Prometheus configuration
  - `alert_rules.yml` - Alert definitions
  - `alertmanager.yml` - Alert routing
  - `grafana_dashboard.json` - Pre-built Grafana dashboard
  - `grafana_datasources.yml` - Grafana datasource config
  - `docker-compose.yml` - Container orchestration
  - `requirements.txt` - Python dependencies
- **Usage**: Reference these when setting up monitoring tools

#### `scripts/`
- **Purpose**: Automation and utility scripts
- **Contents**:
  - `install.sh` - Install Prometheus & Grafana
  - `start.sh` - Start all monitoring services
  - `stop.sh` - Stop all monitoring services
  - `load_test.sh` - Generate test traffic
- **Usage**: Run from command line for setup/operation

#### `docs/`
- **Purpose**: Comprehensive documentation
- **Contents**:
  - `README.md` - Overview and quick start
  - `SETUP_GUIDE.md` - Detailed setup instructions
  - `QUICK_REFERENCE.md` - Commands and queries
  - `IMPLEMENTATION_SUMMARY.md` - Feature details
  - `SOLID_ARCHITECTURE.md` - Architecture explanation
- **Usage**: Read for understanding and reference

#### `deprecated/`
- **Purpose**: Old files kept for reference (not used in code)
- **Contents**:
  - `logging_config.py` - Old logging (replaced by config/logging_setup.py)
  - `metrics.py` - Old metrics (replaced by SOLID collectors/exporters)
  - `alerts.py` - Old alerts (replaced by configs/alert_rules.yml)
- **Status**: ⚠️ NOT USED - Can be deleted if needed

### **Root Files**

#### `__init__.py`
- **Purpose**: Public API and exports
- **Exports**: 
  - `get_monitoring_service()` - Main entry point
  - Interfaces, collectors, exporters
  - Legacy adapter functions
- **Usage**: `from backend.monitoring import get_monitoring_service`

#### `legacy_adapter.py`
- **Purpose**: Backward compatibility (Adapter pattern)
- **Provides**: Old API functions that delegate to new SOLID architecture
- **Usage**: Allows old code to work without changes

## 🚀 Quick Start

### Use the Monitoring System

```python
from backend.monitoring import get_monitoring_service

monitoring = get_monitoring_service()
monitoring.record_ai_inference(duration=2.5, success=True)
monitoring.log_info("Processing started", logger_type='ai')
```

### Run Scripts

```bash
# Install monitoring tools
cd backend/monitoring/scripts
./install.sh

# Start monitoring
./start.sh

# Stop monitoring
./stop.sh

# Run load test
./load_test.sh
```

### Configuration

All config files are in `configs/`:
- Edit `configs/prometheus.yml` for Prometheus settings
- Edit `configs/alert_rules.yml` for alert thresholds
- Import `configs/grafana_dashboard.json` into Grafana

### Documentation

All docs are in `docs/`:
- Start with `docs/README.md`
- Read `docs/SOLID_ARCHITECTURE.md` for architecture details
- Check `docs/QUICK_REFERENCE.md` for commands

## 🗑️ Files That Can Be Deleted

The `deprecated/` folder contains old files that are **NO LONGER USED**:
- `deprecated/logging_config.py` - Replaced by `config/logging_setup.py`
- `deprecated/metrics.py` - Replaced by SOLID collectors and exporters
- `deprecated/alerts.py` - Replaced by `configs/alert_rules.yml`

**You can safely delete the entire `deprecated/` folder if you want.**

## 📊 Why This Structure?

### Benefits

✅ **Clear Organization** - Each folder has a specific purpose
✅ **SOLID Principles** - Architecture follows best practices
✅ **Easy to Navigate** - Find what you need quickly
✅ **Separation of Concerns** - Code, config, docs, scripts separated
✅ **Maintainable** - Easy to add/modify/remove components
✅ **Professional** - Enterprise-grade structure

### Design Decisions

1. **`interfaces/`** - Abstractions enable dependency injection
2. **`collectors/`** - Each collector has one responsibility
3. **`exporters/`** - Can add new exporters without changing collectors
4. **`services/`** - Facade simplifies complex subsystem
5. **`configs/`** - Static configs separated from code
6. **`scripts/`** - Automation separated from application code
7. **`docs/`** - Documentation easily accessible
8. **`deprecated/`** - Old files isolated, can be deleted

## 🔍 How to Find Things

| I want to... | Look in... |
|--------------|------------|
| Add a new metric | `collectors/` - create new collector |
| Change alert thresholds | `configs/alert_rules.yml` |
| Modify logging | `loggers/structured_logger.py` |
| Update Prometheus config | `configs/prometheus.yml` |
| Read documentation | `docs/` folder |
| Run scripts | `scripts/` folder |
| Understand architecture | `docs/SOLID_ARCHITECTURE.md` |
| Use monitoring in code | Import from `__init__.py` |

## 📚 Next Steps

1. **Read docs**: Start with `docs/README.md`
2. **Review configs**: Check `configs/` for settings
3. **Run scripts**: Use `scripts/` to start monitoring
4. **Delete deprecated**: Remove `deprecated/` folder (optional)
5. **Use in code**: Import `get_monitoring_service()`

---

**Status**: ✅ Fully Organized and Ready to Use  
**Date**: November 12, 2025


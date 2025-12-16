# Choreo AI Assistant - Monitoring Quick Reference

## 🎯 Run Prometheus + Grafana Together

### **Option 1: Quick Start Script (Recommended)**
```bash
cd backend/monitoring/scripts
./start_monitoring.sh
```

This will start both Prometheus and Grafana together automatically!

### **Option 2: Manual Start**
```bash
# Start Grafana (if not running)
sudo systemctl start grafana-server

# Start Prometheus in background
cd backend/monitoring
nohup prometheus --config.file=configs/prometheus.yml --storage.tsdb.path=prometheus_data > logs/prometheus.log 2>&1 &
```

### **Option 3: Docker (Easiest)**
```bash
cd backend/monitoring/configs
docker-compose up -d
```

### **Check Status**
```bash
# Check both services
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana

# View processes
ps aux | grep -E "prometheus|grafana"
```

### **Stop Both Services**
```bash
cd backend/monitoring/scripts
./stop_monitoring.sh
```

## 🚀 Quick Start Commands

### Start Everything (All Services)
```bash
cd backend/monitoring
./start.sh
```

### Stop Everything
```bash
cd backend/monitoring
./stop.sh
```

### Install Monitoring Tools
```bash
cd backend/monitoring
./install.sh
```

### Run Load Test
```bash
cd backend/monitoring
./load_test.sh
```

## 📊 Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| FastAPI | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Metrics | http://localhost:8000/metrics | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |

## 🔍 Common Prometheus Queries

```promql
# Request rate
rate(http_requests_total[5m])

# Response time (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(errors_total[5m])

# Active requests
http_requests_active

# CPU usage
cpu_usage_percent

# Memory usage
memory_usage_percent

# AI inference time
histogram_quantile(0.95, rate(ai_inference_duration_seconds_bucket[5m]))

# Vector search performance
histogram_quantile(0.95, rate(vector_search_duration_seconds_bucket[5m]))
```

## 📝 Useful Log Commands

```bash
# Follow all logs
tail -f ../logs/app.log

# Follow errors only
tail -f ../logs/error.log

# Follow AI operations
tail -f ../logs/ai.log

# Search for errors
grep ERROR ../logs/app.log

# Count requests
grep "AI request received" ../logs/ai.log | wc -l
```

## 🎯 Key Metrics to Monitor

### Performance
- Response time (should be <2s for 95th percentile)
- AI inference time (should be <5s)
- Vector search time (should be <1s)

### Reliability
- Error rate (should be <5%)
- Health check status (should always be 1)
- Active requests (watch for buildup)

### Resources
- CPU usage (alert at >80%)
- Memory usage (alert at >85%, critical at >95%)
- Disk usage (alert at >80%)

## 🔔 Alert Thresholds

| Alert | Threshold | Duration |
|-------|-----------|----------|
| High Response Time | >2s (P95) | 2 min |
| High Error Rate | >5% | 2 min |
| High CPU | >80% | 5 min |
| High Memory | >85% | 5 min |
| Critical Memory | >95% | 2 min |
| Slow AI Inference | >5s (P95) | 3 min |
| Service Down | Health check fails | 1 min |

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check if ports are available
lsof -i :8000 :9090 :3000

# Kill existing processes
./stop.sh

# Start again
./start.sh
```

### No Metrics in Grafana
```bash
# Verify metrics endpoint
curl http://localhost:8000/metrics

# Check Prometheus targets
# Open: http://localhost:9090/targets

# Restart services
./stop.sh && ./start.sh
```

### High Memory Usage
```bash
# Check what's using memory
ps aux --sort=-%mem | head

# Clear Prometheus data (if needed)
rm -rf prometheus_data/*
```

## 📦 Docker Commands

```bash
# Start with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `prometheus.yml` | Prometheus configuration |
| `alert_rules.yml` | Alert definitions |
| `grafana_dashboard.json` | Dashboard template |
| `alertmanager.yml` | Alert routing |
| `docker-compose.yml` | Container orchestration |

## 📱 Frontend Integration

The monitoring icon appears in the bottom-right corner of the DevChoreo interface:
- Click it to open Grafana dashboard in a new tab
- Icon shows activity/monitoring status
- Blue color indicates monitoring is available

---

For detailed setup instructions, see [SETUP_GUIDE.md](./SETUP_GUIDE.md)


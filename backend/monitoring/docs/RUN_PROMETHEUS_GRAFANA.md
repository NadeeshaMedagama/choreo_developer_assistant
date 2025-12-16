# 🎯 Running Prometheus + Grafana Together

This guide shows you exactly how to run Prometheus and Grafana together for complete monitoring.

## ✅ Quick Start (Recommended)

### Single Command to Start Both

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/monitoring/scripts"
./start_monitoring.sh
```

This script will:
1. ✅ Check if Grafana is running, start it if needed
2. ✅ Start Prometheus in background mode
3. ✅ Verify both services are healthy
4. ✅ Show you the access URLs

### Stop Both Services

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/monitoring/scripts"
./stop_monitoring.sh
```

## 📋 Step-by-Step Guide

### Option 1: Using the Startup Script

```bash
# Navigate to scripts directory
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/monitoring/scripts"

# Start both services
./start_monitoring.sh

# Output will show:
# ✅ Grafana is already running
# ✅ Prometheus started
# ✅ Both services are healthy

# Access the services:
# • Prometheus: http://localhost:9090
# • Grafana: http://localhost:3000 (admin/admin)
```

### Option 2: Manual Start

```bash
# 1. Start Grafana (if not already running)
sudo systemctl start grafana-server

# 2. Start Prometheus
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/monitoring"
nohup prometheus \
    --config.file=configs/prometheus.yml \
    --storage.tsdb.path=prometheus_data \
    --web.listen-address=":9090" \
    > logs/prometheus.log 2>&1 &

# 3. Verify both are running
curl http://localhost:9090/-/healthy  # Should return: Prometheus Server is Healthy.
curl http://localhost:3000/api/health # Should return health status
```

### Option 3: Using Docker Compose

```bash
# Navigate to monitoring directory
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/monitoring/configs"

# Start both services with Docker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔍 Verify Services Are Running

```bash
# Check Prometheus
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3000/api/health

# Check processes
ps aux | grep -E "prometheus|grafana"

# Check ports
netstat -tlnp | grep -E "9090|3000"
```

## 📊 Complete Setup Flow

### 1. Start Monitoring Stack

```bash
cd backend/monitoring/scripts
./start_monitoring.sh
```

### 2. Start Your Application

**Terminal 1 - Backend:**
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/frontend"
npm run dev
```

### 3. Configure Grafana (First Time Only)

1. Open Grafana: http://localhost:3000
2. Login with: `admin` / `admin`
3. Go to **Configuration** → **Data Sources**
4. Click **Add data source**
5. Select **Prometheus**
6. Enter URL: `http://localhost:9090`
7. Click **Save & Test** (should show green checkmark)

### 4. Import Dashboard

1. Go to **Dashboards** → **Import**
2. Click **Upload JSON file**
3. Select: `backend/monitoring/configs/grafana_dashboard.json`
4. Choose Prometheus datasource
5. Click **Import**

### 5. Access Monitoring

Open DevChoreo (http://localhost:5173) and click the blue monitoring icon (bottom-right):
- 📊 **Metrics** → View raw Prometheus metrics
- 💚 **Health Check** → View system health
- 🔍 **Prometheus** → Prometheus UI ✅ Working!
- 📈 **Grafana** → Beautiful dashboards ✅ Working!

## 🎯 Common Tasks

### Check What's Running

```bash
# Quick check
curl -s http://localhost:9090/-/healthy && echo "✅ Prometheus OK"
curl -s http://localhost:3000/api/health && echo "✅ Grafana OK"

# Detailed check
systemctl status grafana-server
ps aux | grep prometheus
```

### View Logs

```bash
# Prometheus logs
tail -f backend/monitoring/logs/prometheus.log

# Grafana logs
sudo journalctl -u grafana-server -f

# Backend logs
tail -f logs/app.log
```

### Restart Services

```bash
# Restart both
cd backend/monitoring/scripts
./stop_monitoring.sh
./start_monitoring.sh

# Or restart individually
sudo systemctl restart grafana-server
pkill prometheus && ./start_monitoring.sh
```

## 🛠️ Troubleshooting

### "Address already in use" Error

```bash
# Port 9090 is in use - stop existing Prometheus
pkill prometheus

# Port 3000 is in use - check what's using it
lsof -i :3000
sudo systemctl stop grafana-server

# Then start again
./start_monitoring.sh
```

### Grafana Not Starting

```bash
# Check if installed
which grafana-server

# Check service status
sudo systemctl status grafana-server

# If not installed, see GRAFANA_INSTALLATION.md
```

### Prometheus Not Starting

```bash
# Check config file
promtool check config backend/monitoring/configs/prometheus.yml

# View logs for errors
tail -50 backend/monitoring/logs/prometheus.log

# Check port availability
lsof -i :9090
```

### Can't Connect Grafana to Prometheus

1. Make sure Prometheus is running: `curl http://localhost:9090/-/healthy`
2. In Grafana datasource, use: `http://localhost:9090` (not https)
3. Click "Save & Test" - should show "Data source is working"
4. If fails, check both services are running

## 📦 Services Status Summary

| Service | Default Port | Status Check | Config Location |
|---------|-------------|--------------|-----------------|
| **Grafana** | 3000 | `systemctl status grafana-server` | `/etc/grafana/grafana.ini` |
| **Prometheus** | 9090 | `curl localhost:9090/-/healthy` | `configs/prometheus.yml` |
| **Backend** | 8000 | `curl localhost:8000/api/health` | `backend/.env` |
| **Frontend** | 5173 | Open browser | `frontend/` |

## 🚀 Production Deployment

For production, consider using systemd services:

### Create Prometheus Service

```bash
sudo nano /etc/systemd/system/prometheus.service
```

Add:
```ini
[Unit]
Description=Prometheus Monitoring
After=network.target

[Service]
Type=simple
User=nadeeshame
ExecStart=/usr/local/bin/prometheus \
    --config.file=/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/monitoring/configs/prometheus.yml \
    --storage.tsdb.path=/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant/backend/monitoring/prometheus_data
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus
sudo systemctl start grafana-server
```

Now both services start automatically on boot!

## 📚 Additional Resources

- **Quick Reference**: `backend/monitoring/docs/QUICK_REFERENCE.md`
- **Setup Guide**: `backend/monitoring/docs/SETUP_GUIDE.md`
- **Prometheus Docs**: https://prometheus.io/docs/
- **Grafana Docs**: https://grafana.com/docs/

---

## ✅ Summary

**To run Prometheus + Grafana together:**

```bash
cd backend/monitoring/scripts
./start_monitoring.sh
```

**That's it!** Both services will start and you can access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

**To stop:**
```bash
./stop_monitoring.sh
```

🎉 **Happy Monitoring!**


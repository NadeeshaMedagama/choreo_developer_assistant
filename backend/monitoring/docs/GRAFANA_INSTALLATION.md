# Installing Grafana for Full Monitoring

## Problem

When you click the monitoring icon and select "Grafana", you see:
```
ERR_CONNECTION_REFUSED
This site can't be reached localhost refused to connect
```

This means **Grafana is not installed or not running**.

## Quick Solution (Works Immediately)

The monitoring button now shows a **menu with multiple options**:

1. **📊 Metrics** - Always available (shows raw Prometheus metrics)
2. **💚 Health Check** - Always available (shows system health)
3. **🔍 Prometheus** - Only if Prometheus is installed and running
4. **📈 Grafana** - Only if Grafana is installed and running

**You can use Metrics and Health Check right now without installing anything!**

## How to Use Monitoring Without Grafana

1. Start the backend:
   ```bash
   python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Click the **blue monitoring icon** (Activity icon) in the bottom-right corner

4. Select:
   - **📊 Metrics** - View raw metrics data
   - **💚 Health Check** - Check if services are healthy

## Installing Grafana (Optional - For Beautiful Dashboards)

### On Ubuntu/Debian

```bash
# Install dependencies (including musl which is required)
sudo apt-get install -y adduser libfontconfig1 musl

# Download Grafana
cd /tmp
wget https://dl.grafana.com/oss/release/grafana_10.2.0_amd64.deb

# Install
sudo dpkg -i grafana_10.2.0_amd64.deb

# If you get dependency errors, install musl and reconfigure:
# sudo apt-get install -y musl
# sudo dpkg --configure grafana

# Start Grafana
sudo systemctl daemon-reload
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Check status
sudo systemctl status grafana-server

# Verify it's running
curl -I http://localhost:3000
```

### On macOS

```bash
# Using Homebrew
brew install grafana

# Start Grafana
brew services start grafana
```

### Using Docker (Any OS)

```bash
cd backend/monitoring/configs

# Start with Docker Compose (includes Grafana + Prometheus)
docker-compose up -d

# Check if running
docker ps
```

## After Installing Grafana

1. Open Grafana: http://localhost:3000
2. Login: `admin` / `admin` (change password when prompted)
3. Add Prometheus data source:
   - Go to **Configuration** → **Data Sources**
   - Click **Add data source**
   - Select **Prometheus**
   - URL: `http://localhost:9090`
   - Click **Save & Test**
4. Import dashboard:
   - Go to **Dashboards** → **Import**
   - Upload: `backend/monitoring/configs/grafana_dashboard.json`
   - Select Prometheus datasource
   - Click **Import**

## Installing Prometheus (Optional - For Metrics Storage)

### On Ubuntu/Debian

```bash
cd /tmp
PROMETHEUS_VERSION="2.47.0"
wget "https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz"
tar xzf "prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz"
cd "prometheus-${PROMETHEUS_VERSION}.linux-amd64"
sudo cp prometheus promtool /usr/local/bin/
sudo chmod +x /usr/local/bin/prometheus /usr/local/bin/promtool
```

### On macOS

```bash
brew install prometheus
```

### Start Prometheus

```bash
cd backend/monitoring/configs
prometheus --config.file=prometheus.yml --storage.tsdb.path=../prometheus_data
```

## Automated Installation

Use the provided script:

```bash
cd backend/monitoring/scripts
./install.sh
```

This will:
- ✅ Install Python dependencies
- ✅ Download and install Prometheus (if on Linux)
- ✅ Download and install Grafana (if on Linux)
- ✅ Set up all necessary directories

## Start Everything

### Option 1: Use the start script

```bash
cd backend/monitoring/scripts
./start.sh
```

### Option 2: Manual start

Terminal 1 - Backend:
```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Terminal 3 - Prometheus (if installed):
```bash
cd backend/monitoring/configs
prometheus --config.file=prometheus.yml --storage.tsdb.path=../prometheus_data
```

Terminal 4 - Grafana (if installed):
```bash
sudo systemctl start grafana-server  # Linux
# OR
brew services start grafana  # macOS
```

### Option 3: Docker (easiest)

```bash
cd backend/monitoring/configs
docker-compose up -d
```

This starts everything: Backend, Prometheus, and Grafana!

## Verification

After installation, check if services are running:

```bash
# Check Prometheus
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3000/api/health

# Check Backend
curl http://localhost:8000/api/health
```

## Summary

### Works Without Installation
- ✅ **Metrics endpoint** - http://localhost:8000/metrics
- ✅ **Health check** - http://localhost:8000/api/health
- ✅ **Monitoring button** → Select "Metrics" or "Health Check"

### Requires Installation
- ❌ **Grafana** - Beautiful dashboards (install optional)
- ❌ **Prometheus** - Metrics storage and querying (install optional)

### What to Do Now

**Option A**: Just use Metrics endpoint (no installation needed)
```bash
# Start backend and frontend
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
cd frontend && npm run dev

# Click monitoring icon → Select "📊 Metrics"
```

**Option B**: Install Grafana for beautiful dashboards
```bash
# Follow installation instructions above
# Then click monitoring icon → Select "📈 Grafana"
```

**Option C**: Use Docker for everything
```bash
cd backend/monitoring/configs
docker-compose up -d
```

---

**The monitoring button now works perfectly even without Grafana installed!** 🎉


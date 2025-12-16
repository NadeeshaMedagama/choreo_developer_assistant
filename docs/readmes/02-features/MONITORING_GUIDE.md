# 🔍 Monitoring System Guide

This project has **TWO monitoring setups** for different environments:

## 📦 1. Local Development Monitoring (`backend/monitoring/`)

**For local development** using Prometheus + Grafana on your machine.

### Quick Start

```bash
# Navigate to monitoring scripts
cd backend/monitoring/scripts

# Start Prometheus + Grafana
./start_monitoring.sh
```

### Access Dashboards

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Monitor Key Metrics

In Prometheus (http://localhost:9090), use these queries:

```promql
# Skipped Scrapes
prometheus_target_scrapes_exceeded_sample_limit_total

# Tardy Scrapes (late scrapes)
prometheus_target_scrapes_sample_out_of_order_total

# Reload Failures
prometheus_config_last_reload_successful == 0

# Sample Scrape Duration
prometheus_target_interval_length_seconds

# Application Metrics (if backend is running)
http_requests_total
http_request_duration_seconds
```

### View Logs

```bash
# Prometheus logs
tail -f backend/monitoring/logs/prometheus.log

# Grafana logs (if running as service)
sudo journalctl -u grafana-server -f
```

### Stop Monitoring

```bash
cd backend/monitoring/scripts
./stop_monitoring.sh
```

---

## ☸️ 2. Kubernetes Monitoring (`backend/k8s/base/monitoring/`)

**For Kubernetes deployments** using ServiceMonitor (works with Prometheus Operator).

### Prerequisites

Install Prometheus + Grafana in your Kubernetes cluster:

```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

### Deploy ServiceMonitor

```bash
# Apply the ServiceMonitor to your cluster
kubectl apply -f backend/k8s/base/monitoring/prometheus-servicemonitor.yaml

# Verify it's created
kubectl get servicemonitor -n choreo-ai-assistant
```

### Access Dashboards in Kubernetes

```bash
# Get Grafana admin password
kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode
echo

# Port-forward Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9091:9090 &

# Port-forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &
```

Then access:
- **Prometheus**: http://localhost:9091
- **Grafana**: http://localhost:3000

### Check Monitoring Status

```bash
# Check monitoring pods
kubectl get pods -n monitoring

# Check if backend is being scraped
kubectl get servicemonitor -n choreo-ai-assistant

# View Prometheus targets
# Open http://localhost:9091/targets
```

---

## 📊 Key Differences

| Feature | Local Monitoring | Kubernetes Monitoring |
|---------|------------------|----------------------|
| **Location** | `backend/monitoring/` | `backend/k8s/base/monitoring/` |
| **Environment** | Development (localhost) | Production/Staging (K8s) |
| **Prometheus** | Standalone binary | Prometheus Operator |
| **Configuration** | `configs/prometheus.yml` | ServiceMonitor CRD |
| **Scrape Targets** | localhost:8000 | K8s service endpoints |
| **Start Command** | `./start_monitoring.sh` | `kubectl apply -f ...` |

---

## 🎯 Recommended Workflow

### For Local Development:
1. Start monitoring: `cd backend/monitoring/scripts && ./start_monitoring.sh`
2. Start backend: `python -m uvicorn backend.app:app --reload`
3. Open Prometheus: http://localhost:9090
4. Open Grafana: http://localhost:3000

### For Kubernetes Deployment:
1. Install Prometheus stack via Helm (one-time setup)
2. Deploy your app: `cd backend/k8s && make deploy`
3. Apply ServiceMonitor: `kubectl apply -f base/monitoring/prometheus-servicemonitor.yaml`
4. Port-forward and access dashboards

---

## 🔧 Configuration Files

### Local Monitoring
- **Prometheus Config**: `backend/monitoring/configs/prometheus.yml`
- **Alert Rules**: `backend/monitoring/configs/alert_rules.yml`
- **Grafana Dashboard**: `backend/monitoring/configs/grafana_dashboard.json`
- **Start Script**: `backend/monitoring/scripts/start_monitoring.sh`

### Kubernetes Monitoring
- **ServiceMonitor**: `backend/k8s/base/monitoring/prometheus-servicemonitor.yaml`
- **Deployment**: `backend/k8s/base/deployments/backend-deployment.yaml`
- **Service**: `backend/k8s/base/services/backend-service.yaml`

---

## 📝 Metrics Tracked

Both setups track these metrics (exposed by the backend at `/metrics`):

- **HTTP Requests**: Total requests, response times, status codes
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Active connections, request queue
- **AI Metrics**: Model inference time, token usage
- **Custom Business Metrics**: User queries, RAG operations

---

## 🛑 Troubleshooting

### Local Monitoring Issues

**Prometheus not starting?**
```bash
# Check if port 9090 is already in use
sudo lsof -i :9090

# Kill existing Prometheus
pkill -f prometheus

# Restart
cd backend/monitoring/scripts && ./start_monitoring.sh
```

**Backend metrics not showing?**
```bash
# Verify backend is running and exposing metrics
curl http://localhost:8000/metrics

# Check Prometheus targets
# Open http://localhost:9090/targets
```

### Kubernetes Monitoring Issues

**ServiceMonitor not discovered?**
```bash
# Check if ServiceMonitor exists
kubectl get servicemonitor -n choreo-ai-assistant

# Check Prometheus operator logs
kubectl logs -n monitoring -l app.kubernetes.io/name=prometheus-operator

# Verify service labels match ServiceMonitor selector
kubectl get svc -n choreo-ai-assistant -o yaml
```

**No metrics in Prometheus?**
```bash
# Check if backend pods are running
kubectl get pods -n choreo-ai-assistant

# Verify metrics endpoint
kubectl exec -n choreo-ai-assistant <pod-name> -- curl localhost:8000/metrics
```

---

## 📚 Additional Resources

- **Monitoring README**: `backend/monitoring/README.md`
- **Quick Reference**: `backend/monitoring/docs/QUICK_REFERENCE.md`
- **K8s Deployment Guide**: `backend/k8s/docs/DEPLOYMENT_GUIDE.md`
- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/


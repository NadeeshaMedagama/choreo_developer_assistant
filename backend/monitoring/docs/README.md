# Choreo AI Assistant Monitoring

This directory contains the monitoring infrastructure for the Choreo AI Assistant, including Prometheus metrics, Grafana dashboards, and alerting configurations.

## 📊 Components

- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization and dashboarding
- **Custom Metrics**: Application-specific metrics tracking
- **Alerting**: Alert rules for critical conditions
- **Logging**: Structured logging configuration

## 🚀 Quick Start

### Local Development

1. **Install Dependencies** (if not already installed):
   ```bash
   # Install Prometheus
   wget https://github.com/prometheus/prometheus/releases/download/v2.47.0/prometheus-2.47.0.linux-amd64.tar.gz
   tar xvfz prometheus-2.47.0.linux-amd64.tar.gz
   cd prometheus-2.47.0.linux-amd64
   sudo cp prometheus promtool /usr/local/bin/
   
   # Install Grafana
   sudo apt-get install -y adduser libfontconfig1
   wget https://dl.grafana.com/oss/release/grafana_10.2.0_amd64.deb
   sudo dpkg -i grafana_10.2.0_amd64.deb
   
   # Install Python dependencies
   pip install prometheus-client psutil
   ```

2. **Start All Services**:
   ```bash
   cd backend/monitoring
   chmod +x start.sh stop.sh
   ./start.sh
   ```

3. **Access Services**:
   - FastAPI: http://localhost:8000
   - Metrics Endpoint: http://localhost:8000/metrics
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin)

4. **Stop All Services**:
   ```bash
   ./stop.sh
   ```

### Production/Choreo Deployment

In Choreo environment, only the FastAPI application runs with metrics exposed at `/metrics`. Prometheus and Grafana are typically deployed separately and configured to scrape the metrics endpoint.

## 📈 Metrics Categories

### 1. Infrastructure Metrics
- `cpu_usage_percent`: CPU usage percentage
- `memory_usage_bytes`: Memory usage in bytes
- `memory_usage_percent`: Memory usage percentage
- `disk_usage_bytes`: Disk usage in bytes
- `disk_usage_percent`: Disk usage percentage
- `process_count`: Number of running processes

### 2. Application Metrics
- `http_requests_total`: Total HTTP requests (by method, endpoint, status)
- `http_request_duration_seconds`: Request latency histogram
- `http_requests_active`: Number of active requests
- `errors_total`: Total errors (by type, endpoint)

### 3. AI-Specific Metrics
- `ai_inference_duration_seconds`: AI model inference time
- `ai_requests_total`: Total AI inference requests
- `ai_tokens_total`: Total tokens processed (input/output)
- `ai_payload_size_bytes`: Size of AI payloads

### 4. Vector Database Metrics
- `vector_search_duration_seconds`: Vector search query time
- `vector_searches_total`: Total vector searches
- `vector_search_results`: Number of results returned

### 5. GitHub/Ingestion Metrics
- `github_ingestion_total`: Total GitHub repository ingestions
- `github_ingestion_duration_seconds`: Ingestion duration
- `github_files_processed_total`: Files processed from GitHub

### 6. Health Metrics
- `health_check_status`: Health status of components (1=healthy, 0=unhealthy)

## 🔔 Alert Rules

Alerts are configured for:
- High response time (>2s for 95th percentile)
- High error rate (>5% of requests)
- High CPU usage (>80%)
- High memory usage (>85%, critical at >95%)
- High disk usage (>80%)
- Slow AI inference (>5s)
- AI inference failures
- Slow vector searches
- Service down
- Request rate spikes

## 📊 Grafana Dashboards

### Pre-configured Dashboard: "Choreo AI Assistant - Overview"

The dashboard includes panels for:
1. **Request Rate**: Real-time request rate by endpoint
2. **Response Time**: 95th percentile response time
3. **CPU Usage**: Current CPU usage percentage
4. **Memory Usage**: Current memory usage percentage
5. **AI Inference Time**: AI model performance
6. **Error Rate**: Error trends over time
7. **Vector Search Time**: Database query performance

### Importing the Dashboard

1. Open Grafana (http://localhost:3000)
2. Login with admin/admin
3. Go to Dashboards → Import
4. Upload `grafana_dashboard.json` or paste its contents
5. Select Prometheus as the data source

## 📝 Logging

Logs are stored in the `logs/` directory:
- `app.log`: All application logs
- `error.log`: Errors only
- `ai.log`: AI-specific operations
- `ingestion.log`: Data ingestion operations

Logs can be configured for JSON format for easier parsing:
```python
from backend.monitoring.logging_config import setup_logging
setup_logging(log_level="INFO", enable_json=True)
```

## 🔧 Configuration

### Prometheus Configuration
Edit `prometheus.yml` to:
- Adjust scrape intervals
- Add new targets
- Configure alerting

### Alert Rules
Edit `alert_rules.yml` to:
- Modify thresholds
- Add new alerts
- Change notification settings

## 🧪 Testing

Test the monitoring setup:

```bash
# Check if metrics are being collected
curl http://localhost:8000/metrics

# Check Prometheus targets
# Open http://localhost:9090/targets

# Generate some load
for i in {1..100}; do
  curl -X POST "http://localhost:8000/api/ask?question=test"
done

# Check alerts
# Open http://localhost:9090/alerts
```

## 🌐 Frontend Integration

A monitoring icon is available in the frontend (bottom-right corner) that opens the Grafana dashboard in a new tab.

## 📚 Best Practices

1. **Regular Review**: Review metrics and alerts weekly
2. **Adjust Thresholds**: Fine-tune alert thresholds based on actual usage
3. **Dashboard Customization**: Create custom dashboards for specific use cases
4. **Log Retention**: Configure log rotation to manage disk space
5. **Backup**: Regularly backup Prometheus and Grafana data
6. **Security**: Change default Grafana password immediately
7. **Performance**: Monitor the monitoring system's own resource usage

## 🐛 Troubleshooting

### Metrics not appearing
- Check if FastAPI is running: `curl http://localhost:8000/health`
- Verify metrics endpoint: `curl http://localhost:8000/metrics`
- Check Prometheus targets: http://localhost:9090/targets

### High memory usage
- Reduce Prometheus retention period
- Decrease scrape intervals
- Archive old logs

### Grafana dashboard empty
- Verify Prometheus data source is configured
- Check time range in dashboard
- Ensure metrics are being collected

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review Prometheus targets and alerts
3. Verify service health: http://localhost:8000/api/health


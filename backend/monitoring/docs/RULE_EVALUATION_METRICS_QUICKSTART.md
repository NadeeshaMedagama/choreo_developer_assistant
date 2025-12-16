# Rule Evaluation Metrics - Quick Start Guide

## 🚀 New Metrics Added

Four new metrics have been successfully added to track rule evaluation performance and system status:

1. ✅ **Average Rule Evaluation Duration** - How long rules take to evaluate
2. ✅ **HTTP Request Duration** - How long HTTP requests take
3. ✅ **Rule Evaluator Iterations** - Number of rule evaluation cycles
4. ✅ **Currently Down** - System up/down status

## 📊 Quick Integration

### Basic Usage

```python
from monitoring import get_monitoring_service

monitoring = get_monitoring_service()

# Record rule evaluation
monitoring.record_rule_evaluation(duration_seconds=2.5)

# Record HTTP request duration
monitoring.record_http_request_duration(duration_seconds=1.2)

# Record rule evaluator iteration
monitoring.record_rule_evaluator_iteration(duration_seconds=3.0)

# Set system status
monitoring.set_system_down(True)   # Mark system as down
monitoring.set_system_up()          # Mark system as up

# Check system status
if monitoring.is_system_down():
    print("System is currently down!")

# Get health status
health = monitoring.get_rule_evaluation_health()
print(f"Healthy: {health['healthy']}")
print(f"Avg rule eval: {health['avg_rule_evaluation_duration']}s")
```

## 🎯 Use Cases

### 1. Track Rule Evaluation Performance

```python
import time

def evaluate_rules():
    start = time.time()
    try:
        # Your rule evaluation logic
        process_business_rules()
        
        # Record the duration
        duration = time.time() - start
        monitoring.record_rule_evaluation(duration)
    except Exception as e:
        monitoring.set_system_down(True)
        raise
```

### 2. Monitor HTTP Request Performance

```python
import requests
import time

def make_api_call(url):
    start = time.time()
    try:
        response = requests.get(url)
        duration = time.time() - start
        monitoring.record_http_request_duration(duration)
        return response
    except Exception as e:
        monitoring.set_system_down(True)
        raise
```

### 3. Track Rule Evaluator Iterations

```python
def rule_evaluation_loop():
    iteration = 0
    while True:
        iteration += 1
        start = time.time()
        
        try:
            evaluate_all_rules()
            duration = time.time() - start
            monitoring.record_rule_evaluator_iteration(duration)
            monitoring.set_system_up()
        except Exception as e:
            monitoring.set_system_down(True)
            logging.error(f"Iteration {iteration} failed: {e}")
        
        time.sleep(60)  # Wait before next iteration
```

### 4. System Health Monitoring

```python
def check_system_health():
    health = monitoring.get_rule_evaluation_health()
    
    if not health['healthy']:
        alert_team({
            'message': 'System health degraded',
            'avg_rule_eval': health['avg_rule_evaluation_duration'],
            'avg_http_duration': health['avg_http_request_duration'],
            'system_down': health['system_down']
        })
    
    return health
```

## 📈 View Metrics in Grafana

1. **Open Grafana**: http://localhost:3000 (admin/admin)
2. **Go to Dashboard**: "Choreo AI Assistant - Overview"
3. **Scroll to new panels** at position y=40:
   - **Avg Rule Evaluation Duration** (Gauge)
   - **HTTP Request Duration (Avg)** (Gauge)
   - **Rule Evaluator Iterations** (Time series)
   - **System Status (Currently Down)** (Gauge)

## 🔍 Check Metrics Endpoint

```bash
# View all rule evaluation metrics
curl http://localhost:8000/metrics | grep -E "(rule_evaluation|http_request_duration|rule_evaluator|system_currently_down)"
```

Expected output:
```
rule_evaluation_duration_seconds 2.5
rule_evaluation_duration_avg_seconds 2.1
http_request_duration_last_seconds 1.2
http_request_duration_avg_seconds 1.0
rule_evaluator_iterations_total 150.0
system_currently_down 0.0
```

## 🚨 Alerts Configured

The following alerts are automatically configured:

| Alert | Threshold | Severity | Description |
|-------|-----------|----------|-------------|
| SlowRuleEvaluation | > 5s avg | Warning | Rules taking too long |
| VerySlowRuleEvaluation | > 10s avg | Critical | Rules critically slow |
| SlowHTTPRequests | > 3s avg | Warning | HTTP requests slow |
| VerySlowHTTPRequests | > 5s avg | Critical | HTTP critically slow |
| HighRuleEvaluatorIterationRate | > 10/sec | Warning | Too many iterations |
| SystemCurrentlyDown | = 1 | Critical | System is down |
| SystemDownExtended | = 1 for 5m | Critical | Down for extended time |

## 🧪 Test It

Run the test suite:

```bash
cd "/home/nadeeshame/CHOREO/Choreo AI Assistant/choreo-ai-assistant"
python -m backend.monitoring.examples.test_rule_evaluation_metrics
```

## 💡 Best Practices

1. **Record Every Evaluation**: Track all rule evaluations for accurate averages
2. **Set Realistic Thresholds**: Adjust alert thresholds based on your SLA
3. **Monitor Trends**: Watch for gradual degradation over time
4. **Handle Failures**: Always set system_down when critical failures occur
5. **Check Health Regularly**: Use `get_rule_evaluation_health()` in your health checks

## 📊 Prometheus Queries

Useful queries for custom dashboards:

```promql
# Average rule evaluation duration over 5 minutes
avg_over_time(rule_evaluation_duration_avg_seconds[5m])

# HTTP request duration trend
rate(http_request_duration_avg_seconds[5m])

# Rule evaluator iteration rate
rate(rule_evaluator_iterations_total[1m])

# System uptime percentage (last hour)
avg_over_time(system_currently_down[1h]) * 100

# P95 rule evaluation duration
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## ✅ Health Check Response

The health check returns:

```python
{
    'healthy': True,  # False if avg_rule_eval > 5s or avg_http > 3s or system_down
    'avg_rule_evaluation_duration': 2.5,
    'avg_http_request_duration': 1.2,
    'total_iterations': 150,
    'system_down': False,
    'total_downtime_seconds': 0.0,
    'metrics': {
        'last_rule_eval_duration': 2.5,
        'last_http_duration': 1.2,
        'rule_eval_samples': 100,
        'http_samples': 100
    }
}
```

## 🔧 Troubleshooting

### Metrics Not Showing Up?

```bash
# Check if monitoring service is initialized
curl http://localhost:8000/metrics | grep rule_evaluation

# Should see output like:
# rule_evaluation_duration_seconds 0.0
# rule_evaluation_duration_avg_seconds 0.0
```

### High Rule Evaluation Duration?

1. Check what rules are slow
2. Review rule complexity
3. Consider caching results
4. Optimize database queries in rules

### System Marked as Down?

```python
# Check and reset if needed
if monitoring.is_system_down():
    # Investigate the issue
    # Fix the problem
    monitoring.set_system_up()
```

## 📚 Documentation

- **Full Guide**: See implementation details in code
- **Test Suite**: `examples/test_rule_evaluation_metrics.py`
- **Grafana Panels**: 4 new panels added to dashboard
- **Alert Rules**: 7 new alerts configured

---

**You're all set!** Start recording rule evaluation metrics and monitor them in Grafana. 🎉


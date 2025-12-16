# Scraping Metrics Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         YOUR INGESTION CODE                                  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  from monitoring import get_monitoring_service                      │    │
│  │  from monitoring.helpers.scraping_metrics import                    │    │
│  │      ScrapingIterationTracker                                       │    │
│  │                                                                      │    │
│  │  monitoring = get_monitoring_service()                              │    │
│  │                                                                      │    │
│  │  with ScrapingIterationTracker(monitoring) as tracker:              │    │
│  │      try:                                                            │    │
│  │          run_ingestion()                                            │    │
│  │          tracker.mark_success()                                     │    │
│  │      except Exception:                                              │    │
│  │          tracker.mark_failure()                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MONITORING SERVICE (Facade)                             │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │  • record_missed_iteration()                                      │      │
│  │  • record_skipped_iteration()                                     │      │
│  │  • record_tardy_scrape()                                          │      │
│  │  • record_reload_failure()                                        │      │
│  │  • record_skipped_scrape()                                        │      │
│  │  • record_iteration_start()                                       │      │
│  │  • record_scrape_complete()                                       │      │
│  │  • set_scraping_interval()                                        │      │
│  │  • get_scraping_health()                                          │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                    │                                         │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  System Metrics      │  │  Application         │  │  Scraping Metrics    │
│  Collector           │  │  Metrics Collector   │  │  Collector (NEW!)    │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│ • CPU usage          │  │ • HTTP requests      │  │ • Missed iterations  │
│ • Memory usage       │  │ • Errors             │  │ • Skipped iterations │
│ • Disk usage         │  │ • Active requests    │  │ • Tardy scrapes      │
│ • Process count      │  │ • Latency            │  │ • Reload failures    │
│                      │  │                      │  │ • Skipped scrapes    │
│                      │  │                      │  │ • Success rate       │
│                      │  │                      │  │ • Iteration delay    │
└──────────┬───────────┘  └──────────┬───────────┘  └──────────┬───────────┘
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                                     ▼
           ┌─────────────────────────────────────────────────────┐
           │         PROMETHEUS EXPORTER                          │
           │                                                      │
           │  Converts metrics to Prometheus format:             │
           │  • scraping_missed_iterations_total                 │
           │  • scraping_skipped_iterations_total                │
           │  • scraping_tardy_scrapes_total                     │
           │  • scraping_reload_failures_total                   │
           │  • scraping_skipped_scrapes_total                   │
           │  • scraping_iterations_total                        │
           │  • scraping_successful_scrapes_total                │
           │  • scraping_last_scrape_timestamp                   │
           │  • scraping_last_scrape_duration_seconds            │
           │  • scraping_iteration_delay_seconds                 │
           └──────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
           ┌─────────────────────────────────────────────────────┐
           │         /metrics ENDPOINT                            │
           │                                                      │
           │  http://localhost:8000/metrics                       │
           │                                                      │
           │  # HELP scraping_missed_iterations_total ...         │
           │  # TYPE scraping_missed_iterations_total counter     │
           │  scraping_missed_iterations_total 0.0                │
           │  ...                                                 │
           └──────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
           ┌─────────────────────────────────────────────────────┐
           │         PROMETHEUS                                   │
           │                                                      │
           │  • Scrapes /metrics every 15s                        │
           │  • Stores time-series data                           │
           │  • Evaluates alert rules                             │
           │  • Sends to Alertmanager                             │
           │                                                      │
           │  http://localhost:9090                               │
           └──────────────────────┬──────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │   GRAFANA        │  │  ALERT RULES     │  │  ALERTMANAGER    │
    │                  │  │                  │  │                  │
    │  Dashboards:     │  │  • Missed > 0    │  │  • Slack         │
    │  ┌────────────┐  │  │  • Tardy > 0.2   │  │  • Email         │
    │  │ Scraping   │  │  │  • Delay > 2h    │  │  • PagerDuty     │
    │  │ Issues     │  │  │  • Success < 90% │  │  • Webhook       │
    │  ├────────────┤  │  │  • Reload fail   │  │                  │
    │  │ Scraping   │  │  │    (Critical)    │  │                  │
    │  │ Failures   │  │  │  ...             │  │                  │
    │  ├────────────┤  │  │                  │  │                  │
    │  │ Iteration  │  │  │                  │  │                  │
    │  │ Delay      │  │  │                  │  │                  │
    │  ├────────────┤  │  │                  │  │                  │
    │  │ Last       │  │  │                  │  │                  │
    │  │ Duration   │  │  │                  │  │                  │
    │  ├────────────┤  │  │                  │  │                  │
    │  │ Stats      │  │  │                  │  │                  │
    │  └────────────┘  │  │                  │  │                  │
    │                  │  │                  │  │                  │
    │  localhost:3000  │  │  prometheus.yml  │  │  localhost:9093  │
    └──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Data Flow

1. **Your Code** → Calls helper functions/decorators
2. **Monitoring Service** → Records events in collectors
3. **Scraping Collector** → Maintains counters and state
4. **Prometheus Exporter** → Exposes metrics at `/metrics`
5. **Prometheus** → Scrapes and stores metrics
6. **Grafana** → Visualizes metrics in dashboards
7. **Alert Rules** → Trigger notifications via Alertmanager

## Integration Points

### Level 1: Simple (Decorator)
```python
@track_scraping_iteration(monitoring)
def run_job():
    pass
```

### Level 2: Standard (Context Manager)
```python
with ScrapingIterationTracker(monitoring) as tracker:
    tracker.mark_success()
```

### Level 3: Advanced (Manual)
```python
monitoring.record_iteration_start()
monitoring.record_scrape_complete(duration, success=True)
```

## Component Responsibilities

### ScrapingMetricsCollector
- Tracks counters (missed, skipped, tardy, etc.)
- Calculates health metrics
- Provides current state

### MonitoringService
- Facade for all metric operations
- Coordinates between collectors
- Simplifies API

### PrometheusExporter
- Converts Python metrics to Prometheus format
- Registers metric definitions
- Updates metric values

### Helpers
- ScrapingIterationTracker: Context manager
- ScrapingMetricsHelper: Convenience methods
- Decorators: Function wrappers

## Metrics Categories

### Failure Metrics (Counters)
- missed_iterations
- skipped_iterations
- tardy_scrapes
- reload_failures
- skipped_scrapes

### Success Metrics (Counters)
- iterations_total
- successful_scrapes_total

### Timing Metrics (Gauges)
- last_scrape_timestamp
- last_scrape_duration_seconds
- iteration_delay_seconds

## Health Calculation

```python
health = {
    'healthy': (
        success_rate >= 90% AND
        reload_failures == 0 AND
        missed_iterations < 5
    ),
    'success_rate_percent': (successful / total) * 100,
    'total_failures': sum(all_failure_metrics),
    'metrics': { ... }
}
```

## Alert Triggers

```
Missed Iterations     → rate > 0          → Warning
Skipped Iterations    → rate > 0.5/sec    → Warning
Tardy Scrapes         → rate > 0.2/sec    → Warning
Reload Failures       → rate > 0          → CRITICAL
High Skip Rate        → rate > 1/sec      → Warning
Iteration Delay       → > 2 hours         → Warning
Iteration Delay       → > 4 hours         → CRITICAL
Low Success Rate      → < 90%             → Warning
Very Low Success      → < 70%             → CRITICAL
```

## Technology Stack

```
Python (Backend)
    ↓
prometheus_client (Metrics)
    ↓
FastAPI /metrics endpoint
    ↓
Prometheus (Scraping & Storage)
    ↓
Grafana (Visualization)
    ↓
Alertmanager (Notifications)
```

## SOLID Principles Applied

- **S**ingle Responsibility: Each collector handles one type of metrics
- **O**pen/Closed: New collectors added without modifying existing ones
- **L**iskov Substitution: All collectors implement IMetricsCollector
- **I**nterface Segregation: Clean, focused interfaces
- **D**ependency Inversion: Depend on abstractions (IMetricsCollector)


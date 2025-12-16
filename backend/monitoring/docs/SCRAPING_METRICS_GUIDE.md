# Scraping Metrics Guide

## Overview

The scraping metrics system tracks the health and performance of your data ingestion/scraping operations. This guide shows you how to integrate these metrics into your existing ingestion workflows.

## Available Metrics

### 1. **Missed Iterations** (`scraping_missed_iterations_total`)
- **What it tracks**: Number of scheduled scraping iterations that didn't start on time
- **When to use**: When your scraping job should run on a schedule but failed to start
- **Example**: A cron job that should run every hour but missed 3 consecutive runs

### 2. **Skipped Iterations** (`scraping_skipped_iterations_total`)
- **What it tracks**: Number of iterations intentionally skipped
- **When to use**: When you deliberately skip a scheduled iteration (e.g., maintenance window)
- **Example**: Skipping scraping during system maintenance

### 3. **Tardy Scrapes** (`scraping_tardy_scrapes_total`)
- **What it tracks**: Number of scrapes that started later than expected
- **When to use**: When a scrape starts but is delayed beyond acceptable threshold
- **Example**: A scrape scheduled for 10:00 that actually starts at 10:05

### 4. **Reload Failures** (`scraping_reload_failures_total`)
- **What it tracks**: Number of configuration or data reload failures
- **When to use**: When reloading configuration, reconnecting to services, or reinitializing state fails
- **Example**: Failed to reload GitHub token or Pinecone credentials

### 5. **Skipped Scrapes** (`scraping_skipped_scrapes_total`)
- **What it tracks**: Number of individual scrape operations that were skipped
- **When to use**: When you skip scraping individual items (files, repos, etc.)
- **Example**: Skipping a file because it's too large or corrupted

## Quick Start

### Option 1: Using Decorators (Easiest)

Perfect for simple scraping functions:

```python
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import track_scraping_iteration

monitoring = get_monitoring_service()

@track_scraping_iteration(monitoring)
def run_my_scraping_job():
    """This will automatically track the iteration."""
    # Your scraping logic here
    scrape_repositories()
    process_documents()
    # Success/failure is automatically recorded
```

### Option 2: Using Context Manager (Recommended)

For more control and granular tracking:

```python
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import ScrapingIterationTracker

monitoring = get_monitoring_service()

def run_scraping_with_tracking():
    with ScrapingIterationTracker(monitoring) as tracker:
        try:
            # Your scraping logic
            repos = fetch_repositories()
            
            for repo in repos:
                try:
                    scrape_repo(repo)
                except Exception as e:
                    # Track skipped individual scrape
                    tracker.record_skipped_scrape()
                    continue
            
            # Mark as successful
            tracker.mark_success()
            
        except Exception as e:
            # Automatically marked as failure
            tracker.mark_failure()
            raise
```

### Option 3: Using Helper Class (Most Flexible)

For complex workflows with multiple metric types:

```python
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import ScrapingMetricsHelper

monitoring = get_monitoring_service()
scraping_metrics = ScrapingMetricsHelper(monitoring)

# Set expected interval (e.g., 1 hour = 3600 seconds)
scraping_metrics.set_interval(3600)

def complex_scraping_workflow():
    # Check if we should skip this iteration
    if is_maintenance_window():
        scraping_metrics.skipped(1)
        return
    
    # Track the iteration
    with scraping_metrics.iteration() as tracker:
        try:
            # Reload configuration
            try:
                reload_config()
            except Exception:
                scraping_metrics.reload_failed()
                raise
            
            # Process items
            items = get_items_to_scrape()
            
            for item in items:
                if should_skip(item):
                    scraping_metrics.skipped_scrape()
                    continue
                
                try:
                    scrape_item(item)
                except Exception:
                    scraping_metrics.skipped_scrape()
            
            tracker.mark_success()
            
        except Exception as e:
            tracker.mark_failure()
            raise
```

## Integration with Existing Ingestion Service

### Minimal Integration Example

Add to your `run_ingestion.py` or wherever you run scraping:

```python
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import ScrapingIterationTracker

# Get monitoring service (already initialized in app.py)
monitoring = get_monitoring_service()

# Set expected interval if running on a schedule
# Example: scraping runs every 1 hour
monitoring.set_scraping_interval(3600)

def main():
    """Main ingestion function with metrics tracking."""
    
    with ScrapingIterationTracker(monitoring) as tracker:
        try:
            logger.info("Starting ingestion...")
            
            # Your existing ingestion logic
            vector_client = VectorClient(...)
            github_service = GitHubService(...)
            ingestion_service = IngestionService(...)
            
            # Run ingestion
            result = ingestion_service.ingest_repository(
                owner=REPO_OWNER,
                repo=REPO_NAME
            )
            
            # Track individual skips if applicable
            if result.get('skipped_files', 0) > 0:
                tracker.record_skipped_scrape(result['skipped_files'])
            
            # Mark as successful
            tracker.mark_success()
            
            logger.info("Ingestion completed successfully")
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            tracker.mark_failure()
            raise

if __name__ == "__main__":
    main()
```

### Advanced Integration with Scheduled Jobs

If using APScheduler or similar:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import ScrapingMetricsHelper

monitoring = get_monitoring_service()
scraping_metrics = ScrapingMetricsHelper(monitoring)

# Set interval (1 hour)
scraping_metrics.set_interval(3600)

def scheduled_scraping_job():
    """Job that runs on schedule."""
    with scraping_metrics.iteration() as tracker:
        try:
            # Your scraping logic
            run_ingestion()
            tracker.mark_success()
        except Exception as e:
            tracker.mark_failure()
            raise

# Setup scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    scheduled_scraping_job,
    'interval',
    hours=1,
    id='scraping_job'
)

# Add missed iteration detection
def check_for_missed_iterations():
    """Check if we missed any iterations."""
    health = scraping_metrics.health()
    if not health['healthy']:
        logger.warning(f"Scraping health issues detected: {health}")

scheduler.add_job(
    check_for_missed_iterations,
    'interval',
    minutes=5,
    id='health_check'
)

scheduler.start()
```

## Tracking Specific Scenarios

### Scenario 1: File Skipped During Processing

```python
def process_file(file_path):
    try:
        content = read_file(file_path)
        if len(content) > MAX_SIZE:
            monitoring.record_skipped_scrape()
            logger.warning(f"Skipped large file: {file_path}")
            return
        
        # Process normally
        process_content(content)
        
    except Exception as e:
        monitoring.record_skipped_scrape()
        logger.error(f"Failed to process {file_path}: {e}")
```

### Scenario 2: Configuration Reload Failed

```python
def reload_configuration():
    try:
        new_config = load_config_from_file()
        validate_config(new_config)
        apply_config(new_config)
    except Exception as e:
        monitoring.record_reload_failure()
        logger.error(f"Config reload failed: {e}")
        raise
```

### Scenario 3: Scheduled Job Missed

```python
from datetime import datetime, timedelta

last_run_time = None
expected_interval = timedelta(hours=1)

def scheduled_job():
    global last_run_time
    
    now = datetime.now()
    
    # Check if we missed iterations
    if last_run_time:
        time_since_last = now - last_run_time
        missed_count = int((time_since_last - expected_interval).total_seconds() / 3600)
        if missed_count > 0:
            monitoring.record_missed_iteration(missed_count)
    
    # Run the job
    with ScrapingIterationTracker(monitoring) as tracker:
        try:
            run_scraping()
            tracker.mark_success()
            last_run_time = now
        except Exception as e:
            tracker.mark_failure()
            raise
```

### Scenario 4: Delayed Start (Tardy)

```python
import time

scheduled_time = datetime.now().replace(hour=10, minute=0, second=0)
actual_start = datetime.now()

def check_and_run():
    delay = (actual_start - scheduled_time).total_seconds()
    
    # If delayed by more than 5 minutes, it's tardy
    if delay > 300:
        monitoring.record_tardy_scrape()
        logger.warning(f"Scrape started {delay}s late")
    
    run_scraping()
```

## Monitoring in Grafana

Once metrics are being recorded, you can view them in Grafana:

1. **Open Grafana**: http://localhost:3000
2. **Navigate to**: Choreo AI Assistant - Overview dashboard
3. **View panels**:
   - **Scraping Issues**: Shows missed iterations, skipped iterations, and tardy scrapes
   - **Scraping Failures**: Shows reload failures and skipped scrapes
   - **Time Since Last Iteration**: Gauge showing delay
   - **Last Scrape Duration**: How long the last scrape took
   - **Scraping Iteration Stats**: Total iterations vs successful scrapes

## Alerts

The following alerts are automatically configured:

| Alert | Threshold | Severity | Description |
|-------|-----------|----------|-------------|
| ScrapingMissedIterations | Any missed | Warning | Iterations are being missed |
| ScrapingTooManySkippedIterations | >0.5/sec over 1h | Warning | Too many iterations skipped |
| ScrapingTardyScrapes | >0.2/sec over 1h | Warning | Scrapes starting late |
| ScrapingReloadFailures | Any failures | **Critical** | Config reload failures |
| ScrapingHighSkipRate | >1/sec over 1h | Warning | High rate of skipped scrapes |
| ScrapingIterationDelayHigh | >2 hours | Warning | Iteration overdue |
| ScrapingIterationDelayCritical | >4 hours | **Critical** | Iteration critically overdue |
| ScrapingLowSuccessRate | <90% | Warning | Low success rate |
| ScrapingVeryLowSuccessRate | <70% | **Critical** | Very low success rate |

## Health Check

Check scraping health programmatically:

```python
from monitoring import get_monitoring_service

monitoring = get_monitoring_service()

# Get health status
health = monitoring.get_scraping_health()

print(f"Healthy: {health['healthy']}")
print(f"Success Rate: {health['success_rate_percent']:.2f}%")
print(f"Total Failures: {health['total_failures']}")
print(f"Last Scrape: {health['last_scrape']}")
print(f"Metrics: {health['metrics']}")

# Example output:
# Healthy: True
# Success Rate: 95.50%
# Total Failures: 3
# Last Scrape: 2025-11-19T10:30:00
# Metrics: {'missed_iterations': 0, 'skipped_iterations': 1, ...}
```

## Prometheus Queries

Useful queries for custom dashboards:

```promql
# Rate of missed iterations in last hour
rate(scraping_missed_iterations_total[1h])

# Success rate percentage
(rate(scraping_successful_scrapes_total[1h]) / rate(scraping_iterations_total[1h])) * 100

# Total failures
sum(rate(scraping_missed_iterations_total[1h]) + 
    rate(scraping_skipped_iterations_total[1h]) + 
    rate(scraping_tardy_scrapes_total[1h]) + 
    rate(scraping_reload_failures_total[1h]) + 
    rate(scraping_skipped_scrapes_total[1h]))

# Time since last scrape in hours
scraping_iteration_delay_seconds / 3600

# Average scrape duration over 5 minutes
avg_over_time(scraping_last_scrape_duration_seconds[5m])
```

## Best Practices

1. **Set Expected Interval**: Always call `set_scraping_interval()` if running on a schedule
2. **Use Context Managers**: They handle exceptions and ensure metrics are recorded
3. **Track Granularly**: Record skipped individual items, not just whole iterations
4. **Monitor Health**: Regularly check scraping health in your code
5. **Configure Alerts**: Adjust alert thresholds based on your requirements
6. **Review Metrics**: Regularly review Grafana dashboards to catch issues early

## Troubleshooting

### Metrics Not Showing Up

1. Check that monitoring service is initialized:
   ```python
   from monitoring import get_monitoring_service
   monitoring = get_monitoring_service()
   print(monitoring)  # Should not be None
   ```

2. Verify Prometheus is scraping:
   - Visit http://localhost:9090/targets
   - Ensure your app endpoint is listed and UP

3. Check metrics endpoint:
   - Visit http://localhost:8000/metrics
   - Search for "scraping_" metrics

### Metrics Incrementing Unexpectedly

- Check that you're not calling record methods in loops accidentally
- Use context managers to avoid double-counting
- Review your code for duplicate tracking calls

### Alerts Not Firing

1. Check Prometheus alert rules:
   - Visit http://localhost:9090/alerts
   - Verify rules are loaded

2. Check alert expressions in Grafana

3. Verify Alertmanager is running:
   ```bash
   docker-compose ps alertmanager
   ```

## Examples Repository

See the `backend/monitoring/examples/` directory for complete working examples.


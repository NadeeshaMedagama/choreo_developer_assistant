# Scraping Metrics - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Import and Initialize

Add to your ingestion script (`run_ingestion.py` or similar):

```python
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import ScrapingIterationTracker

# Get monitoring service
monitoring = get_monitoring_service()

# Set expected interval if running on schedule (e.g., every hour = 3600 seconds)
monitoring.set_scraping_interval(3600)
```

### Step 2: Wrap Your Ingestion Logic

Replace your main function with this pattern:

```python
def main():
    """Main ingestion function with metrics tracking."""
    
    with ScrapingIterationTracker(monitoring) as tracker:
        try:
            # Your existing ingestion code here
            logger.info("Starting ingestion...")
            
            # Initialize services
            vector_client = VectorClient(...)
            github_service = GitHubService(...)
            ingestion_service = IngestionService(...)
            
            # Run ingestion
            ingestion_service.ingest_repository(
                owner="your-org",
                repo="your-repo"
            )
            
            # Mark as successful
            tracker.mark_success()
            logger.info("Ingestion completed successfully")
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            tracker.mark_failure()
            raise
```

### Step 3: Track Skipped Files (Optional but Recommended)

When processing files, track skips:

```python
for file in files_to_process:
    try:
        if should_skip_file(file):
            monitoring.record_skipped_scrape()
            continue
        
        process_file(file)
        
    except Exception as e:
        monitoring.record_skipped_scrape()
        logger.error(f"Failed to process {file}: {e}")
```

### Step 4: View Metrics

1. **Start your application** (if not already running):
   ```bash
   cd backend
   python -m uvicorn app:app --reload
   ```

2. **Check metrics endpoint**:
   ```bash
   curl http://localhost:8000/metrics | grep scraping
   ```

3. **View in Grafana**:
   - Open http://localhost:3000
   - Go to "Choreo AI Assistant - Overview" dashboard
   - Scroll to the scraping metrics panels

## 📊 What You Get

Once integrated, you'll automatically track:

| Metric | What it means | When to investigate |
|--------|---------------|---------------------|
| **Missed Iterations** | Scheduled jobs didn't run | Alert when > 0 |
| **Skipped Iterations** | Jobs intentionally skipped | Review if excessive |
| **Tardy Scrapes** | Jobs started late | Check system resources |
| **Reload Failures** | Config/connection failures | **Critical** - fix immediately |
| **Skipped Scrapes** | Individual items skipped | Normal if < 10% of total |
| **Iteration Delay** | Time since last run | Alert if > 2x expected interval |
| **Success Rate** | % of successful runs | Alert if < 90% |

## 🔧 Advanced Usage

### Using Decorators (Simplest)

```python
from monitoring.helpers.scraping_metrics import track_scraping_iteration

@track_scraping_iteration(monitoring)
def run_ingestion():
    # Your code here
    pass
```

### Manual Control (Most Flexible)

```python
from monitoring.helpers.scraping_metrics import ScrapingMetricsHelper

scraping = ScrapingMetricsHelper(monitoring)

# Record specific events
scraping.missed(1)           # Missed iteration
scraping.skipped(1)          # Skipped iteration
scraping.tardy(1)            # Tardy scrape
scraping.reload_failed(1)    # Reload failure
scraping.skipped_scrape(5)   # Skipped 5 items

# Check health
health = scraping.health()
print(f"Healthy: {health['healthy']}")
print(f"Success rate: {health['success_rate_percent']:.1f}%")
```

### Tracking Reload Failures

```python
from monitoring.helpers.scraping_metrics import track_reload_operation

def reload_config():
    with track_reload_operation(monitoring):
        # Reload logic here
        # If this raises an exception, it's tracked as a failure
        load_config_from_file()
```

## 🎯 Integration Examples

### Example 1: Basic Integration

```python
# In your run_ingestion.py
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import ScrapingIterationTracker

monitoring = get_monitoring_service()

def main():
    with ScrapingIterationTracker(monitoring) as tracker:
        try:
            run_your_ingestion()
            tracker.mark_success()
        except Exception as e:
            tracker.mark_failure()
            raise

if __name__ == "__main__":
    main()
```

### Example 2: Scheduled Job

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from monitoring import get_monitoring_service
from monitoring.helpers.scraping_metrics import ScrapingIterationTracker

monitoring = get_monitoring_service()
monitoring.set_scraping_interval(3600)  # 1 hour

def hourly_ingestion():
    with ScrapingIterationTracker(monitoring) as tracker:
        try:
            run_ingestion()
            tracker.mark_success()
        except Exception:
            tracker.mark_failure()
            raise

scheduler = BlockingScheduler()
scheduler.add_job(hourly_ingestion, 'interval', hours=1)
scheduler.start()
```

### Example 3: Tracking Individual Files

```python
def process_files(file_list):
    successful = 0
    
    with ScrapingIterationTracker(monitoring) as tracker:
        for file in file_list:
            try:
                if file.size > MAX_SIZE:
                    tracker.record_skipped_scrape()
                    continue
                
                process_file(file)
                successful += 1
                
            except Exception as e:
                tracker.record_skipped_scrape()
                logger.error(f"Failed: {file}")
        
        if successful > 0:
            tracker.mark_success()
        else:
            tracker.mark_failure()
```

## 📈 Viewing Metrics in Grafana

The updated dashboard includes these new panels:

1. **Scraping Issues (1h rate)** - Line chart showing:
   - Missed Iterations
   - Skipped Iterations
   - Tardy Scrapes

2. **Scraping Failures (1h rate)** - Line chart showing:
   - Reload Failures
   - Skipped Scrapes

3. **Time Since Last Iteration** - Gauge showing how long since last run

4. **Last Scrape Duration** - Gauge showing how long the last scrape took

5. **Scraping Iteration Stats** - Line chart showing:
   - Total Iterations
   - Successful Scrapes

## 🚨 Alerts

Alerts are automatically configured and will fire when:

| Alert | Condition | Action Required |
|-------|-----------|-----------------|
| Missed Iterations | Any missed | Check scheduler/cron |
| Too Many Skips | > 0.5/sec over 1h | Review skip logic |
| Tardy Scrapes | > 0.2/sec over 1h | Check system load |
| Reload Failures | Any failures | **Fix immediately** |
| Iteration Delay | > 2 hours | Restart scheduler |
| Low Success Rate | < 90% | Investigate errors |

## ✅ Checklist

- [ ] Imported monitoring service
- [ ] Set scraping interval with `set_scraping_interval()`
- [ ] Wrapped main ingestion with `ScrapingIterationTracker`
- [ ] Track skipped files with `record_skipped_scrape()`
- [ ] Track reload failures if applicable
- [ ] Tested by running ingestion once
- [ ] Verified metrics at `/metrics` endpoint
- [ ] Checked Grafana dashboard
- [ ] Reviewed alert rules

## 🔍 Troubleshooting

### Metrics not showing up?

```bash
# Check if monitoring is initialized
curl http://localhost:8000/metrics | grep scraping

# Should see output like:
# scraping_iterations_total 5.0
# scraping_successful_scrapes_total 4.0
# scraping_missed_iterations_total 0.0
```

### Dashboard not updating?

1. Check Prometheus is scraping: http://localhost:9090/targets
2. Verify your app is in the targets list
3. Check Grafana data source: http://localhost:3000/datasources

### Need help?

- Full documentation: `backend/monitoring/docs/SCRAPING_METRICS_GUIDE.md`
- Example code: `backend/monitoring/examples/scraping_metrics_integration.py`
- Architecture: `backend/monitoring/README.md`

## 📚 Next Steps

1. **Review the full guide**: See `SCRAPING_METRICS_GUIDE.md` for all features
2. **Customize thresholds**: Edit `alert_rules.yml` for your use case
3. **Add custom panels**: Extend the Grafana dashboard
4. **Set up alerting**: Configure Alertmanager for notifications

## 💡 Tips

- Start simple with the decorator pattern
- Add granular tracking as needed
- Monitor the health endpoint regularly
- Adjust alert thresholds based on your SLA
- Use context managers for automatic cleanup

---

**That's it! You're now tracking scraping metrics.** 🎉

Run your ingestion and check Grafana to see your metrics in action.


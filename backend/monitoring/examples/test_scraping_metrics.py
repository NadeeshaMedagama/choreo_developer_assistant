"""
Test Script for Scraping Metrics

This script tests the scraping metrics functionality to ensure everything is working correctly.

Run this script to verify your metrics integration:
    python -m backend.monitoring.examples.test_scraping_metrics
"""

import time
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    from monitoring import get_monitoring_service
    from monitoring.helpers.scraping_metrics import (
        ScrapingIterationTracker,
        ScrapingMetricsHelper,
        track_scraping_iteration,
        track_scrape
    )
    print("✓ Successfully imported monitoring modules")
except ImportError as e:
    print(f"✗ Failed to import monitoring modules: {e}")
    sys.exit(1)


def test_basic_tracking():
    """Test basic iteration tracking."""
    print("\n" + "="*60)
    print("TEST 1: Basic Iteration Tracking")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Test iteration tracking
    with ScrapingIterationTracker(monitoring) as tracker:
        print("- Starting iteration...")
        time.sleep(0.1)  # Simulate work
        print("- Marking as success...")
        tracker.mark_success()
    
    print("✓ Basic tracking completed")


def test_metrics_helper():
    """Test metrics helper class."""
    print("\n" + "="*60)
    print("TEST 2: Metrics Helper")
    print("="*60)
    
    monitoring = get_monitoring_service()
    helper = ScrapingMetricsHelper(monitoring)
    
    # Set interval
    helper.set_interval(3600)
    print("- Set interval to 3600 seconds")
    
    # Record various metrics
    helper.missed(1)
    print("- Recorded 1 missed iteration")
    
    helper.skipped(1)
    print("- Recorded 1 skipped iteration")
    
    helper.tardy(1)
    print("- Recorded 1 tardy scrape")
    
    helper.skipped_scrape(3)
    print("- Recorded 3 skipped scrapes")
    
    # Check health
    health = helper.health()
    print(f"\n- Health Status:")
    print(f"  Healthy: {health['healthy']}")
    print(f"  Success Rate: {health['success_rate_percent']:.2f}%")
    print(f"  Total Failures: {health['total_failures']}")
    print(f"  Metrics: {health['metrics']}")
    
    print("\n✓ Metrics helper test completed")


def test_decorator_pattern():
    """Test decorator pattern."""
    print("\n" + "="*60)
    print("TEST 3: Decorator Pattern")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    @track_scraping_iteration(monitoring)
    def sample_ingestion():
        """Sample ingestion function."""
        print("- Running sample ingestion...")
        time.sleep(0.1)
        print("- Ingestion completed")
    
    # Run it
    sample_ingestion()
    print("✓ Decorator pattern test completed")


def test_scrape_decorator():
    """Test individual scrape decorator."""
    print("\n" + "="*60)
    print("TEST 4: Individual Scrape Tracking")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    @track_scrape(monitoring)
    def process_item(item_name):
        """Process a single item."""
        print(f"- Processing {item_name}...")
        time.sleep(0.05)
        return f"Processed {item_name}"
    
    # Process some items
    for i in range(3):
        result = process_item(f"item_{i}")
        print(f"  {result}")
    
    print("✓ Individual scrape tracking test completed")


def test_failure_tracking():
    """Test failure tracking."""
    print("\n" + "="*60)
    print("TEST 5: Failure Tracking")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    try:
        with ScrapingIterationTracker(monitoring) as tracker:
            print("- Starting iteration that will fail...")
            time.sleep(0.1)
            print("- Simulating failure...")
            tracker.mark_failure()
            raise Exception("Simulated failure")
    except Exception as e:
        print(f"- Caught exception: {e}")
    
    print("✓ Failure tracking test completed")


def test_reload_failure():
    """Test reload failure tracking."""
    print("\n" + "="*60)
    print("TEST 6: Reload Failure Tracking")
    print("="*60)
    
    monitoring = get_monitoring_service()
    helper = ScrapingMetricsHelper(monitoring)
    
    # Simulate reload failure
    print("- Recording reload failure...")
    helper.reload_failed(1)
    
    # Check health
    health = helper.health()
    print(f"- Health after reload failure: {health['healthy']}")
    
    print("✓ Reload failure test completed")


def test_metrics_collection():
    """Test that metrics are being collected."""
    print("\n" + "="*60)
    print("TEST 7: Metrics Collection")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Get current metrics
    print("- Collecting metrics from scraping collector...")
    metrics = monitoring.scraping_collector.collect()
    
    print("\n- Current Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Metrics collection test completed")


def test_prometheus_export():
    """Test Prometheus export."""
    print("\n" + "="*60)
    print("TEST 8: Prometheus Export")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Get Prometheus formatted metrics
    print("- Exporting metrics in Prometheus format...")
    prometheus_output = monitoring.get_metrics()
    
    # Check for scraping metrics
    scraping_metrics = [line for line in prometheus_output.split('\n') if 'scraping_' in line]
    
    print(f"\n- Found {len(scraping_metrics)} scraping metric lines")
    print("\n- Sample scraping metrics:")
    for line in scraping_metrics[:10]:  # Show first 10
        if line and not line.startswith('#'):
            print(f"  {line}")
    
    print("\n✓ Prometheus export test completed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("SCRAPING METRICS TEST SUITE")
    print("="*60)
    
    tests = [
        test_basic_tracking,
        test_metrics_helper,
        test_decorator_pattern,
        test_scrape_decorator,
        test_failure_tracking,
        test_reload_failure,
        test_metrics_collection,
        test_prometheus_export,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Scraping metrics are working correctly.")
        print("\nNext steps:")
        print("1. View metrics at: http://localhost:8000/metrics")
        print("2. Check Grafana dashboard: http://localhost:3000")
        print("3. See SCRAPING_METRICS_QUICKSTART.md for integration guide")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()


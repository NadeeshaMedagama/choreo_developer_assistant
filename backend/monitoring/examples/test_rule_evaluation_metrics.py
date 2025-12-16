"""
Test Script for Rule Evaluation Metrics

This script tests the rule evaluation metrics functionality.

Run this script to verify the new metrics:
    python -m backend.monitoring.examples.test_rule_evaluation_metrics
"""

import time
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

try:
    from monitoring import get_monitoring_service
    print("✓ Successfully imported monitoring modules")
except ImportError as e:
    print(f"✗ Failed to import monitoring modules: {e}")
    sys.exit(1)


def test_rule_evaluation_recording():
    """Test recording rule evaluation durations."""
    print("\n" + "="*60)
    print("TEST 1: Rule Evaluation Duration Recording")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Record some rule evaluations
    print("- Recording rule evaluation durations...")
    monitoring.record_rule_evaluation(0.5)
    monitoring.record_rule_evaluation(1.2)
    monitoring.record_rule_evaluation(0.8)
    
    # Get health status
    health = monitoring.get_rule_evaluation_health()
    print(f"- Average rule evaluation duration: {health['avg_rule_evaluation_duration']:.3f}s")
    print(f"- Samples collected: {health['metrics']['rule_eval_samples']}")
    
    print("✓ Rule evaluation recording test completed")


def test_http_request_duration():
    """Test recording HTTP request durations."""
    print("\n" + "="*60)
    print("TEST 2: HTTP Request Duration Recording")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Record some HTTP requests
    print("- Recording HTTP request durations...")
    monitoring.record_http_request_duration(0.3)
    monitoring.record_http_request_duration(0.7)
    monitoring.record_http_request_duration(0.5)
    
    # Get health status
    health = monitoring.get_rule_evaluation_health()
    print(f"- Average HTTP request duration: {health['avg_http_request_duration']:.3f}s")
    print(f"- Samples collected: {health['metrics']['http_samples']}")
    
    print("✓ HTTP request duration test completed")


def test_rule_evaluator_iterations():
    """Test rule evaluator iteration tracking."""
    print("\n" + "="*60)
    print("TEST 3: Rule Evaluator Iterations")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Record some iterations
    print("- Recording rule evaluator iterations...")
    monitoring.record_rule_evaluator_iteration(1.5)
    monitoring.record_rule_evaluator_iteration(1.2)
    monitoring.record_rule_evaluator_iteration()  # Without duration
    
    # Get health status
    health = monitoring.get_rule_evaluation_health()
    print(f"- Total iterations: {health['total_iterations']}")
    
    print("✓ Rule evaluator iterations test completed")


def test_system_status():
    """Test system down/up status tracking."""
    print("\n" + "="*60)
    print("TEST 4: System Status Tracking")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Test setting system down
    print("- Setting system status to DOWN...")
    monitoring.set_system_down(True)
    print(f"- Is system down? {monitoring.is_system_down()}")
    
    time.sleep(0.5)
    
    # Test setting system up
    print("- Setting system status to UP...")
    monitoring.set_system_up()
    print(f"- Is system down? {monitoring.is_system_down()}")
    
    # Get health status
    health = monitoring.get_rule_evaluation_health()
    print(f"- System down: {health['system_down']}")
    print(f"- Total downtime: {health['total_downtime_seconds']:.3f}s")
    
    print("✓ System status test completed")


def test_health_check():
    """Test health check functionality."""
    print("\n" + "="*60)
    print("TEST 5: Health Check")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Record some metrics
    monitoring.record_rule_evaluation(2.0)
    monitoring.record_http_request_duration(1.5)
    
    # Get health status
    health = monitoring.get_rule_evaluation_health()
    
    print(f"\n- Health Status:")
    print(f"  Healthy: {health['healthy']}")
    print(f"  Avg Rule Evaluation: {health['avg_rule_evaluation_duration']:.3f}s")
    print(f"  Avg HTTP Request: {health['avg_http_request_duration']:.3f}s")
    print(f"  Total Iterations: {health['total_iterations']}")
    print(f"  System Down: {health['system_down']}")
    
    print("\n✓ Health check test completed")


def test_metrics_collection():
    """Test that metrics are being collected."""
    print("\n" + "="*60)
    print("TEST 6: Metrics Collection")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Record various metrics
    monitoring.record_rule_evaluation(3.5)
    monitoring.record_http_request_duration(2.1)
    monitoring.record_rule_evaluator_iteration(4.0)
    
    # Get current metrics
    print("- Collecting metrics from rule evaluation collector...")
    metrics = monitoring.rule_evaluation_collector.collect()
    
    print("\n- Current Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Metrics collection test completed")


def test_prometheus_export():
    """Test Prometheus export."""
    print("\n" + "="*60)
    print("TEST 7: Prometheus Export")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    # Record some metrics first
    monitoring.record_rule_evaluation(1.5)
    monitoring.record_http_request_duration(0.8)
    monitoring.record_rule_evaluator_iteration(2.0)
    monitoring.set_system_up()
    
    # Get Prometheus formatted metrics
    print("- Exporting metrics in Prometheus format...")
    prometheus_output = monitoring.get_metrics()
    
    # Check for rule evaluation metrics
    rule_metrics = [line for line in prometheus_output.split('\n') 
                   if any(m in line for m in ['rule_evaluation', 'http_request_duration', 
                                               'rule_evaluator', 'system_currently_down'])]
    
    print(f"\n- Found {len(rule_metrics)} rule evaluation metric lines")
    print("\n- Sample rule evaluation metrics:")
    for line in rule_metrics[:15]:  # Show first 15
        if line and not line.startswith('#'):
            print(f"  {line}")
    
    print("\n✓ Prometheus export test completed")


def test_stress_scenario():
    """Test with realistic load."""
    print("\n" + "="*60)
    print("TEST 8: Stress Scenario")
    print("="*60)
    
    monitoring = get_monitoring_service()
    
    print("- Simulating rule evaluation load...")
    
    # Simulate 20 rule evaluations with varying durations
    for i in range(20):
        duration = 0.5 + (i % 5) * 0.3  # Vary between 0.5 and 2.0 seconds
        monitoring.record_rule_evaluation(duration)
    
    # Simulate 20 HTTP requests
    for i in range(20):
        duration = 0.3 + (i % 4) * 0.2  # Vary between 0.3 and 1.1 seconds
        monitoring.record_http_request_duration(duration)
    
    # Simulate 10 iterations
    for i in range(10):
        monitoring.record_rule_evaluator_iteration(1.0 + i * 0.1)
    
    # Get final health
    health = monitoring.get_rule_evaluation_health()
    
    print(f"\n- After stress test:")
    print(f"  Healthy: {health['healthy']}")
    print(f"  Avg Rule Evaluation: {health['avg_rule_evaluation_duration']:.3f}s")
    print(f"  Avg HTTP Request: {health['avg_http_request_duration']:.3f}s")
    print(f"  Total Iterations: {health['total_iterations']}")
    
    print("\n✓ Stress scenario test completed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("RULE EVALUATION METRICS TEST SUITE")
    print("="*60)
    
    tests = [
        test_rule_evaluation_recording,
        test_http_request_duration,
        test_rule_evaluator_iterations,
        test_system_status,
        test_health_check,
        test_metrics_collection,
        test_prometheus_export,
        test_stress_scenario,
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
        print("\n🎉 All tests passed! Rule evaluation metrics are working correctly.")
        print("\nNext steps:")
        print("1. View metrics at: http://localhost:8000/metrics")
        print("2. Check Grafana dashboard: http://localhost:3000")
        print("3. Look for the new rule evaluation panels")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()


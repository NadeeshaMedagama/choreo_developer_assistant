#!/usr/bin/env python3
"""Quick test to verify monitoring service can be imported."""
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    print("Testing monitoring service import...")
    from backend.monitoring import get_monitoring_service
    print("✅ Import successful")
    
    print("\nInitializing monitoring service...")
    monitoring = get_monitoring_service()
    print("✅ Monitoring service initialized")
    
    print("\nChecking collectors...")
    print(f"✅ System collector: {monitoring.system_collector}")
    print(f"✅ App collector: {monitoring.app_collector}")
    print(f"✅ AI collector: {monitoring.ai_collector}")
    print(f"✅ Scraping collector: {monitoring.scraping_collector}")
    print(f"✅ Rule evaluation collector: {monitoring.rule_evaluation_collector}")
    
    print("\n✅ All collectors initialized successfully!")
    print("\nTesting basic functionality...")
    
    # Test scraping metrics
    monitoring.record_missed_iteration(1)
    print("✅ Scraping metrics work")
    
    # Test rule evaluation metrics
    monitoring.record_rule_evaluation(2.5)
    print("✅ Rule evaluation metrics work")
    
    print("\n🎉 All tests passed! Ready to start the application.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


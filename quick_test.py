#!/usr/bin/env python3
"""
Quick Test - Run all MVP tests in sequence
For when you just want to verify everything works
"""

import subprocess
import sys
from datetime import datetime

def run_test(script, name):
    """Run a single test script"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(f"python3 {script}", shell=True)
        
        if result.returncode == 0:
            print(f"\n✅ {name} - PASSED")
            return True
        else:
            print(f"\n❌ {name} - FAILED")
            return False
            
    except KeyboardInterrupt:
        print(f"\n⚠️ {name} - INTERRUPTED")
        return False
    except Exception as e:
        print(f"\n💥 {name} - ERROR: {e}")
        return False

def main():
    """Run all tests quickly"""
    
    print("🚀 SEMICONDUCTOR TRADE MONITOR - QUICK TEST")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("This will run all MVP tests automatically...")
    
    tests = [
        ("simple_data_test.py", "Data Validation & Sample Generation"),
        ("etl_pipeline.py", "Database Creation & ETL Pipeline"), 
        ("simple_dashboard_test.py", "Analytics & Reporting"),
        ("api_server.py", "API Endpoints & Anomaly Detection")
    ]
    
    results = []
    
    for script, name in tests:
        success = run_test(script, name)
        results.append((name, success))
        
        if not success:
            print(f"\n⚠️ Test failed: {name}")
            choice = input("Continue with remaining tests? (y/N): ").lower()
            if choice != 'y':
                break
    
    # Final summary
    print(f"\n{'='*80}")
    print("📊 QUICK TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"The MVP is working perfectly!")
        print(f"\n⏰ Completed: {datetime.now().strftime('%H:%M:%S')}")
        print(f"\nNext step: python3 test_runner.py (for interactive testing)")
        print(f"Or install Streamlit: pip3 install streamlit pandas plotly")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print(f"Run 'python3 test_runner.py' for detailed testing")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n👋 Quick test interrupted. Run again anytime!")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
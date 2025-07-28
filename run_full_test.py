#!/usr/bin/env python3
"""
Full system test for Semiconductor Trade Monitor MVP
Tests the complete pipeline from ETL to analytics to API
"""

import subprocess
import os
from datetime import datetime

def run_command(command, description):
    """Run a command and capture output"""
    print(f"\n🔄 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    """Run complete system test"""
    
    print("=" * 80)
    print("SEMICONDUCTOR TRADE MONITOR - FULL SYSTEM TEST")
    print(f"Test started: {datetime.now()}")
    print("=" * 80)
    
    # Change to project directory
    project_dir = "/home/manuel/semiconductormonitor"
    os.chdir(project_dir)
    
    tests = [
        ("python3 simple_data_test.py", "1. Validate MVP approach and create sample data"),
        ("python3 etl_pipeline.py", "2. Run ETL pipeline and create database"),
        ("python3 simple_dashboard_test.py", "3. Test analytics and generate reports"),
        ("python3 api_server.py", "4. Test API endpoints and anomaly detection"),
    ]
    
    results = []
    
    for command, description in tests:
        success = run_command(command, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe Semiconductor Trade Monitor MVP is ready!")
        print("\nNext steps:")
        print("1. Install streamlit: pip install streamlit pandas plotly")
        print("2. Run dashboard: streamlit run dashboard.py")
        print("3. Access at: http://localhost:8501")
        
        print("\nMVP Features Available:")
        print("✅ SQLite database with trade data")
        print("✅ ETL pipeline for data processing")
        print("✅ Analytics dashboard with charts")
        print("✅ REST API endpoints")
        print("✅ Anomaly detection system")
        print("✅ Alert configuration system")
        
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("Please check the output above for error details")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
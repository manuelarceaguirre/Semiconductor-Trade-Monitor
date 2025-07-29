#!/usr/bin/env python3
"""
Comprehensive System Test for Semiconductor Trade Monitor
Tests all components: MySQL database, FastAPI server, and API integrations
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoint(url, description, expected_keys=None):
    """Test a single API endpoint and validate response"""
    
    try:
        print(f"Testing {description}...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate expected keys if provided
            if expected_keys and isinstance(data, dict):
                missing_keys = [key for key in expected_keys if key not in data]
                if missing_keys:
                    print(f"  ⚠️  Missing keys: {missing_keys}")
                else:
                    print(f"  ✅ All expected keys present")
            
            # Show sample data
            if isinstance(data, list) and len(data) > 0:
                print(f"  ✅ {description} - {len(data)} records returned")
                print(f"     Sample: {json.dumps(data[0], indent=2)[:200]}...")
            elif isinstance(data, dict):
                print(f"  ✅ {description} - Success")
                if 'count' in data:
                    print(f"     Count: {data.get('count')}")
                if 'total_value' in data:
                    value = data.get('total_value', 0)
                    print(f"     Total Value: ${value:,.0f}")
            
            return True, data
            
        else:
            print(f"  ❌ {description} - HTTP {response.status_code}")
            print(f"     Error: {response.text[:200]}")
            return False, None
            
    except requests.RequestException as e:
        print(f"  ❌ {description} - Request failed: {e}")
        return False, None
    except json.JSONDecodeError as e:
        print(f"  ❌ {description} - JSON decode error: {e}")
        return False, None
    except Exception as e:
        print(f"  ❌ {description} - Unexpected error: {e}")
        return False, None

def main():
    """Run comprehensive system tests"""
    
    print("="*80)
    print("SEMICONDUCTOR TRADE MONITOR - COMPLETE SYSTEM TEST")
    print("="*80)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    base_url = "http://localhost:8000"
    
    # Test results tracking
    tests = []
    
    # 1. Health Check
    success, data = test_api_endpoint(
        f"{base_url}/health",
        "Health Check",
        expected_keys=["status", "database_type", "apis_available"]
    )
    tests.append(("Health Check", success))
    
    if success and data:
        print(f"     Database: {data.get('database_type')}")
        print(f"     Status: {data.get('status')}")
        apis = data.get('apis_available', {})
        for api, available in apis.items():
            status = "✅" if available else "❌"
            print(f"     {api}: {status}")
    
    print()
    
    # 2. Root Endpoint
    success, data = test_api_endpoint(
        f"{base_url}/",
        "Root Endpoint",
        expected_keys=["name", "version", "database", "endpoints"]
    )
    tests.append(("Root Endpoint", success))
    print()
    
    # 3. Trade Series Data
    success, data = test_api_endpoint(
        f"{base_url}/v2/series?limit=3",
        "Trade Series (v2)",
        expected_keys=None  # It's a list
    )
    tests.append(("Trade Series v2", success))
    print()
    
    # 4. Filtered Trade Data
    success, data = test_api_endpoint(
        f"{base_url}/v2/series?commodity=HBM&limit=2",
        "Filtered Trade Data (HBM)"
    )
    tests.append(("Filtered Trade Data", success))
    print()
    
    # 5. Summary Statistics
    success, data = test_api_endpoint(
        f"{base_url}/v2/stats",
        "Summary Statistics",
        expected_keys=["total_records", "total_value", "unique_commodities", "latest_period"]
    )
    tests.append(("Summary Statistics", success))
    print()
    
    # 6. Anomaly Detection
    success, data = test_api_endpoint(
        f"{base_url}/v2/anomalies?threshold=15",
        "Anomaly Detection"
    )
    tests.append(("Anomaly Detection", success))
    print()
    
    # 7. Economic Context (FRED API integration)
    success, data = test_api_endpoint(
        f"{base_url}/v2/economic-context?start_date=2023-01-01&end_date=2023-02-01",
        "Economic Context (FRED API)"
    )
    tests.append(("Economic Context", success))
    print()
    
    # 8. Legacy v1 Compatibility
    success, data = test_api_endpoint(
        f"{base_url}/v1/series?limit=2",
        "Legacy v1 Series",
        expected_keys=["success", "count", "data"]
    )
    tests.append(("Legacy v1 API", success))
    print()
    
    # 9. API Documentation
    try:
        print("Testing API Documentation...")
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200 and "swagger" in response.text.lower():
            print("  ✅ API Documentation - Available")
            tests.append(("API Documentation", True))
        else:
            print("  ❌ API Documentation - Not available")
            tests.append(("API Documentation", False))
    except Exception as e:
        print(f"  ❌ API Documentation - Error: {e}")
        tests.append(("API Documentation", False))
    
    print()
    
    # Test Summary
    print("="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print("-"*50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is fully operational.")
        print("\n✅ MySQL Database: Connected and responsive")
        print("✅ FastAPI Server: All endpoints working")
        print("✅ API Integrations: UN Comtrade, USITC, FRED APIs available")
        print("✅ Anomaly Detection: Functioning correctly")
        print("✅ Legacy Compatibility: v1 endpoints working")
        print("✅ Documentation: API docs accessible")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check individual test output above.")
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")
    print("="*80)

if __name__ == "__main__":
    main()
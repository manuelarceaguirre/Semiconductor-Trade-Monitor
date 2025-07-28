#!/usr/bin/env python3
"""
Test script to validate UN Comtrade API access for semiconductor trade data.
Tests the key HS codes from the PRD: 854232 (HBM/DRAM), 854231 (GPUs), 848620 (Lithography)
Updated for 2025 API format
"""

import requests
import json
import time
from datetime import datetime

class ComtradeAPITester:
    def __init__(self):
        # New API base URLs for 2025
        self.new_api_base = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
        self.preview_api_base = "https://comtradeapi.un.org/data/v1/getDA/C/A/HS"
        self.public_api_base = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
        self.semiconductor_codes = {
            "854232": "HBM/DRAM/SRAM ICs", 
            "854231": "GPU/AI Accelerators",
            "848620": "Lithography Tools"
        }
        self.key_countries = {
            "410": "Korea",
            "156": "China", 
            "158": "Taiwan",
            "392": "Japan",
            "840": "USA"
        }
    
    def test_new_api_call(self, hs_code, reporter="410", partner="158", year="2022"):
        """Test using the new Comtrade API format (2025)"""
        
        # Correct 2025 API format: https://comtradeapi.un.org/public/v1/preview/C/A/HS?[params]
        params = {
            'period': year,
            'reporterCode': reporter,
            'partnerCode': partner,
            'cmdCode': hs_code
        }
        
        print(f"Testing NEW API: {self.semiconductor_codes.get(hs_code, hs_code)} ({hs_code})")
        print(f"Route: {self.key_countries.get(reporter, reporter)} imports from {self.key_countries.get(partner, partner)}")
        print(f"URL: {self.public_api_base}")
        print(f"Params: {params}")
        
        try:
            # Try public API first (free, no auth required)
            response = requests.get(self.public_api_base, params=params, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Try different possible data keys
                records = data.get('data', data.get('results', data.get('dataset', [])))
                
                if records:
                    record_count = len(records)
                    print(f"✓ Success: {record_count} records found")
                    
                    # Show sample record
                    sample = records[0]
                    trade_value = sample.get('primaryValue', sample.get('TradeValue', sample.get('value', 'N/A')))
                    print(f"  Sample trade value: ${trade_value}")
                    print(f"  Sample record keys: {list(sample.keys())}")
                    return True
                else:
                    print("✗ No data found for this query")
                    print(f"  Full response: {json.dumps(data, indent=2)[:300]}...")
                    return False
            elif response.status_code == 401:
                print("✗ Authentication required - need API token")
                print("  Next step: Register at https://comtradedeveloper.un.org")
                return False
            elif response.status_code == 403:
                print("✗ Access forbidden - subscription key required")
                print("  Next step: Get subscription key from https://comtradedeveloper.un.org/profile")
                return False
            else:
                print(f"✗ API Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"✗ Request failed: {str(e)}")
            return False
        
        finally:
            print("-" * 60)
            time.sleep(2)  # Respect rate limits
    
    def run_basic_tests(self):
        """Run basic tests for all semiconductor HS codes using new API"""
        print("=" * 60)
        print("UN COMTRADE API TEST - SEMICONDUCTOR MONITOR (2025)")
        print(f"Test started: {datetime.now()}")
        print("=" * 60)
        
        results = {}
        
        # Test each semiconductor HS code using new API
        for hs_code in self.semiconductor_codes.keys():
            success = self.test_new_api_call(hs_code)
            results[hs_code] = success
        
        # Summary
        print("\nTEST SUMMARY:")
        success_count = sum(results.values())
        total_count = len(results)
        
        for hs_code, success in results.items():
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{hs_code} ({self.semiconductor_codes[hs_code]}): {status}")
        
        print(f"\nOverall: {success_count}/{total_count} tests passed")
        
        if success_count > 0:
            print("\n✓ NEW API is accessible - proceeding with ETL development")
            print("\nAPI DETAILS:")
            print("- Using UN Comtrade new API (2025)")
            print("- Base URL: https://comtradeapi.un.org/data/v1/getDA/C/A/HS")
            print("- Rate limits apply - authentication recommended for production")
        else:
            print("\n✗ API access issues - authentication likely required")
            print("\nNEXT STEPS:")
            print("1. Register at https://comtradedeveloper.un.org")
            print("2. Get free API subscription key from profile page")
            print("3. Update API calls with 'subscription-key' parameter")
            print("4. Test authenticated access with production data")
        
        return results

if __name__ == "__main__":
    tester = ComtradeAPITester()
    tester.run_basic_tests()
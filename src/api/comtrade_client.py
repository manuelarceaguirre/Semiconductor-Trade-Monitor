#!/usr/bin/env python3
"""
UN Comtrade API Client for Semiconductor Trade Monitor
Handles authenticated API requests and data extraction for semiconductor trade data
Uses the official comtradeapicall library
"""

import time
import json
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import comtradeapicall

# Load environment variables
load_dotenv()

class ComtradeAPIClient:
    """UN Comtrade API client with rate limiting and error handling"""
    
    def __init__(self):
        self.api_key = os.getenv('UN_COMTRADE_API_KEY')
        self.base_url = "https://comtradeapi.un.org/data/v1/getDA"
        self.rate_limit = 100  # requests per minute for authenticated users
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        
        # Semiconductor HS codes we're monitoring
        self.target_hs_codes = {
            "854232": "HBM/DRAM/SRAM ICs",
            "854231": "GPU/AI Accelerators", 
            "848620": "Lithography Tools"
        }
        
        # Key trading countries/regions  
        self.key_countries = {
            "KOR": 410,  # South Korea
            "TWN": 158,  # Taiwan
            "USA": 842,  # United States
            "CHN": 156,  # China
            "JPN": 392,  # Japan
            "NLD": 528,  # Netherlands
            "DEU": 276,  # Germany
            "SGP": 702,  # Singapore
            "MYS": 458,  # Malaysia
            "THA": 764   # Thailand
        }
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting (100 requests per minute)"""
        current_time = time.time()
        
        # Reset counter if we're in a new minute window
        if current_time - self.request_window_start >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        # If we've hit the rate limit, wait
        if self.request_count >= self.rate_limit:
            wait_time = 60 - (current_time - self.request_window_start)
            if wait_time > 0:
                print(f"Rate limit reached, waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        # Minimum delay between requests to be respectful
        time_since_last = current_time - self.last_request_time
        if time_since_last < 0.6:  # 100 req/min = 1 request per 0.6 seconds
            time.sleep(0.6 - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_trade_data(self, 
                      typeCode: str = "C",  # C=commodities, S=services
                      freqCode: str = "A",  # A=annual, M=monthly
                      clCode: str = "HS",   # HS=Harmonized System
                      period: str = "2023",
                      reporterCode: str = "410",  # South Korea
                      cmdCode: str = "854232",    # HBM/DRAM
                      flowCode: str = "X",        # X=exports, M=imports
                      partnerCode: Optional[str] = None,  # Taiwan
                      maxRecords: int = 250) -> Dict[str, Any]:
        """
        Get trade data from UN Comtrade API using official library
        
        Args:
            typeCode: C=commodities, S=services
            freqCode: A=annual, M=monthly  
            clCode: HS=Harmonized System
            period: Year (2023) or range (2022,2023)
            reporterCode: ISO3 numeric code of reporting country
            cmdCode: Commodity code (HS6 format)
            flowCode: X=exports, M=imports
            partnerCode: ISO3 numeric code of partner country (optional)
            maxRecords: Maximum records to return
            
        Returns:
            Dictionary containing API response data
        """
        
        if not self.api_key:
            raise ValueError("UN_COMTRADE_API_KEY not found in environment variables")
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        try:
            print(f"Requesting: {cmdCode} from {reporterCode} to {partnerCode or 'all'} for {period}")
            
            # Use the official comtradeapicall library
            if partnerCode:
                # Specific partner
                df = comtradeapicall.getFinalData(
                    subscription_key=self.api_key,
                    typeCode=typeCode,
                    freqCode=freqCode,
                    clCode=clCode,
                    period=period,
                    reporterCode=reporterCode,
                    cmdCode=cmdCode,
                    flowCode=flowCode,
                    partnerCode=partnerCode,
                    partner2Code="0",  # Required parameter, 0 for none
                    customsCode="C00",  # Required parameter, C00 for customs territory
                    motCode="0",       # Required parameter, 0 for all modes of transport
                    maxRecords=maxRecords
                )
            else:
                # All partners  
                df = comtradeapicall.getFinalData(
                    subscription_key=self.api_key,
                    typeCode=typeCode,
                    freqCode=freqCode,
                    clCode=clCode,
                    period=period,
                    reporterCode=reporterCode,
                    cmdCode=cmdCode,
                    flowCode=flowCode,
                    partnerCode="0",   # 0 for all partners
                    partner2Code="0",  # Required parameter, 0 for none
                    customsCode="C00",  # Required parameter, C00 for customs territory
                    motCode="0",       # Required parameter, 0 for all modes of transport
                    maxRecords=maxRecords
                )
            
            if df is not None and not df.empty:
                # Convert DataFrame to list of dictionaries
                data_records = df.to_dict('records')
                
                return {
                    "success": True,
                    "count": len(data_records),
                    "data": data_records,
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "period": period,
                        "reporter": reporterCode,
                        "partner": partnerCode,
                        "commodity": cmdCode
                    }
                }
            else:
                print(f"No data returned for {cmdCode} from {reporterCode}")
                return {
                    "success": True,
                    "count": 0,
                    "data": [],
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "period": period,
                        "reporter": reporterCode,
                        "partner": partnerCode,
                        "commodity": cmdCode
                    }
                }
                
        except Exception as e:
            print(f"API request failed: {e}")
            return {"error": str(e), "data": []}
    
    def get_semiconductor_trade_flows(self, 
                                    year: str = "2023",
                                    flow_type: str = "X",  # X=exports, M=imports
                                    max_records_per_request: int = 250) -> List[Dict[str, Any]]:
        """
        Get comprehensive semiconductor trade flows for key countries and commodities
        
        Args:
            year: Year to fetch data for
            flow_type: X=exports, M=imports  
            max_records_per_request: Max records per API call
            
        Returns:
            List of trade flow records
        """
        
        all_data = []
        total_requests = 0
        
        print(f"Fetching {year} semiconductor {'exports' if flow_type == 'X' else 'imports'} data...")
        
        # Key trade routes based on semiconductor supply chain
        priority_routes = [
            ("410", "158", "854232"),  # KOR -> TWN: HBM/DRAM
            ("158", "842", "854231"),  # TWN -> USA: GPU/AI
            ("528", "158", "848620"),  # NLD -> TWN: Lithography
            ("410", "842", "854232"),  # KOR -> USA: Memory
            ("158", "156", "854231"),  # TWN -> CHN: Processors
            ("392", "158", "854232"),  # JPN -> TWN: Memory components
        ]
        
        # Fetch priority routes first
        for reporter, partner, hs_code in priority_routes:
            try:
                result = self.get_trade_data(
                    period=year,
                    reporterCode=reporter,
                    partnerCode=partner,
                    cmdCode=hs_code,
                    flowCode=flow_type,
                    maxRecords=max_records_per_request
                )
                
                total_requests += 1
                
                if result.get("success") and result.get("data"):
                    all_data.extend(result["data"])
                    print(f"✓ Got {len(result['data'])} records for {hs_code}: {reporter}→{partner}")
                else:
                    print(f"✗ No data for {hs_code}: {reporter}→{partner}")
                    
            except Exception as e:
                print(f"Error fetching {reporter}→{partner} {hs_code}: {e}")
                continue
        
        # Add broader search for other significant flows
        for hs_code in self.target_hs_codes.keys():
            for reporter_iso, reporter_code in self.key_countries.items():
                try:
                    # Get top partners for this reporter-commodity combination
                    result = self.get_trade_data(
                        period=year,
                        reporterCode=str(reporter_code),
                        partnerCode="all",  # All partners
                        cmdCode=hs_code,
                        flowCode=flow_type,
                        maxRecords=50  # Top 50 partners
                    )
                    
                    total_requests += 1
                    
                    if result.get("success") and result.get("data"):
                        # Filter for significant trade values (>$1M)
                        significant_flows = [
                            record for record in result["data"] 
                            if record.get("primaryValue", 0) > 1000000
                        ]
                        
                        if significant_flows:
                            all_data.extend(significant_flows)
                            print(f"✓ Got {len(significant_flows)} significant flows for {hs_code} from {reporter_iso}")
                    
                    # Don't overwhelm the API
                    if total_requests >= 50:  # Reasonable limit for initial run
                        print(f"Reached request limit ({total_requests}), stopping...")
                        break
                        
                except Exception as e:
                    print(f"Error fetching broad data for {reporter_iso} {hs_code}: {e}")
                    continue
                    
            if total_requests >= 50:
                break
        
        print(f"Completed {total_requests} API requests, got {len(all_data)} total records")
        return all_data
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Test API connection and authentication"""
        
        print("Testing UN Comtrade API connection...")
        
        if not self.api_key:
            return {
                "success": False,
                "error": "No API key found in environment variables"
            }
        
        # Simple test request - South Korea HBM exports to Taiwan in 2023
        try:
            result = self.get_trade_data(
                period="2023",
                reporterCode="410",  # South Korea
                partnerCode="158",   # Taiwan  
                cmdCode="854232",    # HBM/DRAM
                flowCode="X",        # Exports
                maxRecords=10
            )
            
            if result.get("success"):
                count = result.get("count", 0)
                print(f"✓ API connection successful - found {count} records")
                return {
                    "success": True,
                    "records_found": count,
                    "sample_data": result.get("data", [])[:2]  # First 2 records
                }
            else:
                print(f"✗ API request failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error")
                }
                
        except Exception as e:
            print(f"✗ API test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

if __name__ == "__main__":
    # Test the Comtrade API client
    client = ComtradeAPIClient()
    
    # Test connection
    test_result = client.test_api_connection()
    
    if test_result["success"]:
        print("\n" + "="*60)
        print("UN COMTRADE API CLIENT - SUCCESS!")
        print(f"Found {test_result['records_found']} records")
        if test_result["sample_data"]:
            print("Sample record:")
            sample = test_result["sample_data"][0]
            print(f"- Period: {sample.get('period')}")
            print(f"- Trade Value: ${sample.get('primaryValue', 0):,.0f}")
            print(f"- Commodity: {sample.get('cmdDesc', 'N/A')}")
        print("="*60)
    else:
        print(f"\n❌ API test failed: {test_result['error']}")
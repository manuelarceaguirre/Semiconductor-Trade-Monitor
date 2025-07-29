#!/usr/bin/env python3
"""
FRED API Client for Semiconductor Trade Monitor
Fetches economic context data from Federal Reserve Economic Data (FRED)
"""

import requests
import time
import json
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FREDAPIClient:
    """FRED (Federal Reserve Economic Data) API client for economic indicators"""
    
    def __init__(self):
        self.api_key = os.getenv('FRED_API_KEY')
        self.base_url = "https://api.stlouisfed.org/fred"
        self.rate_limit = 120  # 120 requests per minute
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        
        # Key economic indicators for semiconductor industry context
        self.key_indicators = {
            # Trade and Economy
            "GDPC1": "US GDP (Real, Quarterly)",
            "GDPPOT": "US GDP Potential (Real, Quarterly)", 
            "IMPGS": "US Imports of Goods and Services",
            "EXPGS": "US Exports of Goods and Services",
            "BOPGSTB": "US Trade Balance",
            
            # Technology and Manufacturing
            "INDPRO": "US Industrial Production Index",
            "CAPUTLG3274S": "US Semiconductor Manufacturing Capacity Utilization",
            "PCU334413334413": "Producer Price Index: Semiconductors",
            "IPG334413S": "Industrial Production: Semiconductors",
            
            # Financial and Business
            "FEDFUNDS": "Federal Funds Rate",
            "DGS10": "10-Year Treasury Rate", 
            "VIXCLS": "VIX Volatility Index",
            "NASDAQCOM": "NASDAQ Composite Index",
            
            # Global Context
            "DEXUSEU": "US/Euro Exchange Rate",
            "DEXJPUS": "Japan/US Exchange Rate",
            "DEXKOUS": "South Korea/US Exchange Rate",
            "DEXTAUS": "Taiwan/US Exchange Rate",
            
            # Technology Sector
            "PAYEMS": "US Total Nonfarm Payrolls",
            "UNRATE": "US Unemployment Rate",
            "CPIALLMINFD": "US CPI All Items Less Food and Energy"
        }
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting (120 requests per minute)"""
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
        
        # Minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < 0.5:  # 120 req/min = 1 request per 0.5 seconds
            time.sleep(0.5 - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def get_series_data(self,
                       series_id: str,
                       start_date: str = "2020-01-01",
                       end_date: Optional[str] = None,
                       frequency: str = "m",  # d, w, bw, m, q, sa, a
                       aggregation_method: str = "avg",  # avg, sum, eop
                       units: str = "lin") -> Dict[str, Any]:  # lin, chg, ch1, pch, pc1, pca, cch, cca, log
        """
        Get economic time series data from FRED
        
        Args:
            series_id: FRED series identifier (e.g., "GDPC1")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (defaults to today)
            frequency: Data frequency (d=daily, w=weekly, m=monthly, q=quarterly, a=annual)
            aggregation_method: How to aggregate data (avg=average, sum=sum, eop=end of period)
            units: Data transformation (lin=levels, chg=change, pch=percent change, etc.)
            
        Returns:
            Dictionary containing series data and metadata
        """
        
        if not self.api_key:
            raise ValueError("FRED_API_KEY not found in environment variables")
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Rate limiting
        self._wait_for_rate_limit()
        
        # Build API request
        endpoint = f"{self.base_url}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
            "frequency": frequency,
            "aggregation_method": aggregation_method,
            "units": units,
            "sort_order": "asc"
        }
        
        try:
            print(f"Requesting FRED series: {series_id} ({start_date} to {end_date})")
            
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse FRED response structure
            if 'observations' in data:
                observations = data['observations']
                
                # Filter out missing values (FRED uses "." for missing data)
                valid_observations = [
                    obs for obs in observations 
                    if obs.get('value') != '.' and obs.get('value') is not None
                ]
                
                # Convert values to float
                for obs in valid_observations:
                    try:
                        obs['value'] = float(obs['value'])
                    except (ValueError, TypeError):
                        obs['value'] = None
                
                return {
                    "success": True,
                    "series_id": series_id,
                    "count": len(valid_observations),
                    "data": valid_observations,
                    "metadata": {
                        "source": "FRED",
                        "timestamp": datetime.now().isoformat(),
                        "start_date": start_date,
                        "end_date": end_date,
                        "frequency": frequency,
                        "units": units,
                        "description": self.key_indicators.get(series_id, f"FRED Series {series_id}")
                    }
                }
            else:
                print(f"No observations found for series {series_id}")
                return {"success": False, "error": "No observations found", "data": []}
                
        except requests.exceptions.RequestException as e:
            print(f"FRED API request failed: {e}")
            return {"error": str(e), "data": []}
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {"error": "Invalid JSON response", "data": []}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"error": str(e), "data": []}
    
    def get_multiple_series(self,
                           series_ids: List[str],
                           start_date: str = "2020-01-01",
                           end_date: Optional[str] = None,
                           frequency: str = "m") -> Dict[str, Any]:
        """
        Get multiple economic time series data from FRED
        
        Args:
            series_ids: List of FRED series identifiers
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            frequency: Data frequency
            
        Returns:
            Dictionary containing all series data
        """
        
        all_series_data = {}
        successful_requests = 0
        
        print(f"Fetching {len(series_ids)} economic indicators from FRED...")
        
        for series_id in series_ids:
            try:
                result = self.get_series_data(
                    series_id=series_id,
                    start_date=start_date,
                    end_date=end_date,
                    frequency=frequency
                )
                
                if result.get("success"):
                    all_series_data[series_id] = result
                    successful_requests += 1
                    print(f"✓ {series_id}: {result.get('count', 0)} observations")
                else:
                    print(f"✗ {series_id}: {result.get('error', 'No data')}")
                    
            except Exception as e:
                print(f"Error fetching {series_id}: {e}")
                continue
        
        return {
            "success": True,
            "total_series": len(series_ids),
            "successful_requests": successful_requests,
            "data": all_series_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_semiconductor_context_data(self,
                                     start_date: str = "2020-01-01",
                                     end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive economic context data relevant to semiconductor trade
        
        Args:
            start_date: Start date for data collection
            end_date: End date for data collection
            
        Returns:
            Dictionary containing relevant economic indicators
        """
        
        # Priority indicators for semiconductor trade analysis
        priority_indicators = [
            "GDPC1",        # US GDP
            "IMPGS",        # US Imports
            "EXPGS",        # US Exports  
            "INDPRO",       # Industrial Production
            "NASDAQCOM",    # NASDAQ (tech-heavy index)
            "FEDFUNDS",     # Federal Funds Rate
            "DEXJPUS",      # Japan/US Exchange Rate
            "DEXKOUS",      # South Korea/US Exchange Rate
            "VIXCLS",       # VIX Volatility
            "UNRATE"        # Unemployment Rate
        ]
        
        return self.get_multiple_series(
            series_ids=priority_indicators,
            start_date=start_date,
            end_date=end_date,
            frequency="m"  # Monthly data
        )
    
    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata information about a FRED series
        
        Args:
            series_id: FRED series identifier
            
        Returns:
            Dictionary containing series metadata
        """
        
        if not self.api_key:
            raise ValueError("FRED_API_KEY not found in environment variables")
        
        self._wait_for_rate_limit()
        
        endpoint = f"{self.base_url}/series"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'seriess' in data and len(data['seriess']) > 0:
                series_info = data['seriess'][0]
                return {
                    "success": True,
                    "series_id": series_id,
                    "info": series_info
                }
            else:
                return {"success": False, "error": "Series not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Test FRED API connection and authentication"""
        
        print("Testing FRED API connection...")
        
        if not self.api_key:
            return {
                "success": False,
                "error": "No FRED API key found in environment variables"
            }
        
        # Simple test request - US GDP data
        try:
            result = self.get_series_data(
                series_id="GDPC1",  # Real GDP
                start_date="2023-01-01",
                end_date="2023-12-31",
                frequency="q"  # Quarterly
            )
            
            if result.get("success"):
                count = result.get("count", 0)
                print(f"✓ FRED API connection successful - found {count} GDP observations")
                return {
                    "success": True,
                    "records_found": count,
                    "sample_data": result.get("data", [])[:2],  # First 2 records
                    "description": result.get("metadata", {}).get("description")
                }
            else:
                print(f"✗ FRED API request failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error")
                }
                
        except Exception as e:
            print(f"✗ FRED API test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

if __name__ == "__main__":
    # Test the FRED API client
    client = FREDAPIClient()
    
    # Test connection
    test_result = client.test_api_connection()
    
    if test_result["success"]:
        print("\n" + "="*60)
        print("FRED API CLIENT - SUCCESS!")
        print(f"Found {test_result['records_found']} GDP records")
        print(f"Description: {test_result['description']}")
        if test_result["sample_data"]:
            print("Sample data:")
            for i, record in enumerate(test_result["sample_data"], 1):
                date = record.get('date')
                value = record.get('value')
                print(f"  {i}. {date}: ${value:,.0f}B (if applicable)")
        print("="*60)
        
        # Test semiconductor context data
        print("\nTesting semiconductor context indicators...")
        context_result = client.get_semiconductor_context_data(
            start_date="2023-01-01",
            end_date="2023-06-30"
        )
        
        if context_result.get("success"):
            print(f"✓ Retrieved {context_result['successful_requests']}/{context_result['total_series']} indicators")
    else:
        print(f"\n❌ FRED API test failed: {test_result['error']}")
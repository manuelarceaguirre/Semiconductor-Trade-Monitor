#!/usr/bin/env python3
"""
US ITC DataWeb API Client for Semiconductor Trade Monitor
Handles US trade data requests using the USITC API
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

class USITCAPIClient:
    """US ITC DataWeb API client for US trade data"""
    
    def __init__(self):
        self.api_token = os.getenv('USITC_API_TOKEN')
        self.base_url = "https://datawebws.usitc.gov/dataweb"
        self.rate_limit = None  # No documented rate limits for USITC
        
        # US HTS codes mapping to our HS codes
        self.target_hts_codes = {
            # HTS codes are more detailed than HS codes
            "8542321000": "HBM/DRAM Memory", 
            "8542311000": "GPU Processors",
            "8542319000": "Other Processors",
            "8486203000": "Lithography Equipment",
            "8542900000": "Other Semiconductor Parts"
        }
        
        # Key trading partners for US
        self.key_partners = {
            "Taiwan": "TW",
            "South Korea": "KR", 
            "China": "CN",
            "Japan": "JP",
            "Singapore": "SG",
            "Malaysia": "MY",
            "Philippines": "PH",
            "Thailand": "TH",
            "Netherlands": "NL",
            "Germany": "DE"
        }
    
    def get_trade_data(self,
                      hts_code: str = "8542900000",
                      trade_flow: str = "imports",  # "imports" or "exports"
                      partner_country: Optional[str] = None,
                      start_year: int = 2022,
                      end_year: int = 2023,
                      frequency: str = "annual") -> Dict[str, Any]:
        """
        Get US trade data from USITC DataWeb API
        
        Args:
            hts_code: US HTS code (10-digit)
            trade_flow: "imports" or "exports"
            partner_country: ISO2 country code (e.g., "TW" for Taiwan)
            start_year: Starting year
            end_year: Ending year
            frequency: "annual" or "monthly"
            
        Returns:
            Dictionary containing API response data
        """
        
        if not self.api_token:
            raise ValueError("USITC_API_TOKEN not found in environment variables")
        
        # Build API endpoint URL
        endpoint = f"{self.base_url}/api/v2/report2/runReport"
        
        # Build the query payload for USITC DataWeb API
        # This structure is based on the official API documentation
        query_payload = {
            "reportName": "TradeQuery",
            "format": "JSON",
            "query": {
                "tradeFlow": "IMP" if trade_flow == "imports" else "EXP",
                "htsNumbers": [hts_code],
                "timeRange": {
                    "startYear": start_year,
                    "endYear": end_year,
                    "frequency": frequency.upper()
                }
            }
        }
        
        # Add partner country filter if specified
        if partner_country:
            query_payload["query"]["partnerCountries"] = [partner_country]
        
        # Set authorization headers
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "User-Agent": "SemiconductorTradeMonitor/1.0"
        }
        
        try:
            print(f"Requesting US {trade_flow}: {hts_code} from {partner_country or 'all partners'} ({start_year}-{end_year})")
            
            response = requests.post(endpoint, json=query_payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response structure based on USITC API format
            if isinstance(data, dict):
                if 'results' in data:
                    trade_data = data['results']
                elif 'data' in data:
                    trade_data = data['data']
                else:
                    trade_data = [data]
            elif isinstance(data, list):
                trade_data = data
            else:
                trade_data = []
            
            return {
                "success": True,
                "count": len(trade_data),
                "data": trade_data,
                "metadata": {
                    "source": "USITC DataWeb",
                    "timestamp": datetime.now().isoformat(),
                    "hts_code": hts_code,
                    "trade_flow": trade_flow,
                    "partner": partner_country,
                    "period": f"{start_year}-{end_year}",
                    "query_payload": query_payload
                }
            }
            
        except requests.exceptions.RequestException as e:
            print(f"USITC API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response content: {e.response.text}")
            return {"error": str(e), "data": []}
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {"error": "Invalid JSON response", "data": []}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"error": str(e), "data": []}
    
    def get_us_semiconductor_imports(self, 
                                   year: int = 2023,
                                   top_n_partners: int = 10) -> List[Dict[str, Any]]:
        """
        Get comprehensive US semiconductor imports for key HTS codes and partners
        
        Args:
            year: Year to fetch data for
            top_n_partners: Number of top partners to include
            
        Returns:
            List of trade flow records
        """
        
        all_data = []
        
        print(f"Fetching US semiconductor imports for {year}...")
        
        # Priority HTS codes for semiconductors
        priority_codes = [
            "8542321000",  # DRAM Memory
            "8542311000",  # GPU Processors
            "8542319000",  # Other Processors  
            "8542900000",  # Other Semiconductor Parts
        ]
        
        # Get data for each HTS code
        for hts_code in priority_codes:
            description = self.target_hts_codes.get(hts_code, f"HTS {hts_code}")
            
            try:
                # Get imports from all partners
                result = self.get_trade_data(
                    hts_code=hts_code,
                    trade_flow="imports",
                    partner_country=None,  # All partners
                    start_year=year,
                    end_year=year,
                    frequency="annual"
                )
                
                if result.get("success") and result.get("data"):
                    # Add commodity description to each record
                    for record in result["data"]:
                        record["commodity_description"] = description
                        record["hts_code"] = hts_code
                    
                    all_data.extend(result["data"])
                    print(f"✓ Got {len(result['data'])} records for {description}")
                else:
                    print(f"✗ No data for {description}")
                    
                # Small delay to be respectful
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching {hts_code}: {e}")
                continue
        
        # Sort by trade value and get top partners
        if all_data:
            # Assuming the API returns value in a field like 'value' or 'trade_value'
            # This will need to be adjusted based on actual API response structure
            try:
                all_data.sort(key=lambda x: float(x.get('value', 0) or 0), reverse=True)
            except:
                pass  # If sorting fails, continue with unsorted data
        
        print(f"Total records retrieved: {len(all_data)}")
        return all_data[:top_n_partners * len(priority_codes)]  # Limit results
    
    def get_bilateral_trade(self,
                          partner_country: str,
                          year: int = 2023,
                          include_exports: bool = True,
                          include_imports: bool = True) -> Dict[str, Any]:
        """
        Get bilateral US trade data with a specific partner
        
        Args:
            partner_country: ISO2 country code (e.g., "TW", "KR")
            year: Year to fetch data for
            include_exports: Include US exports to partner
            include_imports: Include US imports from partner
            
        Returns:
            Dictionary with bilateral trade data
        """
        
        results = {
            "partner": partner_country,
            "year": year,
            "exports": [],
            "imports": [],
            "total_trade_value": 0
        }
        
        print(f"Fetching bilateral trade with {partner_country} for {year}...")
        
        # Get data for key semiconductor codes
        for hts_code, description in self.target_hts_codes.items():
            
            # Get exports if requested
            if include_exports:
                try:
                    export_result = self.get_trade_data(
                        hts_code=hts_code,
                        trade_flow="exports",
                        partner_country=partner_country,
                        start_year=year,
                        end_year=year
                    )
                    
                    if export_result.get("success") and export_result.get("data"):
                        for record in export_result["data"]:
                            record["flow_type"] = "exports"
                            record["commodity_description"] = description
                        results["exports"].extend(export_result["data"])
                        
                except Exception as e:
                    print(f"Error fetching exports for {hts_code}: {e}")
            
            # Get imports if requested  
            if include_imports:
                try:
                    import_result = self.get_trade_data(
                        hts_code=hts_code,
                        trade_flow="imports",
                        partner_country=partner_country,
                        start_year=year,
                        end_year=year
                    )
                    
                    if import_result.get("success") and import_result.get("data"):
                        for record in import_result["data"]:
                            record["flow_type"] = "imports"
                            record["commodity_description"] = description
                        results["imports"].extend(import_result["data"])
                        
                except Exception as e:
                    print(f"Error fetching imports for {hts_code}: {e}")
            
            time.sleep(0.3)  # Be respectful to the API
        
        # Calculate total trade value
        total_value = 0
        for record in results["exports"] + results["imports"]:
            try:
                value = float(record.get('value', 0) or 0)
                total_value += value
            except:
                pass
        
        results["total_trade_value"] = total_value
        
        return results
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Test USITC API connection and authentication"""
        
        print("Testing USITC DataWeb API connection...")
        
        if not self.api_token:
            return {
                "success": False,
                "error": "No USITC API token found in environment variables"
            }
        
        # Simple test request - US semiconductor imports from Taiwan
        try:
            result = self.get_trade_data(
                hts_code="8542900000",  # Broad semiconductor category
                trade_flow="imports",
                partner_country="TW",   # Taiwan
                start_year=2022,
                end_year=2022,
                frequency="annual"
            )
            
            if result.get("success"):
                count = result.get("count", 0)
                print(f"✓ USITC API connection successful - found {count} records")
                return {
                    "success": True,
                    "records_found": count,
                    "sample_data": result.get("data", [])[:2]  # First 2 records
                }
            else:
                print(f"✗ USITC API request failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error")
                }
                
        except Exception as e:
            print(f"✗ USITC API test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

if __name__ == "__main__":
    # Test the USITC API client
    client = USITCAPIClient()
    
    # Test connection
    test_result = client.test_api_connection()
    
    if test_result["success"]:
        print("\n" + "="*60)
        print("USITC DATAWEB API CLIENT - SUCCESS!")
        print(f"Found {test_result['records_found']} records")
        if test_result["sample_data"]:
            print("Sample record fields:")
            sample = test_result["sample_data"][0]
            for key, value in sample.items():
                print(f"- {key}: {value}")
        print("="*60)
    else:
        print(f"\n❌ USITC API test failed: {test_result['error']}")
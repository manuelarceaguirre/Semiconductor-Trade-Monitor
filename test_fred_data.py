#!/usr/bin/env python3
"""Test FRED API with properly formatted requests"""

from src.api.fred_client import FREDAPIClient

def main():
    client = FREDAPIClient()
    
    print("=== FRED API Semiconductor Context Test ===\n")
    
    # Test individual series with correct frequencies
    test_series = [
        ("INDPRO", "m", "US Industrial Production Index"),
        ("NASDAQCOM", "m", "NASDAQ Composite (Tech Index)"),
        ("FEDFUNDS", "m", "Federal Funds Rate"),
        ("DEXJPUS", "m", "Japan/US Exchange Rate"),
        ("DEXKOUS", "m", "South Korea/US Exchange Rate"),
        ("VIXCLS", "m", "VIX Volatility Index"),
        ("UNRATE", "m", "US Unemployment Rate"),
        ("GDPC1", "q", "US Real GDP (Quarterly)"),
        ("IMPGS", "q", "US Imports (Quarterly)"),
        ("EXPGS", "q", "US Exports (Quarterly)")
    ]
    
    for series_id, freq, description in test_series:
        print(f"Testing {series_id} ({description})...")
        
        result = client.get_series_data(
            series_id=series_id,
            start_date="2023-01-01",
            end_date="2023-12-31",
            frequency=freq
        )
        
        if result.get('success'):
            data = result.get('data', [])
            if data:
                latest = data[-1]  # Most recent observation
                print(f"  ✓ {len(data)} observations, latest: {latest.get('date')} = {latest.get('value')}")
            else:
                print(f"  ✓ Connected but no data for time period")
        else:
            print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
        print()
    
    print("=== Key Economic Context for Semiconductor Trade ===")
    print("FRED API provides essential economic indicators that correlate with semiconductor trade:")
    print("• Industrial Production Index - Manufacturing activity")
    print("• NASDAQ Index - Technology sector performance") 
    print("• Exchange Rates (Japan, South Korea) - Key semiconductor trading partners")
    print("• Federal Funds Rate - Interest rate impact on tech investment")
    print("• VIX Volatility - Market uncertainty affecting supply chains")
    print("• GDP & Trade Data - Overall economic health")

if __name__ == "__main__":
    main()
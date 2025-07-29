#!/usr/bin/env python3
"""Test script for UN Comtrade API real data"""

from src.api.comtrade_client import ComtradeAPIClient

def main():
    client = ComtradeAPIClient()
    
    print("Testing broader semiconductor data...")
    result = client.get_trade_data(
        period="2022",
        reporterCode="410",  # South Korea
        cmdCode="8542",      # Broader semiconductor category
        flowCode="X",        # Exports
        partnerCode=None,    # All partners
        maxRecords=20
    )
    
    print(f"Found {result.get('count', 0)} records")
    
    if result.get('data'):
        for i, record in enumerate(result['data'][:3]):
            print(f"\nRecord {i+1}:")
            print(f"  Period: {record.get('period')}")
            print(f"  Reporter: {record.get('reporterDesc')}")
            print(f"  Partner: {record.get('partnerDesc')}")
            print(f"  Commodity: {record.get('cmdDesc')}")
            primary_value = record.get('primaryValue', 0)
            if primary_value:
                print(f"  Primary Value: ${primary_value:,.0f}")
            else:
                print(f"  Primary Value: No data")
            print(f"  Flow: {record.get('flowDesc')}")
    
    # Test specific semiconductor codes
    print("\n" + "="*60)
    print("Testing specific semiconductor HS codes...")
    
    for hs_code, description in [("854232", "Memory chips"), ("854231", "Processors"), ("854239", "Other semiconductors")]:
        print(f"\nTesting {hs_code} ({description})...")
        result = client.get_trade_data(
            period="2022",
            reporterCode="410",  # South Korea
            cmdCode=hs_code,
            flowCode="X",       # Exports
            partnerCode="158",  # Taiwan
            maxRecords=10
        )
        
        if result.get('count', 0) > 0:
            print(f"✓ Found {result['count']} records for {hs_code}")
            sample = result['data'][0]
            value = sample.get('primaryValue', 0)
            if value:
                print(f"  Sample value: ${value:,.0f}")
        else:
            print(f"✗ No data found for {hs_code}")

if __name__ == "__main__":
    main()
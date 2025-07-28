#!/usr/bin/env python3
"""
Help & Usage Guide for Semiconductor Trade Monitor MVP
"""

def show_help():
    print("🔬 SEMICONDUCTOR TRADE MONITOR - HELP GUIDE")
    print("=" * 60)
    print()
    
    print("📋 AVAILABLE TEST COMMANDS:")
    print()
    print("🚀 QUICK TESTING:")
    print("   python3 quick_test.py       # Run all tests automatically")
    print("   python3 test_runner.py      # Interactive test menu")
    print()
    
    print("🧪 INDIVIDUAL TESTS:")
    print("   python3 simple_data_test.py        # Validate data & approach")
    print("   python3 etl_pipeline.py           # Create database & load data")
    print("   python3 simple_dashboard_test.py  # Generate analytics report")
    print("   python3 api_server.py             # Test API & anomaly detection")
    print("   python3 run_full_test.py          # Complete system test")
    print()
    
    print("🌐 DASHBOARD:")
    print("   # First install Streamlit:")
    print("   pip3 install streamlit pandas plotly")
    print("   # Then run dashboard:")
    print("   streamlit run dashboard.py")
    print("   # Access at: http://localhost:8501")
    print()
    
    print("📊 WHAT EACH TEST DOES:")
    print()
    print("📁 simple_data_test.py")
    print("   - Validates internet connectivity")
    print("   - Creates sample semiconductor trade data") 
    print("   - Saves CSV for dashboard development")
    print()
    
    print("🗄️ etl_pipeline.py")
    print("   - Creates SQLite database schema")
    print("   - Loads sample data from CSV")
    print("   - Generates summary statistics")
    print("   - Exports data for dashboard")
    print()
    
    print("📈 simple_dashboard_test.py")
    print("   - Analyzes trade data from database")
    print("   - Calculates growth rates and trends")
    print("   - Shows top commodities and routes")
    print("   - Generates comprehensive report")
    print()
    
    print("🌐 api_server.py")
    print("   - Tests REST API endpoints (/v1/series, /v1/stats)")
    print("   - Runs anomaly detection (±20% threshold)")
    print("   - Tests alert system configuration")
    print("   - Validates JSON data responses")
    print()
    
    print("📋 FILES CREATED:")
    print("   semiconductor_trade.db           # SQLite database")
    print("   sample_semiconductor_trade.csv  # Sample data")
    print("   dashboard_data.json             # Dashboard export")
    print()
    
    print("🎯 EXPECTED RESULTS:")
    print("   Total Trade Value: $6.5B")
    print("   Growth Rate: +125% (2022-2023)")
    print("   Top Route: South Korea → Taiwan ($4.5B)")
    print("   Anomalies: 1 detected (HBM spike +25%)")
    print("   Top Commodity: HBM/DRAM (69.2% market share)")
    print()
    
    print("🚨 TROUBLESHOOTING:")
    print("   ❌ 'No such file' error:")
    print("      Run: cd /home/manuel/semiconductormonitor")
    print()
    print("   ❌ 'module not found' error:")
    print("      This MVP uses only Python standard library")
    print("      (sqlite3, json, csv, requests)")
    print()
    print("   ❌ Database errors:")
    print("      Run: python3 test_runner.py → option 8 (Clean & Reset)")
    print()
    print("   ❌ Streamlit not found:")
    print("      Install: pip3 install streamlit pandas plotly")
    print("      Or use virtual environment (see README.md)")
    print()
    
    print("📚 NEXT STEPS:")
    print("   1. Run quick_test.py to verify everything works")
    print("   2. Try test_runner.py for interactive testing")
    print("   3. Install Streamlit and run the dashboard")
    print("   4. Check README.md for production deployment")
    print()
    
    print("💡 TIP: Start with 'python3 quick_test.py' for first-time testing!")
    print("=" * 60)

if __name__ == "__main__":
    show_help()
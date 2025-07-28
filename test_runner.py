#!/usr/bin/env python3
"""
Easy Test Runner for Semiconductor Trade Monitor MVP
Simple interactive menu to test all components
"""

import os
import subprocess
import sys
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.project_dir = "/home/manuel/semiconductormonitor"
        os.chdir(self.project_dir)
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def run_command(self, command, description, pause=True):
        """Run a command and show output"""
        print(f"\n🔄 Running: {description}")
        print(f"Command: {command}")
        print("=" * 60)
        
        try:
            result = subprocess.run(command, shell=True)
            
            if result.returncode == 0:
                print("\n✅ Test completed successfully!")
            else:
                print("\n❌ Test failed!")
                
            if pause:
                input("\nPress Enter to continue...")
            
            return result.returncode == 0
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Test interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Error running test: {e}")
            return False
    
    def show_menu(self):
        """Display main test menu"""
        self.clear_screen()
        print("🔬 SEMICONDUCTOR TRADE MONITOR - TEST RUNNER")
        print("=" * 60)
        print(f"Project Directory: {self.project_dir}")
        print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("\nSelect a test to run:")
        print()
        print("1. 📊 Quick System Check")
        print("2. 🗄️  ETL Pipeline Test")
        print("3. 📈 Analytics Report Test")
        print("4. 🌐 API Server Test")
        print("5. 🎯 Full System Test")
        print("6. 📋 View Files & Status")
        print("7. 🚀 Start Dashboard (if Streamlit installed)")
        print("8. 🧹 Clean & Reset Database")
        print()
        print("0. ❌ Exit")
        print("=" * 60)
    
    def quick_check(self):
        """Quick system validation"""
        print("\n🔍 QUICK SYSTEM CHECK")
        print("=" * 40)
        
        checks = [
            ("ls semiconductor_trade.db", "Database file exists"),
            ("ls sample_semiconductor_trade.csv", "Sample data exists"),
            ("python3 -c 'import sqlite3; print(\"SQLite available\")'", "SQLite module"),
            ("python3 -c 'import json; print(\"JSON available\")'", "JSON module"),
            ("python3 -c 'import requests; print(\"Requests available\")'", "Requests module")
        ]
        
        passed = 0
        for command, description in checks:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {description}")
                    passed += 1
                else:
                    print(f"❌ {description}")
            except:
                print(f"❌ {description}")
        
        print(f"\nResult: {passed}/{len(checks)} checks passed")
        input("\nPress Enter to continue...")
    
    def view_status(self):
        """Show project files and status"""
        print("\n📋 PROJECT STATUS")
        print("=" * 40)
        
        print("\n📁 Project Files:")
        files = [
            "etl_pipeline.py",
            "dashboard.py", 
            "simple_dashboard_test.py",
            "api_server.py",
            "test_comtrade_api.py",
            "semiconductor_trade.db",
            "sample_semiconductor_trade.csv",
            "README.md"
        ]
        
        for file in files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"✅ {file} ({size:,} bytes)")
            else:
                print(f"❌ {file} (missing)")
        
        # Database status
        if os.path.exists("semiconductor_trade.db"):
            try:
                import sqlite3
                conn = sqlite3.connect("semiconductor_trade.db")
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM trade_flows")
                record_count = cursor.fetchone()[0]
                conn.close()
                print(f"\n🗄️ Database: {record_count} trade records")
            except:
                print("\n❌ Database: Cannot read")
        
        input("\nPress Enter to continue...")
    
    def start_dashboard(self):
        """Try to start Streamlit dashboard"""
        print("\n🚀 STARTING DASHBOARD")
        print("=" * 40)
        
        # Check if streamlit is available
        try:
            result = subprocess.run("python3 -c 'import streamlit'", shell=True, capture_output=True)
            if result.returncode != 0:
                print("❌ Streamlit not installed")
                print("\nTo install Streamlit:")
                print("pip3 install streamlit pandas plotly")
                print("\nOr create a virtual environment:")
                print("python3 -m venv venv")
                print("source venv/bin/activate")
                print("pip install streamlit pandas plotly")
                input("\nPress Enter to continue...")
                return
        except:
            print("❌ Cannot check Streamlit installation")
            input("\nPress Enter to continue...")
            return
        
        print("✅ Streamlit is available")
        print("\n🌐 Starting dashboard server...")
        print("Dashboard will open at: http://localhost:8501")
        print("\nPress Ctrl+C to stop the server")
        input("\nPress Enter to start (or Ctrl+C to cancel)...")
        
        try:
            subprocess.run("streamlit run dashboard.py", shell=True)
        except KeyboardInterrupt:
            print("\n\n⚠️ Dashboard stopped")
    
    def clean_reset(self):
        """Clean and reset the database"""
        print("\n🧹 CLEAN & RESET")
        print("=" * 40)
        
        confirm = input("This will delete the database and recreate it. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Reset cancelled")
            input("Press Enter to continue...")
            return
        
        # Remove existing files
        files_to_remove = [
            "semiconductor_trade.db",
            "sample_semiconductor_trade.csv", 
            "dashboard_data.json"
        ]
        
        for file in files_to_remove:
            if os.path.exists(file):
                os.remove(file)
                print(f"🗑️ Removed {file}")
        
        # Recreate sample data and database
        print("\n🔄 Recreating sample data...")
        self.run_command("python3 simple_data_test.py", "Generate sample data", pause=False)
        
        print("\n🔄 Recreating database...")
        self.run_command("python3 etl_pipeline.py", "Run ETL pipeline", pause=False)
        
        print("\n✅ Reset complete!")
        input("Press Enter to continue...")
    
    def run(self):
        """Main test runner loop"""
        while True:
            try:
                self.show_menu()
                choice = input("\nSelect option (0-8): ").strip()
                
                if choice == '0':
                    print("\n👋 Goodbye!")
                    break
                
                elif choice == '1':
                    self.quick_check()
                
                elif choice == '2':
                    self.run_command("python3 etl_pipeline.py", "ETL Pipeline Test")
                
                elif choice == '3':
                    self.run_command("python3 simple_dashboard_test.py", "Analytics Report Test")
                
                elif choice == '4':
                    self.run_command("python3 api_server.py", "API Server Test")
                
                elif choice == '5':
                    self.run_command("python3 run_full_test.py", "Full System Test")
                
                elif choice == '6':
                    self.view_status()
                
                elif choice == '7':
                    self.start_dashboard()
                
                elif choice == '8':
                    self.clean_reset()
                
                else:
                    print("\n❌ Invalid option. Please select 0-8.")
                    input("Press Enter to continue...")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")

if __name__ == "__main__":
    runner = TestRunner()
    runner.run()
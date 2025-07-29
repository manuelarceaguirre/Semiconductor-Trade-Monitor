#!/usr/bin/env python3
"""
ETL Pipeline for Semiconductor Trade Monitor 
Supports both SQLite and MySQL databases with sample and real API data
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database configuration
from config.database import db_config

class SemiconductorETL:
    def __init__(self):
        self.semiconductor_codes = {
            "854232": "HBM/DRAM/SRAM ICs",
            "854231": "GPU/AI Accelerators", 
            "848620": "Lithography Tools"
        }
        
        # Country code mapping
        self.country_codes = {
            "KOR": "South Korea",
            "TWN": "Taiwan", 
            "USA": "United States",
            "CHN": "China",
            "JPN": "Japan",
            "NLD": "Netherlands",
            "DEU": "Germany",
            "SGP": "Singapore",
            "MYS": "Malaysia",
            "THA": "Thailand"
        }
    
    def create_database_schema(self):
        """Create database tables - now handled by database config"""
        # Schema creation is now handled by the setup_mysql.py script
        # This method now just verifies the schema exists
        
        try:
            # Test that tables exist by querying them
            countries = db_config.execute_query("SELECT COUNT(*) as count FROM countries", fetch='one')
            hs_codes = db_config.execute_query("SELECT COUNT(*) as count FROM hs_codes", fetch='one')
            
            print(f"✓ Database schema verified: {countries['count']} countries, {hs_codes['count']} HS codes")
            return True
            
        except Exception as e:
            print(f"✗ Database schema verification failed: {e}")
            print("Please run: python3 setup_mysql.py")
            return False
    
    def load_sample_data(self, csv_file="sample_semiconductor_trade.csv"):
        """Load sample data from CSV into database"""
        
        if not Path(csv_file).exists():
            print(f"✗ Sample data file not found: {csv_file}")
            return False
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            trade_data = []
            
            for row in reader:
                try:
                    trade_data.append((
                        row['period'],
                        row['reporter_iso'],
                        row['partner_iso'], 
                        row['hs6'],
                        float(row['value_usd']),
                        float(row['quantity']),
                        row['unit'],
                        'sample'  # src_system
                    ))
                except Exception as e:
                    print(f"Error processing row: {row} - {e}")
        
        if trade_data:
            # Use appropriate SQL syntax based on database type
            if db_config.db_type == 'mysql':
                query = """
                INSERT IGNORE INTO trade_flows 
                (period, reporter_iso, partner_iso, hs6, value_usd, quantity, unit, src_system)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
            else:  # SQLite
                query = """
                INSERT OR REPLACE INTO trade_flows 
                (period, reporter_iso, partner_iso, hs6, value_usd, quantity, unit, src_system)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
            
            rows_affected = db_config.execute_many(query, trade_data)
            print(f"✓ Loaded {len(trade_data)} trade records")
            return True
        else:
            print("✗ No valid data found to load")
            return False
    
    def get_trade_summary(self):
        """Get summary statistics from the database"""
        
        # Basic counts
        total_records = db_config.execute_query("SELECT COUNT(*) as count FROM trade_flows", fetch='one')
        unique_hs_codes = db_config.execute_query("SELECT COUNT(DISTINCT hs6) as count FROM trade_flows", fetch='one')
        unique_reporters = db_config.execute_query("SELECT COUNT(DISTINCT reporter_iso) as count FROM trade_flows", fetch='one')
        
        # Top trade flows by value
        top_flows_query = """
            SELECT 
                tf.period,
                c1.name as reporter,
                c2.name as partner,
                hs.description as commodity,
                tf.value_usd
            FROM trade_flows tf
            JOIN countries c1 ON tf.reporter_iso = c1.iso3
            JOIN countries c2 ON tf.partner_iso = c2.iso3  
            JOIN hs_codes hs ON tf.hs6 = hs.hs6
            ORDER BY tf.value_usd DESC
            LIMIT 3
        """
        top_flows = db_config.execute_query(top_flows_query, fetch='all')
        
        summary = {
            "total_records": total_records['count'],
            "unique_hs_codes": unique_hs_codes['count'],
            "unique_reporters": unique_reporters['count'],
            "top_flows": top_flows
        }
        
        return summary
    
    def export_for_dashboard(self, output_file="dashboard_data.json"):
        """Export processed data for Streamlit dashboard"""
        
        export_query = """
            SELECT 
                tf.period,
                c1.name as reporter,
                c2.name as partner,
                hs.description as commodity,
                tf.hs6,
                tf.value_usd,
                tf.quantity,
                tf.unit
            FROM trade_flows tf
            JOIN countries c1 ON tf.reporter_iso = c1.iso3
            JOIN countries c2 ON tf.partner_iso = c2.iso3
            JOIN hs_codes hs ON tf.hs6 = hs.hs6
            ORDER BY tf.period DESC, tf.value_usd DESC
        """
        
        rows = db_config.execute_query(export_query, fetch='all')
        
        # Convert to JSON serializable format
        data = []
        for row in rows:
            # Handle different database return types
            if isinstance(row, dict):
                # MySQL returns dict
                data.append(row)
            else:
                # SQLite returns tuple, convert to dict
                data.append({
                    'period': row[0],
                    'reporter': row[1], 
                    'partner': row[2],
                    'commodity': row[3],
                    'hs6': row[4],
                    'value_usd': float(row[5]) if row[5] else 0,
                    'quantity': float(row[6]) if row[6] else 0,
                    'unit': row[7]
                })
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✓ Dashboard data exported: {output_file}")
        return output_file
    
    def run_etl_pipeline(self):
        """Run complete ETL pipeline"""
        
        print("=" * 60)
        print("SEMICONDUCTOR TRADE MONITOR - ETL PIPELINE")
        print(f"Pipeline started: {datetime.now()}")
        print("=" * 60)
        
        # Step 1: Create database
        print("1. Creating database schema...")
        self.create_database_schema()
        
        # Step 2: Load sample data
        print("\n2. Loading sample trade data...")
        if not self.load_sample_data():
            print("✗ ETL pipeline failed at data loading")
            return False
        
        # Step 3: Generate summary
        print("\n3. Generating data summary...")
        summary = self.get_trade_summary()
        
        print(f"   Total records: {summary['total_records']}")
        print(f"   Unique HS codes: {summary['unique_hs_codes']}")
        print(f"   Unique reporters: {summary['unique_reporters']}")
        
        print("\n   Top trade flows:")
        for i, flow in enumerate(summary['top_flows'], 1):
            if isinstance(flow, dict):
                # MySQL returns dict
                period, reporter, partner = flow['period'], flow['reporter'], flow['partner']
                commodity, value = flow['commodity'], flow['value_usd']
            else:
                # SQLite returns tuple
                period, reporter, partner, commodity, value = flow
            
            print(f"   {i}. {period}: {reporter} -> {partner}")
            print(f"      {commodity}: ${value:,.0f}")
        
        # Step 4: Export for dashboard
        print("\n4. Exporting data for dashboard...")
        self.export_for_dashboard()
        
        print("\n" + "=" * 60)
        print("✓ ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("Ready for dashboard development!")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    etl = SemiconductorETL()
    etl.run_etl_pipeline()
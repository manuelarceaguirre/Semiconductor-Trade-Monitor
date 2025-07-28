#!/usr/bin/env python3
"""
ETL Pipeline for Semiconductor Trade Monitor MVP
Creates SQLite database and ingests sample trade data
"""

import sqlite3
import csv
import json
from datetime import datetime
from pathlib import Path

class SemiconductorETL:
    def __init__(self, db_path="semiconductor_trade.db"):
        self.db_path = db_path
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
            "DEU": "Germany"
        }
    
    def create_database_schema(self):
        """Create database tables matching PRD schema"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main trade flows table (from PRD)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL,
                reporter_iso TEXT NOT NULL,
                partner_iso TEXT NOT NULL,
                hs6 TEXT NOT NULL,
                hs_extended TEXT,
                value_usd REAL,
                quantity REAL,
                unit TEXT,
                src_system TEXT DEFAULT 'sample',
                load_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(period, reporter_iso, partner_iso, hs6)
            )
        """)
        
        # Reference tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hs_codes (
                hs6 TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                category TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                iso3 TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Populate reference tables
        for hs_code, description in self.semiconductor_codes.items():
            cursor.execute("""
                INSERT OR REPLACE INTO hs_codes (hs6, description, category)
                VALUES (?, ?, 'Semiconductor')
            """, (hs_code, description))
        
        for iso3, name in self.country_codes.items():
            cursor.execute("""
                INSERT OR REPLACE INTO countries (iso3, name)
                VALUES (?, ?)
            """, (iso3, name))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Database schema created: {self.db_path}")
    
    def load_sample_data(self, csv_file="sample_semiconductor_trade.csv"):
        """Load sample data from CSV into database"""
        
        if not Path(csv_file).exists():
            print(f"✗ Sample data file not found: {csv_file}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            records_loaded = 0
            
            for row in reader:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO trade_flows 
                        (period, reporter_iso, partner_iso, hs6, value_usd, quantity, unit)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['period'],
                        row['reporter_iso'],
                        row['partner_iso'], 
                        row['hs6'],
                        float(row['value_usd']),
                        float(row['quantity']),
                        row['unit']
                    ))
                    records_loaded += 1
                except Exception as e:
                    print(f"Error loading row: {row} - {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✓ Loaded {records_loaded} trade records")
        return True
    
    def get_trade_summary(self):
        """Get summary statistics from the database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM trade_flows")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT hs6) FROM trade_flows")
        unique_hs_codes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT reporter_iso) FROM trade_flows")
        unique_reporters = cursor.fetchone()[0]
        
        # Top trade flows by value
        cursor.execute("""
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
        """)
        top_flows = cursor.fetchall()
        
        conn.close()
        
        summary = {
            "total_records": total_records,
            "unique_hs_codes": unique_hs_codes,
            "unique_reporters": unique_reporters,
            "top_flows": top_flows
        }
        
        return summary
    
    def export_for_dashboard(self, output_file="dashboard_data.json"):
        """Export processed data for Streamlit dashboard"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
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
        """)
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        conn.close()
        
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
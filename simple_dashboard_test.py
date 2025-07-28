#!/usr/bin/env python3
"""
Simple dashboard test without external dependencies
Tests the data pipeline and basic analytics functionality
"""

import sqlite3
import json
from datetime import datetime

class SimpleDashboardTest:
    def __init__(self, db_path="semiconductor_trade.db"):
        self.db_path = db_path
    
    def load_and_analyze_data(self):
        """Load data from database and perform basic analysis"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all trade data with joins
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
            
            data = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            conn.close()
            
            return data, columns
            
        except Exception as e:
            print(f"Database error: {e}")
            return [], []
    
    def calculate_analytics(self, data):
        """Calculate basic analytics from the trade data"""
        
        if not data:
            return {}
        
        # Convert to more workable format
        records = []
        for row in data:
            records.append({
                'period': row[0],
                'reporter': row[1], 
                'partner': row[2],
                'commodity': row[3],
                'hs6': row[4],
                'value_usd': row[5],
                'quantity': row[6],
                'unit': row[7]
            })
        
        # Analytics calculations
        total_value = sum(r['value_usd'] for r in records)
        
        # Top commodities by value
        commodity_values = {}
        for r in records:
            commodity = r['commodity']
            if commodity not in commodity_values:
                commodity_values[commodity] = 0
            commodity_values[commodity] += r['value_usd']
        
        top_commodities = sorted(commodity_values.items(), key=lambda x: x[1], reverse=True)
        
        # Top trade routes
        route_values = {}
        for r in records:
            route = f"{r['reporter']} → {r['partner']}"
            if route not in route_values:
                route_values[route] = 0
            route_values[route] += r['value_usd']
        
        top_routes = sorted(route_values.items(), key=lambda x: x[1], reverse=True)
        
        # Year over year growth (if we have multiple years)
        yearly_values = {}
        for r in records:
            period = r['period']
            if period not in yearly_values:
                yearly_values[period] = 0
            yearly_values[period] += r['value_usd']
        
        growth_analysis = {}
        years = sorted(yearly_values.keys())
        if len(years) > 1:
            for i in range(1, len(years)):
                prev_year = years[i-1]
                curr_year = years[i]
                prev_value = yearly_values[prev_year]
                curr_value = yearly_values[curr_year]
                growth_rate = ((curr_value - prev_value) / prev_value) * 100
                growth_analysis[f"{prev_year}-{curr_year}"] = {
                    'growth_rate': growth_rate,
                    'prev_value': prev_value,
                    'curr_value': curr_value
                }
        
        return {
            'total_value': total_value,
            'record_count': len(records),
            'unique_commodities': len(commodity_values),
            'unique_routes': len(route_values),
            'top_commodities': top_commodities[:3],
            'top_routes': top_routes[:3],
            'yearly_values': yearly_values,
            'growth_analysis': growth_analysis
        }
    
    def display_analytics_report(self, analytics):
        """Display analytics in a formatted report"""
        
        print("=" * 80)
        print("SEMICONDUCTOR TRADE ANALYTICS REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        if not analytics:
            print("No data available for analysis")
            return
        
        # Overview
        print("\n📊 OVERVIEW")
        print("-" * 40)
        print(f"Total Trade Value:    ${analytics['total_value']:,.0f}")
        print(f"Total Records:        {analytics['record_count']}")
        print(f"Unique Commodities:   {analytics['unique_commodities']}")
        print(f"Unique Trade Routes:  {analytics['unique_routes']}")
        
        # Top commodities
        print("\n🔬 TOP COMMODITIES BY VALUE")
        print("-" * 40)
        for i, (commodity, value) in enumerate(analytics['top_commodities'], 1):
            percentage = (value / analytics['total_value']) * 100
            print(f"{i}. {commodity}")
            print(f"   Value: ${value:,.0f} ({percentage:.1f}%)")
        
        # Top trade routes
        print("\n🌍 TOP TRADE ROUTES BY VALUE")
        print("-" * 40)
        for i, (route, value) in enumerate(analytics['top_routes'], 1):
            percentage = (value / analytics['total_value']) * 100
            print(f"{i}. {route}")
            print(f"   Value: ${value:,.0f} ({percentage:.1f}%)")
        
        # Yearly breakdown
        print("\n📈 YEARLY TRADE VALUES")
        print("-" * 40)
        for year, value in sorted(analytics['yearly_values'].items()):
            print(f"{year}: ${value:,.0f}")
        
        # Growth analysis
        if analytics['growth_analysis']:
            print("\n📊 YEAR-OVER-YEAR GROWTH")
            print("-" * 40)
            for period, growth_data in analytics['growth_analysis'].items():
                growth_rate = growth_data['growth_rate']
                direction = "📈" if growth_rate > 0 else "📉"
                print(f"{period}: {direction} {growth_rate:+.1f}%")
                print(f"   ${growth_data['prev_value']:,.0f} → ${growth_data['curr_value']:,.0f}")
        
        print("\n" + "=" * 80)
        print("✅ ANALYTICS COMPLETE")
        print("Dashboard test successful - ready for Streamlit deployment")
        print("=" * 80)
    
    def run_test(self):
        """Run the complete dashboard test"""
        
        print("Testing dashboard functionality...")
        
        # Load data
        data, columns = self.load_and_analyze_data()
        
        if not data:
            print("❌ No data found - run ETL pipeline first")
            return False
        
        # Calculate analytics
        analytics = self.calculate_analytics(data)
        
        # Display report
        self.display_analytics_report(analytics)
        
        return True

if __name__ == "__main__":
    test = SimpleDashboardTest()
    test.run_test()
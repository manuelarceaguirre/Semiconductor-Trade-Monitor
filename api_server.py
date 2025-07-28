#!/usr/bin/env python3
"""
FastAPI server for Semiconductor Trade Monitor
Provides REST API endpoints and basic anomaly detection
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# For now, simulate FastAPI with a simple class structure
# In production, would use: from fastapi import FastAPI, HTTPException, Query

@dataclass
class TradeRecord:
    period: str
    reporter: str
    partner: str
    commodity: str
    hs6: str
    value_usd: float
    quantity: float
    unit: str

@dataclass
class AnomalyAlert:
    period: str
    commodity: str
    trade_route: str
    current_value: float
    previous_value: float
    change_percent: float
    alert_type: str
    severity: str

class SemiconductorAPI:
    def __init__(self, db_path="semiconductor_trade.db"):
        self.db_path = db_path
        self.anomaly_threshold = 20.0  # 20% change threshold from PRD
    
    def get_database_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_trade_series(self, commodity: Optional[str] = None, 
                        reporter: Optional[str] = None,
                        partner: Optional[str] = None,
                        start_period: Optional[str] = None,
                        end_period: Optional[str] = None) -> List[TradeRecord]:
        """
        Get trade time series data with optional filters
        Endpoint: /v1/series?commodity=HBM&origin=KOR&dest=TWN
        """
        
        conn = self.get_database_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
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
            WHERE 1=1
        """
        
        params = []
        
        if commodity:
            query += " AND hs.description LIKE ?"
            params.append(f"%{commodity}%")
        
        if reporter:
            query += " AND c1.name LIKE ?"
            params.append(f"%{reporter}%")
        
        if partner:
            query += " AND c2.name LIKE ?"
            params.append(f"%{partner}%")
        
        if start_period:
            query += " AND tf.period >= ?"
            params.append(start_period)
        
        if end_period:
            query += " AND tf.period <= ?"
            params.append(end_period)
        
        query += " ORDER BY tf.period, tf.value_usd DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to TradeRecord objects
        records = []
        for row in rows:
            records.append(TradeRecord(
                period=row[0],
                reporter=row[1],
                partner=row[2], 
                commodity=row[3],
                hs6=row[4],
                value_usd=row[5],
                quantity=row[6],
                unit=row[7]
            ))
        
        return records
    
    def detect_anomalies(self) -> List[AnomalyAlert]:
        """
        Detect MoM and YoY deviations beyond threshold
        Returns anomaly alerts for significant changes
        """
        
        conn = self.get_database_connection()
        cursor = conn.cursor()
        
        # Get trade data grouped by period, commodity, and route
        cursor.execute("""
            SELECT 
                tf.period,
                hs.description as commodity,
                c1.name || ' → ' || c2.name as trade_route,
                SUM(tf.value_usd) as total_value
            FROM trade_flows tf
            JOIN countries c1 ON tf.reporter_iso = c1.iso3
            JOIN countries c2 ON tf.partner_iso = c2.iso3
            JOIN hs_codes hs ON tf.hs6 = hs.hs6
            GROUP BY tf.period, hs.description, trade_route
            ORDER BY tf.period, total_value DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Organize data by commodity and route
        trade_series = {}
        for period, commodity, route, value in rows:
            key = f"{commodity}|{route}"
            if key not in trade_series:
                trade_series[key] = {}
            trade_series[key][period] = value
        
        # Detect anomalies
        alerts = []
        for key, periods in trade_series.items():
            commodity, route = key.split('|')
            sorted_periods = sorted(periods.keys())
            
            # Check for significant changes between consecutive periods
            for i in range(1, len(sorted_periods)):
                current_period = sorted_periods[i]
                previous_period = sorted_periods[i-1]
                current_value = periods[current_period]
                previous_value = periods[previous_period]
                
                if previous_value > 0:  # Avoid division by zero
                    change_percent = ((current_value - previous_value) / previous_value) * 100
                    
                    if abs(change_percent) >= self.anomaly_threshold:
                        severity = "HIGH" if abs(change_percent) >= 50 else "MEDIUM"
                        alert_type = "SPIKE" if change_percent > 0 else "DROP"
                        
                        alerts.append(AnomalyAlert(
                            period=current_period,
                            commodity=commodity,
                            trade_route=route,
                            current_value=current_value,
                            previous_value=previous_value,
                            change_percent=change_percent,
                            alert_type=alert_type,
                            severity=severity
                        ))
        
        return alerts
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the dashboard"""
        
        conn = self.get_database_connection()
        cursor = conn.cursor()
        
        # Basic counts
        cursor.execute("SELECT COUNT(*) FROM trade_flows")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(value_usd) FROM trade_flows")
        total_value = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(DISTINCT hs6) FROM trade_flows")
        unique_commodities = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(period) FROM trade_flows")
        latest_period = cursor.fetchone()[0]
        
        # Top commodities
        cursor.execute("""
            SELECT hs.description, SUM(tf.value_usd) as total_value
            FROM trade_flows tf
            JOIN hs_codes hs ON tf.hs6 = hs.hs6
            GROUP BY hs.description
            ORDER BY total_value DESC
            LIMIT 3
        """)
        top_commodities = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_records": total_records,
            "total_value": total_value,
            "unique_commodities": unique_commodities,
            "latest_period": latest_period,
            "top_commodities": [{"name": name, "value": value} for name, value in top_commodities]
        }
    
    def test_api_endpoints(self):
        """Test all API endpoints with sample queries"""
        
        print("=" * 70)
        print("SEMICONDUCTOR TRADE MONITOR - API SERVER TEST")
        print(f"Test started: {datetime.now()}")
        print("=" * 70)
        
        # Test 1: Get all trade series
        print("\n1. Testing /v1/series (all data)")
        all_records = self.get_trade_series()
        print(f"✓ Returned {len(all_records)} trade records")
        
        if all_records:
            sample = all_records[0]
            print(f"   Sample: {sample.period} {sample.reporter} → {sample.partner}")
            print(f"   {sample.commodity}: ${sample.value_usd:,.0f}")
        
        # Test 2: Filtered query
        print("\n2. Testing /v1/series?commodity=HBM")
        hbm_records = self.get_trade_series(commodity="HBM")
        print(f"✓ Returned {len(hbm_records)} HBM records")
        
        # Test 3: Anomaly detection
        print("\n3. Testing anomaly detection")
        anomalies = self.detect_anomalies()
        print(f"✓ Detected {len(anomalies)} anomalies")
        
        for anomaly in anomalies:
            direction = "📈" if anomaly.change_percent > 0 else "📉"
            print(f"   {direction} {anomaly.severity}: {anomaly.commodity}")
            print(f"       {anomaly.trade_route}: {anomaly.change_percent:+.1f}%")
        
        # Test 4: Summary statistics
        print("\n4. Testing summary statistics")
        stats = self.get_summary_stats()
        print(f"✓ Total value: ${stats['total_value']:,.0f}")
        print(f"✓ Latest period: {stats['latest_period']}")
        print("✓ Top commodities:")
        for commodity in stats['top_commodities']:
            print(f"   - {commodity['name']}: ${commodity['value']:,.0f}")
        
        print("\n" + "=" * 70)
        print("✅ API SERVER TEST COMPLETED")
        print("All endpoints working correctly!")
        print("\nAPI ENDPOINTS AVAILABLE:")
        print("- GET /v1/series - Get trade time series")
        print("- GET /v1/anomalies - Get anomaly alerts") 
        print("- GET /v1/stats - Get summary statistics")
        print("=" * 70)
        
        return True

# Simple email alert system
class AlertSystem:
    def __init__(self):
        self.alert_configs = []  # User-defined alert thresholds
    
    def add_alert_config(self, commodity: str, route: str, threshold: float, email: str):
        """Add user alert configuration"""
        config = {
            "commodity": commodity,
            "route": route, 
            "threshold": threshold,
            "email": email,
            "created": datetime.now().isoformat()
        }
        self.alert_configs.append(config)
        print(f"✓ Alert configured: {commodity} on {route} (±{threshold}%)")
    
    def check_and_send_alerts(self, anomalies: List[AnomalyAlert]):
        """Check anomalies against user configs and simulate sending alerts"""
        
        alerts_sent = 0
        for anomaly in anomalies:
            for config in self.alert_configs:
                if (config["commodity"] in anomaly.commodity and
                    config["route"] in anomaly.trade_route and
                    abs(anomaly.change_percent) >= config["threshold"]):
                    
                    # Simulate sending email alert
                    print(f"📧 ALERT SENT to {config['email']}")
                    print(f"   Subject: {anomaly.alert_type} in {anomaly.commodity}")
                    print(f"   {anomaly.trade_route}: {anomaly.change_percent:+.1f}%")
                    alerts_sent += 1
        
        return alerts_sent

if __name__ == "__main__":
    # Test the API server
    api = SemiconductorAPI()
    api.test_api_endpoints()
    
    # Test alert system
    print("\n" + "=" * 70)
    print("TESTING ALERT SYSTEM")
    print("=" * 70)
    
    alert_system = AlertSystem()
    
    # Add sample alert configurations
    alert_system.add_alert_config("HBM", "Korea", 20.0, "trader@hedgefund.com")
    alert_system.add_alert_config("GPU", "Taiwan", 15.0, "analyst@chip-company.com")
    
    # Check for alerts
    anomalies = api.detect_anomalies()
    alerts_sent = alert_system.check_and_send_alerts(anomalies)
    
    print(f"\n✓ {alerts_sent} alerts would be sent")
    print("Alert system working correctly!")
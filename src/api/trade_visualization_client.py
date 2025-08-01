"""
Trade Visualization Client for 3D Globe Integration
Provides data endpoints specifically formatted for the 3D world visualization
"""
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .comtrade_client import ComtradeAPIClient
from .usitc_client import USITCAPIClient
from .fred_client import FREDAPIClient
from config.database import db_config

logger = logging.getLogger(__name__)

class TradeVisualizationClient:
    """Client to provide formatted data for 3D globe visualization"""
    
    def __init__(self):
        self.db_config = db_config
        self.comtrade_client = ComtradeAPIClient()
        self.usitc_client = USITCAPIClient()
        self.fred_client = FREDAPIClient()
        
        # Key trade routes for visualization
        self.key_routes = [
            {"from": "South Korea", "to": "Taiwan", "commodity": "HBM/DRAM", "hs_code": "854232"},
            {"from": "Taiwan", "to": "USA", "commodity": "GPUs", "hs_code": "854231"},
            {"from": "Netherlands", "to": "Taiwan", "commodity": "Lithography", "hs_code": "848620"},
            {"from": "China", "to": "USA", "commodity": "Semiconductors", "hs_code": "854232"},
            {"from": "Japan", "to": "China", "commodity": "Electronic ICs", "hs_code": "854231"},
        ]
        
        # Country coordinates for 3D positioning
        self.country_coords = {
            "South Korea": {"lat": 37.5665, "lng": 126.9780},
            "Taiwan": {"lat": 23.8103, "lng": 120.9675},
            "USA": {"lat": 39.8283, "lng": -98.5795},
            "Netherlands": {"lat": 52.1326, "lng": 5.2913},
            "China": {"lat": 35.8617, "lng": 104.1954},
            "Japan": {"lat": 36.2048, "lng": 138.2529},
            "Germany": {"lat": 51.1657, "lng": 10.4515},
            "Singapore": {"lat": 1.3521, "lng": 103.8198},
        }
    
    async def get_trade_flows_for_globe(self, 
                                      period: str = "recent",
                                      min_value_usd: float = 100000000) -> Dict[str, Any]:
        """Get trade flows formatted for 3D globe visualization"""
        try:
            # Get trade data from database
            query = """
            SELECT r.name as reporter_name, p.name as partner_name, 
                   h.description as commodity_name, tf.hs6 as hs_code,
                   tf.value_usd as trade_value_usd, 'export' as trade_flow, tf.period
            FROM trade_flows tf
            JOIN countries r ON tf.reporter_iso = r.iso3
            JOIN countries p ON tf.partner_iso = p.iso3  
            JOIN hs_codes h ON tf.hs6 = h.hs6
            WHERE tf.value_usd >= ?
            AND tf.period >= ?
            ORDER BY tf.value_usd DESC
            LIMIT 100
            """
            
            # Calculate date filter - use latest available data
            if period == "recent":
                # Get the latest period available in database
                latest_query = "SELECT MAX(period) FROM trade_flows"
                latest_result = self.db_config.execute_query(latest_query, fetch='one')
                date_filter = latest_result[0] if latest_result and latest_result[0] else "2023"
            else:
                date_filter = period
            
            results = self.db_config.execute_query(query, (min_value_usd, date_filter), fetch='all')
            
            # Format data for 3D visualization
            trade_flows = []
            country_stats = {}
            
            for row in results:
                if isinstance(row, dict):
                    reporter = row['reporter_name']
                    partner = row['partner_name']
                    value = float(row['trade_value_usd'])
                    commodity_name = row.get('commodity_name', 'Semiconductors')
                    hs_code = row.get('hs_code', '854232')
                    period = row.get('period', date_filter)
                else:
                    reporter = row[0]
                    partner = row[1]
                    commodity_name = row[2] if len(row) > 2 else 'Semiconductors'
                    hs_code = row[3] if len(row) > 3 else '854232'
                    value = float(row[4]) if len(row) > 4 else 0
                    period = row[6] if len(row) > 6 else date_filter
                
                # Skip invalid data
                if not reporter or not partner or reporter == partner:
                    continue
                
                # Get coordinates
                reporter_coords = self.country_coords.get(reporter)
                partner_coords = self.country_coords.get(partner)
                
                if not reporter_coords or not partner_coords:
                    continue
                
                # Create trade flow object
                flow = {
                    "from": {
                        "country": reporter,
                        "coordinates": [reporter_coords["lng"], reporter_coords["lat"]]
                    },
                    "to": {
                        "country": partner, 
                        "coordinates": [partner_coords["lng"], partner_coords["lat"]]
                    },
                    "value": value,
                    "commodity": commodity_name,
                    "hs_code": hs_code,
                    "period": period,
                    "intensity": min(value / 1000000000, 1.0)  # Normalize for visualization
                }
                
                trade_flows.append(flow)
                
                # Update country statistics
                for country in [reporter, partner]:
                    if country not in country_stats:
                        country_stats[country] = {
                            "total_trade": 0,
                            "export_value": 0,
                            "import_value": 0,
                            "coordinates": self.country_coords.get(country, {"lat": 0, "lng": 0})
                        }
                    
                    country_stats[country]["total_trade"] += value
                    if country == reporter:
                        country_stats[country]["export_value"] += value
                    else:
                        country_stats[country]["import_value"] += value
            
            return {
                "trade_flows": trade_flows[:50],  # Limit for performance
                "country_stats": country_stats,
                "metadata": {
                    "total_flows": len(trade_flows),
                    "period": period,
                    "min_value_filter": min_value_usd,
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting trade flows: {e}")
            return {"trade_flows": [], "country_stats": {}, "metadata": {"error": str(e)}}
    
    async def get_anomalies_for_globe(self) -> Dict[str, Any]:
        """Get anomaly data for globe visualization"""
        try:
            # Get recent anomalies
            query = """
            SELECT reporter_name, partner_name, commodity_name, hs_code,
                   current_value, previous_value, change_percent, 
                   anomaly_type, severity, detection_period
            FROM (
                SELECT *, 
                       ((current_value - previous_value) / previous_value * 100) as change_percent,
                       CASE 
                           WHEN ABS((current_value - previous_value) / previous_value * 100) > 50 THEN 'HIGH'
                           WHEN ABS((current_value - previous_value) / previous_value * 100) > 25 THEN 'MEDIUM'
                           ELSE 'LOW'
                       END as severity,
                       CASE
                           WHEN current_value > previous_value THEN 'SPIKE'
                           ELSE 'DROP'
                       END as anomaly_type
                FROM trade_flows 
                WHERE previous_value > 0
                AND ABS((current_value - previous_value) / previous_value * 100) > 20
                ORDER BY ABS((current_value - previous_value) / previous_value * 100) DESC
            ) anomalies
            LIMIT 20
            """
            
            results = self.db_config.execute_query(query, fetch='all')
            
            anomaly_points = []
            for row in results:
                if isinstance(row, dict):
                    reporter = row['reporter_name']
                    partner = row['partner_name']
                    change_percent = float(row['change_percent'])
                    severity = row['severity']
                    anomaly_type = row['anomaly_type']
                    commodity_name = row.get('commodity_name', 'Semiconductors')
                    current_value = float(row['current_value'])
                    previous_value = float(row['previous_value'])
                else:
                    reporter = row[0]
                    partner = row[1]
                    commodity_name = row[2] if len(row) > 2 else 'Semiconductors'
                    current_value = float(row[3]) if len(row) > 3 else 0
                    previous_value = float(row[4]) if len(row) > 4 else 0
                    change_percent = float(row[5]) if len(row) > 5 else 0
                    anomaly_type = row[6] if len(row) > 6 else 'SPIKE'
                    severity = row[7] if len(row) > 7 else 'LOW'
                
                # Get coordinates for both countries
                reporter_coords = self.country_coords.get(reporter)
                partner_coords = self.country_coords.get(partner)
                
                if reporter_coords and partner_coords:
                    anomaly = {
                        "route": {
                            "from": {"country": reporter, "coordinates": [reporter_coords["lng"], reporter_coords["lat"]]},
                            "to": {"country": partner, "coordinates": [partner_coords["lng"], partner_coords["lat"]]}
                        },
                        "change_percent": change_percent,
                        "severity": severity,
                        "type": anomaly_type,
                        "commodity": commodity_name,
                        "current_value": current_value,
                        "previous_value": previous_value
                    }
                    anomaly_points.append(anomaly)
            
            return {
                "anomalies": anomaly_points,
                "metadata": {
                    "total_anomalies": len(anomaly_points),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting anomalies: {e}")
            return {"anomalies": [], "metadata": {"error": str(e)}}
    
    async def get_economic_context_for_globe(self) -> Dict[str, Any]:
        """Get economic indicators for globe context"""
        try:
            # Get latest FRED data - simplified for MVP
            indicators = [
                ("GDP", "Gross Domestic Product"),
                ("NASDAQCOM", "NASDAQ Composite Index"),
                ("INDPRO", "Industrial Production Index")
            ]
            
            market_conditions = {}
            
            for series_id, description in indicators:
                try:
                    result = self.fred_client.get_series_data(
                        series_id=series_id,
                        start_date="2023-01-01",
                        end_date=datetime.now().strftime("%Y-%m-%d"),
                        frequency="m"
                    )
                    
                    if result.get("success") and result.get("data"):
                        latest_point = result["data"][-1]
                        market_conditions[series_id.lower() + "_level"] = latest_point.get("value", 0)
                
                except Exception as e:
                    logger.warning(f"Failed to get {series_id}: {e}")
                    market_conditions[series_id.lower() + "_level"] = 0
            
            # Format for globe visualization
            context = {
                "global_indicators": {},
                "market_conditions": market_conditions,
                "last_updated": datetime.now().isoformat()
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting economic context: {e}")
            return {"global_indicators": {}, "market_conditions": {}, "error": str(e)}

    async def get_us_trade_flows_from_census(self, 
                                          year: int = 2024,
                                          min_value_usd: float = 500000000) -> List[Dict[str, Any]]:
        """Get US semiconductor trade flows from cached Census data for globe integration"""
        try:
            logger.info(f"Fetching US trade flows from Census cache for {year}")
            
            us_flows = []
            
            # Get real US trade data from Census cache
            query = """
            SELECT partner_name, hs_code, commodity_description, trade_value_usd, period
            FROM census_trade_cache 
            WHERE trade_value_usd >= ?
            ORDER BY trade_value_usd DESC
            """
            
            results = self.db_config.execute_query(query, (min_value_usd,), fetch='all')
            
            if results:
                for row in results:
                    try:
                        partner_name, hs_code, commodity_desc, trade_value, period = row
                        
                        # Map partner names to our coordinate system
                        if partner_name in self.country_coords and "USA" in self.country_coords:
                            partner_coords = self.country_coords[partner_name]
                            usa_coords = self.country_coords["USA"]
                            
                            # Create trade flow from partner to USA
                            flow = {
                                "from": {
                                    "country": partner_name,
                                    "coordinates": [partner_coords["lng"], partner_coords["lat"]]
                                },
                                "to": {
                                    "country": "USA", 
                                    "coordinates": [usa_coords["lng"], usa_coords["lat"]]
                                },
                                "value": trade_value,
                                "commodity": commodity_desc,
                                "hs_code": hs_code,
                                "period": period,
                                "intensity": min(trade_value / 50000000000, 1.0),  # Normalize for visualization (higher values)
                                "source": "Census_Real"  # Mark as real data
                            }
                            
                            us_flows.append(flow)
                            logger.info(f"Added real US import flow: {partner_name} → USA, ${trade_value/1000000:.1f}M ({commodity_desc})")
                            
                    except Exception as e:
                        logger.warning(f"Error processing Census record: {e}")
                        continue
            
            logger.info(f"Retrieved {len(us_flows)} real US trade flows from Census data")
            return us_flows
            
        except Exception as e:
            logger.error(f"Error getting US trade flows from USITC: {e}")
            return []

    async def get_enhanced_trade_flows_for_globe(self, 
                                               period: str = "recent",
                                               min_value_usd: float = 100000000,
                                               include_usitc: bool = True) -> Dict[str, Any]:
        """Get enhanced trade flows including USITC data for 3D globe visualization"""
        try:
            # Get base trade flows from database (UN Comtrade data)
            base_result = await self.get_trade_flows_for_globe(period, min_value_usd)
            
            if not include_usitc or not self.usitc_client.api_token:
                # Return base data if USITC not requested or not available
                return base_result
            
            # Add real US trade flows from Census data
            try:
                us_flows = await self.get_us_trade_flows_from_census(
                    year=2024,  # Use 2024 Census data
                    min_value_usd=min_value_usd
                )
                
                if us_flows:
                    # Merge USITC flows with base flows
                    base_result["trade_flows"].extend(us_flows)
                    
                    # Update metadata
                    base_result["metadata"]["census_flows_added"] = len(us_flows)
                    base_result["metadata"]["total_flows"] = len(base_result["trade_flows"])
                    base_result["metadata"]["data_sources"] = ["UN Comtrade (database)", "US Census Bureau (real data)"]
                    
                    logger.info(f"Enhanced globe data with {len(us_flows)} real Census flows")
                else:
                    base_result["metadata"]["census_flows_added"] = 0
                    base_result["metadata"]["census_note"] = "No cached Census data available"
                    
            except Exception as e:
                logger.warning(f"Census integration failed, using base data only: {e}")
                base_result["metadata"]["census_error"] = str(e)
            
            return base_result
            
        except Exception as e:
            logger.error(f"Error getting enhanced trade flows: {e}")
            return {"trade_flows": [], "country_stats": {}, "metadata": {"error": str(e)}}

# Global client instance
visualization_client = TradeVisualizationClient()
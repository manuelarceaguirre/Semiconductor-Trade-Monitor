#!/usr/bin/env python3
"""
FastAPI Server for Semiconductor Trade Monitor
Production-ready REST API with real database integration
"""

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import asyncio
import logging

# Load environment variables
load_dotenv()

# Import database configuration and API clients
from config.database import db_config
from src.api.comtrade_client import ComtradeAPIClient
from src.api.usitc_client import USITCAPIClient
from src.api.fred_client import FREDAPIClient
from src.api.trade_visualization_client import visualization_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Semiconductor Trade Monitor API",
    description="Production REST API for global semiconductor trade flow analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the 3D globe visualization
app.mount("/node_modules", StaticFiles(directory="node_modules"), name="node_modules")

# Serve specific files needed for the globe
from fastapi import Request
from fastapi.responses import FileResponse

@app.get("/world.js")
async def serve_world_js():
    return FileResponse("world.js")

@app.get("/world-simple.js")
async def serve_world_simple_js():
    return FileResponse("world-simple.js")

@app.get("/world-original.js")
async def serve_world_original_js():
    return FileResponse("world-original.js")

@app.get("/globe.js")
async def serve_globe_js():
    return FileResponse("globe.js")

@app.get("/world.geojson") 
async def serve_world_geojson():
    return FileResponse("world.geojson")

@app.get("/world-trade.js")
async def serve_world_trade_js():
    return FileResponse("world-trade.js")

@app.get("/test-simple")
async def serve_test_simple():
    return FileResponse("test-simple.html")

@app.get("/test-minimal")
async def serve_test_minimal():
    return FileResponse("test-minimal.html")

@app.get("/world-minimal.js")
async def serve_world_minimal_js():
    return FileResponse("world-minimal.js")

@app.get("/debug-logger.js")
async def serve_debug_logger_js():
    return FileResponse("debug-logger.js")

@app.get("/test-complete")
async def serve_test_complete():
    return FileResponse("test-complete.html")

@app.get("/globe-working")
async def serve_globe_working():
    return FileResponse("globe-working.html")

@app.get("/globe-fixed")
async def serve_globe_fixed():
    return FileResponse("globe-fixed.html")

@app.get("/globe-test")
async def serve_globe_test():
    return FileResponse("globe-test.html")

@app.get("/globe_github.html")
async def serve_globe_github_html():
    return FileResponse("globe_github.html")

@app.get("/globe_github.js")
async def serve_globe_github_js():
    return FileResponse("globe_github.js")

@app.post("/write-debug-file")
async def write_debug_file(request: Request):
    """Write debug logs directly to file"""
    try:
        data = await request.json()
        logs = data.get('logs', [])
        timestamp = data.get('timestamp', '')
        session_start = data.get('sessionStart', '')
        
        # Write to debug file with session info
        with open("debug_output.txt", "a") as f:
            f.write(f"\n=== FLUSH AT {timestamp} (Session started: {session_start}) ===\n")
            for log in logs:
                f.write(f"{log}\n")
            f.write("=== END FLUSH ===\n")
        
        return {"status": "written", "log_count": len(logs)}
    except Exception as e:
        logger.error(f"Failed to write debug file: {e}")
        return {"status": "error", "message": str(e)}

# Initialize API clients
comtrade_client = ComtradeAPIClient()
usitc_client = USITCAPIClient()
fred_client = FREDAPIClient()

# Pydantic models for request/response validation
class TradeFlowResponse(BaseModel):
    period: str
    reporter: str
    partner: str
    commodity: str
    hs6: str
    value_usd: float
    quantity: Optional[float] = None
    unit: Optional[str] = None

class AnomalyResponse(BaseModel):
    period: str
    commodity: str
    trade_route: str
    current_value: float
    previous_value: float
    change_percent: float
    alert_type: str  # SPIKE or DROP
    severity: str    # LOW, MEDIUM, HIGH

class SummaryStatsResponse(BaseModel):
    total_records: int
    total_value: float
    unique_commodities: int
    latest_period: str
    top_commodities: List[Dict[str, Union[str, float]]]

class EconomicIndicatorResponse(BaseModel):
    series_id: str
    description: str
    latest_value: Optional[float] = None
    latest_date: Optional[str] = None
    data_points: int

class APIStatusResponse(BaseModel):
    status: str
    database_type: str
    timestamp: str
    apis_available: Dict[str, bool]

# Health check endpoint
@app.get("/health", response_model=APIStatusResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    
    # Test database connection
    db_status = db_config.test_connection()
    
    # Check API availability (simplified)
    apis_status = {
        "comtrade": comtrade_client.api_key is not None,
        "usitc": usitc_client.api_token is not None,
        "fred": fred_client.api_key is not None,
        "database": db_status.get("status") == "connected"
    }
    
    return APIStatusResponse(
        status="healthy" if all(apis_status.values()) else "degraded",
        database_type=db_status.get("database_type", "unknown"),
        timestamp=datetime.now().isoformat(),
        apis_available=apis_status
    )

# Trade data endpoints
@app.get("/v2/series", response_model=List[TradeFlowResponse])
async def get_trade_series(
    commodity: Optional[str] = Query(None, description="Filter by commodity (e.g., 'HBM', 'GPU')"),
    reporter: Optional[str] = Query(None, description="Filter by reporter country"),
    partner: Optional[str] = Query(None, description="Filter by partner country"),
    start_period: Optional[str] = Query(None, description="Start period (YYYY)"),
    end_period: Optional[str] = Query(None, description="End period (YYYY)"),
    limit: int = Query(100, le=1000, description="Maximum number of records to return")
):
    """
    Get semiconductor trade time series data with optional filters
    
    Returns trade flow records from the database with applied filters.
    """
    
    try:
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
            if db_config.db_type == 'mysql':
                query += " AND hs.description LIKE %s"
            else:
                query += " AND hs.description LIKE ?"
            params.append(f"%{commodity}%")
        
        if reporter:
            if db_config.db_type == 'mysql':
                query += " AND c1.name LIKE %s"
            else:
                query += " AND c1.name LIKE ?"
            params.append(f"%{reporter}%")
        
        if partner:
            if db_config.db_type == 'mysql':
                query += " AND c2.name LIKE %s"
            else:
                query += " AND c2.name LIKE ?"
            params.append(f"%{partner}%")
        
        if start_period:
            if db_config.db_type == 'mysql':
                query += " AND tf.period >= %s"
            else:
                query += " AND tf.period >= ?"
            params.append(start_period)
        
        if end_period:
            if db_config.db_type == 'mysql':
                query += " AND tf.period <= %s"
            else:
                query += " AND tf.period <= ?"
            params.append(end_period)
        
        query += f" ORDER BY tf.period DESC, tf.value_usd DESC LIMIT {limit}"
        
        rows = db_config.execute_query(query, tuple(params), fetch='all')
        
        # Convert to response models
        trade_flows = []
        for row in rows:
            if isinstance(row, dict):
                # MySQL returns dict
                trade_flows.append(TradeFlowResponse(
                    period=row['period'],
                    reporter=row['reporter'],
                    partner=row['partner'],
                    commodity=row['commodity'],
                    hs6=row['hs6'],
                    value_usd=float(row['value_usd']) if row['value_usd'] else 0.0,
                    quantity=float(row['quantity']) if row['quantity'] else None,
                    unit=row['unit']
                ))
            else:
                # SQLite returns tuple
                trade_flows.append(TradeFlowResponse(
                    period=row[0],
                    reporter=row[1],
                    partner=row[2],
                    commodity=row[3],
                    hs6=row[4],
                    value_usd=float(row[5]) if row[5] else 0.0,
                    quantity=float(row[6]) if row[6] else None,
                    unit=row[7]
                ))
        
        return trade_flows
        
    except Exception as e:
        logger.error(f"Error fetching trade series: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/v2/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    threshold: float = Query(20.0, ge=1.0, le=100.0, description="Anomaly detection threshold percentage"),
    severity: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH)$", description="Filter by severity level")
):
    """
    Get detected trade anomalies based on period-over-period changes
    
    Returns anomalies where trade values changed significantly between periods.
    """
    
    try:
        # Get trade data grouped by period, commodity, and route
        if db_config.db_type == 'mysql':
            concat_clause = "CONCAT(c1.name, ' → ', c2.name)"
        else:
            concat_clause = "c1.name || ' → ' || c2.name"
        
        query = f"""
            SELECT 
                tf.period,
                hs.description as commodity,
                {concat_clause} as trade_route,
                SUM(tf.value_usd) as total_value
            FROM trade_flows tf
            JOIN countries c1 ON tf.reporter_iso = c1.iso3
            JOIN countries c2 ON tf.partner_iso = c2.iso3
            JOIN hs_codes hs ON tf.hs6 = hs.hs6
            GROUP BY tf.period, hs.description, trade_route
            HAVING SUM(tf.value_usd) > 0
            ORDER BY tf.period, total_value DESC
        """
        
        rows = db_config.execute_query(query, fetch='all')
        
        # Organize data by commodity and route for anomaly detection
        trade_series = {}
        for row in rows:
            if isinstance(row, dict):
                # MySQL returns dict
                period, commodity, route, value = row['period'], row['commodity'], row['trade_route'], row['total_value']
            else:
                # SQLite returns tuple
                period, commodity, route, value = row
            
            key = f"{commodity}|{route}"
            if key not in trade_series:
                trade_series[key] = {}
            trade_series[key][period] = float(value)
        
        # Detect anomalies
        anomalies = []
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
                    
                    if abs(change_percent) >= threshold:
                        # Determine severity
                        if abs(change_percent) >= 50:
                            anomaly_severity = "HIGH"
                        elif abs(change_percent) >= 25:
                            anomaly_severity = "MEDIUM"
                        else:
                            anomaly_severity = "LOW"
                        
                        # Filter by severity if requested
                        if severity is None or anomaly_severity == severity:
                            alert_type = "SPIKE" if change_percent > 0 else "DROP"
                            
                            anomalies.append(AnomalyResponse(
                                period=current_period,
                                commodity=commodity,
                                trade_route=route,
                                current_value=current_value,
                                previous_value=previous_value,
                                change_percent=round(change_percent, 2),
                                alert_type=alert_type,
                                severity=anomaly_severity
                            ))
        
        # Sort by absolute change percentage (most significant first)
        anomalies.sort(key=lambda x: abs(x.change_percent), reverse=True)
        
        return anomalies[:50]  # Limit to top 50 anomalies
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection error: {str(e)}")

@app.get("/v2/stats", response_model=SummaryStatsResponse)
async def get_summary_stats():
    """
    Get summary statistics for the trade data
    
    Returns aggregate statistics about the trade database.
    """
    
    try:
        # Basic counts
        total_records = db_config.execute_query("SELECT COUNT(*) as count FROM trade_flows", fetch='one')
        total_value = db_config.execute_query("SELECT SUM(value_usd) as total FROM trade_flows", fetch='one')
        unique_commodities = db_config.execute_query("SELECT COUNT(DISTINCT hs6) as count FROM trade_flows", fetch='one')
        latest_period = db_config.execute_query("SELECT MAX(period) as period FROM trade_flows", fetch='one')
        
        # Top commodities
        top_commodities_query = """
            SELECT hs.description, SUM(tf.value_usd) as total_value
            FROM trade_flows tf
            JOIN hs_codes hs ON tf.hs6 = hs.hs6
            GROUP BY hs.description
            ORDER BY total_value DESC
            LIMIT 5
        """
        top_commodities_rows = db_config.execute_query(top_commodities_query, fetch='all')
        
        # Format top commodities
        top_commodities = []
        for row in top_commodities_rows:
            if isinstance(row, dict):
                # MySQL returns dict
                top_commodities.append({
                    "name": row['description'],
                    "value": float(row['total_value'])
                })
            else:
                # SQLite returns tuple
                top_commodities.append({
                    "name": row[0],
                    "value": float(row[1])
                })
        
        return SummaryStatsResponse(
            total_records=total_records['count'] if isinstance(total_records, dict) else total_records[0],
            total_value=float(total_value['total'] or 0) if isinstance(total_value, dict) else float(total_value[0] or 0),
            unique_commodities=unique_commodities['count'] if isinstance(unique_commodities, dict) else unique_commodities[0],
            latest_period=latest_period['period'] if isinstance(latest_period, dict) else latest_period[0],
            top_commodities=top_commodities
        )
        
    except Exception as e:
        logger.error(f"Error fetching summary stats: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@app.get("/v2/economic-context", response_model=List[EconomicIndicatorResponse])
async def get_economic_context(
    start_date: str = Query("2023-01-01", description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Get economic context data from FRED API
    
    Returns key economic indicators relevant to semiconductor trade.
    """
    
    try:
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Priority indicators for semiconductor context
        indicators = [
            ("INDPRO", "US Industrial Production Index"),
            ("NASDAQCOM", "NASDAQ Composite Index"),
            ("FEDFUNDS", "Federal Funds Rate"),
            ("DEXJPUS", "Japan/US Exchange Rate"),
            ("DEXKOUS", "South Korea/US Exchange Rate"),
            ("VIXCLS", "VIX Volatility Index"),
            ("UNRATE", "US Unemployment Rate")
        ]
        
        context_data = []
        
        for series_id, description in indicators:
            try:
                result = fred_client.get_series_data(
                    series_id=series_id,
                    start_date=start_date,
                    end_date=end_date,
                    frequency="m"
                )
                
                if result.get("success") and result.get("data"):
                    data_points = result["data"]
                    latest_point = data_points[-1] if data_points else None
                    
                    context_data.append(EconomicIndicatorResponse(
                        series_id=series_id,
                        description=description,
                        latest_value=latest_point.get("value") if latest_point else None,
                        latest_date=latest_point.get("date") if latest_point else None,
                        data_points=len(data_points)
                    ))
                else:
                    context_data.append(EconomicIndicatorResponse(
                        series_id=series_id,
                        description=description,
                        latest_value=None,
                        latest_date=None,
                        data_points=0
                    ))
                    
            except Exception as e:
                logger.warning(f"Failed to fetch {series_id}: {e}")
                continue
        
        return context_data
        
    except Exception as e:
        logger.error(f"Error fetching economic context: {e}")
        raise HTTPException(status_code=500, detail=f"Economic data error: {str(e)}")

# 3D Globe Visualization Endpoints
@app.get("/v2/globe/trade-flows")
async def get_globe_trade_flows(
    period: str = Query("recent", description="Time period for data (recent, YYYY-MM, etc.)"),
    min_value: float = Query(100000000, description="Minimum trade value in USD"),
    include_usitc: bool = Query(False, description="Include USITC US trade data (may be slow due to rate limits)")
):
    """Get trade flows formatted for 3D globe visualization with optional USITC data"""
    if include_usitc:
        return await visualization_client.get_enhanced_trade_flows_for_globe(period, min_value, include_usitc=True)
    else:
        return await visualization_client.get_trade_flows_for_globe(period, min_value)

@app.get("/v2/globe/trade-flows-enhanced")
async def get_enhanced_globe_trade_flows(
    period: str = Query("recent", description="Time period for data (recent, YYYY-MM, etc.)"),
    min_value: float = Query(100000000, description="Minimum trade value in USD")
):
    """Get enhanced trade flows including USITC US data for 3D globe visualization"""
    return await visualization_client.get_enhanced_trade_flows_for_globe(period, min_value, include_usitc=True)

@app.get("/v2/globe/anomalies")
async def get_globe_anomalies():
    """Get anomaly data formatted for 3D globe visualization"""
    return await visualization_client.get_anomalies_for_globe()

@app.get("/v2/globe/economic-context")
async def get_globe_economic_context():
    """Get economic indicators for globe context"""
    return await visualization_client.get_economic_context_for_globe()

# Legacy API compatibility (v1 endpoints)
@app.get("/v1/series")
async def get_trade_series_v1(
    commodity: Optional[str] = None,
    reporter: Optional[str] = None,
    partner: Optional[str] = None,
    start_period: Optional[str] = None,
    end_period: Optional[str] = None
):
    """Legacy v1 endpoint for backward compatibility"""
    
    trade_flows = await get_trade_series(
        commodity=commodity,
        reporter=reporter,
        partner=partner,
        start_period=start_period,
        end_period=end_period,
        limit=100
    )
    
    # Convert to legacy format
    return {
        "success": True,
        "count": len(trade_flows),
        "data": [flow.dict() for flow in trade_flows]
    }

@app.get("/v1/anomalies")
async def get_anomalies_v1():
    """Legacy v1 endpoint for backward compatibility"""
    
    anomalies = await get_anomalies()
    
    return {
        "success": True,
        "count": len(anomalies),
        "data": [anomaly.dict() for anomaly in anomalies]
    }

@app.get("/v1/stats")
async def get_stats_v1():
    """Legacy v1 endpoint for backward compatibility"""
    
    stats = await get_summary_stats()
    
    return {
        "success": True,
        "data": stats.dict()
    }

# 3D Globe visualization endpoint
from fastapi.responses import HTMLResponse

@app.get("/globe", response_class=HTMLResponse)
async def serve_globe():
    """Serve the 3D globe visualization"""
    try:
        # Use the original working globe first
        with open("world.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Globe visualization not found")

@app.post("/debug-log")
async def debug_log(request: Request):
    """Log debug messages from frontend to file"""
    try:
        data = await request.json()
        message = data.get('message', '')
        timestamp = data.get('timestamp', '')
        
        # Write to debug log file
        with open("debug.log", "a") as f:
            f.write(f"{timestamp} | {message}\n")
        
        return {"status": "logged"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/get-debug-logs")
async def get_debug_logs():
    """Get debug logs"""
    try:
        with open("debug.log", "r") as f:
            logs = f.read()
        return {"logs": logs}
    except FileNotFoundError:
        return {"logs": "No debug logs found"}
    except Exception as e:
        return {"error": str(e)}

# USITC DataWeb API endpoint
@app.get("/v2/usitc/status", response_model=Dict[str, Any])
async def get_usitc_status():
    """Get USITC DataWeb API status without making actual requests"""
    try:
        return {
            "success": True,
            "message": "USITC API client configured and ready",
            "data": {
                "authentication": "JWT Bearer token" if usitc_client.api_token else "No token configured",
                "base_url": usitc_client.base_url,
                "working_endpoint": "https://datawebws.usitc.gov/dataweb/api/v2/report2/runReport",
                "rate_limiting": "10 seconds between requests (very conservative)",
                "supported_hts_codes": {
                    code: desc for code, desc in list(usitc_client.target_hts_codes.items())[:8]
                },
                "known_limitations": [
                    "Extremely strict rate limiting (429 errors common)",
                    "Requires Login.gov authentication and manual token renewal",
                    "Best used for occasional detailed HTS10 queries only",
                    "UN Comtrade recommended for bulk/frequent queries"
                ],
                "fallback_available": "UN Comtrade API provides similar HS6 data"
            }
        }
    except Exception as e:
        logger.error(f"USITC status check failed: {e}")
        return {
            "success": False,
            "message": "USITC status check failed",
            "error": str(e)
        }

@app.get("/v2/usitc/us-imports", response_model=Dict[str, Any])
async def get_us_semiconductor_imports(
    year: int = Query(default=2023, description="Year to fetch data for"),
    hts_code: Optional[str] = Query(default=None, description="Specific HTS code (e.g., 8542310040 for GPUs)"),
    partner_country: Optional[str] = Query(default=None, description="Partner country ISO2 code (e.g., TW, KR)")
):
    """Get US semiconductor imports from USITC DataWeb with fallback"""
    try:
        logger.info(f"Fetching US semiconductor imports for {year}")
        
        # Check if USITC is available
        if not usitc_client.api_token:
            return {
                "success": False,
                "message": "USITC API token not configured",
                "fallback": "Use UN Comtrade API for US trade data at HS6 level",
                "alternative_endpoint": "/v2/series?reporter=USA"
            }
        
        # Use specific HTS code or default to GPUs
        target_hts = hts_code or "8542310040"  # GPUs as default
        description = usitc_client.target_hts_codes.get(target_hts, f"HTS {target_hts}")
        
        # Get trade data with conservative rate limiting
        result = usitc_client.get_trade_data(
            hts_code=target_hts,
            trade_flow="imports",
            partner_country=partner_country,
            start_year=year,
            end_year=year,
            frequency="annual"
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"US semiconductor imports retrieved successfully",
                "data": {
                    "trade_records": result.get("data", []),
                    "count": result.get("count", 0),
                    "hts_code": target_hts,
                    "commodity": description,
                    "trade_flow": "US imports",
                    "partner": partner_country or "All partners",
                    "year": year,
                    "source": "USITC DataWeb API",
                    "rate_limited": True
                },
                "metadata": result.get("metadata", {})
            }
        else:
            # Fallback recommendation
            return {
                "success": False,
                "message": "USITC API request failed - using fallback",
                "error": result.get("error"),
                "fallback": {
                    "message": "USITC API is heavily rate-limited. Use UN Comtrade for similar data.",
                    "alternative_endpoint": f"/v2/series?reporter=USA&partner={partner_country}&commodity=8542",
                    "note": "UN Comtrade provides HS6 level data, USITC provides HTS10 detail"
                }
            }
            
    except Exception as e:
        logger.error(f"USITC import query failed: {e}")
        return {
            "success": False,
            "message": "USITC API error",
            "error": str(e),
            "fallback": {
                "message": "Use UN Comtrade API as alternative",
                "endpoint": "/v2/series?reporter=USA"
            }
        }

@app.get("/v2/globe/trade-flows-demo", response_model=Dict[str, Any])
async def get_demo_enhanced_trade_flows(
    min_value: float = Query(100000000, description="Minimum trade value in USD")
):
    """Demo endpoint showing what enhanced USITC + UN Comtrade data would look like"""
    try:
        # Get base UN Comtrade flows
        base_result = await visualization_client.get_trade_flows_for_globe("recent", min_value)
        
        # Add simulated USITC US import flows
        demo_usitc_flows = [
            {
                "from": {"country": "Taiwan", "coordinates": [120.9675, 23.8103]},
                "to": {"country": "USA", "coordinates": [-98.5795, 39.8283]},
                "value": 15400000000.0,  # $15.4B
                "commodity": "Graphics Processing Units (GPUs)",
                "hs_code": "8542",
                "period": "2023",
                "intensity": 0.8,
                "source": "USITC Demo"
            },
            {
                "from": {"country": "South Korea", "coordinates": [126.978, 37.5665]},
                "to": {"country": "USA", "coordinates": [-98.5795, 39.8283]},
                "value": 8200000000.0,  # $8.2B
                "commodity": "DRAM Memory >1 Gigabit",
                "hs_code": "8542",
                "period": "2023",
                "intensity": 0.6,
                "source": "USITC Demo"
            },
            {
                "from": {"country": "China", "coordinates": [104.1954, 35.8617]},
                "to": {"country": "USA", "coordinates": [-98.5795, 39.8283]},
                "value": 6100000000.0,  # $6.1B
                "commodity": "Central Processing Units (CPUs)",
                "hs_code": "8542",
                "period": "2023",
                "intensity": 0.5,
                "source": "USITC Demo"
            }
        ]
        
        # Add demo flows to base result
        base_result["trade_flows"].extend(demo_usitc_flows)
        
        # Update metadata
        base_result["metadata"]["usitc_flows_added"] = len(demo_usitc_flows)
        base_result["metadata"]["total_flows"] = len(base_result["trade_flows"])
        base_result["metadata"]["data_sources"] = ["UN Comtrade (database)", "USITC Demo Data"]
        base_result["metadata"]["demo_mode"] = True
        base_result["metadata"]["note"] = "This endpoint demonstrates enhanced trade flows with simulated USITC data"
        
        return base_result
        
    except Exception as e:
        logger.error(f"Error creating demo enhanced flows: {e}")
        return {"trade_flows": [], "country_stats": {}, "metadata": {"error": str(e)}}

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint with basic information"""
    
    return {
        "name": "Semiconductor Trade Monitor API",
        "version": "2.0.0",
        "description": "Production REST API for global semiconductor trade flow analysis",
        "visualization": "/globe",
        "endpoints": {
            "health": "/health",
            "documentation": "/docs",
            "trade_series": "/v2/series",
            "anomalies": "/v2/anomalies", 
            "statistics": "/v2/stats",
            "economic_context": "/v2/economic-context",
            "globe_trade_flows": "/v2/globe/trade-flows",
            "globe_anomalies": "/v2/globe/anomalies",
            "globe_economic_context": "/v2/globe/economic-context"
        },
        "database": db_config.db_type,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI server
    uvicorn.run(
        "src.api.fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
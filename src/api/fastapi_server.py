#!/usr/bin/env python3
"""
FastAPI Server for Semiconductor Trade Monitor
Production-ready REST API with real database integration
"""

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint with basic information"""
    
    return {
        "name": "Semiconductor Trade Monitor API",
        "version": "2.0.0",
        "description": "Production REST API for global semiconductor trade flow analysis",
        "endpoints": {
            "health": "/health",
            "documentation": "/docs",
            "trade_series": "/v2/series",
            "anomalies": "/v2/anomalies", 
            "statistics": "/v2/stats",
            "economic_context": "/v2/economic-context"
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
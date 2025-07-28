# Semiconductor Trade Monitor MVP

A lean web-based analytics platform for monitoring global semiconductor trade flows. This MVP provides real-time insights into HBM memory, GPU/AI accelerators, and lithography equipment trade between key countries.

## 🚀 Quick Start

### ⚡ Super Easy Testing (Recommended)
```bash
# Test everything automatically
python3 quick_test.py

# Or use interactive test menu
python3 test_runner.py

# Get help
python3 help.py
```

### 🔧 Manual Testing (Step by Step)
```bash
# 1. Run the ETL Pipeline
python3 etl_pipeline.py

# 2. Test the Analytics  
python3 simple_dashboard_test.py

# 3. Test the API Server
python3 api_server.py

# 4. Run Full System Test
python3 run_full_test.py
```

### 🌐 Dashboard (Optional - Requires Streamlit)
```bash
# Install dependencies
pip install streamlit pandas plotly

# Run dashboard
streamlit run dashboard.py
# Access at: http://localhost:8501
```

## 📊 Features Implemented

### ✅ Core MVP Features
- **ETL Pipeline**: Automated data processing with SQLite database
- **Dashboard Analytics**: Interactive charts and trade flow analysis  
- **REST API**: JSON endpoints for programmatic access
- **Anomaly Detection**: Automated alerts for ±20% trade value changes
- **Email Alerts**: Configurable threshold-based notifications

### ✅ Data Coverage
- **HBM/DRAM Memory** (HS Code 854232): Korea → Taiwan flows
- **GPU/AI Accelerators** (HS Code 854231): Taiwan → USA flows  
- **Lithography Equipment** (HS Code 848620): Netherlands → Taiwan flows

### ✅ Analytics Capabilities
- Year-over-year growth analysis (+125% growth detected)
- Top trade routes by value
- Commodity breakdown and market share
- Anomaly detection (25% spike in HBM trade detected)

## 🗂️ File Structure

```
semiconductormonitor/
├── etl_pipeline.py              # Data extraction and loading
├── dashboard.py                 # Streamlit interactive dashboard
├── simple_dashboard_test.py     # Analytics without dependencies
├── api_server.py               # REST API and anomaly detection
├── test_comtrade_api.py        # UN Comtrade API validation
├── simple_data_test.py         # MVP validation script
├── quick_test.py               # 🚀 Easy automated testing
├── test_runner.py              # 🎯 Interactive test menu
├── run_full_test.py            # Complete system test
├── help.py                     # 📚 Usage guide & help
├── semiconductor_trade.db      # SQLite database (created by ETL)
├── sample_semiconductor_trade.csv  # Sample data
├── dashboard_data.json         # Dashboard export
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📈 Sample Analytics Results

**Total Trade Value**: $6.5B  
**Growth Rate**: +125% (2022-2023)  
**Top Trade Route**: South Korea → Taiwan ($4.5B)  
**Anomalies Detected**: 1 (HBM spike +25%)

### Top Commodities by Value:
1. **HBM/DRAM Memory**: $4.5B (69.2%)
2. **GPU/AI Accelerators**: $1.2B (18.5%)  
3. **Lithography Tools**: $800M (12.3%)

## 🧪 Easy Testing Tools

We've created several tools to make testing super easy:

### 🚀 `quick_test.py` - Automated Testing
- Runs all tests automatically in sequence
- Shows clear pass/fail status for each component
- Perfect for first-time validation
- Takes ~30 seconds to complete

### 🎯 `test_runner.py` - Interactive Menu
- **Option 1**: Quick system check
- **Option 2**: ETL pipeline test
- **Option 3**: Analytics report
- **Option 4**: API server test
- **Option 5**: Full system test
- **Option 6**: View files & status
- **Option 7**: Start dashboard (if Streamlit installed)
- **Option 8**: Clean & reset database

### 📚 `help.py` - Usage Guide
- Complete command reference
- Explains what each test does
- Troubleshooting tips
- Expected results and outputs

### 🔍 What Gets Tested
- ✅ Database creation and data loading
- ✅ Trade analytics and growth calculations
- ✅ REST API endpoints (`/v1/series`, `/v1/stats`, `/v1/anomalies`)
- ✅ Anomaly detection (±20% threshold)
- ✅ Alert system configuration
- ✅ Data export for dashboard

## 🔧 Technical Architecture

- **Database**: SQLite (local, no external dependencies)
- **Backend**: Python with FastAPI structure
- **Frontend**: Streamlit dashboard
- **Analytics**: Pandas + custom algorithms
- **Deployment**: Local development server

## 🎯 Next Steps for Production

1. **API Access**: Integrate with UN Comtrade API (requires authentication token)
2. **Real Data**: Replace sample data with live trade data feeds
3. **Cloud Deployment**: Deploy to Fly.io/Railway with PostgreSQL
4. **Authentication**: Add user management and API keys
5. **Advanced Analytics**: ML-based forecasting and deeper insights

## 📋 API Endpoints

### GET /v1/series
```json
{
  "commodity": "HBM",
  "reporter": "Korea", 
  "partner": "Taiwan",
  "start_period": "2022",
  "end_period": "2023"
}
```

### GET /v1/anomalies
Returns detected trade anomalies with severity levels.

### GET /v1/stats  
Returns summary statistics and top trade flows.

## 🚨 Anomaly Detection

Automatically detects trade value changes ≥20% between periods:
- **MEDIUM**: 20-50% change
- **HIGH**: >50% change
- **Types**: SPIKE (increase) or DROP (decrease)

## 📧 Alert System

Configure email alerts for specific commodity-route combinations:
```python
alert_system.add_alert_config("HBM", "Korea", 20.0, "your@email.com")
```

## 🔍 Development Status

- ✅ **Phase 1**: ETL Pipeline + Database
- ✅ **Phase 2**: Dashboard + Analytics  
- ✅ **Phase 3**: API + Anomaly Detection
- ⏳ **Phase 4**: Authentication + Subscriptions
- ⏳ **Phase 5**: Production Deployment

This MVP validates the core concept and provides a foundation for scaling to production with real data sources.
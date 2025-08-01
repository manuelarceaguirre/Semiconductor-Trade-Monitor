# API Data Sources Documentation - Globe Visualization

## 📊 **Data Sources Overview for globe.js**

This document catalogs all data sources used by the 3D globe visualization (`globe.js`) in the Semiconductor Trade Monitor project.

**Last Updated**: August 1, 2025  
**Globe URL**: `http://localhost:8000/globe`  
**Total Trade Data**: $431.9B across all sources

---

## 🌐 **Primary Data Sources**

### 1. **UN Comtrade API** - Global Bilateral Trade Flows
- **API Provider**: United Nations Department of Economic and Social Affairs
- **Endpoint**: `https://comtradeapi.un.org/data/v1/get/C/A/HS`
- **Authentication**: `Ocp-Apim-Subscription-Key` header
- **Data Period**: 2022 (latest complete bilateral data)
- **HS Code**: 8542 (Electronic Integrated Circuits)
- **Trade Value**: $90.8B in bilateral semiconductor flows
- **Globe Integration**: `/v2/globe/trade-flows` (standard endpoint)

**Key Routes Captured**:
- Taiwan → China: $57.4B
- South Korea → Taiwan: $11.8B  
- Japan → Taiwan: $8.5B
- Singapore → USA: $5.1B
- Taiwan → USA: $3.2B

**Rate Limiting**: 1.2 second delays, ~50 requests/minute
**Data Quality**: Official UN trade statistics, HS6 level detail

### 2. **US Census Bureau International Trade API** - Real US Import Data
- **API Provider**: US Census Bureau
- **Endpoint**: `https://api.census.gov/data/timeseries/intltrade/imports/hs`
- **Authentication**: None required (public API)
- **Data Period**: December 2023 (latest available)
- **HS Codes**: 854231, 854232, 854233, 854239, 848620
- **Trade Value**: $341.1B in US semiconductor imports
- **Globe Integration**: Enhanced flows with `"source": "Census_Real"`

**Major Import Flows**:
- Taiwan → USA: $220.9B (Equipment: $142.3B, Processors: $43.0B, Memory: $13.3B)
- South Korea → USA: $120.2B (Processors: $49.4B, Other ICs: $37.4B, Equipment: $22.6B)

**Commodity Breakdown**:
- **Processors/Controllers (HS 854231)**: CPUs, GPUs - $92.4B
- **Manufacturing Equipment (HS 848620)**: Lithography, etchers - $165.8B
- **Memory Chips (HS 854232)**: DRAM, Flash - $20.8B
- **Other ICs (HS 854233, 854239)**: Amplifiers, mixed signals - $62.1B

**Rate Limiting**: No strict limits, generous usage policy
**Data Quality**: Official US government import statistics, HS6 level

### 3. **USITC DataWeb API** - Detailed US Trade (Fallback)
- **API Provider**: US International Trade Commission
- **Endpoint**: `https://datawebws.usitc.gov/dataweb/api/v2/report2/runReport`
- **Authentication**: JWT Bearer token via Login.gov
- **Data Period**: 2022-2023
- **HTS Codes**: 10-digit precision (8542310040, 8542320036, etc.)
- **Status**: Rate limited (429 errors), used as fallback only
- **Globe Integration**: Enhanced endpoint with 3-second timeout

**Working HTS Codes**:
- `8542310040`: Graphics Processing Units (GPUs)
- `8542310045`: Central Processing Units (CPUs)
- `8542320036`: DRAM Memory >1 Gigabit
- `8486200000`: Semiconductor Manufacturing Equipment

**Rate Limiting**: Very strict, 10+ second delays required
**Usage**: Fallback for detailed commodity analysis

---

## 🎯 **Data Flow Architecture**

### Globe Loading Strategy (globe.js lines 254-282)

```javascript
// Primary attempt: Enhanced endpoint with Census + UN Comtrade
fetch('/v2/globe/trade-flows?include_usitc=true&min_value=100000000')

// Fallback: Standard UN Comtrade only  
fetch('/v2/globe/trade-flows?min_value=100000000&period=recent')
```

### Data Source Priority:
1. **Enhanced Mode**: UN Comtrade + US Census Bureau (real data)
2. **Standard Mode**: UN Comtrade bilateral flows only
3. **Demo Mode**: Sample data (only for testing)

### Auto-Refresh System:
- **Interval**: 30 seconds (line 199: `updateInterval = 30000`)
- **Trigger**: Automatic background refresh of trade flow data
- **Status**: Console logging shows refresh activity

---

## 📅 **Data Time Periods**

### Current Data Coverage:
- **UN Comtrade**: 2022 (latest complete bilateral data)
- **US Census**: December 2023 (most recent monthly data)
- **USITC**: 2022-2023 (when accessible)

### Data Freshness:
- **UN Comtrade**: Updated annually with 6-12 month lag
- **US Census**: Updated monthly with 2-3 month lag  
- **USITC**: Updated monthly with 1-2 month lag (when accessible)

---

## 🎨 **Visual Coding System**

### Color Coding by Data Source (globe.js lines 492-512):

**Real Census Data (`source: "Census_Real"`):**
- **Green (0x00ff88)**: Processors/CPUs/GPUs  
- **Magenta (0xff0088)**: Memory/DRAM
- **Purple (0x8800ff)**: Manufacturing Equipment
- **Orange (0xffaa00)**: Amplifiers
- **Cyan (0x00ffff)**: Other real data

**UN Comtrade Data (standard):**
- **Red (0xff0000)**: $30B+ flows
- **Orange (0xff8800)**: $15B+ flows  
- **Blue (0x0088ff)**: Smaller flows

**USITC Demo Data (`source: "USITC Demo"`):**
- **Green (0x00ff88)**: GPUs
- **Magenta (0xff0088)**: DRAM
- **Purple (0x8800ff)**: CPUs
- **Cyan (0x00ffff)**: Other USITC data

### Animation Properties:
- **Particle Count**: Proportional to trade value (`Math.floor(value / 10)`)
- **Animation Speed**: Higher value = faster particles (`0.001 + value/1000`)
- **Line Width**: Thicker lines for larger flows (`value / 10`, max 5px)

---

## 🔧 **API Integration Details**

### Database Caching:
- **UN Comtrade**: Stored in `trade_flows` table
- **US Census**: Cached in `census_trade_cache` table  
- **USITC**: Cached in `usitc_trade_cache` table (when available)

### Rate Limiting Strategies:
- **UN Comtrade**: 1.2 second delays between requests
- **US Census**: No rate limiting required
- **USITC**: 10+ second delays, exponential backoff (tenacity library)

### Error Handling:
- **Connection Timeouts**: 3-second timeout for enhanced API calls
- **Graceful Fallback**: Automatic degradation to standard endpoints
- **Console Logging**: Comprehensive status reporting for debugging

---

## 🌍 **Geographic Coverage**

### Countries with Trade Flow Data:
- **Major Exporters**: Taiwan, South Korea, China, Japan, Singapore
- **Major Importers**: USA, China, Germany, Netherlands
- **Trade Hubs**: Singapore (re-exports), Netherlands (EU gateway)

### Coordinate System (globe.js lines 201-211):
```javascript
tradeHubs = {
    'US': [39.8283, -98.5795],
    'Taiwan': [23.6978, 120.9605], 
    'China': [35.8617, 104.1954],
    'South Korea': [35.9078, 127.7669],
    'Japan': [36.2048, 138.2529],
    'Germany': [51.1657, 10.4515],
    'Netherlands': [52.1326, 5.2913],
    'Singapore': [1.3521, 103.8198]
}
```

---

## 📊 **Data Quality Metrics**

### Coverage Completeness:
- **UN Comtrade**: 8 major trading nations, $90.8B captured
- **US Census**: Complete US import data, $341.1B total
- **Combined**: $431.9B total semiconductor trade flows

### Data Validation:
- **Mirror Statistics**: Export/import matching where possible
- **Value Thresholds**: Minimum $100M for visualization (configurable)
- **Coordinate Validation**: All countries have verified lat/lng coordinates

### Update Frequency:
- **Production**: Monthly refresh from Census Bureau
- **Development**: On-demand refresh via API calls
- **Globe Display**: 30-second auto-refresh cycle

---

## 🚀 **Future Data Sources**

### Planned Integrations:
- **European Union Comext**: EU semiconductor trade data
- **Korean KOTRA**: Korea-specific export statistics
- **Taiwan Ministry of Finance**: Taiwan export data
- **Japan Customs**: Japanese trade statistics

### Commercial Options:
- **Panjiva/S&P Global**: Bill of lading data
- **Import Genius**: Real-time shipment tracking
- **Trading Economics**: Economic context data

---

## 🔍 **Debugging & Monitoring**

### Console Logging Messages:
```
🌐 Loading real trade flow data from API...
🔄 Attempting to load enhanced trade flows with USITC data...
✅ Successfully loaded enhanced trade flows with USITC data
📊 API Response: {trade_flows: 13, metadata: {...}}
🎯 Creating 13 real trade flow visualizations...
✨ Trade flow visualization complete! Total active flows: 13
```

### Health Monitoring:
- **API Status**: `/health` endpoint shows all data source availability
- **Response Times**: Tracked for performance optimization
- **Error Rates**: Logged for reliability monitoring

---

## 📝 **Data Attribution**

### Required Citations:
- **UN Comtrade**: "Trade data from UN Comtrade Database (comtradeapi.un.org)"
- **US Census**: "Import data from US Census Bureau International Trade API"
- **USITC**: "Trade statistics from US International Trade Commission DataWeb"

### Disclaimers:
- Data shown represents official government statistics
- Time periods may vary by source (2022-2023)
- Values converted to USD billions for visualization
- Geographic coordinates are approximate country centroids

---

**This documentation ensures transparency in data sourcing and provides technical reference for the globe visualization system.**
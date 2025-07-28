# Claude Memory - Semiconductor Trade Monitor Project

## 🎯 Project Overview

**Project Name**: HBM & Semiconductor Trade Monitor  
**Type**: Web-based analytics platform for semiconductor trade flows  
**Owner**: Manuel  
**Status**: MVP Complete, moving to production readiness  

## 📋 Key Instructions & Preferences

### Always Remember To:
1. **Update TODO.md** whenever making major changes or completing tasks
2. **Track progress** using the TodoWrite tool for complex multi-step work
3. **Maintain lean approach** - start simple, scale gradually
4. **Focus on defensive security** - no malicious code assistance
5. **Keep responses concise** - user prefers brief, direct answers

### Project Philosophy
- **Lean MVP first** - validate concept before scaling
- **No cloud complexity initially** - start with local/SQLite
- **Real data integration comes after MVP validation**
- **Progressive enhancement** - build foundation, then add features

## 📊 Current Project State

### ✅ MVP Completed Features
- SQLite database with trade data schema
- ETL pipeline for data processing
- Streamlit dashboard with interactive charts
- REST API endpoints (/v1/series, /v1/stats, /v1/anomalies)
- Anomaly detection system (±20% threshold)
- Alert configuration system
- Comprehensive testing tools (quick_test.py, test_runner.py)
- Complete documentation and help system

### 📈 Key Metrics Achieved
- **Total Trade Value**: $6.5B sample data
- **Growth Analysis**: +125% YoY (2022-2023)
- **Top Route**: South Korea → Taiwan ($4.5B HBM/DRAM)
- **Anomaly Detection**: Working (detected 25% HBM spike)
- **Test Coverage**: 4/4 automated tests passing

### 🗂️ Current File Structure
```
semiconductormonitor/
├── etl_pipeline.py              # ✅ Data extraction and loading
├── dashboard.py                 # ✅ Streamlit interactive dashboard
├── simple_dashboard_test.py     # ✅ Analytics without dependencies
├── api_server.py               # ✅ REST API and anomaly detection
├── quick_test.py               # ✅ Easy automated testing
├── test_runner.py              # ✅ Interactive test menu
├── help.py                     # ✅ Usage guide & help
├── semiconductor_trade.db      # ✅ SQLite database
├── TODO.md                     # ✅ Project task tracking
├── CLAUDE.md                   # ✅ This memory file
├── README.md                   # ✅ Complete documentation
└── requirements.txt            # ✅ Python dependencies
```

## 🎯 Next Phase Focus

### Immediate Priorities (based on TODO.md)
1. **Real Data Integration** - Get UN Comtrade API access working
2. **Production Database** - Migrate from SQLite to PostgreSQL  
3. **Cloud Deployment** - Deploy to Fly.io/Railway
4. **Authentication System** - Basic user management

### Technical Architecture Decisions
- **Database**: SQLite → PostgreSQL migration planned
- **Backend**: Python FastAPI (simulated currently, real FastAPI next)
- **Frontend**: Streamlit dashboard
- **Deployment**: Local MVP → Cloud production
- **API**: REST endpoints, GraphQL later

## 📋 Key Product Requirements (from PRD)

### Core HS Codes to Monitor
- **854232**: HBM/DRAM/SRAM ICs
- **854231**: GPU/AI Accelerators  
- **848620**: Lithography Tools

### Key Trade Routes
- South Korea → Taiwan (HBM/DRAM)
- Taiwan → USA (GPUs)
- Netherlands → Taiwan (Lithography)

### Success Metrics (3-month targets)
- Active free users: ≥ 300
- Premium conversions: ≥ 10 paid seats
- Alert engagement: ≥ 50% premium users
- Query latency: < 500ms cached
- Data freshness: 90% loads < 12h

## 🔧 Technical Context

### Current Tech Stack
- **Language**: Python 3
- **Database**: SQLite (MVP) → PostgreSQL (production)
- **API Framework**: Custom classes (MVP) → FastAPI (production)
- **Frontend**: Streamlit
- **Testing**: Custom test suite with automated validation
- **Data Source**: Sample data (MVP) → UN Comtrade API (production)

### API Endpoints Implemented
- `GET /v1/series` - Trade time series data with filters
- `GET /v1/stats` - Summary statistics
- `GET /v1/anomalies` - Detected trade anomalies

### Anomaly Detection Logic
- Detects ±20% changes between periods (MoM/YoY)
- Severity levels: MEDIUM (20-50%), HIGH (>50%)
- Alert types: SPIKE (increase), DROP (decrease)

## 🚨 Important Constraints & Preferences

### Security Requirements
- **Defensive security only** - no malicious code assistance
- Follow OWASP best practices
- Never expose secrets/keys
- Validate all inputs

### Development Approach
- **Start lean, scale gradually** - core principle
- **Test everything** - comprehensive testing required
- **Document thoroughly** - clear documentation essential
- **User-friendly** - easy testing and setup

### Communication Style
- **Concise responses** - user prefers brief, direct answers
- **Action-oriented** - focus on what to do next
- **Clear status updates** - always show progress
- **Practical examples** - concrete, runnable code

## 📝 Development Notes

### Current Challenges
1. **UN Comtrade API Access** - Need authentication token for real data
2. **Rate Limiting** - 1 req/sec without auth, need premium access
3. **Data Quality** - Sample data vs real data validation needed
4. **Scalability** - SQLite to PostgreSQL migration required

### Lessons Learned
- Sample data approach validated MVP concept successfully
- Comprehensive testing tools essential for development
- Interactive test menu greatly improves developer experience
- Clear documentation reduces setup friction

### Best Practices Established
- Always use TODO.md for task tracking
- Create both automated and interactive testing
- Provide comprehensive help and documentation
- Build incrementally with working prototypes

## 🔄 Update History

**2025-07-24**: 
- ✅ Completed comprehensive API research
- ✅ Selected 9 free APIs for complete data coverage
- 🎯 Next: Implement multi-API ETL pipeline architecture

**2025-07-23**: 
- ✅ MVP completed with full testing suite
- ✅ Created TODO.md and CLAUDE.md for project tracking
- 🎯 Next: Real data integration and production deployment

## 🆓 Selected Free API Stack

### Core Trade Data APIs (FREE)
1. **UN Comtrade API** - Global HS6 trade data (100 req/min free)
2. **US ITC DataWeb API** - US HTS10 trade data (completely free)
3. **Eurostat Comext API** - EU CN8 trade data (open access)
4. **Korea Customs API** - Korea trade data (10k req/day free)
5. **Taiwan MOF** - Taiwan trade data (free, web scraping)

### Context & Signals APIs (FREE)
6. **FRED API** - US economic data (120 req/min free)
7. **World Bank API** - Global economic indicators (100k calls/day)
8. **IMF Data API** - International trade statistics (free)
9. **GDELT API** - Geopolitical news events (free, 15min updates)

### Key Benefits of Free Stack
- **$0 data costs** vs $100k+ for commercial APIs
- **Comprehensive coverage** - Global trade + economic context
- **Multiple update frequencies** - From real-time news to monthly trade
- **Official sources** - Government and international organizations

---

**Remember**: Always update TODO.md when completing major tasks, and use TodoWrite tool for complex multi-step work. Keep the lean, iterative approach that's working well.
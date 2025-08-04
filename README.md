# Semiconductor Trade Monitor

Interactive 3D globe showing global semiconductor trade flows with animated routes.

## Quick Start

```bash
# Clone and run
git clone https://github.com/yourusername/semiconductormonitor.git
cd semiconductormonitor
python3 -m http.server 8080
open http://localhost:8080
```

## Features

- **Interactive 3D Globe** - Drag to rotate, scroll to zoom
- **Animated Trade Flows** - Curved arcs with moving particles  
- **Color-coded Routes** - Red (>$30B), Orange (>$15B), Blue (smaller)
- **Real-time Data** - FastAPI backend with live trade data

## Files

```
semiconductormonitor/
├── index.html              # Landing page
├── globe-static.html       # 3D globe visualization
├── globe-static.js         # Globe implementation  
├── world.geojson          # World map data
├── src/api/               # FastAPI backend
└── requirements.txt       # Dependencies
```

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python3 -m uvicorn src.api.fastapi_server:app --host 0.0.0.0 --port 8000 --reload

# View at http://localhost:8000/globe
```

## Credits

3D Globe implementation based on [three-geojson globe example](https://github.com/gkjohnson/three-geojson/blob/main/example/globe.js)
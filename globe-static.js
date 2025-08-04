// Static version of the globe visualization for GitHub Pages
// No API dependencies - all data embedded in the HTML file

// Camera setup - exact from original
const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.01, 1000);
camera.position.x = -2;
camera.position.y = 1;
camera.position.z = -1;

// Scene setup
const scene = new THREE.Scene();

// Renderer setup - exact from original
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setAnimationLoop(animate);
document.body.appendChild(renderer.domElement);

// Controls setup - exact from original
const clock = new THREE.Clock();
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.minDistance = 1;
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.rotateSpeed = 0.8;
controls.zoomSpeed = 1.2;

// Lighting setup - exact from original
const directionalLight = new THREE.DirectionalLight(0xffffff, 2.75);
directionalLight.position.set(1, 2, 0);

const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
scene.add(directionalLight, ambientLight);

// Globe group setup - exact from original
const group = new THREE.Group();
group.rotation.x = -Math.PI / 2;
scene.add(group);

// WGS84 ellipsoid constants
const WGS84_ELLIPSOID = {
    radius: { x: 6378137, y: 6378137, z: 6356752.314245179 }
};

// Dashboard functionality for static data
class StaticDashboardManager {
    constructor() {
        this.dashboardContent = document.getElementById('dashboard-content');
        this.dashboardHeader = document.getElementById('dashboard-header');
        this.isH100Mode = true;
        this.selectedFlowIndex = null;
        this.init();
    }

    init() {
        this.renderStaticTiles();
    }

    renderStaticTiles() {
        if (!this.dashboardContent) return;
        
        if (this.isH100Mode) {
            this.renderH100Tiles();
        } else {
            this.renderTradeFlowTiles();
        }
    }

    renderTradeFlowTiles() {
        if (this.dashboardHeader) {
            this.dashboardHeader.textContent = 'Semiconductor Trade Flows • 2024';
        }
        
        const staticTradeData = [
            { value: '$45.2B', route: 'China → US', commodity: 'Semiconductor devices', time: 'Recent', code: 'HS: 854231' },
            { value: '$32.1B', route: 'Taiwan → US', commodity: 'Electronic circuits', time: 'Recent', code: 'HS: 854219' },
            { value: '$28.5B', route: 'South Korea → China', commodity: 'Memory chips', time: 'Recent', code: 'HS: 854232' },
            { value: '$22.9B', route: 'Singapore → US', commodity: 'Assembly services', time: 'Recent', code: 'HS: 854213' },
            { value: '$18.7B', route: 'Japan → US', commodity: 'Semiconductor materials', time: 'Recent', code: 'HS: 854290' },
            { value: '$12.4B', route: 'Germany → China', commodity: 'Manufacturing equipment', time: 'Recent', code: 'HS: 848620' },
            { value: '$8.3B', route: 'Netherlands → Taiwan', commodity: 'Lithography equipment', time: 'Recent', code: 'HS: 848620' }
        ];
        
        this.dashboardContent.innerHTML = staticTradeData.map((trade, index) => `
            <div class="trade-tile" data-flow-index="${index}" data-flow-type="trade">
                <div class="trade-value">${trade.value}</div>
                <div>${trade.route}: ${trade.commodity}</div>
                <div class="trade-meta">${trade.time} • ${trade.code}</div>
            </div>
        `).join('');
        
        this.addTileClickHandlers();
    }

    renderH100Tiles() {
        if (this.dashboardHeader) {
            this.dashboardHeader.textContent = 'H100 GPU Supply Chain Paths • All 66 Routes';
        }
        
        // Get all H100 supply chain flows from the embedded data
        const h100Data = window.H100_SUPPLY_CHAIN_DATA || (typeof H100_SUPPLY_CHAIN_DATA !== 'undefined' ? H100_SUPPLY_CHAIN_DATA : null);
        
        if (!h100Data || !h100Data.supply_flows) {
            console.error('❌ H100 supply chain data not available for dashboard');
            this.dashboardContent.innerHTML = '<div class="trade-tile">H100 data not available</div>';
            return;
        }
        
        // Sort flows by trade value (descending) to show most important first
        const sortedFlows = [...h100Data.supply_flows].sort((a, b) => b.trade_value - a.trade_value);
        
        // Format flows for display
        const h100SupplyData = sortedFlows.map(flow => {
            // Use city names if available, fallback to country names
            const fromLocation = flow.from_city && flow.from_city !== '–' && flow.from_city !== '' 
                ? `${flow.from_city}, ${flow.from_country}` 
                : flow.from_country;
            const toLocation = flow.to_city && flow.to_city !== '–' && flow.to_city !== ''
                ? `${flow.to_city}, ${flow.to_country}`
                : flow.to_country;
                
            return {
                value: `$${(flow.trade_value / 1000).toFixed(1)}B`,
                route: `${fromLocation} → ${toLocation}`,
                commodity: flow.commodity,
                company: flow.company || 'Multiple suppliers',
                // Determine tier based on trade value and commodity type
                tier: this.determineTier(flow)
            };
        });
        
        this.dashboardContent.innerHTML = h100SupplyData.map((supply, index) => `
            <div class="trade-tile" data-flow-index="${index}" data-flow-type="h100">
                <div class="trade-value">${supply.value}</div>
                <div>${supply.route}</div>
                <div style="font-size: 9px; color: rgba(255,255,255,0.9); margin: 2px 0;">${supply.commodity}</div>
                <div class="trade-meta">${supply.company} • ${supply.tier}</div>
            </div>
        `).join('');
        
        this.addTileClickHandlers();
    }
    
    determineTier(flow) {
        // Use the actual tier from the H100 data if available
        if (flow.tier) {
            // Extract just the tier number and category for display
            const tierMatch = flow.tier.match(/^(Tier \d+):/);
            if (tierMatch) {
                return tierMatch[1];
            }
            return flow.tier;
        }
        
        // Fallback to value-based logic for data without tier info
        const value = flow.trade_value;
        const commodity = flow.commodity.toLowerCase();
        
        // Final assembly components
        if (commodity.includes('die') || commodity.includes('hbm') || commodity.includes('interposer') || value >= 1000) {
            return 'Tier 1';
        }
        // Major sub-assemblies  
        else if (commodity.includes('substrate') || commodity.includes('vrm') || commodity.includes('pcb') || value >= 200) {
            return 'Tier 2';
        }
        // Components and materials
        else if (value >= 50) {
            return 'Tier 3';
        }
        // Raw materials
        else {
            return 'Raw Materials';
        }
    }
    
    addTileClickHandlers() {
        const tiles = this.dashboardContent.querySelectorAll('.trade-tile');
        tiles.forEach(tile => {
            tile.addEventListener('click', (e) => {
                const flowIndex = parseInt(tile.dataset.flowIndex);
                const flowType = tile.dataset.flowType;
                
                // Toggle selection
                if (this.selectedFlowIndex === flowIndex) {
                    // Deselect - show all flows
                    this.selectedFlowIndex = null;
                    this.updateTileSelection();
                    if (window.tradeFlowManager) {
                        window.tradeFlowManager.showAllFlows();
                    }
                } else {
                    // Select this flow
                    this.selectedFlowIndex = flowIndex;
                    this.updateTileSelection();
                    if (window.tradeFlowManager) {
                        window.tradeFlowManager.showSingleFlow(flowIndex, flowType);
                    }
                }
            });
        });
    }
    
    updateTileSelection() {
        const tiles = this.dashboardContent.querySelectorAll('.trade-tile');
        tiles.forEach((tile, index) => {
            if (index === this.selectedFlowIndex) {
                tile.classList.add('selected');
            } else {
                tile.classList.remove('selected');
            }
        });
    }
    
    clearSelection() {
        this.selectedFlowIndex = null;
        this.updateTileSelection();
    }

    switchToH100Mode() {
        this.isH100Mode = true;
        this.clearSelection();
        this.renderStaticTiles();
    }

    switchToTradeMode() {
        this.isH100Mode = false;
        this.clearSelection();
        this.renderStaticTiles();
    }
}

// Initialize dashboard when DOM is ready
let dashboardManager;
let isH100Mode = true;

document.addEventListener('DOMContentLoaded', () => {
    dashboardManager = new StaticDashboardManager();
    console.log('📊 Dashboard manager initialized');
    
    // Force toggle initialization immediately
    setTimeout(() => {
        console.log('🔄 Force initializing toggle from DOMContentLoaded...');
        initializeToggle();
    }, 500);
    
    // Backup toggle initialization
    setTimeout(() => {
        if (!document.getElementById('data-toggle').onclick) {
            console.log('🔄 Running backup toggle initialization...');
            initializeToggle();
        }
    }, 3000);
});

// Simple toggle functionality that works
function initializeToggle() {
    console.log('🔄 Initializing toggle controls...');
    
    // Wait a bit to ensure DOM is ready
    setTimeout(() => {
        const toggle = document.getElementById('data-toggle');
        const tradeLabel = document.getElementById('trade-label');
        const h100Label = document.getElementById('h100-label');
        
        console.log('Toggle elements found:', { 
            toggle: !!toggle, 
            tradeLabel: !!tradeLabel, 
            h100Label: !!h100Label 
        });
        
        if (!toggle || !tradeLabel || !h100Label) {
            console.error('❌ Toggle elements not found in DOM');
            return;
        }

        // Test basic click first
        toggle.addEventListener('click', function(e) {
            console.log('🖱️ CLICK DETECTED!');
            e.stopPropagation();
        });

        // Also try onclick
        toggle.onclick = function(e) {
            console.log('🖱️ ONCLICK DETECTED!');
            console.log('Current mode before toggle:', isH100Mode ? 'H100' : 'Trade');
            
            if (isH100Mode) {
                // Switch to trade mode
                isH100Mode = false;
                toggle.classList.remove('active');
                tradeLabel.classList.add('active');
                h100Label.classList.remove('active');
                
                console.log('🌐 Switching to Trade Mode');
                if (dashboardManager) dashboardManager.switchToTradeMode();
                if (window.tradeFlowManager) window.tradeFlowManager.switchToTradeMode();
                
            } else {
                // Switch to H100 mode
                isH100Mode = true;
                toggle.classList.add('active');
                tradeLabel.classList.remove('active');
                h100Label.classList.add('active');
                
                console.log('🔥 Switching to H100 Mode');
                if (dashboardManager) dashboardManager.switchToH100Mode();
                if (window.tradeFlowManager) window.tradeFlowManager.switchToH100Mode();
            }
            
            if (e) e.preventDefault();
            return false;
        };

        // Test if the element is actually there and clickable
        console.log('Toggle element style:', toggle.style.cssText);
        console.log('Toggle element position:', toggle.getBoundingClientRect());
        
        // Add a test that should definitely work
        document.body.addEventListener('click', function(e) {
            if (e.target.id === 'data-toggle' || e.target.closest('#data-toggle')) {
                console.log('🖱️ Body detected click on toggle!');
            }
        });

        console.log('✅ Toggle initialized successfully');
    }, 100);
}

// Load world GeoJSON from external source or fallback
async function loadWorldGeoJSON() {
    try {
        console.log('🌍 Loading world map from external source...');
        const response = await fetch(WORLD_GEOJSON_URL);
        if (!response.ok) throw new Error('Failed to fetch world map');
        return await response.json();
    } catch (error) {
        console.warn('⚠️ Failed to load external world map, using simplified version');
        // Fallback to simplified world data - basic continents
        return createSimplifiedWorldMap();
    }
}

function createSimplifiedWorldMap() {
    // Simplified world map with major countries as polygons
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": { "NAME": "United States" },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-125, 25], [-125, 49], [-66, 49], [-66, 25], [-125, 25]
                    ]]
                }
            },
            {
                "type": "Feature", 
                "properties": { "NAME": "China" },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [73, 18], [135, 18], [135, 53], [73, 53], [73, 18]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": { "NAME": "Europe" },
                "geometry": {
                    "type": "Polygon", 
                    "coordinates": [[
                        [-10, 35], [40, 35], [40, 71], [-10, 71], [-10, 35]
                    ]]
                }
            }
        ]
    };
}

// Load GeoJSON and initialize globe
loadWorldGeoJSON().then(res => {
    console.log(`🌍 Processing ${res.features.length} GeoJSON features...`);
    
    // Add base globe
    const globeBase = new THREE.Mesh(
        new THREE.SphereGeometry(1, 32, 16),
        new THREE.MeshStandardMaterial({
            color: 0x222222,
            transparent: true,
            opacity: 0.75,
            roughness: 1.0,
            metalness: 0.0
        })
    );
    globeBase.scale.copy(WGS84_ELLIPSOID.radius);
    group.add(globeBase);

    // Process GeoJSON features
    processGeoJSONFeatures(res.features);

    // Scale and center the model - EXACT from original
    const box = new THREE.Box3();
    box.setFromObject(group);
    box.getCenter(group.position).multiplyScalar(-1);

    const size = new THREE.Vector3();
    box.getSize(size);
    const globeScale = 1.5 / Math.max(...size.toArray());
    group.scale.setScalar(globeScale);  
    group.position.multiplyScalar(group.scale.x);

    console.log(`🌍 Globe scaled by ${globeScale.toFixed(4)}`);
    
    // Initialize trade flow manager after globe is loaded
    window.tradeFlowManager = new StaticTradeFlowManager(scene, group);
    
    // Initialize toggle after everything is ready
    console.log('🔄 About to call initializeToggle...');
    initializeToggle();
    console.log('🔄 Called initializeToggle');
    
    // Add country labels only for countries in trade flows
    console.log('🏷️ Adding trade-relevant country labels...');
    const tradeCountries = window.tradeFlowManager.getTradeCountries();
    console.log('📍 Trade countries:', tradeCountries);
    
    // Country name standardization and coordinates
    const countryCoordinates = {
            'China': [35.8617, 104.1954],
            'Taiwan': [23.6978, 120.9605],
            'South Korea': [35.9078, 127.7669],
            'Japan': [36.2048, 138.2529],
            'United States': [39.8283, -98.5795],
            'USA': [39.8283, -98.5795],
            'Singapore': [1.3521, 103.8198],
            'Netherlands': [52.1326, 5.2913],
            'Germany': [51.1657, 10.4515],
            'Malaysia': [4.2105, 101.9758],
            'Chile': [-35.6751, -71.5430],
            'Australia': [-25.2744, 133.7751],
            'Canada': [56.1304, -106.3468],
            'Russia': [61.5240, 105.3188],
            'Peru': [-9.1900, -75.0152],
            'Saudi Arabia': [23.8859, 45.0792],
            'Poland': [51.9194, 19.1451],
            'Thailand': [15.8700, 100.9925]
        };
        
        // Standardize country names to avoid duplicates
        const countryNameMap = {
            'United States': 'USA',
            'USA': 'USA'
        };
        
        // Get unique standardized countries
        const standardizedCountries = new Set();
        tradeCountries.forEach(country => {
            const standardName = countryNameMap[country] || country;
            standardizedCountries.add(standardName);
        });
        
        // Add labels for unique countries only
        Array.from(standardizedCountries).forEach(country => {
            const coords = countryCoordinates[country];
            if (coords) {
                const [lat, lng] = coords;
                addStaticCountryLabel(country, lat, lng, globeScale);
            } else {
                console.warn(`⚠️ No coordinates found for country: ${country}`);
            }
        });
}).catch(error => {
    console.error('Failed to load world map:', error);
});

function processGeoJSONFeatures(features) {    
    features.forEach(feature => {
        if (feature.geometry) {
            createCountryLines(feature);
        }
    });
}

function createCountryLines(feature) {
    if (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon') {
        const coordinates = feature.geometry.type === 'Polygon' 
            ? [feature.geometry.coordinates] 
            : feature.geometry.coordinates;

        coordinates.forEach(polygon => {
            polygon.forEach(ring => {
                if (ring.length > 2) {
                    const points = convertCoordinatesToPoints(ring);
                    if (points.length > 1) {
                        // Simplify points for performance
                        const simplifiedPoints = points.length > 50 
                            ? points.filter((_, i) => i % 2 === 0)
                            : points;
                        
                        const geometry = new THREE.BufferGeometry().setFromPoints(simplifiedPoints);
                        
                        const material = new THREE.LineBasicMaterial({
                            color: 0xffffff
                        });

                        const line = new THREE.Line(geometry, material);
                        line.userData = { countryName: feature.properties.NAME || feature.properties.name };
                        group.add(line);
                    }
                }
            });
        });
    }
}

function convertCoordinatesToPoints(ring) {
    const points = [];
    ring.forEach(coord => {
        if (coord.length >= 2) {
            const [lng, lat] = coord;
            
            const latRad = lat * Math.PI / 180;
            const lngRad = lng * Math.PI / 180;

            const cosLat = Math.cos(latRad);
            const sinLat = Math.sin(latRad);
            const cosLng = Math.cos(lngRad);
            const sinLng = Math.sin(lngRad);

            const x = WGS84_ELLIPSOID.radius.x * cosLat * cosLng;
            const y = WGS84_ELLIPSOID.radius.y * cosLat * sinLng;
            const z = WGS84_ELLIPSOID.radius.z * sinLat;

            points.push(new THREE.Vector3(x, y, z));
        }
    });
    return points;
}

function addStaticCountryLabel(name, lat, lng, globeScale) {
    console.log(`🏷️ Creating label for ${name}`);
    
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const fontSize = 32;
    canvas.width = 256;
    canvas.height = 64;

    context.font = `bold ${fontSize}px Arial`;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.strokeStyle = 'black';
    context.lineWidth = 4;
    context.fillStyle = 'white';

    context.strokeText(name, canvas.width / 2, canvas.height / 2);
    context.fillText(name, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);

    const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true,
        alphaTest: 0.5 
    });
    
    const sprite = new THREE.Sprite(spriteMaterial);

    const latRad = lat * Math.PI / 180;
    const lngRad = lng * Math.PI / 180;
    
    const cosLat = Math.cos(latRad);
    const sinLat = Math.sin(latRad);
    const cosLng = Math.cos(lngRad);
    const sinLng = Math.sin(lngRad);

    let localPosition = new THREE.Vector3(
        WGS84_ELLIPSOID.radius.x * cosLat * cosLng,
        WGS84_ELLIPSOID.radius.y * cosLat * sinLng,
        WGS84_ELLIPSOID.radius.z * sinLat
    );

    localPosition.multiplyScalar(1.02);
    sprite.position.copy(localPosition);
    
    const finalScaleX = 0.15 / globeScale;
    const finalScaleY = 0.0375 / globeScale;
    sprite.scale.set(finalScaleX, finalScaleY, 1);
    
    sprite.userData = { countryName: name, isStaticLabel: true };
    sprite.visible = true;
    
    group.add(sprite);
    console.log(`✅ Added label for ${name}`);
}

// Static Trade Flow System
class StaticTradeFlowManager {
    constructor(scene, group) {
        this.scene = scene;
        this.group = group;
        this.tradeFlows = [];
        this.h100Flows = [];
        this.animatedParticles = [];
        this.animationFrameCount = 0;
        this.isH100Mode = true;
        this.selectedFlowIndex = null;
        this.selectedFlowType = null;
        this.tradeCountries = new Set(); // Track countries in trade flows
        
        this.init();
    }
    
    init() {
        console.log('🚀 StaticTradeFlowManager initializing...');
        this.loadStaticTradeFlows();
        this.loadH100SupplyChain();
        console.log('🚀 StaticTradeFlowManager initialization complete');
    }
    
    loadStaticTradeFlows() {
        console.log('🌐 Loading static trade flow data...');
        
        // Transform static data to our format
        const flows = STATIC_TRADE_DATA.trade_flows.map(flow => {
            // Track countries for labeling
            this.tradeCountries.add(flow.from_country);
            this.tradeCountries.add(flow.to_country);
            
            return {
                from: flow.from_country,
                to: flow.to_country,
                value: flow.trade_value,
                commodity: flow.commodity,
                coordinates: {
                    from: [flow.from_lon, flow.from_lat],
                    to: [flow.to_lon, flow.to_lat]
                }
            };
        });
        
        console.log(`✅ Loaded ${flows.length} static trade flows`);
        this.createTradeFlowVisualizations(flows, 'trade');
    }

    loadH100SupplyChain() {
        console.log('🔥 Loading H100 supply chain data...');
        
        // Check if H100 data exists
        console.log('🔍 Checking for H100 data...');
        console.log('window.H100_SUPPLY_CHAIN_DATA exists:', !!window.H100_SUPPLY_CHAIN_DATA);
        console.log('Direct H100_SUPPLY_CHAIN_DATA exists:', typeof H100_SUPPLY_CHAIN_DATA !== 'undefined');
        
        const h100Data = window.H100_SUPPLY_CHAIN_DATA || (typeof H100_SUPPLY_CHAIN_DATA !== 'undefined' ? H100_SUPPLY_CHAIN_DATA : null);
        
        if (!h100Data) {
            console.error('❌ H100_SUPPLY_CHAIN_DATA not found anywhere!');
            return;
        }
        
        console.log('🔥 H100_SUPPLY_CHAIN_DATA found:', h100Data);
        
        // Transform H100 data to our format
        const flows = h100Data.supply_flows.map((flow, index) => {
            // Track countries for labeling
            this.tradeCountries.add(flow.from_country);
            this.tradeCountries.add(flow.to_country);
            
            return {
                from: flow.from_country,
                to: flow.to_country,
                value: flow.trade_value || (50 + (index * 5)), // Default values for animation if missing
                commodity: flow.commodity,
                company: flow.company,
                coordinates: {
                    from: [flow.from_lon, flow.from_lat],
                    to: [flow.to_lon, flow.to_lat]
                }
            };
        });
        
        console.log(`✅ Loaded ${flows.length} H100 supply chain flows`);
        this.createTradeFlowVisualizations(flows, 'h100');
    }
    
    createTradeFlowVisualizations(flows, type = 'trade') {
        console.log(`🎨 Creating ${flows.length} ${type} flow visualizations...`);
        
        const flowArray = type === 'h100' ? this.h100Flows : this.tradeFlows;
        
        flows.forEach((flow, index) => {
            console.log(`  📍 Creating ${type} route ${index + 1}: ${flow.from} → ${flow.to}`);
            const routeObjects = this.createTradeRoute(flow, type);
            flowArray.push(routeObjects);
        });
        
        // Initially show H100 flows, hide trade flows
        if (type === 'h100') {
            this.setH100FlowsVisibility(true);
            console.log(`🔥 H100 flows visible initially (${flowArray.length} flows)`);
        } else {
            this.setTradeFlowsVisibility(false);
            console.log(`🌐 Trade flows hidden initially (${flowArray.length} flows)`);
        }
        
        console.log(`✨ ${type} flow visualization complete! Total ${type} flows: ${flowArray.length}`);
    }
    
    createTradeRoute(flow, type = 'trade') {
        // Convert API coordinates [lng, lat] to [lat, lng]
        const fromCoords = [flow.coordinates.from[1], flow.coordinates.from[0]];
        const toCoords = [flow.coordinates.to[1], flow.coordinates.to[0]];
        
        console.log(`  ✅ Route coordinates: ${flow.from} [${fromCoords}] → ${flow.to} [${toCoords}]`);
        
        // Convert to 3D coordinates
        const fromPoint = this.latLngTo3D(fromCoords[0], fromCoords[1]);
        const toPoint = this.latLngTo3D(toCoords[0], toCoords[1]);
        
        // Create curved path
        const curve = this.createCurvedPath(fromPoint, toPoint);
        
        // Create route line with type-specific colors
        const routeLine = this.createRouteLine(curve, flow, type);
        this.group.add(routeLine);
        
        // Create animated particles
        const particles = this.createAnimatedParticles(curve, flow, type);
        particles.forEach(particle => {
            this.group.add(particle);
            this.animatedParticles.push({
                mesh: particle,
                curve: curve,
                progress: Math.random(),
                speed: this.getSpeedFromValue(flow.value),
                flow: flow,
                type: type
            });
        });
        
        return { routeLine, particles, flow, type };
    }
    
    latLngTo3D(lat, lng) {
        const latRad = lat * Math.PI / 180;
        const lngRad = lng * Math.PI / 180;
        
        const radius = 1.02;
        const cosLat = Math.cos(latRad);
        const sinLat = Math.sin(latRad);
        const cosLng = Math.cos(lngRad);
        const sinLng = Math.sin(lngRad);
        
        return new THREE.Vector3(
            radius * cosLat * cosLng,
            radius * cosLat * sinLng, 
            radius * sinLat
        ).multiplyScalar(WGS84_ELLIPSOID.radius.x);
    }
    
    createCurvedPath(fromPoint, toPoint) {
        // Normalize points to ensure they're on the sphere surface
        const from = fromPoint.clone().normalize().multiplyScalar(WGS84_ELLIPSOID.radius.x);
        const to = toPoint.clone().normalize().multiplyScalar(WGS84_ELLIPSOID.radius.x);
        
        // Calculate angle between points
        const angle = from.angleTo(to);
        
        // Create multiple points along the great circle
        const points = [];
        const numPoints = Math.max(5, Math.floor(angle * 10)); // More points for longer arcs
        
        for (let i = 0; i <= numPoints; i++) {
            const t = i / numPoints;
            
            // Use spherical interpolation (slerp) for great circle
            const point = new THREE.Vector3();
            point.copy(from).lerp(to, t).normalize();
            
            // Add height that peaks in the middle
            const heightCurve = Math.sin(t * Math.PI); // Sine curve for natural arc
            const maxHeight = Math.min(angle * WGS84_ELLIPSOID.radius.x * 0.15, WGS84_ELLIPSOID.radius.x * 0.2);
            const currentHeight = heightCurve * maxHeight;
            
            point.multiplyScalar(WGS84_ELLIPSOID.radius.x + currentHeight);
            points.push(point);
        }
        
        return new THREE.CatmullRomCurve3(points);
    }
    
    createRouteLine(curve, flow, type = 'trade') {
        const points = curve.getPoints(50);
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        const color = this.getColorFromValue(flow.value, type);
        const material = new THREE.LineBasicMaterial({ 
            color: color,
            transparent: true,
            opacity: 0.6
        });
        
        return new THREE.Line(geometry, material);
    }
    
    createAnimatedParticles(curve, flow, type = 'trade') {
        const particles = [];
        
        let particleCount;
        if (type === 'h100') {
            // Much fewer particles for H100 supply chain to reduce clutter
            particleCount = Math.max(1, Math.floor(flow.value / 100)); // Reduced by 10x
            particleCount = Math.min(particleCount, 3); // Max 3 particles per flow
        } else {
            // Regular trade flows keep original particle count
            particleCount = Math.max(2, Math.floor(flow.value / 10));
        }
        
        for (let i = 0; i < particleCount; i++) {
            const geometry = new THREE.SphereGeometry(0.008 * WGS84_ELLIPSOID.radius.x, 6, 4);
            const material = new THREE.MeshBasicMaterial({ 
                color: this.getColorFromValue(flow.value, type),
                transparent: true,
                opacity: type === 'h100' ? 0.6 : 0.8 // Slightly more transparent for H100
            });
            
            const particle = new THREE.Mesh(geometry, material);
            particles.push(particle);
        }
        
        return particles;
    }
    
    getColorFromValue(value, type = 'trade') {
        if (type === 'h100') {
            // H100 supply chain uses NVIDIA green color scheme
            if (value >= 1000) return 0x76b900; // NVIDIA bright green for $1B+
            if (value >= 100) return 0x5a8a00; // Medium green for $100M+
            return 0x3d5c00; // Dark green for smaller values
        }
        
        // Regular trade flows use original color scheme
        if (value >= 30) return 0xff0000; // Red for $30B+
        if (value >= 15) return 0xff8800; // Orange for $15B+
        return 0x0088ff; // Blue for smaller values
    }
    
    getSpeedFromValue(value) {
        return 0.0001 + (value / 10000); // Made 10x slower
    }

    setTradeFlowsVisibility(visible) {
        this.tradeFlows.forEach(({ routeLine, particles }) => {
            routeLine.visible = visible;
            particles.forEach(particle => particle.visible = visible);
        });
    }

    setH100FlowsVisibility(visible) {
        this.h100Flows.forEach(({ routeLine, particles }) => {
            routeLine.visible = visible;
            particles.forEach(particle => particle.visible = visible);
        });
    }

    switchToH100Mode() {
        this.isH100Mode = true;
        this.setTradeFlowsVisibility(false);
        this.setH100FlowsVisibility(true);
        console.log('🔥 Switched to H100 supply chain mode');
    }

    switchToTradeMode() {
        this.isH100Mode = false;
        this.setH100FlowsVisibility(false);
        this.setTradeFlowsVisibility(true);
        this.selectedFlowIndex = null;
        this.selectedFlowType = null;
        console.log('🌐 Switched to trade flows mode');
    }
    
    showSingleFlow(flowIndex, flowType) {
        console.log(`🎯 Showing single flow: ${flowType} #${flowIndex}`);
        this.selectedFlowIndex = flowIndex;
        this.selectedFlowType = flowType;
        
        if (flowType === 'h100') {
            // Hide all trade flows, show only selected H100 flow
            this.setTradeFlowsVisibility(false);
            this.setH100FlowsVisibility(false);
            
            if (flowIndex < this.h100Flows.length) {
                const selectedFlow = this.h100Flows[flowIndex];
                selectedFlow.routeLine.visible = true;
                selectedFlow.particles.forEach(particle => particle.visible = true);
            }
        } else {
            // Hide all H100 flows, show only selected trade flow
            this.setH100FlowsVisibility(false);
            this.setTradeFlowsVisibility(false);
            
            if (flowIndex < this.tradeFlows.length) {
                const selectedFlow = this.tradeFlows[flowIndex];
                selectedFlow.routeLine.visible = true;
                selectedFlow.particles.forEach(particle => particle.visible = true);
            }
        }
    }
    
    showAllFlows() {
        console.log('🌐 Showing all flows for current mode');
        this.selectedFlowIndex = null;
        this.selectedFlowType = null;
        
        if (this.isH100Mode) {
            this.setTradeFlowsVisibility(false);
            this.setH100FlowsVisibility(true);
        } else {
            this.setH100FlowsVisibility(false);
            this.setTradeFlowsVisibility(true);
        }
    }
    
    updateAnimations() {
        if (this.animationFrameCount % 2 === 0) {
            this.animatedParticles.forEach(({ mesh, curve, progress, speed, type }) => {
                // Only animate particles that are currently visible
                if (mesh.visible) {
                    const newProgress = (progress + speed) % 1;
                    
                    const position = curve.getPoint(newProgress);
                    mesh.position.copy(position);
                    
                    const particleData = this.animatedParticles.find(p => p.mesh === mesh);
                    if (particleData) particleData.progress = newProgress;
                }
            });
        }
    }
    
    getTradeCountries() {
        return Array.from(this.tradeCountries);
    }
}

// Animation loop
function animate() {
    controls.update(Math.min(clock.getDelta(), 64 / 1000));
    
    if (window.tradeFlowManager) {
        window.tradeFlowManager.animationFrameCount++;
        window.tradeFlowManager.updateAnimations();
    }
    
    renderer.render(scene, camera);
    
    // Slow auto-rotation
    group.rotation.z = window.performance.now() * 0.15e-4;
}

// Resize handling
function onResize() {
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
}

onResize();
window.addEventListener('resize', onResize);
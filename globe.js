// Revert to CDN approach with manual geometry processing
// Professional libraries require complex build setup

// camera - exact from original
const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.01, 1000);
camera.position.x = -2;
camera.position.y = 1;
camera.position.z = -1;

// scene
const scene = new THREE.Scene();

// renderer - exact from original
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setAnimationLoop(animate);
document.body.appendChild(renderer.domElement);

// controls - exact from original
const clock = new THREE.Clock();
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.minDistance = 1;
controls.enableDamping = true;
controls.dampingFactor = 0.05; // Smoother damping
controls.rotateSpeed = 0.8; // Slightly slower rotation for smoother feel
controls.zoomSpeed = 1.2;

// lights - exact from original
const directionalLight = new THREE.DirectionalLight(0xffffff, 2.75);
directionalLight.position.set(1, 2, 0);

const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
scene.add(directionalLight, ambientLight);

// construct geo group - exact from original
const group = new THREE.Group();
group.rotation.x = -Math.PI / 2;
scene.add(group);

// Simulate WGS84_ELLIPSOID for CDN version
const WGS84_ELLIPSOID = {
    radius: { x: 6378137, y: 6378137, z: 6356752.314245179 }
};


// Dashboard functionality
class DashboardManager {
    constructor() {
        this.dashboardContent = document.getElementById('dashboard-content');
        this.tradeData = [];
        this.isUpdating = false;
        this.init();
    }

    async init() {
        await this.fetchTradeData();
        this.renderTiles();
        this.startAutoUpdate();
    }

    async fetchTradeData() {
        try {
            // Try enhanced endpoint first, then fallback to standard
            let response;
            let dataSource = 'UN Comtrade';
            try {
                response = await fetch('/v2/globe/trade-flows-enhanced?min_value=100000000');
                if (!response.ok) throw new Error('Enhanced endpoint failed');
                dataSource = 'UN Comtrade + USITC';
            } catch {
                response = await fetch('/v2/globe/trade-flows?min_value=100000000&period=recent');
            }
            
            const data = await response.json();
            this.dataSource = dataSource;
            
            this.tradeData = data.trade_flows?.slice(0, 10).map(flow => ({
                value: this.formatValue(flow.value),
                route: `${flow.from.country} → ${flow.to.country}`,
                commodity: flow.commodity || 'Semiconductors',
                time: this.formatTime(null),
                code: flow.hs_code || 'HS: 8542',
                intensity: flow.intensity
            })) || [];
        } catch (error) {
            console.log('Globe API failed, using demo data for dashboard');
            this.dataSource = 'Demo Data';
            this.tradeData = this.getDemoData();
        }
    }

    getDemoData() {
        return [
            { value: '$45.8B', route: 'Taiwan → US', commodity: 'GPU Semiconductors', time: '1 hour ago', code: 'HS: 854231' },
            { value: '$32.1B', route: 'China → US', commodity: 'Electronic Components', time: '2 hours ago', code: 'HS: 854219' },
            { value: '$22.9B', route: 'Singapore → US', commodity: 'Assembly Services', time: '3 hours ago', code: 'HS: 854213' },
            { value: '$18.7B', route: 'Japan → US', commodity: 'Raw Materials', time: '4 hours ago', code: 'HS: 854232' },
            { value: '$15.2B', route: 'South Korea → Taiwan', commodity: 'HBM Memory', time: '5 hours ago', code: 'HS: 854232' },
            { value: '$12.4B', route: 'Germany → China', commodity: 'Manufacturing Equipment', time: '6 hours ago', code: 'HS: 848620' },
            { value: '$8.3B', route: 'Netherlands → Taiwan', commodity: 'Lithography Equipment', time: '7 hours ago', code: 'HS: 848620' }
        ];
    }

    formatValue(value) {
        if (!value) return '$0';
        const num = parseFloat(value);
        if (num >= 1e9) return `$${(num/1e9).toFixed(1)}B`;
        if (num >= 1e6) return `$${(num/1e6).toFixed(0)}M`;
        return `$${num.toLocaleString()}`;
    }

    formatTime(period) {
        if (!period) return 'Recent';
        return `${Math.floor(Math.random() * 12) + 1} hours ago`;
    }

    renderTiles() {
        if (!this.dashboardContent) return;
        
        const headerText = `${this.dataSource || 'Loading...'} • 2024`;
        
        this.dashboardContent.parentElement.innerHTML = `
            <div id="dashboard-header">${headerText}</div>
            <div id="dashboard-content">
                ${this.tradeData.map(trade => `
                    <div class="trade-tile">
                        <div class="trade-value">${trade.value}</div>
                        <div>${trade.route}: ${trade.commodity}</div>
                        <div class="trade-meta">${trade.time} • ${trade.code}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        this.dashboardContent = document.getElementById('dashboard-content');
    }

    startAutoUpdate() {
        setInterval(async () => {
            if (!this.isUpdating) {
                this.isUpdating = true;
                await this.fetchTradeData();
                this.renderTiles();
                this.isUpdating = false;
            }
        }, 30000);
    }
}

// Initialize dashboard when DOM is ready
let dashboardManager;
document.addEventListener('DOMContentLoaded', () => {
    dashboardManager = new DashboardManager();
});

// load geojson - back to working fetch approach
fetch('./world.geojson')
    .then(response => response.json())
    .then(res => {
        
        const queryParams = new URLSearchParams(location.search);
        const country = queryParams.get('country') || 'Japan';
        let thickness = parseFloat(queryParams.get('thickness'));
        let resolution = parseFloat(queryParams.get('resolution')) || 2.5;
        let wireframe = Boolean(queryParams.get('wireframe'));
        if (thickness !== 0) {
            thickness = thickness || (1e5 * 0.5);
        }

        // add base globe color - optimized geometry for performance
        const globeBase = new THREE.Mesh(
            new THREE.SphereGeometry(1, 32, 16), // Reduced from 100,50 to 32,16 for better performance
            new THREE.MeshStandardMaterial({
                color: 0x222222,
                transparent: true,
                opacity: 0.75,
                premultipliedAlpha: true,
                side: THREE.FrontSide,
                roughness: 1.0,
                metalness: 0.0,
                polygonOffset: true,
                polygonOffsetFactor: 1,
                polygonOffsetUnits: 1,
            }),
        );
        globeBase.scale.copy(WGS84_ELLIPSOID.radius);
        globeBase.renderOrder = 1;
        group.add(globeBase);

        const wireframeGroup = new THREE.Group();
        wireframeGroup.visible = wireframe;
        group.add(wireframeGroup);

        // Process GeoJSON features to recreate original rendering
        console.log(`🌍 Processing ${res.features.length} GeoJSON features for country labels...`);
        processGeoJSONFeatures(res.features, country, thickness, resolution, wireframeGroup);

        // scale and center the model - EXACT from original
        const box = new THREE.Box3();
        box.setFromObject(group);
        box.getCenter(group.position).multiplyScalar(-1);

        const size = new THREE.Vector3();
        box.getSize(size);
        const globeScale = 1.5 / Math.max(...size.toArray());
        group.scale.setScalar(globeScale);
        group.position.multiplyScalar(group.scale.x);

        console.log(res);
        console.log(`🌍 Globe scaled by ${globeScale.toFixed(4)} and positioned at:`, group.position);
        
        // Initialize trade flow manager after globe is loaded
        tradeFlowManager = new TradeFlowManager(scene, group);
        
        // Add test labels manually AFTER scaling (like in working test)
        setTimeout(() => {
            console.log('🏷️ Adding manual test labels after globe scaling...');
            addManualLabelAfterScaling('USA', 39.8283, -98.5795, globeScale, group.position);
            addManualLabelAfterScaling('China', 35.8617, 104.1954, globeScale, group.position);
            addManualLabelAfterScaling('Japan', 36.2048, 138.2529, globeScale, group.position);
            addManualLabelAfterScaling('Germany', 51.1657, 10.4515, globeScale, group.position);
            addManualLabelAfterScaling('Taiwan', 23.6978, 120.9605, globeScale, group.position);
            addManualLabelAfterScaling('Netherlands', 52.1326, 5.2913, globeScale, group.position);
            addManualLabelAfterScaling('South Korea', 35.9078, 127.7669, globeScale, group.position);
            addManualLabelAfterScaling('Singapore', 1.3521, 103.8198, globeScale, group.position);
            console.log(`✅ Added ${scene.children.filter(c => c.userData?.isManualLabel).length} manual labels to scene`);
        }, 1000);
    })
    .catch(error => {
        console.error('Failed to load GeoJSON: ' + error.message);
    });

function processGeoJSONFeatures(features, country, thickness, resolution, wireframeGroup) {    
    features.forEach(feature => {
        if (feature.geometry) {
            // We no longer check for a highlighted country.
            // We just create the lines for every feature.
            createCountryLines(feature, resolution);
        }
    });
}


function createCountryLines(feature, resolution) {
    if (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon') {
        const coordinates = feature.geometry.type === 'Polygon' 
            ? [feature.geometry.coordinates] 
            : feature.geometry.coordinates;

        coordinates.forEach(polygon => {
            polygon.forEach(ring => {
                if (ring.length > 2) {
                    const points = convertCoordinatesToPoints(ring);
                    if (points.length > 1) {
                        // Aggressive simplification for performance - more reduction for small countries
                        let simplifiedPoints;
                        if (points.length > 200) {
                            simplifiedPoints = points.filter((_, i) => i % 4 === 0); // Keep every 4th point for very detailed countries
                        } else if (points.length > 50) {
                            simplifiedPoints = points.filter((_, i) => i % 2 === 0); // Keep every 2nd point
                        } else {
                            simplifiedPoints = points; // Keep all points for simple countries
                        }
                        
                        const geometry = new THREE.BufferGeometry().setFromPoints(simplifiedPoints);
                        
                        // Bright white solid lines for all countries
                        const material = new THREE.LineBasicMaterial({
                            color: 0xffffff, // Bright white
                        });

                        const line = new THREE.Line(geometry, material);
                        line.userData = { countryName: feature.properties.NAME || feature.properties.name };
                        group.add(line);
                    }
                }
            });
        });
        
        // Add country label
        if (feature.properties && (feature.properties.NAME || feature.properties.name)) {
            // createCountryLabel(feature, coordinates); // <-- DISABLED: This system creates invisible labels
        }
    }
}

function createPolygonGeometry(ring) {
    const points = convertCoordinatesToPoints(ring);
    if (points.length < 3) return null;

    const vertices = [];
    const indices = [];

    points.forEach(point => {
        vertices.push(point.x, point.y, point.z);
    });

    // Fan triangulation
    for (let i = 1; i < points.length - 2; i++) {
        indices.push(0, i, i + 1);
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();

    return geometry;
}

function convertCoordinatesToPoints(ring) {
    const points = [];
    ring.forEach(coord => {
        if (coord.length >= 2) {
            const [lng, lat] = coord;
            
            // Convert to 3D coordinates on ellipsoid surface - like original
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

function createCountryLabel(feature, coordinates) {
    // DISABLED: This function creates invisible labels due to incorrect transformation handling
    return;
    
    // Calculate country centroid for label placement - simplified
    const centroid = calculateSimpleCentroid(coordinates);
    if (!centroid) return;
    
    // Create text sprite
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const fontSize = 24;
    
    // Configure canvas
    canvas.width = 200;
    canvas.height = 50;
    context.font = `${fontSize}px Arial`;
    context.fillStyle = 'white';
    context.strokeStyle = 'black';
    context.lineWidth = 2;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    
    // Use shorter names for display
    const displayName = getDisplayName(countryName);
    
    // Draw text with outline
    context.strokeText(displayName, canvas.width / 2, canvas.height / 2);
    context.fillText(displayName, canvas.width / 2, canvas.height / 2);
    
    // Create texture and sprite
    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: false,
        depthWrite: true
    });
    
    const sprite = new THREE.Sprite(spriteMaterial);
    
    // Position label using simplified coordinate conversion (like test version)
    const [avgLat, avgLng] = centroid;
    const latRad = avgLat * Math.PI / 180;
    const lngRad = avgLng * Math.PI / 180;
    const radius = 1.1; // Above globe surface
    
    const x = radius * Math.cos(latRad) * Math.cos(lngRad);
    const y = radius * Math.cos(latRad) * Math.sin(lngRad);
    const z = radius * Math.sin(latRad);
    
    sprite.position.set(x * WGS84_ELLIPSOID.radius.x, y * WGS84_ELLIPSOID.radius.x, z * WGS84_ELLIPSOID.radius.x);
    sprite.scale.set(WGS84_ELLIPSOID.radius.x * 0.0002, WGS84_ELLIPSOID.radius.x * 0.00005, 1);
    
    // Store country name in userData
    sprite.userData = { countryName, isLabel: true };
    
    // Make visible by default for major countries
    sprite.visible = true;
    group.add(sprite);
    
    console.log(`Added label for ${displayName} at lat=${avgLat.toFixed(2)}, lng=${avgLng.toFixed(2)}`);
}

function getDisplayName(countryName) {
    if (countryName.includes('United States')) return 'USA';
    if (countryName === 'Taiwan') return 'Taiwan';
    if (countryName === 'South Korea') return 'S. Korea';
    if (countryName === 'Netherlands') return 'Netherlands';
    return countryName;
}

function calculateSimpleCentroid(coordinates) {
    let totalLat = 0, totalLng = 0, count = 0;
    
    coordinates.forEach(polygon => {
        polygon.forEach(ring => {
            ring.forEach(coord => {
                if (coord.length >= 2) {
                    totalLng += coord[0];
                    totalLat += coord[1];
                    count++;
                }
            });
        });
    });
    
    if (count === 0) return null;
    
    return [totalLat / count, totalLng / count]; // [lat, lng]
}

function calculateCountryCentroid(coordinates) {
    let totalX = 0, totalY = 0, totalZ = 0, count = 0;
    
    coordinates.forEach(polygon => {
        polygon.forEach(ring => {
            ring.forEach(coord => {
                if (coord.length >= 2) {
                    const [lng, lat] = coord;
                    const latRad = lat * Math.PI / 180;
                    const lngRad = lng * Math.PI / 180;
                    
                    const cosLat = Math.cos(latRad);
                    const sinLat = Math.sin(latRad);
                    const cosLng = Math.cos(lngRad);
                    const sinLng = Math.sin(lngRad);
                    
                    totalX += WGS84_ELLIPSOID.radius.x * cosLat * cosLng;
                    totalY += WGS84_ELLIPSOID.radius.y * cosLat * sinLng;
                    totalZ += WGS84_ELLIPSOID.radius.z * sinLat;
                    count++;
                }
            });
        });
    });
    
    if (count === 0) return null;
    
    return new THREE.Vector3(totalX / count, totalY / count, totalZ / count);
}

// Manual label function that applies globe scaling and positioning
// Manual label function that applies globe scaling and positioning
function addManualLabelAfterScaling(name, lat, lng, globeScale, globePosition) {
    console.log(`🏷️ Creating manual label for ${name} at ${lat}, ${lng} with scale ${globeScale.toFixed(4)}`);
    
    // --- START: Sprite and Canvas Creation ---
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const fontSize = 32;
    canvas.width = 256;
    canvas.height = 64;

    // Configure text style
    context.font = `bold ${fontSize}px Arial`;
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.strokeStyle = 'black';
    context.lineWidth = 4;
    context.fillStyle = 'white';

    // Draw only the outlined text. No background rectangle is drawn.
    context.strokeText(name, canvas.width / 2, canvas.height / 2);
    context.fillText(name, canvas.width / 2, canvas.height / 2);
    
    const texture = new THREE.CanvasTexture(canvas);

    // Create the sprite material.
    // `transparent: true` allows for see-through sections.
    // `alphaTest` forces pixels with low alpha (like the transparent background) to be discarded entirely.
    const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true,
        alphaTest: 0.5 
    });
    
    const sprite = new THREE.Sprite(spriteMaterial);
    // --- END: Sprite and Canvas Creation ---


    // --- START: SIMPLIFIED Positioning Logic ---
    const latRad = lat * Math.PI / 180;
    const lngRad = lng * Math.PI / 180;
    
    const cosLat = Math.cos(latRad);
    const sinLat = Math.sin(latRad);
    const cosLng = Math.cos(lngRad);
    const sinLng = Math.sin(lngRad);

    // 1. Calculate the position in the globe's LOCAL coordinate system.
    let localPosition = new THREE.Vector3(
        WGS84_ELLIPSOID.radius.x * cosLat * cosLng,
        WGS84_ELLIPSOID.radius.y * cosLat * sinLng,
        WGS84_ELLIPSOID.radius.z * sinLat
    );

    // 2. Lift the label slightly off the surface.
    localPosition.multiplyScalar(1.02);
    
    sprite.position.copy(localPosition);
    // --- END: SIMPLIFIED Positioning Logic ---


    // --- START: Corrected Sizing and Scene Addition ---
    
    // 1. Compensate for the group's scale so the label maintains a consistent size.
    const finalScaleX = 0.15 / globeScale;
    const finalScaleY = 0.0375 / globeScale;
    sprite.scale.set(finalScaleX, finalScaleY, 1);
    
    sprite.userData = { countryName: name, isManualLabel: true };
    sprite.visible = true;
    
    // 2. Add the sprite to the GROUP, not the scene, so it rotates with the globe.
    group.add(sprite);
    
    console.log(`✅ Added manual label for ${name} to the globe group.`);
}
// Trade Flow System
class TradeFlowManager {
    constructor(scene, group) {
        this.scene = scene;
        this.group = group;
        this.tradeFlows = [];
        this.animatedParticles = [];
        this.isLoading = false;
        this.lastUpdate = 0;
        this.updateInterval = 30000; // 30 seconds
        this.animationFrameCount = 0; // For optimized particle updates
        
        // Major semiconductor trade hubs (lat, lng)
        this.tradeHubs = {
            'US': [39.8283, -98.5795],
            'Taiwan': [23.6978, 120.9605], 
            'China': [35.8617, 104.1954],
            'South Korea': [35.9078, 127.7669],
            'Japan': [36.2048, 138.2529],
            'Germany': [51.1657, 10.4515],
            'Netherlands': [52.1326, 5.2913],
            'Singapore': [1.3521, 103.8198]
        };
        
        this.init();
    }
    
    init() {
        this.loadTradeFlowData();
    }
    
    async loadTradeFlowData() {
        if (this.isLoading) return;
        this.isLoading = true;
        
        try {
            console.log('🌐 Loading real trade flow data from API...');
            
            let apiData;
            let dataSource = "Standard";
            
            // Check URL for demo mode
            const urlParams = new URLSearchParams(window.location.search);
            const demoMode = urlParams.get('demo') === 'true';
            
            if (demoMode) {
                console.log('🎭 Demo mode activated - loading enhanced trade flows demo');
                try {
                    const demoResponse = await fetch('/v2/globe/trade-flows-demo?min_value=100000000');
                    if (demoResponse.ok) {
                        apiData = await demoResponse.json();
                        dataSource = "Demo (UN Comtrade + Simulated USITC)";
                        console.log('✅ Successfully loaded demo enhanced trade flows');
                    } else {
                        throw new Error(`Demo API error: ${demoResponse.status}`);
                    }
                } catch (demoError) {
                    console.log('⚠️ Demo API failed, using standard endpoint:', demoError.message);
                    const standardResponse = await fetch('/v2/globe/trade-flows?min_value=100000000&period=recent');
                    if (!standardResponse.ok) {
                        throw new Error(`Standard API error: ${standardResponse.status}`);
                    }
                    apiData = await standardResponse.json();
                    dataSource = "Standard (UN Comtrade)";
                }
            } else {
                // Try enhanced endpoint first (with timeout)
                try {
                    console.log('🔄 Attempting to load enhanced trade flows with USITC data...');
                    const enhancedResponse = await Promise.race([
                        fetch('/v2/globe/trade-flows?min_value=100000000&period=recent&include_usitc=true'),
                        new Promise((_, reject) => setTimeout(() => reject(new Error('Enhanced API timeout')), 3000))
                    ]);
                    
                    if (enhancedResponse.ok) {
                        apiData = await enhancedResponse.json();
                        dataSource = "Enhanced (UN Comtrade + USITC)";
                        console.log('✅ Successfully loaded enhanced trade flows with USITC data');
                    } else {
                        throw new Error(`Enhanced API error: ${enhancedResponse.status}`);
                    }
                } catch (enhancedError) {
                    console.log('⚠️ Enhanced API failed, falling back to standard endpoint:', enhancedError.message);
                    
                    // Fallback to standard endpoint
                    const standardResponse = await fetch('/v2/globe/trade-flows?min_value=100000000&period=recent');
                    if (!standardResponse.ok) {
                        throw new Error(`Standard API error: ${standardResponse.status} ${standardResponse.statusText}`);
                    }
                    apiData = await standardResponse.json();
                    dataSource = "Standard (UN Comtrade)";
                    console.log('✅ Successfully loaded standard trade flows');
                }
            }
            console.log('📊 API Response:', apiData);
            
            // Transform API data format to our visualization format
            const tradeFlows = apiData.trade_flows?.map(flow => ({
                from: flow.from.country,
                to: flow.to.country,
                value: flow.value / 1000000000, // Convert to billions for display
                type: this.getTradeType(flow.commodity, flow.hs_code),
                commodity: flow.commodity,
                hs_code: flow.hs_code,
                intensity: flow.intensity,
                coordinates: {
                    from: flow.from.coordinates,
                    to: flow.to.coordinates
                }
            })) || [];
            
            console.log(`✅ Loaded ${tradeFlows.length} trade flows from ${dataSource} API`);
            console.log(`📈 Total trade value: $${(apiData.trade_flows?.reduce((sum, flow) => sum + flow.value, 0) / 1000000000).toFixed(1)}B`);
            if (apiData.metadata) {
                console.log(`⏰ Data last updated: ${apiData.metadata.last_updated}`);
                console.log(`🎯 Min value filter: $${(apiData.metadata.min_value_filter / 1000000000).toFixed(1)}B`);
            }
            
            // Process trade flows for visualization
            if (tradeFlows.length === 0) {
                console.log('⚠️ No API data received, using sample trade flows');
                const sampleTradeFlows = [
                    { from: 'South Korea', to: 'Taiwan', value: 15.2, type: 'HBM' },
                    { from: 'Taiwan', to: 'USA', value: 45.8, type: 'GPU' },
                    { from: 'Netherlands', to: 'Taiwan', value: 8.3, type: 'Lithography' },
                    { from: 'China', to: 'USA', value: 32.1, type: 'Components' },
                    { from: 'Japan', to: 'USA', value: 18.7, type: 'Materials' },
                    { from: 'Germany', to: 'China', value: 12.4, type: 'Equipment' },
                    { from: 'Singapore', to: 'USA', value: 22.9, type: 'Assembly' }
                ];
                console.log('🎯 Creating sample trade flow visualizations...');
                this.createTradeFlowVisualizations(sampleTradeFlows);
            } else {
                console.log(`🎯 Creating ${tradeFlows.length} real trade flow visualizations...`);
                tradeFlows.forEach((flow, index) => {
                    console.log(`  ${index + 1}. ${flow.from} → ${flow.to}: $${flow.value.toFixed(1)}B (${flow.commodity})`);
                });
                this.createTradeFlowVisualizations(tradeFlows);
            }
        } catch (error) {
            console.error('❌ Failed to load trade flow data:', error);
            console.log('⚠️ Falling back to sample data');
            
            // Fallback to sample data on error
            const sampleTradeFlows = [
                { from: 'South Korea', to: 'Taiwan', value: 15.2, type: 'HBM' },
                { from: 'Taiwan', to: 'USA', value: 45.8, type: 'GPU' },
                { from: 'Netherlands', to: 'Taiwan', value: 8.3, type: 'Lithography' },
                { from: 'China', to: 'USA', value: 32.1, type: 'Components' },
                { from: 'Japan', to: 'USA', value: 18.7, type: 'Materials' },
                { from: 'Germany', to: 'China', value: 12.4, type: 'Equipment' },
                { from: 'Singapore', to: 'USA', value: 22.9, type: 'Assembly' }
            ];
            this.createTradeFlowVisualizations(sampleTradeFlows);
        } finally {
            this.isLoading = false;
        }
    }
    
    getTradeType(commodity, hs_code) {
        if (hs_code === '854232' || commodity?.toLowerCase().includes('dram') || commodity?.toLowerCase().includes('hbm')) {
            return 'HBM/DRAM';
        }
        if (hs_code === '854231' || commodity?.toLowerCase().includes('gpu') || commodity?.toLowerCase().includes('graphic')) {
            return 'GPU';
        }
        if (hs_code === '848620' || commodity?.toLowerCase().includes('lithography') || commodity?.toLowerCase().includes('etching')) {
            return 'Lithography';
        }
        return 'Semiconductors';
    }
    
    createTradeFlowVisualizations(flows) {
        console.log(`🎨 Creating trade flow visualizations for ${flows.length} flows...`);
        
        // Clear existing flows
        this.clearTradeFlows();
        
        flows.forEach((flow, index) => {
            console.log(`  📍 Creating route ${index + 1}: ${flow.from} → ${flow.to}`);
            this.createTradeRoute(flow);
        });
        
        console.log(`✨ Trade flow visualization complete! Total active flows: ${this.tradeFlows.length}`);
    }
    
    createTradeRoute(flow) {
        // Use API coordinates if available, otherwise fall back to predefined hubs
        let fromCoords, toCoords;
        
        if (flow.coordinates) {
            // API provides [lng, lat] format
            fromCoords = [flow.coordinates.from[1], flow.coordinates.from[0]]; // Convert to [lat, lng]
            toCoords = [flow.coordinates.to[1], flow.coordinates.to[0]]; // Convert to [lat, lng]
        } else {
            // Fall back to predefined trade hubs
            fromCoords = this.tradeHubs[flow.from];
            toCoords = this.tradeHubs[flow.to];
        }
        
        if (!fromCoords || !toCoords) {
            console.warn(`❌ Trade route coordinates not found: ${flow.from} -> ${flow.to}`);
            console.warn(`   Coordinates check - From: ${fromCoords}, To: ${toCoords}`);
            return;
        }
        
        console.log(`  ✅ Route coordinates found: ${flow.from} [${fromCoords}] → ${flow.to} [${toCoords}]`);
        
        // Convert lat/lng to 3D coordinates
        const fromPoint = this.latLngTo3D(fromCoords[0], fromCoords[1]);
        const toPoint = this.latLngTo3D(toCoords[0], toCoords[1]);
        
        console.log(`  🌍 3D points: From ${fromPoint.x.toFixed(2)},${fromPoint.y.toFixed(2)},${fromPoint.z.toFixed(2)} → To ${toPoint.x.toFixed(2)},${toPoint.y.toFixed(2)},${toPoint.z.toFixed(2)}`);
        
        // Create curved path
        const curve = this.createCurvedPath(fromPoint, toPoint);
        
        // Create route line
        const routeLine = this.createRouteLine(curve, flow);
        this.group.add(routeLine);
        
        // Create animated particles
        const particles = this.createAnimatedParticles(curve, flow);
        particles.forEach(particle => {
            this.group.add(particle);
            this.animatedParticles.push({
                mesh: particle,
                curve: curve,
                progress: Math.random(), // Random start position
                speed: this.getSpeedFromValue(flow.value),
                flow: flow
            });
        });
        
        this.tradeFlows.push({ routeLine, particles, flow });
    }
    
    latLngTo3D(lat, lng) {
        const latRad = lat * Math.PI / 180;
        const lngRad = lng * Math.PI / 180;
        
        const radius = 1.02; // Slightly above globe surface
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
        // Calculate control point for arc (higher altitude)
        const midPoint = new THREE.Vector3()
            .addVectors(fromPoint, toPoint)
            .multiplyScalar(0.5);
        
        // Lift the midpoint for arc effect
        const distance = fromPoint.distanceTo(toPoint);
        const heightFactor = Math.min(distance * 0.3, WGS84_ELLIPSOID.radius.x * 0.5);
        midPoint.normalize().multiplyScalar(WGS84_ELLIPSOID.radius.x + heightFactor);
        
        return new THREE.CatmullRomCurve3([fromPoint, midPoint, toPoint]);
    }
    
    createRouteLine(curve, flow) {
        const points = curve.getPoints(50); // Reduced from 100 to 50 for performance
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        // Enhanced color coding by trade value and commodity type
        const color = this.getEnhancedColor(flow);
        const material = new THREE.LineBasicMaterial({ 
            color: color,
            transparent: true,
            opacity: flow.source === 'USITC Demo' ? 0.9 : 0.6, // Higher opacity for USITC flows
            linewidth: this.getLineWidthFromValue(flow.value)
        });
        
        return new THREE.Line(geometry, material);
    }
    
    createAnimatedParticles(curve, flow) {
        const particles = [];
        const particleCount = Math.max(2, Math.floor(flow.value / 10)); // More particles for higher value
        
        for (let i = 0; i < particleCount; i++) {
            const geometry = new THREE.SphereGeometry(0.008 * WGS84_ELLIPSOID.radius.x, 6, 4); // Reduced from 8,6 to 6,4 for performance
            const material = new THREE.MeshBasicMaterial({ 
                color: this.getEnhancedColor(flow),
                transparent: true,
                opacity: 0.8
            });
            
            const particle = new THREE.Mesh(geometry, material);
            particles.push(particle);
        }
        
        return particles;
    }
    
    getEnhancedColor(flow) {
        // Real Census data gets distinct colors based on commodity
        if (flow.source === 'Census_Real') {
            if (flow.commodity?.includes('Processors') || flow.commodity?.includes('CPU')) return 0x00ff88; // Bright green for CPUs/GPUs
            if (flow.commodity?.includes('Memories') || flow.commodity?.includes('DRAM')) return 0xff0088; // Magenta for Memory
            if (flow.commodity?.includes('equipment') || flow.commodity?.includes('Equipment')) return 0x8800ff; // Purple for Equipment
            if (flow.commodity?.includes('Amplifiers')) return 0xffaa00; // Orange for Amplifiers
            return 0x00ffff; // Cyan for other real data
        }
        
        // USITC demo flows (if any)
        if (flow.source === 'USITC Demo') {
            if (flow.commodity?.includes('GPU')) return 0x00ff88; // Bright green for GPUs
            if (flow.commodity?.includes('DRAM')) return 0xff0088; // Magenta for DRAM
            if (flow.commodity?.includes('CPU')) return 0x8800ff; // Purple for CPUs
            return 0x00ffff; // Cyan for other USITC
        }
        
        // Standard UN Comtrade color coding by value
        return this.getColorFromValue(flow.value);
    }
    
    getColorFromValue(value) {
        if (value >= 30) return 0xff0000; // Red for $30B+ (scaled down from $1B+)
        if (value >= 15) return 0xff8800; // Orange for $15B+ (scaled down from $500M+)
        return 0x0088ff; // Blue for smaller values
    }
    
    getLineWidthFromValue(value) {
        return Math.max(1, Math.min(5, value / 10));
    }
    
    getSpeedFromValue(value) {
        return 0.001 + (value / 1000); // Faster animation for higher values
    }
    
    clearTradeFlows() {
        this.tradeFlows.forEach(({ routeLine, particles }) => {
            this.group.remove(routeLine);
            // Dispose geometry and material to prevent memory leaks
            if (routeLine.geometry) routeLine.geometry.dispose();
            if (routeLine.material) routeLine.material.dispose();
            
            particles.forEach(particle => {
                this.group.remove(particle);
                if (particle.geometry) particle.geometry.dispose();
                if (particle.material) particle.material.dispose();
            });
        });
        this.tradeFlows = [];
        this.animatedParticles = [];
    }
    
    updateAnimations() {
        // Optimize particle updates - only update every 2nd frame for smoother performance
        if (this.animationFrameCount % 2 === 0) {
            this.animatedParticles.forEach(({ mesh, curve, progress, speed }) => {
                // Update progress
                const newProgress = (progress + speed) % 1;
                
                // Get position on curve
                const position = curve.getPoint(newProgress);
                mesh.position.copy(position);
                
                // Update stored progress
                const particleData = this.animatedParticles.find(p => p.mesh === mesh);
                if (particleData) particleData.progress = newProgress;
            });
        }
        
        // Check if we need to refresh data
        const now = Date.now();
        if (now - this.lastUpdate > this.updateInterval) {
            this.lastUpdate = now;
            console.log('🔄 Auto-refreshing trade flow data...');
            this.loadTradeFlowData();
        }
    }
}

// Initialize trade flow manager
let tradeFlowManager;

// animation - optimized for performance
function animate() {
    controls.update(Math.min(clock.getDelta(), 64 / 1000));
    
    // Update trade flow animations
    if (tradeFlowManager) {
        tradeFlowManager.animationFrameCount++;
        tradeFlowManager.updateAnimations();
    }
    
    renderer.render(scene, camera);
    
    // Slower auto-rotation for smoother interaction
    group.rotation.z = window.performance.now() * 0.15e-4;
}

// resize handling - exact from original
function onResize() {
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
}

onResize();
window.addEventListener('resize', onResize);

// Mouse interaction for country labels
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let hoveredCountry = null;

function onMouseMove(event) {
    // Calculate mouse position in normalized device coordinates
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    
    // Update the picking ray with the camera and mouse position
    raycaster.setFromCamera(mouse, camera);
    
    // Find intersections with country lines
    const intersects = raycaster.intersectObjects(group.children.filter(child => 
        child.type === 'Line' && child.userData.countryName
    ));
    
    if (intersects.length > 0) {
        const countryName = intersects[0].object.userData.countryName;
        
        // Show label for hovered country
        if (hoveredCountry !== countryName) {
            hideAllLabels();
            showCountryLabel(countryName);
            hoveredCountry = countryName;
        }
    } else {
        // Hide labels when not hovering
        if (hoveredCountry) {
            hideAllLabels();
            hoveredCountry = null;
        }
    }
}

function showCountryLabel(countryName) {
    group.children.forEach(child => {
        if (child.userData.isLabel && child.userData.countryName === countryName) {
            child.visible = true;
        }
    });
}

function hideAllLabels() {
    group.children.forEach(child => {
        if (child.userData.isLabel) {
            child.visible = false;
        }
    });
}

// Add mouse event listener
window.addEventListener('mousemove', onMouseMove);

// Labels are now visible by default for major countries - no timeout needed


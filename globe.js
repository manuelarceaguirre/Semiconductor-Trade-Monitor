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

        // add base globe color - improved material rendering
        const globeBase = new THREE.Mesh(
            new THREE.SphereGeometry(1, 100, 50),
            new THREE.MeshStandardMaterial({
                color: 0x222222,
                transparent: true,
                opacity: 0.75,
                // depthWrite: false, // REMOVED - let it write to depth buffer
                premultipliedAlpha: true,
                side: THREE.FrontSide, // ADDED - only render outer surface
                roughness: 1.0, // ADDED - matte surface, no shine
                metalness: 0.0, // ADDED - non-metallic
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
        processGeoJSONFeatures(res.features, country, thickness, resolution, wireframeGroup);

        // scale and center the model - EXACT from original
        const box = new THREE.Box3();
        box.setFromObject(group);
        box.getCenter(group.position).multiplyScalar(-1);

        const size = new THREE.Vector3();
        box.getSize(size);
        group.scale.setScalar(1.5 / Math.max(...size.toArray()));
        group.position.multiplyScalar(group.scale.x);

        console.log(res);
        
        // Initialize trade flow manager after globe is loaded
        tradeFlowManager = new TradeFlowManager(scene, group);
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
                        const geometry = new THREE.BufferGeometry().setFromPoints(points);
                        
                        // Bright white solid lines for all countries
                        const material = new THREE.LineBasicMaterial({
                            color: 0xffffff, // Bright white
                        });

                        const line = new THREE.Line(geometry, material);
                        group.add(line);
                    }
                }
            });
        });
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
            
            // Connect to production API endpoint
            const response = await fetch('/v2/globe/trade-flows?min_value=500000000&period=recent');
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            
            const apiData = await response.json();
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
            
            console.log(`✅ Loaded ${tradeFlows.length} trade flows from production API`);
            console.log(`📈 Total trade value: $${(apiData.trade_flows?.reduce((sum, flow) => sum + flow.value, 0) / 1000000000).toFixed(1)}B`);
            if (apiData.metadata) {
                console.log(`⏰ Data last updated: ${apiData.metadata.last_updated}`);
                console.log(`🎯 Min value filter: $${(apiData.metadata.min_value_filter / 1000000000).toFixed(1)}B`);
            }
            
            // Fallback to sample data if API returns empty
            if (tradeFlows.length === 0) {
                console.log('⚠️ No API data, using sample trade flows');
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
            } else {
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
        // Clear existing flows
        this.clearTradeFlows();
        
        flows.forEach(flow => {
            this.createTradeRoute(flow);
        });
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
            return;
        }
        
        // Convert lat/lng to 3D coordinates
        const fromPoint = this.latLngTo3D(fromCoords[0], fromCoords[1]);
        const toPoint = this.latLngTo3D(toCoords[0], toCoords[1]);
        
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
        const points = curve.getPoints(100);
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        // Color coding by trade value
        const color = this.getColorFromValue(flow.value);
        const material = new THREE.LineBasicMaterial({ 
            color: color,
            transparent: true,
            opacity: 0.6,
            linewidth: this.getLineWidthFromValue(flow.value)
        });
        
        return new THREE.Line(geometry, material);
    }
    
    createAnimatedParticles(curve, flow) {
        const particles = [];
        const particleCount = Math.max(2, Math.floor(flow.value / 10)); // More particles for higher value
        
        for (let i = 0; i < particleCount; i++) {
            const geometry = new THREE.SphereGeometry(0.008 * WGS84_ELLIPSOID.radius.x, 8, 6);
            const material = new THREE.MeshBasicMaterial({ 
                color: this.getColorFromValue(flow.value),
                transparent: true,
                opacity: 0.8
            });
            
            const particle = new THREE.Mesh(geometry, material);
            particles.push(particle);
        }
        
        return particles;
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
            particles.forEach(particle => this.group.remove(particle));
        });
        this.tradeFlows = [];
        this.animatedParticles = [];
    }
    
    updateAnimations() {
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

// animation - EXACT from original
function animate() {
    controls.update(Math.min(clock.getDelta(), 64 / 1000));
    
    // Update trade flow animations
    if (tradeFlowManager) {
        tradeFlowManager.updateAnimations();
    }
    
    renderer.render(scene, camera);
    
    group.rotation.z = window.performance.now() * 0.25e-4;
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


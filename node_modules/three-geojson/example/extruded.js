import {
	PerspectiveCamera,
	Scene,
	WebGLRenderer,
	Group,
	Box3,
	Vector3,
	Clock,
	DirectionalLight,
	MeshStandardMaterial,
	AmbientLight,
} from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GeoJSONLoader } from '../src/index.js';

// camera
const camera = new PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.01, 1000 );
camera.position.z = 2;

// scene
const scene = new Scene();

// renderer
const renderer = new WebGLRenderer( { antialias: true } );
renderer.setAnimationLoop( animate );
document.body.appendChild( renderer.domElement );

// controls
const clock = new Clock();
const controls = new OrbitControls( camera, renderer.domElement );
controls.minDistance = 1;
controls.enableDamping = true;
controls.autoRotate = true;

const directionalLight = new DirectionalLight( 0xffffff, 3.5 );
directionalLight.position.set( 1, 2, 3 );

const ambientLight = new AmbientLight( 0xffffff, 1.0 );
scene.add( directionalLight, ambientLight );

// construct geo group
const group = new Group();
scene.add( group );

// load geojson
const url = new URL( './world.geojson', import.meta.url );
new GeoJSONLoader()
	.loadAsync( url )
	.then( res => {

		// load the globe lines
		res.features
			.filter( f => f.properties.name === 'Japan' )
			.flatMap( f => f.polygons )
			.forEach( geom => {

				const mesh = geom.getMeshObject( {
					thickness: 1,
				} );

				mesh.material = new MeshStandardMaterial();
				group.add( mesh );

			} );

		// scale and center the model
		const box = new Box3();
		box.setFromObject( group );
		box.getCenter( group.position ).multiplyScalar( - 1 );

		const size = new Vector3();
		box.getSize( size );
		group.scale.setScalar( 1 / Math.max( ...size ) );
		group.position.multiplyScalar( group.scale.x );

		console.log( res );

	} );

onResize();
window.addEventListener( 'resize', onResize );

// animation
function animate() {

	controls.update( Math.min( clock.getDelta(), 64 / 1000 ) );
	renderer.render( scene, camera );

}

function onResize() {

	renderer.setSize( window.innerWidth, window.innerHeight );
	renderer.setPixelRatio( window.devicePixelRatio );

	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();

}

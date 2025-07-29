import { Vector3 } from 'three';
import { unkinkPolygon } from '@turf/unkink-polygon';
import { dedupeCoordinates, isClockWise, isPointInPolygon } from './GeoJSONShapeUtils.js';

const _min = /* @__PURE__ */ new Vector3();
const _max = /* @__PURE__ */ new Vector3();
const _center = /* @__PURE__ */ new Vector3();

function fixLoop( loop ) {

	return unkinkPolygon( { type: 'Polygon', coordinates: [ loop ] } )
		.features
		.flatMap( feature => {

			return feature.geometry.type === 'Multipolygon' ?
				feature.geometry.coordinates.flatMap( loop => loop ) :
				feature.geometry.coordinates;

 		} );

}

export function splitPolygon( polygon ) {

	// get the dimension of the loops
	const dimension = polygon[ 0 ][ 0 ].length;

	// find the bounds of the shape
	getPolygonBounds( polygon, _min, _max );
	_center.addVectors( _min, _max ).multiplyScalar( 0.5 );

	// offset the shape to near zero to improve precision
	polygon.forEach( loop => loop.forEach( coord => {

		coord[ 0 ] -= _center.x;
		coord[ 1 ] -= _center.y;

	} ) );

	// fix up each shape separately
	const [ contour, ...holes ] = polygon;
	const fixedHoles = holes.flatMap( hole => fixLoop( hole ) );
	const fixedContours = fixLoop( contour );
	let fixedPolygons;

	// find the holes that are inside each contour
	if ( fixedContours.length === 1 ) {

		fixedPolygons = [[ contour, ...holes ]];

	} else {

		fixedPolygons = fixedContours.map( contour => {

			return [ contour, ...fixedHoles.filter( hole => {

				return isPointInPolygon( [ contour ], ...hole[ 0 ] );

			} ) ];

		} );

	}

	// Reset the centering
	fixedPolygons.forEach( shape => shape.forEach( loop => loop.forEach( coord => {

		coord[ 0 ] += _center.x;
		coord[ 1 ] += _center.y;

	} ) ) );

	// Fix the 2d offset
	if ( fixedPolygons.length > 1 && dimension > 2 ) {

		fixedPolygons.forEach( shape => shape.forEach( loop => loop.forEach( coord => {

			if ( coord.length === 2 ) {

				coord[ 2 ] = _center.z;

			}

		} ) ) );

	}

	return fixedPolygons;

}

export function getPolygonBounds( polygon, min, max ) {

	min.setScalar( Infinity );
	max.setScalar( - Infinity );
	polygon.forEach( loop => loop.forEach( coord => {

		const [ x, y, z = 0 ] = coord;
		min.x = Math.min( min.x, x );
		min.y = Math.min( min.y, y );
		min.z = Math.min( min.z, z );

		max.x = Math.max( max.x, x );
		max.y = Math.max( max.y, y );
		max.z = Math.max( max.z, z );

	} ) );

}

export function correctPolygonWinding( polygon ) {

	const [ contour, ...holes ] = polygon;
	if ( ! isClockWise( contour ) ) {

		contour.reverse();

	}

	holes.forEach( hole => {

		if ( isClockWise( hole ) ) {

			hole.reverse();

		}

	} );

	return polygon;

}

export function dedupePolygonPoints( polygon ) {

	return polygon
		.map( loop => dedupeCoordinates( loop.slice() ) )
		.filter( loop => loop.length > 3 );

}

export function countVerticesInPolygons( polygons ) {

	let total = 0;
	polygons.forEach( polygon => {

		polygon.forEach( loop => {

			total += loop.length;

		} );

	} );

	return total;

}

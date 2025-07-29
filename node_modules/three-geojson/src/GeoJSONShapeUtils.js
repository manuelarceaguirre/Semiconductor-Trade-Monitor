import { MathUtils } from 'three';

// Removes any duplicate vertices
export function dedupeCoordinates( coords ) {

	for ( let i = 0; i < coords.length - 1; i ++ ) {

		const ni = ( i + 1 ) % coords.length;
		const c = coords[ i ];
		const nc = coords[ ni ];

		if ( c[ 0 ] === nc[ 0 ] && c[ 1 ] === nc[ 1 ] ) {

			coords.splice( ni, 1 );
			i --;

		}

	}

	return coords;

}

// Retrieve the coordinate dimension
export function getDimension( coordinates ) {

	return coordinates?.length ?? null;

}

// Extract the non-schema keys from the GeoJSON object
export function extractForeignKeys( object ) {

	const result = { ...object };
	delete result.type;
	delete result.bbox;

	switch ( object.type ) {

		case 'Point':
		case 'MultiPoint':
		case 'LineString':
		case 'MultiLineString':
		case 'Polygon':
		case 'MultiPolygon':

			delete result.coordinates;
			break;

		case 'GeometryCollection':

			delete result.geometries;
			break;

		case 'Feature':

			delete result.id;
			delete result.properties;
			delete result.geometry;
			break;

		case 'FeatureCollection':

			delete result.features;
			break;

	}

	return result;

}

// Traverse the parsed tree
export function traverse( object, callback ) {

	callback( object );

	switch ( object.type ) {

		case 'GeometryCollection':
		case 'FeatureCollection':

			object.data.forEach( o => traverse( o, callback ) );
			break;

		case 'Feature':
			traverse( object.data, callback );
			break;

	}

}

// takes the provided line and resamples it so the segments are at most minDistance long
export function resampleLine( loop, minDistance, mode = 'grid' ) {

	const result = [];
	for ( let i = 0, li = loop.length; i < li - 1; i ++ ) {

		const ni = ( i + 1 ) % li;
		const c = loop[ i ];
		const nc = loop[ ni ];

		const dx = nc[ 0 ] - c[ 0 ];
		const dy = nc[ 1 ] - c[ 1 ];
		let steps;
		if ( mode === 'grid' ) {

			const dist = Math.sqrt( dx ** 2 + dy ** 2 );
			steps = Math.ceil( dist / minDistance );

		} else {

			const midy = ( c[ 1 ] + nc[ 1 ] ) / 2;
			const yDist = minDistance;
			const xDist = minDistance / Math.sin( Math.PI / 2 + MathUtils.DEG2RAD * midy );

			const ySteps = Math.abs( dy / yDist );
			const xSteps = Math.abs( dx / xDist );

			steps = Math.ceil( Math.max( xSteps, ySteps ) );

		}

		result.push( c );

		const [ cx, cy ] = c;
		for ( let j = 1; j < steps; j ++ ) {

			result.push( [ cx + dx * j / steps, cy + dy * j / steps ] );

		}

	}

	result.push( loop[ loop.length - 1 ] );

	return result;

}

// calculates the area of the given loop
export function calculateArea( loop ) {

	const n = loop.length;
	let a = 0.0;

	for ( let p = n - 1, q = 0; q < n; p = q ++ ) {

		a += loop[ p ][ 0 ] * loop[ q ][ 1 ] - loop[ q ][ 0 ] * loop[ p ][ 1 ];

	}

	return a * 0.5;

}

// returns whether the given loop is clockwise or not
export function isClockWise( loop ) {

	return calculateArea( loop ) < 0;

}

// returns the angle sum of all the segments relative to the given point
export function calculateAngleSum( loop, x, y ) {

	let angleSum = 0;
	for ( let i = 0, l = loop.length; i < l; i ++ ) {

		const ni = ( i + 1 ) % l;

		const c0 = loop[ i ];
		const c1 = loop[ ni ];

		let dx0 = c0[ 0 ] - x;
		let dy0 = c0[ 1 ] - y;
		let dx1 = c1[ 0 ] - x;
		let dy1 = c1[ 1 ] - y;

		const l0 = Math.sqrt( dx0 ** 2 + dy0 ** 2 );
		const l1 = Math.sqrt( dx1 ** 2 + dy1 ** 2 );

		dx0 /= l0;
		dy0 /= l0;

		dx1 /= l1;
		dy1 /= l1;

		angleSum += Math.atan2( dx0 * dy1 - dy0 * dx1, dx0 * dx1 + dy0 * dy1 );

	}

	return Math.abs( angleSum );

}

export function isPointInPolygon( polygon, x, y ) {

	// TODO: check distance to edges

	const [ contour, ...holes ] = polygon;
	const isInContour = calculateAngleSum( contour, x, y ) > 3.14;
	if ( ! isInContour ) {

		return false;

	}

	for ( let i = 0, l = holes.length; i < l; i ++ ) {

		const isInHole = calculateAngleSum( holes[ i ], x, y ) > 3.14;
		if ( isInHole ) {

			return false;

		}

	}

	return true;

}

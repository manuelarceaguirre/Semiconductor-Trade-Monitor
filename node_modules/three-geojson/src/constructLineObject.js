import { BufferAttribute, LineSegments, Vector3 } from 'three';
import { getCenter, offsetPoints, transformToEllipsoid } from './FlatVertexBufferUtils.js';
import { resampleLine } from './GeoJSONShapeUtils.js';

const _vec = /* @__PURE__ */ new Vector3();

// Takes a set of vertex data and constructs a line segment
export function constructLineObject( lineStrings, options = {} ) {

	const {
		flat = false,
		offset = 0,
		ellipsoid = null,
		resolution = null,
		altitudeScale = 1,
		groups = null,
	} = options;

	// resample the polygon edge
	if ( resolution !== null ) {

		lineStrings = lineStrings.map( loop => {

			return resampleLine( loop, resolution );

		} );

	}

	// calculate total segments
	let totalSegments = 0;
	lineStrings.forEach( vertices => {

		const segments = vertices.length - 1;
		totalSegments += segments * 2;

	} );

	// roll up all the vertices
	let index = 0;
	const posArray = new Array( totalSegments * 3 );
	const vertexCounts = [];
	lineStrings.forEach( vertices => {

		const length = vertices.length;
		const segments = length - 1;
		for ( let i = 0; i < segments; i ++ ) {

			const ni = ( i + 1 ) % length;

			const v0 = vertices[ i ];
			const v1 = vertices[ ni ];
			posArray[ index + 0 ] = v0[ 0 ];
			posArray[ index + 1 ] = v0[ 1 ];
			posArray[ index + 2 ] = ( flat ? 0 : v0[ 2 ] || 0 ) * altitudeScale + offset;

			posArray[ index + 3 ] = v1[ 0 ];
			posArray[ index + 4 ] = v1[ 1 ];
			posArray[ index + 5 ] = ( flat ? 0 : v1[ 2 ] || 0 ) * altitudeScale + offset;

			index += 6;

		}

		vertexCounts.push( segments * 2 );

	} );

	// transform the points to the ellipsoid
	if ( ellipsoid ) {

		transformToEllipsoid( posArray, ellipsoid );

	}

	// center the shape
	const line = new LineSegments();
	getCenter( posArray, line.position );
	_vec.copy( line.position ).multiplyScalar( - 1 );
	offsetPoints( posArray, ..._vec );

	line.geometry.setAttribute( 'position', new BufferAttribute( new Float32Array( posArray ), 3, false ) );

	if ( groups ) {

		const stack = [ ...groups ];
		let offset = 0;
		let materialIndex = 0;
		while ( stack.length ) {

			let count = stack.shift() || 0;
			let vertexCount = 0;
			while ( count !== 0 ) {

				vertexCount += vertexCounts.shift() || 0;
				count --;

			}

			line.geometry.addGroup( offset, vertexCount, materialIndex );
			materialIndex ++;
			offset += vertexCount;

		}

	}

	return line;

}

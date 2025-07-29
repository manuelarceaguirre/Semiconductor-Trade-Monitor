import Delaunator from 'delaunator';
import Constrainautor from '@kninnug/constrainautor';

export function getLoopEdges( loop, offset, target = [] ) {

	loop.forEach( ( e, i ) => {

		const e0 = i + offset;
		const e1 = ( i + 1 ) % loop.length + offset;

		target.push( [
			e0,
			e1,
		] );

	} );

	return target;

}

// find the triangle index with the provided edge
function findTriangleWithEdge( triangles, edge ) {

	const [ e0, e1 ] = edge;
	for ( let i = 0, l = triangles.length; i < l; i += 3 ) {

		for ( let j = 0; j < 3; j ++ ) {

			const n = ( j + 1 ) % 3;
			const t0 = triangles[ i + j ];
			const t1 = triangles[ i + n ];

			if ( t0 === e0 && t1 === e1 ) {

				return i / 3;

			}

		}

	}

	return - 1;

}

export function triangulate( contour, holes, extraPoints = [] ) {

	// retrieve the set of constrained indices
	let offset = 0;
	const constrainedIndices = [];
	getLoopEdges( contour, offset, constrainedIndices );
	offset += contour.length;

	holes.forEach( hole => {

		getLoopEdges( hole, offset, constrainedIndices );
		offset += hole.length;

	} );

	// construct the set of points
	const points = [ ...contour, ...holes.flatMap( hole => hole ), ...extraPoints ];
	const points2d = points.map( coord => [ coord[ 0 ], coord[ 1 ] ] );

	// construct the triangulation
	const delaunay = Delaunator.from( points2d );
	const con = new Constrainautor( delaunay );
	con.constrainAll( constrainedIndices );

	// find the triangles that make up the given polygon
	// TODO: move to a separate function
	const result = [];
	const { triangles, halfedges } = delaunay;
	const startTri = findTriangleWithEdge( triangles, constrainedIndices[ 0 ] );

	if ( startTri === - 1 ) {

		throw new Error();

	}

	const edgeHashSet = new Set();
	constrainedIndices.forEach( ( [ e0, e1 ] ) => {

		edgeHashSet.add( `${ e0 }_${ e1 }` );

	} );

	const traversed = new Set();
	const stack = [ startTri ];
	while ( stack.length > 0 ) {

		const tri = stack.pop();
		if ( traversed.has( tri ) ) {

			continue;

		}

		traversed.add( tri );

		const tri3 = 3 * tri;
		for ( let v = 0; v < 3; v ++ ) {

			// add this triangle to the list of results
			result.push( triangles[ tri3 + v ] );

			// calculate the next half edge index
			const siblingEdge = halfedges[ tri3 + v ];
			if ( siblingEdge === - 1 ) {

				continue;

			}

			// calculate the other tri index
			const otherTri = ~ ~ ( siblingEdge / 3 );
			if ( traversed.has( otherTri ) ) {

				continue;

			}

			const p0 = siblingEdge - ( otherTri * 3 );
			const p1 = ( p0 + 1 ) % 3;
			const e0 = triangles[ otherTri * 3 + p0 ];
			const e1 = triangles[ otherTri * 3 + p1 ];
			const found = edgeHashSet.has( `${ e1 }_${ e0 }` );

			if ( ! found ) {

				stack.push( otherTri );

			}

		}

	}

	return {
		indices: result,
		edges: constrainedIndices,
		points,
	};

}

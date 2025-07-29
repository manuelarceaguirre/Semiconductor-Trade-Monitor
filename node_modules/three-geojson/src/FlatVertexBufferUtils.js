import { Vector3, Box3, MathUtils } from 'three';

const _vec = /* @__PURE__ */ new Vector3();
const _box = /* @__PURE__ */ new Box3();

export function getCenter( arr, target ) {

	_box.makeEmpty();

	for ( let i = 0, l = arr.length; i < l; i += 3 ) {

		_vec.x = arr[ i + 0 ];
		_vec.y = arr[ i + 1 ];
		_vec.z = arr[ i + 2 ];
		_box.expandByPoint( _vec );

	}

	_box.getCenter( target );

}

export function transformToEllipsoid( arr, ellipsoid ) {

	for ( let i = 0, l = arr.length; i < l; i += 3 ) {

		const lon = arr[ i + 0 ];
		const lat = arr[ i + 1 ];
		const alt = arr[ i + 2 ];
		ellipsoid.getCartographicToPosition( lat * MathUtils.DEG2RAD, lon * MathUtils.DEG2RAD, alt, _vec );
		arr[ i + 0 ] = _vec.x;
		arr[ i + 1 ] = _vec.y;
		arr[ i + 2 ] = _vec.z;

	}

}

export function offsetPoints( arr, x, y, z ) {

	for ( let i = 0, l = arr.length; i < l; i += 3 ) {

		arr[ i + 0 ] += x;
		arr[ i + 1 ] += y;
		arr[ i + 2 ] += z;

	}

}

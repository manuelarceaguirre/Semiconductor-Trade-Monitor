import { getDimension, extractForeignKeys, traverse } from './GeoJSONShapeUtils.js';
import { parseBounds } from './ParseUtils.js';
import { constructLineObject } from './constructLineObject.js';
import { constructPolygonMeshObject } from './constructPolygonMeshObject.js';

// Get the base object definition for GeoJSON type
function getBase( object ) {

	return {
		type: object.type,
		boundingBox: parseBounds( object.bbox ),
		data: null,
		foreign: extractForeignKeys( object ),
	};

}

// Shape construction functions
function getLineObject( options = {} ) {

	return constructLineObject( this.data, options );


}

function getPolygonLineObject( options = {} ) {

	return constructLineObject( this.data.flatMap( shape => shape ), options );

}

function getPolygonMeshObject( options ) {

	return constructPolygonMeshObject( this.data, options );

}

// Parser for GeoJSON https://geojson.org/
export class GeoJSONLoader {

	// Construct a merged geometry of all lines
	static getLineObject( objects, options ) {

		const lines = [];
		const groups = [];
		objects.forEach( o => {

			if ( /LineString/.test( o.type ) ) {

				lines.push( ...o.data );
				groups.push( o.data.length );

			} else if ( /Polygon/.test( o.type ) ) {

				const shapes = o.data.flatMap( shape => shape );
				lines.push( ...shapes );
				groups.push( shapes.length );

			}

		} );

		return constructLineObject( lines, {
			...options,
			groups: [],
	 	} );

	}

	// Construct a merged geometry of all shapes
	static getMeshObject( objects, options ) {

		// TODO: support cap / edges group generation. Requires groups caps and edges for each individual geometry together
		const polygons = [];
		const groups = [];
		objects.forEach( o => {

			if ( /Polygon/.test( o.type ) ) {

				const shapes = o.data;
				polygons.push( ...shapes );
				groups.push( shapes.length );

			}

		} );

		return constructPolygonMeshObject( polygons, {
			...options,
			groups,
	 	} );

	}

	constructor() {

		this.fetchOptions = {};

	}

	loadAsync( url ) {

		return fetch( url )
			.then( res => res.json() )
			.then( json => this.parse( json ) );

	}

	parse( json ) {

		if ( typeof json === 'string' ) {

			json = JSON.parse( json );

		}

		const root = this.parseObject( json );
		const features = [];
		const geometries = [];

		// find all features and geometries
		traverse( root, object => {

			if ( object.type !== 'FeatureCollection' && object.type !== 'GeometryCollection' ) {

				if ( object.type === 'Feature' ) {

					features.push( object );

				} else {

					geometries.push( object );

					if ( object.feature ) {

						object.feature.geometries.push( object );

					}

				}

			}

		} );

		// collect all shapes within each feature
		features.forEach( feature => {

			const { geometries } = feature;
			feature.points = geometries.filter( object => /Point/.test( object.type ) );
			feature.lines = geometries.filter( object => /Line/.test( object.type ) );
			feature.polygons = geometries.filter( object => /Polygon/.test( object.type ) );

		} );

		return {
			features,
			geometries,
			points: geometries.filter( object => /Point/.test( object.type ) ),
			lines: geometries.filter( object => /Line/.test( object.type ) ),
			polygons: geometries.filter( object => /Polygon/.test( object.type ) ),
		};

	}

	parseObject( object, feature = null ) {

		switch ( object.type ) {

			case 'Point': {

				return {
					...getBase( object ),
					feature,
					data: [ object.coordinates ],
					dimension: getDimension( object.coordinates ),
				};

			}

			case 'MultiPoint': {

				return {
					...getBase( object ),
					feature,
					data: object.coordinates,
					dimension: getDimension( object.coordinates[ 0 ] ),
				};

			}

			case 'LineString': {

				return {
					...getBase( object ),
					feature,
					data: [ object.coordinates ],
					dimension: getDimension( object.coordinates[ 0 ] ),

					getLineObject,
				};

			}

			case 'MultiLineString': {

				return {
					...getBase( object ),
					feature,
					data: object.coordinates,
					dimension: getDimension( object.coordinates[ 0 ][ 0 ] ),

					getLineObject,
				};

			}

			case 'Polygon': {

				return {
					...getBase( object ),
					feature,
					data: [ object.coordinates ],
					dimension: getDimension( object.coordinates[ 0 ][ 0 ] ),

					getLineObject: getPolygonLineObject,
					getMeshObject: getPolygonMeshObject,
				};

			}

			case 'MultiPolygon': {

				return {
					...getBase( object ),
					feature,
					data: object.coordinates,
					dimension: getDimension( object.coordinates[ 0 ][ 0 ][ 0 ] ),

					getLineObject: getPolygonLineObject,
					getMeshObject: getPolygonMeshObject,
				};

			}

			case 'GeometryCollection': {

				return {
					...getBase( object ),
					feature,
					data: object.geometries.map( obj => this.parseObject( obj, feature ) ),
				};

			}

			case 'Feature': {

				const feature = {
					...getBase( object ),
					id: object.id ?? null,
					properties: object.properties,
					geometries: [],
					data: null,
				};

				feature.data = this.parseObject( object.geometry, feature );
				return feature;

			}

			case 'FeatureCollection': {

				return {
					...getBase( object ),
					data: object.features.map( feat => this.parseObject( feat ) ),
				};

			}

		}

	}

}

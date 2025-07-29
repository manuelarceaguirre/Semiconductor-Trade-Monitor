import { GeoJSONLoader } from './GeoJSONLoader.js';
import { wktToGeoJSON } from "betterknown";

export class WKTLoader extends GeoJSONLoader {

	loadAsync( url ) {

		return fetch( url )
			.then( res => res.text() )
			.then( json => this.parse( json ) );

	}

	parse( text ) {

		return super.parse( wktToGeoJSON( text ) );

	}

}

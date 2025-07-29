import { searchForWorkspaceRoot, loadEnv } from 'vite';
import fs from 'fs';

export default ( { mode } ) => {

	process.env = { ...process.env, ...loadEnv( mode, process.cwd() ) };

	return {

		root: './example/',
		envDir: '.',
		base: '',
		build: {
			outDir: './bundle/',
			rollupOptions: {
				input: [
					...fs.readdirSync( './example/' ),
				]
					.filter( p => /\.html$/.test( p ) )
					.map( p => `./example/${ p }` ),
			},
		},
		server: {
			fs: {
				allow: [
					// search up for workspace root
					searchForWorkspaceRoot( process.cwd() ),
				],
			},
		},
	};

};

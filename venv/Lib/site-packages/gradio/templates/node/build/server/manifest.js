const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {start:"_app/immutable/entry/start.S7FLmPsw.js",app:"_app/immutable/entry/app.BgNyzhTG.js",imports:["_app/immutable/entry/start.S7FLmPsw.js","_app/immutable/chunks/D7YGuTcL.js","_app/immutable/chunks/BiJ6z1av.js","_app/immutable/chunks/DcUPjU6e.js","_app/immutable/entry/app.BgNyzhTG.js","_app/immutable/chunks/BYUUP2JM.js","_app/immutable/chunks/BiJ6z1av.js","_app/immutable/chunks/DcUPjU6e.js","_app/immutable/chunks/m3X5E8Ce.js","_app/immutable/chunks/B9qV0nBn.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./chunks/0-BxOarSIg.js')),
			__memo(() => import('./chunks/1-Ca_Em4sS.js')),
			__memo(() => import('./chunks/2-htxqz-Pd.js').then(function (n) { return n.c; }))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/[...catchall]",
				pattern: /^(?:\/([^]*))?\/?$/,
				params: [{"name":"catchall","optional":false,"rest":true,"chained":true}],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();

const prerendered = new Set([]);

const base = "";

export { base, manifest, prerendered };
//# sourceMappingURL=manifest.js.map

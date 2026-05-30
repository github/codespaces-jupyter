import { s as ssr_context } from './context-CBkBucIx.js';
import { n as noop } from './async-D55cHugf.js';

/** @import { SSRContext } from '#server' */
/** @import { Renderer } from './internal/server/renderer.js' */

/** @param {() => void} fn */
function onDestroy(fn) {
	/** @type {Renderer} */ (/** @type {SSRContext} */ (ssr_context).r).on_destroy(fn);
}

function createEventDispatcher() {
	return noop;
}

async function tick() {}

export { createEventDispatcher as c, onDestroy as o, tick as t };
//# sourceMappingURL=index-server-CQz6EZl_.js.map

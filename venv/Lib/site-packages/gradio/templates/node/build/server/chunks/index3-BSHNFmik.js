import { n as noop } from './async-D55cHugf.js';
import { f as attr_class, g as attr_style, i as stringify, e as ensure_array_like, s as slot, b as store_get, u as unsubscribe_stores } from './index-u8mz_F03.js';
import { w as writable } from './index-Cg-Pg6j3.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import { w } from './IconButton-BRnu7KaR.js';
import { o } from './Clear-D7Yjckqz.js';
import './2-htxqz-Pd.js';

/** @import { Raf } from '#client' */

const now = () => Date.now();

/** @type {Raf} */
const raf = {
	// don't access requestAnimationFrame eagerly outside method
	// this allows basic testing of user code without JSDOM
	// bunder will eval and remove ternary when the user's app is built
	tick: /** @param {any} _ */ (_) => (noop)(),
	now: () => now(),
	tasks: new Set()
};

/** @import { TaskCallback, Task, TaskEntry } from '#client' */

/**
 * Creates a new task that runs on each raf frame
 * until it returns a falsy value or is aborted
 * @param {TaskCallback} callback
 * @returns {Task}
 */
function loop(callback) {
	/** @type {TaskEntry} */
	let task;

	if (raf.tasks.size === 0) ;

	return {
		promise: new Promise((fulfill) => {
			raf.tasks.add((task = { c: callback, f: fulfill }));
		}),
		abort() {
			raf.tasks.delete(task);
		}
	};
}

/**
 * @param {any} obj
 * @returns {obj is Date}
 */
function is_date(obj) {
	return Object.prototype.toString.call(obj) === '[object Date]';
}

/** @import { Task } from '#client' */
/** @import { SpringOpts, SpringUpdateOpts, TickContext } from './private.js' */
/** @import { Spring as SpringStore } from './public.js' */

/**
 * @template T
 * @param {TickContext} ctx
 * @param {T} last_value
 * @param {T} current_value
 * @param {T} target_value
 * @returns {T}
 */
function tick_spring(ctx, last_value, current_value, target_value) {
	if (typeof current_value === 'number' || is_date(current_value)) {
		// @ts-ignore
		const delta = target_value - current_value;
		// @ts-ignore
		const velocity = (current_value - last_value) / (ctx.dt || 1 / 60); // guard div by 0
		const spring = ctx.opts.stiffness * delta;
		const damper = ctx.opts.damping * velocity;
		const acceleration = (spring - damper) * ctx.inv_mass;
		const d = (velocity + acceleration) * ctx.dt;
		if (Math.abs(d) < ctx.opts.precision && Math.abs(delta) < ctx.opts.precision) {
			return target_value; // settled
		} else {
			ctx.settled = false; // signal loop to keep ticking
			// @ts-ignore
			return is_date(current_value) ? new Date(current_value.getTime() + d) : current_value + d;
		}
	} else if (Array.isArray(current_value)) {
		// @ts-ignore
		return current_value.map((_, i) =>
			// @ts-ignore
			tick_spring(ctx, last_value[i], current_value[i], target_value[i])
		);
	} else if (typeof current_value === 'object') {
		const next_value = {};
		for (const k in current_value) {
			// @ts-ignore
			next_value[k] = tick_spring(ctx, last_value[k], current_value[k], target_value[k]);
		}
		// @ts-ignore
		return next_value;
	} else {
		throw new Error(`Cannot spring ${typeof current_value} values`);
	}
}

/**
 * The spring function in Svelte creates a store whose value is animated, with a motion that simulates the behavior of a spring. This means when the value changes, instead of transitioning at a steady rate, it "bounces" like a spring would, depending on the physics parameters provided. This adds a level of realism to the transitions and can enhance the user experience.
 *
 * @deprecated Use [`Spring`](https://svelte.dev/docs/svelte/svelte-motion#Spring) instead
 * @template [T=any]
 * @param {T} [value]
 * @param {SpringOpts} [opts]
 * @returns {SpringStore<T>}
 */
function spring(value, opts = {}) {
	const store = writable(value);
	const { stiffness = 0.15, damping = 0.8, precision = 0.01 } = opts;
	/** @type {number} */
	let last_time;
	/** @type {Task | null} */
	let task;
	/** @type {object} */
	let current_token;

	let last_value = /** @type {T} */ (value);
	let target_value = /** @type {T | undefined} */ (value);

	let inv_mass = 1;
	let inv_mass_recovery_rate = 0;
	let cancel_task = false;
	/**
	 * @param {T} new_value
	 * @param {SpringUpdateOpts} opts
	 * @returns {Promise<void>}
	 */
	function set(new_value, opts = {}) {
		target_value = new_value;
		const token = (current_token = {});
		if (value == null || opts.hard || (spring.stiffness >= 1 && spring.damping >= 1)) {
			cancel_task = true; // cancel any running animation
			last_time = raf.now();
			last_value = new_value;
			store.set((value = target_value));
			return Promise.resolve();
		} else if (opts.soft) {
			const rate = opts.soft === true ? 0.5 : +opts.soft;
			inv_mass_recovery_rate = 1 / (rate * 60);
			inv_mass = 0; // infinite mass, unaffected by spring forces
		}
		if (!task) {
			last_time = raf.now();
			cancel_task = false;
			task = loop((now) => {
				if (cancel_task) {
					cancel_task = false;
					task = null;
					return false;
				}
				inv_mass = Math.min(inv_mass + inv_mass_recovery_rate, 1);

				// clamp elapsed time to 1/30th of a second, so that longer pauses
				// (blocked thread or inactive tab) don't cause the spring to go haywire
				const elapsed = Math.min(now - last_time, 1000 / 30);

				/** @type {TickContext} */
				const ctx = {
					inv_mass,
					opts: spring,
					settled: true,
					dt: (elapsed * 60) / 1000
				};
				// @ts-ignore
				const next_value = tick_spring(ctx, last_value, value, target_value);
				last_time = now;
				last_value = /** @type {T} */ (value);
				store.set((value = /** @type {T} */ (next_value)));
				if (ctx.settled) {
					task = null;
				}
				return !ctx.settled;
			});
		}
		return new Promise((fulfil) => {
			/** @type {Task} */ (task).promise.then(() => {
				if (token === current_token) fulfil();
			});
		});
	}
	/** @type {SpringStore<T>} */
	// @ts-expect-error - class-only properties are missing
	const spring = {
		set,
		update: (fn, opts) => set(fn(/** @type {T} */ (target_value), /** @type {T} */ (value)), opts),
		subscribe: store.subscribe,
		stiffness,
		damping,
		precision
	};
	return spring;
}

function B(p,h){p.component(s=>{var a;let{margin:b=true}=h;const c=spring([0,0]),m=spring([0,0]);s.push(`<div${attr_class("svelte-1vhirvf",void 0,{margin:b})}><svg viewBox="-1200 -1200 3000 3000" fill="none" xmlns="http://www.w3.org/2000/svg" class="svelte-1vhirvf"><g${attr_style(`transform: translate(${stringify(store_get(a??={},"$top",c)[0])}px, ${stringify(store_get(a??={},"$top",c)[1])}px);`)}><path d="M255.926 0.754768L509.702 139.936V221.027L255.926 81.8465V0.754768Z" fill="#FF7C00" fill-opacity="0.4" class="svelte-1vhirvf"></path><path d="M509.69 139.936L254.981 279.641V361.255L509.69 221.55V139.936Z" fill="#FF7C00" class="svelte-1vhirvf"></path><path d="M0.250138 139.937L254.981 279.641V361.255L0.250138 221.55V139.937Z" fill="#FF7C00" fill-opacity="0.4" class="svelte-1vhirvf"></path><path d="M255.923 0.232622L0.236328 139.936V221.55L255.923 81.8469V0.232622Z" fill="#FF7C00" class="svelte-1vhirvf"></path></g><g${attr_style(`transform: translate(${stringify(store_get(a??={},"$bottom",m)[0])}px, ${stringify(store_get(a??={},"$bottom",m)[1])}px);`)}><path d="M255.926 141.5L509.702 280.681V361.773L255.926 222.592V141.5Z" fill="#FF7C00" fill-opacity="0.4" class="svelte-1vhirvf"></path><path d="M509.69 280.679L254.981 420.384V501.998L509.69 362.293V280.679Z" fill="#FF7C00" class="svelte-1vhirvf"></path><path d="M0.250138 280.681L254.981 420.386V502L0.250138 362.295V280.681Z" fill="#FF7C00" fill-opacity="0.4" class="svelte-1vhirvf"></path><path d="M255.923 140.977L0.236328 280.68V362.294L255.923 222.591V140.977Z" fill="#FF7C00" class="svelte-1vhirvf"></path></g></svg></div>`),a&&unsubscribe_stores(a);});}function x(p){let h=["","k","M","G","T","P","E","Z"],s=0;for(;p>1e3&&s<h.length-1;)p/=1e3,s++;let a=h[s];return (Number.isInteger(p)?p:p.toFixed(1))+a}function $(p,h){p.component(s=>{let{i18n:a,eta:b=null,queue_position:c,queue_size:m,component_id:S=null,fn_index:E=null,status:e,scroll_to_output:G=false,timer:F=true,show_progress:n="full",message:N=null,progress:v=null,variant:g="default",loading_text:C="Loading...",absolute:L=true,translucent:d=false,border:k=false,autoscroll:P,validation_error:_=null,show_validation_error:y=true,type:M=null,on_clear_status:T,used_cache:X=null,cache_duration:A=null,avg_time:D=null,cache_event_id:H=null}=h,Z=null;const I=!(y&&_)&&(M==="input"||!e||e==="complete"||n==="hidden"||e=="streaming"),q=0 .toFixed(1);let z=v==null,o$1=(()=>{let u=null;v!=null?u=v.map(t=>{if(t.index!=null&&t.length!=null)return t.index/t.length;if(t.progress!=null)return t.progress}):u=null;let i,f="";return u?(i=u[u.length-1],i===0?f="0":f="150ms"):i=void 0,{progress_level:u,last_progress_level:i,progress_bar_transition:f}})();if(s.push(`<div${attr_class(`wrap ${stringify(g)} ${stringify(n)}`,"svelte-1uj8rng",{"no-click":_&&y,hide:I,translucent:g==="center"&&(e==="pending"||e==="error")||d||n==="minimal"||_,generating:e==="generating"&&n==="full",border:k})} data-testid="status-tracker"${attr_style("",{position:L?"absolute":"static",padding:L?"0":"var(--size-8) 0"})}>`),_&&y?(s.push("<!--[-->"),s.push(`<div class="validation-error svelte-1uj8rng">${escape_html(_)} <button class="svelte-1uj8rng">`),w(s,{Icon:o,label:a?a("common.clear"):"Clear",disabled:false,size:"x-small",background:"var(--background-fill-primary)",color:"var(--error-background-text)",border:"var(--border-color-primary)",onclick:()=>_=null}),s.push("<!----></button></div>")):s.push("<!--[!-->"),s.push("<!--]--> "),e==="pending"){if(s.push("<!--[-->"),g==="default"&&z&&n==="full"?(s.push("<!--[-->"),s.push(`<div class="eta-bar svelte-1uj8rng"${attr_style("",{transform:`translateX(${stringify(-100)}%)`})}></div>`)):s.push("<!--[!-->"),s.push(`<!--]--> <div${attr_class("progress-text svelte-1uj8rng",void 0,{"meta-text-center":g==="center","meta-text":g==="default"})}>`),v){s.push("<!--[-->"),s.push("<!--[-->");const u=ensure_array_like(v);for(let i=0,f=u.length;i<f;i++){let t=u[i];t.index!=null?(s.push("<!--[-->"),t.length!=null?(s.push("<!--[-->"),s.push(`${escape_html(x(t.index||0))}/${escape_html(x(t.length))}`)):(s.push("<!--[!-->"),s.push(`${escape_html(x(t.index||0))}`)),s.push(`<!--]--> ${escape_html(t.unit)} |  `)):s.push("<!--[!-->"),s.push("<!--]-->");}s.push("<!--]-->");}else s.push("<!--[!-->"),c!==null&&m!==void 0&&c>=0?(s.push("<!--[-->"),s.push(`queue: ${escape_html(c+1)}/${escape_html(m)} |`)):(s.push("<!--[!-->"),c===0?(s.push("<!--[-->"),s.push("processing |")):s.push("<!--[!-->"),s.push("<!--]-->")),s.push("<!--]-->");if(s.push("<!--]--> "),F?(s.push("<!--[-->"),s.push(`${escape_html(q)}${escape_html(b?`/${Z}`:"")}s`)):s.push("<!--[!-->"),s.push("<!--]--></div> "),o$1.last_progress_level!=null){if(s.push("<!--[-->"),s.push('<div class="progress-level svelte-1uj8rng"><div class="progress-level-inner svelte-1uj8rng">'),v!=null){s.push("<!--[-->"),s.push("<!--[-->");const u=ensure_array_like(v);for(let i=0,f=u.length;i<f;i++){let t=u[i];t.desc!=null||o$1.progress_level&&o$1.progress_level[i]!=null?(s.push("<!--[-->"),i!==0?(s.push("<!--[-->"),s.push(" /")):s.push("<!--[!-->"),s.push("<!--]--> "),t.desc!=null?(s.push("<!--[-->"),s.push(`${escape_html(t.desc)}`)):s.push("<!--[!-->"),s.push("<!--]--> "),t.desc!=null&&o$1.progress_level&&o$1.progress_level[i]!=null?(s.push("<!--[-->"),s.push("-")):s.push("<!--[!-->"),s.push("<!--]--> "),o$1.progress_level!=null?(s.push("<!--[-->"),s.push(`${escape_html((100*(o$1.progress_level[i]||0)).toFixed(1))}%`)):s.push("<!--[!-->"),s.push("<!--]-->")):s.push("<!--[!-->"),s.push("<!--]-->");}s.push("<!--]-->");}else s.push("<!--[!-->");s.push(`<!--]--></div> <div class="progress-bar-wrap svelte-1uj8rng"><div class="progress-bar svelte-1uj8rng"${attr_style("",{width:`${stringify(o$1.last_progress_level*100)}%`,transition:o$1.progress_bar_transition})}></div></div></div>`);}else s.push("<!--[!-->"),n==="full"?(s.push("<!--[-->"),B(s,{margin:g==="default"})):s.push("<!--[!-->"),s.push("<!--]-->");s.push("<!--]--> "),F?s.push("<!--[!-->"):(s.push("<!--[-->"),s.push(`<p class="loading svelte-1uj8rng">${escape_html(C)}</p> <!--[-->`),slot(s,h,"additional-loading-text",{}),s.push("<!--]-->")),s.push("<!--]-->");}else s.push("<!--[!-->"),e==="error"?(s.push("<!--[-->"),s.push('<div class="clear-status svelte-1uj8rng">'),w(s,{Icon:o,label:a("common.clear"),disabled:false}),s.push(`<!----></div> <span class="error svelte-1uj8rng">${escape_html(a("common.error"))}</span> <!--[-->`),slot(s,h,"error",{}),s.push("<!--]-->")):s.push("<!--[!-->"),s.push("<!--]-->");s.push("<!--]--></div> "),s.push("<!--[!-->"),s.push("<!--]-->");});}

export { $, B, is_date as i, loop as l, raf as r, spring as s };
//# sourceMappingURL=index3-BSHNFmik.js.map

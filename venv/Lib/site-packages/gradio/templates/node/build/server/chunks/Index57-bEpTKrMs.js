import { f as fallback } from './async-D55cHugf.js';
import { c as spread_props, b as store_get, u as unsubscribe_stores, d as bind_props, f as attr_class, s as slot, g as attr_style, i as stringify, n as sanitize_props, r as rest_props, m as attributes } from './index-u8mz_F03.js';
import { t as tick } from './index-server-CQz6EZl_.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { k } from './BlockLabel-bKYWnOzQ.js';
import { u } from './DownloadLink-nj1p0krE.js';
import { w } from './IconButton-BRnu7KaR.js';
import { p } from './Empty-DGRbZO0a.js';
import { o } from './Clear-D7Yjckqz.js';
import { l } from './Download-DcU5dONL.js';
import { i } from './Image2-vcp9_ifi.js';
import { r } from './Undo-Ce01x-M5.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { k as k$1 } from './FullscreenButton-Bm0pL3TN.js';
import { w as writable } from './index-Cg-Pg6j3.js';
import { l as loop, r as raf, i as is_date, $ as $$1 } from './index3-BSHNFmik.js';
import { e as ee$1 } from './Upload2-CIse88hO.js';
import { G } from './Block-DZmzQwnI.js';
import { k as k$2 } from './UploadText-BDXc1cBO.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './clone-Yk88IHKV.js';
import './Maximize-CuHbK64j.js';
import './Upload-BbxeBrrD.js';

/*
Adapted from https://github.com/mattdesl
Distributed under MIT License https://github.com/mattdesl/eases/blob/master/LICENSE.md
*/

/**
 * @param {number} t
 * @returns {number}
 */
function linear(t) {
	return t;
}

/** @import { Task } from '../internal/client/types' */
/** @import { Tweened } from './public' */
/** @import { TweenedOptions } from './private' */

/**
 * @template T
 * @param {T} a
 * @param {T} b
 * @returns {(t: number) => T}
 */
function get_interpolator(a, b) {
	if (a === b || a !== a) return () => a;

	const type = typeof a;
	if (type !== typeof b || Array.isArray(a) !== Array.isArray(b)) {
		throw new Error('Cannot interpolate values of different type');
	}

	if (Array.isArray(a)) {
		const arr = /** @type {Array<any>} */ (b).map((bi, i) => {
			return get_interpolator(/** @type {Array<any>} */ (a)[i], bi);
		});

		// @ts-ignore
		return (t) => arr.map((fn) => fn(t));
	}

	if (type === 'object') {
		if (!a || !b) {
			throw new Error('Object cannot be null');
		}

		if (is_date(a) && is_date(b)) {
			const an = a.getTime();
			const bn = b.getTime();
			const delta = bn - an;

			// @ts-ignore
			return (t) => new Date(an + t * delta);
		}

		const keys = Object.keys(b);

		/** @type {Record<string, (t: number) => T>} */
		const interpolators = {};
		keys.forEach((key) => {
			// @ts-ignore
			interpolators[key] = get_interpolator(a[key], b[key]);
		});

		// @ts-ignore
		return (t) => {
			/** @type {Record<string, any>} */
			const result = {};
			keys.forEach((key) => {
				result[key] = interpolators[key](t);
			});
			return result;
		};
	}

	if (type === 'number') {
		const delta = /** @type {number} */ (b) - /** @type {number} */ (a);
		// @ts-ignore
		return (t) => a + t * delta;
	}

	// for non-numeric values, snap to the final value immediately
	return () => b;
}

/**
 * A tweened store in Svelte is a special type of store that provides smooth transitions between state values over time.
 *
 * @deprecated Use [`Tween`](https://svelte.dev/docs/svelte/svelte-motion#Tween) instead
 * @template T
 * @param {T} [value]
 * @param {TweenedOptions<T>} [defaults]
 * @returns {Tweened<T>}
 */
function tweened(value, defaults = {}) {
	const store = writable(value);
	/** @type {Task} */
	let task;
	let target_value = value;
	/**
	 * @param {T} new_value
	 * @param {TweenedOptions<T>} [opts]
	 */
	function set(new_value, opts) {
		target_value = new_value;

		if (value == null) {
			store.set((value = new_value));
			return Promise.resolve();
		}

		/** @type {Task | null} */
		let previous_task = task;

		let started = false;
		let {
			delay = 0,
			duration = 400,
			easing = linear,
			interpolate = get_interpolator
		} = { ...defaults, ...opts };

		if (duration === 0) {
			if (previous_task) {
				previous_task.abort();
				previous_task = null;
			}
			store.set((value = target_value));
			return Promise.resolve();
		}

		const start = raf.now() + delay;

		/** @type {(t: number) => T} */
		let fn;
		task = loop((now) => {
			if (now < start) return true;
			if (!started) {
				fn = interpolate(/** @type {any} */ (value), new_value);
				if (typeof duration === 'function')
					duration = duration(/** @type {any} */ (value), new_value);
				started = true;
			}
			if (previous_task) {
				previous_task.abort();
				previous_task = null;
			}
			const elapsed = now - start;
			if (elapsed > /** @type {number} */ (duration)) {
				store.set((value = new_value));
				return false;
			}
			// @ts-ignore
			store.set((value = fn(easing(elapsed / duration))));
			return true;
		});
		return task.promise;
	}
	return {
		set,
		update: (fn, opts) =>
			set(fn(/** @type {any} */ (target_value), /** @type {any} */ (value)), opts),
		subscribe: store.subscribe
	};
}

/* empty css                                          */var It={value:()=>{}};function H(t){this._=t;}function Bt(t,e){return t.trim().split(/^|\s+/).map(function(n){var i="",s=n.indexOf(".");if(s>=0&&(i=n.slice(s+1),n=n.slice(0,s)),n&&!e.hasOwnProperty(n))throw new Error("unknown type: "+n);return {type:n,name:i}})}H.prototype={constructor:H,on:function(t,e){var n=this._,i=Bt(t+"",n),s,o=-1,a=i.length;if(arguments.length<2){for(;++o<a;)if((s=(t=i[o]).type)&&(s=Nt(n[s],t.name)))return s;return}if(e!=null&&typeof e!="function")throw new Error("invalid callback: "+e);for(;++o<a;)if(s=(t=i[o]).type)n[s]=rt(n[s],t.name,e);else if(e==null)for(s in n)n[s]=rt(n[s],t.name,null);return this},copy:function(){var t={},e=this._;for(var n in e)t[n]=e[n].slice();return new H(t)},call:function(t,e){if((s=arguments.length-2)>0)for(var n=new Array(s),i=0,s,o;i<s;++i)n[i]=arguments[i+2];if(!this._.hasOwnProperty(t))throw new Error("unknown type: "+t);for(o=this._[t],i=0,s=o.length;i<s;++i)o[i].value.apply(e,n);},apply:function(t,e,n){if(!this._.hasOwnProperty(t))throw new Error("unknown type: "+t);for(var i=this._[t],s=0,o=i.length;s<o;++s)i[s].value.apply(e,n);}};function Nt(t,e){for(var n=0,i=t.length,s;n<i;++n)if((s=t[n]).name===e)return s.value}function rt(t,e,n){for(var i=0,s=t.length;i<s;++i)if(t[i].name===e){t[i]=It,t=t.slice(0,i).concat(t.slice(i+1));break}return n!=null&&t.push({name:e,value:n}),t}var tt="http://www.w3.org/1999/xhtml";const ut={svg:"http://www.w3.org/2000/svg",xhtml:tt,xlink:"http://www.w3.org/1999/xlink",xml:"http://www.w3.org/XML/1998/namespace",xmlns:"http://www.w3.org/2000/xmlns/"};function mt(t){var e=t+="",n=e.indexOf(":");return n>=0&&(e=t.slice(0,n))!=="xmlns"&&(t=t.slice(n+1)),ut.hasOwnProperty(e)?{space:ut[e],local:t}:t}function Pt(t){return function(){var e=this.ownerDocument,n=this.namespaceURI;return n===tt&&e.documentElement.namespaceURI===tt?e.createElement(t):e.createElementNS(n,t)}}function Ut(t){return function(){return this.ownerDocument.createElementNS(t.space,t.local)}}function vt(t){var e=mt(t);return (e.local?Ut:Pt)(e)}function Ft(){}function wt(t){return t==null?Ft:function(){return this.querySelector(t)}}function Ot(t){typeof t!="function"&&(t=wt(t));for(var e=this._groups,n=e.length,i=new Array(n),s=0;s<n;++s)for(var o=e[s],a=o.length,r=i[s]=new Array(a),l,h,f=0;f<a;++f)(l=o[f])&&(h=t.call(l,l.__data__,f,o))&&("__data__"in l&&(h.__data__=l.__data__),r[f]=h);return new C(i,this._parents)}function Vt(t){return t==null?[]:Array.isArray(t)?t:Array.from(t)}function Wt(){return []}function qt(t){return t==null?Wt:function(){return this.querySelectorAll(t)}}function Ht(t){return function(){return Vt(t.apply(this,arguments))}}function Gt(t){typeof t=="function"?t=Ht(t):t=qt(t);for(var e=this._groups,n=e.length,i=[],s=[],o=0;o<n;++o)for(var a=e[o],r=a.length,l,h=0;h<r;++h)(l=a[h])&&(i.push(t.call(l,l.__data__,h,a)),s.push(l));return new C(i,s)}function Kt(t){return function(){return this.matches(t)}}function bt(t){return function(e){return e.matches(t)}}var Jt=Array.prototype.find;function Zt(t){return function(){return Jt.call(this.children,t)}}function Qt(){return this.firstElementChild}function jt(t){return this.select(t==null?Qt:Zt(typeof t=="function"?t:bt(t)))}var $t=Array.prototype.filter;function te(){return Array.from(this.children)}function ee(t){return function(){return $t.call(this.children,t)}}function ne(t){return this.selectAll(t==null?te:ee(typeof t=="function"?t:bt(t)))}function ie(t){typeof t!="function"&&(t=Kt(t));for(var e=this._groups,n=e.length,i=new Array(n),s=0;s<n;++s)for(var o=e[s],a=o.length,r=i[s]=[],l,h=0;h<a;++h)(l=o[h])&&t.call(l,l.__data__,h,o)&&r.push(l);return new C(i,this._parents)}function yt(t){return new Array(t.length)}function se(){return new C(this._enter||this._groups.map(yt),this._parents)}function K(t,e){this.ownerDocument=t.ownerDocument,this.namespaceURI=t.namespaceURI,this._next=null,this._parent=t,this.__data__=e;}K.prototype={constructor:K,appendChild:function(t){return this._parent.insertBefore(t,this._next)},insertBefore:function(t,e){return this._parent.insertBefore(t,e)},querySelector:function(t){return this._parent.querySelector(t)},querySelectorAll:function(t){return this._parent.querySelectorAll(t)}};function le(t){return function(){return t}}function oe(t,e,n,i,s,o){for(var a=0,r,l=e.length,h=o.length;a<h;++a)(r=e[a])?(r.__data__=o[a],i[a]=r):n[a]=new K(t,o[a]);for(;a<l;++a)(r=e[a])&&(s[a]=r);}function ae(t,e,n,i,s,o,a){var r,l,h=new Map,f=e.length,m=o.length,d=new Array(f),b;for(r=0;r<f;++r)(l=e[r])&&(d[r]=b=a.call(l,l.__data__,r,e)+"",h.has(b)?s[r]=l:h.set(b,l));for(r=0;r<m;++r)b=a.call(t,o[r],r,o)+"",(l=h.get(b))?(i[r]=l,l.__data__=o[r],h.delete(b)):n[r]=new K(t,o[r]);for(r=0;r<f;++r)(l=e[r])&&h.get(d[r])===l&&(s[r]=l);}function re(t){return t.__data__}function ue(t,e){if(!arguments.length)return Array.from(this,re);var n=e?ae:oe,i=this._parents,s=this._groups;typeof t!="function"&&(t=le(t));for(var o=s.length,a=new Array(o),r=new Array(o),l=new Array(o),h=0;h<o;++h){var f=i[h],m=s[h],d=m.length,b=ce(t.call(f,f&&f.__data__,h,i)),E=b.length,z=r[h]=new Array(E),g=a[h]=new Array(E),p=l[h]=new Array(d);n(f,m,z,g,p,b,e);for(var X=0,T=0,c,_;X<E;++X)if(c=z[X]){for(X>=T&&(T=X+1);!(_=g[T])&&++T<E;);c._next=_||null;}}return a=new C(a,i),a._enter=r,a._exit=l,a}function ce(t){return typeof t=="object"&&"length"in t?t:Array.from(t)}function he(){return new C(this._exit||this._groups.map(yt),this._parents)}function fe(t,e,n){var i=this.enter(),s=this,o=this.exit();return typeof t=="function"?(i=t(i),i&&(i=i.selection())):i=i.append(t+""),e!=null&&(s=e(s),s&&(s=s.selection())),n==null?o.remove():n(o),i&&s?i.merge(s).order():s}function de(t){for(var e=t.selection?t.selection():t,n=this._groups,i=e._groups,s=n.length,o=i.length,a=Math.min(s,o),r=new Array(s),l=0;l<a;++l)for(var h=n[l],f=i[l],m=h.length,d=r[l]=new Array(m),b,E=0;E<m;++E)(b=h[E]||f[E])&&(d[E]=b);for(;l<s;++l)r[l]=n[l];return new C(r,this._parents)}function _e(){for(var t=this._groups,e=-1,n=t.length;++e<n;)for(var i=t[e],s=i.length-1,o=i[s],a;--s>=0;)(a=i[s])&&(o&&a.compareDocumentPosition(o)^4&&o.parentNode.insertBefore(a,o),o=a);return this}function ge(t){t||(t=pe);function e(m,d){return m&&d?t(m.__data__,d.__data__):!m-!d}for(var n=this._groups,i=n.length,s=new Array(i),o=0;o<i;++o){for(var a=n[o],r=a.length,l=s[o]=new Array(r),h,f=0;f<r;++f)(h=a[f])&&(l[f]=h);l.sort(e);}return new C(s,this._parents).order()}function pe(t,e){return t<e?-1:t>e?1:t>=e?0:NaN}function me(){var t=arguments[0];return arguments[0]=this,t.apply(null,arguments),this}function ve(){return Array.from(this)}function we(){for(var t=this._groups,e=0,n=t.length;e<n;++e)for(var i=t[e],s=0,o=i.length;s<o;++s){var a=i[s];if(a)return a}return null}function be(){let t=0;for(const e of this)++t;return t}function ye(){return !this.node()}function xe(t){for(var e=this._groups,n=0,i=e.length;n<i;++n)for(var s=e[n],o=0,a=s.length,r;o<a;++o)(r=s[o])&&t.call(r,r.__data__,o,s);return this}function ze(t){return function(){this.removeAttribute(t);}}function ke(t){return function(){this.removeAttributeNS(t.space,t.local);}}function Ee(t,e){return function(){this.setAttribute(t,e);}}function Xe(t,e){return function(){this.setAttributeNS(t.space,t.local,e);}}function Ye(t,e){return function(){var n=e.apply(this,arguments);n==null?this.removeAttribute(t):this.setAttribute(t,n);}}function Ae(t,e){return function(){var n=e.apply(this,arguments);n==null?this.removeAttributeNS(t.space,t.local):this.setAttributeNS(t.space,t.local,n);}}function Me(t,e){var n=mt(t);if(arguments.length<2){var i=this.node();return n.local?i.getAttributeNS(n.space,n.local):i.getAttribute(n)}return this.each((e==null?n.local?ke:ze:typeof e=="function"?n.local?Ae:Ye:n.local?Xe:Ee)(n,e))}function xt(t){return t.ownerDocument&&t.ownerDocument.defaultView||t.document&&t||t.defaultView}function Se(t){return function(){this.style.removeProperty(t);}}function Te(t,e,n){return function(){this.style.setProperty(t,e,n);}}function Ce(t,e,n){return function(){var i=e.apply(this,arguments);i==null?this.style.removeProperty(t):this.style.setProperty(t,i,n);}}function Re(t,e,n){return arguments.length>1?this.each((e==null?Se:typeof e=="function"?Ce:Te)(t,e,n??"")):De(this.node(),t)}function De(t,e){return t.style.getPropertyValue(e)||xt(t).getComputedStyle(t,null).getPropertyValue(e)}function Le(t){return function(){delete this[t];}}function Ie(t,e){return function(){this[t]=e;}}function Be(t,e){return function(){var n=e.apply(this,arguments);n==null?delete this[t]:this[t]=n;}}function Ne(t,e){return arguments.length>1?this.each((e==null?Le:typeof e=="function"?Be:Ie)(t,e)):this.node()[t]}function zt(t){return t.trim().split(/^|\s+/)}function st(t){return t.classList||new kt(t)}function kt(t){this._node=t,this._names=zt(t.getAttribute("class")||"");}kt.prototype={add:function(t){var e=this._names.indexOf(t);e<0&&(this._names.push(t),this._node.setAttribute("class",this._names.join(" ")));},remove:function(t){var e=this._names.indexOf(t);e>=0&&(this._names.splice(e,1),this._node.setAttribute("class",this._names.join(" ")));},contains:function(t){return this._names.indexOf(t)>=0}};function Et(t,e){for(var n=st(t),i=-1,s=e.length;++i<s;)n.add(e[i]);}function Xt(t,e){for(var n=st(t),i=-1,s=e.length;++i<s;)n.remove(e[i]);}function Pe(t){return function(){Et(this,t);}}function Ue(t){return function(){Xt(this,t);}}function Fe(t,e){return function(){(e.apply(this,arguments)?Et:Xt)(this,t);}}function Oe(t,e){var n=zt(t+"");if(arguments.length<2){for(var i=st(this.node()),s=-1,o=n.length;++s<o;)if(!i.contains(n[s]))return  false;return  true}return this.each((typeof e=="function"?Fe:e?Pe:Ue)(n,e))}function Ve(){this.textContent="";}function We(t){return function(){this.textContent=t;}}function qe(t){return function(){var e=t.apply(this,arguments);this.textContent=e??"";}}function He(t){return arguments.length?this.each(t==null?Ve:(typeof t=="function"?qe:We)(t)):this.node().textContent}function Ge(){this.innerHTML="";}function Ke(t){return function(){this.innerHTML=t;}}function Je(t){return function(){var e=t.apply(this,arguments);this.innerHTML=e??"";}}function Ze(t){return arguments.length?this.each(t==null?Ge:(typeof t=="function"?Je:Ke)(t)):this.node().innerHTML}function Qe(){this.nextSibling&&this.parentNode.appendChild(this);}function je(){return this.each(Qe)}function $e(){this.previousSibling&&this.parentNode.insertBefore(this,this.parentNode.firstChild);}function tn(){return this.each($e)}function en(t){var e=typeof t=="function"?t:vt(t);return this.select(function(){return this.appendChild(e.apply(this,arguments))})}function nn(){return null}function sn(t,e){var n=typeof t=="function"?t:vt(t),i=e==null?nn:typeof e=="function"?e:wt(e);return this.select(function(){return this.insertBefore(n.apply(this,arguments),i.apply(this,arguments)||null)})}function ln(){var t=this.parentNode;t&&t.removeChild(this);}function on(){return this.each(ln)}function an(){var t=this.cloneNode(false),e=this.parentNode;return e?e.insertBefore(t,this.nextSibling):t}function rn(){var t=this.cloneNode(true),e=this.parentNode;return e?e.insertBefore(t,this.nextSibling):t}function un(t){return this.select(t?rn:an)}function cn(t){return arguments.length?this.property("__data__",t):this.node().__data__}function hn(t){return function(e){t.call(this,e,this.__data__);}}function fn(t){return t.trim().split(/^|\s+/).map(function(e){var n="",i=e.indexOf(".");return i>=0&&(n=e.slice(i+1),e=e.slice(0,i)),{type:e,name:n}})}function dn(t){return function(){var e=this.__on;if(e){for(var n=0,i=-1,s=e.length,o;n<s;++n)o=e[n],(!t.type||o.type===t.type)&&o.name===t.name?this.removeEventListener(o.type,o.listener,o.options):e[++i]=o;++i?e.length=i:delete this.__on;}}}function _n(t,e,n){return function(){var i=this.__on,s,o=hn(e);if(i){for(var a=0,r=i.length;a<r;++a)if((s=i[a]).type===t.type&&s.name===t.name){this.removeEventListener(s.type,s.listener,s.options),this.addEventListener(s.type,s.listener=o,s.options=n),s.value=e;return}}this.addEventListener(t.type,o,n),s={type:t.type,name:t.name,value:e,listener:o,options:n},i?i.push(s):this.__on=[s];}}function gn(t,e,n){var i=fn(t+""),s,o=i.length,a;if(arguments.length<2){var r=this.node().__on;if(r){for(var l=0,h=r.length,f;l<h;++l)for(s=0,f=r[l];s<o;++s)if((a=i[s]).type===f.type&&a.name===f.name)return f.value}return}for(r=e?_n:dn,s=0;s<o;++s)this.each(r(i[s],e,n));return this}function Yt(t,e,n){var i=xt(t),s=i.CustomEvent;typeof s=="function"?s=new s(e,n):(s=i.document.createEvent("Event"),n?(s.initEvent(e,n.bubbles,n.cancelable),s.detail=n.detail):s.initEvent(e,false,false)),t.dispatchEvent(s);}function pn(t,e){return function(){return Yt(this,t,e)}}function mn(t,e){return function(){return Yt(this,t,e.apply(this,arguments))}}function vn(t,e){return this.each((typeof e=="function"?mn:pn)(t,e))}function*wn(){for(var t=this._groups,e=0,n=t.length;e<n;++e)for(var i=t[e],s=0,o=i.length,a;s<o;++s)(a=i[s])&&(yield a);}function C(t,e){this._groups=t,this._parents=e;}function yn(){return this}C.prototype={constructor:C,select:Ot,selectAll:Gt,selectChild:jt,selectChildren:ne,filter:ie,data:ue,enter:se,exit:he,join:fe,merge:de,selection:yn,order:_e,sort:ge,call:me,nodes:ve,node:we,size:be,empty:ye,each:xe,attr:Me,style:Re,property:Ne,classed:Oe,text:He,html:Ze,raise:je,lower:tn,append:en,insert:sn,remove:on,clone:un,datum:cn,on:gn,dispatch:vn,[Symbol.iterator]:wn};function At(t,e){t.component(n=>{function i(_,Y,k){return Math.min(Math.max(_,Y),k)}let s=fallback(e.position,.5),o=fallback(e.disabled,false),a=fallback(e.slider_color,"var(--border-color-primary)"),r=fallback(e.image_size,()=>({top:0,left:0,width:0,height:0}),true),l=fallback(e.el,void 0),h=fallback(e.parent_el,void 0),m=0,d=false,b=0;function E(_){b=h?.getBoundingClientRect().width||0,_===0&&(r.width=l?.getBoundingClientRect().width||0),m=i(r.width*s+r.left,0,b);}function c(_){m=i(r.width*_+r.left,0,b);}E(r.width),c(s),n.push('<div class="wrap svelte-b2bl92" role="none"><div class="content svelte-b2bl92"><!--[-->'),slot(n,e,"default",{}),n.push(`<!--]--></div> <div${attr_class("outer svelte-b2bl92",void 0,{disabled:o,grab:d})} data-testid="slider" role="none"${attr_style(`transform: translateX(${stringify(m)}px)`)}><span${attr_class("icon-wrap svelte-b2bl92",void 0,{active:d,disabled:o})}><span class="icon left svelte-b2bl92">◢</span><span class="icon center svelte-b2bl92"${attr_style("",{"--color":a})}></span><span class="icon right svelte-b2bl92">◢</span></span> <div class="inner svelte-b2bl92"${attr_style("",{"--color":a})}></div></div></div>`),bind_props(e,{position:s,disabled:o,slider_color:a,image_size:r,el:l,parent_el:h});});}function J(t,e){const n=sanitize_props(e),i=rest_props(n,["src","fullscreen","fixed","transform","img_el","hidden","variant","max_height"]);t.component(s=>{let o=fallback(e.src,void 0),a=fallback(e.fullscreen,false),r=fallback(e.fixed,false),l=fallback(e.transform,"translate(0px, 0px) scale(1)"),h=fallback(e.img_el,null),f=fallback(e.hidden,false),m=fallback(e.variant,"upload"),d=fallback(e.max_height,500);s.push(`<img${attributes({src:o,"data-testid":"imageslider-image",...i},"svelte-j3ek2n",{fixed:r,hidden:f,preview:m==="preview",slider:m==="upload",fullscreen:a,small:!a},{transform:l,"max-height":d&&!a?`${d}px`:null})} onload="this.__e=event" onerror="this.__e=event"/>`),bind_props(e,{src:o,fullscreen:a,fixed:r,transform:l,img_el:h,hidden:f,variant:m,max_height:d});});}class Tn{container;image;scale;offsetX;offsetY;isDragging;lastX;lastY;initial_left_padding;initial_top_padding;initial_width;initial_height;subscribers;handleImageLoad;real_image_size={top:0,left:0,width:0,height:0};last_touch_distance;constructor(e,n){this.container=e,this.image=n,this.scale=1,this.offsetX=0,this.offsetY=0,this.isDragging=false,this.lastX=0,this.lastY=0,this.initial_left_padding=0,this.initial_top_padding=0,this.initial_width=0,this.initial_height=0,this.subscribers=[],this.last_touch_distance=0,this.handleWheel=this.handleWheel.bind(this),this.handleMouseDown=this.handleMouseDown.bind(this),this.handleMouseMove=this.handleMouseMove.bind(this),this.handleMouseUp=this.handleMouseUp.bind(this),this.handleImageLoad=this.init.bind(this),this.handleTouchStart=this.handleTouchStart.bind(this),this.handleTouchMove=this.handleTouchMove.bind(this),this.handleTouchEnd=this.handleTouchEnd.bind(this),this.image.addEventListener("load",this.handleImageLoad),this.container.addEventListener("wheel",this.handleWheel),this.container.addEventListener("mousedown",this.handleMouseDown),document.addEventListener("mousemove",this.handleMouseMove),document.addEventListener("mouseup",this.handleMouseUp),this.container.addEventListener("touchstart",this.handleTouchStart),document.addEventListener("touchmove",this.handleTouchMove),document.addEventListener("touchend",this.handleTouchEnd),new ResizeObserver(s=>{for(const o of s)o.target===this.container&&(this.handleResize(),this.get_image_size(this.image));}).observe(this.container);}handleResize(){this.init();}init(){const e=this.container.getBoundingClientRect(),n=this.image.getBoundingClientRect();this.initial_left_padding=n.left-e.left,this.initial_top_padding=n.top-e.top,this.initial_width=n.width,this.initial_height=n.height,this.reset_zoom(),this.updateTransform();}reset_zoom(){this.scale=1,this.offsetX=0,this.offsetY=0,this.updateTransform();}handleMouseDown(e){const n=this.image.getBoundingClientRect();if(e.clientX>=n.left&&e.clientX<=n.right&&e.clientY>=n.top&&e.clientY<=n.bottom){if(e.preventDefault(),this.scale===1)return;this.isDragging=true,this.lastX=e.clientX,this.lastY=e.clientY,this.image.style.cursor="grabbing";}}handleMouseMove(e){if(!this.isDragging)return;const n=e.clientX-this.lastX,i=e.clientY-this.lastY;this.offsetX+=n,this.offsetY+=i,this.lastX=e.clientX,this.lastY=e.clientY,this.updateTransform(),this.updateTransform();}handleMouseUp(){this.isDragging&&(this.constrain_to_bounds(true),this.updateTransform(),this.isDragging=false,this.image.style.cursor=this.scale>1?"grab":"zoom-in");}async handleWheel(e){e.preventDefault();const n=this.container.getBoundingClientRect(),i=this.image.getBoundingClientRect();if(e.clientX<i.left||e.clientX>i.right||e.clientY<i.top||e.clientY>i.bottom)return;const s=1.05,o=this.scale,a=-Math.sign(e.deltaY)>0?Math.min(15,o*s):Math.max(1,o/s);if(a===o)return;const r=e.clientX-n.left-this.initial_left_padding,l=e.clientY-n.top-this.initial_top_padding;this.scale=a,this.offsetX=this.compute_new_offset({cursor_position:r,current_offset:this.offsetX,new_scale:a,old_scale:o}),this.offsetY=this.compute_new_offset({cursor_position:l,current_offset:this.offsetY,new_scale:a,old_scale:o}),this.updateTransform(),this.constrain_to_bounds(),this.updateTransform(),this.image.style.cursor=this.scale>1?"grab":"zoom-in";}compute_new_position({position:e,scale:n,anchor_position:i}){return e-(e-i)*(n/this.scale)}compute_new_offset({cursor_position:e,current_offset:n,new_scale:i,old_scale:s}){return e-i/s*(e-n)}constrain_to_bounds(e=false){if(this.scale===1){this.offsetX=0,this.offsetY=0;return}const n={top:this.real_image_size.top*this.scale+this.offsetY,left:this.real_image_size.left*this.scale+this.offsetX,width:this.real_image_size.width*this.scale,height:this.real_image_size.height*this.scale,bottom:this.real_image_size.top*this.scale+this.offsetY+this.real_image_size.height*this.scale,right:this.real_image_size.left*this.scale+this.offsetX+this.real_image_size.width*this.scale},i=this.real_image_size.left+this.real_image_size.width,s=this.real_image_size.top+this.real_image_size.height;e&&(n.top>this.real_image_size.top?this.offsetY=this.calculate_position(this.real_image_size.top,0,"y"):n.bottom<s&&(this.offsetY=this.calculate_position(s,1,"y")),n.left>this.real_image_size.left?this.offsetX=this.calculate_position(this.real_image_size.left,0,"x"):n.right<i&&(this.offsetX=this.calculate_position(i,1,"x")));}updateTransform(){this.notify({x:this.offsetX,y:this.offsetY,scale:this.scale});}destroy(){this.container.removeEventListener("wheel",this.handleWheel),this.container.removeEventListener("mousedown",this.handleMouseDown),document.removeEventListener("mousemove",this.handleMouseMove),document.removeEventListener("mouseup",this.handleMouseUp),this.container.removeEventListener("touchstart",this.handleTouchStart),document.removeEventListener("touchmove",this.handleTouchMove),document.removeEventListener("touchend",this.handleTouchEnd),this.image.removeEventListener("load",this.handleImageLoad);}subscribe(e){this.subscribers.push(e);}unsubscribe(e){this.subscribers=this.subscribers.filter(n=>n!==e);}notify({x:e,y:n,scale:i}){this.subscribers.forEach(s=>s({x:e,y:n,scale:i}));}handleTouchStart(e){e.preventDefault();const n=this.image.getBoundingClientRect(),i=e.touches[0];if(i.clientX>=n.left&&i.clientX<=n.right&&i.clientY>=n.top&&i.clientY<=n.bottom){if(e.touches.length===1&&this.scale>1)this.isDragging=true,this.lastX=i.clientX,this.lastY=i.clientY;else if(e.touches.length===2){const s=e.touches[0],o=e.touches[1];this.last_touch_distance=Math.hypot(o.clientX-s.clientX,o.clientY-s.clientY);}}}get_image_size(e){if(!e)return;const n=e.parentElement?.getBoundingClientRect();if(!n)return;const i=e.naturalWidth/e.naturalHeight,s=n.width/n.height;let o,a;i>s?(o=n.width,a=n.width/i):(a=n.height,o=n.height*i);const r=(n.width-o)/2,l=(n.height-a)/2;this.real_image_size={top:l,left:r,width:o,height:a};}handleTouchMove(e){if(e.touches.length===1&&this.isDragging){e.preventDefault();const n=e.touches[0],i=n.clientX-this.lastX,s=n.clientY-this.lastY;this.offsetX+=i,this.offsetY+=s,this.lastX=n.clientX,this.lastY=n.clientY,this.updateTransform();}else if(e.touches.length===2){e.preventDefault();const n=e.touches[0],i=e.touches[1],s=Math.hypot(i.clientX-n.clientX,i.clientY-n.clientY);if(this.last_touch_distance===0){this.last_touch_distance=s;return}const o=s/this.last_touch_distance,a=this.scale,r=Math.min(15,Math.max(1,a*o));if(r===a){this.last_touch_distance=s;return}const l=this.container.getBoundingClientRect(),h=(n.clientX+i.clientX)/2-l.left-this.initial_left_padding,f=(n.clientY+i.clientY)/2-l.top-this.initial_top_padding;this.scale=r,this.offsetX=this.compute_new_offset({cursor_position:h,current_offset:this.offsetX,new_scale:r,old_scale:a}),this.offsetY=this.compute_new_offset({cursor_position:f,current_offset:this.offsetY,new_scale:r,old_scale:a}),this.updateTransform(),this.constrain_to_bounds(),this.updateTransform(),this.last_touch_distance=s,this.image.style.cursor=this.scale>1?"grab":"zoom-in";}}handleTouchEnd(e){this.isDragging&&(this.constrain_to_bounds(true),this.updateTransform(),this.isDragging=false),e.touches.length===0&&(this.last_touch_distance=0);}calculate_position(e,n,i){if(this.container.getBoundingClientRect(),i==="x"){const s=e,o=this.real_image_size.left+n*this.real_image_size.width;return s-o*this.scale}if(i==="y"){const s=e,o=this.real_image_size.top+n*this.real_image_size.height;return s-o*this.scale}return 0}}function Cn(t,e){t.component(n=>{var i$1;let s,o$1,a=fallback(e.value,()=>[null,null],true),r$1=fallback(e.label,void 0),l$1=fallback(e.show_download_button,true),h=e.show_label,f=e.i18n,m=e.position,d=fallback(e.layer_images,true),b=fallback(e.show_single,false),E=e.slider_color,z=fallback(e.show_fullscreen_button,true),g=fallback(e.fullscreen,false),p$1=fallback(e.buttons,null),X=fallback(e.on_custom_button_click,null),T=fallback(e.el_width,0),c=e.max_height,_=fallback(e.interactive,true);let k$2,A,M=tweened({x:0,y:0,z:1},{duration:75}),R;function x(S,y,D,B,j,Mt){return (S*D+B-j)/Mt/y}let v=0,w$1=null,L=null;function Q(S,y){!S||!y||(w$1?.destroy(),L?.disconnect(),S?.getBoundingClientRect().width,v=y?.getBoundingClientRect().width||0,w$1=new Tn(y,S),w$1.subscribe(({x:D,y:B,scale:j})=>{M.set({x:D,y:B,z:j});}),L=new ResizeObserver(D=>{for(const B of D)B.target===y&&(v=B.contentRect.width),B.target===S&&B.contentRect.width;}),L.observe(y),L.observe(S));}let N={top:0,left:0,width:0,height:0};s=x(m,v,N.width,N.left,store_get(i$1??={},"$transform",M).x,store_get(i$1??={},"$transform",M).z),o$1=d?`clip-path: inset(0 0 0 ${s*100}%)`:"",Q(k$2,A);let I=true,U;function W(S){k(S,{show_label:h,Icon:i,label:r$1||f("image.image")}),S.push("<!----> "),(a===null||a[0]===null||a[1]===null)&&!b?(S.push("<!--[-->"),p(S,{unpadded_box:true,size:"large",children:y=>{i(y);},$$slots:{default:true}})):(S.push("<!--[!-->"),S.push('<div class="image-container svelte-1880bc6">'),y(S,{buttons:p$1,on_custom_button_click:X,children:y=>{w(y,{Icon:r,label:f("common.undo"),disabled:store_get(i$1??={},"$transform",M).z===1,onclick:()=>w$1?.reset_zoom()}),y.push("<!----> "),z?(y.push("<!--[-->"),k$1(y,{fullscreen:g})):y.push("<!--[!-->"),y.push("<!--]--> "),l$1?(y.push("<!--[-->"),u(y,{href:a[1]?.url,download:a[1]?.orig_name||"image",children:D=>{w(D,{Icon:l,label:f("common.download")});},$$slots:{default:true}})):y.push("<!--[!-->"),y.push("<!--]--> "),_?(y.push("<!--[-->"),w(y,{Icon:o,label:"Remove Image",onclick:D=>{a=[null,null],D.stopPropagation();}})):y.push("<!--[!-->"),y.push("<!--]-->");}}),S.push(`<!----> <div${attr_class("slider-wrap svelte-1880bc6",void 0,{limit_height:!g})}>`),At(S,{slider_color:E,image_size:N,get position(){return m},set position(y){m=y,I=false;},get el(){return A},set el(y){A=y,I=false;},get parent_el(){return R},set parent_el(y){R=y,I=false;},children:y=>{J(y,{src:a?.[0]?.url,alt:"",loading:"lazy",variant:"preview",transform:`translate(${stringify(store_get(i$1??={},"$transform",M).x)}px, ${stringify(store_get(i$1??={},"$transform",M).y)}px) scale(${stringify(store_get(i$1??={},"$transform",M).z)})`,fullscreen:g,max_height:c,get img_el(){return k$2},set img_el(D){k$2=D,I=false;}}),y.push("<!----> "),J(y,{variant:"preview",fixed:d,hidden:!a?.[1]?.url,src:a?.[1]?.url,alt:"",loading:"lazy",style:`${stringify(o$1)}; background: var(--block-background-fill);`,transform:`translate(${stringify(store_get(i$1??={},"$transform",M).x)}px, ${stringify(store_get(i$1??={},"$transform",M).y)}px) scale(${stringify(store_get(i$1??={},"$transform",M).z)})`,fullscreen:g,max_height:c}),y.push("<!---->");},$$slots:{default:true}}),S.push("<!----></div></div>")),S.push("<!--]-->");}do I=true,U=n.copy(),W(U);while(!I);n.subsume(U),i$1&&unsubscribe_stores(i$1),bind_props(e,{value:a,label:r$1,show_download_button:l$1,show_label:h,i18n:f,position:m,layer_images:d,show_single:b,slider_color:E,show_fullscreen_button:z,fullscreen:g,buttons:p$1,on_custom_button_click:X,el_width:T,max_height:c,interactive:_});});}function Rn(t,e){t.component(n=>{n.push('<div class="svelte-2ufkjh">'),w(n,{Icon:o,label:"Remove Image",onclick:s=>{s.stopPropagation();}}),n.push("<!----></div>");});}function Dn(t,e){t.component(n=>{let i$1=e.value,s=fallback(e.label,void 0),o=e.show_label,a=e.root,r=e.position,l$1=fallback(e.upload_count,2),h=fallback(e.show_download_button,true),f=e.slider_color,m=e.upload,d=e.stream_handler,b=fallback(e.max_file_size,null),E=e.i18n,z=e.max_height,g=fallback(e.upload_promise,null),p$1=i$1||[null,null],X,T;async function c(x,v){const w=[i$1[0],i$1[1]];x.length>1?w[v]=x[0]:w[v]=x[v],i$1=w,await tick();}let _="";let k$1=fallback(e.dragging,false);JSON.stringify(i$1)!==_&&(_=JSON.stringify(i$1),p$1=i$1);let A=true,M;function R(x){k(x,{show_label:o,Icon:i,label:s||E("image.image")}),x.push('<!----> <div data-testid="image" class="image-container svelte-1c8zs50">'),i$1?.[0]?.url||i$1?.[1]?.url?(x.push("<!--[-->"),Rn(x)):x.push("<!--[!-->"),x.push("<!--]--> "),i$1?.[1]?.url?(x.push("<!--[-->"),x.push('<div class="icon-buttons svelte-1c8zs50">'),h?(x.push("<!--[-->"),u(x,{href:i$1[1].url,download:i$1[1].orig_name||"image",children:v=>{w(v,{Icon:l});},$$slots:{default:true}})):x.push("<!--[!-->"),x.push("<!--]--></div>")):x.push("<!--[!-->"),x.push("<!--]--> "),At(x,{disabled:l$1==2||!i$1?.[0],slider_color:f,get position(){return r},set position(v){r=v,A=false;},children:v=>{v.push(`<div${attr_class("upload-wrap svelte-1c8zs50",void 0,{"side-by-side":l$1===2})}${attr_style("",{display:l$1===2?"flex":"block"})}>`),p$1?.[0]?(v.push("<!--[!-->"),J(v,{variant:"upload",src:p$1[0]?.url,alt:"",max_height:z,get img_el(){return X},set img_el(w){X=w,A=false;}})):(v.push("<!--[-->"),v.push(`<div${attr_class("wrap svelte-1c8zs50",void 0,{"half-wrap":l$1===1})}>`),ee$1(v,{filetype:"image/*",onload:w=>c(w,0),disable_click:!!i$1?.[0],root:a,file_count:"multiple",upload:m,stream_handler:d,max_file_size:b,get upload_promise(){return g},set upload_promise(w){g=w,A=false;},get dragging(){return k$1},set dragging(w){k$1=w,A=false;},children:w=>{w.push("<!--[-->"),slot(w,e,"default",{}),w.push("<!--]-->");},$$slots:{default:true}}),v.push("<!----></div>")),v.push("<!--]--> "),!p$1?.[1]&&l$1===2?(v.push("<!--[-->"),ee$1(v,{filetype:"image/*",onload:w=>c(w,1),disable_click:!!i$1?.[1],root:a,file_count:"multiple",upload:m,stream_handler:d,max_file_size:b,get upload_promise(){return g},set upload_promise(w){g=w,A=false;},get dragging(){return k$1},set dragging(w){k$1=w,A=false;},children:w=>{w.push("<!--[-->"),slot(w,e,"default",{}),w.push("<!--]-->");},$$slots:{default:true}})):(v.push("<!--[!-->"),!p$1?.[1]&&l$1===1?(v.push("<!--[-->"),v.push(`<div${attr_class("empty-wrap fixed svelte-1c8zs50",void 0,{"white-icon":!i$1?.[0]?.url})}${attr_style("",{width:`${stringify(T*(1-r))}px`,transform:`translateX(${stringify(T*r)}px)`})}>`),p(v,{unpadded_box:true,size:"large",children:w=>{i(w);},$$slots:{default:true}}),v.push("<!----></div>")):(v.push("<!--[!-->"),p$1?.[1]?(v.push("<!--[-->"),J(v,{variant:"upload",src:p$1[1].url,alt:"",fixed:l$1===1,transform:"translate(0px, 0px) scale(1)",max_height:z})):v.push("<!--[!-->"),v.push("<!--]-->")),v.push("<!--]-->")),v.push("<!--]--></div>");},$$slots:{default:true}}),x.push("<!----></div>");}do A=true,M=n.copy(),R(M);while(!A);n.subsume(M),bind_props(e,{value:i$1,label:s,show_label:o,root:a,position:r,upload_count:l$1,show_download_button:h,slider_color:f,upload:m,stream_handler:d,max_file_size:b,i18n:E,max_height:z,upload_promise:g,dragging:k$1});});}function Ln(t,e){let n=fallback(e.value,()=>[null,null],true),i=e.upload,s=e.stream_handler,o=e.label,a=e.show_label,r=e.i18n,l=e.root,h=fallback(e.upload_count,1),f=e.dragging,m=e.max_height,d=fallback(e.max_file_size,null),b=fallback(e.upload_promise,null),E=true,z;function g(p){Dn(p,{slider_color:"var(--border-color-primary)",position:.5,root:l,label:o,show_label:a,upload_count:h,stream_handler:s,upload:i,max_file_size:d,max_height:m,i18n:r,get upload_promise(){return b},set upload_promise(X){b=X,E=false;},get value(){return n},set value(X){n=X,E=false;},get dragging(){return f},set dragging(X){f=X,E=false;},children:X=>{X.push("<!--[-->"),slot(X,e,"default",{}),X.push("<!--]-->");},$$slots:{default:true}});}do E=true,z=t.copy(),g(z);while(!E);t.subsume(z),bind_props(e,{value:n,upload:i,stream_handler:s,label:o,show_label:a,i18n:r,root:l,upload_count:h,dragging:f,max_height:m,max_file_size:d,upload_promise:b});}function ui(t,e){t.component(n=>{let i;class s extends ${async get_data(){return i&&(await i,await tick()),await super.get_data()}}const{$$slots:o,$$events:a,...r}=e,l=new s(r);let h=false,f=false,m=Math.max(0,Math.min(100,l.props.slider_position))/100;l.watch_for_change();let d=true,b;function E(z){!l.shared.interactive||l.props.value?.[1]&&l.props.value?.[0]?(z.push("<!--[-->"),G(z,{visible:l.shared.visible,variant:"solid",border_mode:f?"focus":"base",padding:false,elem_id:l.shared.elem_id,elem_classes:l.shared.elem_classes,height:l.props.height||void 0,width:l.props.width,allow_overflow:false,container:l.shared.container,scale:l.shared.scale,min_width:l.shared.min_width,get fullscreen(){return h},set fullscreen(g){h=g,d=false;},children:g=>{$$1(g,spread_props([{autoscroll:l.shared.autoscroll,i18n:l.i18n},l.shared.loading_status])),g.push("<!----> "),Cn(g,{fullscreen:h,interactive:l.shared.interactive,label:l.shared.label,show_label:l.shared.show_label,show_download_button:l.props.buttons.some(p=>typeof p=="string"&&p==="download"),i18n:l.i18n,show_fullscreen_button:l.props.buttons.some(p=>typeof p=="string"&&p==="fullscreen"),buttons:l.props.buttons,on_custom_button_click:p=>{l.dispatch("custom_button_click",{id:p});},position:m,slider_color:l.props.slider_color,max_height:l.props.max_height,get value(){return l.props.value},set value(p){l.props.value=p,d=false;}}),g.push("<!---->");},$$slots:{default:true}})):(z.push("<!--[!-->"),G(z,{visible:l.shared.visible,variant:l.props.value===null?"dashed":"solid",border_mode:f?"focus":"base",padding:false,elem_id:l.shared.elem_id,elem_classes:l.shared.elem_classes,height:l.props.height||void 0,width:l.props.width,allow_overflow:false,container:l.shared.container,scale:l.shared.scale,min_width:l.shared.min_width,children:g=>{$$1(g,spread_props([{autoscroll:l.shared.autoscroll,i18n:l.i18n},l.shared.loading_status,{on_clear_status:()=>l.dispatch("clear_status",l.shared.loading_status)}])),g.push("<!----> "),Ln(g,{root:l.shared.root,label:l.shared.label,show_label:l.shared.show_label,upload_count:l.props.upload_count,max_file_size:l.shared.max_file_size,i18n:l.i18n,upload:(...p)=>l.shared.client.upload(...p),stream_handler:l.shared.client?.stream,max_height:l.props.max_height,get upload_promise(){return i},set upload_promise(p){i=p,d=false;},get value(){return l.props.value},set value(p){l.props.value=p,d=false;},get dragging(){return f},set dragging(p){f=p,d=false;},children:p=>{p.push("<!--[-->"),k$2(p,{i18n:l.i18n,type:"image",placeholder:l.props.placeholder}),p.push("<!--]-->");},$$slots:{default:true}}),g.push("<!---->");},$$slots:{default:true}})),z.push("<!--]-->");}do d=true,b=n.copy(),E(b);while(!d);n.subsume(b);});}

export { ui as default };
//# sourceMappingURL=Index57-bEpTKrMs.js.map

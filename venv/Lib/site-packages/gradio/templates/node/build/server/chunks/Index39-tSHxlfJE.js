import { f as fallback } from './async-D55cHugf.js';
import { c as spread_props, f as attr_class, e as ensure_array_like, i as stringify, d as bind_props } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { G } from './Block-DZmzQwnI.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';

function v(j,i){j.component(s=>{let o=i.json,_=fallback(i.depth,1/0),c=fallback(i._cur,0),a=fallback(i._last,true),h=[],l=false,u=["",""],y=false;function f(p){return p===null?"null":typeof p}function m(p){return JSON.stringify(p)}function x(p){switch(f(p)){case "function":return "f () {...}";case "symbol":return p.toString();default:return m(p)}}if(h=f(o)==="object"?Object.keys(o):[],l=Array.isArray(o),u=l?["[","]"]:["{","}"],y=_<c,!h.length)s.push("<!--[-->"),s.push(`<span${attr_class("_jsonBkt empty svelte-zxj9ye",void 0,{isArray:l})}>${escape_html(u[0])}${escape_html(u[1])}</span>`),a?s.push("<!--[!-->"):(s.push("<!--[-->"),s.push('<span class="_jsonSep svelte-zxj9ye">,</span>')),s.push("<!--]-->");else {if(s.push("<!--[!-->"),y)s.push("<!--[-->"),s.push(`<span${attr_class("_jsonBkt svelte-zxj9ye",void 0,{isArray:l})} role="button" tabindex="0">${escape_html(u[0])}...${escape_html(u[1])}</span>`),!a&&y?(s.push("<!--[-->"),s.push('<span class="_jsonSep svelte-zxj9ye">,</span>')):s.push("<!--[!-->"),s.push("<!--]-->");else {s.push("<!--[!-->"),s.push(`<span${attr_class("_jsonBkt svelte-zxj9ye",void 0,{isArray:l})} role="button" tabindex="0">${escape_html(u[0])}</span> <ul class="_jsonList svelte-zxj9ye"><!--[-->`);const p=ensure_array_like(h);for(let n=0,b=p.length;n<b;n++){let e=p[n];s.push("<li>"),l?s.push("<!--[!-->"):(s.push("<!--[-->"),s.push(`<span class="_jsonKey svelte-zxj9ye">${escape_html(m(e))}</span><span class="_jsonSep svelte-zxj9ye">:</span>`)),s.push("<!--]--> "),f(o[e])==="object"?(s.push("<!--[-->"),v(s,{json:o[e],depth:_,_cur:c+1,_last:n===h.length-1}),s.push("<!---->")):(s.push("<!--[!-->"),s.push(`<span${attr_class(`_jsonVal ${stringify(f(o[e]))}`,"svelte-zxj9ye")}>${escape_html(x(o[e]))}</span>`),n<h.length-1?(s.push("<!--[-->"),s.push('<span class="_jsonSep svelte-zxj9ye">,</span>')):s.push("<!--[!-->"),s.push("<!--]-->")),s.push("<!--]--></li>");}s.push(`<!--]--></ul> <span${attr_class("_jsonBkt svelte-zxj9ye",void 0,{isArray:l})} role="button" tabindex="0">${escape_html(u[1])}</span>`),a?s.push("<!--[!-->"):(s.push("<!--[-->"),s.push('<span class="_jsonSep svelte-zxj9ye">,</span>')),s.push("<!--]-->");}s.push("<!--]-->");}s.push("<!--]-->"),bind_props(i,{json:o,depth:_,_cur:c,_last:a});});}function L(j,i){j.component(s=>{const{$$slots:o,$$events:_,...c}=i,a=new $(c);G(s,{visible:a.shared.visible,elem_id:a.shared.elem_id,elem_classes:a.shared.elem_classes,container:true,scale:a.shared.scale,min_width:a.shared.min_width,children:l=>{a.shared.loading_status?(l.push("<!--[-->"),$$1(l,spread_props([{autoscroll:a.shared.autoscroll,i18n:a.i18n},a.shared.loading_status,{on_clear_status:()=>a.dispatch("clear_status",a.shared.loading_status)}]))):l.push("<!--[!-->"),l.push("<!--]--> "),v(l,{json:a.props.value}),l.push("<!---->");},$$slots:{default:true}});});}

export { L as default };
//# sourceMappingURL=Index39-tSHxlfJE.js.map

import { f as fallback } from './async-D55cHugf.js';
import { f as attr_class, e as ensure_array_like, d as bind_props } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';

function q(y,a){y.component(l=>{let s=a.value,h=a.type,p=fallback(a.selected,false),i=a.index,e=Array.isArray(s),b=e&&(s.length===0||s[0].length===0);if(e){if(l.push("<!--[-->"),l.push(`<div${attr_class("svelte-wcwkqi",void 0,{table:h==="table",gallery:h==="gallery",selected:p})}>`),typeof s=="string")l.push("<!--[-->"),l.push(`${escape_html(s)}`);else {if(l.push("<!--[!-->"),b)l.push("<!--[-->"),l.push('<table class="svelte-wcwkqi"><tbody><tr class="svelte-wcwkqi"><td class="svelte-wcwkqi">Empty</td></tr></tbody></table>');else {l.push("<!--[!-->"),l.push('<table class="svelte-wcwkqi"><tbody><!--[-->');const o=ensure_array_like(s.slice(0,3));for(let c=0,f=o.length;c<f;c++){let v=o[c];l.push('<tr class="svelte-wcwkqi"><!--[-->');const w=ensure_array_like(v.slice(0,3));for(let u=0,g=w.length;u<g;u++){let k=w[u];l.push(`<td class="svelte-wcwkqi">${escape_html(k)}</td>`);}l.push("<!--]-->"),v.length>3?(l.push("<!--[-->"),l.push('<td class="svelte-wcwkqi">…</td>')):l.push("<!--[!-->"),l.push("<!--]--></tr>");}l.push("<!--]--></tbody></table> "),s.length>3?(l.push("<!--[-->"),l.push(`<div${attr_class("overlay svelte-wcwkqi",void 0,{odd:i%2!=0,even:i%2==0,button:h==="gallery"})}></div>`)):l.push("<!--[!-->"),l.push("<!--]-->");}l.push("<!--]-->");}l.push("<!--]--></div>");}else l.push("<!--[!-->");l.push("<!--]-->"),bind_props(a,{value:s,type:h,selected:p,index:i});});}

export { q as default };
//# sourceMappingURL=Example14-s-dCDI60.js.map

import { f as fallback } from './async-D55cHugf.js';
import { f as attr_class, e as ensure_array_like, a as attr, d as bind_props } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';

function m(o,i){o.component(s=>{let l=i.value,p=i.type,c=fallback(i.selected,false);if(s.push(`<div${attr_class("container svelte-xds4q5",void 0,{table:p==="table",gallery:p==="gallery",selected:c})}>`),l&&l.length>0){s.push("<!--[-->"),s.push('<div class="images-wrapper svelte-xds4q5"><!--[-->');const h=ensure_array_like(l.slice(0,3));for(let u=0,v=h.length;u<v;u++){let a=h[u];"image"in a&&a.image?(s.push("<!--[-->"),s.push(`<div class="image-container svelte-xds4q5"><img${attr("src",a.image.url)}${attr("alt",a.caption||"")} class="svelte-xds4q5"/> `),a.caption?(s.push("<!--[-->"),s.push(`<span class="caption svelte-xds4q5">${escape_html(a.caption)}</span>`)):s.push("<!--[!-->"),s.push("<!--]--></div>")):(s.push("<!--[!-->"),"video"in a&&a.video?(s.push("<!--[-->"),s.push(`<div class="image-container svelte-xds4q5"><video${attr("src",a.video.url)}${attr("controls",false,true)} muted preload="metadata" class="svelte-xds4q5"></video> `),a.caption?(s.push("<!--[-->"),s.push(`<span class="caption svelte-xds4q5">${escape_html(a.caption)}</span>`)):s.push("<!--[!-->"),s.push("<!--]--></div>")):s.push("<!--[!-->"),s.push("<!--]-->")),s.push("<!--]-->");}s.push("<!--]--> "),l.length>3?(s.push("<!--[-->"),s.push('<div class="more-indicator svelte-xds4q5">…</div>')):s.push("<!--[!-->"),s.push("<!--]--></div>");}else s.push("<!--[!-->");s.push("<!--]--></div>"),bind_props(i,{value:l,type:p,selected:c});});}

export { m as default };
//# sourceMappingURL=Example17-B0rWh-Zw.js.map

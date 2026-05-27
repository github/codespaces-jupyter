import { f as fallback } from './async-D55cHugf.js';
import { f as attr_class, d as bind_props } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';

function r(c,e){c.component(d=>{let i=e.value,t=e.type,n=fallback(e.selected,false),s=e.choices,m=i.map(a=>s.find(f=>f[1]===a)?.[0]).filter(a=>a!==void 0).join(", ");d.push(`<div${attr_class("svelte-25nhtv",void 0,{table:t==="table",gallery:t==="gallery",selected:n})}>${escape_html(m)}</div>`),bind_props(e,{value:i,type:t,selected:n,choices:s});});}

export { r as default };
//# sourceMappingURL=Example12-DCDYOPbl.js.map

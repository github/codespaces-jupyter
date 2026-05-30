import { f as fallback } from './async-D55cHugf.js';
import { f as attr_class, d as bind_props } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';

function u(n,e){n.component(f=>{let t=e.value,a=e.type,c=fallback(e.selected,false),i=e.choices,s;if(t===null)s="";else {let d=i.find(m=>m[1]===t);s=d?d[0]:"";}f.push(`<div${attr_class("svelte-g2dls0",void 0,{table:a==="table",gallery:a==="gallery",selected:c})}>${escape_html(s)}</div>`),bind_props(e,{value:t,type:a,selected:c,choices:i});});}

export { u as default };
//# sourceMappingURL=Example26-Bi4XTQCa.js.map

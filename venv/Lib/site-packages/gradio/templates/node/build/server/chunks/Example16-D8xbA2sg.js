import './async-D55cHugf.js';
import { f as attr_class, e as ensure_array_like } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';

function f(i,u){i.component(l=>{let{value:s,type:p,selected:c=false}=u;if(l.push(`<ul${attr_class("svelte-14aa7hi",void 0,{table:p==="table",gallery:p==="gallery",selected:c})}>`),s){l.push("<!--[-->"),l.push("<!--[-->");const h=ensure_array_like(Array.isArray(s)?s.slice(0,3):[s]);for(let a=0,e=h.length;a<e;a++){let o=h[a];l.push(`<li><code>./${escape_html(o)}</code></li>`);}l.push("<!--]--> "),Array.isArray(s)&&s.length>3?(l.push("<!--[-->"),l.push('<li class="extra svelte-14aa7hi">...</li>')):l.push("<!--[!-->"),l.push("<!--]-->");}else l.push("<!--[!-->");l.push("<!--]--></ul>");});}

export { f as default };
//# sourceMappingURL=Example16-D8xbA2sg.js.map

import './async-D55cHugf.js';
import { f as attr_class, e as ensure_array_like, a as attr } from './index-u8mz_F03.js';
import { c } from './Image-CuPo5pWT.js';
import './2-htxqz-Pd.js';
import { c as ch } from './Video2-BN5I0jvO.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';

function n(o,e){o.component(t=>{let{value:l={text:"",files:[]},type:a,selected:u=false}=e;t.push(`<div${attr_class("container svelte-xz0m7l",void 0,{table:a==="table",gallery:a==="gallery",selected:u,border:l})}><p>${escape_html(l.text?l.text:"")}</p> <!--[-->`);const m=ensure_array_like(l.files);for(let p=0,c$1=m.length;p<c$1;p++){let s=m[p];s.mime_type&&s.mime_type.includes("image")?(t.push("<!--[-->"),c(t,{src:s.url})):(t.push("<!--[!-->"),s.mime_type&&s.mime_type.includes("video")?(t.push("<!--[-->"),ch(t,{src:s.url,alt:"",loop:true,is_stream:false})):(t.push("<!--[!-->"),s.mime_type&&s.mime_type.includes("audio")?(t.push("<!--[-->"),t.push(`<audio${attr("src",s.url)} controls></audio>`)):(t.push("<!--[!-->"),t.push(`${escape_html(s.orig_name)}`)),t.push("<!--]-->")),t.push("<!--]-->")),t.push("<!--]-->");}t.push("<!--]--></div>");});}

export { n as default };
//# sourceMappingURL=Example23-Dd0J9MZS.js.map

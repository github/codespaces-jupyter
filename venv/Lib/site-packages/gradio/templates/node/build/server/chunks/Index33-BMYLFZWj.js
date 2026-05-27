import './async-D55cHugf.js';
import { a as attr } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { q } from './Button-CQkIjvx3.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './Image-CuPo5pWT.js';

function B(o,t){o.component(a=>{let{elem_id:d="",elem_classes:u=[],visible:n=true,variant:i="secondary",size:c="lg",value:e,icon:m,disabled:f=false,scale:_=null,min_width:v=void 0,on_click:b,children:h}=t;function w(){if(b?.(),!e?.url)return;let s;if(!e.orig_name&&e.url){const r=e.url.split("/");s=r[r.length-1],s=s.split("?")[0].split("#")[0];}else s=e.orig_name;const l=document.createElement("a");l.href=e.url,l.download=s||"file",document.body.appendChild(l),l.click(),document.body.removeChild(l);}q(a,{size:c,variant:i,elem_id:d,elem_classes:u,visible:n,onclick:w,scale:_,min_width:v,disabled:f,children:s=>{m?(s.push("<!--[-->"),s.push(`<img class="button-icon svelte-4ac0fl"${attr("src",m.url)}${attr("alt",`${e} icon`)}/>`)):s.push("<!--[!-->"),s.push("<!--]--> "),h?(s.push("<!--[-->"),h(s),s.push("<!---->")):s.push("<!--[!-->"),s.push("<!--]-->");}});});}function D(o,t){o.component(a=>{const{$$slots:d,$$events:u,...n}=t,i=new $(n);B(a,{value:i.props.value,variant:i.props.variant,elem_id:i.shared.elem_id,elem_classes:i.shared.elem_classes,size:i.props.size,scale:i.shared.scale,icon:i.props.icon,min_width:i.shared.min_width,visible:i.shared.visible,disabled:!i.shared.interactive,on_click:()=>i.dispatch("click"),children:c=>{c.push(`<!---->${escape_html(i.shared.label??"")}`);}});});}

export { B as BaseButton, D as default };
//# sourceMappingURL=Index33-BMYLFZWj.js.map

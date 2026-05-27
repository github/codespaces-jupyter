import './async-D55cHugf.js';
import { a as attr, i as stringify } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { q } from './Button-CQkIjvx3.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './Image-CuPo5pWT.js';

/* empty css                                    *//* empty css                                        */function U(n,p){n.component(a=>{let{elem_id:h="",elem_classes:m=[],visible:c=true,label:e,value:u,file_count:s,file_types:o=[],root:t,size:d="lg",icon:f=null,scale:v=null,min_width:b=void 0,variant:y="secondary",disabled:g=false,max_file_size:j=null,upload:I,onclick:z,onchange:W,onupload:q$1,onerror:A,children:_}=p,k,w=o==null?null:o.map(r=>r.startsWith(".")?r:r+"/*").join(", ");function B(){z?.(),k.click();}a.push(`<input class="hide svelte-94gmgt"${attr("accept",w)} type="file"${attr("multiple",s==="multiple"||void 0,true)}${attr("webkitdirectory",s==="directory"||void 0,true)}${attr("mozdirectory",s==="directory"||void 0)}${attr("data-testid",`${stringify(e)}-upload-button`)}/> `),q(a,{size:d,variant:y,elem_id:h,elem_classes:m,visible:c,onclick:B,scale:v,min_width:b,disabled:g,children:i=>{f?(i.push("<!--[-->"),i.push(`<img class="button-icon svelte-94gmgt"${attr("src",f.url)}${attr("alt",`${u} icon`)}/>`)):i.push("<!--[!-->"),i.push("<!--]--> "),_?(i.push("<!--[-->"),_(i),i.push("<!---->")):i.push("<!--[!-->"),i.push("<!--]-->");}}),a.push("<!---->");});}function L(n,p){n.component(a=>{const{$$slots:h,$$events:m,...c}=p,e=new $(c);let u=e.props.value;async function s(t,d){e.props.value=t,e.dispatch(d);}const o=!e.shared.interactive;U(a,{elem_id:e.shared.elem_id,elem_classes:e.shared.elem_classes,visible:e.shared.visible,file_count:e.props.file_count,file_types:e.props.file_types,size:e.props.size,scale:e.shared.scale,icon:e.props.icon,min_width:e.shared.min_width,root:e.shared.root,value:u,disabled:o,variant:e.props.variant,label:e.shared.label,max_file_size:e.shared.max_file_size,onclick:()=>e.dispatch("click"),onchange:t=>s(t,"change"),onupload:t=>s(t,"upload"),onerror:t=>{e.dispatch("error",t);},upload:(...t)=>e.shared.client.upload(...t),children:t=>{t.push(`<!---->${escape_html(e.shared.label??"")}`);}});});}

export { U as BaseUploadButton, L as default };
//# sourceMappingURL=Index38-CcR794j3.js.map

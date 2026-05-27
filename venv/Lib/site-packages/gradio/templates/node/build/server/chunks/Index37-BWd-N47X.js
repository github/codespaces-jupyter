import { f as fallback } from './async-D55cHugf.js';
import { b as store_get, a as attr, f as attr_class, g as attr_style, i as stringify, s as slot, u as unsubscribe_stores, d as bind_props } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { t as tick, c as createEventDispatcher } from './index-server-CQz6EZl_.js';
import { z as z$1 } from './Walkthrough.svelte_svelte_type_style_lang-DRIsDysA.js';
import { y } from './Index.svelte_svelte_type_style_lang-NtqplRHH.js';
import { g as getContext } from './context-CBkBucIx.js';
import './escaping-CBnpiEl5.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './index3-BSHNFmik.js';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';

function N(d,e){d.component(n=>{var r;let m,i=fallback(e.elem_id,""),l=fallback(e.elem_classes,()=>[],true),s=e.label,c=fallback(e.id,()=>({}),true),_=e.visible,f=e.interactive,u=e.order,o=e.scale,p=e.component_id;const h=createEventDispatcher(),{register_tab:v,unregister_tab:g,selected_tab:x,selected_tab_index:k}=getContext(z$1);let b;function y$1(a,B){return a=JSON.parse(a),v(a,B)}m=JSON.stringify({label:s,id:c,elem_id:i,visible:_,interactive:f,scale:o,component_id:p}),b=y$1(m,u),store_get(r??={},"$selected_tab_index",k)===b&&tick().then(()=>h("select",{value:s,index:b})),n.push(`<div${attr("id",i)}${attr_class(`tabitem ${stringify(l.join(" "))}`,"svelte-dmtrd3",{"grow-children":o>=1})} role="tabpanel"${attr_style("",{display:store_get(r??={},"$selected_tab",x)===c&&_!==false?"flex":"none","flex-grow":o})}>`),y(n,{scale:o>=1?o:null,children:a=>{a.push("<!--[-->"),slot(a,e,"default",{}),a.push("<!--]-->");},$$slots:{default:true}}),n.push("<!----></div>"),r&&unsubscribe_stores(r),bind_props(e,{elem_id:i,elem_classes:l,label:s,id:c,visible:_,interactive:f,order:u,scale:o,component_id:p});});}function z(d,e){d.component(n=>{let{$$slots:r,$$events:m,...i}=e;const l=new $(i);N(n,{elem_id:l.shared.elem_id,elem_classes:l.shared.elem_classes,label:l.shared.label,visible:l.shared.visible,interactive:l.shared.interactive,id:l.props.id,order:l.props.order,scale:l.props.scale,component_id:l.props.component_id,children:s=>{s.push("<!--[-->"),slot(s,e,"default",{}),s.push("<!--]-->");},$$slots:{default:true}});});}

export { N as BaseTabItem, z as default };
//# sourceMappingURL=Index37-BWd-N47X.js.map

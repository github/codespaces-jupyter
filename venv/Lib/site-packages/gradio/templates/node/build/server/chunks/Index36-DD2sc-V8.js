import './async-D55cHugf.js';
import { c as spread_props, f as attr_class, a as attr, g as attr_style, i as stringify, s as slot, d as bind_props } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { y } from './Index.svelte_svelte_type_style_lang-NtqplRHH.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';

function B(h,i){h.component(n=>{let {open:_=true,width:d,position:a="left",elem_classes:e=[],elem_id:r="",onexpand:u=()=>{},oncollapse:b=()=>{}}=i,o=false,g=typeof d=="number"?`${d}px`:d,f=false;let w=e?.join(" ")||"";n.push(`<div${attr_class(`sidebar ${stringify(w)}`,"svelte-1uruprb",{open:o,right:a==="right","reduce-motion":f})}${attr("id",r)}${attr_style(`width: ${stringify(g)}; ${stringify(a)}: calc(${stringify(g)} * -1)`)}><button class="toggle-button svelte-1uruprb" aria-label="Toggle Sidebar"><div class="chevron svelte-1uruprb"><span class="chevron-left svelte-1uruprb"></span></div></button> <div class="sidebar-content svelte-1uruprb"><!--[-->`),slot(n,i,"default",{}),n.push("<!--]--></div></div>"),bind_props(i,{open:_,position:a});});}function T(h,i){h.component(n=>{const{$$slots:_,$$events:d,...a}=i,e=new $(a);let r=true,u;function b(o){$$1(o,spread_props([{autoscroll:e.shared.autoscroll,i18n:e.i18n},e.shared.loading_status])),o.push("<!----> "),e.shared.visible?(o.push("<!--[-->"),B(o,{width:e.props.width,onexpand:()=>e.dispatch("expand"),oncollapse:()=>e.dispatch("collapse"),elem_classes:e.shared.elem_classes,elem_id:e.shared.elem_id,get open(){return e.props.open},set open(s){e.props.open=s,r=false;},get position(){return e.props.position},set position(s){e.props.position=s,r=false;},children:s=>{y(s,{children:l=>{l.push("<!--[-->"),slot(l,i,"default",{}),l.push("<!--]-->");},$$slots:{default:true}});},$$slots:{default:true}})):o.push("<!--[!-->"),o.push("<!--]-->");}do r=true,u=n.copy(),b(u);while(!r);n.subsume(u);});}

export { T as default };
//# sourceMappingURL=Index36-DD2sc-V8.js.map

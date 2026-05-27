import './async-D55cHugf.js';
import { c as spread_props, f as attr_class, g as attr_style } from './index-u8mz_F03.js';
import { b as bs } from './2-htxqz-Pd.js';
import { $, x } from './utils.svelte-Cxlx5SLB.js';
import D from './HTML-BHqHXxUM.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { i } from './Code-CrFuQ3ob.js';
import { G } from './Block-DZmzQwnI.js';
import { k } from './BlockLabel-bKYWnOzQ.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
export { default as BaseExample } from './Example18-BxnxeXx7.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import 'fs';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';
import './html-CfyvkLET.js';

function F(n,h){n.component(d=>{let{$$slots:E,$$events:I,...r}=h,c=r.children;const s=new $(r);let u={value:s.props.value??"",label:s.shared.label,visible:s.shared.visible,...s.props.props};s.props.value;let i$1=[];function _(a,t){const e=Array.isArray(a)?a:[a];i$1.push({props:e,callback:t});}function m(a){const t=new Set;for(const e of i$1)e.props.some(o=>a.includes(o))&&t.add(e);for(const e of t)try{e.callback();}catch(o){console.error("Error in watch callback:",o);}}async function f(a){try{const t=await bs([a]),e=await s.shared.client.upload(t,s.shared.root,void 0,s.shared.max_file_size??void 0);if(e&&e[0])return {path:e[0].path,url:e[0].url};throw new Error("Upload failed")}catch(t){throw s.dispatch("error",t instanceof Error?t.message:String(t)),t}}G(d,{visible:s.shared.visible,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,container:s.shared.container,padding:s.props.padding!==false,overflow_behavior:"visible",children:a=>{s.shared.show_label&&s.props.buttons&&s.props.buttons.length>0?(a.push("<!--[-->"),y(a,{buttons:s.props.buttons,on_custom_button_click:t=>{s.dispatch("custom_button_click",{id:t});}})):a.push("<!--[!-->"),a.push("<!--]--> "),s.shared.show_label?(a.push("<!--[-->"),k(a,{Icon:i,show_label:s.shared.show_label,label:s.shared.label,float:true})):a.push("<!--[!-->"),a.push("<!--]--> "),$$1(a,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{variant:"center",on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}])),a.push(`<!----> <div${attr_class("html-container svelte-1jts93g",void 0,{pending:s.shared.loading_status?.status==="pending"&&s.shared.loading_status?.show_progress!=="hidden","label-padding":s.shared.show_label??void 0})}${attr_style("",{"min-height":s.props.min_height&&s.shared.loading_status?.status!=="pending"?x(s.props.min_height):void 0,"max-height":s.props.max_height?x(s.props.max_height):void 0,"overflow-y":s.props.max_height?"auto":void 0})}>`),D(a,{props:u,html_template:s.props.html_template,css_template:s.props.css_template,js_on_load:s.props.js_on_load,elem_classes:s.shared.elem_classes,visible:s.shared.visible,autoscroll:s.shared.autoscroll,apply_default_css:s.props.apply_default_css,head:s.props.head,component_class_name:s.props.component_class_name,upload:f,server:s.shared.server,watch_fn:_,fire_watchers:m,children:t=>{c?.(t);}}),a.push("<!----></div>");},$$slots:{default:true}});});}

export { D as BaseHTML, F as default };
//# sourceMappingURL=Index25-DNpgSOb-.js.map

import './async-D55cHugf.js';
import { c as spread_props } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { k } from './BlockLabel-bKYWnOzQ.js';
import { t as tick } from './index-server-CQz6EZl_.js';
import { p } from './Empty-DGRbZO0a.js';
import { i } from './File-DQh5d1OO.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { S, p as pl } from './FileUpload-ChtCAmSn.js';
import { G } from './Block-DZmzQwnI.js';
import { k as k$1 } from './UploadText-BDXc1cBO.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
export { default as BaseExample } from './Example5-CnJKzaeD.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './Upload2-CIse88hO.js';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';
import './Upload-BbxeBrrD.js';
import './DownloadLink-nj1p0krE.js';
import './html-CfyvkLET.js';

function z(d,c){d.component(t=>{let{value:o,label:_,show_label:p$1,selectable:l,i18n:r,height:h,buttons:s=null,on_custom_button_click:i$1=null,on_select:n,on_download:m}=c;p$1&&s&&s.length>0?(t.push("<!--[-->"),y(t,{buttons:s,on_custom_button_click:i$1})):t.push("<!--[!-->"),t.push("<!--]--> "),k(t,{show_label:p$1,float:o===null,Icon:i,label:_||"File"}),t.push("<!----> "),o&&(!Array.isArray(o)||o.length>0)?(t.push("<!--[-->"),S(t,{i18n:r,selectable:l,value:o,height:h})):(t.push("<!--[!-->"),p(t,{unpadded_box:true,size:"large",children:u=>{i(u);},$$slots:{default:true}})),t.push("<!--]-->");});}function N(d,c){d.component(t=>{const{$$slots:o,$$events:_,...p}=c;let l=null,r=false;class h extends ${async get_data(){return l&&(await l,await tick()),await super.get_data()}}const s=new h(p);s.props.value;let i=true,n;function m(u){G(u,{visible:s.shared.visible,variant:s.props.value?"solid":"dashed",border_mode:r?"focus":"base",padding:false,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,container:s.shared.container,scale:s.shared.scale,min_width:s.shared.min_width,allow_overflow:false,children:e=>{$$1(e,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{status:s.shared.loading_status?.status||"complete",on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}])),e.push("<!----> "),s.shared.interactive?(e.push("<!--[!-->"),pl(e,{upload:(...a)=>s.shared.client.upload(...a),stream_handler:(...a)=>s.shared.client.stream(...a),label:s.shared.label,show_label:s.shared.show_label,value:s.props.value,file_count:s.props.file_count,file_types:s.props.file_types,selectable:s.props._selectable,height:s.props.height??void 0,root:s.shared.root,allow_reordering:s.props.allow_reordering,max_file_size:s.shared.max_file_size,buttons:s.props.buttons,on_custom_button_click:a=>{s.dispatch("custom_button_click",{id:a});},onchange:a=>{s.props.value=a;},ondrag:a=>r=a,onclear:()=>s.dispatch("clear"),onselect:a=>s.dispatch("select",a),onupload:()=>s.dispatch("upload"),onerror:a=>{s.shared.loading_status=s.shared.loading_status||{},s.shared.loading_status.status="error",s.dispatch("error",a);},ondelete:a=>{s.dispatch("delete",a);},i18n:s.i18n,get upload_promise(){return l},set upload_promise(a){l=a,i=false;},children:a=>{k$1(a,{i18n:s.i18n,type:"file"});},$$slots:{default:true}})):(e.push("<!--[-->"),z(e,{on_select:({detail:a})=>s.dispatch("select",a),on_download:({detail:a})=>s.dispatch("download",a),selectable:s.props._selectable,value:s.props.value,label:s.shared.label,show_label:s.shared.show_label,height:s.props.height,i18n:s.i18n,buttons:s.props.buttons,on_custom_button_click:a=>{s.dispatch("custom_button_click",{id:a});}})),e.push("<!--]-->");},$$slots:{default:true}});}do i=true,n=t.copy(),m(n);while(!i);t.subsume(n);});}

export { z as BaseFile, pl as BaseFileUpload, S as FilePreview, N as default };
//# sourceMappingURL=Index22-4GyDcfk-.js.map

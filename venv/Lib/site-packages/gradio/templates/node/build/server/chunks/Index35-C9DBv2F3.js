import './async-D55cHugf.js';
import { d as bind_props, c as spread_props, s as slot } from './index-u8mz_F03.js';
import { t as tick } from './index-server-CQz6EZl_.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import q from './Model3D-D2I_r8xq.js';
import { e as ee } from './Upload2-CIse88hO.js';
import { v } from './ModifyUpload-C1TLJw6F.js';
import { k } from './BlockLabel-bKYWnOzQ.js';
import { i } from './File-DQh5d1OO.js';
import { G } from './Block-DZmzQwnI.js';
import { p } from './Empty-DGRbZO0a.js';
import { k as k$1 } from './UploadText-BDXc1cBO.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
export { default as BaseExample } from './Example22-CvVgGYgY.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './IconButton-BRnu7KaR.js';
import './Download-DcU5dONL.js';
import './Undo-Ce01x-M5.js';
import './DownloadLink-nj1p0krE.js';
import './Clear-D7Yjckqz.js';
import './Edit-DWZSi_T0.js';
import './Upload-BbxeBrrD.js';

function P(b,n){b.component(u=>{let{value:i$1=void 0,display_mode:j="solid",clear_color:F=[0,0,0,0],label:v$1="",show_label:a,root:f,i18n:d,zoom_speed:w=1,pan_speed:r=1,max_file_size:y=null,uploading:h=void 0,upload_promise:c=void 0,camera_position:D=[null,null,null],upload:x,stream_handler:z,onchange:p,onclear:_,ondrag:k$1,onload:l,onerror:s}=n,o=false;async function S(e){i$1=e,await tick(),p?.(i$1),l?.(i$1);}async function L(){i$1=null,await tick(),_?.(),p?.(null);}async function T(){}function W(e){s?.(e);}let m=true,M;function q(e){k(e,{show_label:a,Icon:i,label:v$1||"3D Model"}),e.push("<!----> "),i$1==null?(e.push("<!--[-->"),ee(e,{upload:x,stream_handler:z,onload:S,root:f,max_file_size:y,filetype:[".stl",".obj",".gltf",".glb","model/obj",".splat",".ply"],onerror:W,aria_label:d("model3d.drop_to_upload"),get upload_promise(){return c},set upload_promise(t){c=t,m=false;},get dragging(){return o},set dragging(t){o=t,m=false;},get uploading(){return h},set uploading(t){h=t,m=false;},children:t=>{t.push("<!--[-->"),slot(t,n,"default",{}),t.push("<!--]-->");},$$slots:{default:true}})):(e.push("<!--[!-->"),e.push('<div class="input-model svelte-18wa0f8">'),v(e,{undoable:true,onclear:L,i18n:d,onundo:T}),e.push("<!----> "),e.push("<!--[!-->"),e.push("<!---->"),e.push("<!---->"),e.push("<!--]--></div>")),e.push("<!--]-->");}do m=true,M=u.copy(),q(M);while(!m);u.subsume(M),bind_props(n,{value:i$1,uploading:h,upload_promise:c});});}function ha(b,n){b.component(u=>{let i$1 = class i extends ${async get_data(){return r&&(await r,await tick()),await super.get_data()}};const{$$slots:j,$$events:F,...v}=n,a=new i$1(v);a.props.value;let f=false,d=false,w=false,r;const y$1=typeof window<"u";function h(l){a.props.value=l,a.dispatch("change",l),w=true;}function c(l){d=l;}function D(){a.props.value=null,a.dispatch("clear");}function x(l){a.props.value=l,a.dispatch("upload");}function z(l){a.shared.loading_status&&(a.shared.loading_status.status="error"),a.dispatch("error",l);}let p$1=true,_;function k$2(l){a.shared.interactive?(l.push("<!--[!-->"),G(l,{visible:a.shared.visible,variant:a.props.value===null?"dashed":"solid",border_mode:d?"focus":"base",padding:false,elem_id:a.shared.elem_id,elem_classes:a.shared.elem_classes,container:a.shared.container,scale:a.shared.scale,min_width:a.shared.min_width,height:a.props.height,children:s=>{$$1(s,spread_props([{autoscroll:a.shared.autoscroll,i18n:a.i18n},a.shared.loading_status,{on_clear_status:()=>a.dispatch("clear_status",a.shared.loading_status)}])),s.push("<!----> "),P(s,{label:a.shared.label,show_label:a.shared.show_label,root:a.shared.root,display_mode:a.props.display_mode,clear_color:a.props.clear_color,camera_position:a.props.camera_position,zoom_speed:a.props.zoom_speed,onchange:h,ondrag:c,onclear:D,onload:x,onerror:z,i18n:a.i18n,max_file_size:a.shared.max_file_size,upload:(...o)=>a.shared.client.upload(...o),stream_handler:(...o)=>a.shared.client.stream(...o),get upload_promise(){return r},set upload_promise(o){r=o,p$1=false;},get value(){return a.props.value},set value(o){a.props.value=o,p$1=false;},get uploading(){return f},set uploading(o){f=o,p$1=false;},children:o=>{k$1(o,{i18n:a.i18n,type:"file"});},$$slots:{default:true}}),s.push("<!---->");},$$slots:{default:true}})):(l.push("<!--[-->"),G(l,{visible:a.shared.visible,variant:a.props.value===null?"dashed":"solid",border_mode:d?"focus":"base",padding:false,elem_id:a.shared.elem_id,elem_classes:a.shared.elem_classes,container:a.shared.container,scale:a.shared.scale,min_width:a.shared.min_width,height:a.props.height,children:s=>{$$1(s,spread_props([{autoscroll:a.shared.autoscroll,i18n:a.i18n},a.shared.loading_status,{on_clear_status:()=>a.dispatch("clear_status",a.shared.loading_status)}])),s.push("<!----> "),a.props.value&&y$1?(s.push("<!--[-->"),q(s,{value:a.props.value,i18n:a.i18n,display_mode:a.props.display_mode,clear_color:a.props.clear_color,label:a.shared.label,show_label:a.shared.show_label,camera_position:a.props.camera_position,zoom_speed:a.props.zoom_speed,has_change_history:w})):(s.push("<!--[!-->"),a.shared.show_label&&a.props.buttons&&a.props.buttons.length>0?(s.push("<!--[-->"),y(s,{buttons:a.props.buttons,on_custom_button_click:o=>{a.dispatch("custom_button_click",{id:o});}})):s.push("<!--[!-->"),s.push("<!--]--> "),k(s,{show_label:a.shared.show_label,Icon:i,label:a.shared.label||"3D Model"}),s.push("<!----> "),p(s,{unpadded_box:true,size:"large",children:o=>{i(o);},$$slots:{default:true}}),s.push("<!---->")),s.push("<!--]-->");},$$slots:{default:true}})),l.push("<!--]-->");}do p$1=true,_=u.copy(),k$2(_);while(!p$1);u.subsume(_);});}

export { q as BaseModel3D, P as BaseModel3DUpload, ha as default };
//# sourceMappingURL=Index35-C9DBv2F3.js.map

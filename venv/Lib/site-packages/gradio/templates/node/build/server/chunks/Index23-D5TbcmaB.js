import './async-D55cHugf.js';
import { c as spread_props, f as attr_class, j as clsx } from './index-u8mz_F03.js';
import { t as tick } from './index-server-CQz6EZl_.js';
import { G } from './Block-DZmzQwnI.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { k } from './UploadText-BDXc1cBO.js';
import { w } from './SelectSource-Bhpgvmj9.js';
import { G as xt, h as ll } from './Gallery-CSE6jQcO.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { p as pl } from './FileUpload-ChtCAmSn.js';
import { Z } from './Webcam2-B6v03Stg.js';
export { default as BaseExample } from './Example17-B0rWh-Zw.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './Upload-BbxeBrrD.js';
import './Microphone-BMM9-23W.js';
import './Video-FfbWmOVG.js';
import './Webcam-CvKMKUzA.js';
import './BlockLabel-bKYWnOzQ.js';
import './IconButton-BRnu7KaR.js';
import './Empty-DGRbZO0a.js';
import './ShareButton-C3YeJOKF.js';
import './Clear-D7Yjckqz.js';
import './Download-DcU5dONL.js';
import './Image2-vcp9_ifi.js';
import './Play-B_z3rKL1.js';
import './IconButtonWrapper-CjFRPb3y.js';
import './FullscreenButton-Bm0pL3TN.js';
import './Maximize-CuHbK64j.js';
import './Upload2-CIse88hO.js';
import './ModifyUpload-C1TLJw6F.js';
import './DownloadLink-nj1p0krE.js';
import './Edit-DWZSi_T0.js';
import './Undo-Ce01x-M5.js';
import './Image-CuPo5pWT.js';
import './Video2-BN5I0jvO.js';
import './File-DQh5d1OO.js';
import './html-CfyvkLET.js';
import './StreamingBar-BGU65w2M.js';

function le(g,b){g.component(_=>{let r;class y extends ${async get_data(){return r&&(await r,await tick()),await super.get_data()}}const{$$slots:q,$$events:E,...x}=b,e=new y(x,{selected_index:null,file_types:["image","video"]});let n=false;function G$1(o){if(!e.props.value)return;const{index:a}=o;e.dispatch("delete",o),e.props.value=e.props.value.filter((s,t)=>t!==a),e.dispatch("change",e.props.value);}async function u(o){return (await Promise.all(o.map(async s=>{if(s.path?.toLowerCase().endsWith(".svg")&&s.url){const l=await(await fetch(s.url)).text();return {...s,url:`data:image/svg+xml,${encodeURIComponent(l)}`}}return s}))).map(s=>s.mime_type?.includes("video")?{video:s,caption:null}:{image:s,caption:null})}let i=e.props.sources?e.props.sources[0]:"upload",m=e.props.value===null?true:e.props.value.length===0,c=e.props.file_types?.includes("video")&&e.props.sources.includes("webcam")?e.props.sources.concat(["webcam-video"]):e.props.sources;async function f(){navigator.clipboard.read().then(async o=>{let a=null;for(let s=0;s<o.length;s++){const t=o[s].types.find(l=>(e.props.file_types||["image"]).some(A=>l.startsWith(A+"/")));if(t){const l=await o[s].getType(t);a=new File([l],`clipboard.${t.replace("image/","")}`);break}}if(a){const s=await ll(a,l=>e.shared.client.upload(l,e.shared.root),"clipboard_upload"),t=await u(s);e.props.value?.push(...t),e.dispatch("change",e.props.value),i=null;}else e.dispatch("warning","No image or video found in clipboard");});}async function k$1(o){o==="clipboard"&&await f();}async function S(o){await tick(),o==="clipboard"?await f():(i=o,m=true);}let p=true,d;function z(o){G(o,{visible:e.shared.visible,variant:"solid",padding:false,elem_id:e.shared.elem_id,elem_classes:e.shared.elem_classes,container:e.shared.container,scale:e.shared.scale,min_width:e.shared.min_width,allow_overflow:false,height:e.props.height||void 0,get fullscreen(){return n},set fullscreen(a){n=a,p=false;},children:a=>{$$1(a,spread_props([{autoscroll:e.shared.autoscroll,i18n:e.i18n},e.shared.loading_status,{on_clear_status:()=>e.dispatch("clear_status",e.shared.loading_status)}])),a.push("<!----> "),e.shared.interactive&&m?(a.push("<!--[-->"),a.push(`<div${attr_class(clsx(!e.props.value||i&&i.includes("webcam")?"hidden-upload-input":"upload-wrapper"),"svelte-vrqwbn")}>`),pl(a,{value:null,root:e.shared.root,label:e.shared.label,max_file_size:e.shared.max_file_size,file_count:"multiple",file_types:e.props.file_types,i18n:e.i18n,upload:(...s)=>e.shared.client.upload(...s),stream_handler:(...s)=>e.shared.client.stream(...s),onupload:async s=>{const t=Array.isArray(s)?s:[s];e.props.value=await u(t),i=null,e.dispatch("upload",e.props.value),e.dispatch("change",e.props.value);},onerror:({detail:s})=>{e.shared.loading_status=e.shared.loading_status||{},e.shared.loading_status.status="error",e.dispatch("error",s);},get upload_promise(){return r},set upload_promise(s){r=s,p=false;},children:s=>{k(s,{i18n:e.i18n,type:"gallery"});},$$slots:{default:true}}),a.push("<!----></div> "),i==="webcam"?(a.push("<!--[-->"),Z(a,{root:e.shared.root,value:null,mirror_webcam:true,streaming:false,mode:"image",include_audio:false,i18n:e.i18n,upload:(...s)=>e.shared.client.upload(...s)})):(a.push("<!--[!-->"),i==="webcam-video"?(a.push("<!--[-->"),Z(a,{root:e.shared.root,value:null,mirror_webcam:true,streaming:false,mode:"video",include_audio:false,i18n:e.i18n,upload:(...s)=>e.shared.client.upload(...s)})):a.push("<!--[!-->"),a.push("<!--]-->")),a.push("<!--]--> "),c.length>1||c.includes("clipboard")?(a.push("<!--[-->"),w(a,{sources:c,handle_clear:()=>e.dispatch("clear"),handle_select:k$1,get active_source(){return i},set active_source(s){i=s,p=false;}})):a.push("<!--[!-->"),a.push("<!--]-->")):(a.push("<!--[!-->"),xt(a,{onchange:()=>e.dispatch("change"),onclear:()=>e.dispatch("change"),onselect:s=>e.dispatch("select",s),onshare:s=>e.dispatch("share",s.detail),onerror:s=>e.dispatch("error",s.detail),onpreview_open:()=>{e.dispatch("preview_open");},onpreview_close:()=>e.dispatch("preview_close"),onfullscreen:({detail:s})=>{n=s;},ondelete:G$1,onupload:async s=>{const t=Array.isArray(s)?s:[s],l=await u(t);e.props.value=e.props.value?[...e.props.value,...l]:l,e.dispatch("upload",l),e.dispatch("change",e.props.value);},sources:c,onsource_change:S,label:e.shared.label,show_label:e.shared.show_label,columns:e.props.columns,rows:e.props.rows,height:e.props.height,preview:e.props.preview,object_fit:e.props.object_fit,interactive:e.shared.interactive,allow_preview:e.props.allow_preview,show_share_button:e.props.buttons.some(s=>typeof s=="string"&&s==="share"),show_download_button:e.props.buttons.some(s=>typeof s=="string"&&s==="download"),fit_columns:e.props.fit_columns,i18n:e.i18n,_fetch:(...s)=>e.shared.client.fetch(...s),show_fullscreen_button:e.props.buttons.some(s=>typeof s=="string"&&s==="fullscreen"),buttons:e.props.buttons,oncustom_button_click:s=>{e.dispatch("custom_button_click",{id:s});},fullscreen:n,root:e.shared.root,file_types:e.props.file_types,max_file_size:e.shared.max_file_size,upload:(...s)=>e.shared.client.upload(...s),stream_handler:(...s)=>e.shared.client.stream(...s),get selected_index(){return e.props.selected_index},set selected_index(s){e.props.selected_index=s,p=false;},get value(){return e.props.value},set value(s){e.props.value=s,p=false;}})),a.push("<!--]-->");},$$slots:{default:true}});}do p=true,d=_.copy(),z(d);while(!p);_.subsume(d);});}

export { xt as BaseGallery, le as default };
//# sourceMappingURL=Index23-D5TbcmaB.js.map

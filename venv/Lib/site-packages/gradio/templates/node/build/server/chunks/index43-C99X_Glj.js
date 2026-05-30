import './async-D55cHugf.js';
import { d as bind_props, c as spread_props } from './index-u8mz_F03.js';
import { e as ee } from './Upload2-CIse88hO.js';
import { k } from './BlockLabel-bKYWnOzQ.js';
import { t as tick } from './index-server-CQz6EZl_.js';
import { r } from './Video-FfbWmOVG.js';
import './2-htxqz-Pd.js';
import { w } from './SelectSource-Bhpgvmj9.js';
import { Z } from './Webcam2-B6v03Stg.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import { P as Me, p as $e, V as Fe } from './VideoPreview-8BFo4Syx.js';
export { l as loaded, a as playable } from './VideoPreview-8BFo4Syx.js';
export { default as BaseExample } from './Example28-0xruGNBM.js';
import { G } from './Block-DZmzQwnI.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { k as k$1 } from './UploadText-BDXc1cBO.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './Upload-BbxeBrrD.js';
import './Microphone-BMM9-23W.js';
import './Webcam-CvKMKUzA.js';
import './StreamingBar-BGU65w2M.js';
import './DownloadLink-nj1p0krE.js';
import './IconButton-BRnu7KaR.js';
import './Empty-DGRbZO0a.js';
import './ShareButton-C3YeJOKF.js';
import './Download-DcU5dONL.js';
import './IconButtonWrapper-CjFRPb3y.js';
import './Maximize-CuHbK64j.js';
import './VolumeLevels-DlU2d99x.js';
import './Play-B_z3rKL1.js';
import './Undo-Ce01x-M5.js';
import './Video2-BN5I0jvO.js';
import './ModifyUpload-C1TLJw6F.js';
import './Clear-D7Yjckqz.js';
import './Edit-DWZSi_T0.js';
import './clone-Yk88IHKV.js';

function es(w$1,g){w$1.component(h=>{let{value:i=null,subtitle:P=null,sources:y=["webcam","upload"],label:u=void 0,show_download_button:k$1=false,show_label:s=true,webcam_options:c,include_audio:_,autoplay:m,root:n,i18n:f,active_source:x="webcam",handle_reset_value:z=()=>{},max_file_size:p=null,upload:r$1,stream_handler:B,loop:l,uploading:t=void 0,upload_promise:o=void 0,playback_position:V=void 0,buttons:ts=null,on_custom_button_click:ls=null,onchange:S,onclear:q,onplay:A,onpause:C,onend:D,ondrag:is,onerror:U,onupload:F,onstart_recording:ps,onstop_recording:us,onstop:H,children:G}=g,W=false,b=x??"webcam";function J(a){i=a,S?.(a),a&&F?.(a);}function E(){i=null,S?.(null),q?.();}function K(a){W=true,S?.(a);}let L=false,d=true,I;function M(a){k(a,{show_label:s,Icon:r,label:u||"Video"}),a.push('<!----> <div data-testid="video" class="video-container svelte-ey25pz">'),i===null||i?.url===void 0?(a.push("<!--[-->"),a.push('<div class="upload-container svelte-ey25pz">'),b==="upload"?(a.push("<!--[-->"),ee(a,{filetype:"video/x-m4v,video/*",onload:J,max_file_size:p,onerror:e=>U?.(e),root:n,upload:r$1,stream_handler:B,aria_label:f("video.drop_to_upload"),get upload_promise(){return o},set upload_promise(e){o=e,d=false;},get dragging(){return L},set dragging(e){L=e,d=false;},get uploading(){return t},set uploading(e){t=e,d=false;},children:e=>{G?(e.push("<!--[-->"),G(e),e.push("<!---->")):e.push("<!--[!-->"),e.push("<!--]-->");},$$slots:{default:true}})):(a.push("<!--[!-->"),b==="webcam"?(a.push("<!--[-->"),Z(a,{root:n,mirror_webcam:c.mirror,webcam_constraints:c.constraints,include_audio:_,mode:"video",i18n:f,upload:r$1,stream_every:1})):a.push("<!--[!-->"),a.push("<!--]-->")),a.push("<!--]--></div>")):(a.push("<!--[!-->"),i?.url?(a.push("<!--[-->"),a.push("<!---->"),Me(a,{upload:r$1,root:n,interactive:true,autoplay:m,src:i.url,subtitle:P?.url,is_stream:false,onplay:()=>A?.(),onpause:()=>C?.(),onstop:()=>H?.(),onend:()=>D?.(),onerror:e=>U?.(e),mirror:c.mirror&&b==="webcam",label:u,handle_change:K,handle_reset_value:z,loop:l,value:i,i18n:f,show_download_button:k$1,handle_clear:E,has_change_history:W,get playback_position(){return V},set playback_position(e){V=e,d=false;}}),a.push("<!---->")):(a.push("<!--[!-->"),i.size?(a.push("<!--[-->"),a.push(`<div class="file-name svelte-ey25pz">${escape_html(i.orig_name||i.url)}</div> <div class="file-size svelte-ey25pz">${escape_html($e(i.size))}</div>`)):a.push("<!--[!-->"),a.push("<!--]-->")),a.push("<!--]-->")),a.push("<!--]--> "),w(a,{sources:y,handle_clear:E,get active_source(){return b},set active_source(e){b=e,d=false;}}),a.push("<!----></div>");}do d=true,I=h.copy(),M(I);while(!d);h.subsume(I),bind_props(g,{value:i,uploading:t,upload_promise:o,playback_position:V});});}function Gs(w,g){w.component(h=>{const{$$slots:i,$$events:P,...y}=g;let u;class k extends ${async get_data(){return u&&(await u,await tick()),await super.get_data()}}const s=new k(y);s.props.value;let c=false,_=false,m=s.props.sources?s.props.sources[0]:void 0,n=s.props.value;const f=()=>{n===null||s.props.value===n||(s.props.value=n);};function x(l){l!=null?s.props.value=l:s.props.value=null;}function z(l){const[t,o]=l.includes("Invalid file type")?["warning","complete"]:["error","error"];s.shared.loading_status.status=o,s.shared.loading_status.message=l,s.dispatch(t,l);}let p=true,r;function B(l){s.shared.interactive?(l.push("<!--[!-->"),G(l,{visible:s.shared.visible,variant:s.props.value===null&&m==="upload"?"dashed":"solid",border_mode:_?"focus":"base",padding:false,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,height:s.props.height||void 0,width:s.props.width,container:s.shared.container,scale:s.shared.scale,min_width:s.shared.min_width,allow_overflow:false,children:t=>{$$1(t,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}])),t.push("<!----> "),es(t,{value:s.props.value,subtitle:s.props.subtitles,onchange:x,ondrag:o=>_=o,onerror:z,label:s.shared.label,show_label:s.shared.show_label,buttons:s.props.buttons??["download","share"],on_custom_button_click:o=>{s.dispatch("custom_button_click",{id:o});},sources:s.props.sources,active_source:m,webcam_options:s.props.webcam_options,include_audio:s.props.include_audio,autoplay:s.props.autoplay,root:s.shared.root,loop:s.props.loop,handle_reset_value:f,onclear:()=>{s.props.value=null,s.dispatch("clear"),s.dispatch("input");},onplay:()=>s.dispatch("play"),onpause:()=>s.dispatch("pause"),onupload:()=>{s.dispatch("upload"),s.dispatch("input");},onstop:()=>s.dispatch("stop"),onend:()=>s.dispatch("end"),onstart_recording:()=>s.dispatch("start_recording"),onstop_recording:()=>s.dispatch("stop_recording"),i18n:s.i18n,max_file_size:s.shared.max_file_size,upload:(...o)=>s.shared.client.upload(...o),stream_handler:(...o)=>s.shared.client.stream(...o),get upload_promise(){return u},set upload_promise(o){u=o,p=false;},get uploading(){return c},set uploading(o){c=o,p=false;},get playback_position(){return s.props.playback_position},set playback_position(o){s.props.playback_position=o,p=false;},children:o=>{k$1(o,{i18n:s.i18n,type:"video"});},$$slots:{default:true}}),t.push("<!---->");},$$slots:{default:true}})):(l.push("<!--[-->"),G(l,{visible:s.shared.visible,variant:s.props.value===null&&m==="upload"?"dashed":"solid",border_mode:_?"focus":"base",padding:false,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,height:s.props.height||void 0,width:s.props.width,container:s.shared.container,scale:s.shared.scale,min_width:s.shared.min_width,allow_overflow:false,children:t=>{$$1(t,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}])),t.push("<!----> "),Fe(t,{value:s.props.value,subtitle:s.props.subtitles,label:s.shared.label,show_label:s.shared.show_label,autoplay:s.props.autoplay,loop:s.props.loop,buttons:s.props.buttons??["download","share"],on_custom_button_click:o=>{s.dispatch("custom_button_click",{id:o});},onplay:()=>s.dispatch("play"),onpause:()=>s.dispatch("pause"),onstop:()=>s.dispatch("stop"),onend:()=>s.dispatch("end"),onshare:o=>s.dispatch("share",o),onerror:o=>s.dispatch("error",o),i18n:s.i18n,upload:(...o)=>s.shared.client.upload(...o),get playback_position(){return s.props.playback_position},set playback_position(o){s.props.playback_position=o,p=false;}}),t.push("<!---->");},$$slots:{default:true}})),l.push("<!--]-->");}do p=true,r=h.copy(),B(r);while(!p);h.subsume(r);});}

export { es as BaseInteractiveVideo, Me as BasePlayer, Fe as BaseStaticVideo, Gs as default, $e as prettyBytes };
//# sourceMappingURL=index43-C99X_Glj.js.map

import './async-D55cHugf.js';
import { c as spread_props, f as attr_class, a as attr, e as ensure_array_like, g as attr_style, i as stringify } from './index-u8mz_F03.js';
import { G } from './Block-DZmzQwnI.js';
import { k } from './BlockLabel-bKYWnOzQ.js';
import { p } from './Empty-DGRbZO0a.js';
import { i } from './Image2-vcp9_ifi.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { k as k$1 } from './FullscreenButton-Bm0pL3TN.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './IconButton-BRnu7KaR.js';
import './Maximize-CuHbK64j.js';
import './Clear-D7Yjckqz.js';

function P(_,f){_.component(c=>{const{$$slots:E,$$events:F,...d}=f,t=new $(d);let n=null,i$1=false,g=t.shared.label||t.i18n("annotated_image.annotated_image");t.watch_for_change();let u=true,h;function v(b){G(b,{visible:t.shared.visible,elem_id:t.shared.elem_id,elem_classes:t.shared.elem_classes,padding:false,height:t.props.height,width:t.props.width,allow_overflow:false,container:t.shared.container,scale:t.shared.scale,min_width:t.shared.min_width,get fullscreen(){return i$1},set fullscreen(s){i$1=s,u=false;},children:s=>{if($$1(s,spread_props([{autoscroll:t.shared.autoscroll,i18n:t.i18n},t.shared.loading_status])),s.push("<!----> "),k(s,{show_label:t.shared.show_label,Icon:i,label:g}),s.push('<!----> <div class="container svelte-1oizopk">'),t.props.value==null)s.push("<!--[-->"),p(s,{size:"large",unpadded_box:true,children:p=>{i(p);},$$slots:{default:true}});else {s.push("<!--[!-->"),s.push('<div class="image-container svelte-1oizopk">'),y(s,{buttons:t.props.buttons||[],on_custom_button_click:o=>{t.dispatch("custom_button_click",{id:o});},children:o=>{(t.props.buttons||[]).some(l=>typeof l=="string"&&l==="fullscreen")?(o.push("<!--[-->"),k$1(o,{fullscreen:i$1})):o.push("<!--[!-->"),o.push("<!--]-->");}}),s.push(`<!----> <img${attr_class("base-image svelte-1oizopk",void 0,{"fit-height":t.props.height&&!i$1})}${attr("src",t.props.value?t.props.value.image.url:null)} alt="the base file that is annotated"/> <!--[-->`);const p=ensure_array_like(t.props.value?t.props.value.annotations:[]);for(let o=0,l=p.length;o<l;o++){let e=p[o];s.push(`<img${attr("alt",`segmentation mask identifying ${stringify(t.shared.label)} within the uploaded file`)}${attr_class("mask fit-height svelte-1oizopk",void 0,{"fit-height":!i$1,active:n==e.label,inactive:n!=e.label&&n!=null})}${attr("src",e.image.url)}${attr_style(t.props.color_map&&e.label in t.props.color_map?null:`filter: hue-rotate(${Math.round(o*360/(t.props.value?.annotations.length??1))}deg);`)}/>`);}if(s.push("<!--]--></div> "),t.props.show_legend&&t.props.value){s.push("<!--[-->"),s.push('<div class="legend svelte-1oizopk"><!--[-->');const o=ensure_array_like(t.props.value.annotations);for(let l=0,e=o.length;l<e;l++){let r=o[l];s.push(`<button class="legend-item svelte-1oizopk"${attr_style(`background-color: ${stringify(t.props.color_map&&r.label in t.props.color_map?t.props.color_map[r.label]+"88":`hsla(${Math.round(l*360/t.props.value.annotations.length)}, 100%, 50%, 0.3)`)}`)}>${escape_html(r.label)}</button>`);}s.push("<!--]--></div>");}else s.push("<!--[!-->");s.push("<!--]-->");}s.push("<!--]--></div>");},$$slots:{default:true}});}do u=true,h=c.copy(),v(h);while(!u);c.subsume(h);});}

export { P as default };
//# sourceMappingURL=Index19-Dbd_fAnX.js.map

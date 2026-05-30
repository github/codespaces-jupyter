import './async-D55cHugf.js';
import { c as spread_props } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { G } from './Block-DZmzQwnI.js';
import { c } from './BlockTitle-BnJIYf6a.js';
import { w } from './IconButton-BRnu7KaR.js';
import { p } from './Empty-DGRbZO0a.js';
import { l } from './Download-DcU5dONL.js';
import { e } from './LineChart-DIvFgn2j.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { k } from './FullscreenButton-Bm0pL3TN.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './Info-DU6zbiUl.js';
import './html-CfyvkLET.js';
import './Maximize-CuHbK64j.js';
import './Clear-D7Yjckqz.js';

function Y(d,m){d.component(c$1=>{let{$$slots:G$1,$$events:L,...h}=m;const s=new $(h);(()=>{if(!s.props.color||!s.props.value||s.props.value.datatypes[s.props.color]!=="nominal")return [];const p=s.props.value.columns.indexOf(s.props.color);return p===-1?[]:Array.from(new Set(s.props.value.data.map(o=>o[p])))})();let l$1=s.props.x_lim||null,i=s.props.y_lim||null;l$1?.[0]!==null&&l$1?.[0],l$1?.[1]!==null&&l$1?.[1],i?.[0]!==null&&i?.[0],i?.[1]!==null&&i?.[1];let n=false;function _(p){if(p==="x")return "ascending";if(p==="-x")return "descending";if(p==="y")return {field:s.props.y,order:"ascending"};if(p==="-y")return {field:s.props.y,order:"descending"};if(p===null)return null;if(Array.isArray(p))return p}_(s.props.sort),s.props.value&&s.props.value.datatypes[s.props.x];const g={s:1,m:60,h:3600,d:1440*60};let u=s.props.x_bin?typeof s.props.x_bin=="string"?1e3*parseInt(s.props.x_bin.substring(0,s.props.x_bin.length-1))*g[s.props.x_bin[s.props.x_bin.length-1]]:s.props.x_bin:void 0;(()=>{if(s.props.value)if(s.props.value.mark==="point"){const p=u!==void 0;return s.props.y_aggregate||p?"sum":void 0}else return s.props.y_aggregate?s.props.y_aggregate:"sum"})(),s.props.value&&(s.props.value.mark==="point"||u!==void 0||s.props.value.datatypes[s.props.x]),s.props.value;const b=typeof window<"u";function v(){}JSON.stringify(s.props.color_map);let a=true,r;function x(p$1){G(p$1,{visible:s.shared.visible,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,scale:s.shared.scale,min_width:s.shared.min_width,allow_overflow:false,padding:true,height:s.props.height,get fullscreen(){return n},set fullscreen(o){n=o,a=false;},children:o=>{s.shared.loading_status?(o.push("<!--[-->"),$$1(o,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}]))):o.push("<!--[!-->"),o.push("<!--]--> "),s.props.buttons?.length?(o.push("<!--[-->"),y(o,{buttons:s.props.buttons,on_custom_button_click:t=>{s.dispatch("custom_button_click",{id:t});},children:t=>{s.props.buttons?.some(e=>typeof e=="string"&&e==="export")?(t.push("<!--[-->"),w(t,{Icon:l,label:"Export",onclick:v})):t.push("<!--[!-->"),t.push("<!--]--> "),s.props.buttons?.some(e=>typeof e=="string"&&e==="fullscreen")?(t.push("<!--[-->"),k(t,{fullscreen:n})):t.push("<!--[!-->"),t.push("<!--]-->");}})):o.push("<!--[!-->"),o.push("<!--]--> "),c(o,{show_label:s.shared.show_label,info:void 0,children:t=>{t.push(`<!---->${escape_html(s.shared.label)}`);},$$slots:{default:true}}),o.push("<!----> "),s.props.value&&b?(o.push("<!--[-->"),o.push('<div class="svelte-19utvcn"></div> '),s.props.caption?(o.push("<!--[-->"),o.push(`<p class="caption svelte-19utvcn">${escape_html(s.props.caption)}</p>`)):o.push("<!--[!-->"),o.push("<!--]-->")):(o.push("<!--[!-->"),p(o,{unpadded_box:true,children:t=>{e(t);},$$slots:{default:true}})),o.push("<!--]-->");},$$slots:{default:true}});}do a=true,r=c$1.copy(),x(r);while(!a);c$1.subsume(r);});}

export { Y as default };
//# sourceMappingURL=Index27-BWkZsmIj.js.map

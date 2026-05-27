import './async-D55cHugf.js';
import { c as spread_props } from './index-u8mz_F03.js';
import { t as tick } from './index-server-CQz6EZl_.js';
import { e as et } from './Textbox-Ba-vm1zH.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { G } from './Block-DZmzQwnI.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
export { default as BaseExample } from './Example2-zAdYDcJY.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './BlockTitle-BnJIYf6a.js';
import './Info-DU6zbiUl.js';
import './html-CfyvkLET.js';
import './IconButton-BRnu7KaR.js';
import './Check-C7_ZsXgh.js';
import './Copy-B8YOhH7c.js';
import './Send-C1RPCeF6.js';
import './Square-CDuLMWYC.js';
import './IconButtonWrapper-CjFRPb3y.js';
import './index-Cg-Pg6j3.js';
import './Clear-D7Yjckqz.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './clone-Yk88IHKV.js';

function z(p,i){p.component(l=>{let{$$slots:g,$$events:w,...n}=i;const s=new $(n);let u=s.shared.label||"Textbox";s.props.value=s.props.value??"",s.props.value;async function d(a){!s.shared||!s.props||(s.props.validation_error=null,s.props.value=a,await tick(),s.dispatch("input"));}function c(a){!s.shared||!s.props||(s.props.validation_error=null,s.props.value=a);}let e=true,r;function h(a){G(a,{visible:s.shared.visible,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,scale:s.shared.scale,min_width:s.shared.min_width,allow_overflow:false,padding:s.shared.container,rtl:s.props.rtl,children:o=>{s.shared.loading_status?(o.push("<!--[-->"),$$1(o,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{show_validation_error:false,on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}]))):o.push("<!--[!-->"),o.push("<!--]--> "),et(o,{label:u,info:s.props.info,show_label:s.shared.show_label,lines:s.props.lines,type:s.props.type,rtl:s.props.rtl,text_align:s.props.text_align,max_lines:s.props.max_lines,placeholder:s.props.placeholder,submit_btn:s.props.submit_btn,stop_btn:s.props.stop_btn,buttons:s.props.buttons,autofocus:s.props.autofocus,container:s.shared.container,autoscroll:s.shared.autoscroll,max_length:s.props.max_length,html_attributes:s.props.html_attributes,validation_error:s.shared?.loading_status?.validation_error||s.shared?.validation_error,onchange:c,oninput:d,onsubmit:()=>{s.shared.validation_error=null,s.dispatch("submit");},onblur:()=>s.dispatch("blur"),onselect:t=>s.dispatch("select",t),onfocus:()=>s.dispatch("focus"),onstop:()=>s.dispatch("stop"),oncopy:t=>s.dispatch("copy",t),oncustombuttonclick:t=>{s.dispatch("custom_button_click",{id:t});},disabled:!s.shared.interactive,get value(){return s.props.value},set value(t){s.props.value=t,e=false;}}),o.push("<!---->");},$$slots:{default:true}});}do e=true,r=l.copy(),h(r);while(!e);l.subsume(r);});}

export { et as BaseTextbox, z as default };
//# sourceMappingURL=Index16-VNTQwsn7.js.map

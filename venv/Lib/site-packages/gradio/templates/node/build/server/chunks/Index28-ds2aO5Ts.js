import './async-D55cHugf.js';
import { c as spread_props, f as attr_class, a as attr } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { G } from './Block-DZmzQwnI.js';
import { c } from './BlockTitle-BnJIYf6a.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './Info-DU6zbiUl.js';
import './html-CfyvkLET.js';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';

function S(l,i){l.component(e=>{const{$$slots:m,$$events:_,...r}=i,s=new $(r);s.props.value??=0,s.props.value;const p=!s.shared.interactive;G(e,{visible:s.shared.visible,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,padding:s.shared.container,allow_overflow:false,scale:s.shared.scale,min_width:s.shared.min_width,children:t=>{$$1(t,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{show_validation_error:false,on_clear_status:()=>{s.dispatch("clear_status",s.shared.loading_status);}}])),t.push(`<!----> <label${attr_class("block svelte-16ty2ow",void 0,{container:s.shared.container})}>`),s.shared.show_label&&s.props.buttons&&s.props.buttons.length>0?(t.push("<!--[-->"),y(t,{buttons:s.props.buttons,on_custom_button_click:o=>{s.dispatch("custom_button_click",{id:o});}})):t.push("<!--[!-->"),t.push("<!--]--> "),c(t,{show_label:s.shared.show_label,info:s.props.info,children:o=>{o.push(`<!---->${escape_html(s.shared.label||"Number")} `),s.shared.loading_status?.validation_error?(o.push("<!--[-->"),o.push(`<div class="validation-error svelte-16ty2ow">${escape_html(s.shared.loading_status?.validation_error)}</div>`)):o.push("<!--[!-->"),o.push("<!--]-->");},$$slots:{default:true}}),t.push(`<!----> <input${attr("aria-label",s.shared.label||"Number")} type="number"${attr("value",s.props.value)}${attr("min",s.props.minimum)}${attr("max",s.props.maximum)}${attr("step",s.props.step)}${attr("placeholder",s.props.placeholder)}${attr("disabled",p,true)}${attr_class("svelte-16ty2ow",void 0,{"validation-error":s.shared.loading_status?.validation_error})}/></label>`);},$$slots:{default:true}});});}

export { S as default };
//# sourceMappingURL=Index28-ds2aO5Ts.js.map

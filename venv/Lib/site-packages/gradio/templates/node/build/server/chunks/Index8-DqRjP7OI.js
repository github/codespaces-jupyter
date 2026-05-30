import './async-D55cHugf.js';
import { c as spread_props } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { G } from './Block-DZmzQwnI.js';
import { u } from './Info-DU6zbiUl.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { d } from './Checkbox-C7eMNvyZ.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './html-CfyvkLET.js';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';

function A(e,l){e.component(i=>{let{$$slots:v,$$events:g,...u$1}=l;const s=new $(u$1);let a=true,p;function c(h){G(h,{visible:s.shared.visible,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,children:t=>{$$1(t,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}])),t.push("<!----> "),s.shared.show_label&&s.props.buttons&&s.props.buttons.length>0?(t.push("<!--[-->"),y(t,{buttons:s.props.buttons,on_custom_button_click:o=>{s.dispatch("custom_button_click",{id:o});}})):t.push("<!--[!-->"),t.push("<!--]--> "),d(t,{label:s.shared.label||s.i18n("checkbox.checkbox"),interactive:s.shared.interactive,show_label:s.shared.show_label,on_change:o=>s.dispatch("change",o),on_input:()=>s.dispatch("input"),on_select:o=>s.dispatch("select",o),get value(){return s.props.value},set value(o){s.props.value=o,a=false;}}),t.push("<!----> "),s.props.info?(t.push("<!--[-->"),u(t,{info:s.props.info})):t.push("<!--[!-->"),t.push("<!--]-->");},$$slots:{default:true}});}do a=true,p=i.copy(),c(p);while(!a);i.subsume(p);});}

export { d as BaseCheckbox, A as default };
//# sourceMappingURL=Index8-DqRjP7OI.js.map

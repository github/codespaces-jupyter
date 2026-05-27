import './async-D55cHugf.js';
import { c as spread_props } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { a as b, P as y$1 } from './Plot-DuOLe2_8.js';
import { G } from './Block-DZmzQwnI.js';
import { k } from './BlockLabel-bKYWnOzQ.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { k as k$1 } from './FullscreenButton-Bm0pL3TN.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './Empty-DGRbZO0a.js';
import './IconButton-BRnu7KaR.js';
import './Maximize-CuHbK64j.js';
import './Clear-D7Yjckqz.js';

function D(i,n){i.component(p=>{let{$$slots:B,$$events:k$2,...u}=n;const s=new $(u);let l=false,e=true,a;function r(c){G(c,{padding:false,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,visible:s.shared.visible,container:s.shared.container,scale:s.shared.scale,min_width:s.shared.min_width,allow_overflow:false,get fullscreen(){return l},set fullscreen(o){l=o,e=false;},children:o=>{k(o,{show_label:s.shared.show_label,label:s.shared.label||s.i18n("plot.plot"),Icon:y$1}),o.push("<!----> "),s.props.buttons&&s.props.buttons.length>0||s.props.show_fullscreen_button?(o.push("<!--[-->"),y(o,{buttons:s.props.buttons??[],on_custom_button_click:t=>{s.dispatch("custom_button_click",{id:t});},children:t=>{s.props.show_fullscreen_button?(t.push("<!--[-->"),k$1(t,{fullscreen:l})):t.push("<!--[!-->"),t.push("<!--]-->");}})):o.push("<!--[!-->"),o.push("<!--]--> "),$$1(o,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}])),o.push("<!----> "),b(o,{value:s.props.value,theme_mode:s.props.theme_mode,show_label:s.shared.show_label,caption:s.props.caption,bokeh_version:s.props.bokeh_version,show_actions_button:s.props.show_actions_button,_selectable:s.props._selectable,x_lim:s.props.x_lim,show_fullscreen_button:s.props.show_fullscreen_button,on_change:()=>s.dispatch("change")}),o.push("<!---->");},$$slots:{default:true}});}do e=true,a=p.copy(),r(a);while(!e);p.subsume(a);});}

export { b as BasePlot, D as default };
//# sourceMappingURL=Index14-B6rECJ89.js.map

import './async-D55cHugf.js';
import { c as spread_props, a as attr } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { G } from './Block-DZmzQwnI.js';
import { c } from './BlockTitle-BnJIYf6a.js';
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

let f=0;function T(r,o){r.component(m=>{let{$$slots:b,$$events:_,...u}=o,t=new $(u);t.props.value,t.props.value;const p=`range_id_${f++}`;let n=t.props.minimum??0;(()=>{const a=t.props.minimum,s=t.props.maximum,i=t.props.value;return i>s?100:i<a?0:(i-a)/(s-a)*100})();let l=!t.shared.interactive;G(m,{visible:t.shared.visible,elem_id:t.shared.elem_id,elem_classes:t.shared.elem_classes,container:t.shared.container,scale:t.shared.scale,min_width:t.shared.min_width,children:a=>{$$1(a,spread_props([{autoscroll:t.shared.autoscroll,i18n:t.i18n},t.shared.loading_status,{on_clear_status:()=>t.dispatch("clear_status",t.shared.loading_status)}])),a.push(`<!----> <div class="wrap svelte-8epfm4"><div class="head svelte-8epfm4"><label${attr("for",p)} class="svelte-8epfm4">`),c(a,{show_label:t.shared.show_label,info:t.props.info,children:s=>{s.push(`<!---->${escape_html(t.shared.label||"Slider")}`);},$$slots:{default:true}}),a.push(`<!----></label> <div class="tab-like-container svelte-8epfm4"><input${attr("aria-label",`number input for ${t.shared.label}`)} data-testid="number-input" type="number"${attr("value",t.props.value)}${attr("min",t.props.minimum)}${attr("max",t.props.maximum)}${attr("step",t.props.step)}${attr("disabled",l,true)} class="svelte-8epfm4"/> `),t.props.buttons?.includes("reset")??true?(a.push("<!--[-->"),a.push(`<button class="reset-button svelte-8epfm4"${attr("disabled",l,true)} aria-label="Reset to default value" data-testid="reset-button">↺</button>`)):a.push("<!--[!-->"),a.push(`<!--]--></div></div> <div class="slider_input_container svelte-8epfm4"><span class="min_value svelte-8epfm4" data-testid="min-value">${escape_html(n)}</span> <input type="range"${attr("id",p)} name="cowbell" data-testid="range-input"${attr("value",t.props.value)}${attr("min",t.props.minimum)}${attr("max",t.props.maximum)}${attr("step",t.props.step)}${attr("disabled",l,true)}${attr("aria-label",`range slider for ${t.shared.label}`)} class="svelte-8epfm4"/> <span class="max_value svelte-8epfm4" data-testid="max-value">${escape_html(t.props.maximum)}</span></div></div>`);},$$slots:{default:true}});});}

export { T as default };
//# sourceMappingURL=Index30-DmCmw-Og.js.map

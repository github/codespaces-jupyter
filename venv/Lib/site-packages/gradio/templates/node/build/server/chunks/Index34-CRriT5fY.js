import './async-D55cHugf.js';
import { f as attr_class, g as attr_style, e as ensure_array_like, a as attr, i as stringify, c as spread_props } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { $ } from './utils.svelte-Cxlx5SLB.js';
import { e } from './LineChart-DIvFgn2j.js';
import { G } from './Block-DZmzQwnI.js';
import { k as k$1 } from './BlockLabel-bKYWnOzQ.js';
import { p } from './Empty-DGRbZO0a.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { $ as $$1 } from './index3-BSHNFmik.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';

function k(i,n){i.component(l=>{let{value:c,color:h=void 0,selectable:p=false,show_heading:s=true,onselect:u}=n;function t(e){return e.replace(/\s/g,"-")}if(l.push('<div class="container svelte-g2cwl3">'),s||!c.confidences?(l.push("<!--[-->"),l.push(`<h2${attr_class("output-class svelte-g2cwl3",void 0,{"no-confidence":!("confidences"in c)})} data-testid="label-output-value"${attr_style("",{"background-color":h||"transparent"})}>${escape_html(c.label)}</h2>`)):l.push("<!--[!-->"),l.push("<!--]--> "),typeof c=="object"&&c.confidences){l.push("<!--[-->"),l.push("<!--[-->");const e=ensure_array_like(c.confidences);for(let d=0,b=e.length;d<b;d++){let o=e[d];l.push(`<button${attr_class("confidence-set group svelte-g2cwl3",void 0,{selectable:p})}${attr("data-testid",`${o.label}-confidence-set`)}><div class="inner-wrap svelte-g2cwl3"><meter${attr("aria-labelledby",t(`meter-text-${o.label}`))}${attr("aria-label",o.label)}${attr("aria-valuenow",Math.round(o.confidence*100))} aria-valuemin="0" aria-valuemax="100" class="bar svelte-g2cwl3" min="0" max="1"${attr("value",o.confidence)}${attr_style(`width: ${stringify(o.confidence*100)}%; background: var(--stat-background-fill); `)}></meter> <dl class="label svelte-g2cwl3"><dt${attr("id",t(`meter-text-${o.label}`))} class="text svelte-g2cwl3">${escape_html(o.label)}</dt> <div class="line svelte-g2cwl3"></div> <dd class="confidence svelte-g2cwl3">${escape_html(Math.round(o.confidence*100))}%</dd></dl></div></button>`);}l.push("<!--]-->");}else l.push("<!--[!-->");l.push("<!--]--></div>");});}function A(i,n){i.component(l=>{const{$$slots:c,$$events:h,...p$1}=n,s=new $(p$1);let u=s.props.value.label;s.watch_for_change(),G(l,{test_id:"label",visible:s.shared.visible,elem_id:s.shared.elem_id,elem_classes:s.shared.elem_classes,container:s.shared.container,scale:s.shared.scale,min_width:s.shared.min_width,padding:false,children:t=>{$$1(t,spread_props([{autoscroll:s.shared.autoscroll,i18n:s.i18n},s.shared.loading_status,{on_clear_status:()=>s.dispatch("clear_status",s.shared.loading_status)}])),t.push("<!----> "),s.shared.show_label&&s.props.buttons&&s.props.buttons.length>0?(t.push("<!--[-->"),y(t,{buttons:s.props.buttons,on_custom_button_click:e=>{s.dispatch("custom_button_click",{id:e});}})):t.push("<!--[!-->"),t.push("<!--]--> "),s.shared.show_label?(t.push("<!--[-->"),k$1(t,{Icon:e,label:s.shared.label||s.i18n("label.label"),disable:s.shared.container===false,float:s.props.show_heading===true})):t.push("<!--[!-->"),t.push("<!--]--> "),u!=null?(t.push("<!--[-->"),k(t,{onselect:e=>s.dispatch("select",e),selectable:s.props._selectable,value:s.props.value,color:s.props.color,show_heading:s.props.show_heading})):(t.push("<!--[!-->"),p(t,{unpadded_box:true,children:e$1=>{e(e$1);},$$slots:{default:true}})),t.push("<!--]-->");},$$slots:{default:true}});});}

export { k as BaseLabel, A as default };
//# sourceMappingURL=Index34-CRriT5fY.js.map

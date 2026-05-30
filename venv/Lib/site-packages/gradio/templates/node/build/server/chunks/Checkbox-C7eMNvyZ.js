import './async-D55cHugf.js';
import { f as attr_class, a as attr, d as bind_props } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';

function d(c,a){c.component(t=>{let{label:o="Checkbox",value:s=void 0,indeterminate:n=false,interactive:i=true,show_label:p=true,on_change:b,on_input:h,on_select:u}=a,l=!i;t.push(`<label${attr_class("checkbox-container svelte-1q8xtp9",void 0,{disabled:l})}><input${attr("checked",s,true)}${attr("disabled",l,true)} type="checkbox" name="test" data-testid="checkbox" class="svelte-1q8xtp9"/> `),p?(t.push("<!--[-->"),t.push(`<span class="label-text svelte-1q8xtp9">${escape_html(o)}</span>`)):t.push("<!--[!-->"),t.push("<!--]--></label>"),bind_props(a,{value:s});});}

export { d };
//# sourceMappingURL=Checkbox-C7eMNvyZ.js.map

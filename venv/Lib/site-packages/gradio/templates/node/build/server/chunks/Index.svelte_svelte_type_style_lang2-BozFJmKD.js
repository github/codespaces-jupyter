import './async-D55cHugf.js';
import { f as attr_class, a as attr, g as attr_style, i as stringify } from './index-u8mz_F03.js';
import './2-htxqz-Pd.js';
import { x } from './utils.svelte-Cxlx5SLB.js';
import { e } from './Check-C7_ZsXgh.js';
import { h } from './Copy-B8YOhH7c.js';
import { w } from './IconButton-BRnu7KaR.js';
import { y } from './IconButtonWrapper-CjFRPb3y.js';
import { e as en } from './MarkdownCode-1QWDAoaN.js';

function K(m,r){m.component(t=>{let{elem_classes:c=[],visible:f=true,value:e$1,min_height:s=void 0,rtl:u=false,sanitize_html:d=true,line_breaks:h$1=false,latex_delimiters:_=[],header_links:g=false,height:n=void 0,show_copy_button:v=false,loading_status:y$1=void 0,theme_mode:k,onchange:z=()=>{},oncopy:b=l=>{}}=r,o=false,a;async function w$1(){"clipboard"in navigator&&(await navigator.clipboard.writeText(e$1),b({value:e$1}),C());}function C(){o=true,a&&clearTimeout(a),a=setTimeout(()=>{o=false;},1e3);}t.push(`<div${attr_class(`prose ${stringify(c?.join(" ")||"")}`,"svelte-1xjkzpp",{hide:!f})} data-testid="markdown"${attr("dir",u?"rtl":"ltr")}${attr_style(n?`max-height: ${x(n)}; overflow-y: auto;`:"",{"min-height":s&&y$1?.status!=="pending"?x(s):void 0})}>`),v?(t.push("<!--[-->"),y(t,{children:l=>{w(l,{Icon:o?e:h,onclick:w$1,label:o?"Copied conversation":"Copy conversation"});}})):t.push("<!--[!-->"),t.push("<!--]--> "),en(t,{message:e$1,latex_delimiters:_,sanitize_html:d,line_breaks:h$1,chatbot:false,header_links:g,theme_mode:k}),t.push("<!----></div>");});}

export { K };
//# sourceMappingURL=Index.svelte_svelte_type_style_lang2-BozFJmKD.js.map

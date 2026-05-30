import './async-D55cHugf.js';
import { a as attr, f as attr_class, g as attr_style, i as stringify, c as spread_props, s as slot } from './index-u8mz_F03.js';
import { $ } from './index3-BSHNFmik.js';

function y(e,a){e.component(s=>{let{$$slots:h,$$events:d,...t}=a,p=t.scale??null,n=t.min_width??0,m=t.elem_id??"",u=t.elem_classes??[],c=t.visible??true,o=t.variant??"default",i=t.loading_status;t.show_progress,s.push(`<div${attr("id",m)}${attr_class(`column ${stringify(u.join(" "))}`,"svelte-siq5d6",{compact:o==="compact",panel:o==="panel",hide:!c})}${attr_style("",{"flex-grow":p,"min-width":`calc(min(${stringify(n)}px, 100%))`})}>`),i&&i.show_progress?(s.push("<!--[-->"),$(s,spread_props([{autoscroll:t.autoscroll,i18n:t.i18n},i,{status:i?i.status=="pending"?"generating":i.status:null}]))):s.push("<!--[!-->"),s.push("<!--]--> <!--[-->"),slot(s,a,"default",{}),s.push("<!--]--></div>");});}

export { y };
//# sourceMappingURL=Index.svelte_svelte_type_style_lang-NtqplRHH.js.map

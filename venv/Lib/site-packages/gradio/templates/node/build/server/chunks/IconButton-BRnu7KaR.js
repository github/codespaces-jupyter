import './async-D55cHugf.js';
import { f as attr_class, a as attr, g as attr_style } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';

/* empty css                                        */function w(l,u){let{Icon:h,label:s="",show_label:b=false,pending:e=false,size:t="small",padded:n=true,highlight:p=false,disabled:o=false,hasPopup:m=false,color:d="var(--block-label-text-color)",transparent:f=false,background:g="var(--block-background-fill)",border:r="transparent",onclick:v,children:i}=u,c=p?"var(--color-accent)":d;l.push(`<button${attr_class("icon-button svelte-3jwzs9",void 0,{pending:e,padded:n,highlight:p,transparent:f})}${attr("disabled",o,true)}${attr("aria-label",s)}${attr("aria-haspopup",m)}${attr("title",s)}${attr_style("",{"--border-color":r,color:!o&&c?c:"var(--block-label-text-color)","--bg-color":o?"auto":g})}>`),b?(l.push("<!--[-->"),l.push(`<span class="svelte-3jwzs9">${escape_html(s)}</span>`)):l.push("<!--[!-->"),l.push(`<!--]--> <div${attr_class("svelte-3jwzs9",void 0,{"x-small":t==="x-small",small:t==="small",large:t==="large",medium:t==="medium"})}><!---->`),h(l,{}),l.push("<!----> "),i?(l.push("<!--[-->"),i(l),l.push("<!---->")):l.push("<!--[!-->"),l.push("<!--]--></div></button>");}

export { w };
//# sourceMappingURL=IconButton-BRnu7KaR.js.map

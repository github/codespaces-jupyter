import { f as fallback } from './async-D55cHugf.js';
import { a as attr, f as attr_class, d as bind_props } from './index-u8mz_F03.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';

/* empty css                                        */function k(t,a){let b=fallback(a.label,null),s=a.Icon,e=fallback(a.show_label,true),c=fallback(a.disable,false),f=fallback(a.float,true),o=fallback(a.rtl,false);t.push(`<label for="" data-testid="block-label"${attr("dir",o?"rtl":"ltr")}${attr_class("svelte-19djge9",void 0,{hide:!e,"sr-only":!e,float:f,"hide-label":c})}><span class="svelte-19djge9">`),s(t,{}),t.push(`<!----></span> ${escape_html(b)}</label>`),bind_props(a,{label:b,Icon:s,show_label:e,disable:c,float:f,rtl:o});}

export { k };
//# sourceMappingURL=BlockLabel-bKYWnOzQ.js.map

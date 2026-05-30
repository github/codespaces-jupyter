import './async-D55cHugf.js';
import { f as attr_class, d as bind_props } from './index-u8mz_F03.js';
import { h, e } from './Upload-BbxeBrrD.js';
import { i } from './Microphone-BMM9-23W.js';
import { r } from './Video-FfbWmOVG.js';
import { h as h$1 } from './Webcam-CvKMKUzA.js';

function w(c,u){c.component(s=>{let{sources:o,active_source:t=void 0,handle_clear:b=()=>{},handle_select:v=()=>{}}=u;[...new Set(o)].length>1||o.includes("clipboard")?(s.push("<!--[-->"),s.push('<span class="source-selection svelte-exvkcd" data-testid="source-select">'),o.includes("upload")?(s.push("<!--[-->"),s.push(`<button${attr_class("icon svelte-exvkcd",void 0,{selected:t==="upload"||!t})} aria-label="Upload file">`),h(s),s.push("<!----></button>")):s.push("<!--[!-->"),s.push("<!--]--> "),o.includes("microphone")?(s.push("<!--[-->"),s.push(`<button${attr_class("icon svelte-exvkcd",void 0,{selected:t==="microphone"})} aria-label="Record audio">`),i(s),s.push("<!----></button>")):s.push("<!--[!-->"),s.push("<!--]--> "),o.includes("webcam")?(s.push("<!--[-->"),s.push(`<button${attr_class("icon svelte-exvkcd",void 0,{selected:t==="webcam"})} aria-label="Capture from camera">`),h$1(s),s.push("<!----></button>")):s.push("<!--[!-->"),s.push("<!--]--> "),o.includes("webcam-video")?(s.push("<!--[-->"),s.push(`<button${attr_class("icon svelte-exvkcd",void 0,{selected:t==="webcam-video"})} aria-label="Record video from camera">`),r(s),s.push("<!----></button>")):s.push("<!--[!-->"),s.push("<!--]--> "),o.includes("clipboard")?(s.push("<!--[-->"),s.push(`<button${attr_class("icon svelte-exvkcd",void 0,{selected:t==="clipboard"})} aria-label="Paste from clipboard">`),e(s),s.push("<!----></button>")):s.push("<!--[!-->"),s.push("<!--]--></span>")):s.push("<!--[!-->"),s.push("<!--]-->"),bind_props(u,{active_source:t});});}

export { w };
//# sourceMappingURL=SelectSource-Bhpgvmj9.js.map

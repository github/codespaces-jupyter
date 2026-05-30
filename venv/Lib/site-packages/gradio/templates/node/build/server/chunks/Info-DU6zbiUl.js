import './async-D55cHugf.js';
import { d as bind_props } from './index-u8mz_F03.js';
import { h as html } from './html-CfyvkLET.js';

/* empty css                                        */const c=/`([^`]+)`/g,a=/\[([^\]]+)\]\(([^)]+)\)/g,_=/\*\*(.+?)\*\*/g,l=/__(.+?)__/g,s=/\*(.+?)\*/g,p=/(?<!\w)_(.+?)_(?!\w)/g,i=/^\w+:/;function g(n){return n.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}function m(n,e,t){const r=t.trim();return i.test(r)?/^https?:/i.test(r)?`<a href="${r}" target="_blank" rel="noopener noreferrer">${e}</a>`:e:`<a href="${r}" target="_blank" rel="noopener noreferrer">${e}</a>`}function f(n){let e=g(n);return e=e.replace(c,"<code>$1</code>"),e=e.replace(a,m),e=e.replace(_,"<strong>$1</strong>"),e=e.replace(l,"<strong>$1</strong>"),e=e.replace(s,"<em>$1</em>"),e=e.replace(p,"<em>$1</em>"),e=e.replace(/\n/g,"<br>"),e}function u(n,e){n.component(t=>{let r=e.info;t.push(`<div class="info-text svelte-9hc4ua">${html(f(r))}</div>`),bind_props(e,{info:r});});}

export { u };
//# sourceMappingURL=Info-DU6zbiUl.js.map

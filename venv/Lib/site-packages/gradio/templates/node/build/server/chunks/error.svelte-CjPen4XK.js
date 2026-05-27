import './async-D55cHugf.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import { g as getContext } from './context-CBkBucIx.js';
import { m as m$1, A } from './client-BEJC6ylv.js';
import { s, e } from './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './exports-WsxCBL4M.js';

const g={get error(){return m$1.error},get status(){return m$1.status}};A.updated.check;function t(){return getContext("__request__")}function n(e){try{return t()}catch{throw new Error(`Can only read '${e}' on the server during rendering (not in e.g. \`load\` functions), as it is bound to the current request via component context. This prevents state from leaking between users.For more information, see https://svelte.dev/docs/kit/state-management#avoid-shared-state-on-the-server`)}}const m={get error(){return (e?n("page.error"):t()).page.error},get status(){return (e?n("page.status"):t()).page.status}},a=s?g:m;function l(e,d){e.component(p=>{p.push(`<h1>${escape_html(a.status)}</h1> <p>${escape_html(a.error?.message)}</p>`);});}

export { l as default };
//# sourceMappingURL=error.svelte-CjPen4XK.js.map

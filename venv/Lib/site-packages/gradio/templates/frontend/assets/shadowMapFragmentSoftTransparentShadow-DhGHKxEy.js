import{S as r}from"./index-B3XdImUZ.js";import"./index-0BmjH1qd.js";const a="shadowMapFragmentSoftTransparentShadow",o=`#if SM_SOFTTRANSPARENTSHADOW==1
if ((bayerDither8(floor(((fragmentInputs.position.xy)%(8.0)))))/64.0>=uniforms.softTransparentShadowSM.x*alpha) {discard;}
#endif
`;r.IncludesShadersStoreWGSL[a]||(r.IncludesShadersStoreWGSL[a]=o);const S={name:a,shader:o};export{S as shadowMapFragmentSoftTransparentShadowWGSL};

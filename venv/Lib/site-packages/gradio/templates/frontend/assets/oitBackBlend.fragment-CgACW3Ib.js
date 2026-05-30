import{S as r}from"./index-B3XdImUZ.js";import"./index-0BmjH1qd.js";const t="oitBackBlendPixelShader",e=`var uBackColor: texture_2d<f32>;@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=textureLoad(uBackColor,vec2i(fragmentInputs.position.xy),0);if (fragmentOutputs.color.a==0.0) {discard;}}
`;r.ShadersStoreWGSL[t]||(r.ShadersStoreWGSL[t]=e);const n={name:t,shader:e};export{n as oitBackBlendPixelShaderWGSL};

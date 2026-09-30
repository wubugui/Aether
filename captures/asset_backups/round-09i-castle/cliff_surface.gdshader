shader_type spatial;
render_mode diffuse_lambert,specular_disabled,ambient_light_disabled;
void fragment() {
    vec3 pigment=mix(COLOR.rgb*12.92,1.055*pow(max(COLOR.rgb,vec3(0.)),vec3(1./2.4))-.055,step(vec3(.0031308),COLOR.rgb));
    ALBEDO=mix(COLOR.rgb,pigment,.52);
    EMISSION=ALBEDO*.82;
    ROUGHNESS=1.;
}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.08/PI;
}

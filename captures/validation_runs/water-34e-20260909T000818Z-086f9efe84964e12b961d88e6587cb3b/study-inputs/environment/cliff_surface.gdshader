shader_type spatial;
uniform vec3 study_fill=vec3(1.);
uniform vec3 study_haze=vec3(.40,.53,.65);
render_mode diffuse_lambert,specular_disabled,ambient_light_disabled;
varying vec3 land_position;
void vertex() { land_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz; }
void fragment() {
    vec3 pigment=mix(COLOR.rgb*12.92,1.055*pow(max(COLOR.rgb,vec3(0.)),vec3(1./2.4))-.055,step(vec3(.0031308),COLOR.rgb));
    ALBEDO=mix(COLOR.rgb,pigment,.52);
    float distance_to_camera=distance(INV_VIEW_MATRIX[3].xyz,land_position);
    float low_air=1.-smoothstep(70.,250.,land_position.y);
    float haze=(1.-exp(-max(distance_to_camera-650.,0.)*.00038))*low_air;
    EMISSION=ALBEDO*study_fill*.82*(1.-haze)+study_haze*haze;
    ALBEDO*=1.-haze;
    ROUGHNESS=1.;
}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.08/PI;
}

shader_type spatial;
uniform vec3 study_fill=vec3(1.);
uniform vec3 study_haze=vec3(.40,.53,.65);
render_mode diffuse_lambert,specular_disabled,cull_disabled,ambient_light_disabled;
uniform bool cloth=false;
global uniform float world_time;
void vertex() {
    if(cloth)VERTEX.z+=sin(world_time*2.6+VERTEX.x*2.1)*.10*clamp((VERTEX.x-.95)/1.8,0.,1.);
}
void fragment() {
    ALBEDO=mix(COLOR.rgb*12.92,1.055*pow(max(COLOR.rgb,vec3(0.)),vec3(1./2.4))-.055,step(vec3(.0031308),COLOR.rgb));
    EMISSION=ALBEDO*study_fill*.93;
    ROUGHNESS=1.;
}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.10/PI;
}

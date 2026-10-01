shader_type spatial;
// BEGIN REFLECTION50 CLIP DECLARATIONS
uniform bool lake50_clip_enabled=false;
varying float reflection_world_y50;
// END REFLECTION50 CLIP DECLARATIONS

uniform vec3 scene_fill=vec3(1.);
uniform vec3 scene_haze=vec3(.76,.80,.78);
uniform vec3 scene_sun_direction=vec3(-.48,.82,.30);

render_mode diffuse_lambert,specular_disabled,cull_disabled;
uniform bool cloth=false;
global uniform float world_time;
void vertex() {
    if(cloth)VERTEX.z+=sin(world_time*2.6+VERTEX.x*2.1)*.10*clamp((VERTEX.x-.95)/1.8,0.,1.);

    // BEGIN REFLECTION50 FINAL VERTEX WORLD Y
    reflection_world_y50=(MODEL_MATRIX*vec4(VERTEX,1.0)).y;
    // END REFLECTION50 FINAL VERTEX WORLD Y
}
void fragment() {
    // BEGIN REFLECTION50 CAMERA-ONLY CLIP
    if(lake50_clip_enabled && (CAMERA_VISIBLE_LAYERS & 524288u)!=0u && reflection_world_y50<0.0){discard;}
    // END REFLECTION50 CAMERA-ONLY CLIP

    ALBEDO=mix(COLOR.rgb*12.92,1.055*pow(max(COLOR.rgb,vec3(0.)),vec3(1./2.4))-.055,step(vec3(.0031308),COLOR.rgb));
    EMISSION=vec3(0.);
    ROUGHNESS=1.;



}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)/PI;
}

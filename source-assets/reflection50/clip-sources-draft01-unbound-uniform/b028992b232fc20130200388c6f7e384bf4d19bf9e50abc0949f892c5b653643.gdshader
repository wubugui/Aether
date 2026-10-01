shader_type spatial;
// BEGIN REFLECTION50 CLIP DECLARATIONS
uniform bool reflection_clip50_enabled=false;
varying float reflection_world_y50;
// END REFLECTION50 CLIP DECLARATIONS

uniform vec3 scene_fill=vec3(1.);
uniform vec3 scene_haze=vec3(.76,.80,.78);
uniform vec3 scene_sun_direction=vec3(-.48,.82,.30);

render_mode diffuse_lambert, specular_disabled, cull_disabled;
varying vec3 world_point;
uniform bool cloud_drift=false;
global uniform float world_time;
void vertex() {
    if(cloud_drift)VERTEX.x+=sin(world_time*.018)*9.;
    world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;

    // BEGIN REFLECTION50 FINAL VERTEX WORLD Y
    reflection_world_y50=(MODEL_MATRIX*vec4(VERTEX,1.0)).y;
    // END REFLECTION50 FINAL VERTEX WORLD Y
}
vec3 linear_to_srgb(vec3 c) {
    return mix(c*12.92,1.055*pow(max(c,vec3(0)),vec3(1./2.4))-.055,step(vec3(.0031308),c));
}
void fragment() {
    // BEGIN REFLECTION50 CAMERA-ONLY CLIP
    if(reflection_clip50_enabled && (CAMERA_VISIBLE_LAYERS & 524288u)!=0u && reflection_world_y50<0.0){discard;}
    // END REFLECTION50 CAMERA-ONLY CLIP

    ALBEDO = mix(COLOR.rgb,linear_to_srgb(COLOR.rgb),.30);
    ROUGHNESS=1.;
    // Very restrained world-space grass variation; never uses a source image.
    float grain=sin(world_point.x*.14)*sin(world_point.z*.17)*.012;
    ALBEDO *= 1.+grain;
    // Distance and altitude describe an actual low atmospheric layer. The
    // haze follows the camera during free flight; no screen-space mask or
    // image sampling is involved. The engine adds the thin upper air layer.
    float distance_to_camera=distance(INV_VIEW_MATRIX[3].xyz,world_point);
    float low_air=1.-smoothstep(70.,250.,world_point.y);
    float haze=(1.-exp(-max(distance_to_camera-650.,0.)*.00038))*low_air;
    EMISSION=ALBEDO*.72*(1.-haze)+scene_haze*haze;
    ALBEDO*=1.-haze;

ALBEDO*=mix(vec3(1.),scene_fill,.35);
EMISSION*=scene_fill;
}
void light() {
    DIFFUSE_LIGHT += LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.32/PI;
}

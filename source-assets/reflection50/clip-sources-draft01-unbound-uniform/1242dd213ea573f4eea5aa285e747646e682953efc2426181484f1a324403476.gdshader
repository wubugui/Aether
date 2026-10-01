shader_type spatial;
// BEGIN REFLECTION50 CLIP DECLARATIONS
uniform bool reflection_clip50_enabled=false;
varying float reflection_world_y50;
// END REFLECTION50 CLIP DECLARATIONS

uniform vec3 scene_fill=vec3(1.);
uniform vec3 scene_haze=vec3(.76,.80,.78);
uniform vec3 scene_sun_direction=vec3(-.48,.82,.30);

render_mode unshaded,cull_disabled;
global uniform float world_time;
varying vec3 world_normal;
void vertex(){
    VERTEX.x+=sin(world_time*.018)*9.;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);

    // BEGIN REFLECTION50 FINAL VERTEX WORLD Y
    reflection_world_y50=(MODEL_MATRIX*vec4(VERTEX,1.0)).y;
    // END REFLECTION50 FINAL VERTEX WORLD Y
}
void fragment(){
    // BEGIN REFLECTION50 CAMERA-ONLY CLIP
    if(reflection_clip50_enabled && (CAMERA_VISIBLE_LAYERS & 524288u)!=0u && reflection_world_y50<0.0){discard;}
    // END REFLECTION50 CAMERA-ONLY CLIP

    vec3 n=normalize(world_normal);
    float sunlight=max(dot(n,normalize(scene_sun_direction)),0.);
    float sky_fill=smoothstep(-.70,.65,n.y);
    ALBEDO=mix(vec3(.83,.800,.807),vec3(.98,.950,.930),sky_fill);
    ALBEDO+=(sunlight-.4)*.022;

ALBEDO*=scene_fill;
}

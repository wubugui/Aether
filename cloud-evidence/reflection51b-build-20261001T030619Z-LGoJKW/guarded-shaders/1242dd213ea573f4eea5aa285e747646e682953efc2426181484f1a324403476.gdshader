shader_type spatial;
/* LAKE51_GLOBAL_BEGIN */
varying float lake51_reflection_world_y;
uniform bool lake51_reflection_clip_enabled = true;
uniform float lake51_reflection_plane_y = 0.0;
/* LAKE51_GLOBAL_END */

uniform vec3 scene_fill=vec3(1.);
uniform vec3 scene_haze=vec3(.76,.80,.78);
uniform vec3 scene_sun_direction=vec3(-.48,.82,.30);

render_mode unshaded,cull_disabled;
global uniform float world_time;
varying vec3 world_normal;
void vertex(){
    VERTEX.x+=sin(world_time*.018)*9.;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);

/* LAKE51_VERTEX_BEGIN */
    lake51_reflection_world_y = (MODEL_MATRIX * vec4(VERTEX, 1.0)).y;
/* LAKE51_VERTEX_END */
}
void fragment(){
/* LAKE51_FRAGMENT_BEGIN */
    if (lake51_reflection_clip_enabled && (CAMERA_VISIBLE_LAYERS & 524288u) != 0u && (CAMERA_VISIBLE_LAYERS & 262144u) == 0u && lake51_reflection_world_y < lake51_reflection_plane_y) { discard; }
/* LAKE51_FRAGMENT_END */

    vec3 n=normalize(world_normal);
    float sunlight=max(dot(n,normalize(scene_sun_direction)),0.);
    float sky_fill=smoothstep(-.70,.65,n.y);
    ALBEDO=mix(vec3(.83,.800,.807),vec3(.98,.950,.930),sky_fill);
    ALBEDO+=(sunlight-.4)*.022;

ALBEDO*=scene_fill;
}

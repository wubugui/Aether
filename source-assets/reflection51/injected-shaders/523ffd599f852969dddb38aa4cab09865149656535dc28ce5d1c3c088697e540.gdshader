shader_type spatial;
/* LAKE51_GLOBAL_BEGIN */
varying float lake51_reflection_world_y;
uniform bool lake51_reflection_clip_enabled = true;
uniform float lake51_reflection_plane_y = 0.0;
/* LAKE51_GLOBAL_END */
 render_mode blend_mix,depth_draw_never,cull_disabled; uniform vec3 tint; uniform float precipitation_time=0.; void fragment(){
/* LAKE51_FRAGMENT_BEGIN */
    if (lake51_reflection_clip_enabled && (CAMERA_VISIBLE_LAYERS & 524288u) != 0u && lake51_reflection_world_y < lake51_reflection_plane_y) { discard; }
/* LAKE51_FRAGMENT_END */
float eye_distance=length(VERTEX);float fade=smoothstep(8.,18.,eye_distance);ALBEDO=tint;ROUGHNESS=1.;ALPHA=.48*fade;if(ALPHA<.01)discard;}
/* LAKE51_NEW_VERTEX_BEGIN */
void vertex() {
/* LAKE51_VERTEX_BEGIN */
    lake51_reflection_world_y = (MODEL_MATRIX * vec4(VERTEX, 1.0)).y;
/* LAKE51_VERTEX_END */
}
/* LAKE51_NEW_VERTEX_END */

shader_type spatial;
// BEGIN REFLECTION50 CLIP DECLARATIONS
uniform bool reflection_clip50_enabled=false;
varying float reflection_world_y50;
// END REFLECTION50 CLIP DECLARATIONS
 render_mode blend_mix,depth_draw_never,cull_disabled; uniform vec3 tint; uniform float precipitation_time=0.; void fragment(){
    // BEGIN REFLECTION50 CAMERA-ONLY CLIP
    if(reflection_clip50_enabled && (CAMERA_VISIBLE_LAYERS & 524288u)!=0u && reflection_world_y50<0.0){discard;}
    // END REFLECTION50 CAMERA-ONLY CLIP
float eye_distance=length(VERTEX);float fade=smoothstep(8.,18.,eye_distance);ALBEDO=tint;ROUGHNESS=1.;ALPHA=.48*fade;if(ALPHA<.01)discard;}
void vertex(){
    // BEGIN REFLECTION50 FINAL VERTEX WORLD Y
    reflection_world_y50=(MODEL_MATRIX*vec4(VERTEX,1.0)).y;
    // END REFLECTION50 FINAL VERTEX WORLD Y
}

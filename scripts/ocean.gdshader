shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
varying vec3 world_point;
void vertex() {world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment() {
    float distance_to_camera=length(world_point-CAMERA_POSITION_WORLD);
    float haze=1.-exp(-distance_to_camera*.0008);
    vec3 c=mix(vec3(.27,.53,.68),vec3(.7882,.8784,.9255),haze);
    c+=sin(world_point.x*.017)*sin(world_point.z*.022)*.007;
    ALBEDO=OUTPUT_IS_SRGB?c:pow(c,vec3(2.2));
}

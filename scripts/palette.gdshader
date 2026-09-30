shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
uniform float haze_density = 0.00036;
uniform vec3 haze_color : source_color = vec3(0.74, 0.83, 0.84);
varying vec3 world_position;
void vertex() {
    world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}
vec3 srgb_to_linear(vec3 c) {
    return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}
vec3 linear_to_srgb(vec3 c) {
    return mix(c*12.92,1.055*pow(max(c,vec3(0.0)),vec3(1.0/2.4))-0.055,step(vec3(0.0031308),c));
}
void fragment() {
    float d = length(world_position - CAMERA_POSITION_WORLD);
    float fog = 1.0 - exp(-max(d - 150.0, 0.0) * haze_density);
    vec3 h = vec3(0.745, 0.837, 0.847);
    vec3 c = mix(linear_to_srgb(COLOR.rgb), h, min(fog, 0.96));
    ALBEDO = OUTPUT_IS_SRGB ? c : srgb_to_linear(c);
}

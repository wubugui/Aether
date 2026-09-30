shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
uniform float phase = 0.0;
varying vec3 world_position;
void vertex() { world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
    vec2 p = world_position.xz;
    float wave = sin(p.x * 0.054 + sin(p.y * 0.019) * 2.3 + phase * 0.13) * sin(p.y * 0.31 + phase * 0.1);
    float broad = sin(p.x * 0.013 + p.y * 0.008) * 0.012;
    vec3 c = mix(COLOR.rgb*12.92,1.055*pow(max(COLOR.rgb,vec3(0.0)),vec3(1.0/2.4))-0.055,step(vec3(0.0031308),COLOR.rgb));
    c += wave*0.003;
    float d = length(world_position - CAMERA_POSITION_WORLD);
    float fog = 1.0 - exp(-max(d - 150.0, 0.0) * 0.00036);
    ALBEDO = OUTPUT_IS_SRGB ? c : pow(c, vec3(2.2));
}

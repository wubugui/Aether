shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
varying vec3 local_point;
void vertex() {local_point=VERTEX;}
void fragment() {
    vec3 c=mix(COLOR.rgb*12.92,1.055*pow(max(COLOR.rgb,vec3(0.0)),vec3(1.0/2.4))-0.055,step(vec3(0.0031308),COLOR.rgb));
    float grain=sin(local_point.x*52.0+sin(local_point.y*81.0)*1.8)*sin(local_point.y*94.0+local_point.x*3.0);
    float plank=fract((local_point.y+4.4)*3.8);
    float joint=1.0-smoothstep(0.015,0.055,min(plank,1.0-plank));
    c*=1.0+grain*.025-joint*.14;
    ALBEDO=OUTPUT_IS_SRGB?c:pow(c,vec3(2.2));
}

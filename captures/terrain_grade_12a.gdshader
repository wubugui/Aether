shader_type spatial;
render_mode diffuse_lambert, specular_disabled, cull_disabled, ambient_light_disabled;
varying vec3 world_point;
uniform bool cloud_drift=false;
global uniform float world_time;
void vertex() {
    if(cloud_drift)VERTEX.x+=sin(world_time*.018)*9.;
    world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
vec3 linear_to_srgb(vec3 c) {
    return mix(c*12.92,1.055*pow(max(c,vec3(0)),vec3(1./2.4))-.055,step(vec3(.0031308),c));
}
void fragment() {
    vec3 pigment=linear_to_srgb(COLOR.rgb);
    float grass=step(pigment.b,min(pigment.r,pigment.g)*.88)*step(3.2,world_point.y);
    float coast=(1.-smoothstep(-40.,-5.,world_point.x))*smoothstep(-370.,-150.,world_point.z)*(1.-smoothstep(100.,220.,world_point.z));
    float west=(1.-smoothstep(-150.,-50.,world_point.x))*smoothstep(-1400.,-1100.,world_point.z)*(1.-smoothstep(0.,200.,world_point.z))*(1.-coast);
    float low=1.-smoothstep(10.,16.,world_point.y);
    vec3 coastal_color=mix(vec3(.87,.925,.95),vec3(.81,.85,.86),low);
    vec3 grade=mix(vec3(1.),vec3(.94,.965,1.04),west);
    grade=mix(grade,coastal_color,coast);
    float fields=smoothstep(-20.,0.,world_point.x)*(1.-smoothstep(60.,100.,world_point.x))*smoothstep(-370.,-270.,world_point.z)*(1.-smoothstep(-160.,-80.,world_point.z));
    grade=mix(grade,vec3(1.06,1.055,1.03),fields);
    pigment*=mix(vec3(1.),grade,grass);
    vec3 painted=mix(pigment/12.92,pow((pigment+.055)/1.055,vec3(2.4)),step(vec3(.04045),pigment));
    ALBEDO = mix(painted,pigment,.30);
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
    EMISSION=ALBEDO*.72*(1.-haze)+vec3(.40,.53,.65)*haze;
    ALBEDO*=1.-haze;
}
void light() {
    DIFFUSE_LIGHT += LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.32/PI;
}

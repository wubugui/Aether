shader_type spatial;
render_mode unshaded,cull_back,fog_disabled;
global uniform float world_time;
varying vec3 world_normal;
varying vec3 world_point;
void vertex(){
    VERTEX.x+=sin(world_time*.018)*9.;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
    world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
void fragment(){
    vec3 n=normalize(world_normal);
    float sunlight=max(dot(n,normalize(vec3(-.48,.82,.30))),0.);
    float sky_fill=smoothstep(-.62,.22,n.y);
    vec3 pigment=mix(vec3(.76,.775,.825),vec3(.939,.932,.916),sky_fill);
    pigment+=(sunlight-.32)*.045;
    // High clouds sit above the dense valley haze. A weak distance layer
    // remains camera-relative during flight, without any screen-space mask.
    float distance_to_camera=distance(INV_VIEW_MATRIX[3].xyz,world_point);
    float haze=1.-exp(-max(distance_to_camera-500.,0.)*.000016);
    ALBEDO=mix(pigment,vec3(.69,.80,.87),haze);
}

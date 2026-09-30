shader_type spatial;
render_mode unshaded,cull_disabled;
global uniform float world_time;
varying vec3 world_normal;
void vertex(){
    VERTEX.x+=sin(world_time*.018)*9.;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
}
void fragment(){
    vec3 n=normalize(world_normal);
    float sunlight=max(dot(n,normalize(vec3(-.48,.82,.30))),0.);
    float sky_fill=smoothstep(-.70,.65,n.y);
    ALBEDO=mix(vec3(.87,.835,.825),vec3(1.,.97,.94),sky_fill);
    ALBEDO+=(sunlight-.4)*.095;
}

shader_type spatial;
render_mode unshaded,cull_disabled;
global uniform float world_time;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
varying vec3 world_normal;
void vertex(){VERTEX.x+=sin(world_time*.018)*9.;world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    vec3 n=normalize(world_normal);
    float sky_fill=smoothstep(-.70,.65,n.y);
    vec3 day=mix(vec3(.83,.800,.807),vec3(.98,.950,.930),sky_fill);
    day+=(max(dot(n,normalize(vec3(-.48,.82,.30))),0.)-.4)*.022;
    float moonlight=max(dot(n,normalize(moon_direction)),0.);
    vec3 night=mix(vec3(.070,.105,.20),vec3(.24,.34,.62),sky_fill*.55+moonlight*.45);
    ALBEDO=mix(day,night,study_night);
}

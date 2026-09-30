shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
global uniform float world_time;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
varying vec3 world_normal;
varying vec3 cloud_world;
void vertex(){
    VERTEX.x+=sin(world_time*.018)*9.;
    world_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);
    cloud_world=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
void fragment(){
    vec3 n=normalize(world_normal);
    float sky_fill=smoothstep(-1.,.72,n.y);
    float direct=max(dot(n,normalize(moon_direction)),0.);
    float transmitted=max(dot(-n,normalize(moon_direction)),0.);
    float light=clamp(.44*sky_fill+.43*direct+.13*transmitted,0.,1.);
    vec3 night=mix(vec3(.105,.165,.34),vec3(.38,.50,.86),light);
    vec3 day=mix(vec3(.70,.76,.83),vec3(.97,.95,.92),sky_fill);
    day+=(max(dot(n,normalize(vec3(-.48,.82,.30))),0.)-.4)*.035;
    // Cloud altitude uses its own sparse haze rather than sea-level dense fog.
    // This is spatial distance attenuation; geometry and normals remain real.
    float haze=1.-exp(-distance(CAMERA_POSITION_WORLD,cloud_world)*.000035);
    vec3 air=mix(vec3(.50,.64,.78),vec3(.025,.065,.18),study_night);
    ALBEDO=mix(mix(day,night,study_night),air,haze);
}

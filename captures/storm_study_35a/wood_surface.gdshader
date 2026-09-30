shader_type spatial;

uniform float storm_flash=0.;
uniform vec3 storm_camera=vec3(-2350.,420.,-1300.);
float storm35_mask(vec3 p){
    float edge=-2350.+150.*sin((p.z+3500.)*.0007);
    return (1.-smoothstep(-450.,450.,p.x-edge))*(1.-smoothstep(5200.,6800.,abs(p.z+3500.)))*smoothstep(-12000.,-10000.,p.x);
}
float storm35_flash(vec3 p){
    float f=0.;
    for(int i=0;i<3;i++){
        vec3 c=vec3(-3450.-float(i)*440.,420.,-4000.-float(i)*1600.);
        f+=exp(-length((p-c)/vec3(1150.,850.,1150.))*1.6);
    }
    return f*storm_flash;
}
float storm35_air(vec3 p){
    vec3 ray=p-storm_camera;float density=0.;
    for(int i=0;i<4;i++){
        vec3 q=storm_camera+ray*((float(i)+.5)/4.);
        density+=storm35_mask(q)*(1.-smoothstep(600.,1600.,q.y));
    }
    return 1.-exp(-length(ray)*.00011*density/4.);
}

uniform vec3 study_fill=vec3(1.);
uniform vec3 study_haze=vec3(.40,.53,.65);
render_mode unshaded, cull_disabled;
varying vec3 local_point;
varying vec3 world_point;
void vertex() {
    world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;local_point=VERTEX;}
void fragment() {
    vec3 c=mix(COLOR.rgb*12.92,1.055*pow(max(COLOR.rgb,vec3(0.0)),vec3(1.0/2.4))-0.055,step(vec3(0.0031308),COLOR.rgb));
    float grain=sin(local_point.x*52.0+sin(local_point.y*81.0)*1.8)*sin(local_point.y*94.0+local_point.x*3.0);
    float plank=fract((local_point.y+4.4)*3.8);
    float joint=1.0-smoothstep(0.015,0.055,min(plank,1.0-plank));
    c*=1.0+grain*.025-joint*.14;
    ALBEDO=(OUTPUT_IS_SRGB?c:pow(c,vec3(2.2)))*study_fill;

    float storm=storm35_mask(world_point);
    float storm_air=storm35_air(world_point);
    EMISSION*=mix(vec3(1.13,.92,.59),vec3(.16,.23,.32),storm);
    ALBEDO*=mix(vec3(1.05,.91,.67),vec3(.45,.52,.63),storm);
    EMISSION+=ALBEDO*vec3(.55,.56,.90)*storm35_flash(world_point)*1.4;
    EMISSION=mix(EMISSION,vec3(.11,.15,.21)+vec3(.22,.21,.32)*storm35_flash(world_point),storm_air);
    ALBEDO*=1.-storm_air;
    ROUGHNESS=mix(ROUGHNESS,.58,storm);

}

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
        vec3 c=vec3(-3450.-float(i)*440.,230.,-4000.-float(i)*1600.);
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
    ALBEDO = mix(COLOR.rgb,linear_to_srgb(COLOR.rgb),.30);
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
    EMISSION=ALBEDO*study_fill*.72*(1.-haze)+study_haze*haze;
    ALBEDO*=1.-haze;

    float storm=storm35_mask(world_point);
    float storm_air=storm35_air(world_point);
    EMISSION*=mix(vec3(1.13,.92,.59),vec3(.16,.23,.32),storm);
    ALBEDO*=mix(vec3(1.05,.91,.67),vec3(.45,.52,.63),storm);
    EMISSION+=ALBEDO*vec3(.55,.56,.90)*storm35_flash(world_point)*1.4;
    EMISSION=mix(EMISSION,vec3(.11,.15,.21)+vec3(.22,.21,.32)*storm35_flash(world_point),storm_air);
    ALBEDO*=1.-storm_air;
    ROUGHNESS=mix(ROUGHNESS,.58,storm);

}
void light() {
    DIFFUSE_LIGHT += LIGHT_COLOR*ATTENUATION*(1.-.90*storm35_mask(world_point))*max(dot(NORMAL,LIGHT),0.)*.32/PI;
}

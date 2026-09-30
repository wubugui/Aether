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
render_mode diffuse_lambert, specular_disabled, cull_disabled, ambient_light_disabled;
varying vec3 world_point;
varying vec3 terrain_normal;
varying flat float meadow_moisture;

vec3 linear_to_srgb(vec3 c) {
    return mix(c*12.92,1.055*pow(max(c,vec3(0)),vec3(1./2.4))-.055,step(vec3(.0031308),c));
}
vec3 srgb_to_linear(vec3 c) {
    return mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));
}
float hash21(vec2 p) {
    return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);
}
float land_noise(vec2 p) {
    vec2 i=floor(p), f=fract(p);
    f=f*f*(3.-2.*f);
    return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
               mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x),f.y);
}
void vertex() {
    world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
    terrain_normal=normalize(mat3(MODEL_MATRIX)*NORMAL);
    float broad=land_noise(world_point.xz/128.+vec2(11.8,-3.6));
    float middle=land_noise(world_point.xz/45.+vec2(-7.3,18.2));
    // Flat interpolation keeps a single biome sample over each actual mesh
    // triangle, taken from its provoking vertex. This is not a centroid
    // bake, additional geometry, or a screen-aligned color mask.
    meadow_moisture=smoothstep(.28,.70,broad*.74+middle*.26);
}
void fragment() {
    vec3 original=linear_to_srgb(COLOR.rgb);
    float grass=smoothstep(.055,.12,min(original.r,original.g)-original.b)
        *smoothstep(3.2,7.,world_point.y);
    vec3 n=normalize(terrain_normal);
    float sheltered=(1.-max(0.,dot(n,normalize(vec3(-.48,.82,.30)))));
    float moisture=clamp(meadow_moisture*.83+sheltered*.20,0.,1.);
    vec3 dry=vec3(.73,.745,.46);
    vec3 meadow=vec3(.46,.565,.345);
    vec3 pigment=mix(dry,meadow,moisture);
    float original_light=clamp(dot(original,vec3(.2126,.7152,.0722))/.69,.78,1.20);
    pigment*=mix(1.,original_light,.70);
    pigment*=.89+.11*max(0.,dot(n,normalize(vec3(-.48,.82,.30))));
    pigment=mix(original,pigment,grass*.72);
    ALBEDO=mix(srgb_to_linear(pigment),pigment,.30);
    ROUGHNESS=1.;
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
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*(1.-.90*storm35_mask(world_point))*max(dot(NORMAL,LIGHT),0.)*.32/PI;
}

shader_type spatial;
render_mode diffuse_lambert,cull_disabled,ambient_light_disabled;
uniform vec4 base_color:source_color=vec4(1.);
uniform sampler2D base_texture:source_color;
uniform bool has_texture=false;
uniform bool use_vertex_color=false;
uniform float base_roughness=1.;
uniform vec3 source_emission=vec3(0.);
varying vec3 native_position;

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

void vertex(){native_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;}
void fragment(){
    vec3 base=base_color.rgb;
    if(has_texture)base*=texture(base_texture,UV).rgb;
    if(use_vertex_color)base*=COLOR.rgb;
    float storm=storm35_mask(native_position);
    float air=storm35_air(native_position);
    ALBEDO=base*mix(vec3(1.,.87,.59),vec3(.45,.52,.63),storm)*(1.-air);
    EMISSION=base*mix(vec3(.65,.55,.35),vec3(.05,.085,.13),storm)+source_emission;
    EMISSION+=base*vec3(.55,.56,.90)*storm35_flash(native_position)*1.4;
    EMISSION=mix(EMISSION,vec3(.11,.15,.21),air);
    ROUGHNESS=mix(base_roughness,.55,storm);
}
void light(){DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*(1.-.9*storm35_mask(native_position))*max(dot(NORMAL,LIGHT),0.)*.35/PI;}

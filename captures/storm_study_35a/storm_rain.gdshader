shader_type spatial;
render_mode unshaded,cull_disabled,depth_draw_never;
global uniform float world_time;
varying vec3 rain_position;

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

void vertex(){
    vec3 p=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
    float top=storm_camera.y+450.;
    float new_y=top-mod(top-p.y+world_time*150.,900.);
    VERTEX.y+=new_y-p.y;
    rain_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
void fragment(){
    float d=distance(storm_camera,rain_position);
    float fade=smoothstep(8.,25.,d)*(1.-smoothstep(450.,720.,d));
    float under_cloud=1.-smoothstep(560.,900.,rain_position.y);
    ALBEDO=vec3(.35,.43,.54)+vec3(.35,.33,.50)*storm35_flash(rain_position);
    ALPHA=.30*storm35_mask(rain_position)*fade*under_cloud;
}

shader_type spatial;
render_mode unshaded,cull_disabled,fog_disabled;
varying vec3 cloud_position;
varying vec3 cloud_normal;

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

void vertex(){cloud_position=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;cloud_normal=normalize(MODEL_NORMAL_MATRIX*NORMAL);}
void fragment(){
    vec3 n=normalize(cloud_normal);
    float underside=smoothstep(-.85,.65,n.y);
    float sunward=max(dot(n,normalize(vec3(.32,.14,-.94))),0.);
    float edge=-2350.+150.*sin((cloud_position.z+3500.)*.0007);
    float edge_light=exp(-max(edge-cloud_position.x,0.)/450.);
    vec3 dark=mix(vec3(.021,.032,.047),vec3(.11,.14,.18),underside);
    vec3 warm=mix(vec3(.20,.16,.125),vec3(.76,.53,.28),sunward*.75+underside*.25);
    vec3 c=mix(dark,warm,edge_light*.86);
    c+=vec3(.38,.36,.59)*storm35_flash(cloud_position);
    float air=1.-exp(-distance(storm_camera,cloud_position)*.000035);
    ALBEDO=mix(c,vec3(.16,.18,.22),air*.65);
}

shader_type sky;

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

void sky(){
    vec3 ray=normalize(EYEDIR);float h=clamp(ray.y,0.,1.);
    vec3 sun=normalize(vec3(.97,.11,-.20));
    float glow=exp(-acos(clamp(dot(ray,sun),-1.,1.))*3.5);
    vec3 clear=mix(vec3(.86,.69,.43),vec3(.26,.39,.53),pow(h,.60));
    clear+=vec3(.42,.26,.07)*glow;
    // Optical coverage integrates the finite world weather along the ray;
    // a clear far endpoint no longer leaks a uniform warm stripe underneath it.
    float optical=0.;
    for(int i=0;i<8;i++){
        float distance_along=(float(i)+.5)*900.;
        optical+=storm35_mask(storm_camera+ray*distance_along);
    }
    float cloud_coverage=1.-exp(-optical*.48);
    vec3 overcast=mix(vec3(.14,.19,.25),vec3(.027,.043,.065),pow(h,.6));
    COLOR=mix(clear,overcast,cloud_coverage*.90);
}

shader_type sky;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
float hash21(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
void sky(){
    vec3 ray=normalize(EYEDIR);float altitude=clamp(ray.y,0.,1.);
    vec3 day=mix(vec3(.815,.905,.940),vec3(.440,.630,.837),pow(clamp(altitude/.33,0.,1.),.85));
    day+=vec3(.13,.12,.07)*pow(max(dot(ray,normalize(vec3(-.48,.82,.30))),0.),96.);
    vec3 night=mix(vec3(.035,.085,.20),vec3(.003,.010,.039),pow(clamp(altitude/.7,0.,1.),.6));
    vec3 moon=normalize(moon_direction);float angle=acos(clamp(dot(ray,moon),-1.,1.));
    float disk=1.-smoothstep(.036,.038,angle);
    vec2 sphere=vec2(atan(ray.z,ray.x)/6.2831853+.5,asin(ray.y)/3.14159265+.5);
    vec2 grid=sphere*vec2(650.,325.);vec2 cell=floor(grid);float seed=hash21(cell);
    vec2 offset=vec2(hash21(cell+23.7),hash21(cell-14.8));
    float star=(1.-smoothstep(.015,.055+.035*seed,length(fract(grid)-offset)))*step(.73,seed)*smoothstep(0.,.16,ray.y);
    night+=vec3(.72,.80,1.)*star;
    night+=vec3(.10,.16,.32)*exp(-angle*25.);
    float facets=.76+.24*hash21(floor(sphere*vec2(2200.,1100.)));
    night=mix(night,vec3(.70,.79,1.)*facets,disk);
    COLOR=mix(day,night,study_night);
}

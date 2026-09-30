shader_type spatial;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
uniform vec3 moon_world_center=vec3(-3933.250977,3478.453369,-9791.308594);
uniform float moon_world_radius=330.;
render_mode diffuse_lambert, cull_disabled, ambient_light_disabled;
varying vec3 world_point;
uniform sampler2D depth_texture : hint_depth_texture, repeat_disable, filter_nearest;
global uniform float world_time;
uniform int emitter_count=0;
uniform vec4 emitter_positions[80];
uniform vec4 emitter_dimensions[80];
uniform vec4 emitter_colors[80];
uniform sampler2D emitter_occlusion : filter_nearest, repeat_disable;
uniform float emitter_reflection_gain=18.;

// A continuous world-space wind field; no repeated two-sine grid mask.
float sea_hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float sea_noise(vec2 p){
    vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f);
    return mix(mix(sea_hash(i),sea_hash(i+vec2(1.,0.)),u.x),
               mix(sea_hash(i+vec2(0.,1.)),sea_hash(i+vec2(1.,1.)),u.x),u.y);
}
float sea_height(vec2 p){
    vec2 wind=normalize(vec2(.83,-.56));
    vec2 q=vec2(dot(p,wind),dot(p,vec2(-wind.y,wind.x)));
    q.y+=world_time*.55;
    float swell=2.4*(sea_noise(q*vec2(.045,.085)+vec2(9.2,3.6))-.5);
    float crest=1.35*(sea_noise(q*vec2(.09,.20)+vec2(2.3,1.7))-.5);
    float small=.15*(sea_noise(q*vec2(.17,.45)+vec2(17.2,5.6))-.5);
    return swell+crest+small;
}
// Shared jittered vertices define a continuous piecewise-planar height field.
// This supplies material normals; the existing sea geometry is still flat.
float sea_cross(vec2 a,vec2 b){return a.x*b.y-a.y*b.x;}
vec2 sea_vertex(vec2 id){
    vec2 offset=vec2(sea_hash(id),sea_hash(id+vec2(71.,19.)))-.5;
    return (id+offset*.45)*vec2(5.5,2.8);
}
bool sea_inside(vec2 p,vec2 a,vec2 b,vec2 c){
    return sea_cross(b-a,p-a)>=-.00001 && sea_cross(c-b,p-b)>=-.00001 && sea_cross(a-c,p-c)>=-.00001;
}
vec3 sea_facet_normal(vec2 p){
    vec2 wind=normalize(vec2(.83,-.56));vec2 across=vec2(-wind.y,wind.x);
    vec2 q=vec2(dot(p,wind),dot(p,across));q.y+=world_time*.55;
    vec2 cell=floor(q/vec2(5.5,2.8));
    vec2 va=vec2(0.);vec2 vb=vec2(1.,0.);vec2 vc=vec2(0.,1.);bool found=false;
    for(int y=-1;y<=1;y++){
        for(int x=-1;x<=1;x++){
            vec2 id=cell+vec2(float(x),float(y));
            vec2 a=sea_vertex(id),b=sea_vertex(id+vec2(1.,0.));
            vec2 c=sea_vertex(id+vec2(1.,1.)),d=sea_vertex(id+vec2(0.,1.));
            if(mod(id.x+id.y,2.)<1.){
                if(!found && sea_inside(q,a,b,c)){va=a;vb=b;vc=c;found=true;}
                if(!found && sea_inside(q,a,c,d)){va=a;vb=c;vc=d;found=true;}
            }else{
                if(!found && sea_inside(q,a,b,d)){va=a;vb=b;vc=d;found=true;}
                if(!found && sea_inside(q,b,c,d)){va=b;vb=c;vc=d;found=true;}
            }
        }
    }
    va.y-=world_time*.55;vb.y-=world_time*.55;vc.y-=world_time*.55;
    vec2 wa=wind*va.x+across*va.y,wb=wind*vb.x+across*vb.y,wc=wind*vc.x+across*vc.y;
    vec3 a3=vec3(wa.x,sea_height(wa),wa.y),b3=vec3(wb.x,sea_height(wb),wb.y),c3=vec3(wc.x,sea_height(wc),wc.y);
    vec3 n=normalize(cross(c3-a3,b3-a3));
    return n.y<0.?-n:n;
}
// Reflection of actual registered emission surfaces, independent of native
// Omni illumination cutoff. Finite static scene occlusion covers450m only.
vec3 local_emission_reflection(vec3 point,vec3 ray,float fresnel){
    vec3 result=vec3(0.);
    for(int i=0;i<80;i++){
        if(i>=emitter_count){break;}
        vec3 to_emitter=emitter_positions[i].xyz-point;
        float distance=length(to_emitter);
        if(distance<=.01 || distance>=450. || to_emitter.y<=0.){continue;}
        vec3 direction=to_emitter/distance;
        float facing=dot(ray,direction);
        if(facing<.90){continue;}
        vec3 horizontal=abs(direction.y)>.999?vec3(1.,0.,0.):normalize(cross(direction,vec3(0.,1.,0.)));
        vec3 vertical=normalize(cross(horizontal,direction));
        vec3 axes=emitter_dimensions[i].xyz;
        float width=dot(abs(horizontal),axes)/distance;
        float height=dot(abs(vertical),axes)/distance;
        float rough=emitter_dimensions[i].w;
        float sx=sqrt(width*width+rough*rough),sy=sqrt(height*height+rough*rough);
        vec2 slope=vec2(dot(ray,horizontal),dot(ray,vertical))/max(facing,.001);
        float coverage=exp(-.5*dot(slope/vec2(sx,sy),slope/vec2(sx,sy)))*(width*height)/(sx*sy);
        if(coverage<.00001){continue;}
        vec3 outgoing=-direction;
        float u=fract(atan(outgoing.z,outgoing.x)/6.28318530718+.5);
        float v=clamp(-outgoing.y,0.,.999999);
        vec2 uv=vec2((floor(u*64.)+.5)/64.,(float(i)*32.+floor(v*32.)+.5)/(32.*float(emitter_count)));
        float hit_distance=textureLod(emitter_occlusion,uv,0.).r*450.;
        float visible=step(distance,hit_distance+.25);
        result+=emitter_colors[i].rgb*emitter_colors[i].a*coverage*visible*max(.04,fresnel)*emitter_reflection_gain;
    }
    return result;
}
void vertex() {
    world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
}
void fragment() {
    float ripple=sin(world_point.x*.031+world_time*.8)*sin(world_point.z*.043-world_time*.6);
    // Compatibility renderer uses OpenGL NDC depth [-1, 1]. Shore color
    // follows the real submerged terrain, from every camera direction.
    float scene_depth=textureLod(depth_texture,SCREEN_UV,0.).r;
    vec4 view_position=INV_PROJECTION_MATRIX*vec4(vec3(SCREEN_UV,scene_depth)*2.-1.,1.);
    view_position/=view_position.w;
    vec3 bottom_world=(INV_VIEW_MATRIX*view_position).xyz;
    float water_depth=max(world_point.y-bottom_world.y,0.);
    vec3 deep=mix(vec3(.170,.418,.627),vec3(.230,.498,.677),ripple*.16+.4);
    vec3 c=mix(vec3(.32,.59,.65),deep,smoothstep(0.,6.,water_depth));
    float foam=(1.-smoothstep(.05,.45,water_depth))*(.45+.15*sin(world_point.x*.2+world_point.z*.3+world_time));
    c=mix(c,vec3(.83,.90,.87),foam);
    ALBEDO=mix(pow(c,vec3(2.2)),c,.60);
    ROUGHNESS=.38;SPECULAR=.3;
    vec3 day_emission=ALBEDO*.82;
    // The moon reflection is computed from the actual surface position,
    // wave normal and view ray. It moves with the observer in the same world.
    vec3 wave_normal=sea_facet_normal(world_point.xz);
    vec3 view_direction=normalize(INV_VIEW_MATRIX[3].xyz-world_point);
    // Finite authored world sphere; actual runtime node values are bound
    // after construction. Each water point has its own incident direction.
    vec3 reflected_ray=reflect(-view_direction,wave_normal);
    vec3 to_moon=moon_world_center-world_point;
    float moon_distance=max(length(to_moon),moon_world_radius+1.);
    vec3 local_moon_direction=to_moon/moon_distance;
    float separation=acos(clamp(dot(reflected_ray,local_moon_direction),-1.,1.));
    float moon_radius=asin(clamp(moon_world_radius/moon_distance,0.,1.));
    float pixel_angle=max(.00015,.65*(length(dFdx(view_direction))+length(dFdy(view_direction))));
    float reflected=1.-smoothstep(moon_radius-pixel_angle,moon_radius+pixel_angle,separation);
    // Micro-rough reflection surrounds a smaller silver core. This is an
    // angular surface response, not a screen-space position/brightness mask.
    float rough_width=.045;
    float outside_disk=max(separation-moon_radius,0.);
    float rough_reflection=exp(-outside_disk*outside_disk/(2.*rough_width*rough_width));
    float rough_peak=(moon_radius*moon_radius)/(moon_radius*moon_radius+rough_width*rough_width);
    vec3 moon_radiance=vec3(.36,.55,.95)*rough_reflection*rough_peak+vec3(.60,.78,1.16)*reflected*.62;
    float broken_wave=.70+.30*sea_noise(world_point.xz*vec2(.035,.055)+vec2(4.,world_time*.08));
    vec3 night_color=mix(vec3(.016,.043,.125),vec3(.030,.080,.215),ripple*.3+.5);
    night_color=mix(night_color,vec3(.065,.095,.15),foam*.6);
    vec3 sky_ray=reflect(-view_direction,wave_normal);
    float fresnel=pow(1.-max(dot(wave_normal,view_direction),0.),3.);
    float sky_height=smoothstep(0.,.85,sky_ray.y);
    // Match the actual open_sky night gradient and halo radiance.
    float sky_altitude=clamp(sky_ray.y,0.,1.);
    vec3 reflected_night_sky=mix(vec3(.065,.14,.30),vec3(.009,.028,.085),pow(clamp(sky_altitude/.7,0.,1.),.6));
    reflected_night_sky+=vec3(.10,.16,.32)*exp(-separation*25.);
    vec3 reflected_day_sky=mix(vec3(.66,.77,.87),vec3(.25,.46,.69),sky_height);
    day_emission=mix(day_emission,reflected_day_sky,.40*fresnel);
    night_color=mix(night_color,reflected_night_sky,.65*fresnel);
    EMISSION=mix(day_emission,night_color+moon_radiance*broken_wave+local_emission_reflection(world_point,reflected_ray,fresnel),study_night);
    ALBEDO=mix(ALBEDO,vec3(.006,.016,.043),study_night);
    NORMAL=normalize((VIEW_MATRIX*vec4(wave_normal,0.)).xyz);
    ALPHA=1.;
}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.18/PI;
}

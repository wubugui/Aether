shader_type spatial;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
render_mode diffuse_lambert, cull_disabled, ambient_light_disabled;
varying vec3 world_point;
uniform sampler2D depth_texture : hint_depth_texture, repeat_disable, filter_nearest;
global uniform float world_time;
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
    float warp=sea_noise(q*vec2(.033,.08))*2.;
    float swell=.24*sin(q.y*.34+warp);
    float crest=.42*(sea_noise(q*vec2(.072,.32)+vec2(2.3,1.7))-.5);
    float small=.13*(sea_noise(q*vec2(.21,.86)+vec2(17.2,5.6))-.5);
    return swell+crest+small;
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
    NORMAL=normalize(NORMAL+vec3(cos(world_point.x*.031+world_time*.8)*.04,cos(world_point.z*.043-world_time*.6)*.04,0));
    ROUGHNESS=.38;SPECULAR=.3;
    vec3 day_emission=ALBEDO*.82;
    // The moon reflection is computed from the actual surface position,
    // wave normal and view ray. It moves with the observer in the same world.
    float e=.18;
    float dx=(sea_height(world_point.xz+vec2(e,0.))-sea_height(world_point.xz-vec2(e,0.)))/(2.*e);
    float dz=(sea_height(world_point.xz+vec2(0.,e))-sea_height(world_point.xz-vec2(0.,e)))/(2.*e);
    vec3 wave_normal=normalize(vec3(-dx,1.,-dz));
    vec3 view_direction=normalize(INV_VIEW_MATRIX[3].xyz-world_point);
    float reflected=pow(max(dot(reflect(-view_direction,wave_normal),normalize(moon_direction)),0.),65.);
    float broken_wave=.45+.55*sea_noise(world_point.xz*vec2(.075,.18)+vec2(4.,world_time*.15));
    vec3 night_color=mix(vec3(.012,.035,.105),vec3(.027,.070,.19),ripple*.3+.5);
    night_color=mix(night_color,vec3(.065,.095,.15),foam*.6);
    EMISSION=mix(day_emission,night_color+vec3(.68,.86,1.30)*reflected*broken_wave,study_night);
    ALBEDO=mix(ALBEDO,vec3(.006,.016,.043),study_night);
    NORMAL=mix(NORMAL,normalize((VIEW_MATRIX*vec4(wave_normal,0.)).xyz),study_night);
    ALPHA=1.;
}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.18/PI;
}

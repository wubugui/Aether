shader_type spatial;
uniform float study_night=0.;
uniform vec3 moon_direction=vec3(-.184,.38,-.907);
render_mode diffuse_lambert, cull_disabled, ambient_light_disabled;
varying vec3 world_point;
uniform sampler2D depth_texture : hint_depth_texture, repeat_disable, filter_nearest;
global uniform float world_time;
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
    vec3 wave_normal=normalize(vec3(cos(world_point.x*.19+world_point.z*.27+world_time*.7)*.105+sin(world_point.x*.71-world_point.z*.43-world_time)*.055,1.,cos(world_point.x*.25+world_point.z*.33-world_time*.85)*.10+sin(world_point.x*.47-world_point.z*.57+world_time)*.05));
    vec3 view_direction=normalize(INV_VIEW_MATRIX[3].xyz-world_point);
    float reflected=pow(max(dot(reflect(-view_direction,wave_normal),normalize(moon_direction)),0.),110.);
    float broken_wave=.38+.62*smoothstep(-.2,.75,sin(world_point.x*.85+world_point.z*1.5+world_time)+.7*sin(world_point.x*1.33-world_point.z*.77-world_time*.6));
    vec3 night_color=mix(vec3(.012,.035,.105),vec3(.027,.070,.19),ripple*.3+.5);
    night_color=mix(night_color,vec3(.065,.095,.15),foam*.6);
    EMISSION=mix(day_emission,night_color+vec3(.43,.57,.94)*reflected*broken_wave,study_night);
    ALBEDO=mix(ALBEDO,vec3(.006,.016,.043),study_night);
    NORMAL=mix(NORMAL,normalize((VIEW_MATRIX*vec4(wave_normal,0.)).xyz),study_night);
    ALPHA=1.;
}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.18/PI;
}

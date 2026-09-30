shader_type spatial;
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
    EMISSION=ALBEDO*.82;
    ALPHA=1.;
}
void light() {
    DIFFUSE_LIGHT+=LIGHT_COLOR*ATTENUATION*max(dot(NORMAL,LIGHT),0.)*.18/PI;
}

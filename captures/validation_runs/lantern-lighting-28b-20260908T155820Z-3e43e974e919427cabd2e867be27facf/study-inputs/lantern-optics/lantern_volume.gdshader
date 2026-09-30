shader_type spatial;
render_mode unshaded,blend_add,cull_front,depth_draw_never,depth_test_disabled,fog_disabled;
uniform sampler2D depth_texture : hint_depth_texture,repeat_disable,filter_nearest;
uniform sampler2D beam_occlusion : repeat_disable,filter_linear;
uniform mat4 beam_to_world;
uniform float volume_kind=0.;
uniform float beam_length=560.;
uniform float start_radius=.8;
uniform float divergence=.09;
uniform float halo_radius=1.45;
uniform vec3 warm_color=vec3(1.,.64,.23);
uniform float light_energy=.65;
varying vec3 local_point;
varying vec3 local_camera;
varying vec3 world_point;
void vertex(){
    local_point=VERTEX;world_point=(MODEL_MATRIX*vec4(VERTEX,1.)).xyz;
    local_camera=(inverse(MODEL_MATRIX)*vec4(CAMERA_POSITION_WORLD,1.)).xyz;
}
void fragment(){
    vec3 ray=normalize(local_point-local_camera);
    float far_radius=start_radius+beam_length*divergence;
    vec3 lower=volume_kind>.5?vec3(-halo_radius):vec3(-far_radius,-far_radius,-beam_length);
    vec3 upper=volume_kind>.5?vec3(halo_radius):vec3(far_radius,far_radius,0.);
    vec3 inv_ray=1./(ray+vec3(.000001));
    vec3 a=(lower-local_camera)*inv_ray,b=(upper-local_camera)*inv_ray;
    vec3 near_axis=min(a,b),far_axis=max(a,b);
    float enter=max(max(near_axis.x,near_axis.y),max(near_axis.z,0.));
    float leave=min(min(far_axis.x,far_axis.y),far_axis.z);
    float depth=textureLod(depth_texture,SCREEN_UV,0.).r;
    vec4 screen_position=INV_PROJECTION_MATRIX*vec4(vec3(SCREEN_UV,depth)*2.-1.,1.);
    screen_position/=screen_position.w;
    vec3 scene_world=(INV_VIEW_MATRIX*screen_position).xyz;
    leave=min(leave,length(scene_world-CAMERA_POSITION_WORLD));
    float step_length=max(leave-enter,0.)/32.;
    float optical_depth=0.;
    for(int i=0;i<32;i++){
        vec3 p=local_camera+ray*(enter+(float(i)+.5)*step_length);
        float density=0.;
        if(volume_kind>.5){
            density=(1.-smoothstep(.05,1.,length(p)/halo_radius))*.55;
        }else{
            float along=-p.z;
            float radius=start_radius+along*divergence;
            float radial=length(p.xy)/max(radius,.001);
            if(along>=0. && along<=beam_length && radial<1.){
                vec2 uv=.5+.5*p.xy*beam_length/(max(along,.5)*far_radius);
                vec2 texel_uv=(clamp(uv,vec2(0.),vec2(1.))*32.+.5)/33.;
                float blocker=textureLod(beam_occlusion,texel_uv,0.).r*beam_length;
                float lit=1.-smoothstep(blocker+.25,blocker+1.25,along);
                float above_sea=smoothstep(-.1,.35,(beam_to_world*vec4(p,1.)).y);
                density=(1.-smoothstep(.70,1.,radial))*exp(-along*.0025)*lit*above_sea*.012;
                density*=smoothstep(0.,2.,along)*(1.-smoothstep(beam_length*.80,beam_length,along));
            }
        }
        optical_depth+=density*step_length;
    }
    ALBEDO=vec3(0.);EMISSION=warm_color*light_energy;
    ALPHA=clamp(1.-exp(-optical_depth),0.,.9);
}

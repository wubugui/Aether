import pathlib,json,hashlib,importlib.util
R=pathlib.Path('/workspace/scratch/a29d03198654/Aether');base=(R/'candidates/round40-exclusive-20260930/project/assets/lake_depth50/lake_water_depth50.gdshader').read_bytes().decode()
spec=importlib.util.spec_from_file_location('clip51',R/'source-assets/reflection51/clip_shader_source.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
head='''\n/* LAKE51_WATER_GLOBAL_BEGIN */
uniform bool lake51_reflection_enabled=false;
uniform float lake51_reflection_strength=.94;
uniform sampler2D lake51_reflection_texture : filter_linear, repeat_disable;
uniform mat4 lake51_reflection_view;
uniform mat4 lake51_reflection_projection;
float lake51_region_weight(vec2 p){
    vec2 a=p-vec2(768.,-2304.);vec2 b=vec2(1536.,-768.)-p;
    return smoothstep(0.,64.,max(0.,min(min(a.x,a.y),min(b.x,b.y))));
}
vec3 lake51_srgb_to_linear(vec3 c){
    return mix(c/12.92,pow((c+vec3(.055))/1.055,vec3(2.4)),step(vec3(.04045),c));
}
/* LAKE51_WATER_GLOBAL_END */
'''
needle='vec3 wave_normal=sea_facet_normal(world_point.xz);';assert base.count(needle)==1
normal='''
    /* LAKE51_CALM_BEGIN */
    if(lake51_reflection_enabled){
        float calm=lake51_region_weight(world_point.xz);
        vec3 fine_normal=normalize(vec3(.002*sin(world_point.x*.047+world_time*.12),1.,.002*cos(world_point.z*.043-world_time*.1)));
        wave_normal=normalize(mix(wave_normal,fine_normal,calm));
        ROUGHNESS=mix(ROUGHNESS,.045,calm);
    }
    /* LAKE51_CALM_END */
'''
finish='''
    /* LAKE51_LIVE_REFLECTION_BEGIN */
    if(lake51_reflection_enabled){
        float lake_weight=lake51_region_weight(world_point.xz);
        vec4 clip_point=lake51_reflection_projection*lake51_reflection_view*vec4(world_point,1.);
        if(lake_weight>0. && clip_point.w>0.){
            vec2 ref_uv=clip_point.xy/clip_point.w*.5+.5;ref_uv.y=1.-ref_uv.y;
            float ref_edge=min(min(ref_uv.x,ref_uv.y),min(1.-ref_uv.x,1.-ref_uv.y));
            if(ref_edge>0.){
                vec3 reflected_color=textureLod(lake51_reflection_texture,ref_uv,0.).rgb;
                // Target Godot4.5 Compatibility computes in sRGB. The offscreen
                // color is sampled directly there; other backends need a new gate.
                if(!OUTPUT_IS_SRGB){reflected_color=lake51_srgb_to_linear(reflected_color);}
                float blend=clamp(lake51_reflection_strength,0.,1.)*lake_weight*smoothstep(0.,.012,ref_edge);
                vec3 mirror_color=reflected_color*vec3(.94,.97,1.);
                EMISSION=mix(EMISSION,mirror_color,blend);
                ALBEDO*=1.-blend;
            }
        }
    }
    /* LAKE51_LIVE_REFLECTION_END */
'''
# function_span returns opening/closing positions in original source.
span=helper.function_span(base,'fragment')
# Find closing brace from the helper's exact tuple shape.

# Helper supplies (opening_brace, closing_brace, masked_body).
close=span[1]
code=base[:close]+finish+base[close:]
code=code.replace('shader_type spatial;','shader_type spatial;'+head,1).replace(needle,needle+normal,1)
assert code.replace(head,'',1).replace(normal,'',1).replace(finish,'',1)==base
out=R/'candidates/round40-exclusive-20260930/project/assets/reflection51/lake_water_reflection51.gdshader';out.write_bytes(code.encode())
h=lambda x:hashlib.sha256(x.encode()).hexdigest()
ledger={'baseline_game50_sha256':'031b39ea75680e98fbed4882507251ec0ebfb3469300f82402891a0137351ff0','base_depth50_shader_sha256':h(base),'reflection51_shader_sha256':h(code),'reverse_remove_exact':True,'global_insertion':head,'normal_insertion':normal,'fragment_tail_insertion':finish,'scope':'Three reversible insertions only. Disabled flag uses complete original Game50 shader. Enabled geographic lake mask changes normals/roughness and mixes the live shared-World3D viewport via world-projective coordinates. Global sea outside bounds remains original. This is candidate source, not visual acceptance.','bounds':[768,-2304,1536,-768],'feather_m':64,'main_camera_transform_changed':False,'reflection_image_source':'Actual SubViewport render texture, never an uploaded/reference image','color_pipeline':'Compatibility OUTPUT_IS_SRGB direct sample; other backends unvalidated','hardware_gpu_acceptance':False,'visual_acceptance':False}
(R/'source-assets/reflection51/water-shader-ledger.json').write_text(json.dumps(ledger,indent=2));print(h(code))

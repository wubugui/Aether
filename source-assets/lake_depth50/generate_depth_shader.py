import json,hashlib,pathlib
R=pathlib.Path('/workspace/scratch/a29d03198654/Aether');data=json.loads((R/'cloud-evidence/reflection50-material-intake/saved49-materials.json').read_text());node=next(r for r in data['meshes'] if r['path'].endswith('/World/Ocean'));base=data['materials'][node['active_materials'][0]]['shader_code']
head='''\n// LAKE_DEPTH50_BEGIN: signed actual-mesh bathymetry; all styling stays original.
uniform bool lake50_depth_enabled=false;
uniform sampler2D lake50_height : filter_linear, repeat_disable;
'''
for i in range(4):head+=f'uniform sampler2D lake50_patch{i} : filter_linear, repeat_disable;\nuniform vec4 lake50_patch_bounds{i};\nuniform vec2 lake50_patch_size{i};\n'
head+='''float lake50_edge_distance(vec2 p,vec4 b){return min(min(p.x-b.x,p.y-b.y),min(b.z-p.x,b.w-p.y));}
float lake50_patch_weight(vec2 p,vec4 b){return smoothstep(0.,8.,max(0.,lake50_edge_distance(p,b)));}
float lake50_vertical_height(vec2 p){
    vec2 grid=p-vec2(768.,-2304.);
    float h=textureLod(lake50_height,(grid+vec2(.5))/vec2(769.,1537.),0.).r;
'''
for i in range(4):head+=f'''    float w{i}=lake50_patch_weight(p,lake50_patch_bounds{i});
    if(w{i}>0.){{
        vec2 uv{i}=((p-lake50_patch_bounds{i}.xy)/.25+vec2(.5))/lake50_patch_size{i};
        h=mix(h,textureLod(lake50_patch{i},uv{i},0.).r,w{i});
    }}
'''
head+='''    return h;
}
// LAKE_DEPTH50_END
'''
needle='float water_depth=max(world_point.y-bottom_world.y,0.);';assert base.count(needle)==1
body='''
    // LAKE_DEPTH50_REPLACE_BEGIN: only this depth input is altered.
    if(lake50_depth_enabled){
        float lake50_edge=lake50_edge_distance(world_point.xz,vec4(768.,-2304.,1536.,-768.));
        if(lake50_edge>0.){
            float lake50_world_depth=max(0.,world_point.y-lake50_vertical_height(world_point.xz));
            water_depth=mix(water_depth,lake50_world_depth,smoothstep(0.,32.,lake50_edge));
        }
    }
    // LAKE_DEPTH50_REPLACE_END
'''
code=base.replace('shader_type spatial;','shader_type spatial;'+head,1).replace(needle,needle+body,1)
assert code.replace(head,'',1).replace(body,'',1)==base
out=R/'candidates/round40-exclusive-20260930/project/assets/lake_depth50/lake_water_depth50.gdshader';out.write_bytes(code.encode())
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
ledger={'baseline_scene_sha256':data['scene_sha'],'original_ocean_shader_sha256':sha(base),'new_shader_sha256':sha(code),'reverse_remove_insertions_exact':True,'inserted_declarations_and_helpers':head,'inserted_depth_assignment':body,'unchanged':'All original render modes, vertex, normals, colors, opacity, lighting, weather, night and emitter equations remain byte-identical outside the two insertions. When depth flag false or outside bounded domain, original depth path is used. No reflection in this candidate.','source_bounds':[768,-2304,1536,-768],'domain_feather_m':32,'patch_feather_m':8,'sampler':'float32 signed height; no source_color; linear/no mipmaps; exact texel-center UV'}
(R/'source-assets/lake_depth50/shader-change-ledger.json').write_text(json.dumps(ledger,indent=2))
print(sha(code))

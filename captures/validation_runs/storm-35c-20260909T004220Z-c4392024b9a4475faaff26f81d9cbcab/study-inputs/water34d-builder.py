from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];O=R/'captures/water_study_34d';assert not O.exists();O.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=R/'captures/validation_runs/water-34c-20260908T235317Z-847760e1994442d085ed8c6e530e5ce9/study-inputs';source=prior/'new-environment27f/open_water.gdshader';s=source.read_text(encoding='utf-8')
s=s.replace('global uniform float world_time;', '''global uniform float world_time;
uniform int emitter_count=0;
uniform vec4 emitter_positions[16];
uniform vec4 emitter_dimensions[16];
uniform vec4 emitter_colors[16];
uniform sampler2D emitter_occlusion : filter_nearest, repeat_disable;
uniform float emitter_reflection_gain=6.;
''')
insert='''// Reflection of actual registered emission surfaces, independent of native
// Omni illumination cutoff. Finite static scene occlusion covers450m only.
vec3 local_emission_reflection(vec3 point,vec3 ray,float fresnel){
    vec3 result=vec3(0.);
    for(int i=0;i<16;i++){
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
'''
s=s.replace('void vertex() {',insert+'void vertex() {')
s=s.replace('night_color+moon_radiance*broken_wave','night_color+moon_radiance*broken_wave+local_emission_reflection(world_point,reflected_ray,fresnel)')
(O/'open_water.gdshader').write_text(s,encoding='utf-8')
a=(prior/'coast_environment_27f.gd').read_text(encoding='utf-8')
a=a.replace('\t\tfor material in material_cache.values():','\t\tvar seen_water_materials:Dictionary={}\n\t\tfor material in material_cache.values():')
needle='\t\t\tif material is ShaderMaterial and material.shader==shader_cache.get("open_water"):';assert needle in a
a=a.replace(needle,needle+'\n\t\t\t\tif seen_water_materials.has(material.get_instance_id()):continue\n\t\t\t\tseen_water_materials[material.get_instance_id()]=true')
a=a.replace('{"moon_node":str(moon.get_path()),','{"material_instance_id":material.get_instance_id(),"moon_node":str(moon.get_path()),')
(O/'coast_environment_27f.gd').write_text(a,encoding='utf-8');shutil.copy2(R/'tools/water_emitter_reflections_34d.gd',O/'water_emitter_reflections_34d.gd');shutil.copy2(__file__,O/'builder.py')
(O/'design-plan.json').write_text(json.dumps(dict(label='34d',source=str(source.relative_to(R)),source_sha256=sha(source),shader_sha256=sha(O/'open_water.gdshader'),adapter_source_sha256=sha(prior/'coast_environment_27f.gd'),adapter_sha256=sha(O/'coast_environment_27f.gd'),emitter_runtime_sha256=sha(O/'water_emitter_reflections_34d.gd'),scope='34c water/moon retained. Reflect actual emission13sources (4tower cores,9village flames), actual world AABB halfaxes and material emission with angular roughness and artistic radiance gain6. Static64x32 lower-hemisphere collision-depth atlas450m finite extent. Original tower coarsecolliders replaced only in queries by actual opaque triangles. Other harbor lights/window emitters and full scene reflections not included. Flat sea geometry unchanged.',production_modified=False,full_reference_accepted=False),indent=2),encoding='utf-8')
d=(R/'tools/render_water_34c.py').read_text(encoding='utf-8').replace('34c','34d').replace("prior=root/'captures/validation_runs/water-34b-20260908T234145Z-bcb3451587f949d8b6faa363cf23622d'", "prior=root/'captures/validation_runs/water-34c-20260908T235317Z-847760e1994442d085ed8c6e530e5ce9'")
needle="   p=frozen/'preview.gd';s=p.read_text(encoding='utf-8')";assert needle in d
d=d.replace(needle,"   shutil.copy2(native/'water_emitter_reflections_34d.gd',frozen/'water_emitter_reflections_34d.gd')\n"+needle+'''
   needle='\\tvar village_report:Dictionary='
   start=s.index(needle)
   s=s[:start]+'\\tvar emitter_adapter=load(directory.path_join("water_emitter_reflections_34d.gd")).new()\\n\\tvar emitter_report:Dictionary=await emitter_adapter.configure(game,adapter,output.get_base_dir(),environment_mode=="night")\\n'+s[start:]
   s=s.replace('\\t\\treport["lantern_lighting"]=lantern_report','\\t\\treport["emitter_reflection"]=emitter_report\\n\\t\\treport["lantern_lighting"]=lantern_report')
''')
needle="    run.stage(mode+'-views'";assert needle in d
d=d.replace(needle,"    if mode=='night':outputs.append(image.parent/'actual-emitter-reflection.json')\n"+needle)
d=d.replace("if mode=='night':require(len(d['environment_study']['water_reflection_bindings'])>0,'Actual moon bindings missing')", "if mode=='night':require(len(d['environment_study']['water_reflection_bindings'])>0 and d['emitter_reflection']['count']==13 and d['emitter_reflection']['rays']==26624,'Actual emitter/moon bindings missing')")
d=d.replace('No local light or scene reflections implemented.','13 actual emission-source approximations with finite static collision occlusion; no full scene reflections.')
p=R/'tools/render_water_34d.py';assert not p.exists();p.write_text(d,encoding='utf-8');print('34d prepared')

"""34e bounded delta over34d; no new physics, GPU or world support scan."""
from pathlib import Path
import json,math,hashlib,struct,ast
import numpy as np
R=Path(__file__).resolve().parents[1]
N=R/'captures/water_study_34e'
RUN=R/'captures/validation_runs/water-34e-20260909T000818Z-086f9efe84964e12b961d88e6587cb3b'
P=R/'captures/validation_runs/water-34d-20260909T000325Z-9d52dcd583c84d04a34254a8eab8e9e3'
F=RUN/'study-inputs'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def txt(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def block(s,a,b):return s[s.index(a):s.index(b,s.index(a))]
def canonical(o):
    if isinstance(o,str):return o.replace('ActualOpaqueReflectionCasters34e','ActualOpaqueReflectionCasters34d')
    if isinstance(o,list):return [canonical(x) for x in o]
    if isinstance(o,dict):return {k:canonical(v) for k,v in o.items()}
    return o
manifest=read(RUN/'manifest.json');plan=read(N/'design-plan.json')
em_path=RUN/'images/actual-emitter-reflection.json';em=read(em_path);oldem=read(P/'images/actual-emitter-reflection.json')
d=read(RUN/'images/night-reference.png.json');oldview=read(P/'images/night-reference.png.json')
oldby={x['light_node']:x for x in oldem['emitters']};newby={x['light_node']:x for x in em['emitters']}
retained=[]
stable_fields=['light_node','light_world_position','omni_energy','omni_range','emitter_center','emitter_half_axes','emission_color','emission_multiplier','actual_surfaces']
for node,a in oldby.items():
    b=newby[node]
    retained.append({'node':node,'old_index':a['index'],'new_index':b['index'],
      'emitter_geometry_material_exact':all(a[k]==b[k] for k in stable_fields),
      '2048_radial_depths_exact':a['occlusion_distances_m']==b['occlusion_distances_m'],
      'hit_records_exact_except_versioned_caster_parent':a['occlusion_hits']==canonical(b['occlusion_hits']),
      'old_roughness':a['angular_roughness'],'new_roughness':b['angular_roughness']})
# Pure GLB decoder imported alone, extended in memory to return indexed vertices.
module=ast.parse(txt(R/'reviews/round-34-local-reflection-intake.py'))
fn=next(x for x in module.body if isinstance(x,ast.FunctionDef) and x.name=='emitter_parts')
source=ast.unparse(fn).replace("found.append({'mesh_path_in_glb':", "found.append({'vertices_xyz':xyz.tolist(),'mesh_path_in_glb':")
exec(source,globals())
asset=emitter_parts(F/'harbor-kit/harbor_lantern.glb',['Harbor lantern flame']);flame=asset['parts'][0];xyz=np.array(flame['vertices_xyz'])
harborlights={x['node']:x for x in d['harbor_study']['lights']}
harborassets={x['node']:x for x in d['harbor_study']['assets'] if x['asset']=='harbor_lantern'}
linear=np.array(flame['emissive_factor']);expected_color=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
added=[]
for node,b in newby.items():
    if node in oldby:continue
    light=harborlights[node];parent=node.rsplit('/',1)[0];a=harborassets[parent.rsplit('/',1)[-1]]
    c,s=math.cos(a['yaw']),math.sin(a['yaw']);rot=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    world=xyz@rot.T+np.array(a['position']);center=(world.min(axis=0)+world.max(axis=0))*.5;axes=(world.max(axis=0)-world.min(axis=0))*.5
    distances=np.array(b['occlusion_distances_m']);rows=b['actual_surfaces']
    added.append({'index':b['index'],'node':node,'source_role':light['role'],
      'same_instance_mesh':len(rows)==1 and rows[0]['mesh'].startswith(parent+'/') and rows[0]['material']==flame['material'] and rows[0]['mesh'].split('/')[-1]==flame['mesh_path_in_glb'].split('/')[-1],
      'same_instance_omni_record':b['light_world_position']==light['position'] and b['omni_energy']==light['energy'] and b['omni_range']==light['range_m'],
      'emitter_center':b['emitter_center'],'actual_half_axes':b['emitter_half_axes'],
      'center_error_m':float(np.max(np.abs(center-b['emitter_center']))),'half_axes_error_m':float(np.max(np.abs(axes-b['emitter_half_axes']))),
      'emission_multiplier':b['emission_multiplier'],'material_multiplier_matches':b['emission_multiplier']==flame['emissive_strength'],
      'emission_color_max_error':float(np.max(np.abs(expected_color-b['emission_color']))),
      'rays':len(distances),'finite_0_to_450':bool(np.isfinite(distances).all() and np.all(distances>=0) and np.all(distances<=450)),
      'hit_record_count':len(b['occlusion_hits']),'source_mesh_surfaces':rows})
shader=txt(N/'open_water.gdshader');oldshader=txt(P/'study-inputs/new-environment27f/open_water.gdshader')
expected_shader=oldshader.replace('[16]','[80]').replace('i<16','i<80').replace('emitter_reflection_gain=6.','emitter_reflection_gain=18.')
runtime=txt(N/'water_emitter_reflections_34e.gd');oldruntime=txt(P/'study-inputs/water_emitter_reflections_34d.gd')
preview=txt(F/'preview.gd')
views=[];bindings=[]
for name in ['night-reference','night-water-near','night-water-shift','night-time18','day-reference']:
    v=read(RUN/'images'/(name+'.png.json'));pv=read(P/'images'/(name+'.png.json'));night=name.startswith('night')
    c={'run':v['run_id']==manifest['run_id'],'shader':v['water_shader_sha256']==sha(N/'open_water.gdshader'),
      'camera':v['camera']==pv['camera'],'time':v['environment_study']['sampled_world_time']==(18 if name=='night-time18' else 0),
      'world_coast':v['world_sha256']==pv['world_sha256'] and v['rightcoast_glb_sha256']==pv['rightcoast_glb_sha256'],
      'placements':v['placements']==pv['placements'],'named_trees':v['headland_study']['trees']==pv['headland_study']['trees']}
    if night:c.update({'emitter_report_sha':v['emitter_reflection']['report_sha256']==sha(em_path),'counts':v['emitter_reflection']['count']==67 and v['emitter_reflection']['rays']==137216,
      'unique_bound_moon_emitter_id':len(v['environment_study']['water_reflection_bindings'])==1 and v['environment_study']['water_reflection_bindings'][0]['material_instance_id']==em['material_instance_ids'][0]})
    views.append({'view':name,'checks':c})
    for key in ['images/'+name+'.png','images/'+name+'.png.json']:
        bindings.append({'path':key,'matches_manifest':sha(RUN/key)==manifest['artifacts'][key]['sha256']})
keys=['images/actual-emitter-reflection.json','study-inputs/new-environment27f/open_water.gdshader','study-inputs/coast_environment_27f.gd','study-inputs/water_emitter_reflections_34e.gd','study-inputs/render_water_34e.py','study-inputs/preview.gd','study-inputs/harbor-kit/harbor_lantern.glb']
for key in keys:bindings.append({'path':key,'sha256':sha(RUN/key),'matches_manifest':sha(RUN/key)==manifest['artifacts'][key]['sha256']})
checks={'source_shader_sha':sha(N/'open_water.gdshader')==plan['shader_sha256'],'native_emitter_runtime_sha':sha(N/'water_emitter_reflections_34e.gd')==plan['emitter_runtime_sha256'],
 'native_frozen_same':sha(N/'open_water.gdshader')==sha(F/'new-environment27f/open_water.gdshader') and sha(N/'water_emitter_reflections_34e.gd')==sha(F/'water_emitter_reflections_34e.gd'),
 'shader_only_array_loop_gain_delta':shader==expected_shader,
 'environment_adapter_unchanged':sha(N/'coast_environment_27f.gd')==sha(P/'study-inputs/coast_environment_27f.gd'),
 'one_configure_call':preview.count('await emitter_adapter.configure(')==1,
 'one_material_instance':em['water_material_bindings']==1 and len(set(em['material_instance_ids']))==1,
 'count_67_unique_13_retained_54_added':len(em['emitters'])==len(newby)==67 and len(retained)==13 and len(added)==54,
 'retained13_geometry_material_exact':all(x['emitter_geometry_material_exact'] for x in retained),
 'retained13_depths_exact':all(x['2048_radial_depths_exact'] for x in retained),
 'retained13_hit_records_equivalent':all(x['hit_records_exact_except_versioned_caster_parent'] for x in retained),
 'added54_same_instance_light_and_mesh':all(x['same_instance_mesh'] and x['same_instance_omni_record'] for x in added),
 'added54_glb_aabb_within_1mm':all(max(x['center_error_m'],x['half_axes_error_m'])<.001 for x in added),
 'added54_source_emission_matches':all(x['material_multiplier_matches'] and x['emission_color_max_error']<1e-5 for x in added),
 'ray_counts_and_range':em['rays']==137216 and sum(len(x['occlusion_distances_m']) for x in em['emitters'])==137216 and all(x['rays']==2048 and x['finite_0_to_450'] for x in added),
 '4_opaque_proxy_records_inherited':canonical(em['actual_opaque_tower_colliders'])==oldem['actual_opaque_tower_colliders'],
 'exclusion_records_unchanged':em['excluded_original_colliders']==oldem['excluded_original_colliders'],
 'ray_generation_code_unchanged':block(runtime,'\tvar image:=','\tvar texture:=')==block(oldruntime,'\tvar image:=','\tvar texture:='),
 'shader_450m_hard_zero_inherited':'distance>=450.' in shader,
 'actual_harbor_lights_existing_before_this_change':d['harbor_study']['lights']==oldview['harbor_study']['lights'],
 'views_identity':all(all(x['checks'].values()) for x in views),'bindings':all(x['matches_manifest'] for x in bindings),
 'terminal_passed':manifest['status']=='passed' and manifest['passed'] and all(x['exit_code']==0 for x in manifest['stages'])}
report={'scope':'34e bounded increment; reads56.8MB source report but emits compact fields only. No new physics/GPU/Blender or world-support scan.',
 'checks':checks,'bounded_incremental_checks_passed':all(checks.values()),'retained13':retained,'added54':added,
 'source_report':{'path':str(em_path),'bytes':em_path.stat().st_size,'sha256':sha(em_path)},
 'art_parameters':{'tower_angular_roughness':.024,'lantern_angular_roughness':.006,'radiance_gain':18.,'physical_calibration':False},
 'inheritance':{'34d_opaque_mesh_samples':'Four proxy records unchanged except versioned parent path; inherit34d actual GLB3628tri and12hit sample checks; not repeated.',
  'retained_atlas':'Compare by actual source node. Depth arrays exact; hit records normalize only the versioned caster parent name. Indices do not define source identity.',
  'added_atlas_limit':'Existing54*2048 depth counts/finiteness/range and unchanged generation code checked; no independent full137216-ray world intersection replay or GPU texture readback.',
  'land':'33f full支承 inherited; actual identities/placements only compared.',
  'not_scene_reflection':'WorldAABB angular proxies plus finite nearest64x32 static visibility, 0.25m bias and450m hard coverage boundary retained. No windows or full-scene reflection.'},
 'runtime':{'run_id':manifest['run_id'],'status':manifest['status'],'completed_utc':manifest.get('completed_utc'),
  'views':views,'bindings':bindings,'water_material_ids':em['material_instance_ids'],
  'stage_exit_codes':[{x['name']:x['exit_code']} for x in manifest['stages']]},
 'full_reference_accepted':False,'all_reference_goal_complete':False}
(R/'reviews/34e-water-independent-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'pass':report['bounded_incremental_checks_passed'],'checks':checks,'max_added_aabb_error_m':max(max(x['center_error_m'],x['half_axes_error_m']) for x in added),'source_report_bytes':em_path.stat().st_size,'completed_utc':manifest.get('completed_utc')},indent=2))

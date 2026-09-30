"""Read saved GLBs, source and existing radial hits; no new scene/ray/GPU run."""
from pathlib import Path
import json,math,hashlib,struct,ast
import numpy as np
R=Path(__file__).resolve().parents[1]
N=R/'captures/water_study_34d'
RUN=R/'captures/validation_runs/water-34d-20260909T000325Z-9d52dcd583c84d04a34254a8eab8e9e3'
P=R/'captures/validation_runs/water-34c-20260908T235317Z-847760e1994442d085ed8c6e530e5ce9'
F=RUN/'study-inputs'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def txt(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def block(s,a,b):return s[s.index(a):s.index(b,s.index(a))]
# Import ONLY the bounded pure GLB decoder function, never execute prior report scripts.
module=ast.parse(txt(R/'reviews/round-34-local-reflection-intake.py'))
fn=next(x for x in module.body if isinstance(x,ast.FunctionDef) and x.name=='emitter_parts')
source=ast.unparse(fn).replace("found.append({'mesh_path_in_glb':", "found.append({'vertices_xyz':xyz.tolist(),'triangle_count':len(ix)//3,'mesh_path_in_glb':")
exec(source,globals())
em=read(RUN/'images/actual-emitter-reflection.json');d=read(RUN/'images/night-reference.png.json')
plan=read(N/'design-plan.json');manifest=read(RUN/'manifest.json')
tower=emitter_parts(R/'assets/models/lighthouse.glb',[''])
lantern=emitter_parts(F/'harbor-kit/harbor_lantern.glb',['Harbor lantern flame'])
core=next(x for x in tower['parts'] if x['material']=='Lamp core')
flame=lantern['parts'][0]
expected_opaque=[x for x in tower['parts'] if x['alpha_mode']=='OPAQUE' and 'Lamp core' not in x['material'] and 'glass' not in x['material'].lower()]
def rotation(y):
    c=math.cos(y);s=math.sin(y);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
foot_by_node={x['node']:x for x in d['headland_study']['assets']}
placements={x['island']:x for x in d['placements'] if x['kind']=='lighthouse'}
sizes=[];radial=[]
for e in em['emitters']:
    if 'NativeLanternLight' in e['light_node']:
        island=e['light_node'].split('Lighthouse_')[1].split('/')[0];p=placements[island]
        xyz=np.array(core['vertices_xyz'])@rotation(p['yaw']).T+np.array(p['position'])
        expected_multiplier=6.;expected_color=np.array([1,.58,.16])
    else:
        node=e['light_node'].split('/MainlandVillage23g/')[1].split('/')[0];p=foot_by_node[node]
        offset=np.array([-2.7 if p['asset']!='quay_workshop' else -3.9,0,4.8 if p['asset']=='fisher_cottage' else (4.5 if p['asset']=='quay_workshop' else 6.8)])
        xyz=(np.array(flame['vertices_xyz'])+offset)@rotation(p['yaw']).T+np.array(p['position'])
        expected_multiplier=flame['emissive_strength'];linear=np.array(flame['emissive_factor'])
        expected_color=np.where(linear<=.0031308,12.92*linear,1.055*linear**(1/2.4)-.055)
    center=(xyz.min(axis=0)+xyz.max(axis=0))/2;axes=(xyz.max(axis=0)-xyz.min(axis=0))/2
    sizes.append({'index':e['index'],'node':e['light_node'],'center_max_error_m':float(np.max(np.abs(center-np.array(e['emitter_center'])))),
      'half_axes_max_error_m':float(np.max(np.abs(axes-np.array(e['emitter_half_axes'])))),
      'actual_half_axes':e['emitter_half_axes'],'multiplier_correct':e['emission_multiplier']==expected_multiplier,
      'color_max_error':float(np.max(np.abs(expected_color-np.array(e['emission_color'])))),
      'color_note':'Village glTF linear emissiveFactor converted to Godot Color sRGB representation; raw stored value comparison, not full render-output photometry.'})
    distances=e['occlusion_distances_m'];assert len(distances)==2048
    bycell={};maxdistance=0.;maxangle=0.;reindex_errors=0;blocked_counts={};examples=[]
    for hit in e['occlusion_hits']:
        x,y=hit['x'],hit['y'];assert (x,y) not in bycell;bycell[(x,y)]=hit
        vec=np.array(hit['position'])-np.array(e['emitter_center']);length=float(np.linalg.norm(vec));unit=vec/length
        az=((x+.5)/64-.5)*2*math.pi;down=(y+.5)/32;side=math.sqrt(1-down*down)
        direction=np.array([math.cos(az)*side,-down,math.sin(az)*side])
        maxangle=max(maxangle,math.degrees(math.acos(float(np.clip(unit@direction,-1,1)))))
        maxdistance=max(maxdistance,abs(length-hit['distance_m']),abs(distances[y*64+x]-hit['distance_m']))
        # Shader indexes negative incident-to-emitter direction = emitted ray.
        u=(math.atan2(direction[2],direction[0])/(2*math.pi)+.5)%1;v=min(max(-direction[1],0),.999999)
        reindex_errors+=int(math.floor(u*64)!=x or math.floor(v*32)!=y)
        blocked_counts[hit['collider']]=blocked_counts.get(hit['collider'],0)+1
        if len(examples)<2 or ('OpaqueReflectionCaster' in hit['collider'] and not any('OpaqueReflectionCaster' in z['collider'] for z in examples)):
            examples.append(hit)
    nohit_bad=sum(1 for y in range(32) for x in range(64) if (x,y) not in bycell and distances[y*64+x]!=450.)
    radial.append({'index':e['index'],'ray_count':len(distances),'hits':len(bycell),'no_hit_sentinel_count':2048-len(bycell),
      'bad_no_hit_sentinel':nohit_bad,'max_reported_distance_error_m':maxdistance,'max_reported_hit_direction_error_degrees':maxangle,
      'generator_to_shader_texel_mismatch':reindex_errors,'distance_minmax_m':[min(distances),max(distances)],
      'collider_counts':blocked_counts,'examples':examples})
opaque=[]
for o in em['actual_opaque_tower_colliders']:
    expected={(x['mesh_path_in_glb'].split('/')[-1],x['material']) for x in expected_opaque}
    actual={(x['mesh'].split('/')[-1],x['material']) for x in o['surfaces']}
    opaque.append({'tower':o['tower'],'body':o['body'],'actual_triangles':o['triangles'],
      'independent_glb_expected_triangles':sum(x['triangle_count'] for x in expected_opaque),
      'surface_set_matches':actual==expected,'surfaces':len(actual)})
shader=txt(N/'open_water.gdshader');oldshader=txt(P/'study-inputs/new-environment27f/open_water.gdshader')
views=[];bindings=[]
for name in ['night-reference','night-water-near','night-water-shift','night-time18','day-reference']:
    path=RUN/'images'/(name+'.png.json')
    if not path.exists():continue
    v=read(path);pv=read(P/'images'/(name+'.png.json'));night=name.startswith('night')
    c={'run_id':v['run_id']==manifest['run_id'],'shader_sha':v['water_shader_sha256']==sha(N/'open_water.gdshader'),
      'camera_unchanged':v['camera']==pv['camera'],'time':v['environment_study']['sampled_world_time']==(18 if name=='night-time18' else 0),
      'world_sha':v['world_sha256']==pv['world_sha256'],'coast_sha':v['rightcoast_glb_sha256']==pv['rightcoast_glb_sha256'],
      'placements':v['placements']==pv['placements'],'named_trees':v['headland_study']['trees']==pv['headland_study']['trees']}
    if night:c.update({'emitter_report_sha':v['emitter_reflection']['report_sha256']==sha(RUN/'images/actual-emitter-reflection.json'),
      'counts':v['emitter_reflection']['count']==13 and v['emitter_reflection']['rays']==26624,
      'one_moon_material_id_matches_emitter_material':len(v['environment_study']['water_reflection_bindings'])==1 and v['environment_study']['water_reflection_bindings'][0]['material_instance_id']==em['material_instance_ids'][0]})
    views.append({'view':name,'checks':c})
    for key in ['images/'+name+'.png','images/'+name+'.png.json']:
        bindings.append({'path':key,'matches_manifest':key in manifest['artifacts'] and sha(RUN/key)==manifest['artifacts'][key]['sha256']})
for name in ['open_water.gdshader','coast_environment_27f.gd','water_emitter_reflections_34d.gd']:
    frozen=F/('new-environment27f/'+name if name=='open_water.gdshader' else name)
    bindings.append({'path':str(frozen.relative_to(RUN)),'same_as_native':sha(frozen)==sha(N/name),
      'matches_manifest':sha(frozen)==manifest['artifacts'][frozen.relative_to(RUN).as_posix()]['sha256']})
checks={'emitter_count':len(em['emitters'])==13,'rays':em['rays']==26624,
 'one_unique_water_material':em['water_material_bindings']==1 and len(set(em['material_instance_ids']))==1,
 'aabb_centers_and_axes_within_1mm':all(max(x['center_max_error_m'],x['half_axes_max_error_m'])<.001 for x in sizes),
 'actual_emission_matches':all(x['multiplier_correct'] and x['color_max_error']<1e-5 for x in sizes),
 'four_actual_opaque_tower_sets_and_triangle_counts':len(opaque)==4 and all(x['surface_set_matches'] and x['actual_triangles']==x['independent_glb_expected_triangles'] for x in opaque),
 'excluded_exact_sea_and_four_original_towers':len(em['excluded_original_colliders'])==5 and '/root/Skyfarer/World/Ocean/SeaCollision' in em['excluded_original_colliders'],
 'no_hit_is_450m':all(x['bad_no_hit_sentinel']==0 for x in radial),
 'radial_distances_consistent_1mm':all(x['max_reported_distance_error_m']<.001 for x in radial),
 'radial_direction_consistent_0_05deg':all(x['max_reported_hit_direction_error_degrees']<.05 for x in radial),
 'shader_lookup_matches_generator':all(x['generator_to_shader_texel_mismatch']==0 for x in radial),
 'no_excluded_colliders_in_hits':all(not set(x['collider_counts'])&set(em['excluded_original_colliders']) for x in radial),
 'flat_wave_and_grid_inherited':block(shader,'float sea_hash','// Reflection of actual registered')==block(oldshader,'float sea_hash','void vertex()'),
 'out_of_range_hard_zero_present':'distance>=450.' in shader,
 'views_complete_identity':len(views)==5 and all(all(x['checks'].values()) for x in views),
 'selected_binding_identity':all(x['matches_manifest'] and x.get('same_as_native',True) for x in bindings),
 'run_terminal_passed':manifest['status']=='passed' and manifest['passed']}
report={'scope':'34d bounded independent saved-source/GLB/existing-ray-record audit; no new scene queries or GPU.',
 'checks':checks,'bounded_technical_checks_passed':all(checks.values()),
 'run_status':manifest['status'],'shader_sha256':sha(N/'open_water.gdshader'),'adapter_sha256':sha(N/'water_emitter_reflections_34d.gd'),
 'emitter_geometry':sizes,'opaque_tower_source_verification':opaque,'existing_radial_records':radial,
 'material_deduplication':{'actual_count':em['water_material_bindings'],'instance_ids':em['material_instance_ids'],'fixes_34c_repeated_cache_value_count':True},
 'sampling':{'map':[64,32],'rays':26624,'hemisphere':'Uniform azimuth and down=-direction.y (cosine of zenith), not uniform elevation angles.',
  'generator':'az=((x+.5)/64-.5)*TAU, down=(y+.5)/32, dir=(cos(az)*sqrt(1-down²),-down,sin(az)*sqrt(1-down²))',
  'shader_inverse':'outgoing=-direction_to_emitter; u=fract(atan(outgoing.z,outgoing.x)/TAU+.5), v=-outgoing.y, nearest texel center in 13-row-block atlas.',
  'far_m':450,'out_of_range':'distance>=450 returns zero; inside uses actual radial depth plus0.25m bias.',
  'coverage_limit':'Nearest angular cell is an approximation; no new physics raycasts here. Self-/thin-occluder visibility at arbitrary unsampled water points is not proven.'},
 'emission_model_limits':['WorldAABB projection uses dot(abs(basis),half_axes), the support extent of a box, not exact luminous mesh silhouette. Yaw is reflected in measured world AABB but object-oriented shape is not retained.',
  'Gaussian angular lobe with energy-spread ratio and gain6 is authored reflection approximation; not exact BRDF or calibrated emitted radiance.',
  'Registered Godot material Color values are copied into vec4 uniforms. Raw source agreement does not independently validate renderer color-space/radiance conversion.',
  'Opaque mesh caster lists/counts match actual GLB selection; runtime report does not serialize final collision face coordinates, so exact engine collider triangle identity is not proven solely by counts.',
  'Only13 selected emitting surfaces, not every harbor lantern/window, scene reflection or moving occluder coverage.',
  'Temporary caster bodies use reflection layer1<<20 and collision_mask0, but query layer membership is not a security boundary: any unrelated query mask containing that bit could see them. No gameplay query behavior was tested.'],
 'runtime':{'run_id':manifest['run_id'],'completed_utc':manifest.get('completed_utc'),'views':views,'bindings':bindings},
 'full_reference_accepted':False,'all_reference_goal_complete':False}
(R/'reviews/34d-water-independent-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'checks':checks,'status':manifest['status'],'max_aabb_error_m':max(max(x['center_max_error_m'],x['half_axes_max_error_m']) for x in sizes),'max_hit_direction_error_deg':max(x['max_reported_hit_direction_error_degrees'] for x in radial),'opaque':opaque},indent=2))

"""Bounded 34c source/binding/runtime review. No engine or grid resampling."""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1]
N=R/'captures/water_study_34c'
RUN=R/'captures/validation_runs/water-34c-20260908T235317Z-847760e1994442d085ed8c6e530e5ce9'
P=R/'captures/validation_runs/water-34b-20260908T234145Z-bcb3451587f949d8b6faa363cf23622d'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def txt(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def block(s,a,b):return s[s.index(a):s.index(b,s.index(a))]
plan=read(N/'design-plan.json');s=txt(N/'open_water.gdshader');old=txt(R/plan['source']);adapter=txt(N/'coast_environment_27f.gd')
manifest=read(RUN/'manifest.json');revision=read(RUN/'actual-water-revision.json')
views=[];bindings=[];centers=[]
for row in revision['views']:
    name=row['view'];p=RUN/'images'/(name+'.png.json');d=read(p);prior=read(P/'images'/(name+'.png.json'))
    b=d['environment_study']['water_reflection_bindings'];night=name.startswith('night')
    moon=next((x for x in d['environment_study']['native_sky_assets'] if x['asset']=='moon'),None)
    check={'same_run':d['run_id']==manifest['run_id'],'source_shader':d['water_shader_sha256']==sha(N/'open_water.gdshader'),
      'same_camera_as_34b':d['camera']==prior['camera'],'time':d['environment_study']['sampled_world_time']==(18. if name=='night-time18' else 0.),
      'world_sha':d['world_sha256']==prior['world_sha256'],'coast_sha':d['rightcoast_glb_sha256']==prior['rightcoast_glb_sha256'],
      'placements':d['placements']==prior['placements'],'named_trees':d['headland_study']['trees']==prior['headland_study']['trees'],
      'binding_record_count':len(b)==(2 if night else 0),
      'night_bound_center_radius_equal_actual_moon_record':all(x['center']==moon['position'] and x['radius_m']==moon['radius_m']==330. for x in b) if night else True}
    if night:centers.append(moon['position'])
    views.append({'view':name,'camera':d['camera'],'time':d['environment_study']['sampled_world_time'],'checks':check,'actual_water_binding_records':b,
      'water_source_material_records':[x for x in d['environment_study']['material_bindings'] if x['candidate_shader']=='open_water.gdshader']})
    for key in ['images/'+name+'.png','images/'+name+'.png.json']:
        bindings.append({'path':key,'sha256':sha(RUN/key),'matches_manifest':sha(RUN/key)==manifest['artifacts'][key]['sha256']})
for key in ['study-inputs/new-environment27f/open_water.gdshader','study-inputs/coast_environment_27f.gd','study-inputs/water34c-builder.py','study-inputs/water34c-design-plan.json','study-inputs/render_water_34c.py','study-inputs/new-environment27f/open_sky.gdshader']:
    bindings.append({'path':key,'sha256':sha(RUN/key),'matches_manifest':sha(RUN/key)==manifest['artifacts'][key]['sha256']})
checks={'source_parent_sha':sha(R/plan['source'])==plan['source_sha256'],
 'source_shader_sha':sha(N/'open_water.gdshader')==plan['shader_sha256'],
 'adapter_source_sha':sha(P/'study-inputs/coast_environment_27f.gd')==plan['adapter_source_sha256'],
 'adapter_sha':sha(N/'coast_environment_27f.gd')==plan['adapter_sha256'],
 'frozen_shader_and_adapter_same_native':sha(RUN/'study-inputs/new-environment27f/open_water.gdshader')==sha(N/'open_water.gdshader') and sha(RUN/'study-inputs/coast_environment_27f.gd')==sha(N/'coast_environment_27f.gd'),
 'complete_shared_facet_and_height_code_unchanged':block(s,'float sea_hash','void fragment()')==block(old,'float sea_hash','void fragment()'),
 'shore_depth_color_foam_unchanged':block(s,'    float scene_depth=','    ALBEDO=')==block(old,'    float scene_depth=','    ALBEDO='),
 'old_dead_normal_assignment_removed':'NORMAL=normalize(NORMAL+' not in s,
 'binding_uses_actual_global_position':'set_shader_parameter("moon_world_center",moon.global_position)' in adapter,
 'per_point_direction_implemented':'vec3 to_moon=moon_world_center-world_point;' in s and 'vec3 local_moon_direction=to_moon/moon_distance;' in s,
 'per_point_asin_radius_implemented':'asin(clamp(moon_world_radius/moon_distance,0.,1.))' in s,
 'finite_clamp_inactive_on_current_ocean':all(c[1]>331. for c in centers),
 'runtime_terminal_passed':manifest['status']=='passed' and manifest['passed'],
 'all_stage_exit_zero':all(x['exit_code']==0 for x in manifest['stages']),
 'runtime_identity_and_binding_records_pass':all(all(v['checks'].values()) for v in views),
 'sixteen_selected_bindings_match':all(x['matches_manifest'] for x in bindings)}
report={'scope':'34c source, actual moon bindings and five terminal view records; no GPU/Blender, grid or land scan.',
 'checks':checks,'bounded_technical_checks_passed':all(checks.values()),
 'shader_sha256':sha(N/'open_water.gdshader'),'adapter_sha256':sha(N/'coast_environment_27f.gd'),
 'finite_sphere_fix':{'old_34b_fixed_direction_radius_replaced':True,'actual_center':centers[0],
  'radius_m':330.,'radius_source':'Authored330m radius bound by adapter, not derived from mesh bounds in this review.',
  'per_surface_point_outside_sphere_correct':True,
  'clamp_limit':'max(distance,radius+1) makes to_moon/moon_distance non-unit inside331m. Current Y=0 sea is at least3478.453m vertically below center, so guard is inactive.',
  'not_proven':'Reflections of moon faceted surface shading, cloud occultation, solid world visibility, or physical BRDF integration.'},
 'binding_evidence':{'records_each_night':2,'distinct_material_instances_proven':False,'source_material_records_each_night':1,
  'actual_source_material':'res://scenes/environment/Ocean.tscn::ShaderMaterial_sqy22',
  'cache_alias_mechanism':'configure adapts material_override then get_active_material(surface). adapted(new candidate) caches that same candidate under its own ID after prior old-ID -> candidate entry. material_cache.values() can contain same object twice; repeated identical binding rows are not proof of two distinct materials.',
  'missing_fields':['material_instance_id','receiver_node_path'],
  'recommended_next_logging':'Deduplicate by material.get_instance_id(); record associated actual receiver paths and bound center/radius. Do not rerun GPU solely to strengthen this count.'},
 'rough_blue_layer':{'rough_width_radians':.045,'rough_width_degrees':math.degrees(.045),
  'model':'exp(-max(separation-angular_radius,0)^2/(2*width^2)) times radius²/(radius²+width²), plus0.62 silver disk term.',
  'numerical':'Width fixed positive, peak denominator positive for finite positive-radius scene, acos/asin inputs clamped; no new singularity in current ocean domain.',
  'limits':'Authored angular shoulder and approximate peak compensation, not normalized physical microfacet convolution or measured moon radiance. No new derivative handling of facet boundary jumps.'},
 'sky':{'night_vertical_gradient_matches_actual_open_sky_formula':True,
  'halo_coefficients_match':True,'halo_direction_exact_match':False,
  'halo_difference':'Water uses local finite-moon separation; open_sky uses fixed moon_direction. Stars are not copied; daytime sky gradient still differs.',
  'actual_scene_reflection':False,'scope':'Analytic gradient and analytic halo, not a sampled rendered sky/cubemap, clouds, island or building reflection.'},
 'actual_ocean_source_correction':{'path':'scenes/environment/Ocean.tscn','size_m':[100000,100000],'collision_child':'SeaCollision','collision_layer':5,
  'context':'Runtime material record identifies this actual saved Ocean scene. scripts/open_world.gd make_ocean() is older unused creation code; its Sea level collision name must not be used for actual exclusion.'},
 'runtime':{'run_id':manifest['run_id'],'status':manifest['status'],'completed_utc':manifest.get('completed_utc'),
  'stages':[{'name':x['name'],'exit_code':x['exit_code']} for x in manifest['stages']],
  'error_log_bytes':{n:(RUN/n).stat().st_size for n in ['night-views-error.log','day-views-error.log']},'views':views,'selected_bindings':bindings,
  'land_support':'33f inherited; only unchanged actual records compared.'},
 'art_assessed':False,'full_reference_accepted':False,'all_reference_goal_complete':False}
(R/'reviews/34c-water-independent-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'passed':report['bounded_technical_checks_passed'],'checks':checks,'completed':manifest.get('completed_utc')},indent=2))

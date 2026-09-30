"""34b incremental source and existing runtime identity only; no CPU grid rescan."""
from pathlib import Path
import hashlib,json,math
import numpy as np
R=Path(__file__).resolve().parents[1]
N=R/'captures/water_study_34b'
RUN=R/'captures/validation_runs/water-34b-20260908T234145Z-bcb3451587f949d8b6faa363cf23622d'
P=R/'captures/validation_runs/water-34a-20260908T233808Z-05bd651c68574ef79ba9b59ab98506bb'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(p):return p.read_text(encoding='utf-8-sig')
plan=read(N/'design-plan.json');s=text(N/'open_water.gdshader');old=text(R/plan['source'])
def block(x,a,b):return x[x.index(a):x.index(b,x.index(a))]
# Confirm the entire new shader is explained by these parameter/block changes.
expected=old
for a,b in [('vec2(6.5,4.5)','vec2(5.5,2.8)'),('.95*(sea_noise(q*vec2(.028,.055)','2.4*(sea_noise(q*vec2(.045,.085)'),('.48*(sea_noise(q*vec2(.065,.12)','1.35*(sea_noise(q*vec2(.09,.20)'),('.09*(sea_noise(q*vec2(.14,.24)','.15*(sea_noise(q*vec2(.17,.45)'),('float broken_wave=.38+.62*sea_noise','float broken_wave=.70+.30*sea_noise')]:
    assert a in expected;expected=expected.replace(a,b)
expected=expected.replace(block(expected,'    // Finite pixel footprint','    float broken_wave='),block(s,'    // Reflect the actual finite330m','    float broken_wave='))
manifest=read(RUN/'manifest.json');revision=read(RUN/'actual-water-revision.json')
prior=read(P/'images/night-reference.png.json');views=[];bindings=[]
for row in revision['views']:
    name=row['view'];d=read(RUN/'images'/(name+'.png.json'));oldview=read(P/'images'/(name+'.png.json'))
    check={'run_id':d['run_id']==manifest['run_id'],'shader_sha':d['water_shader_sha256']==sha(N/'open_water.gdshader'),
      'same_camera_as_34a':d['camera']==oldview['camera'],
      'actual_time':d['environment_study']['sampled_world_time']==(18. if name=='night-time18' else 0.),
      'world_sha':d['world_sha256']==prior['world_sha256'],
      'coast_sha':d['rightcoast_glb_sha256']==prior['rightcoast_glb_sha256'],
      'placements':d['placements']==prior['placements'],'named_trees':d['headland_study']['trees']==prior['headland_study']['trees']}
    views.append({'view':name,'camera':d['camera'],'time':d['environment_study']['sampled_world_time'],'checks':check})
    for key in ['images/'+name+'.png','images/'+name+'.png.json']:
        bindings.append({'path':key,'sha256':sha(RUN/key),'matches_manifest':sha(RUN/key)==manifest['artifacts'][key]['sha256']})
for key in ['study-inputs/new-environment27f/open_water.gdshader','study-inputs/water34b-builder.py','study-inputs/water34b-design-plan.json','study-inputs/render_water_34b.py']:
    bindings.append({'path':key,'sha256':sha(RUN/key),'matches_manifest':sha(RUN/key)==manifest['artifacts'][key]['sha256']})
d=read(RUN/'images/night-reference.png.json');env=d['environment_study']
moon=next(x for x in env['native_sky_assets'] if x['asset']=='moon')
center=np.array(moon['position']);direction=np.array(env['moon_direction']);direction/=np.linalg.norm(direction)
angular=[]
for q in [[-2278,0,-1632],[-2400,0,-1900],[-3000,0,-2400]]:
    v=center-np.array(q);distance=float(np.linalg.norm(v));v/=distance
    angular.append({'analytic_test_point_godot':q,'distance_to_recorded_center_m':distance,
      'direction_error_degrees':math.degrees(math.acos(float(np.clip(v@direction,-1,1)))),
      'true_sphere_angular_radius_degrees':math.degrees(math.asin(330/distance))})
checks={'source_parent_sha':sha(R/plan['source'])==plan['source_sha256'],
 'source_shader_sha':sha(N/'open_water.gdshader')==plan['shader_sha256'],
 'frozen_shader_identity':sha(RUN/'study-inputs/new-environment27f/open_water.gdshader')==sha(N/'open_water.gdshader'),
 'entire_shader_explained_by_stated_delta':s==expected,
 'depth_color_foam_unchanged':block(s,'    float scene_depth=','    ALBEDO=')==block(old,'    float scene_depth=','    ALBEDO='),
 'vertex_function_unchanged':block(s,'void vertex()', 'void fragment()')==block(old,'void vertex()', 'void fragment()'),
 'runtime_terminal_passed':manifest['status']=='passed' and manifest['passed'],
 'all_stage_exit_zero':all(x['exit_code']==0 for x in manifest['stages']),
 'runtime_records_consistent':all(all(x['checks'].values()) for x in views),
 'selected_bindings_match':all(x['matches_manifest'] for x in bindings)}
report={'scope':'34b incremental source and terminal runtime review; no repeated grid sampling, engine, Blender or land support checks.',
 'shader_sha256':sha(N/'open_water.gdshader'),'source_parent_sha256':plan['source_sha256'],
 'checks':checks,'incremental_identity_checks_passed':all(checks.values()),
 'delta':{'cell_m':[5.5,2.8],'jitter_fraction':.45,'max_grid_offset_m':[1.2375,.63],
  'height_amplitudes':[2.4,1.35,.15],'frequencies':[[.045,.085],[.09,.20],[.17,.45]],
  'analytic_height_bound_m':[-1.95,1.95],'height_geometry_displaced':False,
  'broken_wave_range':[.70,1.0],
  'triangle_twice_area_lower_bound_exact_arithmetic_m2':(.55*.55-.45*.45)*5.5*2.8,
  'shared_field':'Integer vertex IDs and neighbor/parity logic unchanged; shared C0 height, discontinuous facet normals. 34a sample counts do not apply to the changed 34b field; no grid sample rerun.'},
 'moon_reflection':{'finite_sphere_reflection_correct':False,
  'implementation':'Fixed moon_direction, separation=acos(clamp(dot(reflected_ray,moon_direction),-1,1)); radius=atan(330/9000).',
  'fixed_radius_degrees':math.degrees(math.atan(330/9000)),
  'true_sphere_radius_at_reference_distance_degrees':math.degrees(math.asin(330/9000)),
  'actual_runtime_moon_record':moon,'analytic_comparison_points':angular,
  'point_scope':'Analytic diagnostic points at Y=0, not screenshot ray hits or measured sea surface samples.',
  'required_model':'Use center-world_point direction and asin(radius/distance) for each actual surface point outside sphere; account for material-normal-only flat water separately.',
  'source_comment_overstates':'Comment says reflect actual finite sphere, but no world moon center/distance enters this shader.'},
 'disk_filter':{'pixel_angle_floor_rad':.00015,'formula':'.65*(length(dFdx(view_direction))+length(dFdy(view_direction))) with positive floor',
  'numerical':'acos argument clamped; positive angular width gives ordered smoothstep edges and bounded 0..1 reflected mask for finite rays.',
  'limit':'View-ray derivatives filter disk rim within one facet but omit normal jumps and multi-facet pixel coverage. No temporal anti-aliasing or flicker guarantee.'},
 'inherited_limits':['Flat geometry/collision/silhouette, unchanged screen-space depth method.',
  'Analytic sky color only; no actual cloud/shore/object reflection or local-light specular reflection. Local diffuse lighting still exists.',
  'Old sinusoidal NORMAL assignment remains overwritten by final facet NORMAL.'],
 'runtime':{'run_id':manifest['run_id'],'status':manifest['status'],'completed_utc':manifest.get('completed_utc'),
  'stages':[{'name':x['name'],'exit_code':x['exit_code']} for x in manifest['stages']],
  'error_log_bytes':{n:(RUN/n).stat().st_size for n in ['night-views-error.log','day-views-error.log']},
  'views':views,'selected_bindings':bindings,'land_support':'Inherited33f, not rescanned.'},
 'art_assessed_by_this_report':False,'full_reference_accepted':False,'all_reference_goal_complete':False}
(R/'reviews/34b-water-independent-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'identity_passed':report['incremental_identity_checks_passed'],'checks':checks,'moon_comparison':angular,'completed':manifest.get('completed_utc')},indent=2))

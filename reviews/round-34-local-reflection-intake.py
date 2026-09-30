"""Read-only extraction of nine final village lamps and four tower origins."""
from pathlib import Path
import json,hashlib,math,struct
import numpy as np
R=Path(__file__).resolve().parents[1]
RUN=R/'captures/validation_runs/water-34b-20260908T234145Z-bcb3451587f949d8b6faa363cf23622d'
PRIOR=R/'captures/validation_runs/rightcoast-33f-20260908T233517Z-9aac3867c5f340208c238c9e2b83fc1e'
F=RUN/'study-inputs'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=read(RUN/'images/night-reference.png.json');old=read(PRIOR/'images/night-reference.png.json')
sources=['headland_runtime_23g.gd','coast_environment_27f.gd','lantern_lighting_28h.gd','preview.gd','new-environment27f/open_water.gdshader']
manifest=read(RUN/'manifest.json')
bindings=[{'path':str(F/x),'sha256':sha(F/x),'matches_manifest':sha(F/x)==manifest['artifacts']['study-inputs/'+x]['sha256']} for x in sources]
village=[]
assert len(d['headland_study']['lights'])==9
houses=[x for x in d['headland_study']['assets'] if x['asset']!='mainland_headland']
assert len(houses)==9
for lamp,house in zip(d['headland_study']['lights'],houses):
    h=lamp['position'][1];rad=11.
    village.append({'house':lamp['house'],'world_position_godot':lamp['position'],'energy':lamp['energy'],
      'range_m':rad,'range_provenance':'Frozen headland_runtime_23g.gd configure line32; report omits range.',
      'color_srgb':[1,.47,.12],'omni_attenuation':1.3,
      'node_path_reconstructed':'/root/Skyfarer/MainlandVillage23g/'+house['node']+'/VillageLantern/VillageWarmLight',
      'node_path_provenance':'Reconstructed from actual house node name plus frozen child names, not a final full-tree dump.',
      'sea_plane_y':0,'height_above_sea_m':h,
      'omni_sphere_intersects_sea_plane':h<rad,
      'sea_plane_intersection_radius_m':math.sqrt(max(0,rad*rad-h*h)),
      'sphere_intersection_is_not_visible_water_or_shadow_proof':True,
      'shadow_enabled':'not explicitly set in frozen source; no final runtime property captured'})
towers=[]
assert len(d['lantern_lighting']['beams'])==4
for beam,early in zip(d['lantern_lighting']['beams'],d['environment_study']['local_light_records']):
    pos=beam['position'];h=pos[1];rad=beam['omni_range']
    pitch=math.asin(-beam['direction'][1]);half=math.radians(beam['spot_angle'])
    towers.append({'tower':beam['tower'],'omni_node':beam['tower']+'/NativeLanternLight',
      'spot_node':beam['tower']+'/NativeLanternSpot','world_position_godot':pos,
      'height_above_sea_m':h,'omni_energy':beam['omni_energy'],'omni_range_m':rad,
      'omni_color_srgb':[1,.48,.12],'omni_attenuation':1.5,'omni_shadow_enabled':True,
      'omni_shadow_provenance':'Frozen final configure line74; final report explicitly captures range/energy.',
      'omni_sphere_intersects_sea_plane':h<rad,
      'spot_energy':beam['spot_energy'],'spot_range_m':beam['length_m'],
      'spot_color_srgb':[1,.62,.20],'spot_attenuation':.65,'spot_half_angle_degrees':beam['spot_angle'],
      'spot_shadows':beam['spot_shadows'],'spot_direction':beam['direction'],
      'nearest_ideal_cone_sea_distance_m':h/math.sin(pitch+half),
      'spot_cone_can_reach_infinite_sea_plane_ignoring_occlusion':h/math.sin(pitch+half)<beam['length_m'],
      'early_environment_record_superseded':{'energy':early['energy'],'range_m':early['range_m']}})
checks={'selected_frozen_source_bindings_match':all(x['matches_manifest'] for x in bindings),
 'nine_lamps_runtime_exact_33f':d['headland_study']['lights']==old['headland_study']['lights'],
 'four_final_beam_records_exact_33f':d['lantern_lighting']['beams']==old['lantern_lighting']['beams'],
 'four_lamp_positions_equal_early_records':all(b['position']==a['position'] for b,a in zip(d['lantern_lighting']['beams'],d['environment_study']['local_light_records']))}
def emitter_parts(path,needles):
    raw=path.read_bytes();offset=12;doc=None;binary=None
    while offset<len(raw):
        size,kind=struct.unpack_from('<II',raw,offset);chunk=raw[offset+8:offset+8+size];offset+=8+size
        if kind==0x4e4f534a:doc=json.loads(chunk)
        elif kind==0x004e4942:binary=chunk
    def acc(index):
        a=doc['accessors'][index];bv=doc['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC3':3}[a['type']]
        typ={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];item=np.dtype(typ).itemsize
        return np.ndarray((a['count'],n),dtype=typ,buffer=binary,offset=bv.get('byteOffset',0)+a.get('byteOffset',0),strides=(bv.get('byteStride',item*n),item)).copy()
    def local(n):
        if 'matrix' in n:return np.array(n['matrix']).reshape(4,4,order='F')
        x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4)
        m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
    found=[]
    def visit(i,parent,names):
        node=doc['nodes'][i];m=parent@local(node);names=names+[node.get('name',str(i))]
        if 'mesh' in node:
            for si,p in enumerate(doc['meshes'][node['mesh']]['primitives']):
                mat=doc.get('materials',[])[p['material']];name=mat.get('name','')
                if not any(word.lower() in name.lower() for word in needles):continue
                xyz=acc(p['attributes']['POSITION']);ix=acc(p['indices']).ravel() if 'indices' in p else np.arange(len(xyz));xyz=xyz[np.unique(ix)]
                xyz=(np.column_stack([xyz,np.ones(len(xyz))])@m.T)[:,:3]
                lo=xyz.min(axis=0);hi=xyz.max(axis=0);c=(lo+hi)/2
                found.append({'mesh_path_in_glb':'/'.join(names),'primitive':si,'material':name,'asset_local_godot_aabb_min':lo.tolist(),'asset_local_godot_aabb_max':hi.tolist(),'center':c.tolist(),'size_m':(hi-lo).tolist(),'bounding_vertex_radius_m':float(np.linalg.norm(xyz-c,axis=1).max()),'emissive_factor':mat.get('emissiveFactor',[0,0,0]),'emissive_strength':mat.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1),'alpha_mode':mat.get('alphaMode','OPAQUE')})
        for child in node.get('children',[]):visit(child,m,names)
    for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,np.eye(4),[])
    return {'source':str(path),'sha256':sha(path),'parts':found}
tower_emitter=emitter_parts(R/'assets/models/lighthouse.glb',['Lamp core','Clear optical lens glass','Clear slightly amber lantern glass'])
village_emitter=emitter_parts(F/'harbor-kit/harbor_lantern.glb',['Harbor lantern flame'])
checks['actual_tower_asset_matches_runtime_sha']=tower_emitter['sha256']==d['lighthouse_sha256']
checks['actual_village_lantern_matches_frozen_binding']=village_emitter['sha256']==manifest['artifacts']['study-inputs/harbor-kit/harbor_lantern.glb']['sha256']
report={'scope':'Nine reference-coast village lamps and four tower origins only; read-only frozen sources/reports. Four tower spots recorded as colocated additional lights. No live engine tree interrogation or GPU.',
 'coordinates':'Godot world XYZ in metres; sea at Y=0 per scripts/open_world.gd make_ocean()/WorldBoundaryShape3D.',
 'run_id':d['run_id'],'prior_run_id':old['run_id'],'checks':checks,'sources':bindings,
 'village_lamps':village,'tower_lamps':towers,
 'actual_emitting_mesh_bounds':{'tower':tower_emitter,'village':village_emitter,
  'scope':'Read actual GLB indexed primitive vertices with all node transforms in asset-local Godot axes. Vertex-bounding radius is a conservative proxy, not a measured spherical emitter or permission to enlarge it.',
  'tower_final_material_overrides':[{k:x[k] for k in ['mesh','surface','source_name','energy','alpha','transparency']} for x in d['lantern_lighting']['lamp_materials'] if 'Lamp core' in x['source_name']],
  'photometry_limit':'Omni light energy is a scene light parameter, not emissive surface radiance. Final tower opaque core emission multiplier6 differs from Omni energy4; use material radiance/geometry when approximating visible emitter.'},
 'count_summary':{'village_omni':9,'tower_omni':4,'additional_colocated_tower_spot':4,
   'village_omni_spheres_reaching_sea_plane':sum(x['omni_sphere_intersects_sea_plane'] for x in village),
   'tower_omni_spheres_reaching_sea_plane':sum(x['omni_sphere_intersects_sea_plane'] for x in towers)},
 'current_light_path':{'custom_light':'DIFFUSE_LIGHT += LIGHT_COLOR * ATTENUATION * max(dot(NORMAL,LIGHT),0.) * .18 / PI;',
  'custom_specular_contribution':False,'native_light_path_sufficient_for_all_requested_warm_reflections':False,
  'reason':'Direct specular retains native light range, attenuation, spotlight cone, culling and shadow restrictions; emitting surface visibility/reflection has no Omni range cutoff.',
  'single_ocean_mesh_size_m':[100000,100000],'ocean_source':str(R/'scripts/open_world.gd'),
  'compatibility_default_omni_per_object':8,'project_override_found':False,
  'limit_scope':'Documented default and no matching override in project.godot; actual selected per-draw light list was not captured.'},
 'recommended_implementation':[
  {'phase':'Native direct specular','action':'Add a bounded dielectric specular term to light(), gated to non-directional lights to avoid duplicating analytic moon. Use existing view-space NORMAL/LIGHT/VIEW, SPECULAR_AMOUNT, LIGHT_COLOR and ATTENUATION once; preserve current diffuse.',
   'capability':'Local point/spot highlights wherever actual light volume and visibility allow. Existing sea-plane-reaching village spheres and tower spots are possible, not guaranteed visible.',
   'cannot':'Restore missing high tower/lamp-emitter reflections outside light range or reconstruct emitting geometry.'},
  {'phase':'Actual emitting-surface reflection preferred for complete image','action':'A bounded coast planar reflection SubViewport with the same World3D and mirrored camera about Y=0, sea excluded to prevent recursion, appropriate above-water clipping, actual emissive meshes and solid occluders included. Project into water; use normal distortion only as an explicitly approximate departure from a flat mirror. Keep depth/coverage fallback at view edges and avoid double adding analytic sky/moon.',
   'capability':'Can reflect the visible luminous lamp core/lantern surface even outside its Omni cutoff and include terrain/building occlusion.',
   'cost_limit':'Additional rendering, clipping/cull-layer work, transparent emitters and normal-distortion limitations require a bounded actual implementation; not implemented or performance measured here.'},
  {'phase':'Lower-cost interim emitter approximation','action':'Derive an emitter registry from these final nodes plus actual luminous mesh dimensions/material radiance, not Omni range. At each water point use world center/distance and finite angular extent against reflected ray. Supply actual light-to-water visibility from bounded world-space occlusion sampling; do not reuse outside-range ATTENUATION or silently pass through terrain.',
   'capability':'World-anchored warm emitter highlights across view changes without altering ground illumination.',
   'cannot':'Called an actual full-scene reflection or use user-camera visibility as light-to-water visibility. A center/radius proxy omits lamp housing silhouette, exact emissive shape and dynamic occlusion.'}],
 'alternative_probe':'Godot4.5 Compatibility supports at most two reflection probes per mesh. A local probe with actual emissive geometry can provide coarse static reflections but finite-position parallax and one huge ocean mesh limit fidelity; not an automatic drop-in precise mirror.',
 'proposed_34d_occlusion_atlas_limits':{'proposed_grid':[64,32],'hemisphere':'downward','far_m':450,
  'requirements':['Store actual radial nearest collision depth from each final emitter center; compare water distance in the same world frame, with explicit angular interpolation and depth bias.',
   'Exclude the infinite Sea level collision by exact node/RID. Exclude only emitting optical housing deliberately made transmissive; do not exclude entire tower pedestal or island which physically hides water.',
   'If the tower has a single broad collision shape for the whole lighthouse, excluding it is broader than optical housing and must be recorded or replaced with optical-aware collider sampling.',
   'No-hit must be an explicit far sentinel. Water beyond450m is unverified occlusion; apply a documented coverage limit/fade rather than silently marking clear.',
   'Downward hemisphere applies only to water below emitters. Seam/pole wrapping and filter interpolation cannot guarantee narrow-object visibility at64x32.',
   'Static masks must invalidate on moved source or moved occluder; collision visibility is not identical to alpha/transmission of the rendered geometry.'],
  'not_run_or_accepted':True},
 'required_next_evidence':['Final runtime list of every actual emitter/light node after all adapters, including range/color/energy/shadow/layer and emitting mesh bounds.',
  'One light-off comparison distinguishes source-bound contribution; direct-light range-off and emitter visibility-off must have different effects.',
  'Camera move and source move must move the reflection geometrically; an occluder test must suppress it; retain night/day identity.',
  'For native route, record rendering/limits/opengl/max_lights_per_object and selected receiver partitioning; default full-ocean mesh cannot promise all17 local lights.'],
 'official_sources':[
  {'url':'https://docs.godotengine.org/en/4.5/tutorials/shaders/shader_reference/spatial_shader.html','supports':'View-space LIGHT/VIEW/NORMAL, SPECULAR_LIGHT and ATTENUATION distance/shadow; fragment material/transparent limitations.'},
  {'url':'https://docs.godotengine.org/en/4.5/classes/class_omnilight3d.html','supports':'Hard range cutoff, compatibility default8Omni per mesh and AABB requirement.'},
  {'url':'https://docs.godotengine.org/en/4.5/tutorials/3d/global_illumination/reflection_probes.html','supports':'Probe behavior, box projection and Compatibility two-probe per mesh limit.'},
  {'url':'https://docs.godotengine.org/en/4.5/classes/class_environment.html','supports':'Built-in SSR is Forward+ only, not current Compatibility.'}],
 'implementation_changed':False,'full_reference_accepted':False,'all_reference_goal_complete':False}
(R/'reviews/round-34-local-reflection-intake.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'checks':checks,'counts':report['count_summary'],'village_sea_radii':[(x['house'],x['sea_plane_intersection_radius_m']) for x in village],'tower_spot_min_distance':[(x['tower'],x['nearest_ideal_cone_sea_distance_m']) for x in towers]},indent=2))

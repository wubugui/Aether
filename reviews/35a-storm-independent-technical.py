"""Bounded read-only 35a asset/source/sidecar checks; writes only this review's JSON."""
from pathlib import Path
import json, hashlib, struct, math, re
from collections import Counter
import numpy as np

R=Path(__file__).resolve().parents[1]
RUN=R/'captures/validation_runs/storm-35a-20260909T003123Z-b7154d45310e4e2482e9aff200346918'
PRIOR=R/'captures/validation_runs/water-34e-20260909T000818Z-086f9efe84964e12b961d88e6587cb3b'
S=R/'captures/storm_study_35a'; N=R/'captures/storm_cloud_assets_35a'; F=RUN/'study-inputs'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def txt(p):return p.read_text(encoding='utf-8-sig')
def glb_parts(p):
    raw=p.read_bytes(); assert raw[:4]==b'glTF'
    length,kind=struct.unpack_from('<II',raw,12); assert kind==0x4e4f534a
    g=json.loads(raw[20:20+length]); off=20+length
    blen,bkind=struct.unpack_from('<II',raw,off); assert bkind==0x004e4942
    b=raw[off+8:off+8+blen]
    def acc(i):
        a=g['accessors'][i]; v=g['bufferViews'][a['bufferView']]
        dtype={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
        n={'SCALAR':1,'VEC3':3}[a['type']]; item=np.dtype(dtype).itemsize
        return np.ndarray((a['count'],n),dtype,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*item),item)).copy()
    result=[]
    for node in g['nodes']:
        assert not any(k in node for k in ['matrix','translation','rotation','scale']), 'Unexpected transform requires explicit decoding'
        if 'mesh' not in node:continue
        triangles=[]
        for primitive in g['meshes'][node['mesh']]['primitives']:
            assert primitive.get('mode',4)==4
            v=acc(primitive['attributes']['POSITION']).astype(float)
            ix=acc(primitive['indices']).ravel().astype(int)
            triangles.extend(v[ix.reshape(-1,3)])
        t=np.asarray(triangles)
        # Split export normals/materials are welded by exact float32 coordinates.
        vertices,ix=np.unique(t.reshape(-1,3),axis=0,return_inverse=True); ix=ix.reshape(-1,3)
        edges=Counter(); oriented=Counter()
        for face in ix:
            for a,c in zip(face,np.roll(face,-1)):
                edges[tuple(sorted((int(a),int(c))))]+=1; oriented[int(a),int(c)]+=1
        adjacency=[set() for _ in vertices]
        for a,c in edges:adjacency[a].add(c);adjacency[c].add(a)
        seen=set(); stack=[0]
        while stack:
            a=stack.pop()
            if a in seen:continue
            seen.add(a);stack.extend(adjacency[a]-seen)
        area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
        volume=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6
        result.append(dict(name=node['name'],unique_position_vertices=len(vertices),triangles=len(t),edges=len(edges),euler=len(vertices)-len(edges)+len(t),closed_edges=all(c==2 for c in edges.values()),opposite_edge_orientation=all(oriented[a,c]==oriented[c,a]==1 for a,c in edges),single_component=len(seen)==len(vertices),minimum_triangle_area_m2=float(area.min()),signed_volume_m3=float(volume),godot_local_bounds=[vertices.min(axis=0).tolist(),vertices.max(axis=0).tolist()]))
    return result

model=read(N/'model-report.json'); assets=[]
for a in model['assets']:
    name=a['asset']; parts=glb_parts(N/(name+'.glb'))
    native={p['name']:p for p in a['parts']}
    for p in parts:
        original=native[p['name']]
        p['native_record_vertices_match']=p['unique_position_vertices']==original['vertices']
        p['native_volume_relative_delta']=abs(p['signed_volume_m3']-original['signed_volume_m3'])/original['signed_volume_m3']
    hashes={ext:sha(N/(name+ext)) for ext in ['.blend','.glb']}
    assets.append(dict(asset=name,parts=parts,sha256=hashes,hashes_match_native_record=hashes['.blend']==a['blend_sha256'] and hashes['.glb']==a['glb_sha256'],prepared_and_frozen_identical=all(hashes[e]==sha(S/'cloud-assets'/(name+e))==sha(F/'storm35a/cloud-assets'/(name+e)) for e in hashes)))
plan=read(S/'design-plan.json'); manifest=read(RUN/'manifest.json')
source_checks=[]
for name,h in plan['files_sha256'].items():
    source_checks.append(dict(file=name,sha256=sha(S/name),matches_design=sha(S/name)==h,frozen_same=sha(S/name)==sha(F/'storm35a'/name)))
source_checks.append(dict(file='blender/model_storm_clouds_35a.py',sha256=sha(R/'blender/model_storm_clouds_35a.py'),matches_saved_builder=sha(R/'blender/model_storm_clouds_35a.py')==sha(N/'builder.py')))
environment_shader_copies={p.name:sha(p)==sha(F/'new-environment27f'/p.name) for p in S.glob('*.gdshader') if (F/'new-environment27f'/p.name).exists()}
common=txt(S/'storm_common.gdshaderinc').strip()
common_files=[p.name for p in S.glob('*.gdshader') if 'storm35_mask' in txt(p)]
common_same={name:common in txt(S/name) for name in common_files}
def body(source,token):
    start=source.index(token); a=source.index('{',start); d=1;i=a+1
    while d:
        d+=(source[i]=='{')-(source[i]=='}');i+=1
    return source[a+1:i-1]
gd=txt(S/'storm_front_35a.gd')
gdmask=gd.split('func mask_at',1)[1].split('func adapt',1)[0]
gdexpr=gdmask.split('return ',1)[1].strip()
glslexpr=body(common,'float storm35_mask').split('return ',1)[1].strip().rstrip(';')
gdexpr=gdexpr.replace('absf','abs')
mask_expression_same=re.sub(r'\s+','',gdexpr)==re.sub(r'\s+','',glslexpr)
def smooth(a,b,x):
    v=max(0,min(1,(x-a)/(b-a)));return v*v*(3-2*v)
def mask(p):
    x,y,z=p;edge=-2350+150*math.sin((z+3500)*.0007)
    return (1-smooth(-450,450,x-edge))*(1-smooth(5200,6800,abs(z+3500)))*smooth(-12000,-10000,x)

old=read(PRIOR/'images/day-reference.png.json'); views=[]
names=['storm-high','storm-coast-low','storm-inside','storm-edge','storm-clear','storm-flash','storm-cloud-back']
retained_fields=['world_sha256','rightcoast_glb_sha256','island_a_glb_sha256','island_c_glb_sha256','lighthouse_sha256','placements']
for name in names:
    p=RUN/'images'/(name+'.png.json');d=read(p);sample=d['storm_sample'];setup=d['storm_setup']; camera=d['camera']
    bound=[]
    for suffix in ['.png','.png.json']:
        rel='images/'+name+suffix;bound.append(sha(RUN/rel)==manifest['artifacts'][rel]['sha256'])
    cloud=[]
    for i,record in enumerate(setup['assets']):
        row=i//3; typ=i%3; z=-1000-2100*row;x=-2650+150*math.sin((z+3500)*.0007)
        expected_pos=[[x,920+35*math.sin(row*1.5),z],[x-200,1040,z-180],[x-80,685,z-90]][typ]
        expected_scale=[[1,1,1],[1.05,1,1.05],[.85,.72,.86]][typ]
        asset=assets[typ]
        cloud.append(dict(asset=record['asset'],position_error_m=float(np.max(np.abs(np.array(record['position'])-expected_pos))),scale_error=float(np.max(np.abs(np.array(record['scale'])-expected_scale))),source_and_parts_match=record['glb_sha256']==asset['sha256']['.glb'] and record['mesh_parts']==len(asset['parts'])))
    views.append(dict(view=name,camera=camera,sampled_time=sample['time'],flash=sample['flash'],flash_matches_explicit_time=sample['flash']==int(2<=sample['time']<2.14),camera_weather_recorded=sample['camera_weather'],camera_weather_recomputed=mask(camera['position']),weather_error=abs(sample['camera_weather']-mask(camera['position'])),rain_center=sample['rain_center'],rain_instances=setup['rain_instances'],lightning_lights=sample['lightning_native_lights'],lightning_segments=sample['lightning_segments'],material_bindings=sample['material_bindings'],misnamed_native_materials_adapted=setup['native_materials_adapted'],transparent_retained_count=len(setup['transparent_materials_retained']),same_retained_world_fields={key:d[key]==old[key] for key in retained_fields},same_named_headland_trees=d['headland_study']['trees']==old['headland_study']['trees'],run_and_runtime_identity=d['run_id']==RUN.name and d['storm_runtime_sha256']==sha(S/'storm_front_35a.gd'),image_and_sidecar_bound=all(bound),cloud_instances=cloud))

# Bounded frozen asset identity; no geometry/collision scan of the retained world.
unchanged=[]
for p in (PRIOR/'study-inputs').rglob('*.glb'):
    rel=p.relative_to(PRIOR/'study-inputs');q=F/rel
    unchanged.append(dict(path=rel.as_posix(),same_bytes=q.exists() and sha(q)==sha(p)))
inputs=read(RUN/'inputs.json')['files']; oldinputs=read(PRIOR/'inputs.json')['files']
world_files=[]
for key in ['res://scenes/world/World.tscn','res://assets/world_layout.json']:
    current=R/key.removeprefix('res://');world_files.append(dict(path=key,sha256=sha(current),same_current_prior_run=sha(current)==inputs[key]['sha256']==oldinputs[key]['sha256']))

# Direct shader counterexample, not sampled live instance or GPU replay.
camera_y=330.;top=camera_y+450.;bottom_before=top-4.; upper_before=bottom_before+9.
wrapped=lambda y:top-((top-y)%900.)
counterexample=dict(world_time=0,camera_y=camera_y,input_y=[bottom_before,upper_before],output_y=[wrapped(bottom_before),wrapped(upper_before)],before_vertical_span_m=9,after_vertical_span_m=abs(wrapped(upper_before)-wrapped(bottom_before)),kind='Analytic legal wrap-boundary case; not an observed instance count or screenshot diagnosis')
geometry_pass=all(p['closed_edges'] and p['opposite_edge_orientation'] and p['single_component'] and p['signed_volume_m3']>0 and p['minimum_triangle_area_m2']>0 and p['native_record_vertices_match'] for a in assets for p in a['parts'])
identity_pass=all(a['hashes_match_native_record'] and a['prepared_and_frozen_identical'] for a in assets) and all(v['run_and_runtime_identity'] and v['image_and_sidecar_bound'] and all(v['same_retained_world_fields'].values()) and v['same_named_headland_trees'] for v in views) and all(x['same_bytes'] for x in unchanged)
report=dict(scope='35a independent bounded exported geometry, source, seven sidecars and retained asset identities. No Blender/GPU/physics run and no full-world geometry scan.',run=RUN.name,terminal_status=manifest['status'],stage_exit_codes=[s['exit_code'] for s in manifest['stages']],completed_utc=manifest['completed_utc'],assets=assets,exported_parts=sum(len(a['parts']) for a in assets),exported_triangles=sum(p['triangles'] for a in assets for p in a['parts']),source_identity=source_checks,shared_mask=dict(shader_files=common_same,gdscript_return_expression_identical=mask_expression_same,gdscript_edge_same='-2350.+150.*sin((p.z+3500.)*.0007)' in gdmask,world_coordinates=True,limitation='Same authored field, not ray-traced cloud coverage; cloud color uses the curved edge but cloud geometry is not clipped by this mask.'),views=views,unchanged_frozen_glbs=unchanged,world_source_files=world_files,rain=dict(instances=14000,quads_per_instance=2,triangles_total=56000,local_top_minus_bottom=[-1.2,9,.6],basis='Identity per MultiMesh instance; crossed world-oriented geometry, not camera billboards',vertical_speed_m_s=150,period_s=6,distribution_recenter='100m camera-cell snapping in XZ and camera Y; deterministic local instance seed, not a permanent global precipitation volume',wrap_counterexample=counterexample,complete_rain_motion_pass=False,limitations=['Per-vertex modulo can stretch a crossed ribbon at vertical wrap; needs shared per-instance anchor shift.','No terrain depth/raycast clipping: rain can continue through roofs/ground where rendered above visible foreground.','Only sample() recenters; seven discrete camera observations do not establish continuous flight update behavior.']),lightning=dict(actual_lights_from_runtime=3,segments_from_runtime=60,omni_positions_from_source=[[-3450-i*440,230,-4000-i*1600] for i in range(3)],range_m=1600,energy_during_pulse=9,shadow_enabled=True,flash_interval_s=[2,2.14],sampled_flash_s=2.04,shader_field_centers=[[-3450-i*440,420,-4000-i*1600] for i in range(3)],field_vs_light_vertical_offset_m=190,limitation='Three actual Omni nodes and 60 cylinder segments are counted by sample; node position/energy/visibility are source-derived, not independently serialized per-node runtime states. Additional analytic flash field is approximate and centered 190m above the actual light.'),known_misnamed_field=dict(name='native_materials_adapted',recorded_value=views[0]['misnamed_native_materials_adapted'],meaning='converted.size(): cached original Material IDs, including shader and retained-transparent entries; not a count of converted native materials'),checks=dict(actual_glb_closed_oriented_positive=geometry_pass,source_and_run_identity=identity_pass,shader_common_identical=all(common_same.values()),gdscript_mask_identical=mask_expression_same,rain_wrap_preserves_ribbon=False),technical_accepted=False,visual_accepted=False,visual_assessment='Parent independently viewed seven images and rejected this candidate; this technical review does not repeat or replace that visual assessment.',full_reference_accepted=False,all_reference_goal_complete=False,limitations=['No native Blender reopen was run by this reviewer; saved .blend identity and builder/native volume records were checked against real exported GLB geometry.','Closed vapor meshes intentionally overlap; this check does not certify cloud inter-part self-intersection-free union or volumetric light transport.','Opaque cloud surfaces use unshaded analytic normal/edge color, no volume density or actual cloud shadow transport.','Native material adaptation preserves a subset of material features; transparency is retained and not weather-adapted.','Unchanged retained file identity and reported placements are not a new whole-world collision or flight test.'])
report['environment_shader_copies_identical']=environment_shader_copies
report['checks']['all_design_source_and_saved_builder_hashes']=all(all(v for k,v in item.items() if k in ['matches_design','frozen_same','matches_saved_builder']) for item in source_checks)
report['checks']['runtime_water_shader_bound']=all(read(RUN/'images'/(name+'.png.json'))['water_shader_sha256']==sha(S/'open_water.gdshader') for name in names)
report['checks']['twelve_cloud_instances_and_transform_records']=all(len(v['cloud_instances'])==12 and all(c['source_and_parts_match'] and c['position_error_m']<.001 and c['scale_error']<1e-6 for c in v['cloud_instances']) for v in views)
(R/'reviews/35a-storm-independent-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=report['checks'],parts=report['exported_parts'],triangles=report['exported_triangles'],unchanged_glbs=len(unchanged),weather_errors=[v['weather_error'] for v in views],maximum_native_volume_relative_delta=max(p['native_volume_relative_delta'] for a in assets for p in a['parts']),counterexample=counterexample),ensure_ascii=False))

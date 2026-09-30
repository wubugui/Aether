"""Only bounded 35b/c incremental geometry, source and report checks; no engine."""
from pathlib import Path
import ast,json,hashlib,struct,math,re
from collections import Counter
import numpy as np
R=Path(__file__).resolve().parents[1]
RUN=R/'captures/validation_runs/storm-35c-20260909T004220Z-c4392024b9a4475faaff26f81d9cbcab'
BRUN=R/'captures/validation_runs/storm-35b-20260909T003744Z-443b5747f7fa4c3a9164f2609d8d953a'
ARUN=R/'captures/validation_runs/storm-35a-20260909T003123Z-b7154d45310e4e2482e9aff200346918'
N=R/'captures/storm_cloud_assets_35b'; B=R/'captures/storm_study_35b'; C=R/'captures/storm_study_35c'; F=RUN/'study-inputs/storm35c'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def txt(p):return p.read_text(encoding='utf-8-sig')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Import only pure functions: never execute the frozen 35a report writer.
tree=ast.parse(txt(R/'reviews/35a-storm-independent-technical.py'))
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['glb_parts','smooth','mask','body']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<35a pure decoder>', 'exec'),globals())
model=read(N/'model-report.json'); assets=[]
for a in model['assets']:
    name=a['asset'];parts=glb_parts(N/(name+'.glb')); orig={p['name']:p for p in a['parts']}
    for p in parts:
        o=orig[p['name']];p['native_counts_match']=p['unique_position_vertices']==o['vertices'] and p['triangles']==o['faces'];p['native_volume_relative_delta']=abs(p['signed_volume_m3']-o['volume_m3'])/o['volume_m3']
    identity=[]
    for ext in ['.blend','.glb']:
        name_ext=name+ext;paths=[N/name_ext,B/'cloud-assets'/name_ext,C/'cloud-assets'/name_ext,F/'cloud-assets'/name_ext,BRUN/'study-inputs/storm35b/cloud-assets'/name_ext]
        identity.append(dict(file=name_ext,sha256=sha(paths[0]),native_record_and_b_c_frozen_identical=all(sha(p)==a[ext[1:]+'_sha256'] for p in paths)))
    assets.append(dict(asset=name,parts=parts,identity=identity))
plan=read(C/'design-plan.json'); source_identity=[]
for name,h in plan['files_sha256'].items():source_identity.append(dict(file=name,sha256=sha(C/name),design_and_frozen_match=sha(C/name)==h==sha(F/name)))
gd=txt(C/'storm_front_35c.gd');bgd=txt(B/'storm_front_35b.gd');rain=txt(C/'storm_rain.gdshader');common=txt(C/'storm_common.gdshaderinc').strip()
common_equal={p.name:common in txt(p) for p in C.glob('*.gdshader') if 'storm35_mask' in txt(p)}
mask_b_c_same=body(txt(B/'storm_common.gdshaderinc'),'float storm35_mask')==body(common,'float storm35_mask')
gdexpr=gd.split('func mask_at',1)[1].split('func adapt',1)[0].split('return ',1)[1].strip().replace('absf','abs')
glslexpr=body(common,'float storm35_mask').split('return ',1)[1].strip().rstrip(';')
gdmask_same=re.sub(r'\s+','',gdexpr)==re.sub(r'\s+','',glslexpr)
def rain_mesh(source):
    block=source.split('arrays[Mesh.ARRAY_VERTEX]=PackedVector3Array([',1)[1].split('])',1)[0]
    points=np.array([[float(v) for v in s.split(',')] for s in re.findall(r'Vector3\((.*?)\)',block)])
    indices=source.split('arrays[Mesh.ARRAY_INDEX]=PackedInt32Array([',1)[1].split('])',1)[0]
    return points,np.array([int(i) for i in indices.split(',')]).reshape(-1,3)
vertices,ix=rain_mesh(gd);vb,ib=rain_mesh(bgd)
base_pair=vertices[:,None,:]-vertices[None,:,:]
wrap_cases=[]
# Includes 35a's exact counterexample and both sides of every anchor boundary.
for time in [0,2.04,6]:
    top=780.
    for origin_y in [776.,-119.999999,-120.,-120.000001,779.999999,780.,780.000001]:
        origin=np.array([-3700.,origin_y,-2500.]);new_y=top-((top-origin_y+time*150)%900)
        offset=np.array([(top-new_y)*.16,new_y-origin_y,0.]);out=vertices+origin+offset
        wrap_cases.append(dict(time=time,origin_y=origin_y,shared_shift=offset.tolist(),vertical_span_m=float(np.ptp(out[:,1])),max_pairwise_vector_error_m=float(np.max(np.abs((out[:,None,:]-out[None,:,:])-base_pair)))))
manifest=read(RUN/'manifest.json');bm=read(BRUN/'manifest.json');old=read(ARUN/'images/storm-high.png.json');views=[]
names=['storm-high','storm-coast-low','storm-inside','storm-edge','storm-clear','storm-flash','storm-inside-flash','storm-cloud-back']
for name in names:
    d=read(RUN/'images'/(name+'.png.json'));s=d['storm_sample']; setup=d['storm_setup']; bindings={}
    for ext in ['.png','.png.json']:
        rel='images/'+name+ext;bindings[ext]=sha(RUN/rel)==manifest['artifacts'][rel]['sha256']
    clouds=[]
    for i,a in enumerate(setup['assets']):
        row=i//3;t=i%3;z=-1000-2100*row;x=-2650+150*math.sin((z+3500)*.0007)
        expected=[[x,1160+35*math.sin(row*1.5),z],[x-200,1300,z-180],[x-80,930,z-90]][t]
        clouds.append(dict(asset=a['asset'],parts=a['mesh_parts'],actual_source_sha_match=a['glb_sha256']==sha(N/(a['asset']+'.glb')),position_error_m=float(np.max(np.abs(np.array(a['position'])-expected)))))
    fields=['world_sha256','rightcoast_glb_sha256','island_a_glb_sha256','island_c_glb_sha256','lighthouse_sha256','placements']
    views.append(dict(view=name,camera=d['camera'],time=s['time'],flash=s['flash'],flash_matches_interval=s['flash']==int(2<=s['time']<2.14),mask_actual=s['camera_weather'],mask_recomputed=mask(d['camera']['position']),run_and_runtime_shader_identity=d['run_id']==RUN.name and d['storm_runtime_sha256']==sha(C/'storm_front_35c.gd') and d['water_shader_sha256']==sha(C/'open_water.gdshader'),manifest_bindings=bindings,clouds=clouds,rain_instances=setup['rain_instances'],native_light_count=s['lightning_native_lights'],bolt_segments=s['lightning_segments'],material_cache_entries=setup['material_cache_entries'],retained_original_materials=setup['retained_original_materials'],live_shader_material_bindings=s['material_bindings'],legacy_cloud_meshes_adapted=setup['legacy_cloud_meshes_adapted'],old_misnamed_field_absent='native_materials_adapted' not in setup,land_identity_fields={k:d[k]==old[k] for k in fields},named_headland_trees_retained=d['headland_study']['trees']==old['headland_study']['trees']))
stderr_b=txt(BRUN/'storm-world-views-error.log');stderr_c=txt(RUN/'storm-world-views-error.log');stdout_c=txt(RUN/'storm-world-views.log')
metadata=['storm35_retained_materials','storm35_live_materials','storm35_shader_cache']
checks=dict(six_glb_closed_positive_oriented=all(p['closed_edges'] and p['opposite_edge_orientation'] and p['single_component'] and p['signed_volume_m3']>0 and p['minimum_triangle_area_m2']>0 and p['native_counts_match'] for a in assets for p in a['parts']),b_c_actual_native_assets_identical=all(x['native_record_and_b_c_frozen_identical'] for a in assets for x in a['identity']),all_source_frozen_identity=all(x['design_and_frozen_match'] for x in source_identity),rain_eight_vertices_and_indices_exact=np.array_equal(vertices,vb) and np.array_equal(ix,ib),rain_shared_origin_source='vec3 p=MODEL_MATRIX[3].xyz;' in rain,rain_wrap_cases_preserve_shape=all(w['max_pairwise_vector_error_m']<1e-9 and abs(w['vertical_span_m']-9)<1e-9 for w in wrap_cases),shader_common_identical=all(common_equal.values()),mask_b_c_and_gdscript_identical=mask_b_c_same and gdmask_same,flash_center_agrees_omni='vec3(-3450.-float(i)*440.,230.,-4000.-float(i)*1600.)' in common and 'bottom+Vector3(0,220,0)' in gd,metadata_reference_retention_source=all('game.set_meta("'+m+'"' in gd for m in metadata),eight_sidecar_manifest_identity=all(v['run_and_runtime_shader_identity'] and all(v['manifest_bindings'].values()) for v in views),actual_weather_values_match=all(abs(v['mask_actual']-v['mask_recomputed'])<1e-12 for v in views),b_material_error_not_reproduced_in_c=stderr_b.count('ERROR: Parameter "material" is null.')==4 and stderr_c=='' and 'ERROR:' not in stdout_c,retained_land_sidecars_match=all(all(v['land_identity_fields'].values()) and v['named_headland_trees_retained'] for v in views))
report=dict(scope='35b/c bounded incremental native cloud GLB, source and eight recorded observations; no Blender/GPU/physics/full-world repeat.',run=RUN.name,run_status=manifest['status'],stage_exit_codes=[s['exit_code'] for s in manifest['stages']],completed_utc=manifest['completed_utc'],source_geometry_revision='35b; 35c retains exact three .blend/.glb',assets=assets,exported_parts=sum(len(a['parts']) for a in assets),exported_triangles=sum(p['triangles'] for a in assets for p in a['parts']),source_identity=source_identity,source_builder_identity=dict(native_builder_sha256=sha(N/'builder.py'),matches_live_builder=sha(N/'builder.py')==sha(R/'blender/model_storm_clouds_35b.py')),rain=dict(vertices=vertices.tolist(),indices=ix.tolist(),wrap_cases=wrap_cases,pairwise_error_max_m=max(x['max_pairwise_vector_error_m'] for x in wrap_cases),geometry_correction='One MODEL_MATRIX origin gives shared Y and X offset for all eight vertices under actual identity instance Basis. Existing 9m vertical height is preserved across modulo.',remaining='The whole instance still resets by 900m vertically and approximately 144m horizontally; this is an authored wrap, not continuous drop trajectory through reset. Camera-cell recenter and lack of terrain interception remain. No live instance transform/vertex buffer dump is claimed.'),flash=dict(centers=[[-3450-i*440,230,-4000-i*1600] for i in range(3)],source_omni_range_m=1600,source_energy_at_pulse=9,field='Same centers but exponential ellipsoidal unshadowed artistic field, not native attenuation/shadow radiometry.',unused_old_variable='flash_center Vector3(-3500,420,-4250) remains declared but unused; it does not drive the actual common function.'),shared_mask_shader_files=common_equal,views=views,material_lifecycle=dict(metadata_keys=metadata,retained_original_before_rebinding=True,retained_refs_count=views[0]['retained_original_materials'],live_shader_count=views[0]['live_shader_material_bindings'],cache_count=views[0]['material_cache_entries'],legacy_cloud_meshes=views[0]['legacy_cloud_meshes_adapted'],renamed_count_meaning='Cache IDs, not number of native materials converted. Retained/live arrays and shader cache are also held on game metadata.',b_null_errors=4,c_stderr_bytes=(RUN/'storm-world-views-error.log').stat().st_size,c_stdout_error_lines=stdout_c.count('ERROR:'),root_cause_isolated=False,limit='Runtime reports array counts; metadata contents/lifetime are checked from executed frozen source, not a separate live metadata dump. No isolated A/B experiment establishes which operation caused the prior null RID queries.'),failed_b=dict(status=bm['status'],error=bm.get('error'),image_bindings_in_manifest=sum(k.startswith('images/') for k in bm['artifacts']),eight_images_and_sidecars_present=all((BRUN/'images'/(n+e)).exists() for n in names for e in ['.png','.png.json']),images_manifest_identity_claimed=False,explanation='Failure gate exited before image artifact registration. Existing images are preserved but are not manifest-bound successful evidence.'),checks=checks,bounded_incremental_technical_pass=all(checks.values()),visual_accepted=False,full_reference_accepted=False,all_reference_goal_complete=False,prior_35a_technical_false_preserved=True,limitations=['No Blender reopen or full cloud intersection union check; exact native file hashes plus independent exported per-solid closed/positive geometry.','Six canopy solids have no volume density/inside scattering or physical cloud-shadow transport; visually unaccepted per parent.','35b sun direction, raised cloud banks, legacy-cloud shading, 8-sample sky field and whitecap/rain artistic changes remain; this report does not certify their visual fidelity.','Unchanged world/land SHA fields, placements and trees inherit earlier support; no full terrain hashing/physics/support repetition.','Eight static viewpoints and two explicit flash samples are not continuous weather playback or flight proof.'])
(R/'reviews/35c-storm-independent-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(dict(checks=checks,parts=report['exported_parts'],triangles=report['exported_triangles'],rain_pairwise_error=report['rain']['pairwise_error_max_m'],max_native_volume_delta=max(p['native_volume_relative_delta'] for a in assets for p in a['parts']),failed_b=report['failed_b']),ensure_ascii=False))

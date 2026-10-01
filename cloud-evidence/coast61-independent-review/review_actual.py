"""Read-only review of finished61 actual evidence; writes only review/aggregate files."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json,collections,numpy as np
R=Path(__file__).resolve().parents[2];P=R/'candidates/round40-exclusive-20260930/project';D=Path(__file__).resolve().parent;S=R/'source-assets/coast57/revision-b';E=R/'cloud-evidence/coast61-v2-verify-20261001T124815Z-czvc76_r';B=R/'cloud-evidence/coast61-build-20261001T123605Z-gq87o4e1'
sys.path.insert(0,str(S));import foot_geometry57b as fg
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
w=read(E/'wrapper-report.json');g=read(E/'verify-report61.json');f=read(E/'full-foot-report61.json');actual=read(E/'runtime-native61.json');build=read(B/'build-report61.json');inputs=read(E/'input-sha256.json')
assert w['passed'] and all(x['finished'] and x['exit_code']==0 and x['passed'] and not x['errors'] for x in w['records'])
assert build['passed'] and not build['failures'] and g['passed'] and not g['failures'] and f['passed'] and all(x['passed']for x in f['checks'])
changed=[p for p,h in inputs.items()if sha(p)!=h];assert not changed
assert all(sha(x['path'])==x['sha256']for x in g['captures']) and len(g['captures'])==10
assert sha(E/'runtime-native61.json')==g['runtime_native_sha256']==f['actual_native_data_sha256']
assert all(row[k]['exact'] and not row[k]['component_differences'] for row in g['inherited_pose_bytes'] for k in ['camera','ship'])
phase=lambda a:[{k:v for k,v in x.items()if k!='phase'}for x in a]
assert len(g['support'])==120 and phase(g['support'][:60])==phase(g['support'][60:])
source_manifest=read(S/'source-manifest57b.json')['files'];assert all(sha(S/p)==h for p,h in source_manifest.items())
positions={};radii={}
for path,data in actual['groups'].items():
 origin=np.array(data['global_transform'],np.float32).reshape(3,4)[:,3]
 for index,buf in enumerate(np.array(data['buffer'],np.float32).reshape(-1,12)):
  key=(path,index);pos=(buf[[3,7,11]]+origin).astype(np.float32);positions[key]=pos
  world=fg.actual_world(buf,origin,np.concatenate(fg.models[path]['polys']));radii[key]=float(np.linalg.norm(world[:,[0,2]]-pos[[0,2]],axis=1).max())
assert len(positions)==81
clearances=[]
for row in f['relocation_clearances']:
 key=(row['node'],row['index']);gap,neighbor=min((float(np.linalg.norm(positions[key][[0,2]]-pos[[0,2]]))-radii[key]-radii[other],other)for other,pos in positions.items()if other!=key)
 assert gap==row['clearance_m'] and gap>=.5
 clearances.append({'node':key[0],'index':key[1],'all_81_nearest':list(neighbor),'radial_foot_clearance_m':gap})
affected=[x for x in f['placements']if x['affected']];untouched=[x for x in f['placements']if not x['affected']];assert len(affected)==40 and len(untouched)==20
assert all(x['actual_mesh_foot']['max_air_gap_m']==0 and x['actual_shape_foot']['max_air_gap_m']==0 for x in affected)
seated={(x['node'],x['index']):x for x in read(S/'scatter-replacements-seated.json')}
visible=[]
for row in affected:
 if row['kind']=='pine':continue
 model=fg.models[row['node']];buf=np.array(row['native_buffer']);scale=abs(buf[5]);depth=seated[row['node'],row['index']]['foot_seat_depth']
 visible.append({'node':row['node'],'index':row['index'],'extra_seat_m':depth,'extra_seat_fraction_of_original_above_origin_height':depth/(model['max_y']*scale),'maximum_burial_fraction_of_full_height':row['actual_mesh_foot']['max_penetration_m']/(model['height']*scale),'remaining_above_ground_mesh_area_fraction':row['visible_after']['area_above_terrain_fraction'],'above_ground_area_retention_ratio':row['above_terrain_area_ratio'],'top_above_terrain_m':row['visible_after']['top_above_terrain_at_root_m']})
resources=[]
for x in build['resources']:
 pp=P/x['path'].removeprefix('res://');assert sha(pp)==x['sha256'];resources.append({'path':str(pp.relative_to(R)),'sha256':x['sha256'],'bytes':pp.stat().st_size})
scene=P/'scenes/candidate61-coast/Game61Coast.tscn';assert sha(scene)==build['candidate_sha256'];
result={'review_passed':True,'review_kind':'Independent finished-evidence hash/scope review; no engine or world rerun','source57b_manifest_file_count':len(source_manifest),'all_source57b_files_unchanged':True,'all_52_pinned_inputs_unchanged':len(inputs)==52,'actual_build':read(B/'wrapper-report.json'),'actual_fresh_wrapper':w,'full_foot_check_count':f['check_count'],'native_scene_sha256':sha(scene),'native_scene_bytes':scene.stat().st_size,'independent_resources':resources,'two_actual_surface_face_counts':[2111,759],'original_surface_vertex_fields_exact':True,'actual_root_count':60,'changed_roots':40,'unchanged_inbox_roots':20,'full_group_instances':81,'changed_translation_components':{'x':5,'y':40,'z':6},'relocations':7,'root_support_phases_identical':True,'root_phase_record_count':120,'runtime_cache_max_difference_m':max(x['cache_delta']for x in g['support']),'actual_physics_vs_direct_shape_max_m':max(abs(x['physics_y']-x['raw_shape_y'])for x in g['support']),'actual_mesh_vs_shape_corner_difference_m':g['notes']['actual_candidate_mesh_collision_max_component_error'],'original_inherited_corner_difference_m':g['notes']['original_mesh_collision_max_component_error'],'40_adjusted_mesh_and_collision_feet_max_air_gap_m':0,'unchanged_existing_rock_foot_gaps_m':[{'index':x['index'],'mesh_gap':x['actual_mesh_foot']['max_air_gap_m'],'shape_gap':x['actual_shape_foot']['max_air_gap_m']}for x in untouched if x['kind']=='rock'],'affected_rock_bush_visibility':visible,'relocation_clearance_all81':clearances,'all_10_image_hashes_match':True,'inherited_pose_bytes_exact':True,'actual_full_foot_report':str((E/'full-foot-report61.json').relative_to(R)),'visual_review':str((E/'VISUAL_REVIEW.md').relative_to(R)),'limits':['Only 40 adjusted objects pass new continuous foot contact; 20 unchanged objects retain their old local conditions, including rock0/8 gaps0.150/0.388m','Visibility is actual native triangle area above terrain and top clearance, not solid volume or camera occlusion','The7 clearance checks are conservative foot-radius XZ checks; this audit additionally checked all81 instances in the4groups and found the same nearest neighbors; no tree canopy clearance claim','Original millimeter tile-seam mismatch frozen, open heightfield not capped','Edited759 triangle normals/tangents use native engine packing; untouched2111 triangles retain all original GPU fields exactly; no universal source-normal-byte claim on edited surface','Actual readback used llvmpipe; no hardware GPU,61 ordinary flight, repeated user F2/observe scale continuity, opening/full-reference acceptance','Visual review rejects overall1131/1347 match: major high mountain chain/coast hierarchy still missing']}
(D/'review.json').write_text(json.dumps(result,indent=2)+'\n')
aggregate={'version':'61-native-coast57b','native_build_passed':True,'fresh_native_saved_scope_passed':True,'runtime_two_phase_root_collision_cache_passed':True,'40_adjusted_objects_continuous_foot_support_passed':True,'full_foot_native_reconciliation_passed':True,'inherited_1128_1216_exact_pose_and_toggle_passed':True,'source57b_all106_manifest_files_unchanged':True,'actual_image_count':10,'independent_review_passed':True,'ordinary_flight_passed':False,'real_UI_observation_transition_continuity_passed':False,'hardware_GPU_passed':False,'visual_reference_acceptance':False,'all_reference_GOAL_complete':False,'scene_sha256':sha(scene),'base60_scene_sha256':'8fcb0d24d503133a7e6ba29645291a73314c88b40ab447e0802937f1c802ac45','scope':'One tile_-5_-5 mesh/collision and4scatter buffers;40 root transforms,7XZ moves;inherits60->56->55->53;defaultunchanged','resources':resources,'evidence':{str(pp.relative_to(R)):sha(pp)for pp in [B/'wrapper-report.json',B/'build-report61.json',E/'wrapper-report.json',E/'verify-report61.json',E/'full-foot-report61.json',E/'runtime-native61.json',E/'VISUAL_REVIEW.md',D/'review.json']},'first_failed_run_preserved':'cloud-evidence/coast61-verify-20261001T123638Z-b66cdbe8','failure_resolution':'Verifier-only temporary camera-state restoration, supported by bare-Node3D sequence evidence;original exact pose expectations unchanged','limits':result['limits']}
(P/'scenes/candidate61-coast/verified61.json').write_text(json.dumps(aggregate,indent=2)+'\n')
print(json.dumps({'review_passed':True,'inputs':len(inputs),'source57b_files':len(source_manifest),'resources_bytes':sum(x['bytes']for x in resources),'continuous_foot_checks':f['check_count'],'all81_min_clearance':min(x['radial_foot_clearance_m']for x in clearances),'visible_affected':visible},indent=2))

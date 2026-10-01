"""Read-only external completion gate; no renderer or world invocation."""
from pathlib import Path
import hashlib,json,struct
import numpy as np
from PIL import Image
PHASES=['A0','A','D','A2']
MATERIAL_PHASES=['1216']+PHASES
TARGET_KEYS=['flags_native_typed_exact','original_active_material_identity_exact','actual_source_or_restored_mesh_exact','actual_ancestor_or_restored_components_exact','intrinsic_mesh_change_connection_exact']
RESTORE_KEYS=['all_components_exact','mesh_resource_identity_restored','flags_typed_exact','active_material_identity_exact']
VIEWPORT_KEYS=['viewport_exact','dimensions_contract_exact','requested_size_exact','content_config_exact','actual_readback_size_exact','texture_metadata_formula_exact','projection_aspect_exact']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def all_true(row,keys):return all(row.get(k) is True for k in keys)
def paths_exact(rows,targets):return len(rows)==len(targets) and sorted(r['path'] for r in rows)==sorted(targets)
def material_proofs(groups,targets):
    if [g.get('reference') for g in groups]!=MATERIAL_PHASES:return False
    pathsets=[];initial=None
    for group in groups:
        rows=group['rows'];paths=[r['path'] for r in rows];pathset=set(paths)
        if len(rows)!=125 or len(pathset)!=125 or len({p.split('/')[1] for p in paths})!=25:return False
        if sum('/CloudSea52e_' in p for p in paths)!=75 or sum('/CloudSea52f_' in p for p in paths)!=50:return False
        if group['old']!=75 or group['new']!=50 or group['material_count']!=3 or group.get('all_initial_material_identities_and_values_exact') is not True:return False
        if not set(targets).issubset(pathset):return False
        if not all(all_true(r,['same_world','visible','lit_vertex_color_wrap','renderer_instance_valid','uses_shared_sun_ambient_fog']) for r in rows):return False
        identities={r['path']:(r['active_material_id'],r['active_material_typed_digest']) for r in rows}
        if len({v[0] for v in identities.values()})!=3:return False
        if initial is None:initial=identities
        elif identities!=initial:return False
        pathsets.append(pathset)
    return all(p==pathsets[0] for p in pathsets)
def pixel_pair(a,b,name_a,name_b):
    d=a.astype(np.int16)-b.astype(np.int16);absolute=np.abs(d);m=np.any(d,axis=2);ys,xs=np.where(m)
    return {'a':name_a,'b':name_b,'rgba_exact':not bool(m.any()),'changed_pixels':int(m.sum()),'changed_channels':int(np.count_nonzero(d)),'alpha_changed_pixels':int(np.count_nonzero(d[:,:,3])),'max_channel_difference':int(absolute.max()),'absolute_channel_sum':int(absolute.sum()),'signed_RGBA_difference_field_sha256':hashlib.sha256(d.astype('<i2').tobytes()).hexdigest(),'bbox':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'first_20_pixels':[{'x':int(x),'y':int(y),'a':a[y,x].tolist(),'b':b[y,x].tolist()} for y,x in list(zip(ys,xs))[:20]]}
def camera_proof(capture,targets):
    proof=capture['target_camera_geometry'];rows=proof['rows'];counts=proof['counts']
    if proof['complete'] is not True or proof['phase']!=capture['phase'] or proof['boundary_epsilon_m']!=.025 or proof['ray_hit_dedup_m']!=.001:return False
    if proof['is_ship_or_sphere_clearance_proof'] is not False or not paths_exact(rows,targets):return False
    actual={k:sum(r['classification']==k for r in rows) for k in ['inside','outside','boundary','ambiguous']}
    if counts!=actual or actual['ambiguous'] or proof['outside_all_ten_target_volumes']!=(actual['outside']==10):return False
    for row in rows:
        tests=row['ray_tests'];distance=row['nearest_surface_m'];classification=row['classification']
        if len(tests)!=3 or not np.isfinite(distance) or distance<0 or row['nearest_triangle_index']<0:return False
        if not all(r['odd_parity']==(r['unique_crossings']%2==1) for r in tests):return False
        if classification=='boundary':
            if distance>.025:return False
        elif classification=='inside':
            if distance<=.025 or not all(t['odd_parity'] is True for t in tests):return False
        elif classification=='outside':
            if distance<=.025 or not all(t['odd_parity'] is False for t in tests):return False
        else:return False
        if capture['phase']=='D':
            if row['actual_world_triangles']!=1834 or row['actual_D_resource_bound'] is not True or row['D_closed_source_proof_applies'] is not True:return False
        elif row['actual_world_triangles']!=1100 or row['actual_D_resource_bound'] is not False or row['D_closed_source_proof_applies'] is not False:return False
    return True

def validate(out,contract):
    native=json.loads((out/'images/report.json').read_text());targets=contract['target_paths']
    phases=native['phase_proofs'];captures=native['captures'];restored=native['restore_rows'];viewports=native['viewport_rows'];flags=native['phase_functions_returned']
    phase={row['phase']:row for row in phases};cap={row['phase']:row for row in captures};source=native['source_proof'];closed=native['closed_source_proof']
    requirements={
      'complete actual four-phase run':native.get('run_complete') is True and native.get('native_provisional_passed') is True,
      'exact ten targets':native['target_count']==10 and sorted(native['target_paths'])==sorted(targets),
      'all four phase functions returned':set(flags)==set(PHASES) and all(flags.get(k) is True for k in PHASES) and all_true(native,['source_function_returned','state_comparison_functions_returned','equal_geometry_rebind_returned']),
      'all native checks passed':bool(native['checks']) and all(x.get('passed') is True for x in native['checks']),
      'exact ordered four-phase proofs':[r['phase'] for r in phases]==PHASES,
      'source geometry and closed proof bound':source.get('passed') is True and source['raw_node']==contract['replacement_glb_node'] and source['actual_geometry']['triangles']==1834 and closed.get('passed') is True and closed['geometry_report_sha256']==contract['geometry_report_sha256'] and closed['bound_glb_sha256']==contract['replacement_glb_sha256'] and closed['native_glb_readback_exact'] is True,
      'forty exact intrinsic callbacks':all(paths_exact(p['mesh_connection_rows'],targets) and all(r['exact_current_mesh_changed_callback'] is True for r in p['mesh_connection_rows']) for p in phases),
      'A0 retained baseline':phase['A0']['exact_original_baseline'] is True and native['A0_preserved'] is True,
      'A and A2 fully unmasked original states':all(phase[x].get('full_original_state_exact') is True and phase[x]['full_native_digest']==phase['A0']['full_native_digest']==native['baseline_native_digest'] and phase[x]['actual_stored_property_changes']==[] and phase[x]['runtime_differences']==[] for x in ['A','A2']) and phase['A2']['full_A2_state_exact'] is True,
      'D only ten contracted replacements':phase['D']['all_non_scope_typed_exact'] is True and phase['D']['exact_ten_mesh_changes'] is True,
      'thirty exact target comparisons':all(paths_exact(phase[x]['targets'],targets) and all(all_true(r,TARGET_KEYS) for r in phase[x]['targets']) for x in ['A','D','A2']),
      'ten byte-equivalent clones':paths_exact(native['clone_rows'],targets) and all(all_true(r,['distinct_resource_and_rid','all_geometry_native_bytes_exact','surface_material_identities_exact']) for r in native['clone_rows']),
      'ten original-resource warm rebinds':paths_exact(native['rebind_rows'],targets) and all(all_true(r,['clone_was_bound','original_identity_restored','all_components_untouched_exact','flags_exact','active_material_identity_exact']) for r in native['rebind_rows']),
      'ten exact final restores':native['restoration_complete'] is True and paths_exact(restored,targets) and all(all_true(r,RESTORE_KEYS) and {c['component'] for c in r['components']}=={'position','rotation','rotation_order','scale','local_transform','global_transform'} and len(r['components'])==6 and all(c['exact'] is True and c['before_bytes']==c['restored_bytes'] for c in r['components']) for r in restored),
      'original mesh resources retained':native['original_resources_kept']==10,
      'initialization plus named four material proofs':material_proofs(native['live_cloud_bindings'],targets),
      'exact ordered four captures':[r['phase'] for r in captures]==PHASES,
      'all actual camera triangle diagnoses':all(camera_proof(c,targets) for c in captures),
      'four exact viewport contracts':[r['phase'] for r in viewports]==PHASES and all(all_true(r,VIEWPORT_KEYS) and r['requested_dimensions']==[1180,664] and r['actual_dimensions']==[1179,664] and r['texture_metadata_dimensions']==[831,468] and r['metadata_expected_from_engine_formula']==[831,468] for r in viewports) and len({r['viewport_typed_digest'] for r in viewports})==1,
      'fixed camera lighting projection and world':all(captures[0][key]==r[key] for r in captures[1:] for key in ['camera_transform','camera_fov','camera_near','camera_far','camera_keep_aspect','camera_projection_columns','environment','reflection_sync_count','world_chunk_count','world_core_count']),
      'scope and non-acceptance remain explicit':native['single_full_world'] is True and native['scene_saved'] is False and native['lights_or_materials_changed'] is False and native['visual_acceptance'] is False and native['hardware_gpu_acceptance'] is False and native['complete_flight_passed'] is False and native['old52g_failure_unchanged'] is True and native['shadow_root_cause_proven'] is False and native['A0_A_residual_is_explicit'] is True,
      'fixed scene and source':native['scene_sha256']==contract['baseline_sha256'] and native['replacement_sha256']==contract['replacement_glb_sha256'],
    }
    summary=json.loads((out/'images/A0-native-baseline-summary.json').read_text())
    requirements['one full baseline bound to phase digests']=summary['binary_sha256']==sha(out/'images/A0-native-baseline.bin') and summary['typed_state_digest']==native['baseline_native_digest'] and all(p['node_count']==summary['nodes']==11423 for p in phases)
    pngs=[];rgba={};errors=[]
    for row in captures:
        path=Path(row['path']);raw=path.read_bytes();dims=struct.unpack('>II',raw[16:24]);pngs.append({'name':path.name,'bytes':len(raw),'dimensions':list(dims),'sha256':sha(path)})
        if path.parent!=out/'images' or path.name!=f"1216-front-{row['phase']}.png":errors.append('Unexpected capture path '+str(path))
        if raw[:8]!=b'\x89PNG\r\n\x1a\n' or dims!=(1179,664) or row['size']!=[1179,664] or sha(path)!=row['sha256']:errors.append('PNG signature/dimensions/hash mismatch '+path.name)
        rgba[row['phase']]=np.array(Image.open(path).convert('RGBA'))
    pairs=[pixel_pair(rgba[a],rgba[b],a,b) for a,b in [('A0','A'),('A','D'),('A','A2'),('A0','A2')]]
    pp=native['pixel_proof'];requirements['all raw native and decoded RGBA comparisons agree']=pp['A0_A_rgba_exact']==pairs[0]['rgba_exact'] and pp['D_differs_from_A']==(not pairs[1]['rgba_exact']) and pp['A_A2_rgba_exact']==pairs[2]['rgba_exact']
    requirements['strict A A2 all-RGBA equality']=pairs[2]['rgba_exact'] is True and pp['A_A2_rgba_exact'] is True and pp['strict_pixel_tolerance']==0
    requirements['strict A A2 PNG equality']=cap['A']['sha256']==cap['A2']['sha256'] and pp['A_A2_png_exact'] is True
    requirements['D differs from control A']=pairs[1]['rgba_exact'] is False
    requirements['A0 original residual honestly retained']=pp['A0_preserved_and_not_pixel_acceptance_baseline'] is True and pp['A0_A_png_exact']==(cap['A0']['sha256']==cap['A']['sha256'])
    requirements['exact four PNG files']=sorted(p.name for p in (out/'images').glob('*.png'))==sorted(f'1216-front-{p}.png' for p in PHASES)
    errors += [name for name,ok in requirements.items() if not ok]
    pixels={'pairs':pairs,'A0_A_is_explicit_rebind_residual':True,'A_A2_strict_RGBA_tolerance':0,'old52g_failure_remains_failed':True,'shadow_root_cause_proven':False,'visual_acceptance':False}
    return errors,pngs,pixels,requirements

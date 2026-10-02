#!/usr/bin/env python3
"""Unchanged all-group source replay with three explicit v3 adapter substitutions.

No decoder or query geometry is replaced. The new validator returns actual rock
get_faces bounds; six visual identities use their explicit conservative union.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE_V3=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE_V3),str(HERE_V3.parent/'version-guard-v2'),str(HERE_V3.parent)]
from prepare_proxy62 import *
from version_schema62 import request_v2
from schema_shadow62 import request_v3,validate_native

def analyze(native=None):
    before,guard=validate_dependencies();n,c,p,independent,scenes=load_saved();request=request_v3(request_v2(native_request(n,c)))
    consulted=dict(before)
    for rel,pin in c['source_pins'].items():
        path=ROOT/rel;require(digest(path)==pin['sha256'],'classification source changed '+rel);consulted[str(path)]=pin['sha256']
    for path in [BASE/'dependency_guard62.py',BASE/'run_intake62.py',V1/'decoder62.py',V1/'scene_inputs62.py',V1/'build_inputs62.py',V1/'prepared-inputs.json.gz',V1/'prepared-inputs-identity.json',BASE/'scatter-hit-review-01/classification.json',BASE/'world-boundary-v1/upstream/core__math__transform_3d.h']:
        consulted[str(path)]=digest(path)
    rock_bounds=validate_native(native,request)if native else None
    vertex_bounds={x['mesh_resource']:x['combined_clearance_bounds']for x in native['visual_meshes']}if native else {}
    expected={g['path']:g for g in p['groups']};old={g['path']:g for g in n['groups']};require(set(expected)==set(old)==set(independent),'all path identities')
    rows=[];groups=[];checked=0;visual_total=visual_design=0;species_counts={};protected_counts={};proxy_total=proxy_only=0
    for path,want in expected.items():
        prior=old[path];src=independent[path];saved=want['saved_buffer'];require(src['world_transform_columns']==want['world_transform_columns'],'parent transform changed '+path)
        require(prior['resource']==src['resource']==want['resource'],'resource binding changed '+path)
        uri=want['resource']
        if '::'in uri:
            scene=scenes[uri.split('::')[0]];current=read_text_multimesh(uri,scene)
            rawvalues=numbers(scene['subresources'][uri.split('::')[1]]['properties'].get('buffer','PackedFloat32Array()'),'PackedFloat32Array')
            buffer=struct.pack('<'+'f'*len(rawvalues),*rawvalues)
        else:
            current=read_multimesh(PROJECT/uri[6:],include_buffer=True);buffer=current['raw_buffer']
        for key in ['source_sha256','instance_count','stride_floats','buffer_sha256']:
            require(current[key]==saved[key],'saved input changed '+path+'/'+key)
        require(hashlib.sha256(buffer).hexdigest()==saved['buffer_sha256']==prior['buffer_sha256'],'buffer exact native hash '+path)
        count=saved['instance_count'];stride=saved['stride_floats'];checked+=count
        species=None
        if path.startswith('World/Vegetation/'):
            meta_src=want['property_sources']['metadata/asset_kind'];props=scenes[meta_src]['nodes'][path]['properties']
            species=json.loads(props['metadata/asset_kind']);require(species in ['oak','poplar','pine','rock','bush'],'unknown vegetation kind '+path)
            require(want['model_scene']==f'res://scenes/prefabs/{species}.tscn','model metadata mismatch '+path)
            require(n['mesh_resources'][prior['mesh_resource']]['surface_storage_sha256']==n['mesh_resources'][f'res://assets/meshes/{species}.res']['surface_storage_sha256'],'visual class binding mismatch '+path)
            species_counts[species]=species_counts.get(species,0)+count
        protection=protected(prior)
        if protection:protected_counts[protection]=protected_counts.get(protection,0)+count
        native_hits={h['index']:h for h in prior['instances_overlapping_query']};seen=[];seen_design=[];newindices=[]
        for i,vals in enumerate(struct.iter_unpack('<'+'f'*stride,buffer)):
            local=row_to_columns(vals);world=compose(want['world_transform_columns'],local)
            visual=transform_box_native(world,prior['local_model_bounds_including_shadow'])
            vh=hits(visual,n['query_box_with_40m']);vd=hits(visual,n['design_box'])
            if vh:
                seen.append(i);visual_total+=1;visual_design+=vd
                require(i in native_hits and native_hits[i]['world_bounds_including_shadow']==visual,'exact original native visual bound '+path+'/'+str(i))
                require(vd==native_hits[i]['hits_design'],'original design membership '+path+'/'+str(i))
            if vd:seen_design.append(i)
            proxy=tree_capsule_box(world)if species in ['oak','pine','poplar']else (union(transform_box_outer(world,rock_bounds),transform_box_native(world,rock_bounds))if species=='rock'and rock_bounds else None)
            ph=hits(proxy,n['query_box_with_40m'])if proxy else False
            source_vertices=transform_box_outer(world,vertex_bounds[prior['mesh_resource']])if prior['mesh_resource']in vertex_bounds else None
            envelope=union(visual,proxy,source_vertices)
            if not hits(envelope,n['query_box_with_40m']):continue
            # Rectangular union can bridge disconnected AABBs; tag this conservative-only case.
            uh=hits(envelope,n['design_box']);proxy_total+=ph;proxy_only+=ph and not vh;newindices.append(i)
            rows.append({'path':path,'index':i,'class':species or 'non_vegetation','resource':uri,'buffer_sha256':saved['buffer_sha256'],
                         'world_transform_columns':world,'visual_bounds':visual,'source_specific_visual_and_get_faces_world_bounds':source_vertices,'source_rule_proxy_bounds':proxy,'combined_conservative_bounds':envelope,
                         'visual_query_hit':vh,'visual_design_hit':vd,'proxy_query_hit':ph,'proxy_design_hit':hits(proxy,n['design_box'])if proxy else False,
                         'query_union_bridge_only':not(vh or ph or (hits(source_vertices,n['query_box_with_40m'])if source_vertices else False)),'design_union_hit':uh,'proxy_only_query_hit':ph and not vh,
                         'protected_neighbor':protection,'required_decision':'keep_protected_terrain_and_instances'if protection else ('keep_or_reconcile_support_if_actual_edit_intersects'if uh else 'preserve_blend_boundary_clearance'),
                         'runtime_collision_observed':False})
        require(seen==list(native_hits)and len(seen_design)==prior['design_instance_count'],'complete visual requery membership '+path)
        groups.append({'path':path,'class':species,'instances_checked':count,'source_resource':uri,'buffer_sha256':saved['buffer_sha256'],
                       'protected_neighbor':protection,'visual_query_indices':seen,'union_query_indices':newindices})
    require(checked==57797 and len(groups)==775 and visual_total==676 and visual_design==575,'complete unchanged baseline replay')
    after,afterguard=validate_dependencies();require(before==after and guard==afterguard,'dependency changed during preparation')
    result={'status':'source_bounds_ready_pending_native_rock_and_vertex_read'if native is None else 'source_specific_bounds_read_complete',
            'raw_report_sha256':RAW_SHA,'classification_sha256':CLASS_SHA,'full_dependency_guard':guard,
            'saved_groups_requeried':len(groups),'saved_instances_requeried':checked,'vegetation_instances_by_actual_class':species_counts,
            'visual_query_count':visual_total,'visual_design_count':visual_design,'combined_query_count':len(rows),'combined_design_count':sum(r['design_union_hit']for r in rows),
            'source_proxy_query_count':proxy_total,'proxy_only_query_count':proxy_only,'protected_saved_instance_counts':protected_counts,
            'design_box':n['design_box'],'query_box_with_40m':n['query_box_with_40m'],
            'scope':'All 775 saved groups streamed once; 773 vegetation groups use source metadata. No full-world buffer output or world instantiation.',
            'tree_envelope':'Affine transform of enclosing local box x,z=+-max(2.4,float32(2.4)), y=0..11. Directed binary64 outer bounds union exact native-style float32 bounds. Conservative capsule envelope; not exact capsule contact.',
            'rock_first_imported_faces_observed':native is not None,'native_visual_vertex_bounds_observed':native is not None,
            'rock_pending_policy':'No rock proxy clearance claim until native first-mesh faces exist; visual-only rock entries provisional.'if native is None else 'Actual imported mesh face bounds used; no collision-resource substitution.',
            'runtime_activation_limits':{'focus_cells':'3x3 neighborhood','horizontal_root_distance_max':350,'vertical_root_difference_max':150,'refresh_after_seconds':0.4,'active_colliders_observed':False},
            'original_unproved_flags_unchanged':{f:False for f in FALSE_FLAGS},'terrain_changed':False,'deletion_authorized':False,'groups':groups,'path_index_keep_reconcile':rows}
    for path,sha in consulted.items():require(digest(path)==sha,'consulted source changed '+path)
    return result,request,dict(sorted(consulted.items()))

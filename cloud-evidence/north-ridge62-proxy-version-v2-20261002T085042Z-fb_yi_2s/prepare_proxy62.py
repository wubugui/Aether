#!/usr/bin/env python3
"""Source-bound clearance preparation. Default is a read-only verification, no engine."""
from __future__ import annotations
import argparse,gzip,hashlib,json,struct,sys,re
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=HERE.parents[2]
V1=BASE/'scatter-readonly-v1'
sys.path[:0]=[str(V1),str(BASE),str(BASE/'audit-tools')]
from north62_binary_review import inspect as inspect_imported_resource
from dependency_guard62 import PROJECT,validate_dependencies
from decoder62 import read_multimesh
from scene_inputs62 import read_inputs,read_text_multimesh,numbers,compose
from build_inputs62 import baseline
from proxy_math62 import require,union,hits,row_to_columns,transform_box_native,transform_box_outer,tree_capsule_box,bounds_ok
RUN=ROOT/'cloud-evidence/north-ridge62-scatter-float32-collect-20261002T065622Z-6k1gbidm'
RAW_SHA='62482b889a2dc6c5687274748397f5d4bf9da3be6898b8fbca6d372a5a2452bf'
CLASS_SHA='24341762139c49ae788aff4417e65ebfe90591312e6cc1d890ce9bb57def4186'
ROCK_PREFAB='res://scenes/prefabs/rock.tscn'
ROCK_IMPORT='res://assets/models/rock.glb'
ROCK_CACHE='res://.godot/imported/rock.glb-9fe9ded640b9e8b845c59e36f0f83d1b.scn'
FALSE_FLAGS=['all_occupancy_complete','runtime_generated_entities_proved','runtime_model_scene_and_collision_proved','shader_deformation_envelopes_proved','road_width_proved','visual_acceptance','vertex_payload_bounds_independently_recomputed']

def digest(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read_pinned(path,sha):
    b=Path(path).read_bytes();require(hashlib.sha256(b).hexdigest()==sha,'changed pinned source '+str(path));return b

def load_saved():
    raw=read_pinned(RUN/'native-scatter.json',RAW_SHA)
    require(gzip.decompress((RUN/'native-scatter.json.gz').read_bytes())==raw,'raw gzip mismatch')
    n=json.loads(raw);c=json.loads(read_pinned(BASE/'scatter-hit-review-01/classification.json',CLASS_SHA))
    w=json.loads((RUN/'wrapper-report.json').read_text());require(w['passed']and w['native_scatter_sha256']==RAW_SHA and not w['changed_inputs']and not w['log_errors'],'original native witness failed')
    require(n['status']=='complete'and n['issues']==[]and len(n['groups'])==775 and n['saved_instance_count']==57797,'original report scope')
    require(all(n.get(f)is False for f in FALSE_FLAGS),'original limits changed')
    info=json.loads((V1/'prepared-inputs-identity.json').read_text());packed=read_pinned(V1/'prepared-inputs.json.gz',info['gzip_sha256']);b=gzip.decompress(packed)
    require(hashlib.sha256(b).hexdigest()==info['raw_sha256']and len(b)==info['raw_bytes'],'prepared raw identity')
    p=json.loads(b)
    require(n['expected_inputs_sha256']==info['raw_sha256'],'native prepared identity')
    independent,scenes=read_inputs(PROJECT,p['entry'],baseline())
    return n,c,p,{g['path']:g for g in independent},scenes

def protected(g):
    # Protect by actual immutable saved resource bindings, not misleading species names.
    resource=g['resource']
    return ('coast61_-5_-5' if resource.startswith('res://assets/coast61/') and '_-5_-5' in resource else
            'coast56_-4_-4' if resource.startswith('res://assets/coast56/') and '_-4_-4' in resource else '')

def native_request(n,c):
    identities=sorted({g['mesh_resource']for g in c['groups']});require(len(identities)==6,'six target identities')
    req=[]
    for mesh in identities:
        g=next(g for g in n['groups']if g['mesh_resource']==mesh)
        main=n['mesh_resources'][mesh];shadow=main['shadow_mesh']
        req.append({'mesh_resource':mesh,'saved_multimesh':g['resource'],'group_path':g['path'],
                    'primary_surface_storage_sha256':main['surface_storage_sha256'],
                    'shadow_mesh_resource':shadow,'shadow_surface_storage_sha256':n['mesh_resources'][shadow]['surface_storage_sha256']if shadow else '',
                    'prior_metadata_bounds':main['combined_bounds_including_shadow'],
                    'primary_surfaces':main['surfaces'],'shadow_surfaces':n['mesh_resources'][shadow]['surfaces']if shadow else []})
    inspection=inspect_imported_resource(PROJECT/ROCK_CACHE[6:])
    require(inspection['class']=='PackedScene'and inspection['full_property_stream_boundaries_validated']and inspection['external']==[],'rock cache schema')
    primary=[x for x in inspection['internal_resources']if x['type']=='ArrayMesh'and 'shadow_mesh'in x['property_names']]
    require(len(primary)==1,'rock cache primary mesh ambiguous')
    primary_uri=ROCK_IMPORT+'::'+primary[0]['path'].removeprefix('local://')
    return {'rock_import_inspection':inspection,'rock_expected_primary_resource':primary_uri,'schema':'north62_proxy_mesh_read_v1','visual_meshes':req,'rock_prefab':ROCK_PREFAB,'rock_model_scene':ROCK_IMPORT,'rock_import_cache':ROCK_CACHE,
            'raw_saved_report_sha256':RAW_SHA,'classification_sha256':CLASS_SHA,'engine_version':'4.5.1.stable.official',
            'rules':{'tree_radius':2.4,'tree_height':11.,'tree_local_center':[0.,5.5,0.],'bush_proxy':None,
                     'rock':'first imported prefab mesh.get_faces(), mesh node transform is not applied by open_world.gd'},
            'world_instantiated':False,'runtime_collision_observed':False,'all_occupancy_complete':False}

def sha_ok(x):return type(x)is str and re.fullmatch(r'[0-9a-f]{64}',x)is not None

def positive_int(x):return type(x)is int and x>0

def contains(outer,inner):return bounds_ok(outer)and bounds_ok(inner)and all(outer['min'][i]<=inner['min'][i]<=inner['max'][i]<=outer['max'][i]for i in range(3))

def validate_mesh(item,expected_surfaces=None,allow_shadow=True):
    require(type(item)is dict and type(item.get('mesh_resource'))is str and item['mesh_resource'].startswith('res://'),'invalid mesh resource')
    require(sha_ok(item.get('surface_storage_sha256'))and sha_ok(item.get('face_bytes_sha256')),'invalid native hash')
    surfaces=item.get('surfaces');require(type(surfaces)is list and 0<len(surfaces)<=256,'native surfaces missing')
    require([s.get('index')for s in surfaces]==list(range(len(surfaces))),'surface indices')
    require(positive_int(item.get('vertex_count'))and positive_int(item.get('face_vertex_count'))and item['face_vertex_count']%3==0,'invalid vertex/face count')
    vertices=faces=0
    for s in surfaces:
        require(type(s.get('index'))is int and type(s.get('primitive'))is int and s.get('primitive')==3 and positive_int(s.get('vertex_count'))and type(s.get('index_count'))is int and s['index_count']>=0,'invalid surface counts')
        require(type(s.get('format'))is int and s['format']>0,'invalid surface format')
        require(sha_ok(s.get('vertex_bytes_sha256'))and bounds_ok(s.get('vertex_bounds')),'invalid surface identity/bounds')
        require((s['index_count']or s['vertex_count'])%3==0,'invalid triangle surface length')
        vertices+=s['vertex_count'];faces+=s['index_count']or s['vertex_count']
    require(vertices==item['vertex_count']and faces==item['face_vertex_count'],'mesh counts inconsistent')
    require(bounds_ok(item.get('vertex_bounds'))and item['vertex_bounds']==union(*(s['vertex_bounds']for s in surfaces)),'surface extrema union inconsistent')
    require(contains(item['vertex_bounds'],item.get('face_bounds')),'face extrema outside vertex domain')
    if expected_surfaces is not None:
        require(len(expected_surfaces)==len(surfaces),'surface count changed')
        for s,w in zip(surfaces,expected_surfaces):
            require(all(s[k]==w[k]for k in ['index','format','vertex_count','index_count']),'source-specific surface layout changed')
    shadow_uri=item.get('shadow_mesh_resource');shadow_sha=item.get('shadow_surface_storage_sha256')
    require(type(shadow_uri)is str and type(shadow_sha)is str,'missing shadow fields')
    if shadow_uri:
        require(allow_shadow and sha_ok(shadow_sha)and type(item.get('shadow'))is dict,'missing/recursive shadow')
        shadow=item['shadow'];validate_mesh(shadow,allow_shadow=False)
        require(shadow['mesh_resource']==shadow_uri and shadow['surface_storage_sha256']==shadow_sha,'shadow identity mismatch')
        combined=union(item['vertex_bounds'],shadow['vertex_bounds'])
    else:
        require(shadow_sha==''and 'shadow'not in item,'unexpected shadow data');combined=item['vertex_bounds']
    require(bounds_ok(item.get('combined_vertex_bounds'))and item['combined_vertex_bounds']==combined,'combined vertex bounds inconsistent')

def validate_native(value,request):
    require(value.get('passed')is True and value.get('issues')==[],'native mesh read failed')
    require(value.get('world_instantiated')is False and value.get('runtime_collision_observed')is False and value.get('all_occupancy_complete')is False,'native overclaims')
    actual=value.get('visual_meshes',[]);require(type(actual)is list and len(actual)==6,'native six visual meshes missing')
    require([x['mesh_resource']for x in actual]==[x['mesh_resource']for x in request['visual_meshes']],'native visual identity sequence')
    for item,want in zip(actual,request['visual_meshes']):
        validate_mesh(item,want['primary_surfaces'])
        require(item['surface_storage_sha256']==want['primary_surface_storage_sha256'],'native primary surface changed')
        require(item['shadow_mesh_resource']==want['shadow_mesh_resource'],'native shadow binding changed')
        require(item['shadow_surface_storage_sha256']==want['shadow_surface_storage_sha256'],'native shadow surface changed')
        if want['shadow_mesh_resource']:validate_mesh(item['shadow'],want['shadow_surfaces'],False)
    rock=value['rock'];validate_mesh(rock)
    require(rock['prefab']==ROCK_PREFAB and rock['imported_scene']==ROCK_IMPORT and rock['mesh_node_count']==1,'ambiguous rock source')
    require(rock['mesh_resource']==request['rock_expected_primary_resource'],'wrong imported rock mesh identity')
    require(rock['mesh_node_transform_applied_to_proxy']is False,'runtime rock transform semantics changed')
    nodes=rock.get('imported_node_inventory');require(type(nodes)is list and 0<len(nodes)<=32,'missing rock node inventory')
    require([n.get('index')for n in nodes]==list(range(len(nodes)))and len({n.get('path')for n in nodes})==len(nodes),'invalid rock node sequence')
    require(nodes[0].get('path')=='.'and all(n.get('type')in['Node3D','MeshInstance3D']for n in nodes),'unsupported rock topology')
    meshes=[n for n in nodes if n['type']=='MeshInstance3D'];require(len(meshes)==1,'rock mesh count mismatch')
    first=meshes[0];expected_path='Model'if first['path']=='.'else 'Model/'+first['path'].removeprefix('./')
    require(rock['first_mesh_node_path']==expected_path and first.get('mesh_resource')==rock['mesh_resource'],'rock first mesh path mismatch')
    transform=rock.get('mesh_node_transform_variant_hex');require(type(transform)is str and re.fullmatch('[0-9a-f]{104}',transform)is not None,'missing rock transform witness')
    return rock['face_bounds']

def analyze(native=None):
    before,guard=validate_dependencies();n,c,p,independent,scenes=load_saved();request=native_request(n,c)
    consulted=dict(before)
    for rel,pin in c['source_pins'].items():
        path=ROOT/rel;require(digest(path)==pin['sha256'],'classification source changed '+rel);consulted[str(path)]=pin['sha256']
    for path in [BASE/'dependency_guard62.py',BASE/'run_intake62.py',V1/'decoder62.py',V1/'scene_inputs62.py',V1/'build_inputs62.py',V1/'prepared-inputs.json.gz',V1/'prepared-inputs-identity.json',BASE/'scatter-hit-review-01/classification.json',BASE/'world-boundary-v1/upstream/core__math__transform_3d.h']:
        consulted[str(path)]=digest(path)
    rock_bounds=validate_native(native,request)if native else None
    vertex_bounds={x['mesh_resource']:x['combined_vertex_bounds']for x in native['visual_meshes']}if native else {}
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
                         'world_transform_columns':world,'visual_bounds':visual,'source_specific_vertex_world_bounds':source_vertices,'source_rule_proxy_bounds':proxy,'combined_conservative_bounds':envelope,
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

def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');args=ap.parse_args();result,request,identities=analyze()
    if args.prepare:
        (HERE/'source-bounds-preparation.json').write_bytes(encode(result));(HERE/'native-request.json').write_bytes(encode(request))
        (HERE/'immutable-source-inputs.json').write_bytes(encode(identities))
    print(json.dumps({k:v for k,v in result.items()if k not in ['groups','path_index_keep_reconcile','full_dependency_guard']},indent=2))
if __name__=='__main__':main()

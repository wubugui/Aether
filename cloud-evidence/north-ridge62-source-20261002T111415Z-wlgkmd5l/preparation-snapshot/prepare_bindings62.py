"""Offline four-tile binding preparation only; never starts an engine."""
import sys, importlib.util, argparse, gzip, json, base64
from pathlib import Path
sys.dont_write_bytecode=True
import numpy as np
from scipy.spatial import Delaunay,cKDTree
import contract62 as c

def load_preparation():
    spec=importlib.util.spec_from_file_location('frozen_preparation62',c.PREP/'prepare_authoring62.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def build_binding():
    c.require(c.sha(c.PREP/'FINAL_SHA256.json')==c.PREPARATION_SHA,'Frozen preparation manifest')
    freeze=c.read(c.PREP/'FINAL_SHA256.json')
    for path,row in freeze['files'].items():c.require(c.sha(c.PREP/path)==row['sha256'],'Preparation unchanged '+path)
    p=c.read(c.PREP/'candidate-plan.json');patch=c.read(c.PREP/'candidate-vertex-y.json');a=load_preparation()
    for path,row in p['source_pins'].items():c.require(c.sha(c.ROOT/path)==row['sha256'],'Frozen design input '+path)
    t=a.Terrain(c.read(a.TERRAIN));controls=p['controls'];dt=Delaunay(np.array([x['xz'] for x in controls]));c.require(dt.simplices.tolist()==p['control_triangles'],'Frozen triangulation')
    frozen=set();wet=[]
    for _,_,tri in t.tri:
        if not all(a.inside((q[0],q[2])) for q in tri):frozen.update((float(q[0]),float(q[2])) for q in tri)
        if tri[:,1].min()<=14:wet.append([tri[:,0].min()-80,tri[:,0].max()+80,tri[:,2].min()-80,tri[:,2].max()+80])
    for q in t.vertex_tiles:
        if a.inside(q) and any(b[0]<=q[0]<=b[1] and b[2]<=q[1]<=b[3] for b in wet):frozen.add(q)
    ft=cKDTree(np.array(sorted(frozen)));before=[];master_map={};tiles=[];master_faces=[];source_tri=[];owners=[]
    overrides={x['tile']:{tuple(r['before_xyz']):r['candidate_y'] for r in x['vertex_y_overrides']}for x in patch['tiles']}
    for tile_id,name in enumerate(c.TILES):
        tile=t.tiles[name];local_map={};ids=[];faces=[];corner_map=[];start=len(master_faces)
        for ti,tri in enumerate(tile['tri']):
            face=[]
            for j,q in enumerate(tri):
                key=tuple(map(float,q))
                if key not in master_map:master_map[key]=len(before);before.append(list(key))
                master_id=master_map[key]
                if master_id not in local_map:local_map[master_id]=len(ids);ids.append(master_id)
                face.append(local_map[master_id]);corner_map.append([ti,j,master_id,local_map[master_id]])
            bf=[face[0],face[2],face[1]];faces.append(bf);master_faces.append([ids[i] for i in bf]);source_tri.append(ti);owners.append(tile_id)
        tiles.append(dict(name=name,source_node=tile['node'],source_resource=tile['mesh'],source_origin=tile['origin'],master_vertex_ids=ids,faces_blender=faces,master_face_ids=list(range(start,len(master_faces))),source_triangle_corner_to_master_vertex=corner_map,changed_original_triangles=p['tiles'][name]['changed_original_triangles'],changed_unique_original_coordinates=len(overrides[name])))
    # Preserve original split GPU vertex slots and original triangle index ordering
    # on each derivative, while sharing one geometric controller/evaluated surface.
    c.mapping_authority()
    mapping_summary=c.read(c.HERE/'offline-mapping/mapping-summary.json')
    for path,row in mapping_summary['source_pins'].items():c.require(c.sha(c.ROOT/path)==row['sha256'],'Offline mapping input '+path)
    for tile in tiles:
        mapping=json.loads(gzip.decompress((c.HERE/'offline-mapping'/(tile['name']+'.mapping.json.gz')).read_bytes()))
        source=mapping['source'];rows=mapping['source_vertices'];indices=mapping['index_sequence']
        tile['master_vertex_ids']=[master_map[tuple(row['survey_world_xyz_json'])]for row in rows]
        tile['faces_blender']=np.asarray(indices,int).reshape(-1,3)[:,[0,2,1]].tolist()
        tile['source_triangle_corner_to_master_vertex']=[[k//3,k%3,tile['master_vertex_ids'][index],index]for k,index in enumerate(indices)]
        tile['original_source_local_xyz']=[row['source_local_xyz']for row in rows]
        tile['original_color_rgba8']=[row['source_color_rgba8']for row in rows]
        tile['original_color_float32']=[row['source_color_rgba_normalized_float32']for row in rows]
        tile['original_source_index_sequence']=indices
        tile['original_surface_identity']=source
        tile['original_packed_storage_base64']={name:base64.b64encode((c.HERE/'offline-mapping'/payload['file']).read_bytes()).decode()for name,payload in source['packed_payloads'].items()}
    point_binding={}
    for xyz in before:
        q=(xyz[0],xyz[2])
        if q in point_binding:continue
        si=int(dt.find_simplex(q));weights=[0.,0.,0.];ids=[0,1,2]
        if q not in frozen and si>=0:
            xy=dt.transform[si,:2].dot(np.array(q)-dt.transform[si,2]);weights=np.r_[xy,1-xy.sum()].tolist();ids=dt.simplices[si].tolist()
        u=min(1.,float(ft.query(q)[0])/72.);point_binding[q]=(ids,weights,u*u*(3-2*u),t.sample(*q))
    candidate=[];changed=[]
    for xyz in before:
        vals={overrides[name][tuple(xyz)] for name in c.TILES if tuple(xyz) in overrides[name]}
        c.require(len(vals)<=1,'Shared proposed source Y');candidate.append(next(iter(vals)) if vals else xyz[1]);changed.append(bool(vals))
    binding=dict(version=c.VERSION,origin_godot=c.ORIGIN,axis_map='Blender=(worldX-originX, -(worldZ-originZ), worldY); reverse Godot clockwise triangle [0,1,2] to Blender [0,2,1]',preparation_manifest_sha256=c.PREPARATION_SHA,controls=controls,control_faces_blender=[],before_xyz=before,candidate_y=candidate,changed=changed,control_ids=[],weights64=[],collar64=[],canonical_base_y=[],tiles=tiles,master_faces_blender=master_faces,master_source_triangles=source_tri,master_tile_ids=owners,native_vertex_index_mapping_proved=True,mapping_scope='All 24576 surface_get_arrays indexed corners exactly match offline original compressed vertex decoding plus float32 world transform. Four derivative meshes preserve original split vertex slots, index ordering, original local XYZ, RGBA8 and packed storage. Shared master weld is position-only authoring. No get_faces snapping. UV/UV2 absent. Normals/tangents remain archived original packed bytes; changed geometry derivatives are new source normals, not Godot output.',materials=c.MATERIALS,source_pins=p['source_pins'],support_pending_rows=167,world_integration_allowed=False)
    for xyz in before:
        ids,w,col,base=point_binding[(xyz[0],xyz[2])]
        for key,val in [('control_ids',ids),('weights64',w),('collar64',col),('canonical_base_y',base)]:binding[key].append(val)
    cv=c.local([[x['xz'][0],x['target_y'],x['xz'][1]] for x in controls])
    for f in p['control_triangles']:
        face=list(f)
        if np.cross(cv[face[1]]-cv[face[0]],cv[face[2]]-cv[face[0]])[2]<0:face=[face[0],face[2],face[1]]
        binding['control_faces_blender'].append(face)
    intake=c.read(c.ROOT/'source-assets/north-ridge62-intake/plan.json')
    binding['views']=[dict(name=key,kind='fixed_reference_source_geometry_only',**v)for key,v in intake['fixed_reference_views'].items()]
    binding['views'] += [dict(name='side',kind='diagnostic_only',eye=[-3840,690,-4740],target=[-2490,340,-4730],fov=55),dict(name='back',kind='diagnostic_only',eye=[-2460,790,-6060],target=[-2510,350,-4660],fov=55)]
    check=c.check_binding(binding);return binding,check

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();b,result=build_binding()
    if args.write:c.write(c.HERE/'bindings62.json',b);c.write(c.HERE/'BINDING_CHECK.json',result)
    print(c.json.dumps(result,sort_keys=True))
if __name__=='__main__':main()

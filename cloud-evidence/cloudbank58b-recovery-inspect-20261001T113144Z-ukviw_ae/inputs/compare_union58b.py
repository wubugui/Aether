"""Read True/False union sources; quantify changed outputs and unchanged inputs."""
import hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent;ON=B/'recovery-01';sys.path[:0]=[str(B),str(A)]
from verify58b import mesh_data
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources={'on':ON/'cloud_bank58b_union.blend','off':P/'cloud_bank58b_union.blend'}
before={k:sha(p) for k,p in sources.items()};rows={}
for label,source in sources.items():
    bpy.ops.wm.open_mainfile(filepath=str(source));bank=bpy.data.objects['CloudBank58B_four_root_folded_volume'];v,ids,tri=mesh_data(bank)
    controls={}
    for ob in bpy.data.collections['EDIT58B_closed_3d_fold_volumes'].objects:
        if ob.type=='MESH':
            cv,ci,ct=mesh_data(ob);controls[ob.name]=dict(v=cv,indices=ci,matrix=tuple(x for r in ob.matrix_world for x in r))
    rows[label]=dict(v=v,indices=ids,controls=controls)
assert set(rows['on']['controls'])==set(rows['off']['controls'])
control_proof=[]
for name,c in rows['on']['controls'].items():
    d=rows['off']['controls'][name];same=bool(np.array_equal(c['v'],d['v']) and np.array_equal(c['indices'],d['indices']) and c['matrix']==d['matrix'])
    control_proof.append(dict(name=name,vertices_faces_world_transform_exact=same))
same_topology=bool(np.array_equal(rows['on']['indices'],rows['off']['indices']) and rows['on']['v'].shape==rows['off']['v'].shape)
deltas=np.linalg.norm(rows['on']['v']-rows['off']['v'],axis=1) if same_topology else None
old=json.loads((ON/'union-geometry58b.json').read_text())['geometry'];new=json.loads((P/'union-geometry58b.json').read_text())['geometry']
old_bounds=np.array(old['world_bounds']);new_bounds=np.array(new['world_bounds']);volume_delta=(new['signed_volume_m3']-old['signed_volume_m3'])/old['signed_volume_m3']
after={k:sha(p) for k,p in sources.items()};assert before==after
report=dict(only_declared_geometry_intervention='use_remesh_preserve_volume True -> False; same11 native control meshes and26m voxel size',input_controls=control_proof,
            all_native_input_geometry_and_world_transforms_exact=all(r['vertices_faces_world_transform_exact'] for r in control_proof),source_hashes_before=before,source_hashes_after=after,
            control_recipe_bytes_equal=sha(ON/'native-control-input58b.json')==sha(P/'native-control-input58b.json'),output_triangle_topology_exact=same_topology,
            corresponding_output_vertex_offset_m=None if deltas is None else dict(max=float(deltas.max()),p95=float(np.percentile(deltas,95)),median=float(np.median(deltas))),
            old_volume_m3=old['signed_volume_m3'],new_volume_m3=new['signed_volume_m3'],relative_signed_volume_change=volume_delta,
            old_bounds=old['world_bounds'],new_bounds=new['world_bounds'],signed_bounds_delta_m=(new_bounds-old_bounds).tolist(),
            output_geometry_claimed_unchanged=False,source_geometry_only=True,rendered=False,world_loaded=False,visual_acceptance=False)
(P/'preserve-volume-intervention58b.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['all_native_input_geometry_and_world_transforms_exact'] and report['control_recipe_bytes_equal'],'Inputs changed beyond the single declared intervention'
print(json.dumps({k:report[k] for k in ('all_native_input_geometry_and_world_transforms_exact','output_triangle_topology_exact','corresponding_output_vertex_offset_m','relative_signed_volume_change','signed_bounds_delta_m')},indent=2),flush=True)

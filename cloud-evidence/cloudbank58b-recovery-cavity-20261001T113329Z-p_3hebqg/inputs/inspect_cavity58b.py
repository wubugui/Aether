"""Read-only origin/context of the8-vertex component; no geometry changes."""
import hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent;sys.path[:0]=[str(B),str(A)]
from verify58b import mesh_data
from verify58 import classify
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=P/'cloud_bank58b_union.blend';before=sha(source)
prior=json.loads((P/'actual-intersections58b.json').read_text());assert prior['source_sha256']==before
small=next(c for c in prior['connected_components'] if c['vertex_count']==8);small_ids=small['native_vertex_indices']
bpy.ops.wm.open_mainfile(filepath=str(source));ob=bpy.data.objects['CloudBank58B_four_root_folded_volume'];v,ids,tri=mesh_data(ob)
main=tri[~np.any(np.isin(ids,small_ids),axis=1)];points=v[small_ids];center=points.mean(0)
samples=[]
for label,point in [('center',center)]+[(f'component_vertex_{i}',p) for i,p in zip(small_ids,points)]:
    samples.append(dict(name=label,world=point.tolist(),against_main_closed_surface=classify(point,main)))
control_rows=[]
for control in bpy.data.collections['EDIT58B_closed_3d_fold_volumes'].objects:
    if control.type=='MESH':
        cv,ci,ct=mesh_data(control);control_rows.append(dict(name=control.name,center_against_native_control=classify(center,ct)))
whole=classify(center,tri)
internal=small['signed_volume_m3']<0 and all(s['against_main_closed_surface']['classification']=='inside' for s in samples) and whole['classification']=='outside'
report=dict(source_sha256=before,source_unchanged=before==sha(source),component=small,center_world=center.tolist(),
            samples_against_main=samples,center_against_complete_mesh=whole,native_control_context=control_rows,
            center_inside_controls=[r['name'] for r in control_rows if r['center_against_native_control']['classification']=='inside'],
            internal_negative_volume_cavity=bool(internal),absolute_cavity_to_main_volume_fraction=abs(small['signed_volume_m3'])/prior['connected_components'][0]['signed_volume_m3'],
            authored_void_controls_present=False,component_was_removed=False,rendered=False,world_loaded=False,visual_acceptance=False)
(P/'cavity-context58b.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['source_unchanged']
print(json.dumps({k:report[k] for k in ('source_unchanged','center_world','center_inside_controls','internal_negative_volume_cavity','absolute_cavity_to_main_volume_fraction')},indent=2),flush=True)

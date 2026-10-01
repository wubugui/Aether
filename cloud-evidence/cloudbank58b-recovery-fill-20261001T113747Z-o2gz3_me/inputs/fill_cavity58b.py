"""Explicit model repair: fill only the proven internal200m3 voxel cavity.

The entire main outer shell remains bit-exact in position and oriented polygons.
Original invalid union and controls remain in recovery02 without modification.
"""
import datetime,hashlib,json,shutil,sys,time
from collections import Counter
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent;ROOT=A.parents[1];OLD=B/'recovery-02'
sys.path[:0]=[str(B),str(A)]
from verify58b import geometry,mesh_data
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();start=time.monotonic();stages=[]


def stage(name,state):
    row=dict(operation=name,state=state,elapsed_seconds=time.monotonic()-start,utc=datetime.datetime.now(datetime.timezone.utc).isoformat());stages.append(row)
    (P/'union-stage58b.json').write_text(json.dumps(dict(complete=False,current_operation=name,stages=stages),indent=2)+'\n');print(json.dumps(row),flush=True)


assert not(P/'cloud_bank58b_union.blend').exists(),'Never overwrite a repaired source'
freeze=json.loads((OLD/'cavity-freeze58b.json').read_text());assert all(sha(ROOT/f)==r['sha256'] for f,r in freeze['files'].items())
proof=json.loads((OLD/'cavity-context58b.json').read_text());original=OLD/'cloud_bank58b_union.blend'
assert proof['internal_negative_volume_cavity'] and proof['source_sha256']==sha(original)
small=proof['component'];assert small['vertex_count']==8 and small['triangle_count']==12 and small['signed_volume_m3']<0
assert max(small['dimensions_m'])<9 and proof['absolute_cavity_to_main_volume_fraction']<2e-7
stage('read_frozen_source_and_exact_internal_shell','running')
bpy.ops.wm.open_mainfile(filepath=str(original));scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
bank=bpy.data.objects['CloudBank58B_four_root_folded_volume'];oldmesh=bank.data
before,bv,bi,bt,btree=geometry(bank);removed=set(small['native_vertex_indices']);keep=[i for i in range(len(oldmesh.vertices)) if i not in removed]
mapping={old:new for new,old in enumerate(keep)};old_vertices=[tuple(v.co) for v in oldmesh.vertices]
main_faces=[];removed_faces=[];face_attributes=[]
for face in oldmesh.polygons:
    ids=tuple(face.vertices)
    if set(ids).issubset(removed):removed_faces.append(dict(old_polygon_index=face.index,old_vertex_indices=list(ids)))
    else:
        assert not(set(ids)&removed),'The declared inner shell shares topology with the main shell'
        main_faces.append(ids);face_attributes.append((face.use_smooth,face.material_index))
assert len(removed_faces)==6 and all(len(r['old_vertex_indices'])==4 for r in removed_faces)
def canonical(ids,verts):
    row=tuple(verts[i] for i in ids);return min(row[i:]+row[:i] for i in range(len(row)))
main_signatures=Counter(canonical(f,old_vertices) for f in main_faces)
stage('read_frozen_source_and_exact_internal_shell','finished')
stage('remove_only_internal_shell_topology','running')
new=bpy.data.meshes.new(oldmesh.name+'_filled_internal_cavity')
new.from_pydata([old_vertices[i] for i in keep],[],[tuple(mapping[i] for i in face) for face in main_faces]);new.update()
for material in oldmesh.materials:new.materials.append(material)
for face,attributes in zip(new.polygons,face_attributes):face.use_smooth,face.material_index=attributes
bank.data=new
new_vertices=[tuple(v.co) for v in new.vertices]
vertices_exact=new_vertices==[old_vertices[i] for i in keep]
faces_exact=Counter(canonical(tuple(f.vertices),new_vertices) for f in new.polygons)==main_signatures
assert vertices_exact and faces_exact
stage('remove_only_internal_shell_topology','finished')
stage('check_exact_outer_shell_and_repaired_closed_geometry','running')
after,av,ai,at,atree=geometry(bank);assert after['closed_geometry_passed']
bounds_exact=after['world_bounds']==before['world_bounds'];volume_added=after['signed_volume_m3']-before['signed_volume_m3']
assert bounds_exact and abs(volume_added+small['signed_volume_m3'])<.01
bank['explicit_repair']='Only the proven8-vertex6-quad12-triangle internal negative shell removed; entire exterior unchanged.'
scene['source_method']=scene['source_method']+' Explicit fill of one proven200m3 internal voxel cavity; main exterior exact.'
stage('check_exact_outer_shell_and_repaired_closed_geometry','finished')
stage('save_repaired_union_pending_fresh_readback','running')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_bank58b_union.blend'))
stage('save_repaired_union_pending_fresh_readback','finished')
shutil.copy2(OLD/'native-control-input58b.json',P/'native-control-input58b.json')
repair=dict(action='Fill a proven internal negative-volume cavity by removing ONLY its closed inner shell',source_path=str(original.relative_to(ROOT)),source_sha256=sha(original),
            previous_source_unchanged=sha(original)==proof['source_sha256'],removed_native_vertex_indices=sorted(removed),removed_native_vertex_source_coordinates=[old_vertices[i] for i in sorted(removed)],
            removed_native_quad_faces=removed_faces,removed_triangle_count=12,main_old_to_new_vertex_index_map=mapping,main_outer_vertices_exact=vertices_exact,main_outer_oriented_polygons_exact=faces_exact,
            world_bounds_exact=bounds_exact,volume_added_m3=volume_added,expected_internal_cavity_volume_m3=-small['signed_volume_m3'],geometry_before=before,geometry_after=after,
            source_output_sha256=sha(P/'cloud_bank58b_union.blend'),main_outer_surface_moved=False,source_native_controls_changed=False,world_loaded=False,rendered=False,visual_acceptance=False)
(P/'explicit-cavity-fill58b.json').write_text(json.dumps(repair,indent=2)+'\n')
(P/'union-geometry58b.json').write_text(json.dumps(dict(native_union_geometry_passed=True,geometry=after,source_sha256=sha(P/'cloud_bank58b_union.blend'),
    original_controls_checkpoint=str((OLD/'cloud_bank58b_controls.blend').relative_to(ROOT)),controls_checkpoint_sha256=sha(OLD/'cloud_bank58b_controls.blend'),
    explicit_internal_cavity_fill=True,preserve_volume=False,quadriFlow_ran=False,rendered=False,world_loaded=False,visual_acceptance=False),indent=2)+'\n')
(P/'union-stage58b.json').write_text(json.dumps(dict(complete=True,current_operation='repaired_union_saved_pending_fresh_readback',stages=stages,world_loaded=False,visual_acceptance=False),indent=2)+'\n')
print('Repaired union saved; outer shell exact; filled200m3 interior only; fresh readback still required',flush=True)

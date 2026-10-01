"""Recover only the failed JSON proof from fresh old/new native sources.

No source save, reconstruction, geometry mutation or promotion of the failed run.
"""
import hashlib,json,sys
from collections import Counter
from pathlib import Path
import bpy,numpy as np
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent;ROOT=A.parents[1];OLD=B/'recovery-02'
sys.path[:0]=[str(P),str(B),str(A)]
from verify_final58b import geometry
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources={'before':OLD/'cloud_bank58b_union.blend','after':P/'cloud_bank58b_union.blend'};hashes={k:sha(p) for k,p in sources.items()}
cavity=json.loads((OLD/'cavity-context58b.json').read_text());assert cavity['internal_negative_volume_cavity'] and cavity['source_sha256']==hashes['before']
remove=set(cavity['component']['native_vertex_indices']);stored={}
for label,source in sources.items():
    bpy.ops.wm.open_mainfile(filepath=str(source));bank=bpy.data.objects['CloudBank58B_four_root_folded_volume'];row,*_=geometry(bank)
    stored[label]=dict(geometry=row,vertices=[tuple(v.co) for v in bank.data.vertices],faces=[tuple(f.vertices) for f in bank.data.polygons],matrix=tuple(x for r in bank.matrix_world for x in r),
                       face_attributes=[(f.use_smooth,f.material_index) for f in bank.data.polygons])
before=stored['before'];after=stored['after'];keep=[i for i in range(len(before['vertices'])) if i not in remove];mapping={old:new for new,old in enumerate(keep)}
main_faces=[];deleted=[];main_attrs=[]
for i,face in enumerate(before['faces']):
    if set(face).issubset(remove):deleted.append(dict(old_polygon_index=i,old_vertex_indices=list(face)))
    else:
        assert not(set(face)&remove);main_faces.append(face);main_attrs.append(before['face_attributes'][i])
vertices_exact=after['vertices']==[before['vertices'][i] for i in keep]
expected_faces=[tuple(mapping[i] for i in face) for face in main_faces]
ordered_faces_exact=after['faces']==expected_faces
attributes_exact=after['face_attributes']==main_attrs;matrix_exact=before['matrix']==after['matrix']
bounds_exact=before['geometry']['world_bounds']==after['geometry']['world_bounds']
volume_added=after['geometry']['signed_volume_m3']-before['geometry']['signed_volume_m3']
assert len(deleted)==6 and all(len(f['old_vertex_indices'])==4 for f in deleted)
assert vertices_exact and ordered_faces_exact and attributes_exact and matrix_exact and bounds_exact
assert after['geometry']['closed_geometry_passed'] and abs(volume_added+cavity['component']['signed_volume_m3'])<.01
assert hashes=={k:sha(p) for k,p in sources.items()}
repair=dict(action='Fill the proven internal negative-volume cavity by removing ONLY its closed inner shell',source_path=str(sources['before'].relative_to(ROOT)),source_sha256=hashes['before'],
            previous_source_unchanged=True,removed_native_vertex_indices=sorted(remove),removed_native_vertex_source_coordinates=[before['vertices'][i] for i in sorted(remove)],
            removed_native_quad_faces=deleted,removed_triangle_count=12,main_old_to_new_vertex_index_map=mapping,main_outer_vertices_exact=vertices_exact,
            main_outer_oriented_polygons_exact=ordered_faces_exact,main_outer_polygon_order_exact=ordered_faces_exact,main_outer_polygon_flags_exact=attributes_exact,object_transform_exact=matrix_exact,
            world_bounds_exact=bounds_exact,volume_added_m3=volume_added,expected_internal_cavity_volume_m3=-cavity['component']['signed_volume_m3'],
            geometry_before=before['geometry'],geometry_after=after['geometry'],source_output_sha256=hashes['after'],main_outer_surface_moved=False,source_native_controls_changed=False,
            recovered_from_fresh_saved_native_sources=True,original_failed_run_preserved='cloudbank58b-recovery-fill-20261001T113747Z-o2gz3_me',
            previous_failure='Saved native repair succeeded, then JSON serialization of a numpy.bool_ field failed; original wrapper remains1',rendered=False,world_loaded=False,visual_acceptance=False)
(P/'explicit-cavity-fill58b.json').write_text(json.dumps(repair,indent=2)+'\n')
(P/'union-geometry58b.json').write_text(json.dumps(dict(native_union_geometry_passed=True,geometry=after['geometry'],source_sha256=hashes['after'],
    original_controls_checkpoint=str((OLD/'cloud_bank58b_controls.blend').relative_to(ROOT)),controls_checkpoint_sha256=sha(OLD/'cloud_bank58b_controls.blend'),
    explicit_internal_cavity_fill=True,preserve_volume=False,quadriFlow_ran=False,rendered=False,world_loaded=False,visual_acceptance=False),indent=2)+'\n')
print(json.dumps(dict(main_outer_vertex_array_exact=vertices_exact,main_outer_ordered_polygon_array_exact=ordered_faces_exact,world_bounds_exact=bounds_exact,volume_added_m3=volume_added,
                     native_closed_repair_passed=after['geometry']['closed_geometry_passed'],source_files_unchanged=True,original_failure_preserved=True),indent=2),flush=True)

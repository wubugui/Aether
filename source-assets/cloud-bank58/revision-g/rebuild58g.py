"""Embedded Blender rebuild tool. Explicit Run Script rebuilds, never saves/renders.

Move/rotate/scale CONTROL58G empties and edit their field_strength properties.
The script reads the embedded field/config texts, so no external files or add-ons
are needed. It replaces only the named G surface after constructing a new mesh.
Manual vertex edits to that surface are replaced by an explicit regeneration.
"""
import hashlib
import json
from types import ModuleType
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

BANK_NAME='CloudBank58G_multiscale_field_shell'
CONTROL_COLLECTION='CONTROL58G_editable_field'


def field_module():
    module=ModuleType('embedded_field58g')
    exec(compile(bpy.data.texts['FIELD58G_patch.py'].as_string(),'FIELD58G_patch.py','exec'),module.__dict__)
    return module


def native_controls(config,frame):
    patch=field_module(); basis=patch.source_basis(frame)
    rows=[]
    for original in config['controls']:
        ob=bpy.data.objects['CONTROL58G_'+original['id']]
        assert ob.type=='EMPTY' and ob.parent is None and len(ob.constraints)==0
        matrix=np.asarray(ob.matrix_world,float)
        linear=basis.T@matrix[:3,:3]
        axes=np.linalg.norm(linear,axis=0)
        assert np.all(axes>0),'Control half-axes must stay positive'
        rotation=linear/axes
        assert np.max(np.abs(rotation.T@rotation-np.eye(3)))<2e-5 and np.linalg.det(rotation)>0,'No reflected or sheared controls'
        rows.append(dict(id=original['id'],role=original['role'],center_uvy_m=(basis.T@matrix[:3,3]).tolist(),
                         half_axes_m=axes.tolist(),axes_local=rotation.tolist(),strength=float(ob['field_strength'])))
    return rows


def geometry_arrays(bank):
    return np.asarray([list(v.co) for v in bank.data.vertices],float),np.asarray([list(p.vertices) for p in bank.data.polygons],np.int64)


def group_signature(bank):
    rows=[]
    for group in bank.vertex_groups:
        weights=[(v.index,float(g.weight)) for v in bank.data.vertices for g in v.groups if g.group==group.index]
        rows.append(dict(name=group.name,weights=weights))
    return hashlib.sha256(json.dumps(rows,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def sampled_offset(source_vertices,target_vertices,target_faces):
    tree=BVHTree.FromPolygons([Vector(v) for v in target_vertices],target_faces.tolist(),all_triangles=True)
    distances=[]
    for vertex in source_vertices:
        hit=tree.find_nearest(Vector(vertex))
        assert hit[0] is not None
        distances.append(float(hit[3]))
    return np.asarray(distances)


def rebuild_from_controls():
    assert bpy.context.mode=='OBJECT','Enter Object Mode before explicitly rebuilding the field controls'
    config=json.loads(bpy.data.texts['CONTROL58G.json'].as_string())
    frame=json.loads(bpy.context.scene['source_frame58g_json'])
    patch=field_module(); controls=native_controls(config,frame)
    spec=patch.extract(config,controls)
    raw=patch.source_coordinates(spec['vertices'],frame)
    mesh=bpy.data.meshes.new(BANK_NAME+'_rebuild_mesh')
    mesh.from_pydata(raw.astype(np.float32).tolist(),[],spec['faces'].tolist());mesh.update()
    previous=bpy.data.objects.get(BANK_NAME)
    had_previous=previous is not None
    fresh=bpy.data.objects.new(BANK_NAME+'_unaccepted_rebuild' if previous else BANK_NAME,mesh)
    bpy.data.collections['EDIT58G_surface'].objects.link(fresh)
    material=previous.data.materials[0] if previous and len(previous.data.materials) else bpy.data.materials.get('58G same neutral source inspection')
    if material:fresh.data.materials.append(material)
    fresh['collapse_applied58g']=False
    fresh['raw_extraction_proof58g_json']=json.dumps(dict(topology=spec['proof'],grid=spec['grid']),separators=(',',':'))
    bpy.ops.object.select_all(action='DESELECT');fresh.select_set(True);bpy.context.view_layer.objects.active=fresh
    target=int(config['meshing']['target_triangles'])
    assert len(mesh.polygons)>target,'Design grid no longer needs the one planned collapse; review rather than silently changing workflow'
    modifier=fresh.modifiers.new('One_limited_field_shell_collapse','DECIMATE')
    modifier.decimate_type='COLLAPSE';modifier.ratio=target/len(mesh.polygons)
    modifier.use_collapse_triangulate=True;modifier.use_symmetry=False
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    fresh['collapse_applied58g']=True
    for face in fresh.data.polygons:face.use_smooth=False
    final,faces=geometry_arrays(fresh)
    proof=patch.topology(final,faces)
    local=final@patch.source_basis(frame)
    contribution=patch.field(local,config,controls,contributions=True)
    weights=contribution/np.maximum(contribution.sum(axis=1,keepdims=True),1e-30)
    for index,control in enumerate(controls):
        group=fresh.vertex_groups.new(name='FIELD_'+control['id'])
        for vertex,weight in enumerate(weights[:,index]):
            if weight>1e-5:group.add([vertex],float(weight),'REPLACE')
    # Compact subset of true raw surface samples nearest each prescribed lobe's
    # exposed apex/shoulder turn. This is a sampled guard, not Hausdorff proof.
    raw_local=spec['vertices']; raw_weights=patch.field(raw_local,config,controls,contributions=True)
    landmark_ids=[]
    for i,control in enumerate(controls):
        if control['id']=='Wide_Oblique_Core':continue
        eligible=np.flatnonzero(raw_weights[:,i]>=.40*raw_weights.sum(axis=1))
        if not len(eligible):continue
        q=raw_local[eligible]
        landmark_ids.extend(int(eligible[np.argmax(q[:,axis]*sign)]) for axis in range(3) for sign in (-1,1))
    landmark_ids=sorted(set(landmark_ids))
    to_final=sampled_offset(raw,final,faces)
    to_raw=sampled_offset(final,raw,spec['faces'])
    offsets=dict(raw_vertex_to_final_max_m=float(to_final.max()),final_vertex_to_raw_max_m=float(to_raw.max()),
                 landmark_sample_count=len(landmark_ids),landmark_raw_vertex_ids=landmark_ids,
                 landmark_to_final_max_m=float(to_final[landmark_ids].max()) if landmark_ids else None,
                 basis='Preservation of extracted raw tetrahedral shell only, not distance to analytic density isosurface',
                 analytic_field_distance_proved=False,continuous_hausdorff_proof=False)
    limits=config['meshing']
    offsets['passed']=bool(landmark_ids and max(to_final.max(),to_raw.max())<=limits['maximum_sampled_surface_offset_m']
        and to_final[landmark_ids].max()<=limits['maximum_landmark_sample_offset_m']
        and proof['maximum_edge_m']<=limits['maximum_final_edge_m'])
    # Keep the generated candidate even if a later guard fails. No repair loop.
    accepted_basic=bool(proof['passed'] and offsets['passed'])
    if had_previous and accepted_basic:
        oldmesh=previous.data;bpy.data.objects.remove(previous,do_unlink=True)
        if oldmesh.users==0:bpy.data.meshes.remove(oldmesh)
    if not had_previous or accepted_basic:
        fresh.name=BANK_NAME;fresh.data.name=BANK_NAME+'_mesh'
    if mesh.users==0:bpy.data.meshes.remove(mesh)
    report=dict(raw_topology=spec['proof'],raw_grid=spec['grid'],final_topology=proof,
                mesh_identity=patch.fingerprint(final,faces),group_sha256=group_signature(fresh),
                sampled_shape_preservation=offsets,decimation_passes=1,target_triangles=target,
                passed=accepted_basic,previous_surface_retained=bool(had_previous and not accepted_basic),
                single_shared_field_surface=True,final_geometry_pass=False,visual_acceptance=False)
    fresh['source_method']='Finite-support multiscale ellipsoid density; shared-edge marching tetrahedra; one collapse; flat faces'
    fresh['edit_warning']='Run embedded EDIT58G_rebuild.py to regenerate from CONTROL58G empties. Explicit regeneration replaces manual surface edits; never auto-runs, saves or renders.'
    fresh['rebuild_report58g_json']=json.dumps(report,separators=(',',':'),allow_nan=False)
    fresh['control58g_json_sha256']=hashlib.sha256(bpy.data.texts['CONTROL58G.json'].as_string().encode()).hexdigest()
    return fresh,report


if __name__=='__main__':
    bank,report=rebuild_from_controls()
    print(json.dumps(report,indent=2))
    if not report['passed']:raise RuntimeError('Generated G candidate retained; basic or sampled guard failed. Do not save over accepted work automatically.')

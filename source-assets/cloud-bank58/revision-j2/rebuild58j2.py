"""Native editable rebuild entry. Explicit execution only; never saves/renders.

Run this embedded Text after editing the eight cage Empty transforms. Planes are
independently editable in CONTROL58J2.json. Failed construction leaves the prior
surface intact. This script is not run during source-only preparation.
"""
import hashlib
import json
from types import ModuleType
import bpy
import numpy as np

BANK_NAME='CloudBank58J2_authored_polyhedral_shell'
CONTROL_COLLECTION='CONTROL58J2_eight_authored_regions'


def load_embedded():
    module=ModuleType('embedded_poly58j2')
    exec(compile(bpy.data.texts['POLY58J2_math.py'].as_string(),'POLY58J2_math.py','exec'),module.__dict__)
    return module


def geometry_arrays(bank):
    return np.asarray([list(v.co) for v in bank.data.vertices]),np.asarray([list(p.vertices) for p in bank.data.polygons],int)


def group_signature(bank):
    rows=[(v.index,[(bank.vertex_groups[g.group].name,float(g.weight)) for g in v.groups]) for v in bank.data.vertices]
    return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()


def effective_config():
    poly=load_embedded();config=json.loads(bpy.data.texts['CONTROL58J2.json'].as_string())
    frame=json.loads(bpy.context.scene['source_frame58j2_json']);basis=poly.source_basis(frame)
    for row in config['controls']:
        ob=bpy.data.objects['CONTROL58J2_'+row['id']]
        matrix=np.asarray(ob.matrix_world);local_linear=np.linalg.inv(basis)@matrix[:3,:3]
        row['center']=(np.linalg.inv(basis)@matrix[:3,3]).tolist()
        row['scale']=[1.,1.,1.];row['matrix3']=local_linear.tolist()
    return poly,config,frame


def rebuild_from_controls():
    poly,config,frame=effective_config();candidate=poly.build(config)
    local=candidate['vertices'];source=local@poly.source_basis(frame).T
    native=source.astype(np.float32).astype(float)
    movement=np.linalg.norm(native-source,axis=1)
    poly.require(float(movement.max())<=config['tolerances']['float32_max_displacement_m'],'Float32 conversion movement')
    topology=poly.topology(native,candidate['faces'],config['tolerances'])
    intersections=poly.intersection_check(native,candidate['faces'],eps=1e-8)
    poly.require(set(candidate['owners'])=={row['id'] for row in config['controls']},'A semantic region is entirely hidden')
    mesh=bpy.data.meshes.new(BANK_NAME+'_mesh')
    mesh.from_pydata(native.tolist(),[],candidate['faces'].tolist());mesh.update()
    bank=bpy.data.objects.get(BANK_NAME)
    if bank is None:
        bank=bpy.data.objects.new(BANK_NAME,mesh);bpy.data.collections['EDIT58J2_surface'].objects.link(bank)
    else:
        old=bank.data;bank.data=mesh
        if old.users==0:bpy.data.meshes.remove(old)
        for group in list(bank.vertex_groups):bank.vertex_groups.remove(group)
    # Every seam station belongs to every adjacent semantic region. Face owner
    # remains one integer, preserving the actual original exposed plane.
    groups={row['id']:bank.vertex_groups.new(name='REGION_'+row['id']) for row in config['controls']}
    members={key:set() for key in groups}
    attr=mesh.attributes.new(name='semantic_region',type='INT',domain='FACE')
    panel=mesh.attributes.new(name='authored_plane',type='INT',domain='FACE')
    ids=[row['id'] for row in config['controls']]
    for i,(face,owner,panel_key) in enumerate(zip(candidate['faces'],candidate['owners'],candidate['panels'])):
        members[owner].update(map(int,face));attr.data[i].value=ids.index(owner)
        panel.data[i].value=int(panel_key.rsplit(':',1)[1]);mesh.polygons[i].use_smooth=False
    for name,indices in members.items():
        poly.require(bool(indices),'Completely hidden semantic region '+name)
        groups[name].add(sorted(indices),1.,'REPLACE')
    material=bpy.data.materials.get('58J2 same neutral source inspection')
    if material:mesh.materials.append(material)
    bank['candidate']='58J2';bank['visual_acceptance']=False
    proof=dict(passed=True,math_topology=candidate['proof'],native_float32_topology=topology,
        float32_maximum_displacement_m=float(movement.max()),native_coordinate_intersections=intersections,
        arithmetic_audit=candidate['audit'],effective_control_config=config,
        fingerprint=poly.fingerprint(native,candidate['faces']),final_world_geometry_pass=False,visual_acceptance=False)
    bank['construction_proof_json']=json.dumps(proof,separators=(',',':'))
    return bank,proof


if __name__=='__main__':
    bank,proof=rebuild_from_controls()
    print('Explicit 58J2 cage rebuild complete; unsaved and unrendered.',proof['native_float32_topology'])

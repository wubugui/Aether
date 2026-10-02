"""Native editable rebuild entry. Explicit execution only; never saves/renders.

Run this embedded Text after editing the six semantic Empty transforms. The
authored section/angle/diagonal recipe is independently editable in CONTROL58K.json. Failed construction leaves the prior
surface intact. This script is not run during source-only preparation.
"""
import hashlib
import json
from types import ModuleType
import bpy
import numpy as np

BANK_NAME='CloudBank58K_authored_polyhedral_shell'
CONTROL_COLLECTION='CONTROL58K_six_semantic_handles'


def load_embedded():
    module=ModuleType('embedded_poly58k')
    exec(compile(bpy.data.texts['POLY58K_math.py'].as_string(),'POLY58K_math.py','exec'),module.__dict__)
    return module


def geometry_arrays(bank):
    return np.asarray([list(v.co) for v in bank.data.vertices]),np.asarray([list(p.vertices) for p in bank.data.polygons],int)


def group_signature(bank):
    rows=[(v.index,[(bank.vertex_groups[g.group].name,float(g.weight)) for g in v.groups]) for v in bank.data.vertices]
    return hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()


def effective_config():
    poly=load_embedded();config=json.loads(bpy.data.texts['CONTROL58K.json'].as_string())
    frame=json.loads(bpy.context.scene['source_frame58k_json']);basis=poly.source_basis(frame)
    for row in config['controls']:
        ob=bpy.data.objects['CONTROL58K_'+row['id']]
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
    contact=ModuleType('embedded_contact58k')
    exec(compile(bpy.data.texts['CONTACT58K_check.py'].as_string(),'CONTACT58K_check.py','exec'),contact.__dict__)
    contacts=contact.check_coplanar_contacts(native,candidate['faces'],eps=1e-8)
    poly.require(not contacts['nonindexed_contact_violations'],'Nonindexed native contact')
    poly.require(contacts['aabb_pairs']==intersections['aabb_pairs_tested'] and contacts['coplanar_pairs']==intersections['coplanar_pairs_tested'],'Native contact coverage')
    poly.require(set(candidate['owners'])=={row['id'] for row in config['controls']},'A semantic region is entirely hidden')
    mesh=bpy.data.meshes.new(BANK_NAME+'_mesh')
    mesh.from_pydata(native.tolist(),[],candidate['faces'].tolist());mesh.update()
    bank=bpy.data.objects.get(BANK_NAME)
    if bank is None:
        bank=bpy.data.objects.new(BANK_NAME,mesh);bpy.data.collections['EDIT58K_surface'].objects.link(bank)
    else:
        old=bank.data;bank.data=mesh
        if old.users==0:bpy.data.meshes.remove(old)
        for group in list(bank.vertex_groups):bank.vertex_groups.remove(group)
    # Native vertex groups store the actual convex semantic deformation weights.
    groups={row['id']:bank.vertex_groups.new(name='REGION_'+row['id']) for row in config['controls']}
    attr=mesh.attributes.new(name='semantic_region',type='INT',domain='FACE')
    panel=mesh.attributes.new(name='authored_patch',type='INT',domain='FACE')
    station=mesh.attributes.new(name='authored_station',type='INT',domain='POINT')
    sector=mesh.attributes.new(name='authored_sector',type='INT',domain='POINT')
    ids=[row['id'] for row in config['controls']]
    for i,(face,owner,panel_key) in enumerate(zip(candidate['faces'],candidate['owners'],candidate['panels'])):
        attr.data[i].value=ids.index(owner)
        panel.data[i].value=int(panel_key.rsplit(':',1)[1]);mesh.polygons[i].use_smooth=False
    for v,w in enumerate(candidate['weights']):
        for i,weight in enumerate(w):
            if weight>0:groups[ids[i]].add([v],float(weight),'REPLACE')
        station.data[v].value=int(candidate['station_indices'][v]);sector.data[v].value=int(candidate['sector_indices'][v])
    material=bpy.data.materials.get('58K same neutral source inspection')
    if material:mesh.materials.append(material)
    bank['candidate']='58K';bank['visual_acceptance']=False
    proof=dict(passed=True,math_topology=candidate['proof'],native_float32_topology=topology,
        float32_maximum_displacement_m=float(movement.max()),native_coordinate_intersections=intersections,native_coordinate_contacts=contacts,
        arithmetic_audit=candidate['audit'],effective_control_config=config,
        fingerprint=poly.fingerprint(native,candidate['faces']),final_world_geometry_pass=False,visual_acceptance=False)
    bank['construction_proof_json']=json.dumps(proof,separators=(',',':'))
    return bank,proof


if __name__=='__main__':
    bank,proof=rebuild_from_controls()
    print('Explicit 58K envelope rebuild complete; unsaved and unrendered.',proof['native_float32_topology'])

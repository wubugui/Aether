"""Native editable rebuild entry. Explicit execution only; never saves/renders.

Run this embedded Text after editing the six semantic Empty transforms. The
authored section/angle/diagonal recipe is independently editable in CONTROL58K.json. Mathematical preflight precedes native replacement; later native failures can
leave the replacement partially authored and must not be saved as success. This script is not run during source-only preparation.
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


ATTRIBUTE_DOMAINS=(('semantic_region','FACE'),('authored_patch','FACE'),
                   ('authored_station','POINT'),('authored_sector','POINT'))


def require(ok,message):
    if not ok:raise ValueError(message)


def semantic_expectations(config):
    # Recipe-only expectations: no native mesh rebuild or replacement on readback.
    _,faces,weights,patch,stations,sectors=load_embedded().authored_arrays(config)
    owners=[]
    for face in faces:
        influence=weights[face].mean(axis=0)
        owners.append(5 if influence[5]>.28 else int(np.argmax(influence[:5])))
    return weights,dict(semantic_region=owners,authored_patch=list(map(int,patch)),
                       authored_station=list(map(int,stations)),authored_sector=list(map(int,sectors)))


def populate_native_semantics(bank,candidate,config):
    """No Attribute/Attribute.data handle crosses a structural mutation."""
    ids=[row['id'] for row in config['controls']]
    for name in ids:bank.vertex_groups.new(name='REGION_'+name)
    # Phase 1: finish every deform-layer/weight allocation before attributes.
    for v,weights in enumerate(candidate['weights']):
        for i,weight in enumerate(weights):
            if weight>0:bank.vertex_groups['REGION_'+ids[i]].add([v],float(weight),'REPLACE')
    # Phase 2: create every custom layer, deliberately retaining no RNA handle.
    for name,domain in ATTRIBUTE_DOMAINS:
        bank.data.attributes.new(name=name,type='INT',domain=domain)
    # Phase 3: fresh name lookup only after the last structural mutation.
    values=dict(semantic_region=[ids.index(owner) for owner in candidate['owners']],
                authored_patch=[int(key.rsplit(':',1)[1]) for key in candidate['panels']],
                authored_station=list(map(int,candidate['station_indices'])),
                authored_sector=list(map(int,candidate['sector_indices'])))
    for name,domain in ATTRIBUTE_DOMAINS:
        attribute=bank.data.attributes[name]
        require(attribute.domain==domain and attribute.data_type=='INT','Native attribute schema')
        require(len(attribute.data)==len(values[name]),'Native attribute population length')
        for i,value in enumerate(values[name]):attribute.data[i].value=value
        del attribute


def native_semantic_identity(bank,config):
    """Check every 194x6 slot and all 1,156 integer attribute values exactly."""
    expected,attributes=semantic_expectations(config)
    names=['REGION_'+row['id'] for row in config['controls']]
    require(expected.shape==(194,6),'Frozen K semantic dimensions')
    require([g.name for g in bank.vertex_groups]==names,'Native group names/order')
    require(len(bank.data.vertices)==194,'Frozen K native vertex count')
    actual=np.zeros(expected.shape,dtype='<f8');present=np.zeros(expected.shape,dtype=bool)
    # Only immutable Python numbers escape this read; no structural changes here.
    for v in bank.data.vertices:
        for member in v.groups:
            index=int(member.group);weight=float(member.weight)
            require(0<=index<6 and not present[v.index,index],'Invalid/duplicate native group index')
            require(np.isfinite(weight) and 0<=weight<=1,'Invalid native group weight')
            actual[v.index,index]=weight;present[v.index,index]=True
    expected32=np.asarray(expected,dtype='<f4')
    require(np.array_equal(present,expected>0),'Native membership differs from authored recipe')
    require(np.array_equal(actual,expected32.astype('<f8')),'Native weights differ from exact float32 recipe')
    actual_bytes=np.asarray(actual,dtype='<f4').tobytes()
    require(actual_bytes==expected32.tobytes(),'Native weight bytes differ')
    attribute_rows={}
    for name,domain in ATTRIBUTE_DOMAINS:
        attribute=bank.data.attributes[name]
        require(attribute.domain==domain and attribute.data_type=='INT','Native attribute schema')
        values=[int(d.value) for d in attribute.data]
        require(values==attributes[name],'Native attribute values differ: '+name)
        digest=hashlib.sha256(np.asarray(values,dtype='<i4').tobytes()).hexdigest()
        attribute_rows[name]=dict(domain=domain,data_type='INT',count=len(values),sha256=digest,
                                  exact_authored_recipe_match=True)
        del attribute
    return dict(passed=True,vertices=194,groups=6,weight_slots_checked=1164,
                stored_memberships=int(present.sum()),exact_float32_weights=True,
                weights_sha256=hashlib.sha256(actual_bytes).hexdigest(),
                membership_sha256=hashlib.sha256(present.astype('u1').tobytes()).hexdigest(),
                integer_attribute_values_checked=sum(len(v) for v in attributes.values()),
                attributes=attribute_rows)


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
    # Finish CustomData structural writes before looking up custom attributes.
    # VertexGroup.add may allocate CD_MDEFORMVERT; use_smooth may add sharp_face.
    material=bpy.data.materials.get('58K same neutral source inspection')
    if material:mesh.materials.append(material)
    for i in range(len(mesh.polygons)):mesh.polygons[i].use_smooth=False
    populate_native_semantics(bank,candidate,config)
    semantic_identity=native_semantic_identity(bank,config)
    bank['candidate']='58K';bank['visual_acceptance']=False
    proof=dict(passed=True,math_topology=candidate['proof'],native_float32_topology=topology,
        float32_maximum_displacement_m=float(movement.max()),native_coordinate_intersections=intersections,native_coordinate_contacts=contacts,
        arithmetic_audit=candidate['audit'],effective_control_config=config,
        fingerprint=poly.fingerprint(native,candidate['faces']),native_semantic_identity=semantic_identity,
        final_world_geometry_pass=False,visual_acceptance=False)
    bank['construction_proof_json']=json.dumps(proof,separators=(',',':'))
    return bank,proof


if __name__=='__main__':
    bank,proof=rebuild_from_controls()
    print('Explicit 58K envelope rebuild complete; unsaved and unrendered.',proof['native_float32_topology'])

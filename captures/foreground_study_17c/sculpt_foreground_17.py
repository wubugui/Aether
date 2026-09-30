"""Author western shoulder studies from the current native foreground assets."""
from pathlib import Path
import hashlib
import json
import math
import shutil
import sys
import bpy
import bmesh
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
LABEL = sys.argv[sys.argv.index('--')+1]
assert LABEL in ('17a', '17b', '17c')
OUT = ROOT/'captures'/('foreground_study_'+LABEL)
assert not OUT.exists(), OUT
OUT.mkdir()
shutil.copy2(__file__, OUT/Path(__file__).name)
catalog = {x['name']: x for x in json.loads((ROOT/'assets/cliff_kit.json').read_text())}
focal = 941/(2*math.tan(math.radians(25)))
pitch = math.radians(-3.526)
sun = Vector((-.48,-.30,.82)).normalized()

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def color(value):return np.array([int(value[i:i+2],16)/255 for i in (0,2,4)])
def linear(value):return np.where(value<=.04045,value/12.92,((value+.055)/1.055)**2.4)
def at_depth(u,v,z):
    y=(470.5-v)/focal
    ray=np.array([(u-836)/focal,math.cos(pitch)*y+math.sin(pitch),math.sin(pitch)*y-math.cos(pitch)])
    return np.array([0.,145.,250.])+ray*((z-250)/ray[2])

edits = {
    'cliff_western_slab': {11:(1192,735,-8),12:(1244,690,-14),13:(1290,727,-10)},
    'cliff_front_columns': {},
}
if LABEL == '17c':
    edits['cliff_western_slab'][14]=(1316,758,-5)
records=[]
for name,controls in edits.items():
    item=catalog[name]
    native=ROOT/item['native_source']
    source_hash=sha(native)
    source_glb_hash=sha(ROOT/item['path'])
    bpy.ops.wm.open_mainfile(filepath=str(native))
    obj=bpy.data.objects[name]
    assert np.allclose(np.array(obj.matrix_world),np.eye(4))
    mesh=obj.data
    prior=np.array([v.co[:] for v in mesh.vertices])
    floor={v.index for v in mesh.vertices if v.co.z < -14}
    rim=set()
    for edge in mesh.edges:
        a,b=edge.vertices
        if (a in floor)!=(b in floor):
            upper,lower=(b,a) if a in floor else (a,b)
            if np.linalg.norm(prior[upper,:2]-prior[lower,:2])<.001:rim.add(upper)
    assert rim and not set(controls)&(rim|floor)
    origin=np.array(item['position'])
    changes=[]
    for index,(u,v,dz) in controls.items():
        old=prior[index]
        world=old[[0,2,1]]*[1,1,-1]+origin
        target=at_depth(u,v,world[2]+dz)-origin
        mesh.vertices[index].co=(target[0],-target[2],target[1])
        changes.append({'index':index,'before':old.tolist(),'after':list(mesh.vertices[index].co),
            'survey_uv':[u,v],'depth_offset_m':dz})
    if LABEL in ('17b','17c'):
        selected = ((16,17,18,19) if LABEL=='17c' else (16,17,18)) if name == 'cliff_western_slab' else (5,6)
        for index in selected:
            if name == 'cliff_western_slab':
                point=mesh.vertices[index-5].co.lerp(mesh.vertices[index+5].co,.5)
                point.z += [-1.,2.,0.,0.][index-16]
                mesh.vertices[index].co=point
            else:
                mesh.vertices[index].co.z={5:41.,6:38.}[index]
            changes.append({'index':index,'before':prior[index].tolist(),'after':list(mesh.vertices[index].co),
                'survey_uv':None,'depth_offset_m':None,
                'authoring_rule':'Rear shoulder interpolates between deeper crest and original rear toe, with unequal height offsets.' if name=='cliff_western_slab' else 'Raise the middle wall break while keeping its safe XZ corridor.'})
    mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    added_controls=[]
    if LABEL in ('17b','17c') and name=='cliff_front_columns':
        bm.verts.ensure_lookup_table()
        a,b,c,d=[bm.verts[i] for i in (5,6,10,9)]
        old_faces=[f for f in bm.faces if set(f.verts)<=set((a,b,c,d))]
        assert len(old_faces)==2
        _,lower=bmesh.utils.edge_split(bm.edges.get((a,b)),a,.5)
        _,upper=bmesh.utils.edge_split(bm.edges.get((d,c)),d,.5)
        lower.co=(a.co+b.co)*.5+Vector((0.,-.6,0.))
        upper.co=(d.co+c.co)*.5+Vector((0.,-1.6,0.))
        bmesh.ops.delete(bm,geom=old_faces,context='FACES_ONLY')
        role_layer=bm.faces.layers.int.get('Geological section')
        for vertices in ([a,lower,upper,d],[lower,b,c,upper]):
            face=bm.faces.new(vertices);face[role_layer]=1
        unused=[edge for edge in bm.edges if not edge.link_faces]
        if unused:bmesh.ops.delete(bm,geom=unused,context='EDGES')
        added_controls=[{'role':'middle wall buttress','blender_xyz':list(lower.co)},
                        {'role':'front wall buttress','blender_xyz':list(upper.co)}]
        bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3])
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(len(edge.link_faces)==2 for edge in bm.edges)
    assert all(face.calc_area()>1e-8 for face in bm.faces)
    volume=bm.calc_volume(signed=True)
    assert volume>0
    bm.to_mesh(mesh);bm.free();mesh.update()
    zones=mesh.attributes['Geological section']
    palette=mesh.color_attributes['Palette']
    painted=[]
    for face in mesh.polygons:
        role=zones.data[face.index].value
        indices=set(face.vertices)
        if name=='cliff_western_slab':
            if not indices&set(range(5,20)):continue
        elif not indices&set(range(4,16)):
            continue
        light=max(0,face.normal.dot(sun))
        if role==0:
            if LABEL in ('17b','17c'):
                up=max(0,face.normal.z)
                brightness=np.clip(.10+.75*up+.15*light,0,1)
                pigment=color('6c8467')*(1-brightness)+color('b0bc80')*brightness
            else: pigment=color('bec381')*(.84+.16*light)
        elif role==1:
            pigment=color('a5a0a0')*(1-light)+color('beb5ab')*light
        elif role==2:
            pigment=color('899775')*(.76+.24*light)
        else:continue
        for loop in face.loop_indices:palette.data[loop].color=(*linear(pigment),1)
        painted.append(face.index)
    points={tuple(v.co) for v in mesh.vertices}
    assert all(tuple(prior[i]) in points for i in rim|floor)
    obj['study_version']=LABEL
    obj['source_native_sha256']=source_hash
    obj['closed_volume_m3']=volume
    obj['production_modified']=False
    if controls:obj.vertex_groups.new(name=LABEL+' western shoulder').add(list(controls),1,'REPLACE')
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    glb=OUT/(name+'.glb');blend=OUT/(name+'.blend')
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    assert sha(native)==source_hash and sha(ROOT/item['path'])==source_glb_hash
    records.append({'name':name,'path':str(glb.relative_to(ROOT)),'native_source':str(blend.relative_to(ROOT)),
        'source_sha256':source_hash,'source_glb_sha256':source_glb_hash,'glb_sha256':sha(glb),'blend_sha256':sha(blend),
        'vertices':len(mesh.vertices),'triangles':len(mesh.polygons),'volume_m3':volume,
        'unchanged_rim_vertices':len(rim),'unchanged_floor_vertices':len(floor),'controls':changes,
        'added_controls':added_controls,
        'repainted_faces':painted,'production_modified':False,
        'validation_scope':'Native closed edges, positive area/volume, exact rim/floor retention. Separate exported surface gate and raw GPU review required.'})
    print('FOREGROUND CANDIDATE '+name,flush=True)
(OUT/'manifest.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print('FOREGROUND BUILD COMPLETE '+str(OUT),flush=True)

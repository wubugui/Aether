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
assert LABEL == '17a'
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
    mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    assert all(len(edge.link_faces)==2 for edge in bm.edges)
    assert all(face.calc_area()>1e-8 for face in bm.faces)
    volume=bm.calc_volume(signed=True)
    assert volume>0
    bm.free()
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
            pigment=color('bec381')*(.84+.16*light)
        elif role==1:
            pigment=color('a5a0a0')*(1-light)+color('beb5ab')*light
        elif role==2:
            pigment=color('899775')*(.76+.24*light)
        else:continue
        for loop in face.loop_indices:palette.data[loop].color=(*linear(pigment),1)
        painted.append(face.index)
    assert np.array_equal(prior[list(rim|floor)],np.array([v.co[:] for v in mesh.vertices])[list(rim|floor)])
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
        'repainted_faces':painted,'production_modified':False,
        'validation_scope':'Native closed edges, positive area/volume, exact rim/floor retention. Separate exported surface gate and raw GPU review required.'})
    print('FOREGROUND CANDIDATE '+name,flush=True)
(OUT/'manifest.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print('FOREGROUND BUILD COMPLETE '+str(OUT),flush=True)

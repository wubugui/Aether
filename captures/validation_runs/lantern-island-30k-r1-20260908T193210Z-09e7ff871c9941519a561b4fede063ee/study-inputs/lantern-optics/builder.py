"""Editable optical control volumes, separate from the protected19h lighthouse."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];OUT=R/'captures/lantern_volume_assets_28a'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
rows=[]
def reset():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def save(name):
    parts=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        assert all(e.is_manifold for e in bm.edges) and all(f.calc_area()>1e-9 for f in bm.faces)
        vol=bm.calc_volume(signed=True);assert vol>0
        bm.to_mesh(obj.data);parts.append({'name':obj.name,'vertices':len(bm.verts),'faces':len(bm.faces),'volume_m3':vol});bm.free()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',export_yup=True,export_animations=False)
    rows.append({'asset':name,'parts':parts,'source_sha256':hashlib.sha256((OUT/(name+'.blend')).read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((OUT/(name+'.glb')).read_bytes()).hexdigest()})
reset();points=[];faces=[];rings=[0.,60.,180.,350.,560.];count=32
# Blender+Y becomes Godot-Z. Source has literal metre dimensions, no billboard.
for distance in rings:
    radius=.8+distance*.09
    for k in range(count):
        angle=2*math.pi*k/count;points.append((radius*math.cos(angle),distance,radius*math.sin(angle)))
faces.append(tuple(reversed(range(count))))
for j in range(len(rings)-1):
    for k in range(count):faces.append((j*count+k,j*count+(k+1)%count,(j+1)*count+(k+1)%count,(j+1)*count+k))
faces.append(tuple((len(rings)-1)*count+k for k in range(count)))
mesh=bpy.data.meshes.new('Closed lantern optical frustum mesh');mesh.from_pydata(points,[],faces);mesh.update()
obj=bpy.data.objects.new('Lantern beam closed world volume 560m',mesh);bpy.context.collection.objects.link(obj)
save('lantern_beam')
reset();bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1.45)
bpy.context.object.name='Lantern luminous haze closed sphere 1.45m';save('lantern_halo')
(OUT/'model-report.json').write_text(json.dumps({'scope':'Independent editable Blender optical control volumes. Runtime integrates density inside their true3D interior and clips to camera depth and sampled light-space scene occlusion. Native19h lighthouse is unchanged; these are not camera-facing image planes.','assets':rows},indent=2),encoding='utf-8')
print('LANTERN OPTICAL VOLUMES BUILT',flush=True)

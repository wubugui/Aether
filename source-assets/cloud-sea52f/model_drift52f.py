"""Second additive connector, after parent's actual first-source five-face review."""
import bpy,bmesh,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
PREVIOUS=P/'cloud_sea52f.blend'
protected=[PREVIOUS,P.parent/'cloud-sea52e/cloud_sea52e.blend',
 ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend',
 ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52e/Game52e.tscn',
 ROOT/'candidates/round40-exclusive-20260930/project/project.godot']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.open_mainfile(filepath=str(PREVIOUS))
# Independent curved layout, turning from rear/tail boundary to the shoulder edge.
# Vary belly height as well as top height; medium lobes sit partly within the spine.
# role, x, y, z, rx, ry, rz, yaw
volumes=[
 ('low_start', -534,478,-53,156,143,104,-26),
 ('rear_swell',-364,588,-30,164,172,115, 21),
 ('low_trough',-146,618,-89,169,157, 93,-31),
 ('tail_return', 49,515,-44,167,155,115, 24),
 ('turn',       211,373,-12,150,170,128,-34),
 ('low_outer',  381,295,-58,164,148, 93, 18),
 ('falling_end',561,230,-92,133,125, 75,-27),
 # Unequal shoulder groups climb along the old tail and right shoulder.
 ('medium_rear_shoulder',-476,566,29, 83,92,75,-14),
 ('medium_rear_shoulder',-345,641,59, 93,87,69, 25),
 ('medium_rear_shoulder',-244,593,11, 86,82,77,-21),
 ('medium_inner_shoulder',-44,472,44, 79,87,91, 18),
 ('medium_inner_shoulder', 91,387,59, 90,91,81,-26),
 ('medium_turn_shoulder',226,291,86, 80,84,79, 34),
 ('medium_outer_shoulder',332,372,25, 85,78,63,-19),
 ('medium_end_shoulder',450,231,-3, 82,79,71, 28),
 # Small scallops, concentrated in the rising shoulder and falling outer edge.
 ('small_rear_edge',-562,553,39,42,39,38, 13),
 ('small_rear_edge',-415,676,79,37,39,32,-24),
 ('small_rear_edge',-309,716,71,36,39,34, 17),
 ('small_rear_edge',-248,666,48,40,36,33,-15),
 ('small_turn_edge', 38,397,112,35,37,36, 23),
 ('small_turn_edge',135,328,97,39,33,38,-18),
 ('small_turn_edge',218,225,119,37,36,39, 27),
 ('small_outer_edge',287,475,23,42,36,34,-33),
 ('small_outer_edge',411,406,-7,39,36,35, 21),
 ('small_end_edge',544,327,-39,36,39,33,-25),
 # Curved lower returns break any shared ceiling plane in an underside view.
 ('belly_return',-435,507,-135,88,96,63, 19),
 ('belly_return',-182,650,-150,99,92,58,-22),
 ('belly_return', 60,484,-141,78,90,62, 31),
 ('belly_return',249,414,-112,88,84,68,-17),
 ('belly_return',495,258,-140,77,88,57, 24),
]
col=bpy.data.collections['cloud_sea_52f_prototype']
controls=bpy.data.collections.new('Editable52f_v0_low_drift_controls')
bpy.context.scene.collection.children.link(controls);copies=[]
for i,(role,cx,cy,cz,rx,ry,rz,heading) in enumerate(volumes):
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=4,radius=1)
    ca,sa=math.cos(math.radians(heading)),math.sin(math.radians(heading))
    for v in bm.verts:
        q=v.co.copy();a=math.atan2(q.y,q.x)
        radial=1+.022*math.sin(a*3+i*.72)*(1-q.z*q.z)
        x=q.x*rx*radial;y=q.y*ry*radial;z=q.z*rz*(1+.022*math.sin(a*2+i))
        v.co=(cx+x*ca-y*sa,cy+x*sa+y*ca,cz+z)
    me=bpy.data.meshes.new(f'52f_v0_drift_{i}_{role}');bm.to_mesh(me);bm.free()
    cage=bpy.data.objects.new(f'CONTROL52f_v0_drift_{i:02d}_{role}',me)
    controls.objects.link(cage);cage['volume_parameters']=json.dumps(volumes[i]);cage['role']=role;cage.hide_render=True
    work=bpy.data.objects.new(f'work52f_drift_{i}',me.copy());col.objects.link(work);copies.append(work)
bpy.ops.object.select_all(action='DESELECT')
for ob in copies:ob.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=copies[0];ob.name='CloudSea52f_v0_low_drift'
m=ob.modifiers.new('Closed turning drift volume union','REMESH');m.mode='VOXEL';m.voxel_size=5.5;m.use_smooth_shade=False
bpy.ops.object.modifier_apply(modifier=m.name)
bm=bmesh.new();bm.from_mesh(ob.data);todo=set(bm.verts);components=[]
while todo:
    stack=[todo.pop()];part=[]
    while stack:
        v=stack.pop();part.append(v)
        for e in v.link_edges:
            w=e.other_vert(v)
            if w in todo:todo.remove(w);stack.append(w)
    components.append(part)
components.sort(key=len,reverse=True);fragments=[]
for part in components[1:]:
    lo=[min(v.co[k] for v in part) for k in range(3)];hi=[max(v.co[k] for v in part) for k in range(3)]
    assert max(hi[k]-lo[k] for k in range(3))<22 and len(part)<150,'Meaningful disconnected volume requires resculpt'
    fragments.append({'vertices':len(part),'bounds':[lo,hi]});bmesh.ops.delete(bm,geom=part,context='VERTS')
bm.to_mesh(ob.data);bm.free()
m=ob.modifiers.new('Blend shoulders into curved lower spine','SMOOTH');m.factor=.75;m.iterations=3
bpy.ops.object.modifier_apply(modifier=m.name)
tri=sum(len(f.vertices)-2 for f in ob.data.polygons);m=ob.modifiers.new('Preserve silhouette scale hierarchy','DECIMATE');m.ratio=min(1,3400/tri)
bpy.ops.object.modifier_apply(modifier=m.name)
mat=bpy.data.objects['CloudSea52e_v0_main_ridge'].data.materials[0];ob.data.materials.append(mat)
colors=ob.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in ob.data.polygons:
    f.use_smooth=False;z=sum(ob.data.vertices[k].co.z for k in f.vertices)/len(f.vertices)
    v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
    for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
controls.hide_render=True;controls.hide_viewport=True
ob['construction']='Curved trailing drift with staggered swells, shoulders and lower returns'
ob['source_status']='Second representative connector, awaiting actual five-face review'
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for item in objects:item.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(P/name),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
saddle=bpy.data.objects['CloudSea52f_v0_low_saddle'];uppers=list(bpy.data.collections['cloud_sea_52e_0'].objects)
export('cloud_sea_52f_drift_v0.glb',[ob])
export('cloud_sea_52f_pair_v0.glb',[saddle,ob])
export('cloud_sea_52f_two_body_v0.glb',uppers+[saddle,ob])
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52f_two_body.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources52f-drift.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'layout52f-drift.json').write_text(json.dumps({'status':'Second connector only; no world or three-variant acceptance',
 'reviewed_first_source':str(PREVIOUS),'first_five_face_run':'cloud-evidence/cloudsea52f-source-v0-20261001T061523Z-6lh8fn8v',
 'new_body':ob.name,'new_controls':len(volumes),'volumes':volumes,'removed_tiny_voxel_fragments':fragments,
 'old_upper_meshes_changed':False,'first_saddle_changed':False,'world_integration':False,'visual_acceptance':False},indent=2)+'\n')
print('52F SECOND CONNECTOR READY; NO RENDER OR WORLD INTEGRATION')

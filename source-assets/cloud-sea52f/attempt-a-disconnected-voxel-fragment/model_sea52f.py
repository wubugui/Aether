"""Build only the first additive low-saddle prototype. No scene integration or render."""
import bpy, bmesh, hashlib, json, math
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
PREVIOUS = P.parent/'cloud-sea52e/cloud_sea52e.blend'
protected = [PREVIOUS, ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend',
             ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52e/Game52e.tscn',
             ROOT/'candidates/round40-exclusive-20260930/project/project.godot']
protected += [p for p in (P.parent).glob('cloud-sea*/**/*.blend') if p.parent != P]
before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.open_mainfile(filepath=str(PREVIOUS))
for c in bpy.data.collections:
    if c.name.startswith('cloud_sea_52e_'):
        c.hide_render = not c.name.endswith('_0')
        c.hide_viewport = not c.name.endswith('_0')

# Local coordinates are Blender X/Y horizontal, Z vertical.
# Individually authored unequal bends and fork; no common planar base, no noise scatter.
# role, x, y, z, rx, ry, rz, heading_deg
volumes = [
 ('low_core', -485,-12,-22,174,181,104,-18),
 ('low_core', -282,-65, -3,178,178,115, 22),
 ('low_core',  -79, -1,  4,166,165,109,-26),
 ('low_core',  133,-52,-13,174,154,103, 17),
 ('low_core',  326,-81,  9,177,168,124,-23),
 ('low_end',   511,-165,-35,127,140, 79, 28),
 ('fork',     -269,137,-32,143,153, 92,-35),
 ('fork_end', -164,247,-61,115,109, 68, 14),
 # Offset shoulders climbing partway up the preserved upper crowns.
 ('medium_shoulder',-338,-173, 60,100,107,91, 18),
 ('medium_shoulder',-245,-177,100, 73, 86,86,-26),
 ('medium_shoulder',-150,-111, 82, 83, 71,68, 29),
 ('medium_shoulder', -83,  68, 79, 71, 82,57,-17),
 ('medium_shoulder',  52,  89, 42, 96, 80,70,  9),
 ('medium_shoulder', 216,  62, 95, 78, 81,73,-24),
 ('medium_shoulder', 361,  54,110, 88, 91,83, 27),
 ('medium_shoulder', 452,-152, 68, 70, 80,73,-16),
 ('medium_shoulder',-450, 102, 42, 91, 74,64, 24),
 ('medium_shoulder',-242, 227, 20, 76, 82,54,-29),
 # Small lobes belong to three asymmetrical shoulder/valley groups.
 ('small_crown_edge',-321,-239,119,42,38,42, 17),
 ('small_crown_edge',-238,-222,162,37,34,34,-25),
 ('small_crown_edge',-186,-177,132,31,38,39, 36),
 ('small_valley',-149, -31,112,43,39,37,-14),
 ('small_valley', -91, 113,101,36,42,30, 23),
 ('small_valley', -26, 140, 75,31,33,31,-34),
 ('small_shoulder_edge',274, 117,112,39,42,39, 31),
 ('small_shoulder_edge',353, 137,123,35,37,36,-16),
 ('small_shoulder_edge',421,  91,137,40,33,35, 12),
 ('small_shoulder_edge',459, -66,104,32,36,28,-21),
 ('small_fork_edge',-329,244,45,42,35,38, 24),
 ('small_fork_edge',-263,298,29,34,36,31,-33),
 ('small_fork_edge',-191,323,-10,30,32,28, 18),
]

col = bpy.data.collections.new('cloud_sea_52f_prototype')
bpy.context.scene.collection.children.link(col)
controls = bpy.data.collections.new('Editable52f_v0_low_saddle_controls')
bpy.context.scene.collection.children.link(controls)
copies=[]
for i, (role,cx,cy,cz,rx,ry,rz,heading) in enumerate(volumes):
    bm=bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1)
    ca,sa=math.cos(math.radians(heading)),math.sin(math.radians(heading))
    for v in bm.verts:
        q=v.co.copy(); angle=math.atan2(q.y,q.x)
        # Low-amplitude asymmetry only; actual hierarchy comes from volume sizes.
        radial=1+.024*math.sin(angle*3+i*.72)*(1-q.z*q.z)
        x=q.x*rx*radial; y=q.y*ry*radial
        z=q.z*rz*(1+.025*math.sin(angle*2+i))
        v.co=(cx+x*ca-y*sa,cy+x*sa+y*ca,cz+z)
    mesh=bpy.data.meshes.new(f'52f_v0_saddle_{i}_{role}')
    bm.to_mesh(mesh);bm.free()
    cage=bpy.data.objects.new(f'CONTROL52f_v0_saddle_{i:02d}_{role}',mesh)
    controls.objects.link(cage);cage['volume_parameters']=json.dumps(volumes[i])
    cage['role']=role;cage.hide_render=True
    work=bpy.data.objects.new(f'work52f_saddle_{i}',mesh.copy())
    col.objects.link(work);copies.append(work)
bpy.ops.object.select_all(action='DESELECT')
for ob in copies:ob.select_set(True)
bpy.context.view_layer.objects.active=copies[0]
bpy.ops.object.join();ob=copies[0];ob.name='CloudSea52f_v0_low_saddle'
m=ob.modifiers.new('Local closed saddle volume union','REMESH')
m.mode='VOXEL';m.voxel_size=5.5;m.use_smooth_shade=False
bpy.ops.object.modifier_apply(modifier=m.name)
m=ob.modifiers.new('Round joins retain grouped small shoulders','SMOOTH')
m.factor=.7;m.iterations=2;bpy.ops.object.modifier_apply(modifier=m.name)
tri=sum(len(f.vertices)-2 for f in ob.data.polygons)
m=ob.modifiers.new('Varied low-poly facets retain shoulder hierarchy','DECIMATE')
m.ratio=min(1,3600/tri);bpy.ops.object.modifier_apply(modifier=m.name)
mat=bpy.data.objects['CloudSea52e_v0_main_ridge'].data.materials[0]
ob.data.materials.append(mat)
colors=ob.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in ob.data.polygons:
    f.use_smooth=False
    z=sum(ob.data.vertices[k].co.z for k in f.vertices)/len(f.vertices)
    v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
    for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
ob['source_status']='Unreviewed additive prototype only, not a world candidate'
ob['construction']='Unequal bent low spine, down-sloping fork, grouped medium and small shoulders'
controls.hide_render=True;controls.hide_viewport=True

def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(P/name),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
export('cloud_sea_52f_connector_v0.glb',[ob])
old_v0=list(bpy.data.collections['cloud_sea_52e_0'].objects)
export('cloud_sea_52f_prototype_v0.glb',old_v0+[ob])
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52f.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
assert before==after,'Protected source changed'
(P/'protected-sources.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'layout52f.json').write_text(json.dumps({
 'status':'One representative connector only; pending five-face review before expansion',
 'retained_source':str(PREVIOUS),'old_upper_meshes_changed':False,'old_controls_retained':66,
 'new_body':ob.name,'new_controls':len(volumes),'volumes':volumes,
 'export_axis_mapping':'Blender (x,y,z) to glTF/Godot (x,z,-y)',
 'vertex_color_formula':'v=.76+.16*clamp((Blender_Z+190)/460,0,1); linear=((v+.055)/1.055)**2.4',
 'material':mat.name,'voxel_size_m':5.5,'triangle_target':3600,
 'world_integration':False,'visual_acceptance':False
},indent=2)+'\n')
print('52F REPRESENTATIVE SADDLE READY; NO RENDER OR WORLD INTEGRATION')

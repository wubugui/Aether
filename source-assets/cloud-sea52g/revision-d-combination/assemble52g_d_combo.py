"""Only D main replaces originalv0 main; append original other two uppers and lows."""
import bpy,bmesh,json,hashlib,struct
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
OLD=P.parent.parent/'cloud-sea52f/variants/cloud_sea52f_variants.blend'
D=P.parent/'revision-d/cloud_sea52g_d_main.blend'
SCENE=ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn'
protected=[OLD,D,SCENE,ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
def sig(ob):
    me=ob.data;h=hashlib.sha256()
    for v in me.vertices:h.update(struct.pack('<3f',*v.co))
    for f in me.polygons:
        h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
    for ca in me.color_attributes:
        h.update(ca.name.encode());h.update(ca.domain.encode());h.update(ca.data_type.encode())
        for c in ca.data:h.update(struct.pack('<4f',*c.color))
    h.update(json.dumps([[float(x) for x in row] for row in ob.matrix_world]).encode())
    h.update(json.dumps([m.name for m in me.materials]).encode());return h.hexdigest()
def stats(ob):
    me=ob.data;bm=bmesh.new();bm.from_mesh(me)
    lo=[min(v.co[k] for v in me.vertices) for k in range(3)];hi=[max(v.co[k] for v in me.vertices) for k in range(3)]
    r={'name':ob.name,'vertices':len(me.vertices),'triangles':sum(len(p.vertices)-2 for p in me.polygons),
       'bounds_blender_xyz':[lo,hi],'dimensions_xyz':[hi[k]-lo[k] for k in range(3)],'signed_volume_m3':bm.calc_volume(signed=True)}
    bm.free();return r
bpy.ops.wm.open_mainfile(filepath=str(D))
d_before={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH'}
d_stats=stats(bpy.data.objects['CloudSea52g_d_v0_main_crown'])
bpy.ops.wm.open_mainfile(filepath=str(OLD))
old_stats=stats(bpy.data.objects['CloudSea52e_v0_main_ridge'])
kept=['CloudSea52e_v0_offset_shoulder','CloudSea52e_v0_low_tail','CloudSea52f_v0_low_saddle','CloudSea52f_v0_low_drift']
def keep(n):return n in kept or n.startswith(('CONTROL52e_v0_p1_','CONTROL52e_v0_p2_','CONTROL52f_v0_'))
old_before={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH' and keep(o.name)}
for ob in list(bpy.data.objects):
    if not keep(ob.name):bpy.data.objects.remove(ob,do_unlink=True)
mat=bpy.data.objects[kept[0]].data.materials[0]
newcol=bpy.data.collections.new('D_main_and_editable_controls');bpy.context.scene.collection.children.link(newcol)
with bpy.data.libraries.load(str(D),link=False) as (s,d):d.objects=list(s.objects)
for ob in d.objects:
    newcol.objects.link(ob)
    if ob.name=='CloudSea52g_d_v0_main_crown':ob.data.materials.clear();ob.data.materials.append(mat)
for c in bpy.data.collections:
    if c.name.startswith('Editable'):c.hide_render=True;c.hide_viewport=True
    elif c.name.startswith(('cloud_sea_52','D_main')):c.hide_render=False;c.hide_viewport=False
for ob in bpy.data.objects:
    ob.hide_render=ob.name.startswith('CONTROL')
    if ob.name.startswith('CONTROL52g_d_'):ob.hide_set(True)
old_after={n:sig(bpy.data.objects[n]) for n in old_before};d_after={n:sig(bpy.data.objects[n]) for n in d_before}
assert old_before==old_after and d_before==d_after
final=[bpy.data.objects[n] for n in kept]+[bpy.data.objects['CloudSea52g_d_v0_main_crown']]
def export(name,obs):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.export_scene.gltf(filepath=str(P/name),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
export('cloud_sea_52g_d_combination_v0.glb',final)
export('cloud_sea_52g_d_main_only.glb',[bpy.data.objects['CloudSea52g_d_v0_main_crown']])
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52g_d_combination.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources52g-d-combo.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'assembly52g-d-combo.json').write_text(json.dumps({'status':'Onlyv0 main replacement; combination pending five-face review','retained_objects':kept,
 'old_retained_mesh_and_control_count':len(old_before),'d_mesh_and_control_count':len(d_before),'old_before':old_before,'old_after':old_after,'d_before':d_before,'d_after':d_after,
 'retained_old_and_d_geometry_colors_matrices_materials_unchanged':True,'old_main':old_stats,'d_main':d_stats,
 'triangle_change':d_stats['triangles']-old_stats['triangles'],'volume_change_m3':d_stats['signed_volume_m3']-old_stats['signed_volume_m3'],
 'volume_change_fraction':d_stats['signed_volume_m3']/old_stats['signed_volume_m3']-1,
 'dimensions_change_m':[d_stats['dimensions_xyz'][i]-old_stats['dimensions_xyz'][i] for i in range(3)],
 'failed52g_shoulder_or_tail_used':False,'world_integration':False,'visual_acceptance':False},indent=2)+'\n')
print('D MAIN PLUS FOUR ORIGINALS READY; ALL RETAINED GEOMETRY AND EDIT CONTROLS UNCHANGED')

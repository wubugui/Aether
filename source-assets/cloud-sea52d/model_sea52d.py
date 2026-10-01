import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
old=ROOT/'candidates/round40-exclusive-20260930/source-assets/cloud-sea46/cloud_sea46.blend'
protected=[old,ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']+[ROOT/f'source-assets/cloud-sea{v}/cloud_sea{v}.blend' for v in ['52','52b','52c']]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(old),link=False) as (s,d):d.materials=[n for n in s.materials if n.startswith('Cloud46')]
mat=d.materials[0]
col=bpy.data.collections.new('cloud_sea_52d_0_single_representative');bpy.context.scene.collection.children.link(col)
ctrl=bpy.data.collections.new('Editable52d_unequal_volume_controls');bpy.context.scene.collection.children.link(ctrl)
# x,y,z,radiusX,radiusY,radiusZ,heading; deliberately unequal, offset, and no floor body.
rows=[(-95,20,180,180,145,175,-12),(125,45,185,150,125,135,16),(-230,-65,110,115,91,94,-28),(-35,-135,78,111,89,108,24),(270,30,100,108,77,72,-10),(-100,147,110,128,82,85,22),(-292,48,83,80,66,54,-12),(123,-91,119,90,75,78,-20)]
obs=[]
for i,(cx,cy,cz,rx,ry,rz,heading) in enumerate(rows):
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=4,radius=1)
    ca,sa=math.cos(math.radians(heading)),math.sin(math.radians(heading))
    for v in bm.verts:
        q=v.co.copy();a=math.atan2(q.y,q.x)
        r=1+.035*math.sin(a*3+i*.72)*(1-q.z*q.z)+.025*math.sin(a*2+q.z*3+i)
        x=q.x*rx*r+12*q.z*q.z*math.sin(i+.4);y=q.y*ry*r;z=q.z*rz*(1+.025*math.sin(a*2+i))
        v.co=(cx+x*ca-y*sa,cy+x*sa+y*ca,cz+z)
    me=bpy.data.meshes.new(f'52d_volume_{i}');bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(f'CONTROL52d_{i}',me);ctrl.objects.link(ob);ob['volume_parameters']=json.dumps(rows[i]);ob.hide_render=True
    copy=bpy.data.objects.new(f'work52d_{i}',me.copy());col.objects.link(copy);obs.append(copy)
ctrl.hide_render=True;ctrl.hide_viewport=True
bpy.ops.object.select_all(action='DESELECT')
for ob in obs:ob.select_set(True)
bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name='CloudSea52d_v0_representative_round_crown_ridge'
m=ob.modifiers.new('Local union of unequal cloud volumes','REMESH');m.mode='VOXEL';m.voxel_size=10;m.use_smooth_shade=False;bpy.ops.object.modifier_apply(modifier=m.name)
m=ob.modifiers.new('Round local joins without flattening body','SMOOTH');m.factor=.9;m.iterations=2;bpy.ops.object.modifier_apply(modifier=m.name)
tri=sum(len(f.vertices)-2 for f in ob.data.polygons)
m=ob.modifiers.new('Uneven restrained faceting','DECIMATE');m.ratio=min(1,1100/tri);bpy.ops.object.modifier_apply(modifier=m.name)
me=ob.data;me.materials.append(mat);colors=me.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in me.polygons:
    f.use_smooth=False;z=sum(me.vertices[k].co.z for k in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
    for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
bpy.ops.export_scene.gltf(filepath=str(P/'cloud_sea_52d_0.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52d.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2))
print('52d SINGLE REPRESENTATIVE SOURCE READY; NO VISUAL ACCEPTANCE')

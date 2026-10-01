"""One broad crown with unequal offset shoulders and two wide sculpted saddles."""
import bpy,bmesh,hashlib,json,math
from pathlib import Path
from mathutils import Vector,Euler
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
SOURCE=P.parent.parent/'cloud-sea52f/variants/cloud_sea52f_variants.blend'
protected=[SOURCE,P.parent/'cloud_sea52g_prototype.blend',P.parent/'revision-b/cloud_sea52g_b_main.blend',
 ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(SOURCE),link=False) as (s,d):d.materials=[n for n in s.materials if n=='Cloud46 diffuse warm crown cool belly']
mat=d.materials[0]
col=bpy.data.collections.new('CloudSea52g_c_main_crown');bpy.context.scene.collection.children.link(col)
ctrl=bpy.data.collections.new('Editable52g_c_positive_negative_volumes');bpy.context.scene.collection.children.link(ctrl)
# Three visible, unequal, non-collinear raised masses and one buried thick join.
# role, operation, centerXYZ, radiiXYZ, rotationXYZdeg
regions=[
 ('primary_crown','UNION',(-160,-20,165),(240,210,215),(8,-9,-12)),
 ('broad_rear_shoulder','UNION',(125,130,55),(182,160,155),(-12,14,25)),
 ('small_low_front_shoulder','UNION',(245,-125,10),(112,132,105),(16,-12,-26)),
 ('buried_thick_join','UNION',(70,-45,-10),(185,128,100),(-7,11,-18)),
 ('wide_oblique_saddle','DIFFERENCE',(32,30,292),(105,120,95),(18,-9,-28)),
 ('lower_cross_saddle','DIFFERENCE',(160,-30,175),(90,95,75),(-16,18,31)),
]
controls=[];positive=[];cutters=[]
for i,(name,operation,center,radii,rotdeg) in enumerate(regions):
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=5,radius=1)
    rot=Euler(tuple(math.radians(v) for v in rotdeg),'XYZ').to_matrix()
    for v in bm.verts:
        q=v.co.copy();a=math.atan2(q.y,q.x)
        r=1+(0.037*math.sin(a*2+i*.7)*(1-q.z*q.z) if operation=='UNION' else 0)
        form=Vector((q.x*radii[0]*r,q.y*radii[1]*r,q.z*radii[2]*(1+.024*q.x)))
        v.co=Vector(center)+rot@form
    me=bpy.data.meshes.new(f'52g_c_{name}_volume');bm.to_mesh(me);bm.free()
    cage=bpy.data.objects.new(f'CONTROL52g_c_{name}',me);ctrl.objects.link(cage)
    cage['operation']=operation;cage['parameters']=json.dumps(regions[i]);cage.hide_render=True;controls.append(cage)
    work=bpy.data.objects.new(f'work52g_c_{name}',me.copy());col.objects.link(work)
    (positive if operation=='UNION' else cutters).append(work)
bpy.ops.object.select_all(action='DESELECT')
for ob in positive:ob.select_set(True)
bpy.context.view_layer.objects.active=positive[0];bpy.ops.object.join();ob=positive[0];ob.name='CloudSea52g_c_v0_main_crown'
m=ob.modifiers.new('Continuous thick crown and unequal shoulders','REMESH');m.mode='VOXEL';m.voxel_size=5.5;m.use_smooth_shade=False
bpy.ops.object.modifier_apply(modifier=m.name)
for cutter in cutters:
    m=ob.modifiers.new('Sculpt broad off-axis saddle','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
m=ob.modifiers.new('Continuous rounded saddle edges','REMESH');m.mode='VOXEL';m.voxel_size=5.5;m.use_smooth_shade=False
bpy.ops.object.modifier_apply(modifier=m.name)
m=ob.modifiers.new('Broad cloud transitions retain visible saddle relief','SMOOTH');m.factor=.8;m.iterations=5
bpy.ops.object.modifier_apply(modifier=m.name)
tri=sum(len(f.vertices)-2 for f in ob.data.polygons)
m=ob.modifiers.new('Same2200 facet budget for shape comparison','DECIMATE');m.ratio=min(1,2200/tri)
bpy.ops.object.modifier_apply(modifier=m.name)
# One overall placement, preserving every relief and curved belly; no flattened base.
low=[min(v.co[k] for v in ob.data.vertices) for k in range(3)]
high=[max(v.co[k] for v in ob.data.vertices) for k in range(3)]
ca,sa=math.cos(math.radians(12)),math.sin(math.radians(12))
for item in [ob]+controls:
    for v in item.data.vertices:
        x=((v.co.x-low[0])/(high[0]-low[0])-.5)*740
        y=((v.co.y-low[1])/(high[1]-low[1])-.5)*510
        z=-30+(v.co.z-low[2])/(high[2]-low[2])*380
        v.co=(-350+x*ca-y*sa,-360+x*sa+y*ca,z)
ob.data.materials.append(mat);colors=ob.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in ob.data.polygons:
    f.use_smooth=False;z=sum(ob.data.vertices[k].co.z for k in f.vertices)/len(f.vertices)
    v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
    for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
ctrl.hide_render=True;ctrl.hide_viewport=True
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(P/'cloud_sea_52g_c_main_v0.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52g_c_main.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources52g-c.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'layout52g-c.json').write_text(json.dumps({'status':'One main crown, revision-c, pending five-face review',
 'previous_failure':'revision-b too smooth and almost ellipsoidal; shoulder and notch hierarchy unreadable',
 'previous_failed_run':'cloud-evidence/cloudsea52g-b-main-source-v0-20261001T072801Z-o93gtfjf',
 'regions':regions,'construction':'Unequal offset volumes, thick buried join and two broad off-axis sculpted saddles',
 'nominal_dimensions':[740,510,380],'bottom_top':[-30,350],'center_xy':[-350,-360],'heading':12,
 'visible_primary_shoulder_volume_ratios_design':[1,.42,.14],'editable_control_meshes':6,'triangle_target':2200,
 'material':mat.name,'world_integration':False,'visual_acceptance':False},indent=2)+'\n')
print('52G REVISION C SINGLE MAIN CROWN READY; NO RENDER OR WORLD TRIAL')

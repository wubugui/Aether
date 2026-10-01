"""One broad three-dimensional crown; no repeated axial sections, no world write."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
SOURCE=P.parent.parent/'cloud-sea52f/variants/cloud_sea52f_variants.blend'
protected=[SOURCE,P.parent/'cloud_sea52g_prototype.blend',P.parent/'model52g.py',
 ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',
 ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(SOURCE),link=False) as (s,d):
    d.materials=[n for n in s.materials if n=='Cloud46 diffuse warm crown cool belly']
mat=d.materials[0]
col=bpy.data.collections.new('CloudSea52g_b_main_crown');bpy.context.scene.collection.children.link(col)
ctrl=bpy.data.collections.new('Editable52g_b_main_crown_controls');bpy.context.scene.collection.children.link(ctrl)
# Broad angular influence regions around a single closed 3D cage. Directions and
# widths differ; all operate on full solid angles, never parallel cross-sections.
regions=[
 ('dominant_offset_crown',(-.47,-.12,.87), .28,.64),
 ('broad_rear_shoulder',(.79,.42,.24), .18,.48),
 ('unequal_left_return',(-.72,.61,-.19), .12,.49),
 ('low_front_return',(.42,-.77,-.31), .11,.42),
 ('wide_rear_notch',(.22,.86,.46), -.115,.31),
 ('diagonal_front_notch',(.62,-.49,.61), -.095,.26),
 ('shallow_left_dent',(-.87,-.24,.32), -.065,.30),
]
directions=[Vector(d).normalized() for _,d,_,_ in regions]
bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=5,radius=1)
for v in bm.verts:
    q=v.co.normalized();r=1.0
    for (_,_,amplitude,width),direction in zip(regions,directions):
        r+=amplitude*math.exp((q.dot(direction)-1)/(width*width))
    # Broad solid crown with a drifting centre, not separately joined ball shells.
    x=q.x*320*r + 26*q.z*q.z - 14*q.y*q.z
    y=q.y*235*r + 21*q.z*q.x
    z=q.z*185*r + 17*q.x*q.y
    v.co=(x,y,z)
me=bpy.data.meshes.new('52g_b_continuous_sculpt_cage');bm.to_mesh(me);bm.free()
low=[min(v.co[k] for v in me.vertices) for k in range(3)]
high=[max(v.co[k] for v in me.vertices) for k in range(3)]
ca,sa=math.cos(math.radians(12)),math.sin(math.radians(12))
for v in me.vertices:
    x=((v.co.x-low[0])/(high[0]-low[0])-.5)*720
    y=((v.co.y-low[1])/(high[1]-low[1])-.5)*510
    z=-30+(v.co.z-low[2])/(high[2]-low[2])*380
    v.co=(-350+x*ca-y*sa,-360+x*sa+y*ca,z)
cage=bpy.data.objects.new('CONTROL52g_b_main_crown_sculpt_cage',me);ctrl.objects.link(cage)
cage['three_dimensional_regions']=json.dumps(regions)
cage['construction']='Single wide closed cage with unequal broad shoulders and oblique shallow notches'
cage.hide_render=True
for i,(name,direction,amplitude,width) in enumerate(regions):
    handle=bpy.data.objects.new(f'CONTROL52g_b_region_{i}_{name}',None);ctrl.objects.link(handle)
    handle.empty_display_type='SPHERE';handle.empty_display_size=width*100
    d=Vector(direction).normalized();handle.location=(-350+d.x*360,-360+d.y*255,160+d.z*190)
    handle['direction']=json.dumps(direction);handle['amplitude']=amplitude;handle['angular_width']=width
    handle['purpose']='Editable sculpt-region reference; source mesh remains directly editable'
ob=bpy.data.objects.new('CloudSea52g_b_v0_main_crown',me.copy());col.objects.link(ob)
bpy.context.view_layer.objects.active=ob;ob.select_set(True)
tri=sum(len(f.vertices)-2 for f in ob.data.polygons)
m=ob.modifiers.new('Restrained facets on broad continuous crown','DECIMATE');m.ratio=min(1,2200/tri)
bpy.ops.object.modifier_apply(modifier=m.name)
ob.data.materials.append(mat);colors=ob.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
for f in ob.data.polygons:
    f.use_smooth=False;z=sum(ob.data.vertices[k].co.z for k in f.vertices)/len(f.vertices)
    v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
    for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
ctrl.hide_render=True;ctrl.hide_viewport=True
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
bpy.ops.export_scene.gltf(filepath=str(P/'cloud_sea_52g_b_main_v0.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52g_b_main.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources52g-b.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'layout52g-b.json').write_text(json.dumps({'status':'Single main crown revision-b pending five-face review',
 'rejected_previous':'52g section lofts: pointed sail and repeated vertical shell ribs',
 'previous_failed_run':'cloud-evidence/cloudsea52g-prototype-source-v0-20261001T072103Z-qg5lysu0',
 'construction':'One continuous closed 3D cage, no repeated axial cross-section constrictions',
 'regions':regions,'nominal_dimensions':[720,510,380],'blender_bottom_top':[-30,350],
 'center_xy':[-350,-360],'heading':12,'new_closed_meshes':1,'editable_cage_meshes':1,'editable_region_handles':7,
 'material':mat.name,'triangle_target':2200,'world_integration':False,'visual_acceptance':False},indent=2)+'\n')
print('52G REVISION B SINGLE MAIN CROWN READY; NO RENDER OR WORLD TRIAL')

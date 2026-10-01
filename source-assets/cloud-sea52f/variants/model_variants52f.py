"""Add four independently arranged low bodies; preserve reviewed v0 and all52e."""
import bpy,bmesh,hashlib,json,math
from mathutils import Euler,Vector
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent.parent.parent
PREVIOUS=P.parent/'cloud_sea52f_two_body.blend'
protected=[PREVIOUS,P.parent/'cloud_sea52f.blend',P.parent.parent/'cloud-sea52e/cloud_sea52e.blend',
 ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend',
 ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52e/Game52e.tscn',
 ROOT/'candidates/round40-exclusive-20260930/project/project.godot']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.open_mainfile(filepath=str(PREVIOUS))
# role, x,y,z, rx,ry,rz, heading,pitch,roll. Authored in Blender axes.
# Different paths, arc lengths, volume hierarchy and vertical tilt, not scaled v0 copies.
layouts={
 1:{
  'low_saddle':[
   ('core',-550,70,-55,180,140,111,40,14,-8),
   ('core',-360,-65,-20,150,190,140,-25,15,12),
   ('long_neck',-125,-100,-40,240,132,120,9,-7,5),
   ('core',140,-45,-20,150,172,126,45,12,-11),
   ('core',340,-145,5,186,145,110,-26,-16,7),
   ('falling_end',550,-255,-70,138,120,98,28,13,-18),
   ('fork',-160,125,-65,135,165,113,26,-19,8),
   ('fork_end',-40,285,-85,128,114,85,-18,16,-12),
   ('medium',-432,10,49,95,80,82,22,-12,14),
   ('medium',-319,-193,82,91,96,95,-19,16,-9),
   ('medium',-200,-157,76,78,84,86,24,-18,13),
   ('medium',-114,97,48,92,79,78,-33,11,-14),
   ('medium',133,73,48,87,90,80,14,17,9),
   ('medium',272,-16,96,96,88,91,-25,-12,16),
   ('medium',431,-136,71,83,73,77,33,15,-11),
   ('medium',-37,282,-5,84,76,66,-15,-16,12),
   ('small',-462,65,101,41,37,39,17,9,12),
   ('small',-300,-263,143,37,39,36,-24,-14,8),
   ('small',-197,-216,131,32,38,38,32,12,-9),
   ('small',-166,164,71,43,38,36,-14,16,12),
   ('small',125,145,57,36,42,39,23,-13,15),
   ('small',274,62,147,40,35,37,-19,9,-14),
   ('small',465,-171,118,35,33,32,24,-16,7),
   ('small',-29,348,24,32,36,34,-25,12,11),
  ],
  'low_drift':[
   ('low_start',-570,350,-90,170,148,117,-25,16,8),
   ('swell',-470,545,-55,162,178,138,19,-18,12),
   ('swell',-260,655,-70,180,150,120,-22,14,-15),
   ('low_neck',-35,635,-100,172,160,122,26,-17,11),
   ('high_return',135,490,-40,178,160,144,-29,16,8),
   ('swell',335,355,-40,175,130,120,16,-12,-14),
   ('end',505,200,-95,142,142,110,-23,18,9),
   ('medium',-481,480,26,90,106,81,18,-13,12),
   ('medium',-310,638,35,110,88,82,-24,16,-11),
   ('medium',-80,575,15,96,83,75,31,-15,8),
   ('medium',65,465,65,82,93,87,-19,13,17),
   ('medium',225,342,50,92,73,72,24,-14,-9),
   ('medium',412,262,4,75,83,65,-27,16,12),
   ('small',-512,415,75,38,41,38,21,12,-9),
   ('small',-364,695,83,43,39,35,-26,-15,11),
   ('small',-249,710,61,35,38,37,17,14,-13),
   ('small',-31,539,58,36,37,35,-18,-12,8),
   ('small',49,392,111,37,42,34,25,16,9),
   ('small',236,285,86,34,38,36,-21,-17,12),
   ('small',465,230,37,39,34,35,18,11,-13),
  ]
 },
 2:{
  'low_saddle':[
   ('core',-550,-195,-25,165,180,130,-15,-16,13),
   ('core',-355,-10,-40,180,147,105,-25,17,-11),
   ('swell',-155,30,-5,150,165,133,25,-14,9),
   ('long_neck',45,-115,-70,210,117,113,-17,11,-15),
   ('core',265,-95,5,146,167,122,17,-18,12),
   ('core',455,-45,-45,184,140,114,-36,16,-8),
   ('end',620,60,-85,113,127,83,-12,-11,18),
   ('reverse_fork',-330,210,-75,124,178,95,31,17,-12),
   ('fork_end',-435,355,-96,127,120,90,-26,-14,11),
   ('medium',-538,-70,65,91,102,86,22,14,-11),
   ('medium',-319,13,49,93,75,76,-18,-16,9),
   ('medium',-194,145,75,81,93,88,29,12,-17),
   ('medium',21,-151,9,100,74,80,-24,18,12),
   ('medium',267,25,100,86,95,79,18,-13,16),
   ('medium',407,5,55,85,78,76,-26,15,-12),
   ('medium',-417,296,-14,81,75,73,21,-17,9),
   ('small',-572,-12,119,37,42,35,17,13,-11),
   ('small',-264,66,77,34,38,36,-21,-12,16),
   ('small',-184,204,121,38,40,35,28,17,-9),
   ('small',32,-207,59,40,35,38,-16,-11,14),
   ('small',258,90,146,37,39,34,23,15,-12),
   ('small',441,68,90,35,36,32,-24,-16,11),
   ('small',-447,350,26,36,40,37,19,12,-14),
  ],
  'low_drift':[
   ('swell',-485,550,-66,183,155,127,20,14,-12),
   ('swell',-255,540,-48,166,167,136,-34,-17,9),
   ('low_arch',-80,670,-112,167,120,100,7,12,-16),
   ('swell',95,575,-59,155,160,130,-15,-13,18),
   ('diagonal_neck',240,395,-38,180,135,121,-37,16,-11),
   ('outer_swell',410,330,-88,149,165,113,25,-17,12),
   ('reverse_end',560,520,-102,140,150,101,-28,14,-9),
   ('inner_fork',405,165,-65,135,165,111,23,-12,17),
   ('medium',-482,503,27,103,92,83,-21,17,8),
   ('medium',-307,597,56,87,96,88,26,-15,-12),
   ('medium',-39,669,-13,86,70,77,-16,11,15),
   ('medium',105,492,47,90,100,94,19,-17,12),
   ('medium',258,350,52,88,79,79,-25,13,-9),
   ('medium',461,236,-3,86,78,68,22,-14,16),
   ('medium',558,460,-28,88,72,70,-19,16,-11),
   ('small',-540,449,66,39,35,37,17,13,-12),
   ('small',-345,670,112,37,39,34,-22,-16,9),
   ('small',-16,723,22,34,40,37,27,14,-11),
   ('small',83,417,101,40,37,38,-18,-13,15),
   ('small',284,298,102,37,34,36,23,17,-9),
   ('small',502,188,31,34,39,35,-24,-12,13),
   ('small',602,513,9,36,33,36,19,15,-14),
  ]
 }
}
mat=bpy.data.objects['CloudSea52e_v0_main_ridge'].data.materials[0];report=[]
for vi,parts in layouts.items():
    col=bpy.data.collections.new(f'cloud_sea_52f_{vi}_low');bpy.context.scene.collection.children.link(col)
    for kind,volumes in parts.items():
        controls=bpy.data.collections.new(f'Editable52f_v{vi}_{kind}_controls');bpy.context.scene.collection.children.link(controls)
        copies=[]
        for i,(role,cx,cy,cz,rx,ry,rz,heading,pitch,roll) in enumerate(volumes):
            bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=4,radius=1)
            rot=Euler(tuple(math.radians(a) for a in (roll,pitch,heading)),'XYZ').to_matrix()
            for v in bm.verts:
                q=v.co.copy();a=math.atan2(q.y,q.x)
                radial=1+.022*math.sin(a*3+i*.71)*(1-q.z*q.z)
                # Slightly narrower lower return, varied tilt and deep body thickness.
                taper=1+.10*q.z
                shape=Vector((q.x*rx*radial*taper,q.y*ry*radial*taper,q.z*rz*(1+.02*math.sin(a*2+i))))
                v.co=Vector((cx,cy,cz))+rot@shape
            me=bpy.data.meshes.new(f'52f_v{vi}_{kind}_{i}_{role}');bm.to_mesh(me);bm.free()
            cage=bpy.data.objects.new(f'CONTROL52f_v{vi}_{kind}_{i:02d}_{role}',me);controls.objects.link(cage)
            cage['volume_parameters']=json.dumps(volumes[i]);cage['role']=role;cage.hide_render=True
            work=bpy.data.objects.new(f'work52f_{vi}_{kind}_{i}',me.copy());col.objects.link(work);copies.append(work)
        bpy.ops.object.select_all(action='DESELECT')
        for item in copies:item.select_set(True)
        bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=copies[0];ob.name=f'CloudSea52f_v{vi}_{kind}'
        m=ob.modifiers.new('Closed locally authored cloud volume union','REMESH');m.mode='VOXEL';m.voxel_size=5.5;m.use_smooth_shade=False
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
            assert max(hi[k]-lo[k] for k in range(3))<22 and len(part)<150,f'Meaningful disconnected volume: {ob.name}, {lo}, {hi}, {len(part)}'
            fragments.append({'vertices':len(part),'bounds':[lo,hi]});bmesh.ops.delete(bm,geom=part,context='VERTS')
        bm.to_mesh(ob.data);bm.free()
        m=ob.modifiers.new('Round joins preserve grouped shoulders','SMOOTH');m.factor=.75;m.iterations=3;bpy.ops.object.modifier_apply(modifier=m.name)
        tri=sum(len(f.vertices)-2 for f in ob.data.polygons);budget=3500 if kind=='low_saddle' else 3300
        m=ob.modifiers.new('Retain actual scale hierarchy at silhouette','DECIMATE');m.ratio=min(1,budget/tri);bpy.ops.object.modifier_apply(modifier=m.name)
        ob.data.materials.append(mat);colors=ob.data.color_attributes.new('Col','FLOAT_COLOR','CORNER')
        for f in ob.data.polygons:
            f.use_smooth=False;z=sum(ob.data.vertices[k].co.z for k in f.vertices)/len(f.vertices)
            v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
            for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
        controls.hide_render=True;controls.hide_viewport=True
        report.append({'variant':vi,'part':kind,'name':ob.name,'editable_volume_count':len(volumes),'volumes':volumes,'removed_tiny_voxel_fragments':fragments,'triangle_target':budget})
        print('BUILT',ob.name,len(volumes),flush=True)
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(P/name),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
for vi in range(3):
    old=list(bpy.data.collections[f'cloud_sea_52e_{vi}'].objects)
    low=[bpy.data.objects[f'CloudSea52f_v{vi}_{k}'] for k in ('low_saddle','low_drift')]
    for c in bpy.data.collections:
        if c.name.startswith(('cloud_sea_52e_','cloud_sea_52f_')):c.hide_viewport=False;c.hide_render=False
    export(f'cloud_sea_52f_{vi}.glb',old+low)
    export(f'cloud_sea_52f_additions_{vi}.glb',low)
for ob in bpy.data.objects:
    if ob.type=='MESH' and ob.name.startswith(('CloudSea52e_','CloudSea52f_')):
        ob.hide_render=not ('_v0_' in ob.name)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52f_variants.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources52f-variants.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2)+'\n')
(P/'layout52f-variants.json').write_text(json.dumps({'status':'Three additive low-body arrangements pending five-face and world review',
 'preserved_52e_upper_meshes':9,'preserved_reviewed_v0_low_meshes':2,'new_low_meshes':4,'new_parts':report,
 'v0_source':str(PREVIOUS),'v0_five_face_run':'cloud-evidence/cloudsea52f-two-body-source-v0-20261001T062157Z-fze5esem',
 'material':mat.name,'world_integration':False,'visual_acceptance':False},indent=2)+'\n')
print('THREE ADDITIVE52F VARIANTS READY; NO RENDER OR WORLD INTEGRATION')

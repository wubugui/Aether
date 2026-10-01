import bpy,bmesh,math,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
old=ROOT/'candidates/round40-exclusive-20260930/source-assets/cloud-sea46/cloud_sea46.blend'
protected=[old,ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']+[ROOT/f'source-assets/cloud-sea{v}/cloud_sea{v}.blend' for v in ['52','52b','52c','52d']]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(old),link=False) as (s,d):d.materials=[n for n in s.materials if n.startswith('Cloud46')]
mat=d.materials[0]
templates=[
 [(-95,20,180,180,145,175,-12),(125,45,185,150,125,135,16),(-230,-65,110,115,91,94,-28),(-35,-135,78,111,89,108,24),(270,30,100,108,77,72,-10),(-100,147,110,128,82,85,22),(-292,48,83,80,66,54,-12),(123,-91,119,90,75,78,-20)],
 [(40,0,180,190,150,180,17),(-170,35,125,140,100,115,-14),(-280,-40,95,115,80,65,-27),(70,-140,90,115,90,100,28),(170,110,135,100,75,90,-21),(250,-30,80,100,75,60,12),(-50,140,105,105,75,60,-18)],
 [(-80,-30,180,145,130,170,-17),(105,80,165,125,105,130,24),(-230,60,140,120,100,120,-30),(225,15,90,125,95,70,14),(-35,-155,85,125,85,80,20),(-100,160,95,115,75,60,-19),(80,-70,100,95,90,80,12)]
]
# Center, heading, length/width, bottom/top, construction type, triangle target.
layouts=[
 [(-350,-360,12,745,467,-30,355,0,1100),(350,-60,-22,600,400,80,320,1,750),(-40,400,35,530,360,5,245,2,650)],
 [(-335,-350,-14,750,475,-20,365,1,1100),(350,-45,27,610,410,95,335,2,750),(-40,415,-30,535,365,10,260,0,650)],
 [(-340,-350,24,740,470,-35,350,2,1100),(345,-65,-31,630,415,70,315,0,750),(-55,400,9,560,370,15,270,1,650)]
]
report={'status':'52e source candidate for limited CloudSea-only world comparison; no visual acceptance','anchor_y':700,'root_anchors_modified':False,'construction_types':['offset dual crown','single large crown and long low shoulder','bent stepped crown ridge'],'variants':[]}
for vi,parts in enumerate(layouts):
    col=bpy.data.collections.new(f'cloud_sea_52e_{vi}');bpy.context.scene.collection.children.link(col)
    controls=bpy.data.collections.new(f'Editable52e_v{vi}_volume_controls');bpy.context.scene.collection.children.link(controls)
    final=[];pr=[]
    for pi,(px,py,angle,L,W,lo,hi,kind,budget) in enumerate(parts):
        obs=[];cages=[]
        for i,row in enumerate(templates[kind]):
            cx,cy,cz,rx,ry,rz,heading=row
            # Mild unequal secondary rearrangement; main template changes are structural.
            if pi>0:cy+=12*math.sin(i*1.7+vi);cz+=8*math.cos(i+vi);ry*=1+.05*math.sin(i+vi)
            bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=4,radius=1)
            ca,sa=math.cos(math.radians(heading)),math.sin(math.radians(heading))
            for v in bm.verts:
                q=v.co.copy();a=math.atan2(q.y,q.x);r=1+.035*math.sin(a*3+i*.72)*(1-q.z*q.z)+.025*math.sin(a*2+q.z*3+i)
                x=q.x*rx*r+12*q.z*q.z*math.sin(i+.4);y=q.y*ry*r;z=q.z*rz*(1+.025*math.sin(a*2+i))
                v.co=(cx+x*ca-y*sa,cy+x*sa+y*ca,cz+z)
            me=bpy.data.meshes.new(f'52e_v{vi}_p{pi}_volume{i}');bm.to_mesh(me);bm.free()
            cage=bpy.data.objects.new(f'CONTROL52e_v{vi}_p{pi}_{i}',me);controls.objects.link(cage);cage['volume_parameters']=json.dumps(row);cage.hide_render=True;cages.append(cage)
            ob=bpy.data.objects.new(f'work52e_{vi}_{pi}_{i}',me.copy());col.objects.link(ob);obs.append(ob)
        bpy.ops.object.select_all(action='DESELECT')
        for ob in obs:ob.select_set(True)
        bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=f'CloudSea52e_v{vi}_{["main_ridge","offset_shoulder","low_tail"][pi]}'
        m=ob.modifiers.new('Local ridge volume union','REMESH');m.mode='VOXEL';m.voxel_size=10;m.use_smooth_shade=False;bpy.ops.object.modifier_apply(modifier=m.name)
        m=ob.modifiers.new('Round local joins','SMOOTH');m.factor=.9;m.iterations=2;bpy.ops.object.modifier_apply(modifier=m.name)
        tri=sum(len(f.vertices)-2 for f in ob.data.polygons);m=ob.modifiers.new('Restrained varied facets','DECIMATE');m.ratio=min(1,budget/tri);bpy.ops.object.modifier_apply(modifier=m.name)
        low=[min(v.co[k] for v in ob.data.vertices) for k in range(3)];high=[max(v.co[k] for v in ob.data.vertices) for k in range(3)]
        ca,sa=math.cos(math.radians(angle)),math.sin(math.radians(angle))
        for obj in [ob]+cages:
            for v in obj.data.vertices:
                x=((v.co.x-low[0])/(high[0]-low[0])-.5)*L;y=((v.co.y-low[1])/(high[1]-low[1])-.5)*W;z=lo+(v.co.z-low[2])/(high[2]-low[2])*(hi-lo)
                v.co=(px+x*ca-y*sa,py+x*sa+y*ca,z)
        me=ob.data;me.materials.append(mat);colors=me.color_attributes.new('Col','FLOAT_COLOR','CORNER')
        for f in me.polygons:
            f.use_smooth=False;z=sum(me.vertices[k].co.z for k in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
            for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
        final.append(ob);pr.append({'name':ob.name,'construction_type':kind,'editable_volume_count':len(cages),'layout':parts[pi]})
    controls.hide_render=True;controls.hide_viewport=True
    bpy.ops.object.select_all(action='DESELECT')
    for ob in final:ob.select_set(True)
    bpy.context.view_layer.objects.active=final[0]
    bpy.ops.export_scene.gltf(filepath=str(P/f'cloud_sea_52e_{vi}.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    report['variants'].append({'variant':vi,'parts':pr})
for c in bpy.data.collections:
    if c.name.startswith('cloud_sea_52e_'):c.hide_viewport=not c.name.endswith('_0');c.hide_render=not c.name.endswith('_0')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52e.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2))
(P/'layout52e.json').write_text(json.dumps(report,indent=2))
print('52E SOURCE READY; NO WORLD OR VISUAL ACCEPTANCE')

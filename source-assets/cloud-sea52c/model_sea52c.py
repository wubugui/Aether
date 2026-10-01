import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
old=ROOT/'candidates/round40-exclusive-20260930/source-assets/cloud-sea46/cloud_sea46.blend'
protected=[old,ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend',ROOT/'source-assets/cloud-sea52/cloud_sea52.blend']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(old),link=False) as (s,d):d.materials=[n for n in s.materials if n.startswith('Cloud46')]
mat=d.materials[0]
layouts=[
 [(-365,-365,17,750,480,45,360),(340,-90,-18,660,425,135,330),(-30,345,28,570,390,-5,255)],
 [(-355,-390,24,730,465,40,350),(275,-95,-23,640,410,125,325),(-65,325,7,585,400,-15,265)],
 [(-390,-355,9,740,450,55,375),(310,-55,-29,690,440,140,335),(-20,440,34,550,370,0,275)]
]
# Unequal offset canopy cells: x,y,height,footprint radius x/y. Five crowns plus small shoulders.
canopies=[
 [(-.43,.14,1.0,.30,.34),(.12,-.36,.78,.29,.30),(.52,.25,.65,.27,.31),(-.57,-.47,.48,.22,.23),(-.03,.63,.45,.28,.23),(-.82,.04,.24,.20,.21),(.58,-.48,.29,.24,.21),(.37,.69,.23,.21,.20)],
 [(-.44,-.26,.91,.29,.30),(.15,.29,1.0,.28,.31),(.57,-.23,.62,.25,.31),(-.39,.49,.58,.28,.25),(.05,-.63,.38,.26,.22),(-.77,.18,.28,.22,.21),(.57,.56,.31,.20,.22),(-.60,-.59,.23,.22,.19)],
 [(-.52,.23,.77,.27,.29),(-.08,-.32,1.0,.30,.30),(.42,.26,.72,.30,.30),(.64,-.31,.45,.25,.23),(-.11,.62,.43,.27,.23),(-.70,-.32,.34,.22,.24),(.28,-.70,.24,.24,.20),(.73,.42,.26,.20,.19)]
]
def sculpt(vi,pi,row,col,ctrl):
    cx,cy,angle,L,W,lo,hi=row;mode=(vi+pi)%3;spec=canopies[mode]
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=5,radius=1)
    coords=[]
    for v in bm.verts:
        q=v.co.normalized();az=math.atan2(q.y,q.x)
        rim=1
        for ang,amp,spread in [(-2.8,.15,.075),(-1.8,.22,.08),(-.7,.12,.065),(.2,.21,.075),(1.2,.16,.08),(2.25,.24,.06)]:
            delta=math.atan2(math.sin(az-ang-mode*.21),math.cos(az-ang-mode*.21))
            rim+=amp*math.exp(-delta*delta/spread)*(q.x*q.x+q.y*q.y)
        x=q.x*rim;y=q.y*rim+.07*math.sin(q.x*3+mode*.7)*(1-q.z*q.z)
        if q.z>=0:
            cells=[height*math.exp(-(((q.x-cx)/rx)**2+((q.y-cy)/ry)**2)*1.25) for cx,cy,height,rx,ry in spec]
            # Max envelope keeps real saddles between crowns rather than summed plateau.
            z=q.z*(.18+max(cells))
        else:
            pockets=[.46*math.exp(-(((q.x+.42)/.31)**2+((q.y+.14)/.34)**2)),.36*math.exp(-(((q.x-.39)/.30)**2+((q.y-.20)/.35)**2)),.25*math.exp(-(((q.x-.09)/.32)**2+((q.y+.53)/.25)**2))]
            z=q.z*(.12+max(pockets))
        coords.append(Vector((x,y,z)))
    low=[min(v[k] for v in coords) for k in range(3)];high=[max(v[k] for v in coords) for k in range(3)]
    ca,sa=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    for v,q in zip(bm.verts,coords):
        x=((q.x-low[0])/(high[0]-low[0])-.5)*L;y=((q.y-low[1])/(high[1]-low[1])-.5)*W;z=lo+(q.z-low[2])/(high[2]-low[2])*(hi-lo)
        v.co=(cx+x*ca-y*sa,cy+x*sa+y*ca,z)
    name=f'CloudSea52c_v{vi}_{["crown_scroll","notched_shoulder","low_winding_tail"][pi]}'
    me=bpy.data.meshes.new(name+'_triangular_sculpt_cage');bm.to_mesh(me);bm.free()
    cage=bpy.data.objects.new('CONTROL_'+name,me);ctrl.objects.link(cage);cage.hide_render=True
    cage['directional_sculpt_handles']=json.dumps(canopies[mode]);cage['layout']=json.dumps(row)
    ob=bpy.data.objects.new(name,me.copy());col.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    m=ob.modifiers.new('Restrained non-ring facets','DECIMATE');m.ratio=.18;bpy.ops.object.modifier_apply(modifier=m.name)
    me=ob.data;me.materials.append(mat);colors=me.color_attributes.new('Col','FLOAT_COLOR','CORNER')
    for f in me.polygons:
        f.use_smooth=False;z=sum(me.vertices[k].co.z for k in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
        for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
    return ob
for vi,rows in enumerate(layouts):
    col=bpy.data.collections.new(f'cloud_sea_52c_{vi}');bpy.context.scene.collection.children.link(col)
    ctrl=bpy.data.collections.new(f'Editable52c_v{vi}_triangular_cages');bpy.context.scene.collection.children.link(ctrl)
    obs=[sculpt(vi,pi,row,col,ctrl) for pi,row in enumerate(rows)];ctrl.hide_render=True;ctrl.hide_viewport=True
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.export_scene.gltf(filepath=str(P/f'cloud_sea_52c_{vi}.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
for c in bpy.data.collections:
    if c.name.startswith('cloud_sea_52c_'):c.hide_viewport=not c.name.endswith('_0');c.hide_render=not c.name.endswith('_0')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52c.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2))
print('52B_SOURCE_READY_NO_VISUAL_ACCEPTANCE')

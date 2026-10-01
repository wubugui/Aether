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
# Direction, amplitude, angular extent. These displace a single triangular cage.
# Unequal localized crown/shoulder bulges and cuts, not joined primitive spheres.
sculpts=[
 [((-.38,.20,.90),.66,.14),((.43,-.15,.72),.32,.11),((-.77,-.40,.20),.28,.055),((-.34,-.89,.12),.31,.042),((.28,-.94,.07),.20,.035),((.78,-.43,.18),.35,.045),((.78,.53,.12),.17,.035),((.20,.95,.11),.25,.04),((-.44,.85,.03),.30,.05),((-.93,.19,-.14),.13,.035),((-.34,-.35,-.88),.25,.065),((.45,.48,-.74),.28,.075),((.54,-.40,-.68),.12,.038),((0,0,-1),-.20,.10),((-.07,-.64,.73),-.12,.028),((.35,.73,.53),-.16,.04)],
 [((-.46,-.10,.87),.61,.115),((.39,.28,.77),.43,.11),((-.02,.04,.98),-.20,.05),((-.82,-.53,.12),.24,.038),((-.33,-.92,.08),.29,.047),((.43,-.82,.11),.34,.048),((.88,-.15,.21),.18,.035),((.71,.65,.12),.29,.054),((-.08,.95,.20),.20,.035),((-.77,.50,.14),.31,.04),((-.48,-.24,-.81),.29,.065),((.36,.47,-.81),.20,.049),((.54,-.48,-.66),.22,.055),((0,0,-1),-.22,.09)],
 [((.18,.24,.95),.58,.15),((-.52,-.32,.66),.25,.07),((.61,-.44,.55),.33,.075),((-.91,-.20,.08),.23,.036),((-.52,-.80,.10),.33,.049),((.07,-.98,.03),.20,.029),((.72,-.61,.08),.30,.049),((.89,.25,.17),.25,.044),((.22,.92,.14),.33,.044),((-.50,.81,.10),.23,.032),((-.54,-.32,-.76),.31,.059),((.45,.47,-.75),.26,.06),((.53,-.50,-.67),.14,.045),((0,0,-1),-.18,.09),((-.15,.71,.67),-.13,.035)]
]
def sculpt(vi,pi,row,col,ctrl):
    cx,cy,angle,L,W,lo,hi=row;mode=(vi+pi)%3;spec=[(Vector(v).normalized(),amp,wide) for v,amp,wide in sculpts[mode]]
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=5,radius=1)
    coords=[]
    for v in bm.verts:
        q=v.co.normalized();r=1+sum(amp*math.exp(-(1-q.dot(d))/wide) for d,amp,wide in spec)
        # Asymmetric winding spine and underside pinch, with full 3D folded edge.
        x=q.x*r*(1-.19*max(-q.z,0))
        y=q.y*r*(1-.26*max(-q.z,0))+.13*math.sin(q.x*3+mode*.7)*(1-q.z*q.z)
        z=q.z*r
        # Lift offset lower flanks and deepen only two unequal belly pockets.
        z+=.10*math.sin(q.x*4+q.y*2+mode)*max(-q.z,0)
        coords.append(Vector((x,y,z)))
    low=[min(v[k] for v in coords) for k in range(3)];high=[max(v[k] for v in coords) for k in range(3)]
    ca,sa=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    for v,q in zip(bm.verts,coords):
        x=((q.x-low[0])/(high[0]-low[0])-.5)*L;y=((q.y-low[1])/(high[1]-low[1])-.5)*W;z=lo+(q.z-low[2])/(high[2]-low[2])*(hi-lo)
        v.co=(cx+x*ca-y*sa,cy+x*sa+y*ca,z)
    name=f'CloudSea52b_v{vi}_{["crown_scroll","notched_shoulder","low_winding_tail"][pi]}'
    me=bpy.data.meshes.new(name+'_triangular_sculpt_cage');bm.to_mesh(me);bm.free()
    cage=bpy.data.objects.new('CONTROL_'+name,me);ctrl.objects.link(cage);cage.hide_render=True
    cage['directional_sculpt_handles']=json.dumps(sculpts[mode]);cage['layout']=json.dumps(row)
    ob=bpy.data.objects.new(name,me.copy());col.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    m=ob.modifiers.new('Restrained non-ring facets','DECIMATE');m.ratio=.32;bpy.ops.object.modifier_apply(modifier=m.name)
    me=ob.data;me.materials.append(mat);colors=me.color_attributes.new('Col','FLOAT_COLOR','CORNER')
    for f in me.polygons:
        f.use_smooth=False;z=sum(me.vertices[k].co.z for k in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
        for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
    return ob
for vi,rows in enumerate(layouts):
    col=bpy.data.collections.new(f'cloud_sea_52b_{vi}');bpy.context.scene.collection.children.link(col)
    ctrl=bpy.data.collections.new(f'Editable52b_v{vi}_triangular_cages');bpy.context.scene.collection.children.link(ctrl)
    obs=[sculpt(vi,pi,row,col,ctrl) for pi,row in enumerate(rows)];ctrl.hide_render=True;ctrl.hide_viewport=True
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.export_scene.gltf(filepath=str(P/f'cloud_sea_52b_{vi}.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
for c in bpy.data.collections:
    if c.name.startswith('cloud_sea_52b_'):c.hide_viewport=not c.name.endswith('_0');c.hide_render=not c.name.endswith('_0')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cloud_sea52b.blend'))
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected};assert before==after
(P/'protected-sources.json').write_text(json.dumps({'before':before,'after':after,'unchanged':True},indent=2))
print('52B_SOURCE_READY_NO_VISUAL_ACCEPTANCE')

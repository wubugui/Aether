"""Standalone editable lighthouse candidate; never rebuild or overwrite the world."""
from pathlib import Path
import bpy, math, json, shutil
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'captures/lighthouse_study_19e'
if OUT.exists(): raise RuntimeError('Frozen candidate already exists')
OUT.mkdir()
shutil.copy2(__file__,OUT/'builder.py')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
parts=[]
def material(name,color,metal=0,emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.78;p.inputs['Metallic'].default_value=metal
    p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    return m
stone=[material('Limestone '+str(i),c) for i,c in enumerate([(.195,.184,.158),(.215,.205,.178),(.238,.223,.189),(.206,.199,.179)])]
trim=material('Weathered sandstone edges',(.155,.144,.119))
iron=material('Dark forged bronze',(.135,.105,.072),.35)
roof=material('Oxidised terracotta roof',(.26,.105,.067))
wood=material('Oak door boards',(.18,.10,.052))
dark=material('Unlit window recess',(.022,.028,.033))
glass=material('Clear slightly amber lantern glass',(.25,.20,.12))
glass.diffuse_color=(.25,.20,.12,.27)
glass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.27
glass.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.22
glass.surface_render_method='DITHERED'
lensglass=glass.copy();lensglass.name='Clear optical lens glass'
lensglass.diffuse_color=(.25,.20,.12,.10)
lensglass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.10
core=material('Lamp core',(.12,.04,.01))
core.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.42,.07,1)
core.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.9
def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(mat);parts.append(obj)
    return obj
def cone(name,z,depth,r1,r2,mat,n=8):
    bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r1,radius2=r2,depth=depth,location=(0,0,z))
    o=bpy.context.object;o.name=name;o.data.materials.append(mat);parts.append(o);return o
def bar(name,a,b,r,mat,n=6):
    a,b=Vector(a),Vector(b);d=b-a
    o=cone(name,0,d.length,r,r,mat,n);o.location=(a+b)/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def ring(name,z,r,width,mat,n=24):
    for i in range(n):
        a,b=i*math.tau/n,(i+1)*math.tau/n
        bar(name+' %02d'%i,(r*math.cos(a),r*math.sin(a),z),(r*math.cos(b),r*math.sin(b),z),width,mat)
def shaftpoint(angle,z):
    r=3.22-(z-.7)/20*1.18
    return Vector((r*math.cos(angle),r*math.sin(angle),z))
cone('Broad octagonal foundation',.20,.4,3.65,3.65,trim)
cone('Bevelled plinth',.55,.3,3.65,3.22,stone[1])
# Four vertical courses have actual inset openings, with jambs and lintels.
# The shaft exterior is never a stack of painted window rectangles.
for j,(z0,z1) in enumerate(zip([.7,5.7,10.7,15.7],[5.7,10.7,15.7,20.7])):
    for i in range(8):
        a=i*math.tau/8;b=(i+1)*math.tau/8
        corners=[shaftpoint(a,z0),shaftpoint(b,z0),shaftpoint(b,z1),shaftpoint(a,z1)]
        def point(u,v):return corners[0].lerp(corners[1],u).lerp(corners[3].lerp(corners[2],u),v)
        window=(j+i)%4==0
        if not window:
            mesh('Shaft course %d facet %d'%(j,i),corners,[(0,1,2,3)],stone[i%4]);continue
        is_door=j==0 and i==0
        u0,u1=(.24,.76) if is_door else (.39,.61)
        v0,v1=(.015,.65) if is_door else (.36,.67)
        verts=corners+[point(u0,v0),point(u1,v0),point(u1,v1),point(u0,v1)]
        mesh('Stone opening course %d facet %d'%(j,i),verts,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone[i%4])
        normal=Vector((math.cos((a+b)/2),math.sin((a+b)/2),0))
        inner=[p-normal*.28 for p in verts[4:]]
        mesh('Deep stone jamb %d %d'%(j,i),verts[4:]+inner,[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],trim)
        mesh('Recessed oak door' if is_door else 'Dark slit interior %d %d'%(j,i),inner,[(0,1,2,3)],wood if is_door else dark)
        # Shallow solid stone surrounds, separated from the recessed jambs.
        border_u=.055 if is_door else .035
        border_v=.036 if is_door else .023
        outer=[point(u0-border_u,v0),point(u1+border_u,v0),point(u1+border_u,v1+border_v),point(u0-border_u,v1+border_v)]
        opening=[point(u0,v0),point(u1,v0),point(u1,v1),point(u0,v1)]
        frame=[p+normal*.065 for p in outer+opening]+[p-normal*.045 for p in outer+opening]
        faces=[]
        for edge in range(4):
            nxt=(edge+1)%4
            faces.extend([(edge,nxt,4+nxt,4+edge),(8+edge,12+edge,12+nxt,8+nxt),(edge,8+edge,8+nxt,nxt),(4+edge,4+nxt,12+nxt,12+edge)])
        mesh('Door stone surround' if is_door else 'Window stone surround %d %d'%(j,i),frame,faces,trim)
        if is_door:
            tangent=Vector((-normal.y,normal.x,0))
            # Three actual entry treads bridge the ground and raised plinth.
            for step,(distance,height) in enumerate([(4.50,.24),(4.03,.48),(3.56,.72)]):
                center=normal*distance+Vector((0,0,height/2))
                verts=[center+tangent*x+normal*y+Vector((0,0,z)) for z in [-height/2,height/2] for x,y in [(-.86,-.30),(.86,-.30),(.86,.30),(-.86,.30)]]
                mesh('Entry stone step %d'%step,verts,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],stone[1])
            for q in range(1,6):
                u=u0+(u1-u0)*q/6
                bar('Door board seam',point(u,v0)-normal*.269,point(u,v1)-normal*.269,.012,iron,4)
            for v in [.18,.53]:bar('Door strap',point(u0+.04,v)-normal*.26,point(u1-.04,v)-normal*.26,.032,iron)
        else:
            bar('Recessed window central mullion',inner[0].lerp(inner[1],.5),inner[3].lerp(inner[2],.5),.035,iron)
cone('Gallery supporting cornice',20.87,.34,2.10,2.92,trim)
cone('Gallery stone floor',21.10,.16,3.04,3.04,stone[2])
for i in range(16):
    a=math.tau*i/16
    bar('Gallery baluster %02d'%i,(2.9*math.cos(a),2.9*math.sin(a),21.18),(2.9*math.cos(a),2.9*math.sin(a),22.22),.048,iron)
ring('Gallery upper rail',22.22,2.9,.055,iron,16)
ring('Gallery lower rail',21.58,2.9,.032,iron,16)
cone('Lantern pedestal',21.46,.56,1.90,1.90,trim)
cone('Lantern lower brass rim',21.78,.10,2.00,2.00,iron)
for i in range(8):
    a,b=i*math.tau/8,(i+1)*math.tau/8;r=1.89
    bar('Lantern corner column %d'%i,(r*math.cos(a),r*math.sin(a),21.82),(r*math.cos(a),r*math.sin(a),24.76),.075,iron)
    # Transparent real panes reveal the central lamp and lens assembly.
    aa=a+.034;bb=b-.034
    mesh('Lantern glazed panel %d'%i,[(r*math.cos(t),r*math.sin(t),z) for t,z in [(aa,21.88),(bb,21.88),(bb,24.65),(aa,24.65)]],[(0,1,2,3)],glass)
cone('Central luminous lamp',23.20,1.38,.30,.30,core,12)
cone('Lamp bronze base',22.28,.45,.42,.27,iron,12)
cone('Lamp reflector crown',24.09,.38,.74,.25,iron,12)
for k in range(5):
    z=22.65+k*.25
    cone('Fresnel lens tier %02d'%k,z,.18,.64+(.06 if k==2 else 0),.59,lensglass,16)
for k in range(4):
    a=k*math.tau/4
    bar('Lens cage rod %d'%k,(.67*math.cos(a),.67*math.sin(a),22.50),(.67*math.cos(a),.67*math.sin(a),23.97),.022,iron)
cone('Lantern top frame',24.78,.14,2.01,2.01,iron)
cone('Roof projecting fascia',24.94,.18,2.48,2.48,iron)
cone('Eight pitched roof planes',26.00,1.98,2.48,.19,roof)
for i in range(8):
    a=math.tau*i/8
    bar('Roof hip seam %d'%i,(2.48*math.cos(a),2.48*math.sin(a),25.01),(.19*math.cos(a),.19*math.sin(a),26.99),.037,iron)
cone('Roof weather cap',27.14,.32,.23,.10,iron)
bar('Lightning rod',(0,0,27.25),(0,0,28.1),.041,iron)
# A real maintenance ladder behind the shaft, including stand-off brackets.
for x in [-.25,.25]:bar('Rear ladder rail',(x,-3.43,.85),(x,-2.29,20.4),.035,iron)
for k in range(43):
    z=1.05+k*.45;y=-3.43+(z-.85)/19.55*1.14
    bar('Ladder rung %02d'%k,(-.25,y,z),(.25,y,z),.025,iron)
for z in [2,6,10,14,18]:
    y=-3.43+(z-.85)/19.55*1.14
    for x in [-.25,.25]:bar('Ladder anchor',(x,y,z),(x,y+.30,z),.027,iron)
# Coordinated three-dimensional proportion edit, including openings and ladder.
# Compress the shaft 18%, widen its foot 10%, preserve upper lantern dimensions.
bpy.context.view_layer.update()
for obj in parts:
    matrix=obj.matrix_world.copy()
    for vertex in obj.data.vertices:
        p=matrix @ vertex.co
        widen=1.+.10*(1.-max(0.,min(1.,(p.z-.7)/20.)))
        p.x*=widen;p.y*=widen
        p.z=.7+(p.z-.7)*.82 if .7<p.z<=20.7 else (p.z-3.6 if p.z>20.7 else p.z)
        vertex.co=p
    obj.matrix_world.identity()
    obj.data.update()
headstone=material('Deep weathered gallery corbel stone',(.103,.096,.082))
cone('Thick octagonal gallery support',16.92,.86,2.13,2.92,headstone)
cone('Gallery underside projecting lip',17.37,.12,3.04,3.04,headstone)
for obj in parts:obj['authoring_role']='independent lighthouse architectural part'
bpy.context.scene['reference_images']='ref/1126.png; ref/1342.png'
bpy.context.scene['scope']='Tower architecture study only; island, keeper houses, fog, beam and night not completed.'
source_counts={'parts':len(parts),'vertices':sum(len(o.data.vertices) for o in parts),'polygons':sum(len(o.data.polygons) for o in parts)}
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'lighthouse.blend'))
# Keep source parts editable; batch only opaque render objects for repeated islands.
groups={};transparent=[]
for obj in parts:
    mat=obj.data.materials[0]
    if mat in (glass,lensglass):transparent.append(obj)
    else:groups.setdefault(mat.name,[]).append(obj)
exports=list(transparent)
for name,objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:bpy.ops.object.join()
    obj=bpy.context.object;obj.name='Opaque_'+name;exports.append(obj)
parts=exports
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'lighthouse.glb'),export_format='GLB',use_selection=True,export_apply=True)
report={**source_counts,'export_mesh_nodes':len(parts),'height_m':24.5,'foundation_width_m':8.03,'production_modified':False,'scope':bpy.context.scene['scope'],'materials':[m.name for m in bpy.data.materials if m.users]}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2))
print('LIGHTHOUSE CANDIDATE BUILT',json.dumps(report),flush=True)

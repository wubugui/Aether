"""Step 2: native Blender asset library. Run with the original Aether.blend.
All environment assets are full 3D meshes with standalone vertex materials.
"""
from pathlib import Path
import bpy,bmesh,math,json,numpy as np
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'assets/models').mkdir(exist_ok=True)

# Retain the previously authored airship; replace its environment completely.
for obj in list(bpy.data.objects):
    if not any(c.name in ['Airship','Propeller'] for c in obj.users_collection):
        bpy.data.objects.remove(obj,do_unlink=True)
for name in ['Landscape','Asset Library']:
    if name in bpy.data.collections:bpy.data.collections.remove(bpy.data.collections[name])
library=bpy.data.collections.new('Asset Library');bpy.context.scene.collection.children.link(library)
material=bpy.data.materials.new('Environment pigment - vertex colors')
material.use_nodes=True
nodes=material.node_tree.nodes;nodes.clear()
color=nodes.new('ShaderNodeVertexColor');color.layer_name='Palette'
bsdf=nodes.new('ShaderNodeBsdfPrincipled');bsdf.inputs['Roughness'].default_value=.95
output=nodes.new('ShaderNodeOutputMaterial')
material.node_tree.links.new(color.outputs['Color'],bsdf.inputs['Base Color'])
material.node_tree.links.new(bsdf.outputs[0],output.inputs['Surface'])
parts=[];catalog=[]

def bl(v):return (v[0],-v[2],v[1])
def lin(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def finish(obj,tint):
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for c in list(obj.users_collection):c.objects.unlink(obj)
    library.objects.link(obj)
    mesh=obj.data
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
    attr=mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
    c=lin(rgb(tint));values=[]
    for p in mesh.polygons:
        p.use_smooth=False
        shade=.985+.015*math.sin(p.index*21.713)
        values.extend([(*np.clip(c*shade,0,1),1)]*len(p.loop_indices))
    attr.data.foreach_set('color',np.array(values,np.float32).ravel())
    mesh.color_attributes.active_color_index=0;mesh.color_attributes.render_color_index=0
    mesh.materials.clear();mesh.materials.append(material)
    parts.append(obj);obj.select_set(False)
    return obj
def box(p,s,c,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=bl(p))
    o=bpy.context.object;o.scale=(s[0],s[2],s[1])
    if bevel:
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        m=o.modifiers.new('Crafted edges','BEVEL');m.width=bevel;m.segments=1
        bpy.ops.object.modifier_apply(modifier=m.name)
    return finish(o,c)
def ico(p,s,c,sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=bl(p))
    o=bpy.context.object;o.scale=(s[0],s[2],s[1]);return finish(o,c)
def cone(p,h,r1,r2,c,n=8):
    bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r1,radius2=r2,depth=h,location=bl(p))
    return finish(bpy.context.object,c)
def rod(a,b,r,c,n=6,r2=None):
    a=Vector(bl(a));b=Vector(bl(b));d=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(a+b)*.5)
    o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return finish(o,c)
def mesh(points,faces,c):
    m=bpy.data.meshes.new('Hand modeled mesh');m.from_pydata([bl(p) for p in points],[],faces);m.update()
    o=bpy.data.objects.new('Mesh part',m);library.objects.link(o);return finish(o,c)
def roof(x,z,w,d,eaves,ridge,c):
    v=[(x-w/2,eaves,z-d/2),(x+w/2,eaves,z-d/2),(x+w/2,eaves,z+d/2),(x-w/2,eaves,z+d/2),(x-w/2,ridge,z),(x+w/2,ridge,z)]
    return mesh(v,[(0,1,5,4),(4,5,2,3),(0,4,3),(1,2,5),(0,3,2,1)],c)
def torus(p,r,t,c,vertical=False):
    bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=6,location=bl(p),major_radius=r,minor_radius=t,rotation=(math.pi/2 if vertical else 0,0,0))
    return finish(bpy.context.object,c)

def make_asset(name,build):
    global parts
    parts=[];bpy.ops.object.select_all(action='DESELECT');build()
    for p in parts:p.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
    o=bpy.context.object;o.name=name;o.data.name=name+'Geometry'
    if name.startswith('cloud'):
        union=o.modifiers.new('Joined cloud volume','REMESH')
        union.mode='VOXEL';union.voxel_size=3.0;union.adaptivity=.35
        bpy.ops.object.modifier_apply(modifier=union.name)
        dec=o.modifiers.new('Broad cloud facets','DECIMATE');dec.ratio=.25
        dec.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=dec.name)
        for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
        attr=o.data.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
        cloud_color=lin(rgb('e3e3e4'))
        for polygon in o.data.polygons:
            polygon.use_smooth=False
            for loop_index in polygon.loop_indices:attr.data[loop_index].color=(*cloud_color,1)
        o.data.color_attributes.active_color_index=0;o.data.color_attributes.render_color_index=0
    o['authoring']='Blender primitives, complete geometry, no photographic material'
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/models'/f'{name}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    catalog.append(dict(name=name,vertices=len(o.data.vertices),faces=len(o.data.polygons),path=f'assets/models/{name}.glb'))
    o.location=(len(catalog)%5*24, len(catalog)//5*32,0)
    o.select_set(False)
    print('ASSET',name,len(o.data.polygons),'faces',flush=True)

def oak():
    cone((0,2.5,0),5,.5,.27,'796d50',7)
    for a,b in [((0,3,0),(-2.2,6,.3)),((0,3.5,0),(2.0,6.8,-.7)),((0,4,0),(.3,7,1.7))]:rod(a,b,.2,'827252')
    ico((-1.6,7.4,.3),(3.2,3.4,2.9),'7e985a',2)
    ico((1.5,8.4,-.5),(3,3.8,3),'8da669',2)
    ico((.3,7.5,1.5),(2.8,3.1,2.6),'78965c',2)
def poplar():
    cone((0,3.5,0),7,.37,.13,'7b7054',7)
    ico((0,8.0,0),(2.4,6.0,2.2),'789457',2)
    ico((.7,9.3,0),(1.8,4.3,1.7),'8fa766',1)
def pine():
    cone((0,5.8,0),11.6,.43,.12,'72684c',6)
    for y,r,h,c in [(5,3.9,6.5,'64836a'),(7.8,3.2,6.2,'6f8e6e'),(10.4,2.25,5.6,'7b9977')]:cone((0,y,0),h,r,0,c,7)
def bush():
    ico((0,1.1,0),(1.8,1.6,1.7),'8ea168',1);ico((1.1,.8,.2),(1.4,1.1,1.4),'9aac74',1)
def rock():
    ico((0,1.6,0),(3.3,2.7,2.5),'929b92',1)
    ico((2,1.0,.7),(1.9,1.5,1.9),'a4ab9b',1)
def cottage():
    box((0,.4,0),(8.8,.8,6.8),'9f9f89');box((0,2.8,0),(8,4.8,6),'d7cbb1')
    roof(0,0,9.1,7.2,5.3,7.8,'7f8d86')
    for x in [-3.85,0,3.85]:box((x,2.8,3.04),(.19,4.8,.18),'78664c')
    for y in [.7,3.0,5.0]:box((0,y,3.05),(8,.15,.18),'907a58')
    for side in [-1,1]:
        for x in [-2.35,2.35]:
            box((x,3.1,side*3.10),(1.05,1.4,.13),'667f85')
            box((x,3.1,side*3.19),(.10,1.5,.08),'b3a07b')
            box((x,3.1,side*3.19),(1.15,.10,.08),'b3a07b')
    box((.1,1.9,3.15),(1.4,2.6,.23),'736148');box((.5,1.9,3.30),(.12,.12,.08),'c9b882')
    box((2.3,7.1,-1.1),(.9,2.8,.9),'aca18a')
def mill_base():
    cone((0,5.7,0),11.4,3.4,2.6,'d8cbb1',10);cone((0,13,0),4.4,3.6,0,'777e6e',8)
    box((0,1.8,3.3),(1.6,3.5,.25),'71634d')
    for y in [5,8]:box((0,y,3.0),(.9,1.2,.18),'6c7d81')
def mill_rotor():
    rod((0,0,-.8),(0,0,.7),.38,'705f43')
    for i in range(4):
        a=i*math.pi/2+.2
        u=np.array([math.cos(a),math.sin(a),0]);v=np.array([-math.sin(a),math.cos(a),0])
        rod(u*.2,u*8,.13,'806c49')
        pts=[u*2-v*.1,u*7.8-v*.1,u*7.8+v*1.4,u*2+v*.9]
        mesh(pts+[(p+[0,0,.12]) for p in pts],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'dccfa6')
def lighthouse():
    cone((0,11,0),22,3.5,2.6,'d7d5c3',12)
    for y in [8,15]:cone((0,y,0),1.2,3.2 if y==8 else 2.9,3.2 if y==8 else 2.9,'bcae8c',12)
    cone((0,22.3,0),.6,4.0,4.0,'95998a',12)
    cone((0,24,0),3.5,2.25,2.25,'8aafb6',8)
    for a in np.linspace(0,math.tau,9)[:-1]:
        x,z=2.3*math.cos(a),2.3*math.sin(a)
        rod((x,22.5,z),(x,25.7,z),.13,'7f806b')
        x,z=3.6*math.cos(a),3.6*math.sin(a)
        rod((x,22.5,z),(x,24,z),.09,'777963')
    torus((0,24,0),3.6,.09,'8d8d73');cone((0,27,0),2.8,3.3,0,'6d7a72',8)
    box((0,1.8,3.5),(1.7,3.5,.24),'75694f')
    for y in [8,14,19]:box((0,y,3.0),(.7,1.7,.12),'7c9290')
def castle():
    stone='d8c89f';trim='baaf8b'
    for x in [-23,23]:
        for z in [-18,18]:
            cone((x,11,z),22,4.7,4.3,stone,10)
            cone((x,23,z),3,5.0,5.0,trim,10)
            for a in np.linspace(0,math.tau,11)[:-1]:box((x+4.3*math.cos(a),25,z+4.3*math.sin(a)),(1.2,2,1.2),stone)
            cone((x,29,z),8,3.8,0,'adb298',8)
    for x in [-23,23]:box((x,6.5,0),(2.5,13,36),stone)
    box((0,6.5,-18),(46,13,2.5),stone)
    for x in [-14,14]:box((x,6.5,18),(18,13,2.5),stone)
    box((0,11.5,18),(11,3,3),stone)
    for x in np.arange(-21,22,3):
        for z in [-18,18]:box((x,13.7,z),(1.5,1.5,2.8),stone)
    box((0,10,-4),(17,20,15),stone);roof(0,-4,20,18,20,29,'99a68d')
    cone((0,20,-4),40,3.4,3.1,stone,8);cone((0,43,-4),9,4,0,'9aaa98',8)
    for x in [-6,0,6]:box((x,14,3.57),(1.1,3,.13),'8f9784')
def observatory():
    cone((0,4,0),8,7,7,'c3c8bb',12);ico((0,8.2,0),(7.1,5.5,7.1),'a7bcc3',2)
    box((0,2.1,7),(2.2,4.2,.3),'7d8d89')
    rod((0,12,0),(5,15.5,-6),.95,'7f908e',10)
    rod((5,15.5,-6),(5.4,15.8,-6.5),1.18,'b6c5c5',10)
    cone((-10,3,-2),6,1.3,1.1,'c6c7b1',8)
def ruins():
    for x in [-8,8]:
        box((x,1,0),(5,2,5),'9ca797');cone((x,7,0),12,1.7,1.5,'b5bca7',8)
        box((x,13,0),(4,1.5,3),'adb69f')
    for i in range(10):
        a=i*math.pi/10;b=(i+1)*math.pi/10
        v=[]
        for z in [-1.3,1.3]:
            for r,t in [(8.7,a),(8.7,b),(6.3,b),(6.3,a)]:v.append((r*math.cos(t),13+r*math.sin(t),z))
        mesh(v,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'bfc3ab')
    for x,z in [(-12,5),(9,6),(5,-8)]:ico((x,1,z),(3,2,2.6),'a1ac96',1)
def dock():
    box((0,-.35,0),(28,1.0,19),'877453')
    for z in np.arange(-9,10,1):box((0,.18,z),(27.8,.12,.085),'aa936a')
    for x in [-12,12]:
        for z in [-8,0,8]:
            cone((x,-9,z),18,.7,.58,'796b4e',8)
            box((x,1.4,z),(.22,2.5,.22),'9b845a')
        rod((x,2.5,-8),(x,2.5,8),.12,'b09a70')
    rod((-12,2.5,-8),(12,2.5,-8),.12,'b09a70')
    for x in [-10,10]:
        cone((x,4.0,-7),8,.4,.25,'9a895e',7)
        ico((x,8.3,-7),(.65,.9,.65),'e7c779',1)
    for x in [8.5,10.5]:cone((x,1.2,4),2.3,.8,.8,'78634a',10)
def crate():
    box((0,1,0),(2,2,2),'a18458',.06)
    for x in [-.84,.84]:box((x,1,1.03),(.2,2,.1),'786342')
    for y in [.2,1.8]:box((0,y,1.04),(2,.2,.12),'c0a06a')
def cloud():
    for p,s in [((-51,-18,0),(26,6,16)),((-27,-10,-2),(25,14,21)),
                ((15,2,0),(28,29,25)),((38,-16,2),(26,10,21)),
                ((64,-20,0),(25,4,13))]:ico(p,s,'e3e3e4',2)

def cloud_form(kind):
    forms={
      'primary':[((-51,-15,0),(28,6,16)),((-27,-1,-2),(22,18,21)),((26,8,0),(33,35,27)),((57,-7,2),(28,18,21)),((68,-20,0),(24,4,13))],
      'middle':[((9,2,0),(35,38,27)),((-67,12,-2),(28,18,19)),((-29,-5,0),(24,15,20)),((-107,10,1),(25,3,10)),((-28,-15,0),(58,10,25)),((43,-8,1),(23,16,20)),((81,-20,0),(27,3,9))],
      'low':[((12,9,0),(32,34,22)),((-15,-8,-1),(43,10,16)),((-87,-9,0),(30,2.7,8)),((97,-18,0),(40,3,7)),((56,-14,0),(25,8,12))],
      'edge':[((-35,19,-2),(37,27,25)),((18,0,0),(26,17,22)),((34,-7,1),(19,13,17)),((63,-15,0),(28,6,16)),((104,-19,0),(23,2,8))],
      'wisp':[((-20,14,0),(26,24,19)),((-60,-1,0),(30,7,17)),((20,-7,0),(40,6,15)),((78,-10,0),(60,4,10))]}
    for p,s in forms[kind]:ico(p,s,'e3e3e4',2)

# Close the ship's underside and give its moving propeller real thickness.
sections=[(-3.6,.16,-1.68,-2.1),(-2.8,1.02,-1.70,-3.55),(-1.45,1.24,-1.78,-3.9),(1.1,1.15,-1.80,-3.80),(2.7,.73,-1.52,-3.20),(3.45,.12,-1.17,-2.0)]
keel_points=[]
for x,w,t,b in sections:
    for side in [-1,1]:keel_points.append((x*1.16+.3,-1.6+(b+1.6)*1.19,side*w*.45))
keel_faces=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(sections)-1)]
keel=mesh(keel_points,keel_faces,'69523b');keel.name='Closed wooden keel'
library.objects.unlink(keel);bpy.data.collections['Airship'].objects.link(keel);keel.parent=bpy.data.objects['Airship']
for o in bpy.data.collections['Propeller'].objects:
    if o.type=='MESH':
        bpy.context.view_layer.objects.active=o
        mod=o.modifiers.new('Solid wooden blades','SOLIDIFY');mod.thickness=.09
        bpy.ops.object.modifier_apply(modifier=mod.name)
import sys
sys.path.insert(0,str(ROOT/'blender'))
from refine_hero import refine
refine(globals())
for group,filename in [('Airship','airship.glb'),('Propeller','propeller.glb')]:
    root=bpy.data.objects[group];old=root.matrix_world.copy();root.matrix_world=Matrix.Identity(4)
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.collections[group].objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets'/filename),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    root.matrix_world=old

for name,builder in [('oak',oak),('poplar',poplar),('pine',pine),('bush',bush),('rock',rock),('cottage',cottage),('mill',mill_base),('mill_rotor',mill_rotor),('lighthouse',lighthouse),('castle',castle),('observatory',observatory),('ruins',ruins),('dock',dock),('crate',crate),('cloud',cloud),('sky_ring',lambda:torus((0,0,0),8,.27,'d8bb75',True))]:make_asset(name,builder)
for kind in ['primary','middle','low','edge','wisp']:make_asset('cloud_'+kind,lambda kind=kind:cloud_form(kind))

# Neutral studio to inspect the individual assets from arbitrary directions.
bpy.ops.object.camera_add(location=(85,-125,85));camera=bpy.context.object;camera.name='Asset overview camera'
camera.rotation_euler=(Vector((48,50,6))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=205
scene=bpy.context.scene;scene.camera=camera
bpy.ops.object.light_add(type='SUN',location=(-100,-100,120));sun=bpy.context.object;sun.name='World sunlight';sun.rotation_euler=(math.radians(27),math.radians(-28),math.radians(-35));sun.data.energy=2
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.34,.43,.5,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
scene.render.engine='BLENDER_EEVEE_NEXT';scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
scene.render.resolution_x=1600;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene['purpose']='Editable native asset library for the fully modeled flight game'
(ROOT/'assets/asset_catalog.json').write_text(json.dumps(catalog,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Assets.blend'))
for name in ['Airship','Propeller']:bpy.data.collections[name].hide_render=True
scene.render.filepath=str(ROOT/'captures/asset-library.png');bpy.ops.render.render(write_still=True)
print('ASSET LIBRARY COMPLETE',len(catalog),'MODELS',flush=True)

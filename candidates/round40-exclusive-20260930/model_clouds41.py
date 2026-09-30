"""Editable irregular cloud masses and economical distant banks for one world."""
import bpy, bmesh, math, random, os, json
from pathlib import Path
from mathutils import Vector

out=Path(os.environ['HUB_OUTPUT_DIR']); out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mat=bpy.data.materials.new('Cloud41 diffuse density');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF')
vertex=mat.node_tree.nodes.new('ShaderNodeVertexColor');vertex.layer_name='Col'
mat.node_tree.links.new(vertex.outputs['Color'],bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value=1
report={'design':'Unequal connected triangulated cloud shoulders, deep varying crowns and low interstitial wisps. Independent distant banks extend the same physical region; no camera or image inputs.','assets':[]}

def mass(collection,name,center,radii,seed,detail=2):
    rng=random.Random(seed);bm=bmesh.new()
    bmesh.ops.create_icosphere(bm,subdivisions=detail,radius=1)
    for vert in bm.verts:
        v=vert.co.copy()
        # Coherent irregular lobes instead of concentric latitude bands.
        angle=math.atan2(v.y,v.x)
        radial=1+.12*math.sin(3*angle+seed)+.09*math.sin(5*angle+2*v.z+seed*.3)
        radial+=rng.uniform(-.055,.055)
        vert.co=Vector((v.x*radii[0]*radial,v.y*radii[1]*radial,v.z*radii[2]*(1+.10*math.sin(4*angle+seed))))+Vector(center)
    mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free()
    colors=mesh.color_attributes.new('Col','BYTE_COLOR','CORNER')
    for face in mesh.polygons:
        z=sum(mesh.vertices[i].co.z for i in face.vertices)/len(face.vertices)
        density=.69+.22*max(0,min(1,(z+170)/420))+rng.uniform(-.035,.035)
        linear=((density+.055)/1.055)**2.4
        for loop in face.loop_indices:colors.data[loop].color=(linear,linear,linear,1)
        face.use_smooth=False
    mesh.materials.append(mat)
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj)

def export(collection,name):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.all_objects:obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    report['assets'].append({'name':name,'parts':len(collection.objects),'vertices':sum(len(o.data.vertices) for o in collection.objects),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in collection.objects)})

for variant in range(3):
    name=f'cloud_sea_41_{variant}'
    col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
    seed=4100+variant*137;rng=random.Random(seed)
    for i,(x,y,rx,ry,h) in enumerate([(-240,-20,570,490,100),(240,140,490,570,135),(40,-330,440,410,95)]):
        mass(col,f'{name}_connected_body_{i}',(x,y,-100),(rx,ry,h),seed+i,3)
    for i in range(9):
        angle=rng.uniform(0,math.tau);distance=rng.uniform(80,520)
        radius=rng.uniform(70,280)
        height=radius*rng.uniform(.48,.88)
        mass(col,f'{name}_unequal_crown_{i}',(math.cos(angle)*distance,math.sin(angle)*distance,rng.uniform(-10,100)),(radius,radius*rng.uniform(.65,1.45),height),seed+20+i,3 if radius>170 else 2)
    for i in range(8):
        angle=rng.uniform(0,math.tau);distance=rng.uniform(390,620);r=rng.uniform(45,135)
        mass(col,f'{name}_low_wisp_{i}',(math.cos(angle)*distance,math.sin(angle)*distance,-65),(r*2.2,r*1.25,r*.38),seed+60+i,2)
    export(col,name)
    name=f'cloud_bank_41_{variant}'
    col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
    for i in range(8):
        x=(i%4-1.5)*480+rng.uniform(-130,130);y=(i//4-.5)*640
        r=rng.uniform(270,550)
        mass(col,f'{name}_shoulder_{i}',(x,y,rng.uniform(-60,70)),(r*1.6,r,rng.uniform(60,180)),seed+100+i,2)
    export(col,name)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'cloud_sea41.blend'))
(out/'cloud_model41.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('CLOUD41 MODELED',json.dumps(report['assets']))

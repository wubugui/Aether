"""Three editable low-poly cloud masses shared by the whole live world."""
import bpy, bmesh, math, random, os, json
from pathlib import Path
from mathutils import Matrix, Vector

out=Path(os.environ['HUB_OUTPUT_DIR']);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mat=bpy.data.materials.new('Cloud diffuse palette40');mat.use_nodes=True
nodes=mat.node_tree.nodes;bsdf=nodes.get('Principled BSDF')
vertex=nodes.new('ShaderNodeVertexColor');vertex.layer_name='Col'
mat.node_tree.links.new(vertex.outputs['Color'],bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value=1
report={'design':'Three native cloud mass variants, connected broad shoulders and a few dominant billows; no camera-facing planes or source image textures. Same resources reused in exterior and cabin windows.','assets':[]}

def lobe(collection,name,center,radii,seed,segments=12,rings=7):
    rng=random.Random(seed)
    bm=bmesh.new()
    bmesh.ops.create_uvsphere(bm,u_segments=segments,v_segments=rings,radius=1)
    # Gentle shape variation on broad shoulders; retain rounded crowns rather
    # than spiky ico triangles. Consistent faceting remains editable geometry.
    for vert in bm.verts:
        radial=1+.06*math.sin(math.atan2(vert.co.y,vert.co.x)*3+seed)
        vert.co.x*=radii[0]*radial;vert.co.y*=radii[1]*radial
        vert.co.z*=radii[2]
        vert.co+=Vector(center)
    mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free()
    colors=mesh.color_attributes.new('Col','BYTE_COLOR','CORNER')
    for face in mesh.polygons:
        z=sum(mesh.vertices[i].co.z for i in face.vertices)/len(face.vertices)
        # Subtle density colour by world-independent local height, lighting is
        # actual engine moon/sun and atmosphere, not a camera gradient.
        value=.78+.13*max(0,min(1,(z+170)/380))+rng.uniform(-.012,.012)
        linear=((value+.055)/1.055)**2.4
        for loop in face.loop_indices:colors.data[loop].color=(linear,linear,linear,1)
        face.use_smooth=False
    mesh.materials.append(mat)
    obj=bpy.data.objects.new(name,mesh);collection.objects.link(obj)
    return obj

for variant in range(3):
    name=f'cloud_sea_40_{variant}'
    collection=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(collection)
    seed=400+variant*79;rng=random.Random(seed)
    # Broad overlapping body lobes create one connected mass, not a field of
    # equally-sized independent stones; leave a lower darker layer in valleys.
    for i,(x,y,rx,ry,h) in enumerate([(-230,-30,470,500,125),(250,150,460,460,140),(60,-310,460,370,110)]):
        lobe(collection,f'{name}_continuous_body_{i}',(x,y,-85),(rx,ry,h),seed+i,16,8)
    for i in range(9):
        angle=rng.uniform(0,math.tau);distance=rng.uniform(120,490)
        radius=rng.uniform(130,255)
        x=math.cos(angle)*distance;y=math.sin(angle)*distance
        lobe(collection,f'{name}_broad_billow_{i}',(x,y,rng.uniform(5,50)),(radius,radius*rng.uniform(.8,1.3),rng.uniform(80,140)),seed+20+i,12,7)
    for i in range(8):
        angle=rng.uniform(0,math.tau);distance=rng.uniform(390,570)
        r=rng.uniform(75,135)
        lobe(collection,f'{name}_shoulder_wisp_{i}',(math.cos(angle)*distance,math.sin(angle)*distance,-15),(r*1.6,r,r*.55),seed+60+i,10,6)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.all_objects:obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    vertices=sum(len(o.data.vertices) for o in collection.objects)
    triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in collection.objects)
    report['assets'].append({'name':name,'parts':len(collection.objects),'vertices':vertices,'triangles':triangles})
bpy.ops.wm.save_as_mainfile(filepath=str(out/'cloud_sea40.blend'))
(out/'cloud_model40.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('CLOUD40 MODELED',json.dumps(report['assets']))

"""Independent editable airborne cumulus. No cloud-sea base plate."""
import bpy,bmesh,math,random,os,json
from pathlib import Path
from mathutils import Vector
out=Path(os.environ['HUB_OUTPUT_DIR']);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
mat=bpy.data.materials.new('Upper cloud43 diffuse');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=1
vertex=mat.node_tree.nodes.new('ShaderNodeVertexColor');vertex.layer_name='Col'
mat.node_tree.links.new(vertex.outputs['Color'],bsdf.inputs['Base Color'])
report={'design':'Independent spatial cumulus, unequal overlapping crowns and rounded underside scallops; no sea-floor ellipsoid, planar underside or camera inputs.','assets':[]}
for variant in range(3):
    name=f'upper_cloud43_{variant}';col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
    rng=random.Random(4300+variant*113)
    for part in range(11):
        x=(part%4-1.5)*125+rng.uniform(-45,45);y=(part//4-1)*85+rng.uniform(-30,30)
        radius=rng.uniform(90,175);height=radius*rng.uniform(.7,1.15)
        center=Vector((x,y,rng.uniform(-10,90)))
        bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1)
        seed=part+variant*11
        for v in bm.verts:
            original=v.co.copy();angle=math.atan2(original.y,original.x)
            shape=1+.09*math.sin(angle*3+seed)+rng.uniform(-.025,.025)
            v.co=Vector((original.x*radius*shape,original.y*radius*.75*shape,original.z*height))+center
        mesh=bpy.data.meshes.new(f'{name}_crown_{part}');bm.to_mesh(mesh);bm.free()
        colors=mesh.color_attributes.new('Col','BYTE_COLOR','CORNER')
        for face in mesh.polygons:
            value=.86+rng.uniform(-.025,.025);linear=((value+.055)/1.055)**2.4
            for loop in face.loop_indices:colors.data[loop].color=(linear,linear,linear,1)
            face.use_smooth=False
        mesh.materials.append(mat);obj=bpy.data.objects.new(mesh.name,mesh);col.objects.link(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.all_objects:obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    report['assets'].append({'name':name,'mesh_parts':11,'vertices':sum(len(o.data.vertices) for o in col.objects)})
bpy.ops.wm.save_as_mainfile(filepath=str(out/'upper_cloud43.blend'))
(out/'upper_cloud43-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('UPPER43 MODELED',json.dumps(report))

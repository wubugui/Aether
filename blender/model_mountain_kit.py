"""Independent complete alpine massifs, authored in Blender and placed in Godot.

Each mesh contains its own summit, alternating buttresses/drainage valleys,
descending shoulders, foot slopes and closed foundation. No image texture,
view-aligned sheet or whole-world mesh is exported.
"""
from pathlib import Path
import math,json,sys,bpy,bmesh,numpy as np
from mathutils import Vector,noise
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
from alpine_ridge_topology import make_massif
F=941/(2*math.tan(math.radians(25)));pitch=math.radians(-3.5)
def at_depth(u,v,z):
    x=(u-836)/F;y=(470.5-v)/F
    ray=np.array([x,math.cos(pitch)*y+math.sin(pitch),math.sin(pitch)*y-math.cos(pitch)])
    return np.array([0,145,250])+ray*((z-250)/ray[2])
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def linear(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def bl(p):return (p[0],-p[2],p[1])
forms=[
    ('massif_frost_crown',1235,307,-2900,520,520,0.18),
    ('massif_west_summit',1145,325,-2730,430,440,0.53),
    ('massif_needle_ridge',1178,360,-2350,270,370,0.37),
    ('massif_east_summit',1308,358,-2850,310,400,0.71),
    ('massif_east_spur',1373,398,-2320,360,410,0.16),
    ('massif_west_spur',1063,405,-1850,290,350,0.42),
    ('massif_cirque_wall',1239,413,-1780,235,340,0.83),
    ('massif_east_foothill',1458,439,-1810,340,370,0.39),
    ('massif_blue_buttress',1115,451,-1190,135,230,0.63),
    ('massif_valley_guard',1286,445,-1430,245,310,0.25),
    ('massif_west_foothill',997,444,-1520,210,280,0.51),
]
catalog=[]
native=ROOT/'blender/mountain_kit';native.mkdir(exist_ok=True)
for form_index,(name,u,v,z,rx,rz,phase) in enumerate(forms):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    summit=at_depth(u,v,z);height=float(summit[1]);origin=np.array([summit[0],0,summit[2]])
    vertices,faces=make_massif(form_index,rx,rz,height)
    mesh=bpy.data.meshes.new(name+'Geometry');mesh.from_pydata([bl(p) for p in vertices],[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    if form_index<7:
        original_vertices=set(bm.verts)
        exposed=[e for e in bm.edges if all(v.co.z>12 for v in e.verts)]
        bmesh.ops.subdivide_edges(bm,edges=exposed,cuts=1,use_grid_fill=True)
        # Sculpt the new shoulder/face vertices in real metres while retaining
        # every established summit and ridge control. Unequal relief changes
        # surface normals; this is not coplanar triangle subdivision.
        for vertex in bm.verts:
            if vertex in original_vertices:continue
            relative=np.clip(vertex.co.z/height,0,1)
            relief=noise.noise_vector(vertex.co*.031+Vector((form_index*5.1,3.7,8.2))).z
            vertex.co.z+=relief*22*math.sin(math.pi*relative)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces))
    assert all(len(e.link_faces)==2 for e in bm.edges),name
    volume=abs(bm.calc_volume(signed=True));assert volume>0
    bm.to_mesh(mesh);bm.free();mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj)
    attr=mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
    sun=Vector((-.48,-.30,.82)).normalized()
    for face in mesh.polygons:
        light=max(0,face.normal.dot(sun));h=face.center.z
        snowline=height*.30+12*math.sin(face.center.x*.018+phase)
        snow=height>140 and h>snowline and (face.normal.z>.32 or h>height*.72)
        if snow:
            c=rgb('eae7e1')*(np.array([.75,.80,.90])*(1-light)+light)
        else:
            c=rgb('8699b0')*(.70+.34*light)
            if h<26:c=rgb('9daa82')*(.72+.29*light)
        for k in face.loop_indices:attr.data[k].color=(*linear(np.clip(c,0,1)),1)
        face.use_smooth=False
    mesh.color_attributes.active_color_index=0;mesh.color_attributes.render_color_index=0
    mat=bpy.data.materials.new('Alpine rock and snow');mat.use_nodes=True
    nt=mat.node_tree;color=nt.nodes.new('ShaderNodeVertexColor');color.layer_name='Palette'
    bsdf=nt.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=1
    nt.links.new(color.outputs['Color'],bsdf.inputs['Base Color']);mesh.materials.append(mat)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);obj.asset_mark()
    obj['asset_role']='Complete alpine massif, assembled with other modules in Godot World/Mountains'
    obj['closed_volume_m3']=volume
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'assets/models'/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    distance=max(rx,rz)*2.8
    bpy.ops.object.camera_add(location=(distance,-distance,height+distance*.6));camera=bpy.context.object
    camera.rotation_euler=(Vector((0,0,height*.4))-camera.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.camera=camera
    bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.45,-.3,-.4);bpy.context.object.data.energy=2
    bpy.ops.wm.save_as_mainfile(filepath=str(native/(name+'.blend')))
    catalog.append({'name':name,'path':'assets/models/'+name+'.glb','native_source':'blender/mountain_kit/'+name+'.blend','position':origin.tolist(),'category':'Mountains','vertices':len(mesh.vertices),'faces':len(mesh.polygons),'closed':True,'volume_m3':volume})
    print('COMPLETE ALPINE MODULE',name,len(mesh.vertices),len(mesh.polygons),flush=True)
(ROOT/'assets/mountain_kit.json').write_text(json.dumps(catalog,indent=2))

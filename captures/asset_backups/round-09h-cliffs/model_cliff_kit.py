"""Complete, independently reusable Blender cliff volumes.

Sparse silhouette/height measurements become fixed metre-space modeling
controls once. Every asset has a top, back, side walls and a closed bottom.
Godot owns their placement and collision; there are no image materials.
"""
from pathlib import Path
import bpy,bmesh,math,json,sys,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
from cliff_terrace_topology import make_terraced_cliff
OUT=ROOT/'assets/models';NATIVE=ROOT/'blender/cliff_kit'
OUT.mkdir(exist_ok=True);NATIVE.mkdir(exist_ok=True)
F=941/(2*math.tan(math.radians(25)));pitch=math.radians(-3.5)
def survey(u,v,h):
    x=(u-836)/F;y=(470.5-v)/F
    ray=np.array([x,math.cos(pitch)*y+math.sin(pitch),math.sin(pitch)*y-math.cos(pitch)])
    return np.array([0,145,250])+ray*((h-145)/ray[1])
def bl(p):return Vector((p[0],-p[2],p[1]))
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def linear(c):return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
forms=[
 ('cliff_crown',[(1398,624,82),(1447,633,78),(1467,672,66),(1429,718,58),(1372,719,63),(1290,695,65),(1336,663,76)],[(1292,739,24),(1363,782,22),(1452,783,20),(1512,741,22),(1500,691,23),(1390,676,27),(1260,704,27)]),
 ('cliff_western_slab',[(1235,695,65),(1288,725,53),(1280,748,55),(1249,754,55),(1214,742,56),(1192,749,52)],[(1172,798,20),(1180,845,20),(1240,858,19),(1300,852,16),(1340,777,19),(1290,727,23),(1210,727,24)]),
 ('cliff_front_columns',[(1229,750,52),(1278,752,52),(1301,773,45),(1279,809,35),(1248,817,35),(1207,810,38),(1178,780,46)],[(1160,824,16),(1180,857,15),(1230,866,15),(1280,858,16),(1305,830,16),(1320,795,20),(1235,773,19)]),
 ('cliff_eastern_plateau',[(1575,684,62),(1630,692,60),(1684,721,55),(1630,755,49),(1555,752,55),(1514,724,61),(1530,696,60)],[(1510,778,21),(1470,841,17),(1570,918,12),(1720,930,12),(1780,813,17),(1725,733,23),(1590,705,26)]),
 ('cliff_shadow_buttress',[(1040,825,42),(1110,798,48),(1181,849,33),(1164,902,27),(1080,932,21),(995,902,30)],[(940,949,9),(920,1040,6),(1140,1050,6),(1230,995,10),(1210,917,14),(1150,842,17),(1055,851,18)]),
 ('cliff_central_wall',[(1340,743,55),(1377,711,65),(1406,759,52),(1401,804,40),(1354,833,38),(1320,795,48)],[(1287,868,10),(1320,941,5),(1416,985,5),(1460,931,10),(1450,851,20),(1427,793,20),(1350,760,20)]),
 ('cliff_western_mesa',[(126,543,56),(146,540,57),(188,542,56),(207,540,57),(218,550,54),(207,559,52),(166,560,53),(129,552,54)],[])]
catalog=[]
for name,top,base in forms:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    legacy=np.array([survey(*p) for p in top+base])
    original_origin=np.array([legacy[:,0].mean(),legacy[:,1].min(),legacy[:,2].mean()])
    points=np.array([survey(*p) for p in top])
    origin=np.array([points[:,0].mean(),0,points[:,2].mean()])
    # Sculpt a real rear shoulder. A compact plateau with a descending back
    # ridge avoids both a long triangular slab and a thin vertical wall.
    shoulder=points[points[:,2]<origin[2]].copy()
    shoulder[:,2]-=min(30,np.ptp(points[:,0])*.65)
    shoulder[:,1]=np.minimum(shoulder[:,1]-10,shoulder[:,1]*.65+8)
    points=np.r_[points,shoulder]
    vertices,faces=make_terraced_cliff(points,origin,name)
    source=bpy.data.meshes.new(name+'CrownWallShoulder');source.from_pydata([bl(p) for p in vertices],[],faces);source.update()
    bm=bmesh.new();bm.from_mesh(source)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(len(e.link_faces)==2 for e in bm.edges),name+' must be a closed manifold'
    volume=abs(bm.calc_volume(signed=True));assert volume>10,(name,volume)
    bm.faces.ensure_lookup_table()
    mesh=bpy.data.meshes.new(name+'Geometry');bm.to_mesh(mesh);bm.free();mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj)
    attr=mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER');sun=Vector((-.48,-.30,.82)).normalized()
    for face in mesh.polygons:
        light=max(0,face.normal.dot(sun));face.use_smooth=False
        grass=face.normal.z>(.72 if name in ['cliff_crown','cliff_eastern_plateau','cliff_western_mesa'] else .50) and face.center.z+origin[1]>5
        if grass:c=rgb(['a6ae7e','b1b787','95a473'][face.index%3])*(.73+.28*light)
        else:c=rgb('909295')*(1-light)+rgb('c0baae')*light
        for k in face.loop_indices:attr.data[k].color=(*linear(c),1)
    mesh.color_attributes.active_color_index=0;mesh.color_attributes.render_color_index=0
    mat=bpy.data.materials.new(name+' stone and meadow');mat.use_nodes=True
    nt=mat.node_tree;color=nt.nodes.new('ShaderNodeVertexColor');color.layer_name='Palette'
    bsdf=nt.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=1
    nt.links.new(color.outputs['Color'],bsdf.inputs['Base Color']);mesh.materials.append(mat)
    obj['closed_volume_m3']=volume;obj['asset_role']='Independent complete cliff kit; placed in Godot World/Cliffs'
    obj.asset_mark()
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    extent=np.ptp(points,axis=0);distance=max(extent)*2.4
    bpy.ops.object.camera_add(location=(distance,-distance,distance*.8));camera=bpy.context.object
    camera.rotation_euler=(Vector((0,0,extent[1]*.5))-camera.location).to_track_quat('-Z','Y').to_euler();bpy.context.scene.camera=camera
    bpy.ops.object.light_add(type='SUN',location=(-100,-100,150));bpy.context.object.rotation_euler=(.45,-.3,-.4);bpy.context.object.data.energy=2
    bpy.context.scene.world.color=(.22,.27,.32)
    bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE/(name+'.blend')))
    catalog.append({'name':name,'path':'assets/models/'+name+'.glb','native_source':'blender/cliff_kit/'+name+'.blend','position':origin.tolist(),'original_origin':original_origin.tolist(),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'closed':True,'volume_m3':volume})
    print('CLOSED CLIFF MODULE',name,len(mesh.vertices),len(mesh.polygons),volume,flush=True)
(ROOT/'assets/cliff_kit.json').write_text(json.dumps(catalog,indent=2))

import sys,json,bpy,bmesh
import numpy as np
from mathutils import Vector
sys.path.insert(0,'D:/test6/blender');sys.path.insert(0,'D:/test6/captures')
from cliff_sections_10d import make_front_columns,make_western_slab,make_crown,make_central_wall,make_shadow_buttress
selection={'--central-wall':(make_central_wall,'central_wall'),'--crown':(make_crown,'crown'),
    '--western-slab':(make_western_slab,'western_slab'),'--shadow-buttress':(make_shadow_buttress,'shadow_buttress')}
method,suffix=next((value for key,value in selection.items() if key in sys.argv),(make_front_columns,'prototype'))
asset_name='cliff_'+(suffix if suffix!='prototype' else 'front_columns')
item=next(x for x in json.load(open('D:/test6/assets/cliff_kit.json')) if x['name']==asset_name)
vertices,faces,roles=method(np.array(item['position']))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mesh=bpy.data.meshes.new('front_columns_sections')
mesh.from_pydata([(x,-z,y) for x,y,z in vertices],[],faces);mesh.update()
obj=bpy.data.objects.new('Front columns study',mesh);bpy.context.collection.objects.link(obj)
role_names=['grass','wall','slope','buried']
for name in role_names:
    m=bpy.data.materials.new(name);m.diffuse_color={'grass':(.40,.49,.28,1),'wall':(.45,.44,.40,1),'slope':(.32,.38,.25,1),'buried':(.1,.1,.1,1)}[name];mesh.materials.append(m)
for f,role in zip(mesh.polygons,roles):f.material_index=role_names.index(role)
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bad=[e for e in bm.edges if len(e.link_faces)!=2];deg=[f for f in bm.faces if f.calc_area()<1e-8]
print('MODEL STUDY:',len(bm.verts),'vertices',len(bm.faces),'triangles','bad edges',len(bad),'degenerate',len(deg),'volume',bm.calc_volume(),flush=True)
assert not bad and not deg
bm.to_mesh(mesh);bm.free()
attr=mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
sun=Vector((-.48,-.30,.82)).normalized()
def rgb(h):return np.array([int(h[k:k+2],16)/255 for k in (0,2,4)])
for f in mesh.polygons:
    role=role_names[f.material_index];light=max(0.,f.normal.dot(sun))
    if role in ('grass','slope'):c=rgb('949f74')*(.71+.25*light)
    else:c=rgb('96928e')*(1-light)+rgb('c4bcaf')*light
    if role=='grass':
        grass_tone={'cliff_western_slab':'abb67c','cliff_front_columns':'abb67c','cliff_central_wall':'a4ad73','cliff_crown':'89945b'}.get(asset_name,'949f74')
        c=rgb(grass_tone)*(.86+.16*light)
    if asset_name=='cliff_central_wall' and role=='wall':c=rgb('606b75')*(1-light)+rgb('a6aaa2')*light
    if asset_name=='cliff_shadow_buttress':c=(rgb('66784f')*(.70+.25*light)) if role in ('grass','slope') else rgb('4c5e68')*(1-light)+rgb('879781')*light
    c=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
    for k in f.loop_indices:attr.data[k].color=(*c,1)
mesh.color_attributes.active_color_index=0;mesh.color_attributes.render_color_index=0
bpy.context.view_layer.objects.active=obj;obj.select_set(True)
bpy.ops.export_scene.gltf(filepath='D:/test6/captures/cliff_sections_10d_'+suffix+'.glb',export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
bpy.ops.wm.save_as_mainfile(filepath='D:/test6/captures/cliff_sections_10d_'+suffix+'.blend')

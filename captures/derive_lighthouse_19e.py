"""Refine the accepted 19d form and export opaque batches, keeping editable source parts."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
target=root/'blender/model_lighthouse_19e.py'
assert not target.exists()
text=(root/'blender/model_lighthouse_19d.py').read_text()
changes={
"OUT=ROOT/'captures/lighthouse_study_19d'":"OUT=ROOT/'captures/lighthouse_study_19e'",
"glass.diffuse_color=(.25,.20,.12,.16)":"glass.diffuse_color=(.25,.20,.12,.27)",
"inputs['Alpha'].default_value=.16":"inputs['Alpha'].default_value=.27",
"glass.surface_render_method='DITHERED'":"glass.surface_render_method='DITHERED'\nlensglass=glass.copy();lensglass.name='Clear optical lens glass'\nlensglass.diffuse_color=(.25,.20,.12,.10)\nlensglass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.10",
"core=material('Lamp core', (1,.64,.23),0,2.5)":"core=material('Lamp core',(.12,.04,.01))\ncore.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1,.42,.07,1)\ncore.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.9",
"cone('Central luminous lamp',23.20,1.38,.16,.16,core,12)":"cone('Central luminous lamp',23.20,1.38,.30,.30,core,12)",
"for k in range(9):\n    z=22.56+k*.15\n    cone('Fresnel lens tier %02d'%k,z,.10,.59+(.10 if k==4 else 0),.56,glass,16)":"for k in range(5):\n    z=22.65+k*.25\n    cone('Fresnel lens tier %02d'%k,z,.18,.64+(.06 if k==2 else 0),.59,lensglass,16)",
}
for a,b in changes.items():
    assert text.count(a)==1,a
    text=text.replace(a,b)
assert text.count('stone[(i+j)%4]')==2
text=text.replace('stone[(i+j)%4]','stone[i%4]')
anchor="        if is_door:\n            for q in range(1,6):"
replacement='''        # Shallow solid stone surrounds, separated from the recessed jambs.
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
            for q in range(1,6):'''
assert text.count(anchor)==1
text=text.replace(anchor,replacement)
anchor="bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'lighthouse.blend'))"
replacement='''source_counts={'parts':len(parts),'vertices':sum(len(o.data.vertices) for o in parts),'polygons':sum(len(o.data.polygons) for o in parts)}
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
parts=exports'''
assert text.count(anchor)==1
text=text.replace(anchor,replacement)
anchor="report={'parts':len(parts),'vertices':sum(len(o.data.vertices) for o in parts),'polygons':sum(len(o.data.polygons) for o in parts),"
assert text.count(anchor)==1
text=text.replace(anchor,"report={**source_counts,'export_mesh_nodes':len(parts),")
text=text.replace("'base_width_m':8.03","'foundation_width_m':8.03")
target.write_text(text)
print(target)

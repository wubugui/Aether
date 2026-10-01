import bpy,bmesh,json
ob=bpy.data.objects['CloudSea52f_v0_low_saddle'];bm=bmesh.new();bm.from_mesh(ob.data);todo=set(bm.verts);comps=[]
while todo:
    stack=[todo.pop()];vs=[]
    while stack:
        v=stack.pop();vs.append(tuple(v.co))
        for e in v.link_edges:
            w=e.other_vert(v)
            if w in todo:todo.remove(w);stack.append(w)
    comps.append(vs)
print([c for c in comps if len(c)<10])

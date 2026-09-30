from pathlib import Path
root=Path('D:/test6');out=root/'captures'
source=(out/'seat_10e_plateau.py').read_text().replace('10e','10f')
source=source.replace('import cliff_sections_10d\n','import cliff_terrace_topology as C\nimport terrain_topology as T\n')
start=source.index('changed=[]\n')
end=source.index('assert all(len(e.link_faces)',start)
source=source[:start]+'''# Track the original asset's terrain-contact band before changing the cage.
old_ground={v.index:ground_at(v.co.x+origin[0],-v.co.y+origin[2]) for v in mesh.vertices if v.co.z> -14}
import cliff_sections_10d
C.SAMPLER=T.SurfaceSampler()
changed=[]
for v in mesh.vertices:
    if v.index not in old_ground:continue
    old=old_ground[v.index]
    fresh=ground_at(v.co.x+origin[0],-v.co.y+origin[2])
    weight=1-float(cliff_sections_10d.W.smooth(3,12,v.co.z-old))
    target=v.co.z+(fresh-old)*weight
    if v.index in rim:target=fresh-1.5
    if abs(target-v.co.z)>.001:changed.append([v.index,float(v.co.z),target])
    v.co.z=target
bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table()
rim_verts={bm.verts[k] for k in rim}
rim_edges=[e for e in bm.edges if all(v in rim_verts for v in e.verts)]
new_rim=[]
import math
for edge in rim_edges:
    count=math.ceil((edge.verts[0].co.xy-edge.verts[1].co.xy).length/3)
    if count<=1:continue
    before=set(bm.verts)
    bmesh.ops.subdivide_edges(bm,edges=[edge],cuts=count-1,use_grid_fill=False)
    for v in set(bm.verts)-before:
        v.co.z=ground_at(v.co.x+origin[0],-v.co.y+origin[2])-1.5
        new_rim.append(v)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
''' + source[end:]
# The edited mesh has new indices, so record its actual contact vertices.
source=source.replace("obj.vertex_groups.new(name='Seated ground rim').add(sorted(rim),1.,'REPLACE')", "contact=[v.index for v in mesh.vertices if v.co.z> -14 and abs(v.co.z-(ground_at(v.co.x+origin[0],-v.co.y+origin[2])-1.5))<.02]\nobj.vertex_groups.new(name='Seated ground rim').add(contact,1.,'REPLACE')")
(out/'seat_10f_plateau.py').write_text(source)

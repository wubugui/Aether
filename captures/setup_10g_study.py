from pathlib import Path
root=Path('D:/test6');out=root/'captures'
source=(out/'seat_10f_plateau.py').read_text().replace('10f','10g')
start=source.index('bm=bmesh.new();bm.from_mesh(mesh);bm.verts.ensure_lookup_table()')
end=source.index('assert all(len(e.link_faces)',start)
source=source[:start]+'''# Split only the shared contact edge and its two adjacent triangles.
# This avoids subdivision adding unrelated face-interior vertices.
vertices=[np.array(v.co) for v in mesh.vertices]
faces=[tuple(f.vertices) for f in mesh.polygons]
rim_edges=[tuple(e.vertices) for e in mesh.edges if all(k in rim for k in e.vertices)]
import math
for a,b in rim_edges:
    aa,bb=vertices[a],vertices[b]
    count=math.ceil(np.linalg.norm((aa-bb)[:2])/3)
    if count<=1:continue
    curve=[a]
    for j in range(1,count):
        p=aa*(1-j/count)+bb*(j/count)
        p[2]=ground_at(p[0]+origin[0],-p[1]+origin[2])-1.5
        curve.append(len(vertices));vertices.append(p)
    curve.append(b)
    adjacent=[i for i,f in enumerate(faces) if a in f and b in f]
    assert len(adjacent)==2
    for i in adjacent:
        face=faces[i];c=next(k for k in face if k not in (a,b))
        path=curve if face[(face.index(a)+1)%3]==b else curve[::-1]
        replacements=[(c,x,y) for x,y in zip(path,path[1:])]
        faces[i]=replacements[0];faces.extend(replacements[1:])
bm=bmesh.new()
for p in vertices:bm.verts.new(p)
bm.verts.ensure_lookup_table()
for f in faces:bm.faces.new([bm.verts[k] for k in f])
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
print('RIM CHECK',len(bm.verts),len(bm.faces),'bad edges',sum(len(e.link_faces)!=2 for e in bm.edges),'degenerate',sum(f.calc_area()<=1e-8 for f in bm.faces),flush=True)
''' + source[end:]
source=source.replace("attr=mesh.color_attributes['Palette']", "attr=mesh.color_attributes.get('Palette') or mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')")
(out/'seat_10g_plateau.py').write_text(source)

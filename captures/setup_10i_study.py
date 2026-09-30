from pathlib import Path
root=Path('D:/test6');out=root/'captures'
source=(out/'seat_10g_plateau.py').read_text().replace('10g','10i')
start=source.index('bm=bmesh.new()\nfor p in vertices:')
end=source.index('assert all(len(e.link_faces)',start)
source=source[:start]+'''# Rebuild the actual 2.5D roof with millimetre coordinate welding. The old
# CDT shell contains near-collinear needle strips that collapse in float32.
# Keep the edited native height controls; add no noise or artificial relief.
from mathutils.geometry import delaunay_2d_cdt
cloud={}
for p in vertices:
    if p[2]> -14:cloud.setdefault((round(float(p[0]),3),round(float(p[1]),3)),[]).append(float(p[2]))
controls=[[x,y,float(np.mean(z))] for (x,y),z in cloud.items()]
xy,_,roof,mapping,_,_=delaunay_2d_cdt([Vector(p[:2]) for p in controls],[],[],0,.002,True)
vertices=[[float(p.x),float(p.y),float(np.mean([controls[k][2] for k in ids]))] for p,ids in zip(xy,mapping)]
roof=[tuple(f) for f in roof]
edge_count={};oriented={}
for f in roof:
    for a,b in zip(f,f[1:]+f[:1]):
        key=tuple(sorted((a,b)));edge_count[key]=edge_count.get(key,0)+1;oriented[key]=(a,b)
boundary=[oriented[e] for e,count in edge_count.items() if count==1]
for k in {k for e in boundary for k in e}:
    p=vertices[k];p[2]=ground_at(p[0]+origin[0],-p[1]+origin[2])-1.5
count=len(vertices);vertices.extend([[x,y,-15.] for x,y,z in vertices[:]])
faces=list(roof)
faces.extend([(c+count,b+count,a+count) for a,b,c in roof])
for a,b in boundary:faces.extend([(b,a,a+count),(b,a+count,b+count)])
bm=bmesh.new()
for p in vertices:bm.verts.new(p)
bm.verts.ensure_lookup_table()
for f in faces:bm.faces.new([bm.verts[k] for k in f])
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
print('REBUILT CONTACT SHELL',len(bm.verts),len(bm.faces),'bad edges',sum(len(e.link_faces)!=2 for e in bm.edges),'degenerate',sum(f.calc_area()<=1e-8 for f in bm.faces),flush=True)
''' + source[end:]
source=source.replace("print('Seated',len(changed),'of',len(rim),'native rim vertices; volume',volume,flush=True)","print('Adjusted',len(changed),'native contact-band vertices; volume',volume,flush=True)")
(out/'seat_10i_plateau.py').write_text(source)
check=(out/'check_10g_plateau.py').read_text().replace('10g','10i');(out/'check_10i_plateau.py').write_text(check)

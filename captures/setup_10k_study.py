from pathlib import Path
root=Path('D:/test6');out=root/'captures'
source=(out/'seat_10j_plateau.py').read_text().replace('10j','10k')
start=source.index('count=len(vertices);vertices.extend(')
end=source.index('bm=bmesh.new()\nfor p in vertices:',start)
source=source[:start]+'''# This CDT roof has a convex footprint. Close it with an independently
# triangulated convex floor, avoiding nearly collinear roof needles below it.
ring=[a for a,b in boundary]
center_xy=np.array([vertices[k][:2] for k in ring]).mean(axis=0)
for a,b in boundary:
    aa,bb=np.array(vertices[a][:2]),np.array(vertices[b][:2])
    assert np.cross(bb-aa,center_xy-aa)>1e-6,'Floor fan requires a convex footprint and an interior center'
floor_map={}
for k in ring:
    x,y,z=vertices[k];floor_map[k]=len(vertices);vertices.append([x,y,-15.])
center=len(vertices);vertices.append([*center_xy,-15.])
faces=list(roof)
for a,b in boundary:
    fa,fb=floor_map[a],floor_map[b]
    faces.extend([(b,a,fa),(b,fa,fb),(fb,fa,center)])
''' + source[end:]
(out/'seat_10k_plateau.py').write_text(source)
(out/'check_10k_plateau.py').write_text((out/'check_10j_plateau.py').read_text().replace('10j','10k'))

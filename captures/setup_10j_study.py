from pathlib import Path
root=Path('D:/test6');out=root/'captures'
source=(out/'seat_10i_plateau.py').read_text().replace('10i','10j')
marker='count=len(vertices);vertices.extend([[x,y,-15.] for x,y,z in vertices[:]])'
insert='''# CDT removes redundant collinear hull points. Seat the final boundary,
# split its one roof triangle, then copy that topology to the closed bottom.
seated_boundary=[]
for a,b in boundary:
    aa,bb=np.array(vertices[a]),np.array(vertices[b])
    steps=max(1,math.ceil(np.linalg.norm((bb-aa)[:2])/3))
    curve=[a]
    for j in range(1,steps):
        p=aa*(1-j/steps)+bb*(j/steps)
        p[2]=ground_at(p[0]+origin[0],-p[1]+origin[2])-1.5
        curve.append(len(vertices));vertices.append(p.tolist())
    curve.append(b);seated_boundary.extend(zip(curve,curve[1:]))
    if steps==1:continue
    matches=[i for i,f in enumerate(roof) if a in f and b in f]
    assert len(matches)==1
    i=matches[0];f=roof[i];c=next(k for k in f if k not in (a,b))
    path=curve if f[(f.index(a)+1)%3]==b else curve[::-1]
    replacements=[(c,x,y) for x,y in zip(path,path[1:])]
    roof[i]=replacements[0];roof.extend(replacements[1:])
boundary=seated_boundary
'''
assert marker in source
source=source.replace(marker,insert+marker)
(out/'seat_10j_plateau.py').write_text(source)
(out/'check_10j_plateau.py').write_text((out/'check_10i_plateau.py').read_text().replace('10i','10j'))

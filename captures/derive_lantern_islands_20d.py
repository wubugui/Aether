"""Rebuild coastal landforms as sculpted surfaces; preserve the detailed 20c house."""
from pathlib import Path
root=Path(__file__).resolve().parents[1];target=root/'blender/model_lantern_islands_20d.py';assert not target.exists()
text=(root/'blender/model_lantern_islands_20b.py').read_text()
text=text.replace("OUT=ROOT/'captures/lantern_islands_study_20b'","OUT=ROOT/'captures/lantern_islands_study_20d'")
text=text.replace('from mathutils import Vector','from mathutils import Vector\nfrom mathutils.geometry import delaunay_2d_cdt')
for old,new in [('(.118,.136,.148)','(.043,.056,.066)'),('(.165,.172,.170)','(.070,.077,.080)'),('(.070,.085,.093)','(.028,.039,.046)'),('(.150,.205,.072)','(.050,.086,.018)'),('(.098,.107,.056)','(.061,.066,.032)')]:
    assert text.count(old)==1;text=text.replace(old,new)
text=text.replace("profiles=[(1.12,-.35,0,0),(1.0,.05,-.03,.01),(.83,.72,.05,-.04),(.53,1.0,-.10,.07)]",
    "profiles=[(1.12,-.35,0,0),(1.0,.05,-.03,.01),(.81,.63,.13,-.07),(.38,1.0,-.21,.12)]")
text=text.replace("top_offsets=[-.10,.04,.00,-.05,.07,-.02,.02,-.08]","top_offsets=[-.18,.11,.00,-.12,.16,-.09,.04,-.18]")
start=text.index('def island(name,sx,sy,plateau,variant):')
end=text.index("island('island_a',1.,1.,24.,0)",start)
text=text[:start]+'''def inside(x,y,polygon):
    result=False;j=len(polygon)-1
    for i,(xi,yi) in enumerate(polygon):
        xj,yj=polygon[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:result=not result
        j=i
    return result

def island(name,sx,sy,plateau,variant):
    reset();coast=[]
    for i,(x,y) in enumerate(outline):
        dx=([0,5,-3,1,-7,0,3,0,-5,0,2,7,1,-5,0,3,4,-3][i] if variant==1 else ([3,-5,4,0,-2,5,0,-7,4,0,-4,0,8,0,-4,0,3,-3][i] if variant==2 else 0))
        coast.append(((x+dx)*sx,y*sy))
    top_scales=[.98,.92,.85,.79,.88,.90,.96,.83,.79,.72,.74,.80,.95,.98,.89,.82,.75,.79]
    boundary=[(x*top_scales[(i+variant*3)%18],y*top_scales[(i+variant*3)%18]) for i,(x,y) in enumerate(coast)]
    def ungraded(x,y):
        a,b=x/sx,y/sy
        return max(5.,plateau-.0025*a*a-.003*b*b+2.8*math.sin((a+18+variant*9)/32)*math.cos((b-5)/45))
    # Only small building pads are level; the rest remains a real sculpted slope.
    pads=([(-3,6,6.3,6.3,.25),(-22,-2,4.3,7.0,0),(19,-6,3.8,6.2,-.15)] if variant==0 else
          ([(0,2,6.3,6.3,-.12),(-15,-3,3.6,5.9,.08)] if variant==1 else [(1,1,6.3,6.3,.1),(9,-4,3.2,5.3,-.15)]))
    def height(x,y):
        value=ungraded(x,y)
        for cx,cy,wx,wy,angle in pads:
            co,si=math.cos(angle),math.sin(angle);dx,dy=x-cx,y-cy
            u,v=co*dx-si*dy,si*dx+co*dy
            distance=max(abs(u)-wx,abs(v)-wy,0.)
            if distance<3.8:
                t=min(1.,distance/3.8);weight=1-t*t*(3-2*t)
                value=value*(1-weight)+ungraded(cx,cy)*weight
        return value
    coords=[Vector(p) for p in boundary]
    # A staggered terrain lattice provides coherent large facets, not random shards.
    spacing=9.*sx
    for row in range(-12,13):
        y=row*spacing*.866
        for col in range(-14,15):
            x=(col+.5*(row%2))*spacing
            if inside(x,y,boundary) and min((Vector((x,y))-p).length for p in coords[:18])>2.:
                coords.append(Vector((x,y)))
    for cx,cy,wx,wy,angle in pads:
        co,si=math.cos(angle),math.sin(angle)
        for u,v in [(-wx,-wy),(wx,-wy),(wx,wy),(-wx,wy),(0,0)]:
            x,y=cx+co*u+si*v,cy-si*u+co*v
            if inside(x,y,boundary):coords.append(Vector((x,y)))
    verts2,edges,triangles,original,_,_=delaunay_2d_cdt(coords,[],[list(range(18))],1,.00001)
    assert triangles and all(len(t)==3 for t in triangles)
    n=len(verts2);top=[(p.x,p.y,height(p.x,p.y)) for p in verts2]
    lower=[(x,y,z-.65) for x,y,z in top]
    edge_counts={}
    for triangle in triangles:
        for j in range(3):
            a,b=triangle[j],triangle[(j+1)%3];key=tuple(sorted((a,b)))
            edge_counts[key]=edge_counts.get(key,0)+1
    border=[edge for edge,count in edge_counts.items() if count==1]
    capfaces=[tuple(t) for t in triangles]+[tuple(i+n for i in reversed(t)) for t in triangles]
    capfaces.extend([(a,b,b+n,a+n) for a,b in border])
    cap=mesh(name+' sculpted grass terrain',top+lower,capfaces,grass);cap.data.materials.append(soil)
    for i,p in enumerate(cap.data.polygons):
        if i>=len(triangles):p.material_index=1
    # Side silhouette follows the same constrained boundary as the grass.
    # Nonplanar cliff quads are explicitly split into broad fracture planes.
    coreverts=[];corefaces=[]
    for level in range(3):
        for i,(x,y) in enumerate(coast):
            k=top_scales[(i+variant*3)%18]
            if level==0:point=(x*1.10,y*1.10,-9.)
            elif level==1:point=(x,y,1.0+(i%3)*.22)
            else:point=(x*(1+k)/2,y*(1+k)/2,height(boundary[i][0],boundary[i][1])*.48)
            coreverts.append(point)
    coreverts+=lower
    index={}
    for i,orig in enumerate(original):
        for source in orig:
            if source<18:index[source]=54+i
    assert len(index)==18
    corefaces.append(tuple(reversed(range(18))))
    for level in range(3):
        for i in range(18):
            j=(i+1)%18;a=level*18+i;b=level*18+j
            c=(level+1)*18+j if level<2 else index[j]
            d=(level+1)*18+i if level<2 else index[i]
            if (i+level)%2:corefaces.extend([(a,b,d),(b,c,d)])
            else:corefaces.extend([(a,b,c),(a,c,d)])
    corefaces.extend([tuple(54+i for i in tri) for tri in triangles])
    core=mesh(name+' faulted bedrock',coreverts,corefaces,rock)
    core.data.materials.append(rockface);core.data.materials.append(rockdark)
    for p in core.data.polygons:
        if p.center.z<2.:p.material_index=2
        elif p.normal.x<-.60 and p.normal.z<.35:p.material_index=1
    # Four unequal promontories replace the evenly spaced ring of eight round caps.
    for i,(pos,size,turn) in enumerate([
        ((-72,-31,0),(18,11,19),-.60),((70,-7,0),(11,25,13),.70),
        ((25,44,0),(25,10,10),-.25),((-47,34,0),(12,17,15),.35)]):
        x,y,z=pos;a,b,c=size
        block(name+' fractured headland %02d'%i,(x*sx,y*sy,z),(a*sx,b*sy,c*plateau/24),turn+variant*.25)
    for i,(x,y,a,b,h) in enumerate([(-84,-37,10,8,5),(-61,-61,12,8,6),(45,-60,10,7,4),(91,22,9,13,6),(38,58,13,8,5),(-60,48,10,9,4)]):
        block(name+' tidal shelf %02d'%i,(x*sx,y*sy,-.5),(a*sx,b*sy,h),i*.43)
    freeze(name,'Sculpted constrained terrain with small graded building pads, unequal grass tongues and connected faulted rock cliffs. No world or weather acceptance.')

'''+text[end:]
start=text.index("reset()\nbox('Keeper broad masonry footing'")
end=text.index("report={'label':'20b'",start)
text=text[:start]+'''# Keeper architecture is retained byte-for-byte from the corrected 20c source.
prior=ROOT/'captures/lantern_islands_study_20c'
record=next(r for r in json.loads((prior/'model-report.json').read_text())['assets'] if r['name']=='keeper_house')
for extension in ['.blend','.glb']:shutil.copy2(prior/('keeper_house'+extension),OUT/('keeper_house'+extension))
reports.append(record)

'''+text[end:]
text=text.replace("'label':'20b'","'label':'20d'")
target.write_text(text);print(target)

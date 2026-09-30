"""A crown, broken wall, shoulder shelf and foot slope for each cliff asset."""
import math
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
import terrain_topology as T
SAMPLER=T.SurfaceSampler()

def ground_at(x,z):
    cell=(math.floor(x/768),math.floor(z/768))
    if cell not in SAMPLER.tiles:
        v,f=T.chunk_mesh(*cell);SAMPLER.add(*cell,v,f)
    return float(SAMPLER.height(x,z))

def make_terraced_cliff(points,origin,name):
    coords=[Vector((p[0]-origin[0],p[2]-origin[2])) for p in points]
    xy,_,tris,original,_,_=delaunay_2d_cdt(coords,[],[],0,.00001,True)
    vertices=[]
    for p,ids in zip(xy,original):
        assert ids
        vertices.append([p.x,float(np.mean([points[i][1] for i in ids])),p.y])
    faces=[tuple(t) for t in tris]
    count={}
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):
            k=tuple(sorted((a,b)));count[k]=count.get(k,0)+1
    boundary={i for e,n in count.items() if n==1 for i in e}
    # The cap's convex hull has a consistent ring, but its surface retains
    # every authored saddle/control point from the internal triangulation.
    ring=sorted(boundary,key=lambda i:math.atan2(vertices[i][2],vertices[i][0]))
    center_y=float(np.mean([vertices[i][1] for i in ring]))
    crown=[vertices[i][:] for i in ring]
    mesa=name=='cliff_western_mesa'
    # The distant mesa has one exposed escarpment, not the foreland's ledges.
    # Foreground shelves vary around each asset instead of forming a belt.
    for step in range(0 if mesa else 2):
        next_ring=[]
        for i,(x,y,z) in enumerate(crown):
            angle=math.atan2(z,x)
            front=.5+.5*math.sin(angle)
            variation=math.sin(i*2.9+.4)
            if step==0:
                xx=x*1.05+2*variation
                zz=z*1.06+front*5-(1-front)*22
                yy=y-13-4*(.5+.5*variation)
            elif step==1:
                width=1.12+.18*(.5+.5*math.sin(angle*2+.7))
                xx=x*width+2*variation
                zz=z*width+front*8-(1-front)*34
                yy=y-18-8*(.5+.5*variation)
            next_ring.append(len(vertices));vertices.append([xx,yy,zz])
        for i,a in enumerate(ring):
            j=(i+1)%len(ring);b=ring[j];c=next_ring[j];d=next_ring[i]
            # Alternating diagonals avoid a continuous seam on every wall.
            faces.extend([(a,b,c),(a,c,d)] if i%2 else [(a,b,d),(b,c,d)])
        ring=next_ring
    foot_controls=[]
    for i,(x,y,z) in enumerate(crown):
        angle=math.atan2(z,x);front=.5+.5*math.sin(angle)
        if mesa:xx=x*1.75;zz=z*1.02-25
        else:
            xx=x*(1.30+.16*math.sin(angle*2+i*.3))
            zz=z*1.30+front*18-(1-front)*45
        # Keep the mesa's talus on actual land, instead of projecting its
        # supporting block through the beach and into the sea.
        if mesa:
            for _ in range(24):
                if ground_at(xx+origin[0],zz+origin[2])>=7:break
                xx*=.94;zz*=.94
        foot_controls.append([xx,zz])
    foot=[];edge_loops=[]
    for i,a in enumerate(foot_controls):
        b=foot_controls[(i+1)%len(foot_controls)]
        count=max(1,math.ceil(math.dist(a,b)/5))
        ids=[]
        for j in range(count):
            t=j/count;xx=a[0]*(1-t)+b[0]*t;zz=a[1]*(1-t)+b[1]*t
            yy=ground_at(xx+origin[0],zz+origin[2])-1.2
            ids.append(len(vertices));foot.append(len(vertices));vertices.append([xx,yy,zz])
        edge_loops.append(ids)
    for i,ids in enumerate(edge_loops):
        j=(i+1)%len(ring);curve=ids+[edge_loops[j][0]]
        for a,b in zip(curve[:-1],curve[1:]):faces.append((ring[i],a,b))
        faces.append((ring[i],curve[-1],ring[j]))
    floor=[]
    for i in foot:
        x,y,z=vertices[i];floor.append(len(vertices));vertices.append([x,min(-12,y-12),z])
    for i,a in enumerate(foot):
        j=(i+1)%len(foot)
        faces.extend([(a,foot[j],floor[j]),(a,floor[j],floor[i])])
    center=len(vertices);vertices.append([0,-12,0])
    for i,a in enumerate(floor):faces.append((floor[(i+1)%len(floor)],a,center))
    return vertices,faces

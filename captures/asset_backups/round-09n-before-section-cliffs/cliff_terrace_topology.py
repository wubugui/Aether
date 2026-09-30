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

def _make_mesa(points,origin,name):
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
    if name=='cliff_western_mesa':
        # Short vertical erosion bands along a broad escarpment. Subdivide
        # the cap edge too, so every wall strip has its own connected top.
        cap=[p[:] for p in vertices]
        for k,a in enumerate(ring):
            b=ring[(k+1)%len(ring)];aa=np.array(vertices[a]);bb=np.array(vertices[b])
            n=max(1,math.ceil(np.linalg.norm((bb-aa)[[0,2]])/12))
            for j in range(1,n):cap.append((aa*(1-j/n)+bb*j/n).tolist())
        xy,_,tris,original,_,_=delaunay_2d_cdt([Vector((p[0],p[2])) for p in cap],[],[],0,.00001,True)
        vertices=[[p.x,float(np.mean([cap[k][1] for k in ids])),p.y] for p,ids in zip(xy,original)]
        faces=[tuple(t) for t in tris];count={}
        for f in faces:
            for a,b in zip(f,f[1:]+f[:1]):
                key=tuple(sorted((a,b)));count[key]=count.get(key,0)+1
        boundary={k for edge,n in count.items() if n==1 for k in edge}
        ring=sorted(boundary,key=lambda i:math.atan2(vertices[i][2],vertices[i][0]))
    center_y=float(np.mean([vertices[i][1] for i in ring]))
    crown=[vertices[i][:] for i in ring]
    mesa=name=='cliff_western_mesa'
    # The distant mesa has one exposed escarpment, not the foreland's ledges.
    # Foreground shelves vary around each asset instead of forming a belt.
    for step in range(1 if mesa else 2):
        next_ring=[]
        for i,(x,y,z) in enumerate(crown):
            angle=math.atan2(z,x)
            front=.5+.5*math.sin(angle)
            variation=math.sin(i*2.9+.4)
            if mesa:
                xx=x*1.06+.9*variation
                zz=z*1.04+1.4*math.sin(i*1.7)
                yy=y-20-2*(.5+.5*variation)
            elif step==0:
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


def make_terraced_cliff(points,origin,name,top,base):
    if name=='cliff_western_mesa':return _make_mesa(points,origin,name)
    # A cliff is a patch of solid terrain, with independently sculpted summit,
    # face, gullies and rear slope. Never connect a dense foot to a single
    # upper vertex: that produces the tall fan-shaped blades in the old kit.
    controls=[list(p-origin) for p in points]
    controls=np.asarray(controls,float).tolist()
    highest=max(top,key=lambda p:p[2]);peak=points[top.index(highest)]
    focal=941/(2*math.tan(math.radians(25)));pitch=math.radians(-3.5)
    for u,v,_ in base:
        if v<highest[1]+65:continue
        # Measure a wall foot on a coherent forward-facing section. The old
        # arbitrary foot heights placed these points BEHIND their summits.
        z=peak[2]+(v-highest[1])*.24+5
        ray=np.array([(u-836)/focal,math.cos(pitch)*(470.5-v)/focal+math.sin(pitch),math.sin(pitch)*(470.5-v)/focal-math.cos(pitch)])
        p=np.array([0,145,250])+ray*((z-250)/ray[2])
        p[1]=max(p[1],ground_at(p[0],p[2])+2)
        controls.append((p-origin).tolist())
    # The back and flanks are broad descending ridges. They remain part of
    # this separately placeable asset and meet the actual native terrain.
    for i,p in enumerate(points[:len(top)]):
        if p[2]>origin[2]:continue
        x=p[0]-origin[0];z=p[2]-origin[2]-45-9*math.sin(i*1.4)
        ground=ground_at(x+origin[0],z+origin[2])
        controls.append([x, max(ground+1,p[1]-18-4*math.sin(i*2.2)),z])

    def triangulate(values):
        vv,_,ff,ids,_,_=delaunay_2d_cdt([Vector((p[0],p[2])) for p in values],[],[],0,.00001,True)
        return [[p.x,float(np.mean([values[k][1] for k in sources])),p.y] for p,sources in zip(vv,ids)], [tuple(f) for f in ff]
    def boundary(vertices,faces):
        counts={}
        for f in faces:
            for a,b in zip(f,f[1:]+f[:1]):
                key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
        members={k for e,n in counts.items() if n==1 for k in e}
        return sorted(members,key=lambda k:math.atan2(vertices[k][2],vertices[k][0]))
    initial,initial_faces=triangulate(controls)
    outline=[]
    for k in boundary(initial,initial_faces):
        x,_,z=initial[k];length=max(1,math.hypot(x,z))
        outline.append([x+x/length*24,z+z/length*28])
    for i,a in enumerate(outline):
        b=outline[(i+1)%len(outline)];n=max(1,math.ceil(math.dist(a,b)/9))
        for j in range(n):
            t=j/n;x=a[0]*(1-t)+b[0]*t;z=a[1]*(1-t)+b[1]*t
            controls.append([x,ground_at(x+origin[0],z+origin[2])-1.5,z])
    vertices,faces=triangulate(controls)
    # Add irregular intermediate landform controls within broad faces. This
    # breaks the upper-to-foot strips into actual knuckles and drainage dips.
    triangles=np.asarray(vertices)[np.asarray(faces)]
    for i,t in enumerate(triangles):
        a,b,c=t
        area=abs(np.cross((b-a)[[0,2]],(c-a)[[0,2]]))*.5
        if area<55:continue
        p=t.mean(axis=0)
        g=ground_at(p[0]+origin[0],p[2]+origin[2])
        relief=min(3.8,max(0,(p[1]-g)*.22))
        p[1]+=math.sin(i*2.13+len(name)) * relief
        controls.append(p.tolist())
    vertices,faces=triangulate(controls)
    ring=boundary(vertices,faces)
    floor=[]
    for k in ring:
        x,y,z=vertices[k];floor.append(len(vertices));vertices.append([x,-15,z])
    for i,a in enumerate(ring):
        j=(i+1)%len(ring)
        faces.extend([(a,ring[j],floor[j]),(a,floor[j],floor[i])])
    center=len(vertices);vertices.append([0,-15,0])
    for i,a in enumerate(floor):faces.append((floor[(i+1)%len(floor)],a,center))
    return vertices,faces

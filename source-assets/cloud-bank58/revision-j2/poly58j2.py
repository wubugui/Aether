"""Bounded authored halfspace-cage hard union. Pure NumPy; no native execution.

The only tolerances reconcile repeated arithmetic at the same mathematical
intersection. No jitter, simplification, smoothing, geometry repair or remesh.
Ambiguous coplanar source/cutter faces and positive-area slivers are failures.
"""
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import math
import numpy as np


def require(value, message):
    if not value:
        raise ValueError(message)


def area_vector(poly):
    p=np.asarray(poly,float)
    return sum((np.cross(p[i]-p[0],p[i+1]-p[0]) for i in range(1,len(p)-1)),np.zeros(3))*.5


def clean_loop(points, eps, audit):
    out=[]
    for p in points:
        if not out or np.linalg.norm(p-out[-1])>eps:
            out.append(np.asarray(p,float))
        else:
            audit['consecutive_equal_arithmetic_stations']+=1
    if len(out)>1 and np.linalg.norm(out[0]-out[-1])<=eps:
        out.pop();audit['consecutive_equal_arithmetic_stations']+=1
    return out


def valid_polygon(poly, tol, audit):
    if len(poly)<3:
        audit['zero_dimensional_clip_outputs']+=1
        return False
    area=np.linalg.norm(area_vector(poly))
    if area<1e-12:
        audit['zero_area_clip_outputs']+=1
        return False
    require(area>=tol['minimum_area_m2'],f'Positive-area clipping sliver {area}; no silent repair')
    return True


def planes_for(spec):
    angle=math.radians(spec['yaw_degrees']);co,si=math.cos(angle),math.sin(angle)
    R=np.array([[co,-si,0],[si,co,0],[0,0,1.]])
    if 'matrix3' in spec: R=np.asarray(spec['matrix3'],float)
    scale=np.asarray(spec['scale'],float)
    require(np.all(scale>0),'Nonpositive cage scale')
    center=np.asarray(spec['center'],float)
    rows=[]
    for p in spec['planes']:
        n=np.linalg.inv(R).T@(np.asarray(p[:3],float)/scale);d=p[3]+n@center
        length=np.linalg.norm(n);rows.append([*(n/length),d/length])
    return np.asarray(rows)


def cage(spec,tol,audit):
    planes=planes_for(spec);vertices=[]
    for triple in combinations(range(len(planes)),3):
        m=planes[list(triple),:3];det=abs(np.linalg.det(m))
        if det<1e-11:
            audit['nonunique_parallel_plane_triples']+=1
            continue
        point=np.linalg.solve(m,planes[list(triple),3])
        if np.max(planes[:,:3]@point-planes[:,3])>tol['classification_m']:
            continue
        if not any(np.linalg.norm(point-q)<tol['weld_m'] for q in vertices):vertices.append(point)
    require(len(vertices)>=4,'Empty or degenerate authored cage')
    vertices=np.asarray(vertices);polygons=[]
    for plane_id,row in enumerate(planes):
        selected=vertices[np.abs(vertices@row[:3]-row[3])<=tol['weld_m']]
        if len(selected)<3:continue
        center=selected.mean(axis=0);u=selected[0]-center;u/=np.linalg.norm(u)
        v=np.cross(row[:3],u)
        angles=np.arctan2((selected-center)@v,(selected-center)@u)
        poly=selected[np.argsort(angles)]
        require(area_vector(poly)@row[:3]>0,'Cage face ordering')
        polygons.append(dict(points=poly,owner=spec['id'],plane=plane_id,normal=row[:3]))
    require(len(polygons)>=4,'No bounded cage surface')
    return dict(planes=planes,polygons=polygons,vertices=vertices)


def split_polygon(poly,plane,tol,audit):
    distances=np.asarray(poly)@plane[:3]-plane[3]
    eps=tol['classification_m']
    negative=distances < -eps;positive=distances > eps
    if not positive.any():return poly,[]
    if not negative.any():return [],poly
    inside=[];outside=[]
    for i,a in enumerate(poly):
        j=(i+1)%len(poly);b=poly[j];da,db=distances[i],distances[j]
        if da<=eps:inside.append(a)
        if da>=-eps:outside.append(a)
        if (da < -eps and db > eps) or (da > eps and db < -eps):
            point=a+(b-a)*(da/(da-db))
            inside.append(point);outside.append(point)
    return clean_loop(inside,eps,audit),clean_loop(outside,eps,audit)


def subtract_cage(poly,planes,tol,audit):
    # A separating plane proves the complete polygon is outside this cage.
    # Preserve that polygon rather than needlessly partitioning its plane.
    distances=np.asarray(poly)@planes[:,:3].T-planes[:,3]
    if np.any(np.all(distances>=tol['classification_m'],axis=0)):return [poly]
    remaining=poly;outside=[]
    for plane in planes:
        if len(remaining)<3:break
        remaining,part=split_polygon(remaining,plane,tol,audit)
        if part and valid_polygon(part,tol,audit):outside.append(part)
    return outside


def exposed_polygons(cages,tol,audit):
    surface=[]
    for ci,current in enumerate(cages):
        for face in current['polygons']:
            fragments=[list(face['points'])]
            for cj,cutter in enumerate(cages):
                if ci==cj:continue
                # Distinct authored source planes are mandatory. Do not hide
                # coplanar overlap behind an arbitrary ownership priority.
                for plane in cutter['planes']:
                    if np.max(np.abs(face['points']@plane[:3]-plane[3]))<=tol['weld_m']:
                        raise ValueError('Coplanar source/cutter faces require explicit redesign')
                fragments=[piece for fragment in fragments for piece in subtract_cage(fragment,cutter['planes'],tol,audit)]
                require(len(fragments)<200,'Clipping fragmentation limit')
                if not fragments:break
            surface.extend(dict(face,points=np.asarray(fragment)) for fragment in fragments)
    require(0<len(surface)<500,'Exposed polygon count outside bounded trial')
    return surface


def weld_conform(surface,tol,audit):
    eps=tol['weld_m'];vertices=[];members=[];loops=[]
    def identify(p):
        if vertices:
            distances=np.linalg.norm(np.asarray(vertices)-p,axis=1);ids=np.flatnonzero(distances<=eps)
        else:ids=[]
        if len(ids):
            require(len(ids)==1,'Ambiguous weld cluster')
            index=int(ids[0]);members[index].append(p)
            audit['maximum_weld_displacement_m']=max(audit['maximum_weld_displacement_m'],float(np.linalg.norm(vertices[index]-p)))
            require(max(np.linalg.norm(p-q) for q in members[index])<=eps,'Weld cluster diameter exceeds explicit tolerance')
            return index
        vertices.append(p);members.append([p]);return len(vertices)-1
    for face in surface:
        loop=[identify(p) for p in face['points']]
        require(len(set(loop))==len(loop),'Weld would collapse a positive face')
        loops.append(loop)
    V=np.asarray(vertices);conformed=[]
    for loop in loops:
        new=[]
        for a,b in zip(loop,loop[1:]+loop[:1]):
            edge=V[b]-V[a];length2=edge@edge
            require(length2>=tol['minimum_edge_m']**2,'Tiny clipping edge; no repair')
            station=(V-V[a])@edge/length2
            offsets=np.linalg.norm(V-(V[a]+station[:,None]*edge),axis=1)
            middle=np.flatnonzero((station>0)&(station<1)&(offsets<=eps))
            middle=[int(k) for k in middle if k not in (a,b)]
            ordered=sorted(middle,key=lambda k:station[k])
            new.extend([a,*ordered]);audit['shared_edge_stations_inserted']+=len(ordered)
        require(len(set(new))==len(new),'Conforming duplicated a loop station')
        conformed.append(new)
    # Centroid fans retain every mandatory collinear edge station. All triangles
    # within each authored plane have the same normal; no faceting by subdivision.
    faces=[];owners=[];panels=[]
    for source,loop in zip(surface,conformed):
        center=V[loop].mean(axis=0);mid=len(vertices);vertices.append(center)
        for a,b in zip(loop,loop[1:]+loop[:1]):
            faces.append([a,b,mid]);owners.append(source['owner']);panels.append(source['owner']+':'+str(source['plane']))
    return np.asarray(vertices),np.asarray(faces,int),owners,panels


def topology(V,F,tol):
    require(np.isfinite(V).all(),'Nonfinite coordinates')
    require(len(V)<=tol['maximum_vertices'] and len(F)<=tol['maximum_triangles'],'Bounded final mesh budget')
    tri=V[F];normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(normals,axis=1)*.5
    require(float(areas.min())>=tol['minimum_area_m2'],'Degenerate/positive-area sliver triangle')
    undirected=defaultdict(list);directed=Counter()
    for i,f in enumerate(F):
        require(len(set(map(int,f)))==3,'Repeated face vertex')
        for a,b in zip(f,np.roll(f,-1)):
            undirected[tuple(sorted((int(a),int(b))))].append(i);directed[int(a),int(b)]+=1
    require(all(len(a)==2 for a in undirected.values()),'Nonmanifold edge incidence')
    require(all(directed[a,b]==directed[b,a]==1 for a,b in undirected),'Directed edge winding')
    require(len({tuple(sorted(map(int,f))) for f in F})==len(F),'Duplicate triangle')
    require(set(F.ravel())==set(range(len(V))),'Unused vertex')
    adjacency=defaultdict(set)
    for shared in undirected.values():a,b=shared;adjacency[a].add(b);adjacency[b].add(a)
    seen={0};queue=[0]
    while queue:
        for j in adjacency[queue.pop()]:
            if j not in seen:seen.add(j);queue.append(j)
    require(len(seen)==len(F),'More than one surface component')
    # Edge incidence alone does not reject a pinched/nonmanifold vertex.
    links=defaultdict(lambda:defaultdict(set))
    for f in F:
        for k,v in enumerate(f):
            a,b=map(int,(f[(k+1)%3],f[(k+2)%3]));links[int(v)][a].add(b);links[int(v)][b].add(a)
    for v,link in links.items():
        require(all(len(neighbors)==2 for neighbors in link.values()),'Vertex link is not a cycle')
        visited={next(iter(link))};pending=list(visited)
        while pending:
            for k in link[pending.pop()]:
                if k not in visited:visited.add(k);pending.append(k)
        require(len(visited)==len(link),'Disconnected vertex link')
    euler=len(V)-len(undirected)+len(F);require(euler==2,'Shell is not genus zero')
    q=tri-V.mean(axis=0);volume=float(np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2])).sum()/6)
    require(volume>0,'Nonpositive volume')
    edge_lengths=np.array([np.linalg.norm(V[a]-V[b]) for a,b in undirected])
    require(edge_lengths.min()>=tol['minimum_edge_m'],'Tiny edge')
    return dict(vertices=len(V),triangles=len(F),edges=len(undirected),components=1,euler=euler,positive_volume_m3=volume,minimum_triangle_area_m2=float(areas.min()),minimum_edge_m=float(edge_lengths.min()),maximum_edge_m=float(edge_lengths.max()),directed_edge_incidence_two=True,all_vertex_links_one_cycle=True)


def fingerprint(V,F):
    return dict(vertices_sha256=hashlib.sha256(np.asarray(V,dtype='<f8').tobytes()).hexdigest(),faces_sha256=hashlib.sha256(np.asarray(F,dtype='<i4').tobytes()).hexdigest())


def build(config):
    tol=config['tolerances'];audit=dict(consecutive_equal_arithmetic_stations=0,zero_dimensional_clip_outputs=0,zero_area_clip_outputs=0,nonunique_parallel_plane_triples=0,maximum_weld_displacement_m=0.,shared_edge_stations_inserted=0)
    cages=[cage(spec,tol,audit) for spec in config['controls']]
    surface=exposed_polygons(cages,tol,audit)
    V,F,owners,panels=weld_conform(surface,tol,audit)
    proof=topology(V,F,tol)
    return dict(vertices=V,faces=F,owners=owners,panels=panels,proof=proof,audit=audit,cages=cages,exposed_polygon_count=len(surface),fingerprint=fingerprint(V,F))


def source_basis(frame):
    u=np.asarray(frame['local_u_world']);v=np.asarray(frame['local_v_world'])
    return np.array([[u[0],v[0],0],[-u[2],-v[2],0],[0,0,1.]])


def intersection_check(V,F,eps=2e-6):
    """All AABB-overlap triangle pairs, including pairs sharing vertices.

    Coplanar pairs use 2-D convex clipping; noncoplanar pairs compare intervals
    of their plane-line slices. A locus is permitted only on the exact common
    indexed edge/vertex. Float32 conversion is checked by the same algorithm.
    """
    triangles=V[F];cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
    normals=cross/np.linalg.norm(cross,axis=1)[:,None]
    low=triangles.min(axis=1);high=triangles.max(axis=1);tested=coplanar=0
    def plane_slice(tri,n,d):
        dis=tri@n-d;points=[]
        for k in range(3):
            if abs(dis[k])<=eps:points.append(tri[k])
            j=(k+1)%3
            if dis[k]*dis[j]<-eps*eps:
                points.append(tri[k]+(tri[j]-tri[k])*dis[k]/(dis[k]-dis[j]))
        result=[]
        for p in points:
            if not any(np.linalg.norm(p-q)<=eps for q in result):result.append(p)
        return result
    def coplanar_area(a,b,n):
        drop=int(np.argmax(np.abs(n)));a=np.delete(a,drop,axis=1);b=np.delete(b,drop,axis=1)
        def cross2(v,w):return v[0]*w[1]-v[1]*w[0]
        if cross2(b[1]-b[0],b[2]-b[0])<0:b=b[::-1]
        out=list(a)
        for k in range(3):
            edge=b[(k+1)%3]-b[k];previous=out;out=[]
            if not previous:break
            for j,p in enumerate(previous):
                q=previous[(j+1)%len(previous)];dp=cross2(edge,p-b[k]);dq=cross2(edge,q-b[k])
                if dp>=0:out.append(p)
                if (dp<0<dq) or (dq<0<dp):out.append(p+(q-p)*dp/(dp-dq))
        if len(out)<3:return 0.
        return abs(sum(cross2(out[k]-out[0],out[k+1]-out[0]) for k in range(1,len(out)-1)))*.5
    for i,a in enumerate(triangles):
        candidates=np.flatnonzero(np.all(high[i]+eps>=low,axis=1)&np.all(high+eps>=low[i],axis=1))
        for j in candidates:
            if j<=i:continue
            tested+=1;b=triangles[j];shared=sorted(set(map(int,F[i]))&set(map(int,F[j])))
            n,m=normals[i],normals[j];da=a[0]@n;db=b[0]@m
            ab=b@n-da;ba=a@m-db
            if np.all(ab>eps) or np.all(ab<-eps) or np.all(ba>eps) or np.all(ba<-eps):continue
            direction=np.cross(n,m);length=np.linalg.norm(direction)
            if length<1e-7 and max(np.max(np.abs(ab)),np.max(np.abs(ba)))<=eps:
                coplanar+=1;area=coplanar_area(a,b,n)
                require(area<=eps*eps*100,f'Coplanar overlap triangles {i},{j}, area {area}')
                continue
            if length<1e-10:continue
            pa,pb=plane_slice(a,m,db),plane_slice(b,n,da)
            if not pa or not pb:continue
            direction/=length
            va=np.asarray(pa)@direction;vb=np.asarray(pb)@direction
            lo=max(va.min(),vb.min());hi=min(va.max(),vb.max())
            if lo>hi+eps:continue
            require(bool(shared),f'Unexpected disjoint triangle contact/intersection {i},{j}')
            # Compare the intersection interval directly with the indexed
            # shared locus, avoiding unstable reconstruction along the line
            # of two nearly parallel planes.
            common=V[shared]@direction
            require(lo>=common.min()-eps*4 and hi<=common.max()+eps*4,
                    f'Unexpected triangle contact/intersection {i},{j}, shared={shared}')
    return dict(passed=True,aabb_pairs_tested=tested,coplanar_pairs_tested=coplanar,all_pairs_including_shared_vertex_checked=True,tolerance_m=eps)

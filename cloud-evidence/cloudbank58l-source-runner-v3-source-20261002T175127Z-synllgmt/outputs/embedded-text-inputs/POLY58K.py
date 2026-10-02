"""Direct authored cross-section envelope. Pure NumPy, no native execution.

Topology, fingerprint, source basis and all-pairs triangle checker are copied
verbatim from audited J2. The construction is entirely replaced: one ring skin
and two tip fans, never a union of independently bounded shells. Persistent
recipe data contains every section, angular station and strip diagonal.
"""
from collections import Counter, defaultdict
import hashlib
import numpy as np

def require(value, message):
    if not value:
        raise ValueError(message)

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


def authored_arrays(config):
    recipe=config['authoring_recipe'];rings=recipe['rings'];n=12
    require(recipe['type']=='authored_swollen_section_envelope','Unknown authoring recipe')
    require(len(rings)==16 and len(recipe['diagonal_rows'])==15,'Explicit station topology changed')
    require(len(config['controls'])==6,'Six semantic handles required')
    V=[];weights=[];stations=[];sectors=[]
    for i,row in enumerate(rings):
        center=np.asarray(row['center_uvy_m'],float)
        require(row['top_y_m']>center[2]>row['bottom_y_m'],'Positive section thickness')
        require(row['front_halfwidth_m']>0 and row['back_halfwidth_m']>0,'Positive section width')
        angles=np.radians(row['angles_degrees']);offset=np.asarray(row['u_offsets_m'])
        require(len(angles)==n and len(offset)==n and np.all(np.diff(angles)>0),'Ordered authored sectors')
        require(angles[-1]-angles[0]<2*np.pi,'Single angular turn')
        for j,angle in enumerate(angles):
            co,si=np.cos(angle),np.sin(angle)
            p=center+np.array([offset[j],co*(row['back_halfwidth_m'] if co>=0 else row['front_halfwidth_m']),
                si*(row['top_y_m']-center[2] if si>=0 else center[2]-row['bottom_y_m'])])
            belly=max(0.,-si)*recipe['belly_influence_maximum']
            w=np.r_[np.asarray(row['control_weights'])*(1-belly),belly]
            require(np.all(w>=0) and abs(w.sum()-1)<1e-12,'Convex semantic weights')
            V.append(p);weights.append(w);stations.append(i);sectors.append(j)
    # Ordered u sections ensure a monotone base envelope; no overlapping cage seams.
    for i in range(len(rings)-1):
        require(max(p[0] for p in V[i*n:(i+1)*n])<min(p[0] for p in V[(i+1)*n:(i+2)*n]),'Authored station ordering')
    left=len(V);V.append(recipe['left_tip_uvy_m']);weights.append([1,0,0,0,0,0]);stations.append(-1);sectors.append(-1)
    right=len(V);V.append(recipe['right_tip_uvy_m']);weights.append([0,0,1,0,0,0]);stations.append(len(rings));sectors.append(-1)
    require(V[left][0]<min(p[0] for p in V[:n]) and V[right][0]>max(p[0] for p in V[-n-2:-2]),'Tips outside terminal rings')
    F=[];patch=[]
    for i,diagonals in enumerate(recipe['diagonal_rows']):
        require(len(diagonals)==n and set(diagonals)<=set('01'),'Explicit patch diagonals')
        for j in range(n):
            a=i*n+j;b=i*n+(j+1)%n;c=(i+1)*n+(j+1)%n;d=(i+1)*n+j
            pair=([a,b,c],[a,c,d]) if diagonals[j]=='0' else ([a,b,d],[b,c,d])
            F.extend(pair);patch.extend([i*n+j]*2)
    for j in range(n):
        F.extend(([left,(j+1)%n,j],[right,(len(rings)-1)*n+j,(len(rings)-1)*n+(j+1)%n]))
        patch.extend([180+j,192+j])
    return np.asarray(V,float),np.asarray(F,int),np.asarray(weights,float),patch,stations,sectors


def build(config):
    rest,F,W,patch,stations,sectors=authored_arrays(config);V=rest.copy()
    for i,row in enumerate(config['controls']):
        center=np.asarray(row.get('rest_center',row['center']),float)
        moved=np.asarray(row['center'],float)
        angle=np.radians(row['yaw_degrees']);co,si=np.cos(angle),np.sin(angle)
        linear=np.asarray(row.get('matrix3',[[co,-si,0],[si,co,0],[0,0,1]]),float)@np.diag(row['scale'])
        require(np.isfinite(linear).all() and np.linalg.det(linear)>1e-8,'Degenerate or reflected semantic transform')
        V+=W[:,i,None]*((rest-center)@linear.T+moved-rest)
    ids=[r['id'] for r in config['controls']];owners=[];panels=[]
    for face,panel in zip(F,patch):
        influence=W[face].mean(axis=0)
        # The underside remains explicitly inspectable as one semantic belly.
        owner=5 if influence[5]>.28 else int(np.argmax(influence[:5]))
        owners.append(ids[owner]);panels.append(ids[owner]+':'+str(panel))
    proof=topology(V,F,config['tolerances'])
    require(set(owners)==set(ids),'Missing semantic face region')
    return dict(vertices=V,faces=F,owners=owners,panels=panels,proof=proof,
        weights=W,rest_vertices=rest,station_indices=stations,sector_indices=sectors,
        audit=dict(construction='single authored envelope',ring_count=16,ring_vertices=12,tip_count=2,
          independent_closed_cage_count=0,union_operations=0,clipping_operations=0,remesh_operations=0,
          random_numbers_used=0,semantic_control_count=6,authored_patch_count=len(set(patch))),
        exposed_polygon_count=len(set(patch)),fingerprint=fingerprint(V,F))

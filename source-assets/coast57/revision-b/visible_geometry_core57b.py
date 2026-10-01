"""Exact above-terrain rendered triangle area, not an invented solid-volume claim."""
from foot_geometry57b import *
model_triangles={}
for g in geometry['groups']:
    model_triangles[g['node']]=np.concatenate([np.array(s['vertices'],np.float32).astype(float)[np.array(s['indices'],int).reshape(-1,3)] for s in g['surfaces']])

def clip3(poly,n,c):
    out=[]
    for p,q in zip(poly,np.roll(poly,-1,axis=0)):
        a=float(p@n+c);b=float(q@n+c);pa=a>=-1e-8;pb=b>=-1e-8
        if pa:out.append(p)
        if pa!=pb:out.append(p+(q-p)*(a/(a-b)))
    return np.array(out)

def area3(poly):
    if len(poly)<3:return 0.
    return float(sum(np.linalg.norm(np.cross(poly[i]-poly[0],poly[i+1]-poly[0]))/2 for i in range(1,len(poly)-1)))

def measure(r,buf,terrain):
    model=model_triangles[r['node']];tri=actual_world(buf,r['source_group_origin'],model.reshape(-1,3)).reshape(-1,3,3)
    total=sum(area3(t) for t in tri);visible=0.;unclipped=0.;ymin=math.inf;ymax=-math.inf;pieces=0
    for t in tri:
        lo=t[:,[0,2]].min(0);hi=t[:,[0,2]].max(0)
        possible=np.flatnonzero(np.all(terrain['min']<=hi+1e-7,1)&np.all(terrain['max']>=lo-1e-7,1))
        for i in possible:
            t2=terrain['xz'][i];sign=np.sign(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(t2,np.roll(t2,-1,axis=0))))
            poly=t.copy()
            for a,b in zip(t2,np.roll(t2,-1,axis=0)):
                edge=b-a;n=np.array([-edge[1],0,edge[0]])*sign;c=(edge[1]*a[0]-edge[0]*a[1])*sign
                poly=clip3(poly,n,c)
                if len(poly)<3:break
            if len(poly)<3:continue
            unclipped+=area3(poly)
            ground=terrain['planes'][i];poly=clip3(poly,np.array([-ground[0],1,-ground[1]]),-ground[2])
            ar=area3(poly)
            if ar<1e-10:continue
            visible+=ar;pieces+=1;ymin=min(ymin,float(poly[:,1].min()));ymax=max(ymax,float(poly[:,1].max()))
    assert abs(unclipped-total)<max(.001,total*.00001),('Full rendered mesh coverage',r['node'],r['index'],total,unclipped)
    b=np.array(buf,np.float32);g=np.array(r['source_group_origin'],np.float32);root=(b[[3,7,11]]+g).astype(np.float32);gh,_=height(terrain,float(root[0]),float(root[2]))
    return {'total_native_mesh_area_m2':total,'area_above_terrain_m2':visible,'area_above_terrain_fraction':visible/total,'above_ground_world_y_range':[ymin,ymax],'top_above_terrain_at_root_m':ymax-gh,'above_ground_pieces':pieces}


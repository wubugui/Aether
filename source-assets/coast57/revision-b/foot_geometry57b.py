"""Seat real native foot surfaces; retain basis, minimize bounded XZ moves.
Every foot-polygon/terrain-triangle intersection vertex is checked. No engine.
"""
from pathlib import Path
import json,numpy as np,hashlib,math
D=Path(__file__).resolve().parent
source=json.loads((D/'native-authority/authority.json').read_text())
candidate=json.loads((D/'candidate-native.json').read_text())
rows=json.loads((D/'scatter-replacements.json').read_text())
geometry=json.loads((D/'diagnostics-foot57b/prop-foot-geometry.json').read_text())
origin=np.array(source['origin'],float);index=np.array(source['surfaces'][0]['arrays'][12],int).reshape(-1,3)
terrains=[np.array(p,np.float32).astype(float)[index]+origin for p in [source['surfaces'][0]['arrays'][0],candidate['surface_arrays'][0]]]
box=np.array([-3440.,-3090.,-3816.,-3430.]);EPS=.001;SEAT_PAD=.002

def plane(vertices):
    for i in range(1,len(vertices)-1):
        m=np.column_stack([vertices[[0,i,i+1],0],vertices[[0,i,i+1],2],np.ones(3)])
        if abs(np.linalg.det(m))>1e-9:return np.linalg.solve(m,vertices[[0,i,i+1],1])
    return None

terrain_data=[]
for t in terrains:
    coeff=np.array([plane(v) for v in t]);xz=t[:,:,[0,2]]
    terrain_data.append({'tri':t,'xz':xz,'min':xz.min(1),'max':xz.max(1),'planes':coeff})

def height(terrain,x,z):
    query=np.array([x,z]);possible=np.flatnonzero(np.all(terrain['min']<=query+1e-7,1)&np.all(terrain['max']>=query-1e-7,1))
    for i in possible:
        tri=terrain['xz'][i];v=tri[1]-tri[0];w=tri[2]-tri[0];q=query-tri[0]
        den=v[0]*w[1]-v[1]*w[0];u=(q[0]*w[1]-q[1]*w[0])/den;vv=(v[0]*q[1]-v[1]*q[0])/den
        if u>=-1e-7 and vv>=-1e-7 and u+vv<=1+1e-7:
            pp=terrain['planes'][i];return float(pp@[x,z,1]),int(i)
    return None

def clip2(poly,clip):
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(clip,np.roll(clip,-1,axis=0)))
    sign=1 if area>0 else -1
    out=list(poly)
    for a,b in zip(clip,np.roll(clip,-1,axis=0)):
        if not out:break
        edge=b-a
        signed=lambda p:sign*(edge[0]*(p[1]-a[1])-edge[1]*(p[0]-a[0]))
        old=out;out=[]
        for p,q in zip(old,old[1:]+old[:1]):
            dp,dq=signed(p),signed(q);pin=dp>=-1e-8;qin=dq>=-1e-8
            if pin:out.append(p)
            if pin!=qin:out.append(p+(q-p)*(dp/(dp-dq)))
    return np.array(out)

def clip_root(triangle):
    out=[]
    for p,q in zip(triangle,np.roll(triangle,-1,axis=0)):
        if p[1]<=0:out.append(p)
        if (p[1]<=0)!=(q[1]<=0):out.append(p+(q-p)*(-p[1]/(q[1]-p[1])))
    return np.array(out)

models={}
for g in geometry['groups']:
    vv=np.concatenate([np.array(s['vertices'],np.float32).astype(float) for s in g['surfaces']])
    kind='rock' if '/rock_' in g['node'] else ('bush' if '/bush_' in g['node'] else 'pine')
    polys=[]
    if kind=='pine':
        ring=np.unique(vv[vv[:,1]==vv[:,1].min()],axis=0);assert len(ring)==6 and ring[0,1]==0
        angle=np.arctan2(ring[:,2],ring[:,0]);polys=[ring[np.argsort(angle)]]
        first_segment=float(np.min(vv[vv[:,1]>0,1]))
    else:
        first_segment=None
        for s in g['surfaces']:
            v=np.array(s['vertices'],np.float32).astype(float);f=np.array(s['indices'],int).reshape(-1,3)
            for t in v[f]:
                poly=clip_root(t)
                if len(poly)>=3 and plane(poly) is not None:polys.append(poly)
    models[g['node']]={'kind':kind,'polys':polys,'vertices':vv,'first_segment':first_segment,'max_y':float(vv[:,1].max()),'height':float(np.ptp(vv[:,1]))}

def actual_world(buf,grouporigin,vertices):
    b=np.array(buf,np.float32).reshape(3,4).astype(float)
    return vertices@b[:,:3].T+b[:,3]+np.array(grouporigin,float)

def feet(row,buf,terrain):
    model=models[row['node']];worst_gap=-math.inf;worst_pen=math.inf;gap_point=None;pen_point=None;pieces=0;vertices_checked=0
    for pi,poly in enumerate(model['polys']):
        world=actual_world(buf,row['source_group_origin'],poly);pp=plane(world)
        assert pp is not None
        xz=world[:,[0,2]];lo=xz.min(0);hi=xz.max(0)
        possible=np.flatnonzero(np.all(terrain['min']<=hi+1e-7,1)&np.all(terrain['max']>=lo-1e-7,1))
        covered_area=0.
        for i in possible:
            overlap=clip2(xz,terrain['xz'][i])
            if len(overlap)<3:continue
            area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(overlap,np.roll(overlap,-1,axis=0))))/2
            if area<1e-9:continue
            covered_area+=area;pieces+=1;vertices_checked+=len(overlap)
            coords=np.column_stack([overlap[:,0],overlap[:,1],np.ones(len(overlap))]);foot_y=coords@pp;ground_y=coords@terrain['planes'][i];gaps=foot_y-ground_y
            for k in range(len(overlap)):
                gap=float(gaps[k]);point={'foot_polygon':pi,'terrain_triangle':int(i),'world':[float(overlap[k,0]),float(foot_y[k]),float(overlap[k,1])],'terrain_y':float(ground_y[k]),'surface_minus_terrain_y':gap}
                if gap>worst_gap:worst_gap=gap;gap_point=point
                if gap<worst_pen:worst_pen=gap;pen_point=point
        foot_area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xz,np.roll(xz,-1,axis=0))))/2
        assert abs(covered_area-foot_area)<max(.00001,foot_area*.00001),('Footprint terrain coverage',row['node'],row['index'],covered_area,foot_area)
    return {'max_air_gap_m':max(0,worst_gap),'max_penetration_m':max(0,-worst_pen),'signed_max_gap':worst_gap,'worst_air_gap':gap_point,'worst_penetration':pen_point,'intersection_pieces':pieces,'intersection_vertices_checked':vertices_checked,'continuous_piecewise_planar_foot_coverage':True}


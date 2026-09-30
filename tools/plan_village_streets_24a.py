from pathlib import Path
import json,math,heapq,hashlib
import numpy as np
from shapely.geometry import Polygon,Point,LineString
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
survey_path=root/'captures/validation_runs/village-grid-24a-20260908T122557Z-901d701fb6c6490989941a6f2e047718/survey/grid.json'
survey=json.loads(survey_path.read_text(encoding='utf-8'))
layout=json.loads((root/'captures/headland_study_23g/layout.json').read_text())
render=json.loads((root/'captures/validation_runs/headland-assembly-23g-20260908T121755Z-4ca247af11bb4af2a7bba06fe2383718/images/night-reference.png.json').read_text())
out=root/'captures/village_street_layout_24a';assert not out.exists();out.mkdir()
def world(h,u,v):
    x,_,z=h['position'];c,s=math.cos(h['yaw']),math.sin(h['yaw']);return (x+c*u+s*v,z-s*u+c*v)
house_data=[]
for h in layout['houses']:
    name=h['asset'];wx,wz,door,doorwidth=(3.9,5.4,6.4,2.) if name=='keeper_house' else ((3.26,4.1,4.95,1.7) if name=='fisher_cottage' else (4.4,3.4,4.25,3.0))
    shape=Polygon([world(h,u,v) for u,v in [(-wx,-wz),(wx,-wz),(wx,wz),(-wx,wz)]])
    endpoint=world(h,0,door);lead=world(h,0,door+2.)
    house_data.append({**h,'obstacle':shape,'entry':endpoint,'lead':lead,'entry_y':h['position'][1]+.18,'entry_width':doorwidth})
trees=[Point(t['position'][0],t['position'][2]).buffer(1.7) for t in render['headland_study']['trees']]
groups=[];fig,axes=plt.subplots(1,2,figsize=(16,10))
for grid,ax in zip(survey['grids'],axes):
    name=grid['name'];x0,x1,z0,z1=grid['bounds'];heights={(p['position'][0],p['position'][2]):p['position'][1] for p in grid['samples']}
    houses=[h for h in house_data if h['name'].startswith('fore_' if name=='foreground' else 'bay_')]
    hub=(-2254.,-1751.) if name=='foreground' else (-2238.,-1878.)
    obstacles=[h['obstacle'].buffer(.94) for h in houses]+trees
    valid={}
    for key,y in heights.items():
        if y is None or y<2.:continue
        if any(p.contains(Point(key)) for p in obstacles):continue
        # Planning corridor clearance only; exact full width is surveyed after smoothing.
        neighbors=[heights.get((key[0]+dx,key[1]+dz)) for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]]
        if any(v is None for v in neighbors):continue
        cross=max(neighbors)-min(neighbors)
        if cross>1.4:continue
        valid[key]=y
    hub_point=min(valid,key=lambda p:math.dist(p,hub));hub=tuple(float(v) for v in hub_point)
    goals={p for p in valid if math.dist(p,hub)<=2.35}
    assert goals,(name,'no courtyard')
    routes=[]
    for h in houses:
        start=min(valid,key=lambda p:math.dist(p,h['lead']))
        if math.dist(start,h['lead'])>3.5:routes.append({'house':h['name'],'failure':'No safe grid point near front lead','lead':h['lead'],'nearest':start});continue
        q=[(0,start)];best={start:0.};came={};end=None
        while q:
            cost,p=heapq.heappop(q)
            if cost>best[p]+1e-9:continue
            if p in goals:end=p;break
            for dx,dz in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                neighbor=(p[0]+dx,p[1]+dz)
                if neighbor not in valid:continue
                length=math.hypot(dx,dz);delta=valid[neighbor]-valid[p];slope=abs(delta)/length
                if slope>.52:continue
                if dx and dz and ((p[0]+dx,p[1]) not in valid or (p[0],p[1]+dz) not in valid):continue
                value=cost+length*(1+9*slope*slope)
                if value<best.get(neighbor,float('inf')):
                    best[neighbor]=value;came[neighbor]=p;heapq.heappush(q,(value,neighbor))
        if end is None:routes.append({'house':h['name'],'failure':'No path within gradient/obstacle limits','start':start});continue
        chain=[end]
        while chain[-1]!=start:chain.append(came[chain[-1]])
        chain.reverse()
        # Reduce only collinear grid runs; retain corners for explicit curve fitting later.
        reduced=[chain[0]]
        for a,b,c in zip(chain,chain[1:],chain[2:]):
            if (b[0]-a[0],b[1]-a[1])!=(c[0]-b[0],c[1]-b[1]):reduced.append(b)
        reduced.append(chain[-1])
        pts=[h['entry'],h['lead']]+reduced
        length=sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
        routes.append({'house':h['name'],'entry':[h['entry'][0],h['entry_y'],h['entry'][1]],'entry_width':h['entry_width'],'lead':list(h['lead']),'grid_path':chain,'control_points':pts,'length_m':length,'end_ground_y':valid[end],'planning_cost':best[end]})
    array=np.array([[heights[(x,z)] if heights[(x,z)] is not None else np.nan for x in range(x0,x1+1)] for z in range(z0,z1+1)])
    ax.imshow(array,extent=[x0-.5,x1+.5,z1+.5,z0-.5],cmap='terrain',vmin=0,vmax=45)
    for h in houses:
        x,z=h['obstacle'].exterior.xy;ax.fill(x,z,color='#b7b7b7',edgecolor='#222222',lw=1)
        ax.plot(*h['entry'],'ko',ms=3);ax.text(h['position'][0],h['position'][2],h['name'],fontsize=7,color='black',ha='center')
    for t in render['headland_study']['trees']:ax.plot(t['position'][0],t['position'][2],'^',color='#154426',ms=5)
    for route in routes:
        if 'failure' in route:continue
        pts=np.array(route['control_points']);ax.plot(pts[:,0],pts[:,1],lw=2,label=route['house'])
    ax.add_patch(plt.Circle(hub,2.35,fill=False,edgecolor='magenta',linewidth=2));ax.set_xlim(x0,x1);ax.set_ylim(z1,z0);ax.set_aspect('equal');ax.set_title(name+' measured ground and proposed streets');ax.legend(fontsize=7)
    groups.append({'name':name,'hub':list(hub),'hub_radius_m':2.35,'hub_ground_y':valid[hub_point],'routes':routes,'scope':'1m native collision planning only. Corner curves, full width and shared path overlaps must be resolved before Blender geometry.'})
fig.tight_layout();fig.savefig(out/'layout.png',dpi=115);plt.close(fig)
data={'source_run':survey['run_id'],'headland_glb_sha256':survey['headland_glb_sha256'],'houses':[{k:v for k,v in h.items() if k!='obstacle'} for h in house_data],'groups':groups}
(out/'layout.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps([{'group':g['name'],'hub':g['hub'],'routes':[{k:r[k] for k in ['house','length_m','failure'] if k in r} for r in g['routes']]} for g in groups]))

"""Compare actual native trunk-bottom/rock-lower-surface samples to native terrain.
Read-only relative to all world/source resources; writes evidence JSON only.
"""
from pathlib import Path
import json,numpy as np,hashlib,collections
D=Path(__file__).resolve().parent
SRC=D.parent
geom=json.loads((D/'prop-foot-geometry.json').read_text())
orig=json.loads((SRC/'native-authority/authority.json').read_text())
cand=json.loads((SRC/'candidate-native.json').read_text())
scatter=json.loads((SRC/'scatter-replacements.json').read_text())
origin=np.array(orig['origin'],float)
idx=np.array(orig['surfaces'][0]['arrays'][12],int).reshape(-1,3)
terrain=[np.array(a,float)[idx]+origin for a in [orig['surfaces'][0]['arrays'][0],cand['surface_arrays'][0]]]
def sample_height(t,x,z):
    a,b,c=t[:,0],t[:,1],t[:,2]
    den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2]);ok=abs(den)>1e-9
    u=np.divide((b[:,2]-c[:,2])*(x-c[:,0])+(c[:,0]-b[:,0])*(z-c[:,2]),den,out=np.zeros(len(t)),where=ok)
    v=np.divide((c[:,2]-a[:,2])*(x-c[:,0])+(a[:,0]-c[:,0])*(z-c[:,2]),den,out=np.zeros(len(t)),where=ok)
    w=1-u-v;ok&=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)
    ids=np.flatnonzero(ok);assert len(ids),(x,z)
    yy=u*a[:,1]+v*b[:,1]+w*c[:,1];i=ids[np.argmax(yy[ids])]
    return float(yy[i]),int(i)
def clip_below_root(triangle):
    result=[]
    for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
        inside_a=a[1]<=0;inside_b=b[1]<=0
        if inside_a:result.append(a)
        if inside_a!=inside_b:
            result.append(a+(b-a)*(-a[1]/(b[1]-a[1])))
    return result
local_samples={}
geometry_evidence=[]
for g in geom['groups']:
    vertices=np.concatenate([np.array(s['vertices'],float) for s in g['surfaces']])
    kind='rock' if 'rock_' in g['node'] else 'pine'
    if kind=='pine':
        bottom=np.unique(vertices[vertices[:,1]==vertices[:,1].min()],axis=0)
        assert vertices[:,1].min()==0 and len(bottom)==6
        center=bottom.mean(0);angle=np.arctan2(bottom[:,2]-center[2],bottom[:,0]-center[0]);bottom=bottom[np.argsort(angle)]
        samples=np.concatenate([bottom,(bottom+np.roll(bottom,-1,axis=0))/2,center[None,:]])
        method='All six actual minimum-Y trunk-ring vertices, six edge midpoints and root-ring center; no crown footprint'
    else:
        points=[]
        for s in g['surfaces']:
            v=np.array(s['vertices'],float);f=np.array(s['indices'],int).reshape(-1,3)
            for tri in v[f]:
                poly=clip_below_root(tri)
                if len(poly)<3:continue
                poly=np.array(poly);points.extend(poly)
                points.extend((poly+np.roll(poly,-1,axis=0))/2)
                for i in range(1,len(poly)-1):points.append((poly[0]+poly[i]+poly[i+1])/3)
        samples=np.unique(np.round(np.array(points),10),axis=0)
        method='Actual rock surface triangles clipped at original local root plane Y=0; original low vertices, exact edge crossings, edge midpoints and clipped-face centroids'
    local_samples[g['node']]=samples
    geometry_evidence.append({'node':g['node'],'mesh':g['mesh'],'kind':kind,'local_bounds':[vertices.min(0).tolist(),vertices.max(0).tolist()],'method':method,'sample_count':len(samples),'local_samples':samples.tolist()})
rows=[]
for r in scatter:
    samples=local_samples[r['node']]
    measurements=[]
    for phase,field,t in [('original','before_buffer',terrain[0]),('candidate','candidate_buffer',terrain[1])]:
        buf=np.array(r[field],np.float32).reshape(3,4);grouporigin=np.array(r['source_group_origin'],np.float32)
        world=(samples.astype(np.float32)@buf[:,:3].T+buf[:,3]+grouporigin).astype(np.float32)
        hits=[]
        for i,p in enumerate(world):
            y,tri=sample_height(t,float(p[0]),float(p[2]));hits.append({'sample':i,'world':p.tolist(),'terrain_y':y,'terrain_triangle':tri,'surface_minus_terrain_y':float(p[1])-y})
        gaps=np.array([h['surface_minus_terrain_y'] for h in hits])
        measurements.append({'phase':phase,'max_air_gap_m':float(max(0,gaps.max())),'max_penetration_m':float(max(0,-gaps.min())),'air_gap_samples_over_0_1m':int((gaps>.1).sum()),'penetration_samples_over_0_1m':int((gaps<-.1).sum()),'most_air_gap':hits[int(np.argmax(gaps))],'most_penetration':hits[int(np.argmin(gaps))],'samples':hits})
    before,after=measurements
    rows.append({'node':r['node'],'index':r['index'],'kind':r['kind'],'root_height_adjusted':r['before_buffer'][7]!=r['candidate_buffer'][7],'original_slope_degrees':r['before_support']['slope_degrees'],'candidate_slope_degrees':r['candidate_support']['slope_degrees'],'original':before,'candidate':after,'air_gap_increase_m':after['max_air_gap_m']-before['max_air_gap_m'],'penetration_increase_m':after['max_penetration_m']-before['max_penetration_m']})
def summary(items):
    return {'count':len(items),'root_Y_adjusted':sum(r['root_height_adjusted'] for r in items),'candidate_air_gap_over_0_1m':sum(r['candidate']['max_air_gap_m']>.1 for r in items),'candidate_air_gap_over_0_25m':sum(r['candidate']['max_air_gap_m']>.25 for r in items),'air_gap_increase_over_0_1m':sum(r['air_gap_increase_m']>.1 for r in items),'penetration_increase_over_0_1m':sum(r['penetration_increase_m']>.1 for r in items),'max_candidate_air_gap_m':max(r['candidate']['max_air_gap_m'] for r in items),'max_candidate_penetration_m':max(r['candidate']['max_penetration_m'] for r in items)}
report={'mode':'Actual native local mesh foot samples transformed by exact saved/candidate buffers, evaluated against actual original/candidate native indexed terrain triangles; no new renderer or runtime test','candidate_status':'Draft A rejected; exact root-point gates do not establish base support','input_hashes':{p:hashlib.sha256(((D if p=='prop-foot-geometry.json' else SRC)/p).read_bytes()).hexdigest() for p in ['prop-foot-geometry.json','candidate-native.json','scatter-replacements.json']},'method_limits':'0.1/0.25m thresholds summarize evidence; they are not replacement acceptance tolerances. Discrete foot samples identify actual gaps/penetrations but do not prove complete continuous contact or rigid-body stability. Positive means air under an actual foot surface; negative means burial. Rock lower body is intentionally embedded in the original, so compare against original as well as absolute depths.','summary':summary(rows),'by_kind':{kind:summary([r for r in rows if r['kind']==kind]) for kind in ['pine','rock']},'geometry':geometry_evidence,'placements':rows}
(D/'actual-foot-support57.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['candidate_status','summary','by_kind']},indent=2))
for r in sorted(rows,key=lambda r:r['air_gap_increase_m'],reverse=True)[:8]:print(r['node'],r['index'],'air before/after',r['original']['max_air_gap_m'],r['candidate']['max_air_gap_m'],'burial before/after',r['original']['max_penetration_m'],r['candidate']['max_penetration_m'])

"""Independent CPU comparison of actual saved before/after GLBs; no generator fallback."""
import ast,collections,csv,hashlib,json
from pathlib import Path
import numpy as np
R=Path('D:/test6')
source=ast.parse((R/'tools/verify_geology_assets.py').read_text())
ns={}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.FunctionDef) and n.name=='triangles'],type_ignores=[]),'<read-only GLB reader>','exec'),ns)
triangles=ns['triangles']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def topology(t):return collections.Counter(tuple(sorted(tuple(np.round(v[[0,2]],5)) for v in tri)) for tri in t)
def points(t):
    p=np.unique(t.reshape(-1,3),axis=0)
    return p[np.lexsort((p[:,2],p[:,0]))]
class MeshHeight:
    def __init__(self,t):
        self.t=t;self.buckets={}
        aa=np.floor(t[:,:,[0,2]].min(1)/24).astype(int);bb=np.floor(t[:,:,[0,2]].max(1)/24).astype(int)
        for i,(low,high) in enumerate(zip(aa,bb)):
            for x in range(low[0],high[0]+1):
                for z in range(low[1],high[1]+1):self.buckets.setdefault((x,z),[]).append(i)
    def height(self,p):
        bins=np.floor(p[:,[0,2]]/24).astype(int);out=np.full(len(p),np.nan)
        for cell in np.unique(bins,axis=0):
            ii=np.flatnonzero(np.all(bins==cell,axis=1));ids=self.buckets.get(tuple(cell),[])
            if not ids:continue
            t=self.t[ids];a,b,c=t[:,0],t[:,1],t[:,2];x=p[ii,0,None];z=p[ii,2,None]
            den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2])
            wa=((b[:,2]-c[:,2])*(x-c[:,0])+(c[:,0]-b[:,0])*(z-c[:,2]))/den
            wb=((c[:,2]-a[:,2])*(x-c[:,0])+(a[:,0]-c[:,0])*(z-c[:,2]))/den
            wc=1-wa-wb;mask=(wa>=-1e-6)&(wb>=-1e-6)&(wc>=-1e-6)
            good=mask.any(1);pick=mask.argmax(1);jj=np.arange(len(ii))
            out[ii[good]]=(wa[jj,pick]*a[pick,1]+wb[jj,pick]*b[pick,1]+wc[jj,pick]*c[pick,1])[good]
        return out
records=[];pair_mesh={};hashes={};changed_faces=[]
for name,origin in [('Ground_-1_-1',np.array([-768,0,-768])),('Ground_-1_0',np.array([-768,0,0]))]:
    old_path=R/'captures/round-10l-neighbor-integration/before/assets/terrain'/f'{name}.glb'
    new_path=R/'assets/terrain'/f'{name}.glb'
    old=triangles(old_path)[1]+origin;new=triangles(new_path)[1]+origin
    hashes[str(old_path.relative_to(R))]=sha(old_path);hashes[str(new_path.relative_to(R))]=sha(new_path)
    a,b=points(old),points(new)
    assert a.shape==b.shape and np.max(abs(a[:,[0,2]]-b[:,[0,2]]))<1e-5
    delta=b[:,1]-a[:,1];mask=abs(delta)>.001
    old_y={tuple(np.round(p[[0,2]],5)):p[1] for p in a}
    face_delta=np.array([[v[1]-old_y[tuple(np.round(v[[0,2]],5))] for v in tri] for tri in new])
    changed=np.flatnonzero(np.any(abs(face_delta)>.001,axis=1))
    for i in changed:changed_faces.append({'tile':name,'triangle':int(i),'xz':new[i][:,[0,2]].tolist(),'vertex_delta_y':face_delta[i].tolist()})
    records.append({'name':name,'vertices':len(a),'changed_vertices_above_1mm':int(mask.sum()),'max_vertex_delta_metres':float(abs(delta).max()),'changed_vertex_bounds':b[mask].min(0).tolist()+b[mask].max(0).tolist(),'topology_xz_unchanged':topology(old)==topology(new),'affected_triangles':len(changed),'affected_triangle_bounds':new[changed].min((0,1)).tolist()+new[changed].max((0,1)).tolist()})
    pair_mesh[name]=(MeshHeight(old),MeshHeight(new))
road_path=R/'assets/land_details/Trail_Crownreach.glb';road=triangles(road_path)[1];hashes[str(road_path.relative_to(R))]=sha(road_path)
a,b,c=road[:,0],road[:,1],road[:,2]
sample=np.stack([(a+b+c)/3,a*.6+b*.2+c*.2,a*.2+b*.6+c*.2,a*.2+b*.2+c*.6,(a+b)*.5,(b+c)*.5,(c+a)*.5],axis=1).reshape(-1,3)
selected=np.flatnonzero((sample[:,0]<0)&(sample[:,0]>=-768)&(sample[:,2]>=0)&(sample[:,2]<=768));p=sample[selected]
old_ground=pair_mesh['Ground_-1_0'][0].height(p);new_ground=pair_mesh['Ground_-1_0'][1].height(p)
old_error=p[:,1]-old_ground-.1;new_error=p[:,1]-new_ground-.1
bad=abs(old_error)>.08
road_result={'sample_count':len(p),'misses_old':int(np.isnan(old_ground).sum()),'misses_new':int(np.isnan(new_ground).sum()),'old_failed_samples':int(bad.sum()),'new_failed_samples':int((abs(new_error)>.08).sum()),'old_max_error_metres':float(np.nanmax(abs(old_error))),'new_max_error_metres':float(np.nanmax(abs(new_error))),'old_failed_bounds':p[bad].min(0).tolist()+p[bad].max(0).tolist()}
with (R/'reviews/round-10l-neighbor-road-samples.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['triangle','sample','x','road_y','z','old_ground_y','new_ground_y','old_road_error_m','new_road_error_m'])
    for j in np.flatnonzero(bad):w.writerow([int(selected[j]//7),int(selected[j]%7),*p[j],old_ground[j],new_ground[j],old_error[j],new_error[j]])
report={'scope':'Independent actual before/after GLB vertex and XZ triangle comparison; seven actual Crownreach triangle interior/edge samples within Ground_-1_0 against each explicit loaded mesh, no generator or floor-based tile fallback. Not a GPU/full-world test.','terrain':records,'crownreach_west_positive_z':road_result,'affected_triangles':changed_faces,'input_sha256':hashes}
(R/'reviews/round-10l-neighbor-geometry-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'terrain':records,'road':road_result,'hashes':hashes},indent=2))

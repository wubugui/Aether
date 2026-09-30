"""Independent read-only 23g GLB/sidecar audit; writes review JSON only."""
from pathlib import Path
import json,struct,hashlib,math,numpy as np
from shapely.geometry import Polygon
from collections import Counter
ROOT=Path('E:/FeiTing'); sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def glb(path):
 raw=path.read_bytes();ln=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+ln]);buf=raw[28+ln:]
 def ac(i):
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];typ={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'SCALAR':1}[a['type']];sz=np.dtype(typ).itemsize
  return np.ndarray((a['count'],n),dtype=typ,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*sz),sz)).copy()
 ps=[];fs=[];off=0
 for no in d['nodes']:
  assert not any(k in no for k in ['matrix','translation','rotation','scale'])
  if 'mesh' not in no:continue
  for pr in d['meshes'][no['mesh']]['primitives']:
   p=ac(pr['attributes']['POSITION']);ps.append(p);fs.append(ac(pr['indices']).reshape(-1,3)+off);off+=len(p)
 p=np.concatenate(ps).astype(float);f=np.concatenate(fs);u,iv=np.unique(p,axis=0,return_inverse=True);return u,iv[f]
def components(p,f):
 parent=list(range(len(p)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for t in f:
  for a,b in zip(t,t[1:]):parent[find(int(a))]=find(int(b))
 groups={}
 for i in range(len(p)):groups.setdefault(find(i),[]).append(i)
 return sorted(groups.values(),key=len,reverse=True)
def comp_signature(p,f,group):
 ids=set(group);v=p[group];faces=[sorted([tuple(p[i]) for i in t]) for t in f if int(t[0]) in ids];return str(sorted(map(tuple,faces)))
b=ROOT/'captures/headland_study_23g';e=ROOT/'captures/headland_study_23e';run=ROOT/'captures/validation_runs/headland-assembly-23g-20260908T121755Z-4ca247af11bb4af2a7bba06fe2383718';l=json.loads((b/'layout.json').read_text());td=json.loads((b/'terrain-design.json').read_text());p,f=glb(b/'mainland_headland.glb');ep,ef=glb(e/'mainland_headland.glb');groups=components(p,f);egroups=components(ep,ef);rocks_same=Counter(comp_signature(p,f,g) for g in groups[1:])==Counter(comp_signature(ep,ef,g) for g in egroups[1:]);world=p+l['origin'];target=np.array(l['vertices']);target[:,1]=td['heights'];dist=np.linalg.norm(target[:,None,:]-world[None,:,:],axis=2);ids=dist.argmin(1);lookup={int(v):i for i,v in enumerate(ids)};actualtop=[t for t in f if all(int(i) in lookup for i in t)];topsame=Counter(tuple(sorted(lookup[int(i)] for i in t)) for t in actualtop)==Counter(tuple(sorted(t)) for t in l['triangles']);topverts=world[ids]
# Independent distance to seam, not trusting comparison's selected count.
def segment(q,a,b):
 a=np.array(a);b=np.array(b);d=b-a;t=np.clip(np.dot(q-a,d)/np.dot(d,d),0,1);return np.linalg.norm(q-a-t*d)
bd=l['boundary'];seams=[(a['position'],c['position']) for a,c in zip(bd,bd[1:]+bd[:1]) if a['height'] is None or c['height'] is None];shore=[]
for i,v in enumerate(bd):
 if v['height'] is None:continue
 j=np.linalg.norm(target[:,[0,2]]-v['position'],axis=1).argmin();seam=min(segment(np.array(v['position']),a,c) for a,c in seams);expected=max(td['original_ground'][j]+.05,v['height']);shore.append({'index':i,'xz':v['position'],'actual_y':float(world[ids[j],1]),'seam_distance':float(seam),'expected_nontransition_y':expected,'enforced':bool(seam>=24),'error_if_enforced':float(abs(world[ids[j],1]-expected)) if seam>=24 else None})
# Exact polygon clipping against actual top triangles covers the entire pad, not only center or 9 probes.
pads=[]
for h in l['houses']:
 c,s=math.cos(h['yaw']),math.sin(h['yaw']);wx,wz=h['pad_half_size'];x,hy,z=h['position'];poly=Polygon([(x+c*u+s*v,z-s*u+c*v) for u,v in [(-wx,-wz),(wx,-wz),(wx,wz),(-wx,wz)]]);area=0;err=0
 for t in actualtop:
  v=world[t];tp=Polygon(v[:,[0,2]]);cut=tp.intersection(poly)
  if cut.area<1e-10:continue
  area+=cut.area;co=np.linalg.solve(np.column_stack([v[:,0],v[:,2],np.ones(3)]),v[:,1]);pieces=list(cut.geoms) if hasattr(cut,'geoms') else [cut]
  for piece in pieces:
   if not hasattr(piece,'exterior'):continue
   err=max(err,max(abs(co[0]*xx+co[1]*zz+co[2]-hy) for xx,zz in piece.exterior.coords))
 pads.append({'name':h['name'],'pad_area_m2':poly.area,'covered_area_m2':area,'maximum_height_error_m':err})
houses=[]
for name in ['fisher_cottage','quay_workshop']:
 vp,vf=glb(b/(name+'.glb'));ev,eft=glb(e/(name+'.glb'));houses.append({'name':name,'glb_sha_same':sha(b/(name+'.glb'))==sha(e/(name+'.glb')),'source_sha_same':sha(b/(name+'.blend'))==sha(e/(name+'.blend')),'actual_geometry_equal':np.array_equal(vp,ev) and np.array_equal(vf,eft)})
m=json.loads((run/'manifest.json').read_text());bad=[r for r,k in m['artifacts'].items() if sha(run/r)!=k['sha256']];gate=json.loads((ROOT/'reviews/round-23g-headland-native-check.json').read_text());assets=[{'name':r['asset'],'source_sha':sha(b/(r['asset']+'.blend')),'glb_sha':sha(b/(r['asset']+'.glb')),'source_gate_match':sha(b/(r['asset']+'.blend'))==r['source_sha256'],'glb_gate_match':sha(b/(r['asset']+'.glb'))==r['glb_sha256']} for r in gate['assets']];views=[]
for n in ['night-reference','day-front','day-bay','day-back','day-seam']:
 d=json.loads((run/f'images/{n}.png.json').read_text());gaps=[v['gap_m'] for row in d['headland_study']['footings'] for v in row['samples']];views.append({'name':n,'sha':sha(run/f'images/{n}.png'),'same_run':d['run_id']==m['run_id'],'production_modified':d['production_modified'],'footing_count':len(gaps),'gap_range':[min(gaps),max(gaps)]})
out={'scope':'Actual GLB increment and full planar pad clipping, reuse unchanged 23e rock/house evidence; no engine rerun','run':str(run),'manifest_passed':m['passed'],'completed_utc':m['completed_utc'],'stage_count':len(m['stages']),'bindings':len(m['artifacts']),'binding_failures':bad,'assets':assets,'views':views,'actual_top_control_error_m':float(dist.min(1).max()),'top_connectivity_matches':topsame,'shore':shore,'nontransition_shore_count':sum(r['enforced'] for r in shore),'nontransition_max_error_m':max(r['error_if_enforced'] for r in shore if r['enforced']),'pads':pads,'eleven_rock_geometry_exactly_same':rocks_same,'house_comparison':houses,'full_art_accepted':False,'local_shore_fix_retain':True,'production_install_accepted':False}
(ROOT/'reviews/round-23g-headland-independent-audit.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:out[k] for k in ['manifest_passed','stage_count','bindings','binding_failures','actual_top_control_error_m','top_connectivity_matches','nontransition_shore_count','nontransition_max_error_m','pads','eleven_rock_geometry_exactly_same','house_comparison']},indent=2))

"""Onlyhub edits, exact before/after arrays, actual native-precision candidates."""
import hashlib,json,sys,types
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;C=P.parent;ROOT=P.parents[3]
helperpath=C.parent/'revision-b/recovery-03/triangle_pairs58b.py';helper=types.ModuleType('narrow');exec(compile(helperpath.read_bytes(),str(helperpath),'exec'),helper.__dict__)
sys.path.insert(0,str(P));from geometry58c import source_coordinate,world_coordinate
old=json.loads((C/'native-control-input58c.json').read_text())['controls'];new=json.loads((P/'native-control-input58c.json').read_text())['controls'];rows=[]
for a,b in zip(old,new):
 va=np.array(a['vertices']);vb=np.array(b['vertices']);f=np.array(b['faces']);changed=np.flatnonzero(np.any(va!=vb,axis=1)).tolist()
 assert a['faces']==b['faces'] and a['design']==b['design'] and changed==[len(va)-2,len(va)-1]
 assert np.array_equal(va.min(0),vb.min(0)) and np.array_equal(va.max(0),vb.max(0))
 # Same conversion as stored sourcefloat32, then actual worldcoordinate.
 native=np.array([world_coordinate(np.array(source_coordinate(v),dtype=np.float32)) for v in vb]);tri=native[f];lo=tri.min(1);hi=tri.max(1);results=[]
 for i in range(len(f)):
  candidates=np.flatnonzero(np.all(lo<=hi[i],axis=1)&np.all(hi>=lo[i],axis=1)&(np.arange(len(f))>i))
  for j in candidates:
   if set(f[i])&set(f[j]):continue
   r=helper.narrow_phase(tri[i],tri[j]);disjoint=r['classification'] in ['separated_by_triangle_plane','coplanar_disjoint','noncoplanar_disjoint']
   if not disjoint:results.append(dict(triangles=[int(i),int(j)],**r))
 rows.append(dict(id=a['id'],changed_vertex_ids=changed,old_hubs=va[changed].tolist(),new_hubs=vb[changed].tolist(),other_vertices_exact=bool(np.array_equal(va[:-2],vb[:-2])),faces_exact=True,world_bounds_exact=True,native_precision_nonadjacent_failures=results))
result=dict(passed=all(not r['native_precision_nonadjacent_failures'] for r in rows),controls=rows,source_checkpoint_preserved_sha256=hashlib.sha256((C/'cloud_bank58c_controls.blend').read_bytes()).hexdigest(),method='Only114 top/bottom hub XZ positions move to actualterminalring mean; allother2736 nativeauthoringvertices and5472 orientedtriangles unchanged. Bounds,centres,extents andvalleyrules exact. Actualsourcefloat32 precision then everynonadjacentAABBcandidate narrowphase; sharedvertices excluded.',visual_acceptance=False,blender_started=False)
(P/'hub-repair58c.json').write_text(json.dumps(result,indent=2)+'\n');print('Static precise hubrepair:',result['passed']);assert result['passed']

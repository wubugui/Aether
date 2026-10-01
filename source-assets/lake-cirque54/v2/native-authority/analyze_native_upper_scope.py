import json,collections,math
from pathlib import Path
R=Path('/workspace/scratch/a29d03198654/Aether');D=R/'source-assets/lake-cirque54/v2/native-authority';j=json.load(open(R/'source-assets/lake-cirque54/intake/land53-inventory.json'));src=json.load(open(D/'cirque-native-authority.json'))['faces'];regs=json.load(open(R/'source-assets/lake-rim53/revision-d/sculpt-report.json'))['buildings_protected']
verts=[];lookup={};faces=[]
for i in range(0,len(src),3):
 face=[]
 for p in src[i:i+3]:
  k=tuple(p)
  if k not in lookup:lookup[k]=len(verts);verts.append(p)
  face.append(lookup[k])
 faces.append(face)
cache={};segs=[];wet=[];dry=[];protected=[]
def edgezero(a,b):
 key=tuple(sorted([a,b]))
 if key not in cache:
  lo,hi=key;p,q=verts[lo],verts[hi];t=-p[1]/(q[1]-p[1]);v=[p[k]+t*(q[k]-p[k]) for k in range(3)];v[1]=0.;cache[key]=len(verts);verts.append(v)
 return cache[key]
def clip(face,wet_side):
 out=[]
 for a,b in zip(face,face[1:]+face[:1]):
  av,bv=verts[a][1],verts[b][1]
  if (av<=0 if wet_side else av>=0):out.append(a)
  if av*bv<0:out.append(edgezero(a,b))
 return list(dict.fromkeys(out))
def clip2d(poly,axis,value,ge):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]>=value if ge else a[axis]<=value;ib=b[axis]>=value if ge else b[axis]<=value
  if ia:out.append(a)
  if ia!=ib:
   t=(value-a[axis])/(b[axis]-a[axis]);out.append([a[k]+t*(b[k]-a[k]) for k in range(2)])
 return out
def area(poly):return .5*abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))) if poly else 0.
for fi,f in enumerate(faces):
 w=clip(f,True);d=clip(f,False)
 if len(w)>=3:wet.append({'original_triangle':fi,'polygon':w})
 if len(d)>=3:dry.append({'original_triangle':fi,'polygon':d})
 zz=[v for v in w if verts[v][1]==0]
 if len(zz)==2:segs.append(zz)
 hits=[]
 if len(d)>=3:
  for reg in regs:
   p=[[verts[v][0],verts[v][2]] for v in d]
   for ax,val,ge in [(0,reg['xmin'],True),(0,reg['xmax'],False),(1,reg['zmin'],True),(1,reg['zmax'],False)]:p=clip2d(p,ax,val,ge)
   if area(p)>1e-8:hits.append(reg['node'])
 if hits:protected.append({'original_triangle':fi,'whole_polygon_locked':d,'protected_regions':hits})
links=collections.defaultdict(list)
for a,b in segs:links[a].append(b);links[b].append(a)
loops=[];left=set(tuple(sorted(e)) for e in segs)
while left:
 a,b=next(iter(left));left.remove(tuple(sorted((a,b))));loop=[a,b]
 while loop[-1]!=loop[0]:
  choices=[q for q in links[loop[-1]] if tuple(sorted((loop[-1],q))) in left];assert len(choices)==1,(loop[-1],choices)
  q=choices[0];left.remove(tuple(sorted((loop[-1],q))));loop.append(q)
 loops.append(loop[:-1])
report={'authority_sha256':j['source_sha256'],'old_original_unique_vertices':len(lookup),'vertices_with_cached_y0_intersections':verts,'original_triangles':faces,'original_triangle_count':len(faces),'shared_edge_y0_intersection_count':len(cache),'edge_intersections':[{'old_edge':list(k),'new_vertex':v} for k,v in cache.items()],'wet_polygons':wet,'dry_polygons':dry,'waterline_segments':segs,'waterline_loops':loops,'protected_faces':protected,'method':'Clip every original saved triangle at exactY0 with one canonical interpolation per undirected original edge. Protect the whole original dry face when its exactXZ projection intersects a protected rectangle with positive area; no bounding-box-only false positives.'}
json.dump(report,open(D/'upper-remesh-intake.json','w'),indent=2)
print('old verts',len(lookup),'wet polygons',len(wet),'dry polygons',len(dry),'waterloops',[len(l) for l in loops],'locked faces',len(protected))
pp=[verts[i] for r in protected for i in r['whole_polygon_locked']];print('locked bounds',[[min(v[k] for v in pp) for k in range(3)],[max(v[k] for v in pp) for k in range(3)]])
print('dry negatives normals',sum(1 for r in dry if (lambda a,b,c:(c[2]-a[2])*(b[0]-a[0])-(c[0]-a[0])*(b[2]-a[2]))(*(verts[i] for i in r['polygon'][:3]))<0))

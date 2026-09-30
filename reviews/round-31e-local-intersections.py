from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'actualGLB_decoder','exec'))
from shapely.geometry import LineString
P=R/'captures/lantern_island_study_31e';new=glb(P/'island_c.glb');old=glb(R/'captures/lantern_island_study_31d/island_c.glb');key=next(k for k in new if 'olive grass' in k);ts=new[key];oldkeys=counter(old[key]);changed=np.array([tri_key(t) not in oldkeys for t in ts]);lo=ts.min(axis=1);hi=ts.max(axis=1);pairs=set()
for i in np.flatnonzero(changed):
 for j in np.flatnonzero(np.all(hi>=lo[i]-1e-7,axis=1)&np.all(lo<=hi[i]+1e-7,axis=1)):
  if i!=j:pairs.add(tuple(sorted((int(i),int(j)))))
def plane_normal(t):
 n=np.cross(t[1]-t[0],t[2]-t[0]);return n/np.linalg.norm(n)
def in_triangle(p,t):
 u=t[1]-t[0];v=t[2]-t[0];w=p-t[0];a=np.dot(u,u);b=np.dot(u,v);c=np.dot(v,v);d=np.dot(w,u);e=np.dot(w,v);den=a*c-b*b
 if den<1e-18:return False
 s=(d*c-e*b)/den;q=(e*a-d*b)/den;return s>=-1e-7 and q>=-1e-7 and s+q<=1+1e-7
def edge_hits(a,b):
 n=plane_normal(b);hits=[]
 for p,q in zip(a,np.roll(a,-1,axis=0)):
  dp=np.dot(p-b[0],n);dq=np.dot(q-b[0],n)
  if abs(dp)<1e-7 and in_triangle(p,b):hits.append(p)
  if abs(dq)<1e-7 and in_triangle(q,b):hits.append(q)
  if dp*dq<0 and abs(dp-dq)>1e-12:
   t=dp/(dp-dq);h=p+t*(q-p)
   if in_triangle(h,b):hits.append(h)
 return hits
def point_segment_distance(p,a,b):
 ab=b-a;d=np.dot(ab,ab)
 if d==0:return np.linalg.norm(p-a)
 return np.linalg.norm(p-(a+np.clip(np.dot(p-a,ab)/d,0,1)*ab))
issues=[];stats={'aabb_candidate_pairs':len(pairs),'noncoplanar_contact_pairs':0,'coplanar_contact_pairs':0,'shared_feature_only_pairs':0}
for i,j in sorted(pairs):
 a,b=ts[i],ts[j];na,nb=plane_normal(a),plane_normal(b);common=[p for p in a if any(np.linalg.norm(p-q)<1e-5 for q in b)];sameplane=max(abs((b-a[0])@na))<1e-6 and abs(np.dot(na,nb))>1-1e-8
 if sameplane:
  drop=int(np.argmax(abs(na)));dims=[k for k in range(3) if k!=drop];inter=Polygon(a[:,dims]).intersection(Polygon(b[:,dims]));
  if inter.is_empty:continue
  stats['coplanar_contact_pairs']+=1
  allowed=Point(common[0][dims]) if len(common)==1 else LineString([common[0][dims],common[1][dims]]) if len(common)>=2 else None
  beyond=inter if allowed is None else inter.difference(allowed.buffer(1e-4))
  if not beyond.is_empty and (beyond.area>1e-8 or beyond.length>1e-4):issues.append({'triangles':[i,j],'type':'coplanar_overlap_outside_shared_feature','shared_vertices':len(common),'projection_overlap_area_m2':inter.area,'outside_shared_feature_area_m2':beyond.area})
  else:stats['shared_feature_only_pairs']+=1
 else:
  hits=edge_hits(a,b)+edge_hits(b,a)
  if not hits:continue
  stats['noncoplanar_contact_pairs']+=1
  if len(common)==0:bad=hits
  elif len(common)==1:bad=[p for p in hits if np.linalg.norm(p-common[0])>1e-4]
  else:bad=[p for p in hits if point_segment_distance(p,common[0],common[1])>1e-4]
  if bad:issues.append({'triangles':[i,j],'type':'noncoplanar_intersection_outside_shared_feature','shared_vertices':len(common),'intersection_points_xyz':[p.tolist() for p in bad]})
  else:stats['shared_feature_only_pairs']+=1
result={'scope':'Actual finite GLB main-shell triangle intersection check for every pair whose AABBs overlap and at least one triangle differs from31d. Includes all original unchanged triangles as possible partners. No analytic mapping-injectivity argument.','changed_or_new_triangulation_triangles':int(sum(changed)),'statistics':stats,'intersection_candidates_outside_legal_shared_features':issues,'local_self_intersection_pass':not issues,'tolerances':{'aabb_margin_m':1e-7,'plane_m':1e-6,'shared_coordinate_m':1e-5,'allowed_shared_feature_band_m':1e-4},'limits':['Local changed-region versus entire main-shell sweep only; unchanged/unchanged baseline pairs excluded.','Legal shared vertices/edges ignored only inside0.1mm band; smaller defects are outside stated resolution.','17 independent rocks deliberately intersect main shell as separate objects; their authored contact is not a shell self-intersection.','Numerical triangle test is bounded-resolution evidence, not exact-predicate proof or complete walking test.']}
(R/'reviews/round-31e-local-intersections.json').write_text(json.dumps(result,indent=2),encoding='utf-8');p=R/'reviews/round-31e-independent-geometry.json';r=json.loads(p.read_text());r['local_triangle_intersection_check_pending']=False;r['local_triangle_intersections']=result;r['pass']=r['base_geometry_and_support_pass'] and result['local_self_intersection_pass'] and r['changed_triangles_normal_reversal_count']==0;p.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

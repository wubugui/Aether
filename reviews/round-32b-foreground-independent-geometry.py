from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'decoder','exec'))
from shapely.strtree import STRtree
from shapely.geometry import shape
from shapely.affinity import affine_transform
helper=(R/'reviews/round-30d-cutback-intake.py').read_text(encoding='utf-8');exec(helper[helper.index('def triangles'):helper.index('road=unary_union')])
P=R/'captures/foreground_island_study_32b';d=glb(P/'island_a.glb');reopen=json.loads((R/'reviews/round-32b-reopened-source.json').read_text());plan=json.loads((P/'design-plan.json').read_text());tn='island_a grass and exposed rock terrain';cn='island_a faulted bedrock';assert len(d)==11
def key(p):return tuple(map(float,p))
def tk(t):return tuple(sorted(key(p) for p in t))
stats=[]
for name,ts in d.items():
 edges=collections.Counter();direct=collections.Counter();adj=collections.defaultdict(set)
 for t in ts:
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   a,b=key(a),key(b);edges[tuple(sorted([a,b]))]+=1;direct[a,b]+=1;adj[a].add(b);adj[b].add(a)
 remain=set(adj);components=[]
 while remain:
  todo=[remain.pop()];n=0
  while todo:
   a=todo.pop();n+=1
   for b in adj[a]:
    if b in remain:remain.remove(b);todo.append(b)
  components.append(n)
 area=np.linalg.norm(np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]),axis=1)/2;vol=float(np.einsum('ij,ij->i',ts[:,0],np.cross(ts[:,1],ts[:,2])).sum()/6);native=reopen['objects'][name];nv=np.array(native['vertices']);nt=nv[native['triangles']];row={'object':name,'actual_GLB_triangles':len(ts),'exact_coordinate_manifold_edges':all(n==2 for n in edges.values()),'opposite_directed_edges':all(direct[a,b]==direct[b,a]==1 for a,b in edges),'signed_volume_m3':vol,'minimum_triangle_area_m2':float(min(area)),'components_vertices':components,'native_loop_triangle_counter_exact':collections.Counter(tk(t) for t in ts)==collections.Counter(tk(t) for t in nt)};row['pass']=row['exact_coordinate_manifold_edges'] and row['opposite_directed_edges'] and vol>0 and min(area)>1e-10 and row['native_loop_triangle_counter_exact'];stats.append(row)
def surfaces(ts,up=True):
 n=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0])[:,2];return [(i,t,Polygon(t[:,:2]),plane(t)) for i,t in enumerate(ts) if (n[i]>1e-10 if up else n[i]<-1e-10)]
captop=surfaces(d[tn]);capbottom=surfaces(d[tn],False);coretop=surfaces(d[cn]);core_index=STRtree([x[2] for x in coretop])
def flatcheck(mask,height):
 covered=[];flat=[];vals=[];bad=[]
 for fi,t,poly,co in captop:
  inter=poly.intersection(mask)
  if inter.area<1e-10:continue
  covered.append(inter);ds=[float(np.dot(co,[*p,1])-height) for p in coords(inter)];vals+=ds
  if max(abs(x) for x in ds)<.001:flat.append(inter)
  else:bad.append({'triangle':fi,'area_m2':inter.area,'error_min_max_m':[min(ds),max(ds)]})
 cov=unary_union(covered);good=unary_union(flat);return {'footprint_area_m2':mask.area,'covered_area_m2':cov.area,'uncovered_area_m2':mask.difference(cov).area,'not_planar_within1mm_area_m2':mask.difference(good).area,'height_error_min_max_m':[min(vals),max(vals)] if vals else None,'bad_clipped_triangles':bad,'pass':mask.difference(good).area<1e-6}
def interface(mask):
 coverage=[];matched=[];vals=[];bad=[];bottomcoverage=[]
 for fi,t,poly,co in capbottom:
  a=poly.intersection(mask)
  if a.area<1e-10:continue
  bottomcoverage.append(a)
  for j in core_index.query(a):
   fj,tt,pp,cc=coretop[int(j)];patch=a.intersection(pp)
   if patch.area<1e-10:continue
   coverage.append(patch);ds=[float(np.dot(co-cc,[*p,1])) for p in coords(patch)];vals+=ds
   if max(abs(x) for x in ds)<.001:matched.append(patch)
   else:bad.append({'cap_bottom_triangle':fi,'core_top_triangle':fj,'area_m2':patch.area,'cap_bottom_minus_core_top_min_max_m':[min(ds),max(ds)]})
 joint=unary_union(matched);return {'footprint_area_m2':mask.area,'cap_bottom_uncovered_area_m2':mask.difference(unary_union(bottomcoverage)).area,'interface_unmatched_within1mm_area_m2':mask.difference(joint).area,'cap_bottom_minus_core_top_min_max_m':[min(vals),max(vals)] if vals else None,'mismatch_pairs':bad,'pass':mask.difference(joint).area<1e-6}
exec((R/'reviews/round-32b-asset-footprint-decoder.py').read_text(encoding='utf-8'))
house=R/'captures/validation_runs/lantern-island-31i-20260908T214100Z-02d75d5cf747426d88e00816dda55bd0/study-inputs/keeper_house.glb';tower=R/'assets/models/lighthouse.glb';fixtures={}
for role,path in [('house',house),('tower',tower)]:
 at=asset_world_triangles(path);x=at.reshape(-1,3);z=float(x[:,2].min());bottom=x[abs(x[:,2]-z)<1e-6,:2];hull=MultiPoint(bottom).convex_hull;mask=unary_union([Polygon(t[:,:2]) for t in at if np.max(abs(t[:,2]-z))<1e-6 and Polygon(t[:,:2]).area>1e-10]);fixtures[role]={'path':str(path.relative_to(R)),'sha256':sha(path),'native_bottom_z_m':z,'native_bottom_vertex_hull_xy':list(hull.exterior.coords),'actual_bottom_triangle_union_geojson':mask.__geo_interface__,'native_bottom_area_m2':mask.area,'vertex_hull_area_m2':hull.area}
sites=[]
for pad in plan['pads']:
 c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);rot=np.array([[c,-s],[s,c]]);xy=np.array(pad['xy']);hx,hy=pad['half'];pm=Polygon(np.array([[-hx,-hy],[hx,-hy],[hx,hy],[-hx,hy]])@rot.T+xy);asset=fixtures['tower' if pad['id']=='tower' else 'house'];sc=pad['scale'];fm=affine_transform(shape(asset['actual_bottom_triangle_union_geojson']),[c*sc,-s*sc,s*sc,c*sc,*xy]);sites.append({'site':pad['id'],'design':pad,'design_pad_polygon_xy':list(pm.exterior.coords),'actual_asset_bottom_footprint_geojson':fm.__geo_interface__,'actual_asset_base_outside_pad_area_m2':fm.difference(pm).area,'full_design_pad_surface':flatcheck(pm,pad['height']),'actual_building_bottom_footprint_surface':flatcheck(fm,pad['height']),'full_design_pad_cap_core_interface':interface(pm),'actual_asset_footprint_cap_core_interface':interface(fm),'actual_asset_bottom_world_z_if_instance_origin_on_pad_m':pad['height']+asset['native_bottom_z_m']*pad['scale']})
report={'round':'32b','scope':'Independent actual saved native reopen plus exported11mesh topology, full triangle-clipped3design pads and actual frozen building bottom footprints, cap underside/core top interface over pads.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_a.blend',P/'island_a.glb',P/'design-plan.json',P/'native-check.json',R/'reviews/round-32b-reopened-source.json',house,tower]},'source_reopen_report':'reviews/round-32b-reopened-source.json','actual_source_reopened_and_unchanged':reopen['source_file_unchanged'],'native_closed_positive_pass':reopen['native_closed_positive_pass'],'actual_GLB_mesh_checks':stats,'building_assets':fixtures,'sites':sites,'planned_tree_actual_source_rays':reopen['planned_trees_actual_rays'],'pass':all(a['pass'] for a in stats) and all(a['full_design_pad_surface']['pass'] and a['actual_building_bottom_footprint_surface']['pass'] and a['full_design_pad_cap_core_interface']['pass'] and a['actual_asset_footprint_cap_core_interface']['pass'] for a in sites),'full_reference_accepted':False,'limits':['Footprints use actual asset lowest-Z horizontal triangle union after full scene-node transforms, not a convex hull or decorative roof eaves; uniform scale and Blender yaw come from32bdesign, actual runtime placement still pending.','Triangle clipping covers entire pad/base area, not only9sample points.','Cap/core interface tolerance1mm; all measured extrema retained, no whole-island self-intersection or seam check outside3pads.','Native/GLB topology closure and positive volume do not prove all3D self-intersections absent.','8tree checks are axes only, not full trunk base support; steep locations remain flagged for root.','No GPU/fullworld/flight/visual acceptance.']}
(R/'reviews/round-32b-foreground-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'pass':report['pass'],'meshes':stats,'fixtures':fixtures,'sites':[{k:a[k] for k in ['site','actual_asset_base_outside_pad_area_m2','full_design_pad_surface','actual_building_bottom_footprint_surface','full_design_pad_cap_core_interface']} for a in sites]},indent=2))



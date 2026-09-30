from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'round-29a-independent-geometry.py','exec'))
from shapely.strtree import STRtree
helper=(R/'reviews/round-30d-cutback-intake.py').read_text(encoding='utf-8');exec(helper[helper.index('def triangles'):helper.index('road=unary_union')])
P=R/'captures/lantern_island_study_30d';B=R/'captures/lantern_island_study_30c';e=json.loads((P/'geometry-evidence.json').read_text());old=json.loads((B/'geometry-evidence.json').read_text())['new'];d=glb(P/'island_c.glb');db=glb(B/'island_c.glb');actual=counter(np.concatenate(list(d.values())));tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths'
assert e['old']==old and len(e['new'])==19
preserved=[]
for name,ob in e['new'].items():
 if name!=tn:assert ob==old[name];preserved.append(name)
 for i,t in triangles(ob):assert tri_key(t) in actual
key=next(k for k in d if 'olive grass' in k);ts=d[key];baseline=db[key]
assert counter(ts)==counter(np.array(e['new'][tn]['vertices'])[e['new'][tn]['polygons']])
edge=collections.Counter();direct=collections.Counter()
for t in ts:
 for a,b in zip(t,np.roll(t,-1,axis=0)):
  a,b=pointkey(a),pointkey(b);edge[tuple(sorted((a,b)))]+=1;direct[a,b]+=1
assert all(c==2 for c in edge.values()) and all(direct[a,b]==direct[b,a]==1 for a,b in edge)
areas=np.linalg.norm(np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]),axis=1)/2;assert np.min(areas)>1e-10
volume=float(np.sum(np.einsum('ij,ij->i',ts[:,0],np.cross(ts[:,1],ts[:,2]))/6));assert volume>0
def up(ts):return [t for t in ts if np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-9]
ng=up(ts);og=up(baseline);npoly=[Polygon(t[:,:2]) for t in ng];nplane=[plane(t) for t in ng];index=STRtree(npoly)
pathkey=next(k for k in d if 'footpath' in k);assert counter(d[pathkey])==counter(db[pathkey]);road=unary_union([Polygon(t[:,:2]) for t in up(d[pathkey])]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']]);intake=json.loads((R/'reviews/round-30d-cutback-intake.json').read_text());trees=unary_union([Point(p['xy']).buffer(2) for p in intake['tree_axes']]);masks={'road_footprint':road,'padded_sites':pads,'current_CD_tree_axis_2m_disks':trees};supports=[]
for name,mask in masks.items():
 expected=[];pres=[];changedhigher=[];vals=[]
 for ot in og:
  op=Polygon(ot[:,:2]).intersection(mask)
  if op.area<1e-10:continue
  expected.append(op);oc=plane(ot)
  for j in index.query(op):
   patch=op.intersection(npoly[j])
   if patch.area<1e-10:continue
   delta=nplane[j]-oc;ds=[float(np.dot(delta,[*xy,1])) for xy in coords(patch)];vals.extend(ds)
   if max(abs(x) for x in ds)<1e-4:pres.append(patch)
   above=patch.intersection(halfplane(delta-[0,0,1e-4]))
   if above.area>1e-8:changedhigher.append(above)
 expected=unary_union(expected);pres=unary_union(pres);missing=expected.difference(pres).area;higher=unary_union(changedhigher).area
 supports.append({'region':name,'expected_support_projection_area_m2':expected.area,'same_linear_height_coverage_m2':expected.intersection(pres).area,'unpreserved_area_m2':missing,'higher_than_old_by_over_0_1mm_area_m2':higher,'all_intersecting_up_surface_height_delta_min_max_m':[min(vals),max(vals)] if vals else None,'pass':missing<1e-5 and higher<1e-5})
def exposure(ground,rock):
 gp=[Polygon(t[:,:2]) for t in ground];gc=[plane(t) for t in ground];ix=STRtree(gp);projected=[];allroofs=[];surface=0
 for _,rt in upper(rock):
  rc=plane(rt);rp=Polygon(rt[:,:2]).intersection(halfplane(rc-[0,0,.5]));allroofs.append(rp);hidden=[]
  for j in ix.query(rp):
   patch=rp.intersection(gp[j]).intersection(halfplane(gc[j]-rc-[0,0,.0001]))
   if not patch.is_empty:hidden.append(patch)
  exposed=rp.difference(unary_union(hidden));projected.append(exposed);cross=np.cross(rt[1]-rt[0],rt[2]-rt[0]);surface+=exposed.area*np.linalg.norm(cross)/abs(cross[2])
 return {'shoulder_z_threshold_m':.5,'total_roof_projection_area_m2':unary_union(allroofs).area,'exposed_projection_area_m2':unary_union(projected).area,'exposed_upward_3d_surface_area_m2':float(surface)}
exposed=[]
for name in ['West broken shoulder','Southwest leaning crag','North broken ridge']:
 before=exposure(og,old[name]);after=exposure(ng,e['new'][name]);exposed.append({'rock':name,'before_30c':before,'after_30d':after,'exposed_projection_gain_m2':after['exposed_projection_area_m2']-before['exposed_projection_area_m2']})
report={'round':'30d','scope':'Actual GLB native cutback check, no old top-index assumption. Exact clipped supporting linear surfaces checked only required road/pads/current tree disks. Exposure measured for three targeted unchanged rocks only.','files':{str(p.relative_to(R)):sha(p) for p in [P/'island_c.glb',P/'geometry-evidence.json',B/'island_c.glb',R/'reviews/round-30d-cutback-intake.json']},'native_objects':19,'source_terrain_all_triangles_equal_actual_glb':True,'actual_glb_closed_oppositely_paired_edges_at_1e_5m':True,'actual_glb_min_triangle_area_m2':float(min(areas)),'actual_glb_volume_m3':volume,'path_and_17_rocks_source_exact_actual_triangles_present':preserved,'actual_path_glb_counter_exact':True,'required_support_surfaces':supports,'three_rock_exposure':exposed,'pass':all(x['pass'] for x in supports),'limits':['Exposure uses actual upward rock roof minus upper main-shell coverage, roof Z>=0.5m, 0.1mm separation tolerance. It is geometric surface exposure, not screen-space visibility.','Not exhaustive 3D self-intersection or walking test.','Tree support follows current30c runtime axes; candidate runtime placements checked separately by root.','Positive exposed area is not art acceptance; same-camera actual GPU review remains required.']}
(R/'reviews/round-30d-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','path_and_17_rocks_source_exact_actual_triangles_present']},indent=2))

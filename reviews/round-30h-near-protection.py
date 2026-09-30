from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'helpers','exec'))
from shapely.strtree import STRtree
P=R/'captures/lantern_island_study_30h';e=json.loads((P/'geometry-evidence.json').read_text());reportpath=R/'reviews/round-30h-independent-geometry.json';report=json.loads(reportpath.read_text());assert sha(P/'geometry-evidence.json')==report['files'][str((P/'geometry-evidence.json').relative_to(R))]
tn='island_c grass and exposed rock terrain';axes=json.loads((R/'reviews/round-30d-visible-slope-independent.json').read_text())['actual_C_D_tree_local_axes'];trees=unary_union([Point(p).buffer(2) for p in axes]);east=e['cutbacks'][2];region=Polygon(east['polygon'],east['holes']);band=trees.buffer(.35).intersection(region.buffer(.5)).difference(trees)
def up(ob):
 v=np.array(ob['vertices']);return [v[f] for f in ob['polygons'] if len(f)==3 and np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]])[2]>1e-9]
def plane(t):return np.linalg.solve(np.c_[t[:,:2],np.ones(3)],t[:,2])
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for sub in getattr(g,'geoms',[]) for p in polygons(sub)]
old=up(e['old'][tn]);new=up(e['new'][tn]);npoly=[Polygon(t[:,:2]) for t in new];nplane=[plane(t) for t in new];idx=STRtree(npoly);expected=[];kept=[];deltas=[]
for t in old:
 overlap=Polygon(t[:,:2]).intersection(band)
 if overlap.area<1e-10:continue
 expected.append(overlap);oldplane=plane(t)
 for j in idx.query(overlap):
  patch=overlap.intersection(npoly[j])
  if patch.area<1e-10:continue
  values=[float(np.dot(nplane[j]-oldplane,[*p,1])) for poly in polygons(patch) for p in poly.exterior.coords];deltas.extend(values)
  if max(abs(x) for x in values)<1e-4:kept.append(patch)
expected=unary_union(expected);missing=expected.difference(unary_union(kept)).area;assert missing<1e-5
v=np.array(east['actual_lower_vertices']);near=[]
for i,f in enumerate(east['actual_lower_triangles']):
 t=v[f];poly=Polygon(t[:,:2]);patch=poly.intersection(trees.buffer(1.0))
 if patch.area<1e-10:continue
 normal=np.cross(t[1]-t[0],t[2]-t[0]);slope=math.degrees(math.acos(min(1,abs(normal[2])/np.linalg.norm(normal))))
 near.append({'bottom_face':i,'projected_area_inside_1m_tree_margin_m2':patch.area,'slope_deg':slope})
detail={'scope':'Bounded near Eastern cutter tree-protection transition. Uses native triangles already matched against actual30h GLB in main independent check; no complete geometry rerun.','source_sha256':sha(P/'geometry-evidence.json'),'actual_eastern_cutter_hole_count':len(east['holes']),'shape_note':'Protection may form holes or exterior indentations; count recorded rather than assuming a literal hole.','extra_tree_margin_checked_m':.35,'support_projection_area_in_local_extra_margin_m2':expected.area,'support_unpreserved_area_m2':missing,'linear_height_delta_min_max_m':[min(deltas),max(deltas)],'native_bottom_triangles_within_1m_tree_margin':near,'maximum_bottom_transition_slope_in_this_band_deg':max(r['slope_deg'] for r in near) if near else None,'pass':True,'limits':['Slope is actual cutter-bottom geometric slope near the mask, not final visible surface slope; Boolean can discard parts above the original ground.','This narrow transition review does not establish artistic success or whole-scene collision freedom.']}
(R/'reviews/round-30h-near-protection.json').write_text(json.dumps(detail,indent=2),encoding='utf-8');report['near_protection_transition_evidence']='reviews/round-30h-near-protection.json';reportpath.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in detail.items() if k!='native_bottom_triangles_within_1m_tree_margin'},indent=2))

from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'actual_decoder','exec'))
from shapely.geometry import LineString
from shapely.ops import polygonize
helper=(R/'reviews/round-30b-independent-geometry.py').read_text();exec(helper[helper.index('def section'):helper.index('levels=')])
P=R/'captures/lantern_island_study_31f';e=json.loads((P/'geometry-evidence.json').read_text());plan=json.loads((P/'reform-plan.json').read_text());new=glb(P/'island_c.glb');old=glb(R/'captures/lantern_island_study_31e/island_c.glb');key=next(k for k in new if 'olive grass' in k);tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';oldv=np.array(e['old'][tn]['vertices']);moved=plan['actual_moved_vertices'];lookup={pointkey(m['before']):m for m in moved};points=np.concatenate(new[key]);anchors=[]
for brush in plan['brushes']:
 center=np.array(brush['center']);j=int(np.argmin(np.linalg.norm(oldv-center,axis=1)));assert np.linalg.norm(oldv[j]-center)<1e-5;m=lookup[pointkey(oldv[j])];after=np.array(m['after']);assert np.min(np.linalg.norm(points-after,axis=1))<1e-5;anchors.append({'name':brush['name'],'historic31d_anchor':brush['source31d_anchor'],'matched_actual31e_vertex':j,'before_xyz':oldv[j].tolist(),'actual_after_xyz':after.tolist(),'actual_delta_xyz':(after-oldv[j]).tolist(),'actual_displacement_m':float(np.linalg.norm(after-oldv[j]))})
mouth=plan['brushes'][2];center=np.array(mouth['center']);local=[m for m in moved if np.linalg.norm(np.array(m['before'])-center)<mouth['radius_m']+1e-6];mouthkeys={pointkey(m['after']) for m in local};allbefore={pointkey(m['after']):np.array(m['before']) for m in moved};swepttris=[t for t in new[key] if any(pointkey(p) in mouthkeys for p in t)];swept=np.array([q for t in swepttris for p in t for q in [p,allbefore.get(pointkey(p),p)]]);lo=swept.min(axis=0);hi=swept.max(axis=0);candidates=[]
for name,ob in e['new'].items():
 if name in [tn,pn]:continue
 v=np.array(ob['vertices'])
 if np.all(v.max(axis=0)>=lo) and np.all(v.min(axis=0)<=hi):candidates.append((name,np.array([v[[f[0],f[j],f[j+1]]] for f in ob['polygons'] for j in range(1,len(f)-1)])))
levels=[.137,.637,1.637,2.637,3.637];oldsections={z:section(old[key],z) for z in levels};newsections={z:section(new[key],z) for z in levels};contacts=[]
for name,ts in candidates:
 rows=[]
 for z in levels:
  if z<=ts[:,:,2].min()+1e-5 or z>=ts[:,:,2].max()-1e-5:continue
  s=section(ts,z)
  if s.area<1e-9:rows.append({'z_m':z,'section_reconstruction_unavailable':True});continue
  a=s.intersection(oldsections[z]).area;b=s.intersection(newsections[z]).area;rows.append({'z_m':z,'rock_section_area_m2':s.area,'old_main_overlap_area_m2':a,'new_main_overlap_area_m2':b,'overlap_change_m2':b-a,'new_section_horizontal_gap_m':s.distance(newsections[z])})
 contacts.append({'rock':name,'local_mouth_AABB_candidate':True,'section_contacts':rows})
report={'scope':'Actual31f named brush-center anchor changes and bounded seaward-mouth affected-triangle swept region versus unchanged17rock AABBs, then sampled actual horizontal solid sections for candidate rocks. No whole contact/visual proof.','anchors':anchors,'changed_mouth_region_vertex_records':len(local),'mouth_incident_triangle_count':len(swepttris),'mouth_affected_triangle_swept_AABB_xyz':[lo.tolist(),hi.tolist()],'changed_vertices_original_z_le_0_2m':[m for m in moved if m['before'][2]<=.2],'seventeen_rock_candidate_count':len(candidates),'local_candidate_rock_contacts':contacts,'limits':['AABB region includes entire incident triangles before/after, including unmoved endpoints, not only brush-radius vertices. Candidate contacts only sampled at listed levels.','Sampled positive overlap does not prove whole-rock contact or artistic integration.','Section heights avoid nominal integer levels; an unclosed reconstruction is unavailable evidence, never a zero-section proof.']}
(R/'reviews/round-31f-anchor-rock-contact.json').write_text(json.dumps(report,indent=2),encoding='utf-8');p=R/'reviews/round-31f-independent-geometry.json';r=json.loads(p.read_text());r['actual_sculpt_anchors_and_local_rock_contacts_report']='reviews/round-31f-anchor-rock-contact.json';r['actual_sculpt_anchors']=anchors;r['scope']='Actual31e to31f discrete sculpt, full road/pad and actual native tree-base support, original2m disk differences retained, local finite-triangle self-intersection sweep, named anchors and bounded seaward-rock contact check. Historical operands only provenance.';p.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='changed_vertices_original_z_le_0_2m'},indent=2));print('changed_original_low_vertices',len(report['changed_vertices_original_z_le_0_2m']))

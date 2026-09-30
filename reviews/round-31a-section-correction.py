from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'decoder','exec'))
from shapely.geometry import LineString
from shapely.ops import polygonize
helper=(R/'reviews/round-30b-independent-geometry.py').read_text();exec(helper[helper.index('def section'):helper.index('levels=')])
p=R/'reviews/round-31a-independent-geometry.json';report=json.loads(p.read_text())
e=json.loads((R/'captures/lantern_island_study_31a/geometry-evidence.json').read_text())
d=glb(R/'captures/lantern_island_study_30k/island_c.glb');base=d[next(k for k in d if 'olive grass' in k)]
levels=[2.137,4.137,6.137];oldsections={z:section(base,z) for z in levels}
assert all(s.area>0 for s in oldsections.values())
for result,add in zip(report['additions'],e['additions']):
 ob=add['actual_operand_geometry'];v=np.array(ob['vertices']);tris=np.array([v[[f[0],f[j],f[j+1]]] for f in ob['polygons'] for j in range(1,len(f)-1)])
 result['superseded_section_reconstruction']=result.pop('old_main_real_section_intersections')
 result['superseded_section_reason']='Strict-crossing segment reconstruction omitted vertex/coplanar level segments at exact z=4 and z=6; zero polygon area was a reconstruction failure, not measured empty geometry. Superseded with nonvertex levels only, without repeating support checks.'
 out=[]
 for z in levels:
  dz=float(min(np.min(abs(base[:,:,2]-z)),np.min(abs(v[:,2]-z))));assert dz>1e-5
  ss=section(tris,z);assert ss.area>0
  inter=ss.intersection(oldsections[z]);out.append({'z_m':z,'minimum_vertex_height_distance_m':dz,'operand_section_area_m2':ss.area,'old_main_section_area_m2':oldsections[z].area,'overlap_area_m2':inter.area})
 assert any(s['overlap_area_m2']>1e-5 for s in out)
 result['old_main_real_section_intersections']=out
report['section_correction_script']='reviews/round-31a-section-correction.py'
p.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps([{'name':a['name'],'sections':a['old_main_real_section_intersections']} for a in report['additions']],indent=2))

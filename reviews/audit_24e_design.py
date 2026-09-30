"""24e design-only independent cap reconstruction. No Blender, GLB export or engine execution."""
from pathlib import Path
import json,hashlib,math,numpy as np
from shapely.geometry import Polygon,LineString,Point,shape
from shapely.ops import unary_union
ROOT=Path('E:/FeiTing');SRC=ROOT/'captures/village_paving_design_24e/paving.json';D=json.loads(SRC.read_text());PLAN=json.loads((ROOT/'captures/village_street_layout_24a/layout.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def sections(g):
 if g.is_empty:return []
 if isinstance(g,LineString):return [g]
 return [p for c in getattr(g,'geoms',[]) for p in sections(c)]
def caps(group):
 polygons={};areas=[]
 for solid in group['solids']:
  v=np.array(solid['vertices_xz']);triangles=[Polygon(v[t]) for t in solid['cap_triangles']];areas.extend(t.area for t in triangles);poly=unary_union(triangles);polygons.setdefault((solid['kind'],solid['top_y']),[]).append(poly)
 return {k:unary_union(v) for k,v in polygons.items()},min(areas)
def line_profile(line,beds):
 raw=[]
 for y,poly in beds.items():
  for s in sections(line.intersection(poly)):
   ds=[line.project(Point(p)) for p in s.coords];a,b=min(ds),max(ds)
   if b-a>1e-6:raw.append([a,b,y+.012])
 raw.sort();runs=[]
 for a,b,y in raw:
  if runs and abs(runs[-1][2]-y)<1e-6 and a-runs[-1][1]<.001:runs[-1][1]=max(runs[-1][1],b)
  else:runs.append([a,b,y])
 jumps=[];short=[];grooves=[]
 for i,(a,b,y) in enumerate(runs):
  if b-a<.2:short.append({'start_m':a,'length_m':b-a,'height':y,'xz':list(line.interpolate((a+b)/2).coords)[0]})
  if i:
   jump=y-runs[i-1][2]
   if abs(jump)>.1501:jumps.append({'at_m':a,'change_m':jump,'from_y':runs[i-1][2],'to_y':y,'xz':list(line.interpolate(a).coords)[0]})
  if i and i<len(runs)-1 and b-a<.2 and runs[i-1][2]>y+.015 and runs[i+1][2]>y+.015:grooves.append({'start_m':a,'length_m':b-a,'height':y,'left_height':runs[i-1][2],'right_height':runs[i+1][2],'xz':list(line.interpolate((a+b)/2).coords)[0]})
 return {'runs':runs,'short_under_0_20m':short,'grooves_under_0_20m':grooves,'jumps_over_0_1501m':jumps,'max_abs_rise':max([abs(runs[i][2]-runs[i-1][2]) for i in range(1,len(runs))],default=0),'minimum_run_m':min(b-a for a,b,y in runs)}
out=[]
for gi,g in enumerate(D['groups']):
 cs,minarea=caps(g);beds={y:p for (k,y),p in cs.items() if k=='foundation'};pv={y:p for (k,y),p in cs.items() if k=='paver'};allbed=unary_union(list(beds.values()));fp=shape(json.loads(g['footprint_geojson']));routes=[];entries=[]
 for ri,coords in enumerate(g['routes']):
  line=LineString(coords);profiles=[]
  for off in [0,-.6,.6]:
   ll=line if off==0 else line.offset_curve(off,quad_segs=4,join_style=1)
   if ll.geom_type!='LineString':profiles.append({'offset':off,'split':True});continue
   p=line_profile(ll,beds);p['offset']=off;profiles.append(p)
  routes.append({'house':PLAN['groups'][gi]['routes'][ri]['house'],'profiles':profiles})
 for entry in g['entries']:
  poly=shape(json.loads(entry['polygon_geojson']));yy=entry['height'];bed=unary_union([pp for y,pp in beds.items() if abs(y+.012-yy)<1e-6]);stone=unary_union([pp for y,pp in pv.items() if abs(y-yy)<1e-6]);wrong=[{'height':y+.012,'area':pp.intersection(poly).area} for y,pp in beds.items() if abs(y+.012-yy)>1e-6 and pp.intersection(poly).area>1e-7];entries.append({'house':entry['house'],'height':yy,'patch_area':poly.area,'bed_coverage':bed.intersection(poly).area,'paver_coverage':stone.intersection(poly).area,'other_level_overlap':wrong})
 grading={r['height']:shape(json.loads(r['geojson'])) for r in g['grading_bands']};gradeerrors=[{'level':y+.012,'difference_m2':pp.symmetric_difference(grading.get(round(y+.012,7),Polygon())).area} for y,pp in beds.items()];out.append({'group':g['name'],'solids':len(g['solids']),'min_cap_triangle_area':minarea,'footprint_difference_m2':allbed.symmetric_difference(fp).area,'actual_cap_vs_grading_band':gradeerrors,'entries':entries,'routes':routes})
result={'scope':'Design solids cap triangulation reconstruction only. No Blender/native meshes/GPU yet; retained terrain will require separate authored grading and export review.','source':str(SRC),'sha256':sha(SRC),'builder_sha256':sha(ROOT/'tools/prepare_village_paving_24e.py'),'groups':out};(ROOT/'reviews/round-24e-village-paving-independent-design-review.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps([{'group':g['group'],'solids':g['solids'],'entries_wrong':[(e['house'],e['other_level_overlap']) for e in g['entries'] if e['other_level_overlap']],'profiles':[{'house':r['house'],'cuts':[{'offset':p['offset'],'min':p.get('minimum_run_m'),'shorts':len(p.get('short_under_0_20m',[])),'grooves':p.get('grooves_under_0_20m'),'maxrise':p.get('max_abs_rise'),'bigjumps':p.get('jumps_over_0_1501m')} for p in r['profiles']]} for r in g['routes']]} for g in out],indent=2))

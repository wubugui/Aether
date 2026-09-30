"""Read actual 24c GLB caps and measure design interfaces, shared levels and route treads. Writes review JSON only."""
from pathlib import Path
import json,struct,hashlib,math,numpy as np
from shapely.geometry import Polygon,LineString,Point,shape
from shapely.ops import unary_union
ROOT=Path('E:/FeiTing');B=ROOT/'captures/village_paving_study_24c';D=json.loads((B/'paving-design.json').read_text());PLAN=json.loads((ROOT/'captures/village_street_layout_24a/layout.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def glb_caps(path):
 raw=path.read_bytes();ln=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+ln]);buf=raw[28+ln:]
 def acc(i):
  a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];typ={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];n={'VEC3':3,'SCALAR':1}[a['type']];sz=np.dtype(typ).itemsize
  return np.ndarray((a['count'],n),dtype=typ,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*sz),sz)).copy()
 groups={};mins=[];ntris=0
 for node in d['nodes']:
  assert not any(k in node for k in ['matrix','translation','rotation','scale'])
  if 'mesh' not in node:continue
  for pr in d['meshes'][node['mesh']]['primitives']:
   v=acc(pr['attributes']['POSITION']).astype(float)+np.array([-2180,0,-1830]);f=acc(pr['indices']).reshape(-1,3);t=v[f];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mins.append(float((np.linalg.norm(normal,axis=1)/2).min()));ntris+=len(t);mat=d['materials'][pr['material']]['name'];kind='foundation' if 'buried rubble' in mat else 'paver'
   for tri,no in zip(t,normal):
    if no[1]>1e-9 and np.ptp(tri[:,1])<1e-6:
     groups.setdefault((kind,float(tri[0,1])),[]).append(Polygon(tri[:,[0,2]]))
 return {k:unary_union(v) for k,v in groups.items()},{'triangles':ntris,'minimum_triangle_area_m2':min(mins)}
def lines(g):
 if g.is_empty:return []
 if isinstance(g,LineString):return [g]
 return [p for c in getattr(g,'geoms',[]) for p in lines(c)]
reports=[]
for gi,g in enumerate(D['groups']):
 caps,meta=glb_caps(B/('village_'+g['name']+'.glb'));beds={y:poly for (kind,y),poly in caps.items() if kind=='foundation'};pavers={y:poly for (kind,y),poly in caps.items() if kind=='paver'};un=unary_union(list(beds.values()));designfp=shape(json.loads(g['footprint_geojson']));components=list(un.geoms) if hasattr(un,'geoms') else [un];court=shape(json.loads(g['court_geojson']));entries=[]
 for en in g['entries']:
  pp=shape(json.loads(en['polygon_geojson']));height=en['height'];bp=unary_union([poly for y,poly in beds.items() if abs(y+.012-height)<1e-5]);pv=unary_union([poly for y,poly in pavers.items() if abs(y-height)<1e-5]);entries.append({'house':en['house'],'entry_y':height,'patch_area_m2':pp.area,'actual_bedding_coverage_m2':bp.intersection(pp).area,'actual_paver_coverage_m2':pv.intersection(pp).area,'bedding_to_patch_missing_m2':pp.difference(bp).area,'max_bedding_level_error_m':max([abs(y+.012-height) for y,poly in beds.items() if poly.intersection(pp).area>1e-5],default=0)})
 routes=[]
 for ri,coords in enumerate(g['routes']):
  route=LineString(coords);segs=[]
  for y,poly in beds.items():
   for seg in lines(route.intersection(poly)):
    ds=[route.project(Point(pt)) for pt in seg.coords];aa,bb=min(ds),max(ds)
    if bb-aa>1e-6:segs.append([aa,bb,y+.012])
  segs.sort();merge=[]
  for a,b,y in segs:
   if merge and abs(merge[-1][2]-y)<1e-5 and a-merge[-1][1]<.001:merge[-1][1]=max(merge[-1][1],b)
   else:merge.append([a,b,y])
  transitions=[{'at_m':merge[i][0],'rise_m':merge[i][2]-merge[i-1][2],'gap_m':merge[i][0]-merge[i-1][1],'xz':list(route.interpolate(merge[i][0]).coords)[0]} for i in range(1,len(merge))];short=[{'a':a,'b':b,'depth_m':b-a,'y':y,'xz':list(route.interpolate((a+b)/2).coords)[0]} for a,b,y in merge if b-a<.20];routes.append({'house':PLAN['groups'][gi]['routes'][ri]['house'],'length_m':route.length,'terrace_runs':merge,'maximum_abs_rise_m':max([abs(x['rise_m']) for x in transitions],default=0),'rise_over_0_151m':[x for x in transitions if abs(x['rise_m'])>.151],'runs_under_0_20m':short,'run_count':len(merge),'min_run_m':min(b-a for a,b,y in merge),'centerline_xy_missing_m':route.difference(un).length})
 cp=unary_union([v for y,v in pavers.items() if abs(y-g['court_y'])<1e-5]);cb=unary_union([v for y,v in beds.items() if abs(y+.012-g['court_y'])<1e-5]);report={'name':g['name'],'actual_caps':meta,'glb_sha':sha(B/('village_'+g['name']+'.glb')),'source_sha':sha(B/('village_'+g['name']+'.blend')),'foundation_union_area_m2':un.area,'foundation_union_component_count':len(components),'components_over_0_001m2':sum(c.area>.001 for c in components),'largest_component_fraction':max(c.area for c in components)/un.area,'buffer_0_6mm_components':len(un.buffer(.0006).geoms) if hasattr(un.buffer(.0006),'geoms') else 1,'actual_footprint_difference_m2':un.symmetric_difference(designfp).area,'entries':entries,'court':{'level':g['court_y'],'area':court.area,'paver_coverage':cp.intersection(court).area,'bed_coverage':cb.intersection(court).area},'routes':routes};reports.append(report)
out={'scope':'Independent actual GLB horizontal caps; route tread lengths intersect stored design centrelines. Mortar 12mm below pavers treated separately; no GPU or full walking claim.','groups':reports,'design_sha':sha(B/'paving-design.json'),'model_report_sha':sha(B/'model-report.json')};(ROOT/'reviews/round-24c-village-paving-independent-audit.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps([{'name':r['name'],'caps':r['actual_caps'],'raw_components':r['foundation_union_component_count'],'buffer_components':r['buffer_0_6mm_components'],'area_difference':r['actual_footprint_difference_m2'],'entries':r['entries'],'routes':[{'house':q['house'],'count':q['run_count'],'min_run':q['min_run_m'],'under20':len(q['runs_under_0_20m']),'maxrise':q['maximum_abs_rise_m'],'bad_rises':q['rise_over_0_151m'][:3],'shortest':sorted(q['runs_under_0_20m'],key=lambda q:q['depth_m'])[:2]} for q in r['routes']]} for r in reports],indent=2))

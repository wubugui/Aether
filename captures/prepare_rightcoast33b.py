from pathlib import Path
import json,hashlib,math,numpy as np
from shapely.geometry import Polygon,Point,LineString,mapping,shape
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
prior=R/'captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=read(R/'captures/rightcoast33-native-intake.json');layout=read(prior/'study-inputs/headland/layout.json');paving=read(prior/'study-inputs/village-paving/paving-design.json')
assert sha(R/native['source'])==native['source_sha256']
origin=np.array(layout['origin'])
actual=read(R/'reviews/round-33-occupied-regions.json')
occupied=shape(actual['hard_occupied_house_and_paving_union']).buffer(.30)
bound=layout['boundary'];seams=[]
for a,b in zip(bound,bound[1:]+bound[:1]):
 if a['height'] is None or b['height'] is None:
  seams.append(LineString([(p['position'][0]-origin[0],-(p['position'][1]-origin[2])) for p in [a,b]]))
seam=unary_union(seams)
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def lobe(x,y,cx,cy,wx,wy,angle=0):
 c,s=math.cos(angle),math.sin(angle);u=c*(x-cx)+s*(y-cy);v=-s*(x-cx)+c*(y-cy)
 return max(0,1-max(abs(u)/wx,abs(v)/wy))
out={};all_changed=[];frozen_polys=[];locked_by_object={}
# Freeze complete original faces intersecting any conservative occupied region.
for name,obj in native['objects'].items():
 v=np.array(obj['vertices']);locked=set()
 for ids in obj['polygons']:
  p=Polygon(v[ids,:2])
  xyz=v[ids];normal=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0])
  if max(xyz[:,2])>0 and normal[2]>1e-7 and p.area>1e-8 and p.intersects(occupied):
   locked.update(ids);frozen_polys.append(p)
 locked_by_object[name]=locked
frozen=unary_union(frozen_polys)
for name,obj in native['objects'].items():
 v=np.array(obj['vertices']);new=v.copy();locked=locked_by_object[name]
 for i,(x,y,z) in enumerate(v):
  if i in locked or z<=-9.9:continue
  p=Point(x,y);d=frozen.distance(p)
  sitefade=smooth((d-8)/30);seamfade=smooth(seam.distance(p)/28);wetfade=smooth((z+10)/10)
  # Three unequal, oblique inland ridges separated by lower saddles.
  ridge=max(18*lobe(x,y,8,-70,81,96,-.40),24*lobe(x,y,12,88,82,90,.35),16*lobe(x,y,-14,180,55,63,-.34))
  # Two rock noses and a lowered inlet: no repeated uniform extrusions.
  shoulder=4*lobe(x,y,-92,-72,30,34,.20)+6*lobe(x,y,-69,154,30,35,-.3)
  cove=-3.2*lobe(x,y,-52,-3,38,39,.15)-2.5*lobe(x,y,-69,113,26,22,-.1)
  if not name.startswith('Mainland'):ridge=0
  dz=(ridge+shoulder+cove)*sitefade*seamfade*wetfade
  dx=(3*lobe(x,y,-94,-72,30,38,.2)-3*lobe(x,y,-74,160,26,35,-.3)+5*lobe(x,y,-47,0,30,38))*smooth((d-2)/22)*seamfade*wetfade
  new[i,0]+=dx;new[i,2]+=dz
 assert all(np.array_equal(new[i],v[i]) for i in locked)
 t=np.array(obj['triangles']);before=np.cross(v[t[:,1],:2]-v[t[:,0],:2],v[t[:,2],:2]-v[t[:,0],:2]);after=np.cross(new[t[:,1],:2]-new[t[:,0],:2],new[t[:,2],:2]-new[t[:,0],:2]);mask=abs(before)>1e-5
 assert np.all(before[mask]*after[mask]>0),(name,'XY fold')
 delta=np.linalg.norm(new-v,axis=1);ids=np.where(delta>1e-6)[0].tolist()
 out[name]=dict(vertices=new.tolist(),frozen_vertices=sorted(locked),changed_vertices=ids,max_displacement_m=float(max(delta)),minimum_nonvertical_XY_area_ratio=float(np.min(abs(after[mask]/before[mask]))) if mask.any() else None)
 all_changed.extend((name,i) for i in ids)
plan=dict(label='33b',scope='Author unequal real right-coast noses, low inlets and three setback inland ridges on current26b native topology. Full actual house foundation and actual paving occupied upper faces preserved, plus8m no-height-change apron; no buried bottom projection used as a surface freeze region. Trees/scatter refit at runtime. Not art or full20reference acceptance; production unchanged.',source=native['source'],source_sha256=native['source_sha256'],source_intake_sha256=sha(R/'captures/rightcoast33-native-intake.json'),basis_run=prior.name,origin=layout['origin'],occupied_region=mapping(occupied),frozen_face_region=mapping(frozen),occupied_definition='Independent actual nine foundation and922GLB paving domains,0.30m buffer; intersecting actual upward above-water polygons frozen in full. No hand-rotated pad surrogate.',objects=out,changed_vertex_count=len(all_changed),design='Three wider offset inland ridges18/24/16m before fades; near-village apron retains old height for8m, gradual30m rise; first coast nose moves shoreward3m, two lowered bays. Original mainland seam and submerged bottom retained. Authored design coordinates, not inferred original geography.')
p=R/'captures/rightcoast33b-design-plan.json';assert not p.exists()
plan['actual_occupied_report_sha256']=sha(R/'reviews/round-33-occupied-regions.json')
plan['rework_reason']='33a visible long thin transitions and overly continuous tall rock slope. Use actual foundation domains, upward source faces only, broader apron and offset lower ridges.33a mistaken reversed design-pad angle and buried-face protection are not copied.'
p.write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps(dict(changed=len(all_changed),parts=[dict(name=k,changed=len(v['changed_vertices']),max_m=v['max_displacement_m'],xy_ratio=v['minimum_nonvertical_XY_area_ratio']) for k,v in out.items()]),indent=2))

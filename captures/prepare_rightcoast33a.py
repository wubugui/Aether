from pathlib import Path
import json,hashlib,math,numpy as np
from shapely.geometry import Polygon,Point,LineString,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
prior=R/'captures/validation_runs/foreground-island-32f-20260908T224143Z-7598ab628ffa40f0a4f20816ba9f05e2'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=read(R/'captures/rightcoast33-native-intake.json');layout=read(prior/'study-inputs/headland/layout.json');paving=read(prior/'study-inputs/village-paving/paving-design.json')
assert sha(R/native['source'])==native['source_sha256']
origin=np.array(layout['origin']);regions=[]
for h in layout['houses']:
 x,z=h['position'][0]-origin[0],-(h['position'][2]-origin[2]);c,s=math.cos(h['yaw']),math.sin(h['yaw']);w,d=h['pad_half_size']
 regions.append(Polygon([(x+c*u+s*v,z-s*u+c*v) for u,v in [(-w,-d),(w,-d),(w,d),(-w,d)]]))
for g in paving['groups']:
 for solid in g['solids']:
  vs=np.array(solid['vertices_xz']);vs=np.column_stack((vs[:,0]-origin[0],-(vs[:,1]-origin[2])))
  regions.extend(Polygon(vs[ids]) for ids in solid['cap_triangles'])
occupied=unary_union(regions).buffer(.20)
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
  if p.area>1e-8 and p.intersects(occupied):
   locked.update(ids);frozen_polys.append(p)
 locked_by_object[name]=locked
frozen=unary_union(frozen_polys)
for name,obj in native['objects'].items():
 v=np.array(obj['vertices']);new=v.copy();locked=locked_by_object[name]
 for i,(x,y,z) in enumerate(v):
  if i in locked or z<=-9.9:continue
  p=Point(x,y);d=frozen.distance(p)
  sitefade=smooth(d/22);seamfade=smooth(seam.distance(p)/28);wetfade=smooth((z+10)/10)
  # Three unequal, oblique inland ridges separated by lower saddles.
  ridge=max(31*lobe(x,y,-5,-74,66,81,-.30),38*lobe(x,y,-3,83,68,70,.28),28*lobe(x,y,-24,174,42,48,-.24))
  # Two rock noses and a lowered inlet: no repeated uniform extrusions.
  shoulder=7*lobe(x,y,-92,-72,30,34,.20)+9*lobe(x,y,-69,154,30,35,-.3)
  cove=-3.2*lobe(x,y,-52,-3,38,39,.15)-2.5*lobe(x,y,-69,113,26,22,-.1)
  if not name.startswith('Mainland'):ridge=0
  dz=(ridge+shoulder+cove)*sitefade*seamfade*wetfade
  dx=(-5*lobe(x,y,-94,-72,30,38,.2)-6*lobe(x,y,-74,160,26,35,-.3)+3*lobe(x,y,-47,0,30,38))*smooth(d/18)*seamfade*wetfade
  new[i,0]+=dx;new[i,2]+=dz
 assert all(np.array_equal(new[i],v[i]) for i in locked)
 t=np.array(obj['triangles']);before=np.cross(v[t[:,1],:2]-v[t[:,0],:2],v[t[:,2],:2]-v[t[:,0],:2]);after=np.cross(new[t[:,1],:2]-new[t[:,0],:2],new[t[:,2],:2]-new[t[:,0],:2]);mask=abs(before)>1e-5
 assert np.all(before[mask]*after[mask]>0),(name,'XY fold')
 delta=np.linalg.norm(new-v,axis=1);ids=np.where(delta>1e-6)[0].tolist()
 out[name]=dict(vertices=new.tolist(),frozen_vertices=sorted(locked),changed_vertices=ids,max_displacement_m=float(max(delta)),minimum_nonvertical_XY_area_ratio=float(np.min(abs(after[mask]/before[mask]))) if mask.any() else None)
 all_changed.extend((name,i) for i in ids)
plan=dict(label='33a',scope='Author unequal real right-coast noses, low inlets and three setback inland ridges on current26b native topology. Full conservative house pad and every paving-cap intersecting source face preserved. Trees/scatter refit at runtime. Not art or full20reference acceptance; production unchanged.',source=native['source'],source_sha256=native['source_sha256'],source_intake_sha256=sha(R/'captures/rightcoast33-native-intake.json'),basis_run=prior.name,origin=layout['origin'],occupied_region=mapping(occupied),frozen_face_region=mapping(frozen),occupied_definition='Nine conservative authored full pads plus all922 paving solid cap projections, 0.20m buffer. All original polygons intersecting this are frozen in full; actual asset footprint containment verified independently.',objects=out,changed_vertex_count=len(all_changed),design='Three unequal oblique inland height lobes31/38/28m additive maximum before site/seam fades; two seaward noses and two low coves. Original mainland seam and submerged bottom retained. Authored design coordinates, not inferred original geography.')
p=R/'captures/rightcoast33a-design-plan.json'
if p.exists():
 backup=R/'captures/rightcoast33a-preflight-design-before-rock-refinement.json';assert not backup.exists()
 p.rename(backup)
plan['preflight_revision']='Keep original low independent rock shoulders low: inland ridge addition applies to main mainland shell only; source-independent rocks receive only coast nose/cove field.'
p.write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps(dict(changed=len(all_changed),parts=[dict(name=k,changed=len(v['changed_vertices']),max_m=v['max_displacement_m'],xy_ratio=v['minimum_nonvertical_XY_area_ratio']) for k,v in out.items()]),indent=2))

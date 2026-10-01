"""Actual channel cross-sections and independent complete-scene building support."""
import json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/scratch/a29d03198654/Aether');D=R/'source-assets/lake-cirque54/v1'
sys.path.insert(0,str(D.parent/'intake'));import land_support as land
p=json.load(open(D/'cirque54-payload.json'))['mountains'][0];a=json.load(open(D/'authoring-surface.json'))
def tree(ff):return BVHTree.FromPolygons([Vector(v) for v in ff],[(i,i+1,i+2) for i in range(0,len(ff),3)],all_triangles=True)
def h(t,x,z):
 v,_,_,_=t.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
 return v.y if v is not None else None
body=tree(next(c['vertices'] for c in p['components'] if c['name']=='upper_cirque_mass'))
new=tree([v for c in p['components'] if c['name']!='rock_body' for v in c['vertices']])
sections=[]
for label,line in a['channels'].items():
 for i,(x,y,z,width) in enumerate(line):
  before=line[max(0,i-1)];after=line[min(len(line)-1,i+1)];dx=after[0]-before[0];dz=after[2]-before[2];ll=math.hypot(dx,dz);nx=-dz/ll;nz=dx/ll
  center=h(body,x,z);banks=[h(body,x+sign*width*nx,z+sign*width*nz) for sign in [-1,1]]
  sections.append({'channel':label,'control_index':i,'center_xz':[x,z],'actual_rock_center_y':center,'actual_rock_bank_ys':banks,'incision_below_lower_bank_m':min(banks)-center if all(b is not None for b in banks) else None,'original_land_at_center_y':land.height(x,z),'actual_rock_visible_above_saved_land_m':center-land.height(x,z)})
runtimepath=R/'cloud-evidence/rim53d-west-verify-v2-20261001T064631Z-OrTCQY/verify-report-west53-v2.json';runtime=json.load(open(runtimepath));rows=[]
for old in runtime['runtime_support']['mountain_building_rows']:
 if old['kind']!='buildings':continue
 x,z=old['x'],old['z'];current,owner=land.highest(x,z);added=h(new,x,z);candidate=max(current,added) if added is not None else current
 rows.append({'x':x,'z':z,'actual_saved53_runtime_y':old['physics_y'],'full_intake_support_y':current,'full_intake_owner':owner,'candidate_support_y':candidate,'intake_vs_actual_runtime_error_m':abs(current-old['physics_y']),'new_source_support_change_m':candidate-current})
report={'channel_sections':sections,'channel_all_control_centers_have_both_higher_banks':all(s['incision_below_lower_bank_m'] is not None and s['incision_below_lower_bank_m']>1 for s in sections),'full_building_probe_count':len(rows),'actual_saved53_runtime_report':str(runtimepath.relative_to(R)),'runtime_report_sha256':hashlib.sha256(runtimepath.read_bytes()).hexdigest(),'full_intake_vs_actual_physics_max_error_m':max(r['intake_vs_actual_runtime_error_m'] for r in rows),'building_candidate_support_change_max_m':max(r['new_source_support_change_m'] for r in rows),'building_rows':rows,'scope':'Offline independent geometry cross-check against171 existing real saved53west physics rays; not a new54 engine acceptance run.'}
json.dump(report,open(D/'channel-and-full-building-check.json','w'),indent=2)
print('CHANNELS',[(s['channel'],s['control_index'],s['incision_below_lower_bank_m']) for s in sections],flush=True)
print('FULL_BUILDING',len(rows),report['full_intake_vs_actual_physics_max_error_m'],report['building_candidate_support_change_max_m'],flush=True)
assert len(rows)==171 and report['full_intake_vs_actual_physics_max_error_m']<.03 and report['building_candidate_support_change_max_m']==0
# Missing outer bank at an open outlet remains an explicit diagnostic, not a passed closed-basin claim.

"""Explicit layout adjustment after frozenstatic01 actual-camera diagnostic."""
import copy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
original=json.loads((P/'control-plan58c.json').read_text());plan=copy.deepcopy(original);lookup={r['id']:r for r in plan['controls']};old={r['id']:r for r in original['controls']}
changes={
 'L01':dict(center=[3050,515,3740],size=[820,520,910]),
 'L02':dict(center=[3280,450,4130],size=[950,610,920]),
 'L03':dict(size=[1000,540,940]),
 'L04':dict(size=[950,610,930]),
 'L05':dict(center=[3580,500,3520],size=[1070,500,1100]),
 'L06':dict(size=[1070,530,1010]),
 'L07':dict(size=[990,510,850]),
 'L08':dict(size=[1090,540,950]),
 'L09':dict(size=[1000,560,1060]),
 'P01':dict(center=[3180,805,3697],size=[360,300,345]),
 'P02':dict(center=[3720,835,4110],size=[440,340,385]),
 'P03':dict(center=[4270,850,4160],size=[410,330,365]),
 'P04':dict(size=[365,260,305]),
 'P05':dict(center=[4270,800,2850],size=[365,275,310]),
 'P06':dict(size=[295,220,270]),
}
# Mediums inherit parent displacement, with explicit shoulder-specific changes.
# Wide/low shoulders are moved to visible lips; no request that every rear fold
# be visible from this oneview. Top/back views still need independent validation.
for n,c in changes.items():
 if 'center'in c:lookup[n]['center_godot_world_xyz_m']=c['center']
 if 'size'in c:lookup[n]['design_extent_xyz_m']=c['size']
for r in plan['controls']:
 parent=r['parent_form']
 if parent:
  delta=[a-b for a,b in zip(lookup[parent]['center_godot_world_xyz_m'],old[parent]['center_godot_world_xyz_m'])]
  r['center_godot_world_xyz_m']=[a+b for a,b in zip(r['center_godot_world_xyz_m'],delta)]
# Explicit additional medium offsets relative to their already translated positions.
more={'M02':([0,-85,0],[270,240,190]),'M07':([0,-30,0],None),'M12':([0,-30,0],None),'M13':([0,-45,0],None),'M15':([0,-45,0],None),'M01':([60,45,45],None),'M03':([190,160,-115],[220,180,190]),
      'M04':([0,35,-25],[280,205,235]),'M05':([0,50,40],None),
      'M06':([35,40,-10],None),'M08':([-60,65,-45],None),
      'M09':([-25,65,-20],None),'M10':([-100,70,-70],None),
      'M14':([-45,70,-15],None),'M18':([0,55,-20],None)}
for n,(delta,size) in more.items():
 lookup[n]['center_godot_world_xyz_m']=[a+b for a,b in zip(lookup[n]['center_godot_world_xyz_m'],delta)]
 if size:lookup[n]['design_extent_xyz_m']=size
 # Preserve each small fold's attached relative position.
 for r in plan['controls']:
  if r['parent_form']==n:r['center_godot_world_xyz_m']=[a+b for a,b in zip(r['center_godot_world_xyz_m'],delta)]
# Lower localizededgechanges into their actualparent mass by35m. This is
# geometric connection, not an altered supportthreshold. Two primarylips stay.
for r in plan['controls']:
 if r['role']=='small_edge_fold' and r['id'] not in ('S23','S24'):
  r['center_godot_world_xyz_m'][1]-=35
for r in plan['controls']:
 x,y,z=r['center_godot_world_xyz_m'];r['camera_relative_right_m']=(x-3000)*.6853647232+(z-4300)*.7281999588;r['camera_horizontal_depth_m']=(x-3000)*.7281999588-(z-4300)*.6853647232
log=[]
for r in plan['controls']:
 before=old[r['id']]
 if r['center_godot_world_xyz_m']!=before['center_godot_world_xyz_m'] or r['design_extent_xyz_m']!=before['design_extent_xyz_m']:
  log.append(dict(id=r['id'],original_center=before['center_godot_world_xyz_m'],new_center=r['center_godot_world_xyz_m'],original_extent=before['design_extent_xyz_m'],new_extent=r['design_extent_xyz_m']))
plan['status']='C static05 authoring layout after actual-camera static01; native prototype pending'
plan['accepted_plan_sha256']=hashlib.sha256((P/'control-plan58c.json').read_bytes()).hexdigest();plan['projection_driven_changes']=log
(P/'authoring-plan58c.json').write_text(json.dumps(plan,indent=2)+'\n');print('Explicit adjusted controls:',len(log))

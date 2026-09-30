"""Independent read-only evidence and production identity audit after native run completion."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(r'E:\FeiTing')
RUN=ROOT/'captures/validation_runs/17e-native-integration-20260908T060301Z-07dc7a9c264c45aab408ab67177a7dfd'
CAND=ROOT/'captures/validation_runs/foreground-17e-20260908T055006Z-348ac27ec16f49c6bc196accd90eba32'
def js(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=js(RUN/'manifest.json');assert m['status']=='passed' and m['passed'] is True
assert len(m['stages'])==12 and all(x['passed'] for x in m['stages'])
report={'run':str(RUN),'run_status':m['status'],'run_manifest_sha256':sha(RUN/'manifest.json'),'completed_utc':m['completed_utc'],'scope':'Read-only identity, frozen-diff, bound reports and screenshot parity audit; no rendering, engine launch or production writes. Full visual goal remains incomplete.','artifacts':{},'assets':{},'stages':m['stages']}
for key,item in m['artifacts'].items():
 actual=sha(RUN/key);assert actual==item['sha256'];report['artifacts'][key]={'sha256':actual,'matches_manifest':True}
frozen=js(RUN/'inputs.json')['files'];before=js(RUN/'preparation-inputs.json')['files'];changes=js(RUN/'preparation-changes.json');diff={k for k in before if k not in frozen or before[k]['sha256']!=frozen[k]['sha256']};assert diff==set(changes)
new_noncache=[k for k in frozen if k not in before and not k.startswith('res://.godot/')];assert not new_noncache
report['production_changes']=sorted(diff);report['production_input_scope_count']=len(before)
expected={'res://assets/asset_catalog.json','res://assets/cliff_kit.json','res://assets/scatter/Grounded_rock_0_-1.res'}
items=js(CAND/'study-inputs/manifest.json');kit={x['name']:x for x in js(ROOT/'assets/cliff_kit.json')}
for item in items:
 name=item['name'];entry={}
 for suffix,key,field in [('.glb','assets/models','glb_sha256'),('.blend','blender/cliff_kit','blend_sha256')]:
  rel=key+'/'+name+suffix;path=ROOT/rel;actual=sha(path);assert actual==item[field] and actual==frozen['res://'+rel]['sha256'];expected.add('res://'+rel)
  backup=RUN/'source-backup'/rel;assert sha(backup)==before['res://'+rel]['sha256'];entry[suffix]={'production_sha256':actual,'matches_reviewed_candidate':True,'backup_matches_original':True}
 for folder in ('meshes','collision'):
  rel='assets/'+folder+'/'+name+'.res';expected.add('res://'+rel);assert sha(ROOT/rel)==frozen['res://'+rel]['sha256'];entry[folder+'_sha256']=sha(ROOT/rel)
 prefab='scenes/prefabs/'+name+'.tscn';text=(ROOT/prefab).read_text();assert 'res://assets/models/'+name+'.glb' in text and 'res://assets/collision/'+name+'.res' in text;assert sha(ROOT/prefab)==before['res://'+prefab]['sha256'];entry['prefab_unchanged_and_references_current_model_collider']=True
 assert kit[name]['vertices']==item['vertices'] and kit[name]['faces']==item['triangles'] and abs(kit[name]['volume_m3']-item['volume_m3'])<1e-5
 entry['kit_counts_match_candidate']=True;report['assets'][name]=entry
assert diff==expected
preserved={}
for prefix in ('res://scenes/world/','res://scenes/terrain/','res://assets/scatter/'):
 keys=[k for k in before if k.startswith(prefix) and k!='res://assets/scatter/Grounded_rock_0_-1.res'];assert all(k in frozen and frozen[k]['sha256']==before[k]['sha256'] for k in keys)
 # Re-read native scene and foliage outputs; avoid a competing full-resource scan.
 for k in keys:
  if prefix!='res://assets/scatter/':assert sha(ROOT/k.removeprefix('res://'))==frozen[k]['sha256']
 preserved[prefix]={'count':len(keys),'frozen_sha_unchanged':True,'current_sha_recomputed':prefix!='res://assets/scatter/'}
report['preserved_groups']=preserved
report['image_parity']={}
for view in ('opening','cliff-side','cliff-back'):
 path='images/'+view+'.png';a=sha(RUN/path);b=sha(CAND/path)
 native=np.array(Image.open(RUN/path).convert('RGB')).astype(int);candidate=np.array(Image.open(CAND/path).convert('RGB')).astype(int);delta=np.abs(native-candidate);mask=delta.any(axis=2);ys,xs=np.where(mask)
 report['image_parity'][view]={'sha256':a,'candidate_sha256':b,'byte_identical_to_candidate':a==b,'changed_pixels':int(mask.sum()),'maximum_channel_difference':int(delta.max()),'bbox_inclusive':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None,'changed_pixels_y_ge_300':int(mask[300:].sum())}

report['image_parity']['reverse']={'sha256':sha(RUN/'images/reverse.png'),'candidate_comparison':'Candidate 17e had no reverse screenshot; inspected natively without claiming equality.'}
gate=js(RUN/'preparation/round-17e-projected-surface-gate.json');assert gate['passed'] and m['section_surface_gate']['passed'];report['surface_gate']={}
assert sha(RUN/'preparation/round-17e-projected-surface-gate.json')==m['section_surface_gate']['report_sha256']
for entry in gate['assets']:
 rel='res://assets/models/'+entry['name']+'.glb';assert entry['sha256']==frozen[rel]['sha256']==sha(ROOT/rel.removeprefix('res://'));report['surface_gate'][entry['name']]={'sha256':entry['sha256'],'current_and_frozen_and_gate_match':True}
reports={}
for path in RUN.rglob('*.json'):
 if path.parent.name=='reports':reports[path.relative_to(RUN).as_posix()]=js(path)
for key,data in reports.items():
 assert data['passed'] is True
 if 'provenance' in data:
  assert data['provenance']['run_id']==m['run_id']
  for k,v in data['provenance'].get('sha256',{}).items():assert frozen[k]['sha256']==v
 for check in data.get('checks',[]):assert check['passed'] is True
assert len(reports['reports/game-test.json']['checks'])==36
assert reports['reports/cliff-tour-test.json']['waypoints_reached']==6
assert len(reports['reports/cliffs-contact.json']['checks'])==21
assert reports['reports/cliff-ground-rims.json']['samples']==4472
assert reports['reports/road-surfaces.json']['samples']==40642
assert len(reports['reports/geology.json']['assets'])==18
for asset in reports['reports/geology.json']['assets']:
 assert asset['passed'] is True and asset['glb_sha256']==sha(ROOT/'assets/models'/(asset['name']+'.glb'))
report['bound_report_data']=reports
report['changed_scatter']={'path':'res://assets/scatter/Grounded_rock_0_-1.res','before_sha256':before['res://assets/scatter/Grounded_rock_0_-1.res']['sha256'],'frozen_sha256':frozen['res://assets/scatter/Grounded_rock_0_-1.res']['sha256'],'current_sha256':sha(ROOT/'assets/scatter/Grounded_rock_0_-1.res')}
assert report['changed_scatter']['current_sha256']==report['changed_scatter']['frozen_sha256']
report['refresh_log']=(RUN/'refresh-selected-cliffs.log').read_text()
out=ROOT/'reviews/round-17e-native-integration-independent-audit.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),'artifact_count':len(report['artifacts']),'production_changes':len(diff),'preserved_groups':preserved,'report_paths':list(reports),'image_parity':report['image_parity']},indent=2))

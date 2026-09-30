from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
runs={'29a':'lantern-island-29a-20260908T164954Z-61a6c0bfbae148aab6c70a201c5b1ec9','29b':'lantern-island-29b-20260908T170220Z-518110b4cf274a47a5271790baa41f41'}
for label,dirname in runs.items():
 run=R/'captures/validation_runs'/dirname;m=json.loads((run/'manifest.json').read_text());assert m['status']=='passed' and m['passed']
 for name,d in m['artifacts'].items():assert sha(run/name)==d['sha256'],name
 preservation=json.loads((run/'actual-site-preservation.json').read_text());assert preservation['passed']
 views=[]
 for name in ['night-reference','day-reference','day-d-front','day-d-back','day-c-front']:
  p=run/'images'/(name+'.png');s=Path(str(p)+'.json');d=json.loads(s.read_text());assert d['world_sha256']==sha(R/'scenes/world/World.tscn')
  views.append({'name':name,'path':str(p.relative_to(R)),'png_sha256':sha(p),'sidecar_sha256':sha(s),'root_directly_viewed':True,'camera':d['camera']})
 out={'run_id':m['run_id'],'manifest_sha256':sha(run/'manifest.json'),'terminal_passed':True,'binding_count':len(m['artifacts']),'all_bound_hashes_match':True,'actual_site_preservation':preservation,'root_views':views,'independent_review':f'reviews/round-{label}-island-independent-review.md','visual_accepted':False,'production_installed':False,'full_goal_status':'active'}
 p=R/f'reviews/round-{label}-root-evidence.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(label,len(m['artifacts']),'bindings verified')

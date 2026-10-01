from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[2];project=root/'candidates/round40-exclusive-20260930/project';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
runs={m:Path((root.parent/'tools-feiting'/('observation60-'+m+'-last.txt')).read_text().strip()) for m in ['scope','capture','flight']}
proofs={}
for mode,run in runs.items():
 p=run/'process-report.json';j=json.loads(p.read_text());assert j['status']=='finished' and j['passed'] and j['child_exit']==0
 proofs[mode]={'directory':str(run),'process_report':str(p),'sha256':sha(p),'elapsed_seconds':j['elapsed_seconds'],'peak_rss_kib':j['peak_rss_kib']}
files=[project/'scenes/candidate60-observation/Game60Observation.tscn',project/'scripts/game60_observation.gd',project/'assets/observation60/cloud_observation_pose.json',project/'scenes/candidate56-coast/Game56Coast.tscn']
record={'stage':'bounded_native_observation_complete','native_scope_passed':True,'three_pose_capture_passed':True,'ordinary_input_flight_passed':True,'candidate_sha256':sha(files[0]),'input_files':{str(p):sha(p) for p in files},'proofs':proofs,'flight_metres':12.2297825068235,'native_world_base':'Game56Coast -> Game55Observation -> Game53dWest -> Game51b','cloud52f_or58_merged':False,'default_changed':False,'visual_acceptance':False,'hardware_gpu_acceptance':False,'full_goal_passed':False,'independent_review_scope':'Parent viewed59B main study and allowed limited switchable composition candidate, not independent full60/GOAL acceptance'}
(project/'scenes/candidate60-observation/verified60.json').write_text(json.dumps(record,indent=2)+'\n')
print('Recorded verified60 native scope, 10 captures and ordinary flight')

#!/usr/bin/env python3
import argparse,hashlib,json,os,resource,shutil,subprocess,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
H=Path(__file__).resolve().parent;R=H.parents[1];T=R.parent/'tools-feiting';P=R/'candidates/round40-exclusive-20260930/project'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,v):
 q=p.with_name(p.name+'.tmp');q.write_text(json.dumps(v,indent=2)+'\n');q.replace(p)
ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['scope','capture','flight']);ap.add_argument('--parse',action='store_true');a=ap.parse_args()
if not a.parse and not os.environ.get('DISPLAY'):raise SystemExit('Use existing cloud desktop renderer terminal')
names={'scope':'verify_scope60.gd','capture':'observe_saved60.gd','flight':'verify_flight60.gd'};script=H/names[a.mode]
out=Path(tempfile.mkdtemp(prefix='observation60-'+a.mode+('-parse' if a.parse else '')+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-'),dir=R/'cloud-evidence'));print(out,flush=True)
(T/('observation60-'+a.mode+('-parse' if a.parse else '')+'-last.txt')).write_text(str(out)+'\n');(out/'inputs').mkdir()
inputs=[Path(__file__),script,P/'project.godot',P/'scenes/candidate60-observation/Game60Observation.tscn',P/'scenes/candidate56-coast/Game56Coast.tscn',P/'scenes/candidate55-observation/Game55Observation.tscn',P/'scenes/candidate53d-west/Game53dWest.tscn',P/'scripts/game60_observation.gd',P/'scripts/game55_observation.gd',P/'assets/observation60/cloud_observation_pose.json',P/'assets/observation55/lake_observation_poses.json',P/'tools/reflection51b_saved_audit.gd',P/'tools/observe_near_ship53west_v2.gd',P/'tools/observe_camera_ship53west_c.gd']
inputs += list((P/'assets/coast56').glob('*'))
inputs += [P/'scripts'/n for n in ['game.gd','game42b.gd','airship_body.gd','open_world.gd','lake_reflection51b.gd']]
env=os.environ.copy();env['OBSERVATION60_OUT']=str(out);env['OBSERVATION60_INPUTS']=str(out/'input-sha256.json')
if a.mode!='scope' and not a.parse:
 scope=Path((T/'observation60-scope-last.txt').read_text().strip())/'process-report.json';proof=json.loads(scope.read_text())
 if not proof.get('passed') or proof.get('status')!='finished':raise SystemExit('Completed exact60 native scope proof required')
 inputs.append(scope);env['OBSERVATION60_SCOPE']=str(scope)
 # Revalidate every pinned input in the actual completed native scope proof.
 for path,value in json.loads((scope.parent/'input-sha256.json').read_text()).items():
  if sha(path)!=value:raise SystemExit('Scope dependency changed: '+path)
user=Path(tempfile.mkdtemp(prefix='observation60-'+a.mode+'-',dir=T))
for k,n in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
 d=user/n;d.mkdir();env[k]=str(d)
hashes={str(p):sha(p) for p in inputs if p.is_file()};atomic(out/'input-sha256.json',hashes)
for i,p in enumerate(inputs):
 if p.is_file() and p.suffix in ['.py','.gd','.json']:shutil.copy2(p,out/'inputs'/('%02d-'%i+p.name))
cmd=[str(T/'Godot_v4.5.1-stable_linux.x86_64'),'--path',str(P)]
cmd+=['--headless','--check-only'] if a.parse else ['--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync']
cmd+=['--script',str(script)]
if not a.parse and a.mode!='scope':cmd+=['--',f'--output-dir={out}/images']
atomic(out/'process-report.json',{'status':'running','passed':False,'mode':a.mode,'parse':a.parse,'command':cmd});start=time.monotonic();stop=None
with (out/'stdout.log').open('w') as f,(out/'stderr.log').open('w') as e:
 c=subprocess.Popen(cmd,env=env,cwd=R,stdout=f,stderr=e);(out/'child.pid').write_text(str(c.pid)+'\n')
 while True:
  try:code=c.wait(timeout=1);break
  except subprocess.TimeoutExpired:pass
  log=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace')
  bad=[x for x in log.splitlines() if x.startswith(('ERROR:','SCRIPT ERROR:'))]
  if bad or time.monotonic()-start>(60 if a.parse else 420):
   stop=bad or ['timeout'];c.terminate()
   try:code=c.wait(timeout=10)
   except subprocess.TimeoutExpired:c.kill();code=c.wait()
   break
log=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace');errors=[x for x in log.splitlines() if x.startswith(('ERROR:','SCRIPT ERROR:','FAIL ')) or 'leaked' in x.lower()]
unchanged=all(sha(p)==v for p,v in hashes.items());report={};gate_errors=[];pngs=list((out/'images').glob('*.png'))
if not a.parse:
 try:
  report_path=out/'scope-report.json' if a.mode=='scope' else out/'images'/('report60.json' if a.mode=='capture' else 'player-flight-report.json')
  report=json.loads(report_path.read_text())
  if a.mode in ['scope','capture'] and not report.get('passed_provisional'):gate_errors.append('Native provisional gate incomplete/failed')
  if a.mode=='capture' and (len(report.get('poses',[]))!=3 or len(pngs)!=10):gate_errors.append('Expected3 poses/10 actual captures')
  if a.mode=='flight' and (not report.get('complete') or not report.get('actual_player_input_flight_passed') or len(pngs)!=3):gate_errors.append('Flight incomplete/failed')
  if a.mode=='capture':
   from PIL import Image
   import numpy as np
   for channel in ['main','reflection']:
    x=np.array(Image.open(out/f'images/1216--saved60--{channel}.png').convert('RGBA'));y=np.array(Image.open(out/f'images/1216--enabled-repeat--{channel}.png').convert('RGBA'))
    if not np.array_equal(x,y):gate_errors.append('Actual repeated1216 pixels differ '+channel)
 except (OSError,ValueError,KeyError) as exc:gate_errors.append(str(exc))
ok=code==0 and unchanged and not stop and not errors and not gate_errors
row={'status':'finished','mode':a.mode,'parse':a.parse,'passed':ok,'child_exit':code,'errors':errors,'gate_errors':gate_errors,'inputs_unchanged':unchanged,'elapsed_seconds':time.monotonic()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'stopped_for':stop,'visual_acceptance':False,'hardware_gpu_acceptance':False,'report':str(report_path) if not a.parse else None};atomic(out/'process-report.json',row);(out/'wrapper.exit-code.txt').write_text('0\n' if ok else '1\n');print(json.dumps(row));raise SystemExit(0 if ok else 1)

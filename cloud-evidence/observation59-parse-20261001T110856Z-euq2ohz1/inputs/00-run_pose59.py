#!/usr/bin/env python3
"""Read-only bounded pose experiment. Inputs are namespaced; terminal gates are fresh."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile,time,resource
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;R=P.parents[1];T=R.parent/'tools-feiting';PROJECT=R/'candidates/round40-exclusive-20260930/project'
SCENE=PROJECT/'scenes/candidate52f/Game52f.tscn';SHA='201f667747406b1414a298a6b5433ac1550d8b447dff8f6cb6823d94d2acbd7c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,v):
 q=p.with_name(p.name+'.tmp');q.write_text(json.dumps(v,indent=2)+'\n');q.replace(p)
ap=argparse.ArgumentParser();ap.add_argument('--renderer',action='store_true');a=ap.parse_args()
if a.renderer and not os.environ.get('DISPLAY'):raise SystemExit('Existing cloud desktop renderer terminal required')
assert sha(SCENE)==SHA
out=Path(tempfile.mkdtemp(prefix='observation59-'+('renderer' if a.renderer else 'parse')+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-'),dir=R/'cloud-evidence'))
(T/'observation59-last.txt').write_text(str(out)+'\n');(out/'inputs').mkdir()
gatefile=PROJECT/'scenes/candidate52f/verified-saved-52f.json';gate=json.loads(gatefile.read_text());proof=Path(gate['process_report_path'])
assert gate['candidate_sha256']==SHA and gate['runner_final_gate_passed'] and sha(proof)==gate['process_report_sha256']
inputs=[Path(__file__),P/'observe_pose59.gd',P/'proposal.json',SCENE,PROJECT/'project.godot',gatefile,proof,PROJECT/'tools/observe_near_ship53west_v2.gd',R/'ref/1216.png']
inputs += [PROJECT/'scripts'/n for n in ['game.gd','game42b.gd','airship_body.gd','open_world.gd','lake_reflection51b.gd']]
hashes={str(p):sha(p) for p in inputs};atomic(out/'input-sha256.json',hashes)
for i,p in enumerate(inputs):
 if p.suffix in ['.py','.gd','.json']:shutil.copy2(p,out/'inputs'/('%02d-'%i+p.name))
env=os.environ.copy();env['POSE59_INPUT_MANIFEST']=str(out/'input-sha256.json')
for k,n in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:env[k]=str(T/'userdata'/n)
cmd=[str(T/'Godot_v4.5.1-stable_linux.x86_64'),'--path',str(PROJECT)]
cmd+=['--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync'] if a.renderer else ['--headless','--check-only']
cmd+=['--script',str(P/'observe_pose59.gd')]
if a.renderer:cmd+=['--',f'--output-dir={out}/images']
atomic(out/'process-report.json',{'status':'running','passed':False,'command':cmd,'started_utc':datetime.now(timezone.utc).isoformat(),'renderer':a.renderer})
start=time.monotonic();stopped=None
with (out/'stdout.log').open('w') as f,(out/'stderr.log').open('w') as e:
 c=subprocess.Popen(cmd,env=env,cwd=R,stdout=f,stderr=e);(out/'child.pid').write_text(str(c.pid)+'\n')
 while True:
  try:code=c.wait(timeout=1);break
  except subprocess.TimeoutExpired:pass
  logs=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace')
  bad=[x for x in logs.splitlines() if x.startswith(('ERROR:','SCRIPT ERROR:'))]
  if bad or time.monotonic()-start>(420 if a.renderer else 60):
   stopped=bad or ['bounded timeout'];c.terminate()
   try:code=c.wait(timeout=10)
   except subprocess.TimeoutExpired:c.kill();code=c.wait()
   break
logs=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace');errors=[x for x in logs.splitlines() if x.startswith(('ERROR:','SCRIPT ERROR:','FAIL ')) or 'leaked' in x.lower()]
unchanged=all(sha(p)==v for p,v in hashes.items());report={};pngs=[];gate_errors=[]
if a.renderer:
 try:
  report=json.loads((out/'images/report59.json').read_text());pngs=list((out/'images').glob('*.png'))
  if not report.get('passed_provisional') or len(report.get('captures',[]))!=3 or len(pngs)!=6:gate_errors.append('Incomplete native report/capture count')
  from PIL import Image
  import numpy as np
  for tag in ['main','reflection']:
   original=np.array(Image.open(out/f'images/1216--A-original--{tag}.png').convert('RGBA'));restored=np.array(Image.open(out/f'images/1216--A2-restored--{tag}.png').convert('RGBA'))
   if not np.array_equal(original,restored):gate_errors.append('Actual A/A2 pixel mismatch '+tag)
  if np.array_equal(np.array(Image.open(out/'images/1216--A-original--main.png')),np.array(Image.open(out/'images/1216--B-side-study--main.png'))):gate_errors.append('B main has no visible change')
 except (OSError,ValueError,KeyError) as exc:gate_errors.append(str(exc))
ok=code==0 and unchanged and not errors and not stopped and not gate_errors
row={'status':'finished','passed':ok,'child_exit':code,'elapsed_seconds':time.monotonic()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'stopped_for':stopped,'errors':errors,'gate_errors':gate_errors,'inputs_unchanged':unchanged,'renderer':a.renderer,'visual_acceptance':False,'hardware_gpu_acceptance':False,'actual_flight_tested':False,'images':[str(p) for p in pngs]}
atomic(out/'process-report.json',row);(out/'wrapper.exit-code.txt').write_text('0\n' if ok else '1\n');print(out);print(json.dumps(row));raise SystemExit(0 if ok else 1)

"""Scheduled C source build + freshreadback, CPU2,60s/1.5GiB hard gates."""
import datetime,hashlib,json,os,resource,shutil,subprocess,sys,tempfile,time,traceback
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[3];A=P.parents[1];BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,obj):
 temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(obj,indent=2)+'\n');temp.replace(path)
assert not(P/'cloud_bank58c_controls.blend').exists(),'Csource alreadyexists; choose anewcandidate, neveroverwrite'
inputs=[P/f for f in ['build58c.py','verify58c.py','run_source58c.py','native_geometry58c.py','geometry58c.py','triangle_checks58c.py','authoring-plan58c.json','native-control-input58c.json','control-projection58c.json','static-support58c.json','thick-join-input58c.json']]
inputs += [A/'native-intake58.json',A/'revision-a-freeze.json',A/'revision-b-complete-freeze-20261001T1205Z.json',A/'revision-b/recovery-03/triangle_pairs58b.py',P.parent/'failed-controls-freeze58c.json',P.parent/'recovery-01'/'failed-genus-freeze58c.json']
protected={}
for freeze in [A/'revision-a-freeze.json',A/'revision-b-complete-freeze-20261001T1205Z.json',P.parent/'failed-controls-freeze58c.json',P.parent/'recovery-01'/'failed-genus-freeze58c.json']:
 data=json.loads(freeze.read_text())
 for name,r in data['files'].items():protected[name]=r['sha256'] if isinstance(r,dict) else r
assert all(sha(ROOT/f)==s for f,s in protected.items()),'FrozenA/B files changedbeforeC; stop'
manifest={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in inputs}
write(P/'build-input-freeze58c.json',dict(files=manifest,protected_A_B_files=len(protected),world_loaded=False))
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=Path(tempfile.mkdtemp(prefix=f'cloudbank58c-source-{stamp}-',dir=ROOT/'cloud-evidence'))
for name in ['inputs','outputs','blender-config','xdg-cache','xdg-config','xdg-data']:(run/name).mkdir()
for p in inputs:shutil.copy2(p,run/'inputs'/p.name)
shutil.copy2(P/'build-input-freeze58c.json',run/'inputs'/'manifest.json')
state=dict(state='running',complete=False,run_id=run.name,started_utc=stamp,commands=[],world_loaded=False,rendered=False,visual_acceptance=False)
write(run/'result.json',state);print(run,flush=True)
env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
start=time.monotonic();peak=0;reason=None;error=None;child=None;complete=False
try:
 for i,script in enumerate(['build58c.py','verify58c.py']):
  cmd=[str(BLENDER),'-b','-t','2','--python-exit-code','1','--python',str(P/script)];row=dict(script=script,argv=cmd,state='running',complete=False);state['commands'].append(row);write(run/'result.json',state)
  with (run/f'{i}-stdout.log').open('wb') as out,(run/f'{i}-stderr.log').open('wb') as err:
   child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err);(run/f'{i}-child.pid').write_text(str(child.pid)+'\n')
   while child.poll() is None:
    elapsed=time.monotonic()-start;current=None;proc=Path('/proc')/str(child.pid)/'status'
    if proc.exists():
     line=next((s for s in proc.read_text().splitlines() if s.startswith('VmRSS:')),None)
     if line:current=int(line.split()[1]);peak=max(peak,current)
    op=None;stage=P/('build-stage58c.json' if i==0 else 'verify-stage58c.json')
    if stage.exists():
     try:op=json.loads(stage.read_text()).get('current_operation')
     except json.JSONDecodeError:op='stageupdatepending'
    write(run/'live-resource.json',dict(state='running',complete=False,script=script,operation=op,elapsed_seconds=elapsed,current_rss_kib=current,peak_observed_rss_kib=peak))
    if elapsed>60:reason='60secondtotalstagebudget'
    if peak>1572864:reason='1.5GiBRSSbudget'
    if reason:
     child.terminate()
     try:child.wait(timeout=3)
     except subprocess.TimeoutExpired:child.kill();child.wait()
     break
    time.sleep(.25)
   code=child.wait();child=None
  logs=(run/f'{i}-stdout.log').read_text(errors='replace')+'\n'+(run/f'{i}-stderr.log').read_text(errors='replace');hard=[s for s in logs.splitlines() if s.startswith(('Traceback','Error:')) or 'Error: script failed' in s]
  row.update(state='finished',actual_child_exit_code=code,hard_errors=hard,complete=code==0 and not hard and reason is None);(run/f'{i}-child.exit-code.txt').write_text(str(code)+'\n');write(run/'result.json',state)
  if not row['complete']:break
 complete=len(state['commands'])==2 and all(r['complete'] for r in state['commands']) and bool(json.loads((P/'union-fresh-readback58c.json').read_text())['passed'])
except BaseException:
 error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
 if child is not None and child.poll() is None:
  child.terminate()
  try:child.wait(timeout=3)
  except subprocess.TimeoutExpired:child.kill();child.wait()
finally:
 for p in P.glob('*.json'):
  if p.name not in [q.name for q in inputs]:shutil.copy2(p,run/'outputs'/p.name)
 unchanged=all(sha(ROOT/f)==s for f,s in protected.items());inputs_unchanged=all(sha(ROOT/f)==r['sha256'] for f,r in manifest.items());complete=bool(complete and unchanged and inputs_unchanged)
 state.update(state='finished',complete=complete,limit_stop_reason=reason,error=error,wall_seconds=time.monotonic()-start,peak_observed_rss_kib=peak,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,protected_A_B_unchanged=unchanged,frozen_inputs_unchanged=inputs_unchanged,
 source_files={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in P.glob('*.blend')})
 write(run/'result.json',state);write(run/'terminal-proof.json',dict(run_id=run.name,result_sha256=sha(run/'result.json'),complete=complete));(run/'wrapper.exit-code.txt').write_text(('0'if complete else'1')+'\n')
print(json.dumps(state,indent=2));sys.exit(0 if complete else 1)

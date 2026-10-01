import datetime,hashlib,json,os,resource,shutil,subprocess,sys,tempfile,time,traceback
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[3];R=P.parent/'recovery-01';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=Path(tempfile.mkdtemp(prefix=f'cloudbank58c-read-{stamp}-',dir=ROOT/'cloud-evidence'));(run/'inputs').mkdir();(run/'outputs').mkdir()
inputs=[P/'read_mesh58c.py',Path(__file__),R/'native_geometry58c.py',R/'geometry58c.py',R/'cloud_bank58c_union.blend',R/'failed-genus-freeze58c.json'];manifest={str(p.relative_to(ROOT)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in inputs}
for p in inputs:
 if p.suffix!='.blend':shutil.copy2(p,run/'inputs'/p.name)
(run/'inputs/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
def write(name,obj):
 p=run/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(obj,indent=2)+'\n');t.replace(p)
s=dict(state='running',complete=False,run_id=run.name,world_loaded=False,rendered=False,visual_acceptance=False);write('result.json',s);print(run,flush=True)
env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',BLENDER_USER_CONFIG=str(run/'config'),XDG_CACHE_HOME=str(run/'cache'))
start=time.monotonic();peak=0;reason=None;cmd=[str(ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'),'-b','-t','2','--python-exit-code','1','--python',str(P/'read_mesh58c.py')]
with (run/'stdout.log').open('wb') as out,(run/'stderr.log').open('wb') as err:
 child=subprocess.Popen(cmd,env=env,cwd=ROOT,stdout=out,stderr=err)
 while child.poll() is None:
  proc=Path('/proc')/str(child.pid)/'status';current=None
  if proc.exists():
   line=next((v for v in proc.read_text().splitlines() if v.startswith('VmRSS:')),None)
   if line:current=int(line.split()[1]);peak=max(peak,current)
  elapsed=time.monotonic()-start;write('live-resource.json',dict(complete=False,elapsed_seconds=elapsed,peak_rss_kib=peak,current_rss_kib=current))
  if elapsed>60 or peak>1572864:
   reason='60s or1.5GiBhardlimit';child.terminate()
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:child.kill();child.wait()
   break
  time.sleep(.25)
 code=child.wait()
unchanged=all(sha(ROOT/f)==r['sha256'] for f,r in manifest.items());passed=code==0 and reason is None and unchanged and json.loads((P/'readback58c.json').read_text())['passed']
for p in P.glob('*.json'):shutil.copy2(p,run/'outputs'/p.name)
s.update(state='finished',complete=passed,actual_child_exit_code=code,wall_seconds=time.monotonic()-start,peak_observed_rss_kib=peak,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,limit_stop_reason=reason,inputs_unchanged=unchanged);write('result.json',s);write('terminal-proof.json',dict(result_sha256=sha(run/'result.json'),complete=passed));(run/'wrapper.exit-code.txt').write_text(('0'if passed else'1')+'\n');print(json.dumps(s,indent=2));sys.exit(0 if passed else 1)

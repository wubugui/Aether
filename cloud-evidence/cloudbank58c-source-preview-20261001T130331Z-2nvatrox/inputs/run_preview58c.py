"""Parent-scheduled five-view C source render with live same-process RSS records."""
import argparse,datetime,hashlib,json,os,resource,shutil,struct,subprocess,sys,tempfile,time
from pathlib import Path
P=Path(__file__).resolve().parent;C=P.parent;A=C.parent;ROOT=C.parents[2]
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=C/'recovery-02');args=parser.parse_args();S=args.source.resolve()
assert S==C/'recovery-02'
assert json.loads((S/'union-fresh-readback58c.json').read_text())['passed']
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=Path(tempfile.mkdtemp(prefix=f'cloudbank58c-source-preview-{stamp}-',dir=ROOT/'cloud-evidence'))
for name in ('inputs','images','blender-config','xdg-cache','xdg-config','xdg-data'):(run/name).mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
input_freeze=P/'preview-input-freeze58c.json'
assert input_freeze.exists(),'Freeze exact current preview inputs before starting'
frozen_inputs=json.loads(input_freeze.read_text())
assert all(sha(ROOT/f)==r['sha256'] for f,r in frozen_inputs['files'].items()),'Frozen preview input changed; stop and review'
freeze=json.loads((A/'revision-a-freeze.json').read_text());protected={str(ROOT/f):r['sha256'] for f,r in freeze['files'].items()}
for freeze_path in [A/'revision-b-complete-freeze-20261001T1205Z.json',C/'failed-controls-freeze58c.json',C/'recovery-01'/'failed-genus-freeze58c.json',S/'raw-source-freeze58c.json',C/'preview-01'/'failed-rss-freeze58c.json']:
    frozen=json.loads(freeze_path.read_text())
    protected.update({str(ROOT/f):r['sha256'] for f,r in frozen['files'].items()})
assert all(sha(Path(p))==s for p,s in protected.items()),'Prior frozen evidence changed'
protected.update({str(ROOT/f):r['sha256'] for f,r in frozen_inputs['files'].items()});protected[str(input_freeze)]=sha(input_freeze)
protected.update({str(p):sha(p) for p in [S/'cloud_bank58c_union.blend',*S.glob('*.glb'),ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',ROOT/'candidates/round40-exclusive-20260930/project/project.godot']})
for file in ('union-fresh-readback58c.json','raw-source-freeze58c.json'):shutil.copy2(S/file,run/'inputs'/file)
for file in ('preview58c.py','run_preview58c.py'):shutil.copy2(P/file,run/'inputs'/file)
shutil.copy2(input_freeze,run/'inputs'/input_freeze.name)
(run/'inputs'/'manifest.json').write_text(json.dumps({str(p):dict(sha256=sha(p),bytes=p.stat().st_size) for p in [P/'preview58c.py',S/'union-fresh-readback58c.json',S/'cloud_bank58c_union.blend',BLENDER]},indent=2)+'\n')
cmd=[str(BLENDER),'-b','-t','2','--python-exit-code','1','--python',str(P/'preview58c.py'),'--','--out',str(run/'images')]
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
status=dict(state='running',complete=False,run_id=run.name,started_utc=stamp,argv=cmd,expected_images=5,world_loaded=False,visual_acceptance=False)
(run/'result.json').write_text(json.dumps(status,indent=2)+'\n');print(str(run),flush=True)
start=time.monotonic();reason=None;peak=0;code=99
with (run/'stdout.log').open('wb') as out,(run/'stderr.log').open('wb') as err:
    child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err);(run/'child.pid').write_text(str(child.pid)+'\n')
    while child.poll() is None:
        elapsed=time.monotonic()-start
        proc=Path('/proc')/str(child.pid)/'status';rss=None
        if proc.exists():
            info=proc.read_text();row=next((s for s in info.splitlines() if s.startswith('VmRSS:')),None)
            if row:rss=int(row.split()[1]);peak=max(peak,rss)
        (run/'live-resource.json').write_text(json.dumps(dict(state='running',complete=False,elapsed_seconds=elapsed,current_rss_kib=rss,peak_observed_rss_kib=peak,completed_pngs=len(list((run/'images').glob('*.png')))),indent=2)+'\n')
        if peak>1572864:reason='RSS exceeded the1.5GiB source budget'
        if elapsed>90:reason='90second source preview time limit reached'
        if reason:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait()
            break
        time.sleep(.5)
    code=child.wait()
(run/'child.exit-code.txt').write_text(str(code)+'\n')
after={p:sha(Path(p)) for p in protected};pngs=[]
for p in sorted((run/'images').glob('*.png')):
    raw=p.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',raw[16:24]);pngs.append(dict(name=p.name,width=w,height=h,sha256=sha(p),bytes=len(raw)))
logs=(run/'stdout.log').read_text(errors='replace')+'\n'+(run/'stderr.log').read_text(errors='replace')
errors=[s for s in logs.splitlines() if s.startswith(('Traceback','Error:')) or 'Error: script failed' in s]
success=code==0 and not errors and not reason and after==protected and len(pngs)==5 and all((p['width'],p['height'])==((836,471) if '1216' in p['name'] else (1000,700)) for p in pngs) and json.loads((run/'preview-proof.json').read_text())['passed']
status.update(state='finished',complete=success,child_exit_code=code,limit_stop_reason=reason,hard_errors=errors,protected_unchanged=after==protected,protected_before=protected,protected_after=after,
              images=pngs,wall_seconds=time.monotonic()-start,peak_observed_rss_kib=peak,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,hardware_gpu_acceptance=False)
(run/'result.json').write_text(json.dumps(status,indent=2)+'\n');(run/'terminal-proof.json').write_text(json.dumps(dict(run_id=run.name,result_sha256=sha(run/'result.json'),complete=success),indent=2)+'\n')
(run/'wrapper.exit-code.txt').write_text(('0' if success else '1')+'\n');print(json.dumps({k:v for k,v in status.items() if k not in ['protected_before','protected_after']},indent=2));sys.exit(0 if success else 1)

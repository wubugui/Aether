"""Single parent-scheduled B build + fresh readback,2 threads, no renderer/world.

Input reports are namespaced under inputs/. This run writes running/false before
launch and cannot inherit a terminal status from any input report.
"""
import datetime,hashlib,json,os,resource,shutil,subprocess,sys,tempfile,time,traceback
from pathlib import Path
P=Path(__file__).resolve().parent;A=P.parent;ROOT=A.parents[1]
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=Path(tempfile.mkdtemp(prefix=f'cloudbank58b-source-build-{stamp}-',dir=ROOT/'cloud-evidence'))
for folder in ('inputs','outputs','blender-config','xdg-cache','xdg-config','xdg-data'):(run/folder).mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(P/'cloud_bank58b.blend').exists(),'Existing completed B source is immutable'
input_files=[*P.glob('*.py'),A/'native-intake58.json',A/'revision-a-freeze.json',A/'cloud_bank58.blend',A/'geometry-context58.json']
snapshots={}
for p in input_files:
    snapshots[str(p)]=dict(sha256=sha(p),bytes=p.stat().st_size)
    if p.suffix!='.blend':shutil.copy2(p,run/'inputs'/p.name)
(run/'inputs'/'manifest.json').write_text(json.dumps(snapshots,indent=2)+'\n')
status=dict(state='running',complete=False,run_id=run.name,started_utc=stamp,world_loaded=False,rendered=False,visual_acceptance=False,commands=[])
(run/'result.json').write_text(json.dumps(status,indent=2)+'\n')
env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
print(str(run),flush=True);start=time.monotonic();complete=False;error=None
try:
    for phase,script in [('build','build58b.py'),('verify','verify58b.py')]:
        cmd=[str(BLENDER),'-b','-t','2','--python-exit-code','1','--python',str(P/script)]
        row=dict(phase=phase,state='running',complete=False,argv=cmd,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        status['commands'].append(row);(run/'result.json').write_text(json.dumps(status,indent=2)+'\n')
        with (run/f'{phase}-stdout.log').open('wb') as out,(run/f'{phase}-stderr.log').open('wb') as err:
            child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err);(run/f'{phase}.pid').write_text(str(child.pid)+'\n')
            try:code=child.wait(timeout=300)
            except subprocess.TimeoutExpired:
                child.terminate()
                try:child.wait(timeout=10)
                except subprocess.TimeoutExpired:child.kill();child.wait()
                code=124
        row.update(exit_code=code,state='finished',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        logs=(run/f'{phase}-stdout.log').read_text(errors='replace')+'\n'+(run/f'{phase}-stderr.log').read_text(errors='replace')
        row['hard_errors']=[s for s in logs.splitlines() if s.startswith(('Traceback','Error:')) or 'Error: script failed' in s]
        row['complete']=code==0 and not row['hard_errors'];(run/f'{phase}.exit-code.txt').write_text(str(code)+'\n')
        (run/'result.json').write_text(json.dumps(status,indent=2)+'\n')
        if not row['complete']:break
    complete=len(status['commands'])==2 and all(r['complete'] for r in status['commands'])
    if complete:complete=bool(json.loads((P/'geometry-context58b.json').read_text())['native_source_geometry_passed'])
except BaseException:
    error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
finally:
    for p in P.glob('*.json'):shutil.copy2(p,run/'outputs'/p.name)
    status.update(state='finished',complete=bool(complete),wall_seconds=time.monotonic()-start,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                  error=error,source_files={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in P.iterdir() if p.suffix in ('.blend','.glb')},finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (run/'result.json').write_text(json.dumps(status,indent=2)+'\n')
    (run/'terminal-proof.json').write_text(json.dumps(dict(run_id=run.name,result_sha256=sha(run/'result.json'),complete=bool(complete)),indent=2)+'\n')
    (run/'wrapper.exit-code.txt').write_text(('0' if complete else '1')+'\n')
print(json.dumps(status,indent=2));sys.exit(0 if complete else 1)

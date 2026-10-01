"""Parent-scheduled source-only build followed by fresh Blender readback.

No rendering option exists. No Godot executable or world payload is launched.
"""
import datetime,hashlib,json,os,resource,shutil,subprocess,sys,tempfile,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=Path(tempfile.mkdtemp(prefix=f'cloudbank58-source-build-{stamp}-',dir=ROOT/'cloud-evidence'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(P/'cloud_bank58.blend').exists(),'Completed source already exists; never overwrite it'
inputs=[P/f for f in ('geometry58.py','intake58.py','build58.py','verify58.py','run_source58.py','native-intake58.json')]
for p in inputs:shutil.copy2(p,run/p.name)
(run/'input-sha256.json').write_text(json.dumps({str(p):dict(sha256=sha(p),bytes=p.stat().st_size) for p in inputs},indent=2)+'\n')
env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
for name in ('blender-config','xdg-cache','xdg-config','xdg-data'):(run/name).mkdir()
commands=[];success=False;start=time.monotonic()
print(str(run),flush=True)
try:
    for phase,script in [('build','build58.py'),('verify','verify58.py')]:
        cmd=[str(BLENDER),'-b','-t','2','--python-exit-code','1','--python',str(P/script)]
        row=dict(phase=phase,argv=cmd,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());commands.append(row)
        (run/'invocation.json').write_text(json.dumps(dict(commands=commands,threads=2,rendered=False,world_launched=False),indent=2)+'\n')
        with (run/f'{phase}-stdout.log').open('wb') as out,(run/f'{phase}-stderr.log').open('wb') as err:
            child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err)
            (run/f'{phase}.pid').write_text(str(child.pid)+'\n')
            try:code=child.wait(timeout=240)
            except subprocess.TimeoutExpired:
                child.terminate()
                try:child.wait(timeout=10)
                except subprocess.TimeoutExpired:child.kill();child.wait()
                code=124
        row['exit_code']=code;row['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        (run/f'{phase}-exit-code.txt').write_text(str(code)+'\n')
        (run/'invocation.json').write_text(json.dumps(dict(commands=commands,threads=2,rendered=False,world_launched=False),indent=2)+'\n')
        logs=(run/f'{phase}-stdout.log').read_text(errors='replace')+'\n'+(run/f'{phase}-stderr.log').read_text(errors='replace')
        row['hard_errors']=[s for s in logs.splitlines() if s.startswith(('Traceback','Error:')) or 'Error: script failed' in s]
        if code or row['hard_errors']:break
    success=len(commands)==2 and all(r['exit_code']==0 and not r['hard_errors'] for r in commands)
    if success:
        proof=json.loads((P/'geometry-context58.json').read_text());success=proof['native_source_geometry_passed'] and proof['native_controls_match_recipe']
finally:
    for name in ('construction58.json','protected-sources58.json','geometry-context58.json'):
        if (P/name).exists():shutil.copy2(P/name,run/name)
    result=dict(complete=bool(success),commands=commands,wall_seconds=time.monotonic()-start,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                rendered=False,world_launched=False,visual_acceptance=False,hardware_gpu_acceptance=False,
                source_hashes={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in P.iterdir() if p.suffix in ('.blend','.glb')})
    (run/'result.json').write_text(json.dumps(result,indent=2)+'\n');(run/'wrapper-exit-code.txt').write_text(('0' if success else '1')+'\n')
print(json.dumps(result,indent=2),flush=True)
sys.exit(0 if success else 1)

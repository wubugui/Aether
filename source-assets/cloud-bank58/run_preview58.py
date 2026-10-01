"""Requires a separately parent-scheduled source-render window; never a world run."""
import datetime,hashlib,json,os,resource,struct,subprocess,sys,tempfile,time
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
assert (P/'geometry-context58.json').exists()
assert json.loads((P/'geometry-context58.json').read_text())['native_source_geometry_passed']
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=Path(tempfile.mkdtemp(prefix=f'cloudbank58-source-preview-{stamp}-',dir=ROOT/'cloud-evidence'))
for name in ('images','blender-config','xdg-cache','xdg-config','xdg-data'):(run/name).mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected=[P/'cloud_bank58.blend',*P.glob('*.glb'),ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',ROOT/'candidates/round40-exclusive-20260930/project/project.godot']
before={str(p):sha(p) for p in protected}
inputs=protected+[P/'preview58.py',P/'run_preview58.py',P/'geometry-context58.json',P/'native-intake58.json',BLENDER]
(run/'input-sha256.json').write_text(json.dumps({str(p):dict(sha256=sha(p),bytes=p.stat().st_size) for p in inputs},indent=2)+'\n')
cmd=[str(BLENDER),'-b','-t','2','--python-exit-code','1','--python',str(P/'preview58.py'),'--','--out',str(run/'images')]
env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
(run/'invocation.json').write_text(json.dumps(dict(argv=cmd,expected_images=5,threads=2,samples=16,world_loaded=False,source_save=False),indent=2)+'\n')
print(str(run),flush=True);start=time.monotonic();code=99
with (run/'stdout.log').open('wb') as out,(run/'stderr.log').open('wb') as err:
    child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err);(run/'blender.pid').write_text(str(child.pid)+'\n')
    try:code=child.wait(timeout=420)
    except subprocess.TimeoutExpired:
        child.terminate()
        try:child.wait(timeout=10)
        except subprocess.TimeoutExpired:child.kill();child.wait()
        code=124
(run/'blender-exit-code.txt').write_text(str(code)+'\n')
after={str(p):sha(p) for p in protected};pngs=[]
for p in sorted((run/'images').glob('*.png')):
    raw=p.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',raw[16:24]);pngs.append(dict(name=p.name,width=w,height=h,sha256=sha(p),bytes=len(raw)))
logs=(run/'stdout.log').read_text(errors='replace')+'\n'+(run/'stderr.log').read_text(errors='replace')
errors=[s for s in logs.splitlines() if s.startswith(('Traceback','Error:')) or 'Error: script failed' in s]
success=code==0 and not errors and before==after and len(pngs)==5 and all(p['width']==1000 and p['height']==700 for p in pngs)
result=dict(complete=success,blender_exit_code=code,hard_errors=errors,protected_unchanged=before==after,protected_before=before,protected_after=after,
            images=pngs,wall_seconds=time.monotonic()-start,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            world_loaded=False,hardware_gpu_acceptance=False,visual_acceptance=False)
(run/'result.json').write_text(json.dumps(result,indent=2)+'\n');(run/'wrapper-exit-code.txt').write_text(('0' if success else '1')+'\n')
print(json.dumps(result,indent=2));sys.exit(0 if success else 1)

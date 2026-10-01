"""Run only the parent-approved union OR finish stage,60s and1.5GiB total gates.

Each stage includes a fresh Blender readback. No renderer/world is invoked.
"""
import argparse,datetime,hashlib,json,os,resource,shutil,subprocess,sys,tempfile,time,traceback
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent;ROOT=A.parents[1]
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['union','finish']);args=parser.parse_args()
if args.stage=='union':
    assert not(P/'cloud_bank58b_union.blend').exists()
    scripts=[(P/'build_union58b.py',[]),(P/'verify_union58b.py',[])]
else:
    assert not(P/'cloud_bank58b.blend').exists()
    assert json.loads((P/'union-fresh-readback58b.json').read_text())['passed']
    scripts=[(P/'finish58b.py',[]),(B/'verify58b.py',['--source',str(P)])]
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=Path(tempfile.mkdtemp(prefix=f'cloudbank58b-recovery-{args.stage}-{stamp}-',dir=ROOT/'cloud-evidence'))
for name in ('inputs','outputs','blender-config','xdg-cache','xdg-config','xdg-data'):(run/name).mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)
inputs=[p for p,_ in scripts]+[Path(__file__),B/'native-control-input58b.json',B/'failed-build-freeze58b.json',A/'revision-a-freeze.json']
for p in inputs:shutil.copy2(p,run/'inputs'/p.name)
write_json(run/'inputs'/'manifest.json',{str(p):dict(sha256=sha(p),bytes=p.stat().st_size) for p in inputs})
protected={}
for file in (A/'revision-a-freeze.json',B/'failed-build-freeze58b.json'):
    for path,row in json.loads(file.read_text())['files'].items():protected[path]=row['sha256']
status=dict(state='running',complete=False,run_id=run.name,stage=args.stage,started_utc=stamp,commands=[],world_loaded=False,rendered=False,visual_acceptance=False)
write_json(run/'result.json',status);print(str(run),flush=True)
env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONUNBUFFERED='1',BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
start=time.monotonic();peak=0;reason=None;error=None;child=None;complete=False
try:
    for index,(script,extra) in enumerate(scripts):
        cmd=[str(BLENDER),'-b','-t','2','--python-exit-code','1','--python',str(script)]
        if extra:cmd+=['--',*extra]
        row=dict(script=script.name,argv=cmd,state='running',complete=False);status['commands'].append(row);write_json(run/'result.json',status)
        with (run/f'{index}-stdout.log').open('wb') as out,(run/f'{index}-stderr.log').open('wb') as err:
            child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err);(run/f'{index}-child.pid').write_text(str(child.pid)+'\n')
            while child.poll() is None:
                elapsed=time.monotonic()-start;current=None;info=Path('/proc')/str(child.pid)/'status'
                if info.exists():
                    line=next((s for s in info.read_text().splitlines() if s.startswith('VmRSS:')),None)
                    if line:current=int(line.split()[1]);peak=max(peak,current)
                stagefile=P/('union-stage58b.json' if args.stage=='union' else 'facet-stage58b.json')
                operation=None
                if stagefile.exists():
                    try:operation=json.loads(stagefile.read_text()).get('current_operation')
                    except json.JSONDecodeError:operation='stage update pending'
                write_json(run/'live-resource.json',dict(state='running',complete=False,script=script.name,operation=operation,elapsed_seconds=elapsed,current_rss_kib=current,peak_observed_rss_kib=peak))
                if elapsed>60:reason='60second total source-stage limit'
                if peak>1572864:reason='1.5GiB source-stage RSS budget'
                if reason:
                    child.terminate()
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:child.kill();child.wait()
                    break
                time.sleep(.5)
            code=child.wait();child=None
        logs=(run/f'{index}-stdout.log').read_text(errors='replace')+'\n'+(run/f'{index}-stderr.log').read_text(errors='replace')
        hard=[s for s in logs.splitlines() if s.startswith(('Traceback','Error:')) or 'Error: script failed' in s]
        row.update(state='finished',actual_child_exit_code=code,hard_errors=hard,complete=code==0 and not hard and reason is None)
        (run/f'{index}-child.exit-code.txt').write_text(str(code)+'\n');write_json(run/'result.json',status)
        if not row['complete']:break
    complete=len(status['commands'])==2 and all(r['complete'] for r in status['commands'])
    proof=P/('union-fresh-readback58b.json' if args.stage=='union' else 'geometry-context58b.json')
    if complete:complete=bool(json.loads(proof.read_text())['passed' if args.stage=='union' else 'native_source_geometry_passed'])
except BaseException:
    error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
    if child is not None and child.poll() is None:
        child.terminate()
        try:child.wait(timeout=5)
        except subprocess.TimeoutExpired:child.kill();child.wait()
finally:
    for p in P.glob('*.json'):shutil.copy2(p,run/'outputs'/p.name)
    after={path:sha(ROOT/path) for path in protected};complete=complete and after==protected
    status.update(state='finished',complete=bool(complete),limit_stop_reason=reason,error=error,wall_seconds=time.monotonic()-start,peak_observed_rss_kib=peak,
                  peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,protected_unchanged=after==protected,
                  source_files={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in P.iterdir() if p.suffix in ('.blend','.glb')})
    write_json(run/'result.json',status);write_json(run/'terminal-proof.json',dict(run_id=run.name,result_sha256=sha(run/'result.json'),complete=bool(complete)))
    (run/'wrapper.exit-code.txt').write_text(('0' if complete else '1')+'\n')
print(json.dumps(status,indent=2));sys.exit(0 if complete else 1)

"""Parent-scheduled F build + two fresh images, CPU2 / 90s / 1.5GiB.

No work runs on import. Source/image writes require the explicit launch flag.
Inputs are bound by versioned paths and SHA, not copied into duplicate bundles.
"""
import argparse
from datetime import datetime,timezone
import json,os,resource,subprocess,sys,tempfile,time,traceback
from pathlib import Path

P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'revision-d/native-01'))
import common58d as c

SOURCE=P/'shared_patch58f.blend'
VIEWS=['1216-source-front','shared-side-back']


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-approved-patch-trial',action='store_true',required=True)
    parser.parse_args()
    blender=c.ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
    assert c.sha(blender)==c.BINARY_SHA256
    assert not SOURCE.exists(),'Preserve any existing source success or failure'
    preparation=P/'preparation-freeze58f.json'
    prepared=json.loads(preparation.read_text())
    assert all(c.sha(c.ROOT/path)==row['sha256'] for path,row in prepared['files'].items())
    freezes=[c.FREEZE,P.parent/'revision-d/native-01/native-freeze58d-20261001T1620Z.json',
             P.parent/'revision-d/preview-01/preview-freeze58d-20261001T1634Z.json',
             P.parent/'revision-e/layout-freeze58e-20261001T1659Z.json',
             P.parent/'revision-c-complete-freeze-20261001T1305Z.json']
    protected={}
    for path in freezes:protected.update(json.loads(path.read_text())['files'])
    assert all(c.sha(c.ROOT/path)==row['sha256'] for path,row in protected.items())
    png_helper=c.load_pure(P.parent/'revision-d/preview-01/run_preview58d.py')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run=Path(tempfile.mkdtemp(prefix='cloudbank58f-patch-'+stamp+'-',dir=c.ROOT/'cloud-evidence'))
    state=dict(state='running',complete=False,passed=False,run_id=run.name,commands=[],images=[],world_loaded=False,
               final_geometry_pass=False,visual_acceptance=False)
    c.write(run/'process-report.json',state)
    for name in ['inputs','outputs','blender-config','xdg-cache','xdg-config','xdg-data']:(run/name).mkdir()
    c.write(run/'inputs/input-sha256.json',dict(files=prepared['files'],preparation_freeze_sha256=c.sha(preparation),
                                             binary_sha256=c.sha(blender),protected_file_count=len(protected)))
    print(run,flush=True)
    env=os.environ.copy()
    env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',
               BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),
               XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
    jobs=[dict(mode='build',view=None)]+[dict(mode='render',view=view) for view in VIEWS]
    start=time.monotonic();peak=0;reason=None;error=None;child=None
    try:
        for index,job in enumerate(jobs):
            if time.monotonic()-start>=90:reason='90 second total budget exhausted before next stage';break
            argv=[str(blender),'--factory-startup','-b','-t','2','--python-exit-code','1',
                  '--python',str(P/'source58f.py'),'--','--mode',job['mode'],'--out',str(run/'outputs')]
            if job['view']:argv.extend(['--view',job['view']])
            row=dict(job=job,state='running',complete=False,argv=argv)
            state['commands'].append(row);c.write(run/'process-report.json',state)
            with (run/f'{index}-stdout.log').open('wb') as out,(run/f'{index}-stderr.log').open('wb') as err:
                child=subprocess.Popen(argv,cwd=c.ROOT,env=env,stdout=out,stderr=err)
                row['pid']=child.pid;(run/f'{index}-child.pid').write_text(str(child.pid)+'\n')
                while child.poll() is None:
                    current=None;elapsed=time.monotonic()-start
                    try:
                        line=next((s for s in (Path('/proc')/str(child.pid)/'status').read_text().splitlines() if s.startswith('VmRSS:')),None)
                        if line:current=int(line.split()[1]);peak=max(peak,current)
                    except FileNotFoundError:pass
                    c.write(run/'live-resource.json',dict(state='running',job=index,mode=job['mode'],view=job['view'],
                                                         elapsed_seconds=elapsed,current_rss_kib=current,peak_observed_rss_kib=peak))
                    if elapsed>90:reason='90 second total patch trial budget exceeded'
                    if peak>1572864:reason='1.5 GiB observed RSS exceeded'
                    if reason:
                        child.terminate()
                        try:child.wait(timeout=3)
                        except subprocess.TimeoutExpired:child.kill();child.wait()
                        break
                    time.sleep(.2)
                code=child.wait();child=None
            (run/f'{index}-child.exit-code').write_text(str(code)+'\n')
            row.update(state='completed',actual_child_exit_code=code,complete=code==0 and not reason)
            if resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss>1572864:
                reason='1.5 GiB actual child peak exceeded';row['complete']=False
            if row['complete'] and job['mode']=='build':
                built=json.loads((run/'outputs/build-result58f.json').read_text());row['complete']=built['passed']
                if built['source_bytes']>1048576:
                    reason='Saved source exceeds 1 MiB report threshold; preserve and stop';row['complete']=False
            if row['complete'] and job['mode']=='render':
                proof=json.loads((run/'outputs'/(job['view']+'-proof.json')).read_text())
                info=png_helper.png_info(run/'outputs'/('58F-'+job['view']+'.png'))
                expected=(836,471) if job['view']=='1216-source-front' else (836,586)
                row['complete']=bool(proof['passed'] and info['sha256']==proof['image_sha256'] and (info['width'],info['height'])==expected)
                state['images'].append(dict(view=job['view'],**info))
            c.write(run/'process-report.json',state)
            if not row['complete']:break
    except BaseException:
        error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
        if child is not None and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=3)
            except subprocess.TimeoutExpired:child.kill();child.wait()
    finally:
        same=all(c.sha(c.ROOT/path)==row['sha256'] for path,row in protected.items())
        inputs_same=all(c.sha(c.ROOT/path)==row['sha256'] for path,row in prepared['files'].items())
        complete=bool(len(state['commands'])==3 and len(state['images'])==2 and all(row['complete'] for row in state['commands'])
                      and same and inputs_same and not reason and not error)
        code=0 if complete else 1
        state.update(state='completed',complete=complete,passed=complete,actual_wrapper_exit_code=code,error=error,limit_stop_reason=reason,
                     elapsed_seconds=time.monotonic()-start,peak_observed_rss_kib=peak,
                     actual_peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                     protected_unchanged=same,prepared_inputs_unchanged=inputs_same,
                     source=dict(path=str(SOURCE.relative_to(c.ROOT)),bytes=SOURCE.stat().st_size,sha256=c.sha(SOURCE)) if SOURCE.exists() else None)
        c.write(run/'process-report.json',state)
        c.write(run/'terminal-proof.json',dict(run_id=run.name,process_report_sha256=c.sha(run/'process-report.json'),complete=complete))
        (run/'wrapper.exit-code').write_text(str(code)+'\n')
    print(json.dumps(state,indent=2),flush=True)
    return code


if __name__=='__main__':sys.exit(main())

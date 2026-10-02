"""Two fresh post-save source previews, <=30s/CPU2/1.5GiB; never builds/saves."""
import argparse
from datetime import datetime,timezone
import json
import hashlib
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time
import traceback

P=Path(__file__).resolve().parent;H=P.parent;ROOT=P.parents[3]
def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def write(path,data):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');temporary.replace(path)


def matches(rows):
    try:return all((ROOT/key).is_file() and sha(ROOT/key)==row['sha256'] for key,row in rows.items())
    except OSError:return False


def interrupted(number,frame):raise RuntimeError('Preview wrapper interrupted by signal '+str(number))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-approved-saved-source-preview',required=True,action='store_true');parser.parse_args()
    if not __debug__:raise RuntimeError('Optimized Python would disable strict gates; refusing execution')
    started=time.monotonic();stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run=Path(tempfile.mkdtemp(prefix='cloudbank58h-preview-'+stamp+'-',dir=ROOT/'cloud-evidence'))
    for name in ('outputs','xdg-cache','xdg-config','xdg-data','blender-config'):(run/name).mkdir()
    print(run,flush=True)
    state=dict(state='running',complete=False,passed=False,run_id=run.name,commands=[],images=[],
               phase='independent_post_save_previews',original_build_passed=False,source_saved=False,rebuilt=False,
               world_loaded=False,final_geometry_pass=False,visual_acceptance=False)
    write(run/'process-report.json',state)
    child=None;row=None;usage=None;index=None;stage_start=None;prepared={};protected={};source=None
    error=None;reason=None;actual_peak=0;observed_peak=0
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,interrupted)
    try:
        assert not (P/'preview-terminal-freeze58h.json').exists(),'Preserve earlier terminal; no in-place rerun'
        frozen=json.loads((P/'preview-preparation-freeze58h.json').read_text());prepared=frozen['files'];protected=frozen['protected_files']
        assert matches(prepared) and matches(protected)
        # Only execute shared helper code after all transitive frozen hashes pass.
        sys.path.insert(0,str(H.parent/'revision-d/native-01'))
        import common58d as c
        guard=c.load_pure(H/'run_patch58h.py')
        plan=json.loads((P/'preview-plan58h.json').read_text());source=ROOT/plan['inputs']['source']['path']
        assert sha(source)==plan['inputs']['source']['sha256'];state['source_sha256_before']=sha(source)
        binary=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender';assert sha(binary)==plan['blender_binary_sha256']
        limits=plan['limits'];assert limits['total_seconds']==30 and limits['cpu_threads']==2
        cpus=sorted(os.sched_getaffinity(0))[:2];os.sched_setaffinity(0,cpus);state['cpu_affinity']=cpus;state['limits']=limits
        manifest=run/'input-sha256.json'
        write(manifest,dict(preparation_freeze_sha256=sha(P/'preview-preparation-freeze58h.json'),
                 files=prepared,protected_files=protected,binary_sha256=plan['blender_binary_sha256']))
        env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',
            PYTHONUNBUFFERED='1',PYTHONOPTIMIZE='0',BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),
            XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
        for index,view in enumerate(plan['views']):
            if time.monotonic()-started>=limits['total_seconds']:
                reason='30 second total preview budget exhausted before next view';break
            assert matches(prepared) and matches(protected) and sha(source)==plan['inputs']['source']['sha256']
            argv=[str(binary),'--factory-startup','--disable-autoexec','-b','-t','2','--python-exit-code','1',
                  '--python',str(P/'render_saved58h.py'),'--','--view',view,'--out',str(run/'outputs')]
            row=dict(view=view,state='running',complete=False,argv=argv,input_manifest_sha256=sha(manifest),
                     source_sha256_before=sha(source),prepared_before=True,protected_before=True)
            state['commands'].append(row);write(run/'process-report.json',state);stage_start=time.monotonic()
            with (run/f'{index}-stdout.log').open('wb') as stdout,(run/f'{index}-stderr.log').open('wb') as stderr:
                child=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
                row['pid']=child.pid;(run/f'{index}-child.pid').write_text(str(child.pid)+'\n')
                while True:
                    pid,status,usage=os.wait4(child.pid,os.WNOHANG)
                    if pid:
                        code=os.waitstatus_to_exitcode(status);child.returncode=code;child=None;break
                    elapsed=time.monotonic()-started;aggregate=guard.rss_kib(os.getpid())+guard.rss_kib(child.pid)
                    observed_peak=max(observed_peak,aggregate)
                    if elapsed>=limits['total_seconds']:reason='30 second total preview budget exceeded'
                    if aggregate>limits['max_wrapper_plus_child_rss_kib']:reason='1.5 GiB wrapper plus child RSS exceeded'
                    if reason:guard.terminate_group(child)
                    write(run/'live-resource.json',dict(view=view,elapsed_seconds=elapsed,aggregate_rss_kib=aggregate,
                                                         peak_observed_aggregate_rss_kib=observed_peak))
                    time.sleep(.05)
            actual_peak=max(actual_peak,usage.ru_maxrss)
            row.update(state='completed',actual_child_exit_code=code,elapsed_seconds=time.monotonic()-stage_start,
                actual_peak_child_rss_kib=usage.ru_maxrss,actual_child_user_seconds=usage.ru_utime,
                actual_child_system_seconds=usage.ru_stime,source_sha256_after=sha(source),
                protected_after=matches(protected),prepared_after=matches(prepared))
            (run/f'{index}-child.exit-code').write_text(str(code)+'\n')
            if time.monotonic()-started>limits['total_seconds']:reason='30 second total preview budget exceeded'
            if actual_peak+resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>limits['max_wrapper_plus_child_rss_kib']:
                reason='1.5 GiB conservative wrapper plus child peak sum exceeded'
            row['complete']=bool(code==0 and not reason and row['prepared_after'] and row['protected_after']
                                  and row['source_sha256_before']==row['source_sha256_after'])
            if row['complete']:
                proof=json.loads((run/'outputs'/(view+'-proof.json')).read_text())
                info=guard.png_info(run/'outputs'/('58H-'+view+'.png'))
                expected=(836,471) if view=='1216-source-front' else (836,586)
                row['complete']=bool(proof['passed'] and proof['post_save_validation']['passed']
                    and proof['original_build_passed'] is False and proof['source_unchanged']
                    and proof['source_sha256_before']==proof['source_sha256_after']==sha(source)
                    and proof['image_sha256']==info['sha256'] and (info['width'],info['height'])==expected
                    and proof['pid']==row['pid'])
                state['images'].append(dict(view=view,**info))
            write(run/f'{index}-stage-result.json',row);write(run/'process-report.json',state)
            if not row['complete']:break
    except BaseException:
        error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
        if child is not None:
            guard.terminate_group(child);pid,status,usage=os.wait4(child.pid,0);child.returncode=os.waitstatus_to_exitcode(status)
            actual_peak=max(actual_peak,usage.ru_maxrss)
            row.update(state='completed',complete=False,actual_child_exit_code=child.returncode,
                actual_peak_child_rss_kib=usage.ru_maxrss,elapsed_seconds=time.monotonic()-stage_start,wrapper_exception=True)
            (run/f'{index}-child.exit-code').write_text(str(child.returncode)+'\n');child=None
        if row is not None:row.update(state='completed',complete=False);write(run/f'{index}-stage-result.json',row)
    finally:
        same=bool(protected) and matches(protected);prepared_same=bool(prepared) and matches(prepared)
        source_same=source is not None and sha(source)==state.get('source_sha256_before')
        elapsed=time.monotonic()-started;wrapper_peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if elapsed>30:reason='30 second total preview budget exceeded during terminal verification'
        if actual_peak+wrapper_peak>1572864:reason='1.5 GiB conservative wrapper plus child peak sum exceeded at terminal verification'
        complete=bool(len(state['commands'])==2 and len(state['images'])==2 and all(row['complete'] for row in state['commands'])
                      and len({row['pid'] for row in state['commands']})==2 and same and prepared_same and source_same and not error and not reason)
        result_code=0 if complete else 1
        state.update(state='completed',complete=complete,passed=complete,actual_wrapper_exit_code=result_code,error=error,
            limit_stop_reason=reason,elapsed_seconds=elapsed,actual_peak_child_rss_kib=actual_peak,
            actual_peak_wrapper_rss_kib=wrapper_peak,conservative_sum_of_separate_peak_rss_kib=actual_peak+wrapper_peak,
            peak_observed_aggregate_rss_kib=observed_peak,protected_unchanged=same,prepared_unchanged=prepared_same,
            source_unchanged=source_same,source_sha256_after=sha(source) if source is not None else None)
        write(run/'process-report.json',state);(run/'wrapper.exit-code').write_text(str(result_code)+'\n')
        write(run/'terminal-proof.json',dict(process_report_sha256=sha(run/'process-report.json'),run_id=run.name,complete=complete))
        terminal=P/'preview-terminal-freeze58h.json'
        if not terminal.exists():
            paths=[q for q in run.rglob('*') if q.is_file() and not any(part in ('xdg-cache','xdg-config','xdg-data','blender-config') for part in q.relative_to(run).parts)]
            rows={str(q.relative_to(ROOT)):dict(bytes=q.stat().st_size,sha256=sha(q)) for q in paths}
            write(terminal,dict(status='Post-save preview terminal, old build failure preserved',files=rows,
                original_build_passed=False,source_saved=False,rebuilt=False,source_unchanged=source_same,visual_acceptance=False))
    print(json.dumps(state,indent=2),flush=True)
    return result_code


if __name__=='__main__':sys.exit(main())

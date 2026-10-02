"""One explicitly scheduled read-only source inspection, 15s/CPU2/1.5GiB."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time
import traceback

P=Path(__file__).resolve().parent
ROOT=P.parents[3]


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):digest.update(part)
    return digest.hexdigest()


def write(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');tmp.replace(path)


def matches(rows):
    try:return all((ROOT/key).is_file() and sha(ROOT/key)==row['sha256'] for key,row in rows.items())
    except OSError:return False


def rss(pid):
    try:
        lines=(Path('/proc')/str(pid)/'status').read_text().splitlines()
        value=next((line for line in lines if line.startswith('VmRSS:')),None)
        return int(value.split()[1]) if value else 0
    except FileNotFoundError:return 0


def kill(child):
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass


def interrupt(number,frame):raise RuntimeError('Inspection wrapper interrupted by signal '+str(number))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-approved-readonly-inspection',required=True,action='store_true');parser.parse_args()
    started=time.monotonic();stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run=Path(tempfile.mkdtemp(prefix='cloudbank58g-readonly-'+stamp+'-',dir=ROOT/'cloud-evidence'))
    for name in ('outputs','xdg-data','xdg-config','xdg-cache','blender-config'):(run/name).mkdir()
    print(run,flush=True)
    report=dict(state='running',complete=False,passed=False,run_id=run.name,child=None,
                readonly=True,rebuilt=False,source_saved=False,rendered=False,visual_acceptance=False)
    write(run/'wrapper-report.json',report)
    child=None;code=None;usage=None;peak=0;error=None;reason=None;source=None;prepared={};protected={}
    for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,interrupt)
    try:
        assert not (P/'inspection-terminal-freeze58g.json').exists(),'Keep any previous terminal; do not retry in place'
        frozen=json.loads((P/'inspection-preparation-freeze58g.json').read_text());prepared=frozen['files']
        assert matches(prepared)
        plan=json.loads((P/'inspection-plan58g.json').read_text());source=ROOT/plan['source']['path'];limits=plan['limits']
        assert sha(source)==plan['source']['sha256'];report['source_sha256_before']=sha(source)
        freeze=ROOT/plan['original_failure_freeze']['path'];assert sha(freeze)==plan['original_failure_freeze']['sha256']
        protected=json.loads(freeze.read_text())['files'];assert matches(protected)
        binary=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
        assert sha(binary)==plan['blender_binary_sha256']
        cpus=sorted(os.sched_getaffinity(0))[:2];os.sched_setaffinity(0,cpus)
        report['limits']=limits;report['cpu_affinity']=cpus
        write(run/'input-sha256.json',dict(preparation_freeze_sha256=sha(P/'inspection-preparation-freeze58g.json'),
                prepared_files=prepared,protected_files=protected,source=plan['source'],binary_sha256=plan['blender_binary_sha256']))
        env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',
            PYTHONUNBUFFERED='1',BLENDER_USER_CONFIG=str(run/'blender-config'),
            XDG_DATA_HOME=str(run/'xdg-data'),XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_CACHE_HOME=str(run/'xdg-cache'))
        argv=[str(binary),'--factory-startup','--disable-autoexec','-b','-t','2','--python-exit-code','1',
              '--python',str(P/'inspect58g.py'),'--','--out',str(run/'outputs')]
        report['argv']=argv;write(run/'wrapper-report.json',report)
        if time.monotonic()-started>=limits['total_seconds']:raise RuntimeError('15s budget exhausted in preflight')
        with (run/'stdout.log').open('wb') as out,(run/'stderr.log').open('wb') as err:
            child=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=out,stderr=err,start_new_session=True)
            report['pid']=child.pid;(run/'child.pid').write_text(str(child.pid)+'\n')
            while True:
                pid,status,usage=os.wait4(child.pid,os.WNOHANG)
                if pid:
                    code=os.waitstatus_to_exitcode(status);child.returncode=code;child=None;break
                elapsed=time.monotonic()-started;aggregate=rss(os.getpid())+rss(child.pid);peak=max(peak,aggregate)
                if elapsed>=limits['total_seconds']:reason='15 second total inspection limit exceeded'
                if aggregate>limits['max_wrapper_plus_child_rss_kib']:reason='1.5 GiB wrapper plus child RSS exceeded'
                if reason:kill(child)
                write(run/'live-resource.json',dict(elapsed_seconds=elapsed,aggregate_rss_kib=aggregate,peak_observed_aggregate_rss_kib=peak))
                time.sleep(.05)
        report['child']=dict(actual_exit_code=code,actual_peak_rss_kib=usage.ru_maxrss,
                            user_seconds=usage.ru_utime,system_seconds=usage.ru_stime)
        (run/'child.exit-code').write_text(str(code)+'\n')
        if code==0:
            result=json.loads((run/'outputs/inspection-result58g.json').read_text())
            report['inspection_passed']=result['passed']
            report['loaded_image_count']=result['loaded_inventory']['image_count']
            report['loaded_library_count']=result['loaded_inventory']['library_count']
            report['source_unchanged_child']=result['source_unchanged']
    except BaseException:
        error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
        if child is not None:
            kill(child);pid,status,usage=os.wait4(child.pid,0);code=os.waitstatus_to_exitcode(status);child.returncode=code;child=None
            report['child']=dict(actual_exit_code=code,actual_peak_rss_kib=usage.ru_maxrss,
                                user_seconds=usage.ru_utime,system_seconds=usage.ru_stime)
            (run/'child.exit-code').write_text(str(code)+'\n')
    finally:
        if source is not None:
            report['source_sha256_after']=sha(source)
            report['source_unchanged']=report['source_sha256_after']==report.get('source_sha256_before')
        report['protected_unchanged']=bool(protected) and matches(protected)
        report['prepared_unchanged']=bool(prepared) and matches(prepared)
        elapsed=time.monotonic()-started;wrapper_peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        combined_peak=wrapper_peak+(usage.ru_maxrss if usage else 0)
        if elapsed>15:reason='15 second total inspection limit exceeded'
        if combined_peak>1572864:reason='1.5 GiB conservative wrapper plus child peak sum exceeded'
        passed=bool(code==0 and report.get('inspection_passed') and report.get('source_unchanged')
                    and report['protected_unchanged'] and report['prepared_unchanged'] and not error and not reason)
        result_code=0 if passed else 1
        report.update(state='completed',complete=passed,passed=passed,actual_wrapper_exit_code=result_code,
            elapsed_seconds=elapsed,error=error,limit_stop_reason=reason,actual_peak_wrapper_rss_kib=wrapper_peak,
            conservative_sum_of_separate_peak_rss_kib=combined_peak,peak_observed_aggregate_rss_kib=peak)
        write(run/'wrapper-report.json',report);(run/'wrapper.exit-code').write_text(str(result_code)+'\n')
        write(run/'terminal-proof.json',dict(wrapper_report_sha256=sha(run/'wrapper-report.json'),complete=passed,run_id=run.name))
        terminal=P/'inspection-terminal-freeze58g.json'
        if not terminal.exists():
            files=[q for q in run.rglob('*') if q.is_file() and not any(name in ('xdg-cache','xdg-config','xdg-data','blender-config') for name in q.relative_to(run).parts)]
            rows={str(q.relative_to(ROOT)):dict(bytes=q.stat().st_size,sha256=sha(q)) for q in files}
            write(terminal,dict(status='Read-only inspection terminal; original G failure unchanged',files=rows,
                                source_unchanged=report.get('source_unchanged',False),rendered=False,visual_acceptance=False))
    print(json.dumps(report,indent=2),flush=True)
    return result_code


if __name__=='__main__':sys.exit(main())

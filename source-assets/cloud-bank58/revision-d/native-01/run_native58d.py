"""Explicitly authorized isolated native build + fresh readback, never render.

One fresh run directory; all input reports remain under inputs/. A running false
state is written before startup. Actual child exits, source size, input identity
and the terminal report SHA determine completion. Total 60s / 1.5GiB / CPU2.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
import traceback

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import common58d as c


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-approved-native-build',action='store_true',required=True)
    args=parser.parse_args()
    blender=c.ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
    assert c.sha(blender)==c.BINARY_SHA256,'Wrong or unverified Blender binary'
    assert not c.SOURCE.exists(),'Do not overwrite an existing success or failure checkpoint'
    c.frozen_inputs()
    checker=c.load_pure(c.STATIC)
    protected=json.loads(checker.C_FREEZE.read_text())['files']
    assert all(c.sha(c.ROOT/p)==r['sha256'] for p,r in protected.items()),'Frozen C changed'
    preparation=json.loads((HERE/'preparation-freeze58d.json').read_text())
    assert all(c.sha(c.ROOT/p)==r['sha256'] for p,r in preparation['files'].items()),'Prepared scripts changed'
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run=Path(tempfile.mkdtemp(prefix='cloudbank58d-native-'+stamp+'-',dir=c.ROOT/'cloud-evidence'))
    state=dict(state='running',complete=False,passed=False,run_id=run.name,commands=[],world_loaded=False,rendered=False,visual_acceptance=False)
    c.write(run/'process-report.json',state)
    for folder in ['inputs','outputs','blender-config','xdg-cache','xdg-config','xdg-data']:
        (run/folder).mkdir()
    inputs=[*sorted(HERE.glob('*.py')),HERE/'preview-settings58d.json',HERE/'preparation-freeze58d.json',
            c.PLAN,c.CAGE,c.FREEZE,c.STATIC,checker.TOPOLOGY,checker.NARROW,checker.RAYS,checker.C_FREEZE]
    manifest={str(p.relative_to(c.ROOT)):dict(sha256=c.sha(p),bytes=p.stat().st_size) for p in inputs}
    c.write(run/'inputs'/'input-sha256.json',manifest)
    # Versioned input paths and byte hashes suffice; do not duplicate snapshots.
    c.write(run/'inputs'/'binary-identity.json',dict(path=str(blender),sha256=c.sha(blender)))
    print(str(run),flush=True)
    env=os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',
               BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),
               XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
    start=time.monotonic(); peak=0; child=None; reason=None; error=None; complete=False
    try:
        for i,script in enumerate(['build58d.py','verify58d.py']):
            command=[str(blender),'--factory-startup','-b','-t','2','--python-exit-code','1',
                     '--python',str(HERE/script),'--','--out',str(run/'outputs')]
            row=dict(script=script,argv=command,state='running',complete=False)
            state['commands'].append(row);c.write(run/'process-report.json',state)
            with (run/f'{i}-stdout.log').open('wb') as out,(run/f'{i}-stderr.log').open('wb') as err:
                child=subprocess.Popen(command,cwd=c.ROOT,env=env,stdout=out,stderr=err)
                (run/f'{i}-child.pid').write_text(str(child.pid)+'\n')
                while child.poll() is None:
                    current=None; elapsed=time.monotonic()-start
                    try:
                        rss=next((s for s in (Path('/proc')/str(child.pid)/'status').read_text().splitlines() if s.startswith('VmRSS:')),None)
                        if rss:
                            current=int(rss.split()[1]);peak=max(peak,current)
                    except FileNotFoundError:
                        pass
                    c.write(run/'live-resource.json',dict(state='running',script=script,elapsed_seconds=elapsed,current_rss_kib=current,peak_observed_rss_kib=peak))
                    if elapsed>60:reason='60 second total native stage budget exceeded'
                    if peak>1572864:reason='1.5 GiB observed RSS budget exceeded'
                    if reason:
                        child.terminate()
                        try:child.wait(timeout=3)
                        except subprocess.TimeoutExpired:child.kill();child.wait()
                        break
                    time.sleep(.2)
                code=child.wait();child=None
            (run/f'{i}-child.exit-code').write_text(str(code)+'\n')
            row.update(state='completed',actual_child_exit_code=code,complete=code==0 and reason is None)
            c.write(run/'process-report.json',state)
            if not row['complete']:break
            if i==0 and c.SOURCE.stat().st_size>1048576:
                reason='Saved source exceeds 1 MiB report threshold; preserve it and ask parent before fresh stage'
                break
        proof=run/'outputs'/'fresh-readback58d.json'
        complete=(len(state['commands'])==2 and all(r['complete'] for r in state['commands'])
                  and proof.exists() and json.loads(proof.read_text())['passed'])
    except BaseException:
        error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
        if child is not None and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=3)
            except subprocess.TimeoutExpired:child.kill();child.wait()
    finally:
        same_inputs=all(c.sha(c.ROOT/p)==r['sha256'] for p,r in manifest.items())
        same_c=all(c.sha(c.ROOT/p)==r['sha256'] for p,r in protected.items())
        same_static=all(c.sha(c.ROOT/p)==r['sha256'] for p,r in json.loads(c.FREEZE.read_text())['files'].items())
        peak_child=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        if peak_child>1572864:reason=reason or 'Actual child peak RSS exceeds 1.5 GiB'
        complete=bool(complete and same_inputs and same_c and same_static and not reason and not error)
        code=0 if complete else 1
        state.update(state='completed',complete=complete,passed=complete,actual_wrapper_exit_code=code,error=error,limit_stop_reason=reason,
                     elapsed_seconds=time.monotonic()-start,peak_observed_rss_kib=peak,actual_peak_child_rss_kib=peak_child,
                     inputs_unchanged=same_inputs,protected_c_unchanged=same_c,frozen_static_d_unchanged=same_static,
                     source=dict(path=str(c.SOURCE.relative_to(c.ROOT)),sha256=c.sha(c.SOURCE),bytes=c.SOURCE.stat().st_size) if c.SOURCE.exists() else None)
        c.write(run/'process-report.json',state)
        c.write(run/'terminal-proof.json',dict(run_id=run.name,process_report_sha256=c.sha(run/'process-report.json'),complete=complete))
        (run/'wrapper.exit-code').write_text(str(code)+'\n')
    print(json.dumps(state,indent=2),flush=True)
    return code


if __name__=='__main__':
    sys.exit(main())

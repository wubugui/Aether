"""Parent-scheduled F2 native build + two fresh images; 30s/CPU2/1.5GiB.

No work on import. os.wait4 captures each child's actual peak independently.
The frozen F builder retains its *58f.json schema inside this F2 run directory.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent / 'revision-d/native-01'))
import common58d as c

SOURCE = P / 'shared_patch58f2.blend'
VIEWS = ['1216-source-front', 'shared-side-back']
BUDGET_SECONDS = 30
MAX_RSS_KIB = 1572864


def matches(rows):
    return all(c.sha(c.ROOT / path) == row['sha256'] for path, row in rows.items())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-approved-patch-trial', action='store_true', required=True)
    parser.parse_args()
    blender = c.ROOT.parent / 'tools-feiting/blender-4.5.14-linux-x64/blender'
    assert c.sha(blender) == c.BINARY_SHA256
    assert not SOURCE.exists(), 'Keep any prior success/failure; do not overwrite'
    freeze = P / 'preparation-freeze58f2.json'
    prepared = json.loads(freeze.read_text())['files']
    assert matches(prepared)
    manifests = [c.FREEZE,
        P.parent / 'revision-d/native-01/native-freeze58d-20261001T1620Z.json',
        P.parent / 'revision-d/preview-01/preview-freeze58d-20261001T1634Z.json',
        P.parent / 'revision-e/layout-freeze58e-20261001T1659Z.json',
        P.parent / 'revision-c-complete-freeze-20261001T1305Z.json',
        P.parent / 'revision-f/failure-freeze58f.json']
    protected = {}
    for path in manifests:
        protected.update(json.loads(path.read_text())['files'])
    assert matches(protected)
    png_helper = c.load_pure(P.parent / 'revision-d/preview-01/run_preview58d.py')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = Path(tempfile.mkdtemp(prefix='cloudbank58f2-patch-' + stamp + '-', dir=c.ROOT / 'cloud-evidence'))
    state = dict(candidate='F2', state='running', complete=False, passed=False,
                 run_id=run.name, commands=[], images=[], world_loaded=False,
                 final_geometry_pass=False, visual_acceptance=False)
    c.write(run / 'process-report.json', state)
    for name in ['inputs', 'outputs', 'blender-config', 'xdg-cache', 'xdg-config', 'xdg-data']:
        (run / name).mkdir()
    manifest = run / 'inputs/input-sha256.json'
    c.write(manifest, dict(files=prepared, preparation_freeze_sha256=c.sha(freeze),
                          binary_sha256=c.sha(blender), protected_files=protected))
    input_digest = c.sha(manifest)
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1',
               PYTHONUNBUFFERED='1', BLENDER_USER_CONFIG=str(run / 'blender-config'),
               XDG_CACHE_HOME=str(run / 'xdg-cache'), XDG_CONFIG_HOME=str(run / 'xdg-config'),
               XDG_DATA_HOME=str(run / 'xdg-data'))
    print(run, flush=True)
    jobs = [dict(mode='build', view=None)] + [dict(mode='render', view=v) for v in VIEWS]
    start = time.monotonic()
    peak = actual_peak = 0
    reason = error = child = None
    try:
        for index, job in enumerate(jobs):
            if time.monotonic() - start >= BUDGET_SECONDS:
                reason = '30 second total budget exhausted before next stage'
                break
            assert matches(prepared) and matches(protected)
            argv = [str(blender), '--factory-startup', '-b', '-t', '2', '--python-exit-code', '1',
                    '--python', str(P / 'source58f.py'), '--', '--mode', job['mode'], '--out', str(run / 'outputs')]
            if job['view']:
                argv += ['--view', job['view']]
            row = dict(job=job, state='running', complete=False, argv=argv,
                       input_manifest_sha256=input_digest, protected_before=True, prepared_before=True)
            state['commands'].append(row)
            c.write(run / 'process-report.json', state)
            stage_start = time.monotonic()
            stage_peak = 0
            terminated_at = None
            with (run / f'{index}-stdout.log').open('wb') as out, (run / f'{index}-stderr.log').open('wb') as err:
                child = subprocess.Popen(argv, cwd=c.ROOT, env=env, stdout=out, stderr=err)
                row['pid'] = child.pid
                (run / f'{index}-child.pid').write_text(str(child.pid) + '\n')
                while True:
                    pid, status, usage = os.wait4(child.pid, os.WNOHANG)
                    if pid:
                        code = os.waitstatus_to_exitcode(status)
                        child.returncode = code
                        child = None
                        break
                    elapsed = time.monotonic() - start
                    current = None
                    try:
                        lines = (Path('/proc') / str(child.pid) / 'status').read_text().splitlines()
                        line = next((line for line in lines if line.startswith('VmRSS:')), None)
                        if line:
                            current = int(line.split()[1])
                            stage_peak = max(stage_peak, current)
                            peak = max(peak, current)
                    except FileNotFoundError:
                        pass
                    c.write(run / 'live-resource.json', dict(state='running', job=index, mode=job['mode'],
                            view=job['view'], elapsed_seconds=elapsed, current_rss_kib=current,
                            stage_peak_observed_rss_kib=stage_peak, peak_observed_rss_kib=peak))
                    if elapsed >= BUDGET_SECONDS:
                        reason = '30 second total patch trial budget exceeded'
                    if stage_peak > MAX_RSS_KIB:
                        reason = '1.5 GiB observed RSS exceeded'
                    if reason and terminated_at is None:
                        child.terminate()
                        terminated_at = time.monotonic()
                    elif terminated_at is not None and time.monotonic() - terminated_at > 3:
                        child.kill()
                    time.sleep(.1)
            actual_peak = max(actual_peak, usage.ru_maxrss)
            if usage.ru_maxrss > MAX_RSS_KIB:
                reason = '1.5 GiB actual child peak exceeded'
            row.update(state='completed', actual_child_exit_code=code,
                       elapsed_seconds=time.monotonic() - stage_start,
                       peak_observed_rss_kib=stage_peak, actual_peak_child_rss_kib=usage.ru_maxrss,
                       actual_child_user_seconds=usage.ru_utime, actual_child_system_seconds=usage.ru_stime,
                       protected_after=matches(protected), prepared_after=matches(prepared),
                       complete=code == 0 and not reason)
            (run / f'{index}-child.exit-code').write_text(str(code) + '\n')
            row['complete'] = bool(row['complete'] and row['protected_after'] and row['prepared_after'])
            if row['complete'] and job['mode'] == 'build':
                built = json.loads((run / 'outputs/build-result58f.json').read_text())
                row['complete'] = built['passed']
                if built['source_bytes'] > 1048576:
                    reason = 'Source exceeds 1 MiB report threshold; keep source and stop'
                    row['complete'] = False
            if row['complete'] and job['mode'] == 'render':
                proof = json.loads((run / 'outputs' / (job['view'] + '-proof.json')).read_text())
                info = png_helper.png_info(run / 'outputs' / ('58F-' + job['view'] + '.png'))
                expected = (836, 471) if job['view'] == VIEWS[0] else (836, 586)
                row['complete'] = bool(proof['passed'] and info['sha256'] == proof['image_sha256']
                                      and (info['width'], info['height']) == expected)
                state['images'].append(dict(view=job['view'], **info))
            c.write(run / f'{index}-stage-result.json', row)
            c.write(run / 'process-report.json', state)
            if not row['complete']:
                break
    except BaseException:
        error = traceback.format_exc()
        (run / 'wrapper-error.log').write_text(error)
        if child is not None:
            child.kill()
            pid, status, usage = os.wait4(child.pid, 0)
            child.returncode = os.waitstatus_to_exitcode(status)
            actual_peak = max(actual_peak, usage.ru_maxrss)
            if state['commands']:
                row = state['commands'][-1]
                row.update(state='completed', complete=False, actual_child_exit_code=child.returncode,
                           elapsed_seconds=time.monotonic() - stage_start,
                           peak_observed_rss_kib=stage_peak, actual_peak_child_rss_kib=usage.ru_maxrss,
                           wrapper_exception=True)
                (run / f'{index}-child.exit-code').write_text(str(child.returncode) + '\n')
                c.write(run / f'{index}-stage-result.json', row)
            child = None
    finally:
        same, inputs_same = matches(protected), matches(prepared)
        complete = bool(len(state['commands']) == 3 and len(state['images']) == 2
                        and all(row['complete'] for row in state['commands'])
                        and same and inputs_same and not reason and not error)
        code = 0 if complete else 1
        state.update(state='completed', complete=complete, passed=complete, actual_wrapper_exit_code=code,
                     error=error, limit_stop_reason=reason, elapsed_seconds=time.monotonic() - start,
                     peak_observed_rss_kib=peak, actual_peak_child_rss_kib=actual_peak,
                     protected_unchanged=same, prepared_inputs_unchanged=inputs_same,
                     source=dict(path=str(SOURCE.relative_to(c.ROOT)), bytes=SOURCE.stat().st_size,
                                 sha256=c.sha(SOURCE)) if SOURCE.exists() else None)
        c.write(run / 'process-report.json', state)
        c.write(run / 'terminal-proof.json', dict(run_id=run.name,
                process_report_sha256=c.sha(run / 'process-report.json'), complete=complete))
        (run / 'wrapper.exit-code').write_text(str(code) + '\n')
    print(json.dumps(state, indent=2), flush=True)
    return code


if __name__ == '__main__':
    sys.exit(main())

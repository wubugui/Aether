#!/usr/bin/env python3
"""Source-only default; explicit flag admits one bounded read-only Blender child."""
import argparse
import os
from pathlib import Path
import shutil
import signal
import sys
import tempfile
import time
import traceback
sys.dont_write_bytecode = True
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard58k as g
import bounded_support58k as support
import run_import58k as inherited
c = g.c
NATIVE_SECONDS = 30
TOTAL_SECONDS = 60


def frozen_inputs():
    result = inherited.frozen_inputs()
    freeze = g.HERE / 'preparation-freeze.json'
    data = c.read(freeze)
    for path, row in data['files'].items():
        result[str(c.ROOT / path)] = row['sha256']
    result[str(freeze)] = c.sha(freeze)
    _, changed, errors = support.inspect_inputs(result)
    c.require(not changed and not errors, 'Frozen input identities: ' + repr(changed + errors))
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--run-approved-normal-readback', action='store_true')
    args = parser.parse_args()
    if not args.run_approved_normal_readback:
        print('Prepared only. One read-only Blender normal collection requires parent scheduling.'); return 0
    c.require(not (g.HERE / 'native-terminal.json').exists(), 'Completed attempt retained; no rerun')
    with (g.HERE / 'native-attempt.json').open('x') as admitted:
        c.json.dump(dict(pid=os.getpid(), state='admitted_not_completion', time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())), admitted)
        admitted.flush(); os.fsync(admitted.fileno())
    started = time.monotonic()
    run = Path(tempfile.mkdtemp(prefix='cloudbank58k-normal-readback-v1-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-', dir=c.ROOT / 'cloud-evidence'))
    print(run, flush=True)
    report = dict(version=g.VERSION, passed=False, state='preparing', run=str(run), stages=[],
                  limits=dict(native_seconds=NATIVE_SECONDS, total_seconds=TOTAL_SECONDS, cpu_threads=2,
                              max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),
                  source_saved=False, export_performed=False, godot_started=False, world_loaded=False, images=0, visual_acceptance=False)
    before = {}; protected = {}; old_handlers = {}
    def stop(number, frame):
        raise InterruptedError('Wrapper signal ' + str(number))
    try:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
            old_handlers[sig] = signal.signal(sig, stop)
        signal.setitimer(signal.ITIMER_REAL, TOTAL_SECONDS)
        cpus = sorted(os.sched_getaffinity(0))[:2]; c.require(len(cpus) == 2, 'CPU2 available'); os.sched_setaffinity(0, cpus)
        before = frozen_inputs(); verified = c.source_preconditions()
        c.require(c.sha(c.BLENDER) == c.BLENDER_SHA, 'Pinned official executable')
        protected = inherited.file_manifest(inherited.PROJECT)
        support.atomic_json(run / 'main-project-before.json', protected)
        support.atomic_json(run / 'input-sha256.json', before)
        shutil.copytree(g.HERE, run / 'preparation-snapshot', ignore=shutil.ignore_patterns('__pycache__'))
        output = run / 'outputs'; output.mkdir()
        env = os.environ.copy(); env.pop('PYTHONOPTIMIZE', None)
        env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1')
        for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data'), ('BLENDER_USER_CONFIG', 'blender-config')]:
            path = run / name; path.mkdir(); env[key] = str(path)
        command = [str(c.BLENDER), '--factory-startup', '--disable-autoexec', '-b', '-t', '2', '--python-exit-code', '1', '--python', str(g.HERE / 'collect58k.py'), '--', '--out', str(output)]
        remaining = TOTAL_SECONDS - (time.monotonic() - started) - 3
        c.require(remaining > 0, 'Finite total budget')
        report['state'] = 'running'; support.atomic_json(run / 'wrapper-report.json', report)
        row = support.run_child(command, run, env, run, min(NATIVE_SECONDS, remaining), 'blender-normal-readback')
        report['stages'].append(row)
        c.require(support.process_passed(row), 'Native normal readback failed')
        terminal = c.read(output / 'native-result.json'); data = c.read(output / 'source-normal-arrays.json')
        c.require(terminal['version'] == g.VERSION and terminal['passed'] is True and terminal['state'] == 'completed' and terminal['pid'] == row['pid'], 'Native terminal/PID agreement')
        c.require(terminal['raw_sha256'] == c.sha(output / 'source-normal-arrays.json'), 'Native raw artifact binding')
        c.require(data['cpu_affinity'] == row['cpu_affinity'] == cpus, 'Native CPU affinity matches supervised launch')
        report['normal_validation'] = g.validate_readback(data, row['pid'], verified)
        c.require(terminal['validation'] == report['normal_validation'], 'Wrapper independent validation matches native')
        report.update(passed=True, state='completed')
    except BaseException:
        report.update(passed=False, state='failed', error=traceback.format_exc())
    finally:
        try:
            _, changed, errors = support.inspect_inputs(before)
            after = inherited.file_manifest(inherited.PROJECT)
            report.update(inputs_unchanged=bool(before and not changed and not errors), changed_inputs=changed,
                          input_read_errors=errors, main_project_unchanged=bool(protected and protected == after),
                          source_unchanged=c.sha(c.SOURCE) == c.SOURCE_SHA)
            report['passed'] = bool(report['passed'] and report['inputs_unchanged'] and report['main_project_unchanged'] and report['source_unchanged'])
            support.atomic_json(run / 'main-project-after.json', after)
        except BaseException:
            report.update(passed=False, finalization_error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)
        report['elapsed_seconds'] = time.monotonic() - started
        report['logged_errors'] = support.error_lines(sorted(run.glob('*.log')))
        if report['elapsed_seconds'] > TOTAL_SECONDS or report['logged_errors']:
            report['passed'] = False
        if not report['passed']:
            report['state'] = 'failed'
        support.atomic_json(run / 'wrapper-report.json', report)
        (run / 'wrapper.exit-code').write_text('0\n' if report['passed'] else '1\n')
        c.write(g.HERE / 'native-terminal.json', dict(passed=report['passed'], run=str(run), wrapper_report_sha256=c.sha(run / 'wrapper-report.json')))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

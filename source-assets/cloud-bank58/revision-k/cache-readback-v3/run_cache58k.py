#!/usr/bin/env python3
"""Default preparation only. One scheduled cache read/save/fresh reload; no import."""
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
import cache_guard58k as g
import run_transfer58k as previous
import run_import58k as base
import bounded_support58k as support
c = g.c
TOTAL_SECONDS = 120
NATIVE_SECONDS = (20, 20)


def frozen_inputs():
    inputs = previous.frozen_inputs(); path = g.HERE / 'preparation-freeze.json'
    inputs.update({str(c.ROOT / name): row['sha256'] for name, row in c.read(path)['files'].items()})
    inputs[str(path)] = c.sha(path)
    _, changed, errors = support.inspect_inputs(inputs)
    c.require(not changed and not errors, 'Fixed preparation/protected input identities ' + repr(changed+errors))
    return inputs


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--run-approved-cache-readback', action='store_true'); args = parser.parse_args()
    if not args.run_approved_cache_readback:
        print('Prepared only. No import, GLB derivation, Blender or Godot process.'); return 0
    c.require(not (g.HERE / 'native-terminal.json').exists(), 'Prior terminal retained; no rerun')
    with (g.HERE / 'native-attempt.json').open('x') as marker:
        c.json.dump(dict(pid=os.getpid(), state='admitted_not_completion', time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())), marker)
        marker.flush(); os.fsync(marker.fileno())
    started = time.monotonic()
    run = Path(tempfile.mkdtemp(prefix='cloudbank58k-cache-readback-v3-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-', dir=c.ROOT / 'cloud-evidence'))
    print(run, flush=True)
    report = dict(version=g.VERSION, passed=False, state='preparing', stages=[], run=str(run),
                  limits=dict(total_seconds=TOTAL_SECONDS, native_stage_seconds=list(NATIVE_SECONDS), cpu_threads=2, max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),
                  blender_started=False, export_performed=False, glb_derived=False, editor_import_performed=False,
                  source_saved=False, world_loaded=False, images=0, visual_acceptance=False)
    before = {}; protected = {}; scratch = None; handlers = {}
    def stop(number, frame):
        raise InterruptedError('Wrapper signal ' + str(number))
    try:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
            handlers[sig] = signal.signal(sig, stop)
        signal.setitimer(signal.ITIMER_REAL, TOTAL_SECONDS)
        cpus = sorted(os.sched_getaffinity(0))[:2]; c.require(len(cpus) == 2, 'CPU2 available'); os.sched_setaffinity(0, cpus)
        before = frozen_inputs(); source, expected, _, _ = g.reference()
        c.require(c.sha(c.GODOT) == c.GODOT_SHA, 'Pinned official Godot binary')
        protected = base.file_manifest(base.PROJECT)
        support.atomic_json(run / 'main-project-before.json', protected); support.atomic_json(run / 'input-sha256.json', before)
        shutil.copytree(g.HERE, run / 'preparation-snapshot', ignore=shutil.ignore_patterns('__pycache__'))
        c.write(run / 'source-and-cache-proof.json', dict(source=source, expected_stored_surface=expected, cache_sha256=g.CACHE_SHA))
        scratch = Path(tempfile.mkdtemp(prefix='cloud58k-cache-readback-v3-', dir='/tmp')); report['temporary_project'] = str(scratch)
        (scratch / 'project.godot').write_text(base.PROJECT_TEXT)
        shutil.copy2(g.CACHE, scratch / 'imported.scn'); shutil.copy2(g.HERE / 'probe58k.gd', scratch / 'probe58k.gd')
        env = os.environ.copy(); env.pop('PYTHONOPTIMIZE', None)
        env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1')
        for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
            path = run / name; path.mkdir(); env[key] = str(path)
        artifacts = {path: c.sha(path) for path in [run / 'source-and-cache-proof.json', scratch / 'project.godot', scratch / 'probe58k.gd', scratch / 'imported.scn']}
        for mode, label, seconds in [('import', 'godot-cache-read-save', NATIVE_SECONDS[0]), ('reload', 'godot-fresh-reload', NATIVE_SECONDS[1])]:
            c.require(frozen_inputs() == before and all(c.sha(path) == sha for path, sha in artifacts.items()), 'Frozen inputs/artifacts before stage')
            remaining = TOTAL_SECONDS - (time.monotonic()-started) - 3; c.require(remaining > 0, 'Total budget available')
            destination = run / ('native-' + mode + '.json')
            command = [str(c.GODOT), '--headless', '--path', str(scratch), '--script', 'res://probe58k.gd', '--', mode, str(destination)]
            report['state'] = 'running'; support.atomic_json(run / 'wrapper-report.json', report)
            row = support.run_child(command, run, env, scratch, min(seconds, remaining), label)
            report['stages'].append(row); support.atomic_json(run / 'wrapper-report.json', report)
            c.require(support.process_passed(row), 'Native stage failed: ' + label)
            c.require(not support.error_lines([run / (label+'.stdout.log'), run / (label+'.stderr.log')]), 'Native logged error/leak')
            native = c.read(destination); report[mode + '_validation'] = g.validate(native, source, expected, mode, row['pid'])
            if mode == 'import':
                c.require(native['roundtrip_saved'] is True, 'Native snapshot saved')
                c.require((scratch / 'roundtrip.tscn').stat().st_size <= 500000, 'Native snapshot size cap')
                c.require('[ext_resource' not in (scratch / 'roundtrip.tscn').read_text(), 'Embedded resources only')
                imported = native
                artifacts.update({path: c.sha(path) for path in [destination, scratch / 'roundtrip.tscn']})
            else:
                c.require(native['pid'] != imported['pid'], 'Independent fresh reload process')
                c.require(all(native[key] == imported[key] for key in ['geometry', 'tangents', 'channels', 'format', 'stored_surface', 'material', 'transforms', 'aabb', 'aabb_storage']), 'Exact all-array including tangent native roundtrip')
        c.require(all(c.sha(path) == sha for path, sha in artifacts.items()), 'Earlier artifacts unchanged after reload')
        report.update(passed=True, state='completed')
    except BaseException:
        report.update(passed=False, state='failed', error=traceback.format_exc())
    finally:
        try:
            _, changed, errors = support.inspect_inputs(before); after = base.file_manifest(base.PROJECT)
            report.update(inputs_unchanged=bool(before and not changed and not errors), changed_inputs=changed, input_read_errors=errors,
                          main_project_unchanged=bool(protected and protected == after), source_unchanged=c.sha(c.SOURCE) == c.SOURCE_SHA)
            report['passed'] = bool(report['passed'] and report['inputs_unchanged'] and report['main_project_unchanged'] and report['source_unchanged'])
            support.atomic_json(run / 'main-project-after.json', after)
            if scratch:
                report['temporary_project_manifest'] = base.output_files(scratch)
                for name in ['project.godot', 'roundtrip.tscn']:
                    if (scratch / name).is_file():
                        shutil.copy2(scratch / name, run / name)
        except BaseException:
            report.update(passed=False, finalization_error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
        report['elapsed_seconds'] = time.monotonic()-started; report['logged_errors'] = support.error_lines(sorted(run.glob('*.log')))
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

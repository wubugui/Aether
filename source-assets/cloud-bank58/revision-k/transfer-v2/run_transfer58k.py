#!/usr/bin/env python3
"""Prepare by default. One explicit admission derives GLB and runs isolated Godot."""
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
import transfer58k as t
import run_readback58k as readback
import run_import58k as base
import bounded_support58k as support
c = t.c
TOTAL_SECONDS = 120
NATIVE_SECONDS = (30, 20, 20)


def frozen_inputs():
    result = readback.frozen_inputs()
    freeze = t.HERE / 'preparation-freeze.json'
    data = c.read(freeze)
    result.update({str(c.ROOT / path): row['sha256'] for path, row in data['files'].items()})
    result[str(freeze)] = c.sha(freeze)
    _, changed, errors = support.inspect_inputs(result)
    c.require(not changed and not errors, 'Frozen transfer input identities: ' + repr(changed + errors))
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--run-approved-transfer', action='store_true'); args = parser.parse_args()
    if not args.run_approved_transfer:
        print('Prepared only. No adjusted GLB or engine process. One transfer requires parent scheduling.'); return 0
    c.require(not (t.HERE / 'native-terminal.json').exists(), 'Completed attempt retained; no rerun')
    with (t.HERE / 'native-attempt.json').open('x') as admitted:
        c.json.dump(dict(pid=os.getpid(), state='admitted_not_completion', time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())), admitted)
        admitted.flush(); os.fsync(admitted.fileno())
    started = time.monotonic()
    run = Path(tempfile.mkdtemp(prefix='cloudbank58k-transfer-v2-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-', dir=c.ROOT / 'cloud-evidence'))
    print(run, flush=True)
    report = dict(version=t.VERSION, passed=False, state='preparing', run=str(run), stages=[],
                  limits=dict(total_seconds=TOTAL_SECONDS, native_stage_seconds=list(NATIVE_SECONDS), cpu_threads=2, max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),
                  source_saved=False, blender_started=False, export_performed=False, world_loaded=False, world_anchor_applied=False, images=0, visual_acceptance=False)
    before = {}; protected = {}; scratch = None; old_handlers = {}
    def stop(number, frame):
        raise InterruptedError('Wrapper signal ' + str(number))
    try:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
            old_handlers[sig] = signal.signal(sig, stop)
        signal.setitimer(signal.ITIMER_REAL, TOTAL_SECONDS)
        cpus = sorted(os.sched_getaffinity(0))[:2]; c.require(len(cpus) == 2, 'CPU2 available'); os.sched_setaffinity(0, cpus)
        before = frozen_inputs(); source = t.evidence_source()
        c.require(c.sha(c.GODOT) == c.GODOT_SHA, 'Pinned official Godot executable')
        protected = base.file_manifest(base.PROJECT)
        support.atomic_json(run / 'main-project-before.json', protected); support.atomic_json(run / 'input-sha256.json', before)
        shutil.copytree(t.HERE, run / 'preparation-snapshot', ignore=shutil.ignore_patterns('__pycache__'))
        c.require(c.sha(t.g.FAILED_GLB) == t.g.FAILED_GLB_SHA, 'Exact original raw exporter GLB')
        original = t.g.FAILED_GLB.read_bytes()
        adjusted, restoration = t.restore_bytes(original, source)
        (run / 'cloud58k-original-export.glb').write_bytes(original)
        (run / 'cloud58k-restored-corners.glb').write_bytes(adjusted)
        c.write(run / 'transfer-source.json', source); c.write(run / 'normal-restoration.json', restoration)
        report['normal_restoration'] = restoration
        scratch = Path(tempfile.mkdtemp(prefix='cloud58k-transfer-v2-', dir='/tmp')); report['temporary_project'] = str(scratch)
        (scratch / 'project.godot').write_text(base.PROJECT_TEXT)
        shutil.copy2(t.HERE / 'probe58k.gd', scratch / 'probe58k.gd')
        shutil.copy2(run / 'cloud58k-restored-corners.glb', scratch / 'cloud58k.glb')
        lines = ['[remap]', 'importer="scene"', 'importer_version=1', 'type="PackedScene"', '', '[deps]', 'source_file="res://cloud58k.glb"', '', '[params]']
        for key, value in base.IMPORT_PARAMETERS.items():
            lines.append(key + '=' + c.json.dumps(value, separators=(',', ':')))
        (scratch / 'cloud58k.glb.import').write_text('\n'.join(lines) + '\n')
        env = os.environ.copy(); env.pop('PYTHONOPTIMIZE', None)
        env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1')
        for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data')]:
            path = run / name; path.mkdir(); env[key] = str(path)
        commands = [[str(c.GODOT), '--headless', '--editor', '--path', str(scratch), '--import'],
                    [str(c.GODOT), '--headless', '--path', str(scratch), '--script', 'res://probe58k.gd', '--', 'import', str(run / 'godot-import.json')],
                    [str(c.GODOT), '--headless', '--path', str(scratch), '--script', 'res://probe58k.gd', '--', 'reload', str(run / 'godot-reload.json')]]
        labels = ['godot-editor-import', 'godot-import-readback', 'godot-fresh-reload']
        artifacts = {path: c.sha(path) for path in [run / 'cloud58k-original-export.glb', run / 'cloud58k-restored-corners.glb', run / 'transfer-source.json', run / 'normal-restoration.json', scratch / 'project.godot', scratch / 'probe58k.gd', scratch / 'cloud58k.glb']}
        for index, (command, label, limit) in enumerate(zip(commands, labels, NATIVE_SECONDS)):
            c.require(frozen_inputs() == before, 'Frozen inputs unchanged before native stage')
            c.require(all(c.sha(path) == value for path, value in artifacts.items()), 'Prior artifacts unchanged')
            remaining = TOTAL_SECONDS - (time.monotonic() - started) - 3; c.require(remaining > 0, 'Total budget available')
            report['state'] = 'running'; support.atomic_json(run / 'wrapper-report.json', report)
            row = support.run_child(command, run, env, scratch, min(limit, remaining), label)
            report['stages'].append(row); support.atomic_json(run / 'wrapper-report.json', report)
            c.require(support.process_passed(row), 'Native stage failed: ' + label)
            c.require(not support.error_lines([run / (label + '.stdout.log'), run / (label + '.stderr.log')]), 'Native logged error/leak')
            if index == 0:
                c.require((scratch / 'cloud58k.glb.import').is_file() and (scratch / '.godot/imported').is_dir(), 'Actual isolated import outputs')
            elif index == 1:
                imported = base.native_report(run / 'godot-import.json', 'import')
                c.require(imported['pid'] == row['pid'], 'Import result belongs to supervised native PID')
                report['import_validation'] = base.validate_native(imported, source)
                c.require(imported['roundtrip_saved'] is True, 'Native roundtrip saved')
                c.require(all(imported['import_settings'].get(key) == value for key, value in base.IMPORT_PARAMETERS.items()), 'Actual unchanged importer options')
                c.require((scratch / 'roundtrip.tscn').stat().st_size <= 500000, 'Native scene size cap')
                c.require('[ext_resource' not in (scratch / 'roundtrip.tscn').read_text(), 'Embedded native resources only')
                artifacts.update({path: c.sha(path) for path in [run / 'godot-import.json', scratch / 'roundtrip.tscn', scratch / 'cloud58k.glb.import']})
            else:
                reloaded = base.native_report(run / 'godot-reload.json', 'reload')
                c.require(reloaded['pid'] == row['pid'] and reloaded['pid'] != imported['pid'], 'Fresh supervised reload process')
                report['reload_validation'] = base.validate_native(reloaded, source)
                c.require(not reloaded['dependencies'], 'Fresh native snapshot has no external dependencies')
                c.require(all(reloaded[key] == imported[key] for key in ('geometry', 'material', 'transforms', 'aabb')), 'Exact native save/fresh-load identity')
        c.require(all(c.sha(path) == value for path, value in artifacts.items()), 'All transfer artifacts unchanged after final native stage')
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
                for name in ['project.godot', 'cloud58k.glb.import', 'roundtrip.tscn']:
                    if (scratch / name).is_file():
                        shutil.copy2(scratch / name, run / name)
        except BaseException:
            report.update(passed=False, finalization_error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)
        report['elapsed_seconds'] = time.monotonic() - started; report['logged_errors'] = support.error_lines(sorted(run.glob('*.log')))
        if report['elapsed_seconds'] > TOTAL_SECONDS or report['logged_errors']:
            report['passed'] = False
        if not report['passed']:
            report['state'] = 'failed'
        support.atomic_json(run / 'wrapper-report.json', report)
        (run / 'wrapper.exit-code').write_text('0\n' if report['passed'] else '1\n')
        c.write(t.HERE / 'native-terminal.json', dict(passed=report['passed'], run=str(run), wrapper_report_sha256=c.sha(run / 'wrapper-report.json')))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Explicit --run only: real-display GL MultiMesh fixture, CPU2, <=60s; no game/world."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import sys
import tempfile
import time

sys.dont_write_bytecode = True
from wrapper_support import atomic_json, error_lines, inspect_inputs, process_passed, run_child, sha, strict_json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GODOT = ROOT.parent / 'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
EXPECTED_GODOT = 'db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
OLD = [ROOT / 'cloud-evidence' / name for name in [
    'nearbay61-orbit-renderer-20261001T194004Z-n8gym6pm',
    'nearbay61-orbit-renderer-20261002T023336Z-nuh5s3o7',
    'nearbay61-orbit-renderer-20261002T033202Z-i141mgll',
    'nearbay61-orbit-renderer-20261002T040614Z-kyawbpny',
    'nearbay61-orbit-renderer-20261002T044043Z-8wi327py',
]]
PRIOR = ROOT / 'cloud-evidence/player-nearbay61-renderer-20261001T131646Z-f5163t8s/input-sha256.json'
PRIOR_SHA = '3329d137d9c43c0fbd2f43f8ca52c4529b8590d891c5fca6fdd376fe3c2b1db9'
PROJECT_TEXT = '''config_version=5
[application]
config/name="Orbit61 continuous v6 native GL fixture"
[display]
window/size/viewport_width=320
window/size/viewport_height=180
window/size/window_width_override=320
window/size/window_height_override=180
[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
[threading]
worker_pool/max_threads=2
'''


def source_paths() -> list[Path]:
    return sorted(p for p in HERE.parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts)


def manifest(paths) -> dict[str, str]:
    return {str(path): sha(path) for path in paths}


def protected_manifest() -> dict[str, str]:
    if sha(PRIOR) != PRIOR_SHA:
        raise RuntimeError('Historical 1477 input manifest changed')
    original = strict_json(PRIOR)
    if len(original) != 1477:
        raise RuntimeError('Expected unchanged historical 1477 inputs')
    _, changed, errors = inspect_inputs(original)
    if changed or errors:
        raise RuntimeError('Historical input mismatch: ' + repr(changed or errors))
    paths = [PRIOR]
    for old in OLD:
        if not old.is_dir() or not (old / 'wrapper-report.json').is_file():
            raise RuntimeError('Expected complete saved old failure directory: ' + str(old))
        paths.extend(p for p in old.rglob('*') if p.is_file())
    return dict(sorted({**original, **manifest(paths)}.items()))


def required_checks() -> list[str]:
    names = re.findall(r'(?:record|check_guard)\("([^"\n]+)"', (HERE / 'fixture.gd').read_text())
    if not names or len(names) != len(set(names)):
        raise RuntimeError('Invalid native fixture check-name contract')
    return names


def validate_result(path: Path, expected_names: list[str]) -> dict:
    result = strict_json(path)
    if result.get('version') != 'orbit61-continuous-v6' or result.get('passed') is not True:
        raise ValueError('Native result lacks explicit successful versioned completion')
    if result.get('display_backend') != 'X11':
        raise ValueError('Native result lacks actual display backend')
    if result.get('rendering_method') != 'gl_compatibility' or result.get('rendering_driver') not in ('opengl3', 'opengl3_es', 'opengl3_angle') or result.get('world_loaded') is not False:
        raise ValueError('Native fixture rendering/scope mismatch')
    engine = result.get('engine', {})
    if not isinstance(engine, dict) or [engine.get(k) for k in ('major', 'minor', 'patch')] != [4, 5, 1]:
        raise ValueError('Native fixture engine version mismatch')
    checks = result.get('checks')
    if not isinstance(checks, list) or not checks or any(not isinstance(row, dict) or row.get('passed') is not True or not isinstance(row.get('name'), str) for row in checks):
        raise ValueError('Native checks absent, malformed, or failed')
    names = [row['name'] for row in checks]
    if len(names) != len(set(names)) or set(names) != set(expected_names):
        raise ValueError('Native result check set is incomplete, duplicated, or unexpected')
    return result


def execute(out: Path) -> dict:
    report = {'version': 'orbit61-continuous-v6', 'status': 'preparing', 'passed': False,
              'world_loaded': False, 'images': 0, 'orbit_runtime_passed': False,
              'maximum_requested_seconds': 60, 'watchdog_seconds': 59,
              'wrapper_received_signal': None, 'process': None, 'inputs_unchanged': False,
              'input_aftercheck_attempted': False, 'output': str(out)}
    before, protected = {}, {}
    finalizing = False

    def cancel(signum, _frame):
        report['wrapper_received_signal'] = signum
        if not finalizing:
            raise InterruptedError(f'Wrapper received signal {signum}')

    previous = {sig: signal.signal(sig, cancel) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        atomic_json(out / 'wrapper-report.json', report)
        if not os.environ.get('DISPLAY'):
            raise RuntimeError('Actual DISPLAY required for native GL setters/readbacks; no headless fallback')
        if sha(GODOT) != EXPECTED_GODOT:
            raise RuntimeError('Godot 4.5.1 binary SHA256 mismatch')
        protected = protected_manifest()
        before = manifest([GODOT, *source_paths()])
        names = required_checks()
        atomic_json(out / 'protected-before.json', protected)
        atomic_json(out / 'sources-before.json', before)
        report.update(protected_input_count=len(protected), source_input_count=len(before),
                      godot_sha256=EXPECTED_GODOT, expected_check_names=names)
        for path in source_paths():
            target = out / 'source-snapshot' / path.relative_to(HERE.parent)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        scratch = Path(tempfile.mkdtemp(prefix='orbit61-continuous-v6-', dir='/tmp'))
        (scratch / 'project.godot').write_text(PROJECT_TEXT)
        shutil.copy2(scratch / 'project.godot', out / 'synthetic-project.godot')
        env = os.environ.copy()
        env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1')
        for key, sub in [('XDG_DATA_HOME', 'data'), ('XDG_CACHE_HOME', 'cache'), ('XDG_CONFIG_HOME', 'config')]:
            (scratch / sub).mkdir()
            env[key] = str(scratch / sub)
        command = [str(GODOT), '--path', str(scratch), '--display-driver', 'x11',
                   '--rendering-method', 'gl_compatibility', '--audio-driver', 'Dummy',
                   '--resolution', '320x180', '--windowed', '--script', str(HERE / 'fixture.gd'),
                   '--', str(out / 'result.json')]
        # Revalidate old identities and every source after snapshots, at admission.
        if protected_manifest() != protected or manifest([GODOT, *source_paths()]) != before:
            raise RuntimeError('Input changed between preparation and child admission')
        report['status'] = 'running'
        row = run_child(command, out, env, scratch, 59, 'fixture')
        report['process'] = row
        if row.get('wrapper_received_signal') is not None:
            report['wrapper_received_signal'] = row['wrapper_received_signal']
        report.update(returncode=row['returncode'], native_exit_observed=row['native_exit_observed'],
                      wall_seconds=row['wall_seconds'], timeout=row['timeout_triggered'],
                      cpu_affinity=row['cpu_affinity'], max_rss_kib=row['max_rss_kib'])
        report['logged_errors'] = error_lines(sorted(out.glob('*.log')))
        native = validate_result(out / 'result.json', names)
        report['native_checks_count'] = len(native['checks'])
        report.update(display_backend=native['display_backend'], rendering_method=native['rendering_method'], rendering_driver=native['rendering_driver'])
        report['native_result_sha256'] = sha(out / 'result.json')
        report.update(status='finished', passed=bool(process_passed(row) and row['wall_seconds'] <= 60 and not report['logged_errors']))
    except BaseException as exc:
        report.update(status='wrapper_exception', exception=repr(exc), passed=False)
    finally:
        finalizing = True
        report['input_aftercheck_attempted'] = True
        try:
            after, changed, errors = inspect_inputs(before)
            protected_after, protected_changed, protected_errors = inspect_inputs(protected)
            atomic_json(out / 'sources-after.json', after)
            atomic_json(out / 'protected-after.json', protected_after)
            report.update(changed_inputs=changed, protected_changed_inputs=protected_changed,
                          input_recheck_errors=errors + protected_errors,
                          inputs_unchanged=bool(before and protected and not changed and not protected_changed and not errors and not protected_errors))
            # Fixed expected old identities still govern; never adopt a changed baseline.
            report['protected_manifest_rechecked'] = protected_manifest() == protected if protected else False
            report['source_set_unchanged'] = set(before) == {str(p) for p in [GODOT, *source_paths()]} if before else False
            if not report['inputs_unchanged'] or not report['protected_manifest_rechecked'] or not report['source_set_unchanged']:
                report['passed'] = False
        except BaseException as exc:
            report.update(input_recheck_error=repr(exc), inputs_unchanged=False, passed=False)
        if report['wrapper_received_signal'] is not None:
            report['passed'] = False
        try:
            atomic_json(out / 'wrapper-report.json', report)
            (out / 'exit-code.txt').write_text('0\n' if report['passed'] else '1\n')
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        print('Source preparation only. Use --run in the parent-coordinated real-display CPU2 window.')
        return 0
    out = Path(tempfile.mkdtemp(prefix='nearbay61-continuous-v6-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-', dir=ROOT / 'cloud-evidence'))
    print(out, flush=True)
    report = execute(out)
    print(json.dumps(report, indent=2), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

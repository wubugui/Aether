#!/usr/bin/env python3
"""Single-child runner. Default is parse only; renderer execution is explicit.

Evidence and immutable source snapshots survive all child failures, including
SIGKILL/OOM. No project/scene save is performed. Per-run XDG userdata is external
to the project. The parent schedules --run-renderer after other heavy work stops.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

ROOT = Path('/workspace/scratch/a29d03198654')
AETHER = ROOT / 'Aether'
PROJECT = AETHER / 'candidates/round40-exclusive-20260930/project'
GODOT = ROOT / 'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
SCRIPT = AETHER / 'source-assets/observation55/verify_player_flight55.gd'
INTAKE = AETHER / 'cloud-evidence/free-flight51b-readonly-plan/source-intake.json'
BUILD = PROJECT / 'scenes/candidate51b/build-report-51b.json'
AUDIT = AETHER / 'cloud-evidence/reflection51b-motion-20261001T041545Z-WCymsr/images/reflection-motion-report.json'
FULL_AUDIT = AETHER / 'cloud-evidence/reflection51b-verify-full-20261001T032554Z-975juK/images/report.json'
SCENE_SHA = '65d43959d704e7406c56f4003df5063fad37572e42afd9a8025fbed55dbba286'


def digest(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def source_manifest() -> dict[str, str]:
    intake = json.loads(INTAKE.read_text())
    build = json.loads(BUILD.read_text())
    paths = {PROJECT / name for name in intake['sources']}
    paths.update(PROJECT / item['path'].removeprefix('res://') for item in build['independent_assets'])
    paths.update([PROJECT / 'scripts/lake_reflection51b.gd', BUILD, INTAKE, AUDIT, FULL_AUDIT, SCRIPT, Path(__file__).resolve()])
    paths.update([PROJECT/'scenes/candidate55-observation/Game55Observation.tscn',PROJECT/'scenes/candidate53d-west/Game53dWest.tscn',PROJECT/'scripts/game55_observation.gd',PROJECT/'assets/observation55/lake_observation_poses.json'])
    return {str(path): digest(path) for path in sorted(paths)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--parse-only', action='store_true', help='Headless --check-only; never loads or instantiates scene (default)')
    modes.add_argument('--run-renderer', action='store_true', help='Parent-approved single real-renderer flight evidence run')
    parser.add_argument('--wall-timeout', type=float, default=1800, help='Whole-child wall timeout, seconds; separate from 5s physics watchdog')
    args = parser.parse_args()
    mode = 'renderer' if args.run_renderer else 'parse'
    out = Path(tempfile.mkdtemp(prefix=f'player-flight55-{mode}-{time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())}-', dir=AETHER / 'cloud-evidence'))
    user_root = Path(tempfile.mkdtemp(prefix=f'player-flight55-{mode}-', dir=ROOT / 'tools-feiting'))
    print(out, flush=True)
    (ROOT / 'tools-feiting/feiting-player-flight55-last.txt').write_text(str(out) + '\n')
    shutil.copy2(Path(__file__), out / 'run_player_flight55.py')
    shutil.copy2(SCRIPT, out / SCRIPT.name)
    shutil.copy2(INTAKE, out / INTAKE.name)
    for name in ['game.gd', 'game42b.gd', 'airship_body.gd', 'game_tests.gd', 'open_world.gd', 'lake_reflection51b.gd']:
        shutil.copy2(PROJECT / 'scripts' / name, out / name)
    (out / 'SCOPE.txt').write_text(
        'Exact independently inherited Game55Observation. One ordinary scene, unchanged physical input and move_and_slide. '
        'Existing reference1128 navigation is a teleport, explicitly outside flight evidence. '
        'Two existing body shapes plus padded full-visible-mesh envelope must clear25m of active actual solids. '
        'Physical W .75 simulation seconds, release .50, physical Space then stable stop .25. '
        '20m displacement/path cap and5s simulation watchdog release all keys and freeze on failure. '
        'time_scale1; normal callbacks stay active. Three actual start/moving/stopped captures. '
        'No scene save, second scene instance, gameplay patch, user progress save or full1500-check rerun. '
        'All userdata is fresh under tools-feiting. Wrapper records child ru_maxrss, exit status and signal. '
        'SIGKILL may prevent graceful key-release/freeze, but kills only the isolated child; latest atomic partial report is retained. '
        'Scripted physical events do not prove real GUI keyboard focus, hardware GPU, full-route flight, '
        'known1344 two-pixel conversion gate, inherited350m motion or total GOAL acceptance.\n'
    )
    env = os.environ.copy()
    if args.run_renderer:
        scope=Path((ROOT/'tools-feiting/observation55-scope-last.txt').read_text().strip())/'process-report.json'
        if json.loads(scope.read_text()).get('passed') is not True: raise SystemExit('Real55 scope gate required')
        env['OBSERVATION55_SCOPE']=str(scope)
    for key, folder in [('XDG_DATA_HOME', 'data'), ('XDG_CACHE_HOME', 'cache'), ('XDG_CONFIG_HOME', 'config')]:
        path = user_root / folder
        path.mkdir()
        env[key] = str(path)
    before = source_manifest()
    atomic_json(out / 'input-sha256.json', before)
    identity_ok = before[str(PROJECT / 'scenes/candidate55-observation/Game55Observation.tscn')] == SCENE_SHA
    command = [str(GODOT), '--path', str(PROJECT)]
    if args.run_renderer:
        command += ['--rendering-method', 'gl_compatibility', '--audio-driver', 'Dummy', '--disable-vsync', '--script', str(SCRIPT), '--', f'--output-dir={out / "images"}']
    else:
        command += ['--headless', '--check-only', '--script', str(SCRIPT)]
    wrapper = {
        'mode': mode, 'status': 'before_child', 'candidate_sha256': SCENE_SHA,
        'scene_identity_matches': identity_ok, 'command': command, 'userdata_root': str(user_root),
        'output': str(out), 'child_started': False, 'child_max_rss_kib': None,
        'child_signal': None, 'child_exit_code': None, 'wall_timeout_seconds': args.wall_timeout,
        'renderer_run_performed': args.run_renderer, 'actual_player_input_flight_passed': False,
        'parse_success_is_not_runtime_evidence': True,
    }
    atomic_json(out / 'wrapper-report.json', wrapper)
    if not identity_ok:
        wrapper['status'] = 'identity_mismatch_no_child'
        atomic_json(out / 'wrapper-report.json', wrapper)
        return 2
    started = time.monotonic()
    interrupted: int | None = None
    terminate_started: float | None = None
    child: subprocess.Popen | None = None

    def forward_stop(signum: int, _frame: object) -> None:
        nonlocal interrupted, terminate_started
        interrupted = signum
        terminate_started = time.monotonic()
        if child is not None:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    signal.signal(signal.SIGINT, forward_stop)
    signal.signal(signal.SIGTERM, forward_stop)
    with (out / 'child.stdout.log').open('wb') as stdout, (out / 'child.stderr.log').open('wb') as stderr:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, cwd=PROJECT, start_new_session=True)
        wrapper.update(status='child_running', child_started=True, child_pid=child.pid)
        atomic_json(out / 'wrapper-report.json', wrapper)
        while True:
            waited, status, usage = os.wait4(child.pid, os.WNOHANG)
            if waited:
                child.returncode = os.waitstatus_to_exitcode(status)
                break
            now = time.monotonic()
            if now - started > args.wall_timeout and terminate_started is None:
                wrapper['wall_timeout_triggered'] = True
                terminate_started = now
                os.killpg(child.pid, signal.SIGTERM)
                atomic_json(out / 'wrapper-report.json', wrapper)
            if terminate_started is not None and now - terminate_started > 10:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            time.sleep(0.25)
    code = child.returncode
    wrapper.update(status='child_finished', child_max_rss_kib=usage.ru_maxrss, child_user_cpu_seconds=usage.ru_utime,
                   child_system_cpu_seconds=usage.ru_stime, wall_seconds=time.monotonic() - started,
                   child_exit_code=code if code >= 0 else None, child_signal=-code if code < 0 else None,
                   child_signal_name=signal.Signals(-code).name if code < 0 else None,
                   wrapper_received_signal=interrupted, raw_wait_status=status)
    after = source_manifest()
    atomic_json(out / 'output-sha256.json', after)
    wrapper['sources_unchanged'] = before == after
    wrapper['changed_sources'] = [path for path in before if before[path] != after.get(path)]
    runtime_report = out / 'images/player-flight-report.json'
    if runtime_report.exists():
        report = json.loads(runtime_report.read_text())
        wrapper['last_runtime_stage'] = report.get('stage')
        wrapper['runtime_report_complete'] = report.get('complete', False)
        wrapper['actual_player_input_flight_passed'] = bool(code == 0 and before == after and report.get('complete') and report.get('actual_player_input_flight_passed'))
    logs=(out/'child.stdout.log').read_text(errors='replace')+'\n'+(out/'child.stderr.log').read_text(errors='replace')
    errors=[x for x in logs.splitlines() if x.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in x.lower()]
    wrapper['logged_errors']=errors
    if errors: wrapper['actual_player_input_flight_passed']=False
    wrapper['parse_passed'] = mode == 'parse' and code == 0 and before == after
    wrapper['userdata_files_after'] = [str(path.relative_to(user_root)) for path in sorted(user_root.rglob('*')) if path.is_file()]
    atomic_json(out / 'wrapper-report.json', wrapper)
    shell_code = code if code >= 0 else 128 - code
    if before != after:
        shell_code = 3
    if mode == 'renderer' and code == 0 and not wrapper['actual_player_input_flight_passed']:
        shell_code = 4
    (out / 'wrapper-exitcode.txt').write_text(str(shell_code) + '\n')
    print(json.dumps({key: wrapper.get(key) for key in ['mode', 'child_exit_code', 'child_signal_name', 'child_max_rss_kib', 'sources_unchanged', 'parse_passed', 'actual_player_input_flight_passed', 'last_runtime_stage']}, indent=2), flush=True)
    print(f'Evidence retained: {out}', flush=True)
    return shell_code


if __name__ == '__main__':
    raise SystemExit(main())

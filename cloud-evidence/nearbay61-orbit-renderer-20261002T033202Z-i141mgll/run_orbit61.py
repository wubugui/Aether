#!/usr/bin/env python3
"""Default: read-only source/plan checks, no Godot process and no output files.

Explicit --parse-only is a future check-only Godot invocation.
Explicit --run-renderer is the first anchored-orbit item, not a flight test.
The parent coordinates the actual display and heavy-job window separately.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
AETHER = HERE.parents[1]
ROOT = AETHER.parent
PROJECT = AETHER / 'candidates/round40-exclusive-20260930/project'
GODOT = ROOT / 'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
PRIOR = AETHER / 'cloud-evidence/player-nearbay61-renderer-20261001T131646Z-f5163t8s/input-sha256.json'
OLD_CORRIDOR = AETHER / 'source-assets/coast61-nearbay-flight-plan/static-corridor.json'
SCRIPT = HERE / 'verify_orbit61.gd'
HELPER = HERE / 'visible_geometry61.gd'
SCENE = PROJECT / 'scenes/candidate61-coast/Game61Coast.tscn'
SCENE_SHA = 'dff06de665e1fa1f6ab74ff3cdf4e91442e1ac322839a37718e799f0d7fa44d8'


def digest(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def source_manifest() -> dict[str, str]:
    old = json.loads(PRIOR.read_text())
    assert len(old) == 1477, 'The named previous run must retain its1477 inputs'
    for raw, expected in old.items():
        path = Path(raw)
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError('Previous frozen input changed or missing: ' + raw)
    own = [p for p in HERE.iterdir() if p.suffix in {'.py', '.gd', '.md'} or p.name == 'plan.json']
    result = {raw: digest(Path(raw)) for raw in old}
    result.update({str(p): digest(p) for p in [PRIOR, *own]})
    return dict(sorted(result.items()))


def static_checks() -> dict:
    ast.parse(Path(__file__).read_text())
    manifest = source_manifest()
    assert digest(SCENE) == SCENE_SHA
    old = json.loads(OLD_CORRIDOR.read_text())
    plan = json.loads((HERE / 'plan.json').read_text())
    start = plan['fixture_position']
    direction = plan['future_flight_design_only']['direction_xz']
    old_start = old['initial_fixture_ship_position']
    delta = [start[0] - old_start[0], start[2] - old_start[2]]
    along = sum(a * b for a, b in zip(delta, direction))
    lateral = delta[0] * -direction[1] + delta[1] * direction[0]
    assert abs(lateral) < 1e-10
    assert math.isclose(along, 90.13878188659973)
    length = plan['future_flight_design_only']['preflight_corridor_m']
    assert along - 25 >= -25 and along + length + 25 <= old['horizontal_length_m'] + 25
    script = SCRIPT.read_text()
    assert 'const STEP_RADIANS := .05' in script
    assert 'key(KEY_W,true)' not in script and 'key(KEY_SPACE,true)' not in script
    assert 'game.orbit=' not in script.replace('game.orbit==', '')
    assert script.count('game.airship.position=') == 1
    assert script.count('game.airship.rotation=') == 1
    assert script.count('game.camera.position=') == 1
    assert script.count('game.camera.look_at(') == 1
    assert '0xffffffff' in script and 'project_position(pixel,game.camera.near)' in script
    assert 'process_priority=100000' in script
    assert '"nearshore_pixel_coverage_passed":false' in script
    helper = HELPER.read_text()
    assert 'surface_get_arrays(surface)' in helper
    assert 'shape.set_faces(faces)' in helper
    assert 'mesh.get_faces(' not in helper
    assert 'revolution' in helper and '9.0' in helper and 'flag_line' in helper
    return {
        'status': 'source_preparation_static_checks_only',
        'previous_frozen_inputs': 1477, 'all_previous_inputs_match': True,
        'new_manifest_count': len(manifest),
        'new_source_sha256': {str(p.relative_to(AETHER)): digest(p) for p in sorted(HERE.iterdir()) if p.suffix in {'.py', '.gd', '.md'} or p.name == 'plan.json'},
        'python_ast_passed': True, 'source_scope_checks_passed': True,
        'new_centerline_old_along_m': along, 'new_centerline_old_lateral_m': lateral,
        'new_padded_interval_in_old_coordinates_m': [along - 25, along + length + 25],
        'old_padded_interval_m': [-25, old['horizontal_length_m'] + 25],
        'ship_static_terrain_subset_proved': True,
        'camera_orbit_covered_by_old_corridor': False,
        'godot_invoked': False, 'godot_parse_passed': False,
        'first_item_runtime_passed': False, 'nearshore_pixel_coverage_passed': False,
        'flight_attempted': False, 'scope': 'No files written by this static check. Source assertions and geometry arithmetic do not establish GDScript parsing or runtime behavior.'}


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def child_run(command: list[str], out: Path, env: dict, timeout: float, label: str) -> dict:
    started = time.monotonic()
    killed = False
    stop_at = None
    external_signal = None
    with (out / f'{label}.stdout.log').open('wb') as stdout, (out / f'{label}.stderr.log').open('wb') as stderr:
        child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, cwd=PROJECT, start_new_session=True)
        atomic_json(out / f'{label}.process.json', {'status': 'running', 'pid': child.pid, 'command': command})

        def forward_stop(signum: int, _frame: object) -> None:
            nonlocal stop_at, external_signal
            external_signal = signum
            stop_at = time.monotonic()
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

        previous_handlers = {sig: signal.signal(sig, forward_stop) for sig in (signal.SIGINT, signal.SIGTERM)}
        try:
            while True:
                waited, status, usage = os.wait4(child.pid, os.WNOHANG)
                if waited:
                    code = os.waitstatus_to_exitcode(status)
                    child.returncode = code
                    break
                now = time.monotonic()
                if now - started > timeout and stop_at is None:
                    try:
                        os.killpg(child.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    stop_at = now
                if stop_at is not None and now - stop_at > 10 and not killed:
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    killed = True
                time.sleep(.25)
        except BaseException:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
            raise
        finally:
            for sig, handler in previous_handlers.items():
                signal.signal(sig, handler)
    result = {'status': 'finished', 'command': command, 'returncode': code,
              'signal': -code if code < 0 else None, 'wall_seconds': time.monotonic() - started,
              'max_rss_kib': usage.ru_maxrss, 'timeout_triggered': stop_at is not None and external_signal is None,
              'wrapper_received_signal': external_signal}
    atomic_json(out / f'{label}.process.json', result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--static-only', action='store_true')
    mode.add_argument('--parse-only', action='store_true')
    mode.add_argument('--run-renderer', action='store_true')
    parser.add_argument('--wall-timeout', type=float, default=720)
    args = parser.parse_args()
    preparation = static_checks()
    if not args.parse_only and not args.run_renderer:
        print(json.dumps(preparation, indent=2))
        return 0
    if args.run_renderer and not os.environ.get('DISPLAY'):
        raise SystemExit('Actual display required; no headless fallback')
    selected = 'renderer' if args.run_renderer else 'parse'
    out = Path(tempfile.mkdtemp(prefix=f'nearbay61-orbit-{selected}-{time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())}-', dir=AETHER / 'cloud-evidence'))
    userdata = Path(tempfile.mkdtemp(prefix='nearbay61-orbit-', dir=ROOT / 'tools-feiting'))
    print(out, flush=True)
    before = source_manifest()
    atomic_json(out / 'input-sha256.json', before)
    atomic_json(out / 'source-preparation.json', preparation)
    for path in HERE.iterdir():
        if path.is_file():
            shutil.copy2(path, out / path.name)
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1', ORBIT61_INPUTS=str(out / 'input-sha256.json'))
    for key, folder in [('XDG_DATA_HOME', 'data'), ('XDG_CACHE_HOME', 'cache'), ('XDG_CONFIG_HOME', 'config')]:
        path = userdata / folder
        path.mkdir()
        env[key] = str(path)
    processes = []
    if args.run_renderer:
        command = [str(GODOT), '--path', str(PROJECT), '--rendering-method', 'gl_compatibility', '--audio-driver', 'Dummy', '--disable-vsync', '--script', str(SCRIPT), '--', f'--output-dir={out / "images"}']
        processes.append(child_run(command, out, env, args.wall_timeout, 'renderer'))
    else:
        for script in [HELPER, SCRIPT]:
            command = [str(GODOT), '--path', str(PROJECT), '--headless', '--check-only', '--script', str(script)]
            row = child_run(command, out, env, args.wall_timeout, script.stem)
            processes.append(row)
            if row['returncode'] != 0:
                break
    after = source_manifest()
    atomic_json(out / 'output-sha256.json', after)
    errors = []
    for path in sorted(out.glob('*.log')):
        errors.extend(line for line in path.read_text(errors='replace').splitlines() if line.startswith(('ERROR:', 'SCRIPT ERROR:')) or 'leaked' in line.lower())
    runtime_path = out / 'images/orbit-report.json'
    runtime = json.loads(runtime_path.read_text()) if runtime_path.is_file() else {}
    success = before == after and not errors and all(p['returncode'] == 0 and p['wrapper_received_signal'] is None for p in processes)
    if args.run_renderer:
        success = success and runtime.get('complete', False) and runtime.get('first_item_runtime_passed', False)
    result = {'status': 'finished', 'mode': selected, 'processes': processes, 'sources_unchanged': before == after,
              'logged_errors': errors, 'passed': success, 'first_item_runtime_passed': bool(args.run_renderer and success),
              'godot_parse_passed': bool(args.parse_only and success), 'flight_attempted': False,
              'nearshore_pixel_coverage_passed': False, 'actual_png_manual_review_required': bool(args.run_renderer),
              'userdata_root': str(userdata), 'output': str(out)}
    atomic_json(out / 'wrapper-report.json', result)
    (out / 'exit-code.txt').write_text('0\n' if success else '1\n')
    print(json.dumps(result, indent=2), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    raise SystemExit(main())

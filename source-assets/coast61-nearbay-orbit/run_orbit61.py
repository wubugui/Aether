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
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import signal
import sys
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
ENGINE_SHA = 'db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
DEPENDENCY_HOME = AETHER / 'source-assets/north-ridge62-intake'
DEPENDENCY_GUARD_SHA = '67c53dea3c1ab20b30a30fb81e3449cb7c505bc1863eeaea823827f26568014f'
DEPENDENCY_FILES = ('dependency_guard62.py', 'DEPENDENCY_REVIEW.json.gz',
                    'audit-tools/audit_north62_deps.py', 'audit-tools/north62_binary_review.py')
sys.dont_write_bytecode = True


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUPPORT = load_module('orbit61_wrapper_support', HERE / 'continuous-v6/wrapper_support.py')
atomic_json = SUPPORT.atomic_json


def dependency_validation() -> tuple[dict, dict]:
    guard = DEPENDENCY_HOME / 'dependency_guard62.py'
    if digest(guard) != DEPENDENCY_GUARD_SHA:
        raise RuntimeError('Previously verified dependency_guard62.py identity changed')
    module = load_module('orbit61_frozen_dependency_guard62', guard)
    return module.validate_dependencies(PROJECT, PRIOR)


def own_sources() -> list[Path]:
    root_sources = [p for p in HERE.iterdir() if p.is_file() and
                    (p.suffix in {'.py', '.gd', '.md', '.json'})]
    v6_sources = [p for p in (HERE / 'continuous-v6').rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts]
    return sorted(root_sources + v6_sources)



def digest(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def source_manifest() -> dict[str, str]:
    # The immutable north review adds its exact 1483-file loading closure and
    # 51 historical gaps. The original 1477 manifest is never rewritten.
    reviewed, _ = dependency_validation()
    old = SUPPORT.strict_json(PRIOR)
    if len(old) != 1477:
        raise RuntimeError('The named previous run must retain its1477 inputs')
    _, changed, errors = SUPPORT.inspect_inputs(old)
    if changed or errors:
        raise RuntimeError('Previous frozen input changed or missing: ' + repr(changed or errors))
    if digest(GODOT) != ENGINE_SHA:
        raise RuntimeError('Godot 4.5.1 binary SHA256 mismatch')
    extras = [PRIOR, GODOT, *own_sources(), *[DEPENDENCY_HOME / p for p in DEPENDENCY_FILES]]
    result = {**old, **reviewed, **{str(p): digest(p) for p in extras}}
    return dict(sorted(result.items()))


def static_checks() -> dict:
    ast.parse(Path(__file__).read_text())
    manifest = source_manifest()
    _, dependency_guard = dependency_validation()
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
    assert 'const NATIVE_MOUSE = preload("native_mouse61.gd")' in script
    assert 'NATIVE_MOUSE.convert(root.get_final_transform(),center,intended)' in script
    assert 'NATIVE_MOUSE.delivery_check(received,intended,center,mapping_before,mapping_after)' in script
    assert 'absf(game.orbit.x-before.x-radians)<.00001' in script
    assert 'const MAX_WALL_SECONDS := 600.0' in script
    assert 'wait_event_audited()' in script and 'sequence.complete_event()' in script
    assert 'visual.unchanged(true,"late_process",frame)' in script
    assert '"identity_witness":visual.last_identity_witness.duplicate(true)' in script
    assert '"diagnostic_only":true' in script
    assert script.count('if not await wait_settled(): return') == 2
    assert 'sequence.capture_ready(latest.state.process_frame)' in script
    native_mouse = (HERE / 'native_mouse61.gd').read_text()
    assert 'transform.basis_xform(intended_relative)' in native_mouse
    assert 'transform*local_center' in native_mouse
    helper = HELPER.read_text()
    assert 'surface_get_arrays(surface)' in helper
    assert 'shape.set_faces(faces)' in helper
    assert 'mesh.get_faces(' not in helper
    assert 'bind_multimesh_identity(watch)' in helper
    assert 'validate_multimesh_identity(item)' in helper
    assert 'buffer.to_byte_array()' in helper
    assert 'mm.use_custom_data' in helper and 'mm.use_colors' in helper
    assert 'mm==null: return {"ok":true,"bound":false' in helper
    assert 'Resource.changed' not in helper
    assert 'revolution' in helper and '9.0' in helper and 'flag_line' in helper
    return {
        'status': 'source_preparation_static_checks_only',
        'previous_frozen_inputs': 1477, 'all_previous_inputs_match': True,
        'new_manifest_count': len(manifest), 'dependency_guard': dependency_guard,
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


def child_run(command: list[str], out: Path, env: dict, timeout: float, label: str) -> dict:
    return SUPPORT.run_child(command, out, env, PROJECT, timeout, label,
                             heartbeat=out / 'images/orbit-progress.json')


def validate_completion(out: Path, report_sha: str) -> dict:
    """Require real-native post-receipt wall evidence, independently of the last sample."""
    receipt_path = out / 'images/orbit-completion.json'
    receipt = SUPPORT.strict_json(receipt_path)
    prefix = 'ORBIT61_TERMINAL_WALL '
    records = [line[len(prefix):] for line in (out / 'renderer.stdout.log').read_text().splitlines()
               if line.startswith(prefix)]
    if len(records) != 1:
        raise ValueError('Exactly one native terminal wall record is required')
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('Duplicate terminal wall JSON key: ' + key)
            value[key] = item
        return value
    def invalid(value):
        raise ValueError('Nonfinite terminal wall JSON number: ' + value)
    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            invalid(value)
        return number
    terminal = json.loads(records[0], object_pairs_hook=unique, parse_constant=invalid, parse_float=finite)
    for record, version, boundary in [(receipt, 'orbit61-completion-v1', 'finish_after_final_report_and_sha'),
                                      (terminal, 'orbit61-terminal-wall-v1', 'finish_before_cleanup')]:
        if (not isinstance(record, dict) or record.get('version') != version or
                record.get('first_item_runtime_passed') is not True or
                record.get('native_report_sha256') != report_sha):
            raise ValueError('Incomplete or mismatched native wall evidence')
        wall = record.get('wall_deadline')
        if not isinstance(wall, dict):
            raise ValueError('Missing explicit native wall deadline')
        seconds = wall.get('verification_completed_wall_seconds')
        limit = wall.get('limit_seconds')
        last = wall.get('last_check')
        if (type(limit) not in (int, float) or limit != 600 or
                type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 <= seconds <= 600 or
                wall.get('first_exceeded_at') != {} or not isinstance(last, dict) or
                last.get('boundary') != boundary or type(last.get('elapsed_msec')) is not int or
                last['elapsed_msec'] < 0 or seconds != last['elapsed_msec'] / 1000 or
                type(last.get('wall_seconds')) not in (int, float) or last['wall_seconds'] != seconds):
            raise ValueError('Invalid, inconsistent or exceeded native 600-second completion wall')
    if (terminal.get('completion_receipt_sha256') != digest(receipt_path) or
            terminal['wall_deadline']['verification_completed_wall_seconds'] <
            receipt['wall_deadline']['verification_completed_wall_seconds']):
        raise ValueError('Terminal wall does not bind the completed receipt in monotonic order')
    return {'completion_receipt_sha256': digest(receipt_path), 'receipt': receipt, 'terminal': terminal}


def execute(args, out: Path, preparation: dict) -> dict:
    selected = 'renderer' if args.run_renderer else 'parse'
    result = {'status': 'preparing', 'mode': selected, 'processes': [],
              'sources_unchanged': False, 'passed': False, 'first_item_runtime_passed': False,
              'godot_parse_passed': False, 'flight_attempted': False,
              'nearshore_pixel_coverage_passed': False,
              'actual_png_manual_review_required': bool(args.run_renderer),
              'wrapper_received_signal': None, 'input_aftercheck_attempted': False,
              'output': str(out)}
    before = {}
    finalizing = False

    def cancel_setup(signum: int, _frame: object) -> None:
        result['wrapper_received_signal'] = signum
        if not finalizing:
            raise InterruptedError(f'Wrapper received signal {signum}')

    previous = {sig: signal.signal(sig, cancel_setup) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        atomic_json(out / 'wrapper-report.json', result)
        before = source_manifest()
        atomic_json(out / 'input-sha256.json', before)
        atomic_json(out / 'source-preparation.json', preparation)
        for path in own_sources():
            target = out / path.relative_to(HERE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        for relative in DEPENDENCY_FILES:
            target = out / 'dependency-review62' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(DEPENDENCY_HOME / relative, target)
        userdata = Path(tempfile.mkdtemp(prefix='nearbay61-orbit-', dir=ROOT / 'tools-feiting'))
        result['userdata_root'] = str(userdata)
        env = os.environ.copy()
        env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1',
                   ORBIT61_INPUTS=str(out / 'input-sha256.json'))
        for key, folder in [('XDG_DATA_HOME', 'data'), ('XDG_CACHE_HOME', 'cache'), ('XDG_CONFIG_HOME', 'config')]:
            path = userdata / folder
            path.mkdir()
            env[key] = str(path)
        if args.run_renderer:
            if not os.environ.get('DISPLAY'):
                raise RuntimeError('Actual display required; no headless fallback')
            jobs = [('renderer', [str(GODOT), '--path', str(PROJECT), '--rendering-method',
                     'gl_compatibility', '--audio-driver', 'Dummy', '--disable-vsync', '--script',
                     str(SCRIPT), '--', f'--output-dir={out / "images"}'])]
        else:
            jobs = [(script.stem, [str(GODOT), '--path', str(PROJECT), '--headless', '--check-only',
                     '--script', str(script)]) for script in
                    [HERE / 'orbit_telemetry61.gd', HERE / 'native_sequence61.gd', HELPER, SCRIPT]]
        result['expected_processes'] = len(jobs)
        for label, command in jobs:
            # SHA identities AND reviewed absences are checked before each child,
            # including subsequent parse children; changed files are never adopted.
            _, result['dependency_guard_before'] = dependency_validation()
            if source_manifest() != before:
                raise RuntimeError('Inputs changed before child admission')
            result['status'] = 'running'
            row = child_run(command, out, env, args.wall_timeout, label)
            result['processes'].append(row)
            if row.get('wrapper_received_signal') is not None:
                result['wrapper_received_signal'] = row['wrapper_received_signal']
            if not SUPPORT.process_passed(row):
                break
        result['logged_errors'] = SUPPORT.error_lines(sorted(out.glob('*.log')))
        success = (len(result['processes']) == len(jobs) and
                   all(SUPPORT.process_passed(row) for row in result['processes']) and
                   not result['logged_errors'])
        if args.run_renderer:
            runtime_path = out / 'images/orbit-report.json'
            runtime = SUPPORT.strict_json(runtime_path)
            result['native_report_sha256'] = digest(runtime_path)
            result['native_completion'] = validate_completion(out, result['native_report_sha256'])
            result['verification_completed_wall_seconds'] = result['native_completion']['terminal']['wall_deadline']['verification_completed_wall_seconds']
            success = success and runtime.get('complete') is True and runtime.get('first_item_runtime_passed') is True
        result.update(status='finished', passed=bool(success))
    except BaseException as exc:
        result.update(status='wrapper_exception', exception=repr(exc), passed=False)
    finally:
        finalizing = True
        result['input_aftercheck_attempted'] = True
        # Keep absence checks separate: a hashes-only manifest cannot detect a
        # newly appeared override.cfg or unreviewed import/remap sidecar.
        try:
            _, result['dependency_guard_after'] = dependency_validation()
        except BaseException as exc:
            result.update(dependency_guard_recheck_error=repr(exc), passed=False)
        try:
            after, changed, errors = SUPPORT.inspect_inputs(before)
            atomic_json(out / 'output-sha256.json', after)
            result.update(changed_inputs=changed, input_recheck_errors=errors,
                          sources_unchanged=bool(before and not changed and not errors))
            if not result['sources_unchanged'] or source_manifest() != before:
                result['passed'] = False
        except BaseException as exc:
            result.update(input_recheck_error=repr(exc), sources_unchanged=False, passed=False)
        if result['wrapper_received_signal'] is not None:
            result['passed'] = False
        result['first_item_runtime_passed'] = bool(args.run_renderer and result['passed'])
        result['godot_parse_passed'] = bool(args.parse_only and result['passed'])
        try:
            atomic_json(out / 'wrapper-report.json', result)
            (out / 'exit-code.txt').write_text('0\n' if result['passed'] else '1\n')
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--static-only', action='store_true')
    mode.add_argument('--parse-only', action='store_true')
    mode.add_argument('--run-renderer', action='store_true')
    parser.add_argument('--wall-timeout', type=float, default=720)
    args = parser.parse_args()
    if not 0 < args.wall_timeout <= 720:
        parser.error('--wall-timeout must be positive and at most the original 720 seconds')
    preparation = static_checks()
    if not args.parse_only and not args.run_renderer:
        print(json.dumps(preparation, indent=2))
        return 0
    selected = 'renderer' if args.run_renderer else 'parse'
    out = Path(tempfile.mkdtemp(prefix=f'nearbay61-orbit-{selected}-{time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())}-', dir=AETHER / 'cloud-evidence'))
    print(out, flush=True)
    result = execute(args, out, preparation)
    print(json.dumps(result, indent=2), flush=True)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

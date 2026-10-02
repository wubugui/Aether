#!/usr/bin/env python3
"""Default/static-only checks prepare sources; no engine or files are written.

--parse-only is an explicit future Godot --check-only run.
--collect is an explicit future read-only SceneState collection, never a world run.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

# Keep the advertised default/static check free of bytecode-file writes.
sys.dont_write_bytecode = True
from dependency_guard62 import validate_dependencies

HERE = Path(__file__).resolve().parent
AETHER = HERE.parents[1]
PROJECT = AETHER / 'candidates/round40-exclusive-20260930/project'
GODOT = AETHER.parent / 'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
PRIOR = AETHER / 'cloud-evidence/player-nearbay61-renderer-20261001T131646Z-f5163t8s/input-sha256.json'
SCRIPT = HERE / 'collect_saved62.gd'
ENGINE_SHA = 'db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
SOURCES = ('collect_saved62.gd', 'run_intake62.py', 'dependency_guard62.py', 'plan.json',
           'reused-boundary-index.json', 'README.md', 'DEPENDENCY_REVIEW.json.gz',
           'audit-tools/audit_north62_deps.py', 'audit-tools/north62_binary_review.py',
           'audit-tools/README.md')


def digest(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def resolve(raw: str) -> Path:
    return PROJECT / raw[6:] if raw.startswith('res://') else Path(raw)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def manifest() -> dict[str, str]:
    reviewed, _ = validate_dependencies(PROJECT, PRIOR)
    old = json.loads(PRIOR.read_text())
    if len(old) != 1477:
        raise RuntimeError('Expected exactly 1477 protected prior inputs')
    for raw, expected in old.items():
        if not Path(raw).is_file() or digest(Path(raw)) != expected:
            raise RuntimeError('Protected input absent or changed: ' + raw)
    plan = json.loads((HERE / 'plan.json').read_text())
    extra = [PRIOR, GODOT, Path(plan['reuse_geometry_file']), *[HERE / x for x in SOURCES]]
    old.update(reviewed)
    old.update({str(p): digest(p) for p in extra})
    return dict(sorted(old.items()))


def static_checks() -> dict:
    ast.parse(Path(__file__).read_text())
    plan = json.loads((HERE / 'plan.json').read_text())
    protected = manifest()
    _, dependency_guard = validate_dependencies(PROJECT, PRIOR)
    settings = (PROJECT/'project.godot').read_text()
    section = ''
    for raw in settings.splitlines():
        line = raw.strip()
        if line.startswith('[') and line.endswith(']'): section = line[1:-1]
        elif section == 'autoload' and line and not line.startswith(';'):
            raise RuntimeError('Nonempty autoload could instantiate nodes before the SceneTree script')
    require(not (PROJECT/'override.cfg').exists(), 'Unreviewed project settings override')
    require(digest(GODOT) == ENGINE_SHA, 'Engine SHA changed')
    require(digest(resolve(plan['entry'])) == plan['entry_sha256'], 'Entry SHA changed')
    require(digest(resolve(plan['reuse_source'])) == plan['reuse_source_sha256'], 'Reuse source changed')
    require(digest(Path(plan['reuse_geometry_file'])) == plan['reuse_geometry_sha256'], 'Reuse arrays changed')
    require(plan['design_box'] == [-3048,-2040,-5160,-3770], 'Design envelope changed')
    require(plan['query_box_with_40m'] == [-3088,-2000,-5200,-3730], 'Buffered query changed')
    require(plan['execution']['wall_limit_seconds'] == 60 and plan['execution']['cpu_count'] == 2, 'Execution limits changed')
    require(len(plan['target_tiles']) == 6 and len(plan['terrain_and_neighbor_names']) == 16, 'Tile scope changed')
    expected_targets = {f'Ground_{x}_{z}' for x in (-4,-3) for z in (-7,-6,-5)}
    expected_ring = set(expected_targets)
    for x in (-4,-3):
        for z in (-7,-6,-5):
            expected_ring.update(f'Ground_{a}_{b}' for a,b in [(x-1,z),(x+1,z),(x,z-1),(x,z+1)])
    require(set(plan['target_tiles']) == expected_targets and set(plan['terrain_and_neighbor_names']) == expected_ring, 'Exact tile identities changed')
    index = json.loads((HERE / 'reused-boundary-index.json').read_text())
    require(index['input_sha256'] == plan['reuse_geometry_sha256'], 'Boundary index source changed')
    require(sorted(index['tiles']) == sorted(plan['reuse_geometry_tiles']), 'Boundary index tile scope changed')
    old_positions = json.loads(Path(plan['reuse_geometry_file']).read_text())
    for tile,record in index['tiles'].items():
        matches = [r for r in old_positions['terrain'] if r['node'].split('/')[-1] == tile]
        require(len(matches) == 1, 'Ambiguous old position record: '+tile)
        old = matches[0]
        require(record['node'] == old['node'] and record['resource'] == old['mesh'] and record['min'] == old['min'] and record['max'] == old['max'], 'Old boundary identity mismatch: '+tile)
        edges = {side:set() for side in ('west','east','north','south')}
        for p in old['faces']:
            if p[0] == old['min'][0]: edges['west'].add(tuple(p))
            if p[0] == old['max'][0]: edges['east'].add(tuple(p))
            if p[2] == old['min'][2]: edges['north'].add(tuple(p))
            if p[2] == old['max'][2]: edges['south'].add(tuple(p))
        for side,points in edges.items():
            require({tuple(p) for p in record['edges'][side]} == points, 'Boundary data mismatch: '+tile+'/'+side)
    # Source guards only. This is NOT a GDScript parser or runtime proof.
    gd = SCRIPT.read_text()
    code = '\n'.join(line for line in gd.splitlines() if not line.lstrip().startswith('#'))
    forbidden = [r'\.instantiate\s*\(', r'ResourceSaver', r'\.pack\s*\(',
                 r'\.add_child\s*\(', r'get_instance_transform\s*\(',
                 r'\.buffer\b', r'\.save\s*\(', r'get_viewport\s*\(',
                 r'\.set_faces\s*\(', r'\.set_surface\w*\s*\(']
    for pattern in forbidden:
        require(not re.search(pattern, code), f'Forbidden operation: {pattern}')
    for required in ['get_base_scene_state()', 'get_node_instance(i)', 'get_node_instance_placeholder(i)',
                     '"runtime_generated_entities_proved"', '"all_occupancy_complete"']:
        require(required in gd or required.strip('"') in gd, 'Missing guard: '+required)
    return {'status':'source_preparation_only', 'python_ast_passed':True,
            'source_scope_guards_passed':True, 'godot_invoked':False,
            'project_autoload_empty':True,'project_override_absent':True,
            'reused_boundary_index_exactly_recomputed':True,
            'godot_parse_passed':False, 'native_collection_passed':False,
            'all_occupancy_complete':False, 'protected_prior_inputs':1477,
            'dependency_guard':dependency_guard,
            'manifest_count':len(protected), 'target_tiles':plan['target_tiles'],
            'no_previous_position_dataset_tiles':sorted(set(plan['terrain_and_neighbor_names'])-set(plan['reuse_geometry_tiles'])),
            'source_sha256':{name:digest(HERE/name) for name in SOURCES}}


def write_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix+'.tmp')
    with temporary.open('w') as handle:
        json.dump(value,handle,indent=2); handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    temporary.replace(path)


def launch(command: list[str], out: Path, env: dict[str,str]) -> dict:
    """Hard kill at 60 elapsed seconds; reap and preserve terminal evidence."""
    cpus = sorted(os.sched_getaffinity(0))[:2]
    if len(cpus) != 2:
        raise RuntimeError('Two available CPUs are required')
    started = time.monotonic()
    child = None
    result = {'status':'not_started','command':command,'cpu_affinity':cpus,
              'wall_limit_seconds':60,'timeout_triggered':False,'external_signal':None}
    prior_handlers = {}
    stop_signals = {signal.SIGINT,signal.SIGTERM}
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK,stop_signals)
    def stop(signum: int, _frame: object) -> None:
        result['external_signal'] = signum
        if child is not None:
            try: os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError: pass
    def child_setup() -> None:
        os.sched_setaffinity(0,cpus)
        signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
    try:
        prior_handlers = {sig:signal.signal(sig,stop) for sig in stop_signals}
        with (out/'stdout.log').open('wb') as stdout, (out/'stderr.log').open('wb') as stderr:
            child = subprocess.Popen(command,cwd=PROJECT,env=env,stdout=stdout,stderr=stderr,
                                     start_new_session=True,preexec_fn=child_setup)
            # Pending cancellation is delivered only after the child PID is owned.
            signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
            result.update(status='running',pid=child.pid)
            write_json(out/'process-report.json',result)
            while True:
                waited,status,usage = os.wait4(child.pid,os.WNOHANG)
                if waited:
                    child.returncode = os.waitstatus_to_exitcode(status)
                    result.update(status='finished',returncode=child.returncode,max_rss_kib=usage.ru_maxrss)
                    break
                if time.monotonic()-started >= 60:
                    result['timeout_triggered'] = True
                    try: os.killpg(child.pid,signal.SIGKILL)
                    except ProcessLookupError: pass
                time.sleep(.05)
    except BaseException as exc:
        result.update(status='wrapper_exception',exception=repr(exc))
        if child is not None and child.returncode is None:
            try: os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            _,status,usage = os.wait4(child.pid,0)
            child.returncode = os.waitstatus_to_exitcode(status)
            result.update(returncode=child.returncode,max_rss_kib=usage.ru_maxrss)
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
        for sig,handler in prior_handlers.items(): signal.signal(sig,handler)
        result['wall_seconds'] = time.monotonic()-started
        if result['wall_seconds'] > 60: result['timeout_triggered'] = True
        write_json(out/'process-report.json',result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--static-only',action='store_true')
    modes.add_argument('--parse-only',action='store_true')
    modes.add_argument('--collect',action='store_true')
    args = parser.parse_args()
    preparation = static_checks()
    if not args.parse_only and not args.collect:
        print(json.dumps(preparation,indent=2)); return 0
    before = manifest()
    label = 'parse' if args.parse_only else 'collect'
    out = Path(tempfile.mkdtemp(prefix=f'north-ridge62-{label}-{time.strftime("%Y%m%dT%H%M%SZ",time.gmtime())}-',dir=AETHER/'cloud-evidence'))
    print(out,flush=True)
    result = {'status':'preparing','mode':label,'passed':False,'native_collection_passed':False,
              'all_occupancy_complete':False,'godot_parse_passed':False,'output':str(out)}
    def cancel_setup(signum: int, _frame: object) -> None:
        result['wrapper_received_signal'] = signum
        raise InterruptedError(f'Wrapper received signal {signum}')
    prior_handlers = {sig:signal.signal(sig,cancel_setup) for sig in (signal.SIGINT,signal.SIGTERM)}
    try:
        write_json(out/'wrapper-report.json',result)
        write_json(out/'input-sha256.json',before)
        write_json(out/'preparation.json',preparation)
        for name in SOURCES:
            (out/name).parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(HERE/name,out/name)
        userdata = Path(tempfile.mkdtemp(prefix='north-ridge62-xdg-',dir=AETHER.parent/'tools-feiting'))
        env = os.environ.copy()
        env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',
                   NORTH62_PLAN=str(out/'plan.json'),NORTH62_OUTPUT=str(out/'native-intake.json'))
        for key,name in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
            (userdata/name).mkdir(); env[key] = str(userdata/name)
        command = [str(GODOT),'--headless','--path',str(PROJECT),'--audio-driver','Dummy',
                   '--rendering-method','gl_compatibility','--script',str(out/SCRIPT.name)]
        if args.parse_only: command.insert(1,'--check-only')
        # Recheck against the immutable review immediately before the child,
        # including absence claims that a plain hash manifest cannot express.
        _, result['dependency_guard_before'] = validate_dependencies(PROJECT, PRIOR)
        result['status'] = 'running'
        process = launch(command,out,env)
        result['process'] = process
        changed = [raw for raw,sha in before.items() if not Path(raw).is_file() or digest(Path(raw)) != sha]
        result['changed_inputs'] = changed
        logs = (out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace')
        errors = [line for line in logs.splitlines() if any(token in line for token in ['ERROR:', 'SCRIPT ERROR:', 'Parse Error:', 'Leaked instance', 'ObjectDB instances leaked'])]
        result['log_errors'] = errors
        ok = process.get('returncode') == 0 and not process.get('timeout_triggered') and process.get('external_signal') is None and not changed and not errors
        if args.parse_only:
            result['godot_parse_passed'] = ok
        else:
            native_path = out/'native-intake.json'
            native = json.loads(native_path.read_text()) if native_path.is_file() else {}
            ok = ok and native.get('saved_data_read_complete') is True and 'NORTH62_SAVED_INTAKE_END' in logs
            result['native_collection_passed'] = ok
            result['native_intake_sha256'] = digest(native_path) if native_path.is_file() else None
            # Collection is deliberately not complete live-world occupancy clearance.
            result['remaining_scatter_groups'] = len(native.get('scatter_unresolved',[]))
            result['runtime_generation_proved'] = False
        result.update(status='finished',passed=bool(ok))
    except BaseException as exc:
        result.update(status='wrapper_exception',exception=repr(exc),passed=False)
    finally:
        try:
            _, result['dependency_guard_after'] = validate_dependencies(PROJECT, PRIOR)
        except BaseException as exc:
            result.update(dependency_guard_recheck_error=repr(exc),passed=False,
                          godot_parse_passed=False,native_collection_passed=False)
        try:
            result['changed_inputs'] = [raw for raw,sha in before.items() if not Path(raw).is_file() or digest(Path(raw)) != sha]
            if result['changed_inputs']:
                result.update(passed=False,godot_parse_passed=False,native_collection_passed=False)
        except BaseException as exc:
            result.update(input_recheck_error=repr(exc),passed=False,
                          godot_parse_passed=False,native_collection_passed=False)
        write_json(out/'wrapper-report.json',result)
        for sig,handler in prior_handlers.items(): signal.signal(sig,handler)
    print(json.dumps(result,indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

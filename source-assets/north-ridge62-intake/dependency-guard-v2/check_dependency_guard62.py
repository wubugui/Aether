#!/usr/bin/env python3
"""Pure-Python fixtures. Mutations affect copied temporary files only."""
from __future__ import annotations

import ast
import contextlib
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import dependency_guard62 as guard
import run_intake62 as runner


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run() -> dict:
    results = []
    for relative in ('dependency_guard62.py', 'run_intake62.py',
                     'dependency-guard-v2/check_dependency_guard62.py',
                     'audit-tools/audit_north62_deps.py', 'audit-tools/north62_binary_review.py'):
        ast.parse((HERE / relative).read_text())
    results.append({'case': 'all_five_python_sources_parse', 'passed': True})
    identities, real_evidence = guard.validate_dependencies()
    require(len(identities) == 1490, 'Unexpected closure/control/auditor manifest count')
    results.append({'case': 'real_1483_closure_and_startup_identity_pass', 'passed': True})
    review = guard.load_review()
    protected_before = {p: guard.digest(Path(p)) for p in identities}
    frozen = ('PREPARATION_CHECK.json', 'collect_saved62.gd', 'plan.json',
              'reused-boundary-index.json', 'DEPENDENCY_REVIEW.md',
              'DEPENDENCY_REVIEW.json', 'DEPENDENCY_REVIEW.json.gz', 'dependency-storage.json')
    frozen_before = {name: guard.digest(HERE / name) for name in frozen}

    with tempfile.TemporaryDirectory(prefix='north62-guard-fixture-') as raw:
        root = Path(raw)
        project = root / 'project'
        for uri in review['files']:
            relative = uri[6:]
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(guard.PROJECT / relative, target)
        for relative in guard.CONTROL_PATHS:
            source = guard.PROJECT / relative
            if source.is_file():
                target = project / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)

        def check() -> tuple[dict, dict]:
            return guard.validate_dependencies(project=project)

        check()
        results.append({'case': 'isolated_copy_positive', 'passed': True})

        def reject(name: str, action, cleanup, expected: str, check_action=check) -> None:
            try:
                action()
                try:
                    check_action()
                except RuntimeError as exc:
                    require(expected in str(exc), name + ' raised an unrelated error: ' + str(exc))
                    results.append({'case': name, 'passed': True, 'rejection': str(exc)})
                else:
                    raise RuntimeError('Negative fixture unexpectedly passed: ' + name)
            finally:
                cleanup()

        def changed(name: str, relative: str, transform, expected: str) -> None:
            path = project / relative
            saved = path.read_bytes()
            reject(name, lambda: path.write_bytes(transform(saved)), lambda: path.write_bytes(saved), expected)

        def added(name: str, relative: str, expected: str, symlink=False) -> None:
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            action = (lambda: path.symlink_to(root / 'missing')) if symlink else (lambda: path.write_bytes(b''))
            reject(name, action, lambda: path.unlink(), expected)

        flip = lambda b: bytes([b[0] ^ 1]) + b[1:]
        changed('omitted_script_same_length_change', 'scripts/hud.gd', flip, 'SHA256 changed')
        changed('covered_entry_same_length_change', review['entry'][6:], flip, 'SHA256 changed')
        cache = next(u[6:] for u in review['compressed_import_scenes'])
        changed('omitted_imported_scene_same_length_change', cache, flip, 'SHA256 changed')
        changed('existing_import_remap_changed', 'assets/models/poplar.glb.import', flip, 'SHA256 changed')
        changed('uid_cache_same_length_change', '.godot/uid_cache.bin', flip, 'SHA256 changed')
        changed('global_class_cache_same_length_change', '.godot/global_script_class_cache.cfg', flip, 'SHA256 changed')
        changed('nonempty_autoload_added', 'project.godot', lambda b: b + b'\n[autoload]\nUnsafe="*res://scripts/hud.gd"\n', 'byte length changed')
        changed('project_resource_remap_setting_added', 'project.godot', lambda b: b + b'\n[path_remap]\nremapped_paths=[]\n', 'byte length changed')
        added('empty_override_appeared', 'override.cfg', 'reviewed-absent path appeared')
        added('dangling_override_symlink_appeared', 'override.cfg', 'symlinked dependency path', symlink=True)
        added('empty_extension_list_appeared', '.godot/extension_list.cfg', 'reviewed-absent path appeared')
        added('new_dependency_remap_appeared', 'scripts/hud.gd.remap', 'unreviewed remap/import sidecar')
        added('dangling_remap_symlink_appeared', 'scripts/hud.gd.remap', 'unreviewed remap/import sidecar', symlink=True)
        added('new_import_sidecar_appeared', 'scripts/hud.gd.import', 'unreviewed remap/import sidecar')
        missing = project / 'scripts/hud.gd'
        saved_missing = missing.read_bytes()
        reject('omitted_script_missing', lambda: missing.unlink(), lambda: missing.write_bytes(saved_missing), 'missing/nonregular file')
        saved_uid = (project / '.godot/uid_cache.bin').read_bytes()
        reject('uid_cache_missing', lambda: (project / '.godot/uid_cache.bin').unlink(),
               lambda: (project / '.godot/uid_cache.bin').write_bytes(saved_uid), 'missing/nonregular file')

        bad_gzip = root / 'bad-review.json.gz'
        original_gzip = guard.REVIEW.read_bytes()
        reject('frozen_gzip_byte_changed', lambda: bad_gzip.write_bytes(flip(original_gzip)),
               lambda: bad_gzip.unlink(), 'SHA256 changed', lambda: guard.load_review(bad_gzip))
        # Identical decoded JSON with a different gzip header is still unapproved.
        header_changed = original_gzip[:4] + bytes([original_gzip[4] ^ 1]) + original_gzip[5:]
        require(gzip.decompress(header_changed) == gzip.decompress(original_gzip), 'gzip header fixture invalid')
        reject('equivalent_json_unapproved_gzip_rejected', lambda: bad_gzip.write_bytes(header_changed),
               lambda: bad_gzip.unlink(), 'SHA256 changed', lambda: guard.load_review(bad_gzip))
        bad_prior = root / 'prior.json'
        reject('historical_manifest_changed', lambda: bad_prior.write_bytes(guard.PRIOR.read_bytes() + b' '),
               lambda: bad_prior.unlink(), 'historical 1477 manifest identity changed',
               lambda: guard.validate_dependencies(project=project, prior=bad_prior))

        packaged = root / 'packaged'
        for relative in guard.AUDITORS:
            target = packaged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / relative, target)
        auditor = packaged / 'audit-tools/audit_north62_deps.py'
        auditor.write_bytes(flip(auditor.read_bytes()))
        with mock.patch.object(guard, 'HERE', packaged):
            reject('packaged_auditor_changed', lambda: None, lambda: None,
                   'packaged auditor identity changed')

        # Actual main() control flow, with launch replaced before entry. No subprocess
        # can start here; these are simulated terminal paths, never native results.
        def flow(name: str, mutation: str | None, before_launch=False, cancelled=False) -> None:
            flow_root = root / name
            (flow_root / 'cloud-evidence').mkdir(parents=True)
            (root / 'tools-feiting').mkdir(exist_ok=True)
            mutated = project / mutation if mutation else None
            saved = mutated.read_bytes() if mutated and mutated.is_file() else None
            def mutate() -> None:
                if mutated:
                    mutated.write_bytes(flip(saved) if saved else b'')
            def manifest() -> dict:
                value, _ = check()
                if before_launch:
                    mutate()
                return value
            def launch(command, out, env) -> dict:
                require('--check-only' in command, 'fixture is not parse-only')
                (out / 'stdout.log').write_text('simulated parser output\n')
                (out / 'stderr.log').write_text('')
                mutate()
                if cancelled:
                    raise InterruptedError('simulated cancellation after source change')
                return {'returncode': 0, 'timeout_triggered': False, 'external_signal': None,
                        'status': 'fixture_simulation_only'}
            try:
                with mock.patch.object(runner, 'AETHER', flow_root), \
                     mock.patch.object(runner, 'PROJECT', project), \
                     mock.patch.object(runner, 'static_checks', return_value={'fixture_simulated_setup': True}), \
                     mock.patch.object(runner, 'manifest', side_effect=manifest), \
                     mock.patch.object(runner, 'launch', side_effect=launch) as launch_mock, \
                     mock.patch.object(sys, 'argv', ['run_intake62.py', '--parse-only']), \
                     contextlib.redirect_stdout(io.StringIO()):
                    code = runner.main()
                reports = list((flow_root / 'cloud-evidence').glob('*/wrapper-report.json'))
                require(len(reports) == 1, 'missing terminal fixture report')
                report = json.loads(reports[0].read_text())
                require(launch_mock.call_count == (0 if before_launch else 1), 'incorrect launch admission')
                if mutation:
                    require(code == 1 and report['passed'] is False and
                            report['godot_parse_passed'] is False and
                            report['native_collection_passed'] is False and
                            'dependency_guard_recheck_error' in report, 'unsafe terminal success in ' + name)
                else:
                    require(code == 0 and 'dependency_guard_before' in report and
                            'dependency_guard_after' in report, 'simulated positive flow failed')
                results.append({'case': name, 'passed': True, 'simulated_launch_calls': launch_mock.call_count,
                                'wrapper_returncode': code, 'engine_started': False})
            finally:
                if mutated:
                    if saved is None:
                        mutated.unlink(missing_ok=True)
                    else:
                        mutated.write_bytes(saved)

        flow('simulated_positive_terminal_flow', None)
        flow('prelaunch_new_override_blocks_admission', 'override.cfg', before_launch=True)
        flow('postlaunch_new_remap_clears_success', 'scripts/hud.gd.remap')
        flow('postlaunch_uid_change_clears_success', '.godot/uid_cache.bin')
        flow('cancelled_flow_still_checks_absence', '.godot/extension_list.cfg', cancelled=True)
        check()

    require(all(guard.digest(Path(p)) == sha for p, sha in protected_before.items()), 'Real protected input changed')
    require(all(guard.digest(HERE / p) == sha for p, sha in frozen_before.items()), 'Frozen legacy evidence changed')
    results.append({'case': 'real_inputs_and_frozen_evidence_unchanged_after_fixtures', 'passed': True})
    return {'status': 'pure_python_fixture_pass', 'optimization_level': sys.flags.optimize,
            'passed': True, 'checks_passed': len(results), 'checks': results,
            'real_dependency_guard': real_evidence, 'frozen_legacy_sha256': frozen_before,
            'engines_started': False, 'native_parse_passed': False,
            'native_collection_passed': False, 'all_occupancy_complete': False}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))

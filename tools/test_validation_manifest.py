"""Small temporary-fixture tests; never launch Godot or touch game assets."""
import copy
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zlib

import validation_manifest as validation


def put(root, path, data=b'fixture'):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data.encode() if isinstance(data, str) else data)
    return target


def make_fixture(root):
    for path in ['project.godot', 'export_presets.cfg', 'scenes/game.tscn',
                 'assets/airship.glb', 'assets/propeller.glb', 'assets/reference.jpg',
                 'tools/validate_demo.ps1', 'tools/validation_manifest.py',
                 'tools/verify_cliff_flight.gd', 'tools/verify_road_surfaces.gd',
                 'tools/verify_geology_assets.py', 'tools/prepare_windows_export.py',
                 'tools/compare_reference.py', 'materials/world.tres',
                 '.tools/godot/Godot_v4.5.1-stable_win64.exe',
                 '.tools/godot/Godot_v4.5.1-stable_win64_console.exe',
                 *validation.PROVENANCE_PATHS]:
        put(root, path, '[]' if path.endswith('.json') else 'fixture')
    catalog = []
    for library, count in [('cliff_kit', 7), ('mountain_kit', 11), ('road_kit', 3)]:
        entries = []
        for index in range(count):
            name = library + str(index)
            entry = {'name': name, 'path': 'assets/models/' + name + '.glb',
                     'native_source': 'blender/' + name + '.blend'}
            entries.append(entry)
            catalog.append(entry)
            for path in [entry['path'], entry['native_source'], 'scenes/prefabs/' + name + '.tscn']:
                put(root, path)
        validation.write_json(root / 'assets' / (library + '.json'), entries)
    validation.write_json(root / 'assets/asset_catalog.json', catalog)
    put(root, '.godot/imported/fixture.scn')
    put(root, '.godot/imported/fixture.md5', 'source_md5="fixture"')
    put(root, 'assets/airship.glb.import', '[remap]\npath="res://.godot/imported/fixture.scn"\n')


def source_provenance(root, run_id, package=None):
    hashes = {'res://' + path: validation.sha256(root / path) for path in validation.PROVENANCE_PATHS}
    if package is not None:
        hashes = {'res://assets/mountain_kit.json': hashes['res://assets/mountain_kit.json']}
        hashes.update({path: value['sha256'] for path, value in package.items()})
    return {'run_id': run_id, 'utc': validation.utc_now(), 'packaged': package is not None,
            'engine': 'fixture-engine', 'sha256': hashes}


def make_report(root, name, run_id, package=None):
    result = {'passed': True, 'provenance': source_provenance(root, run_id, package)}
    if name in {'game-test', 'packaged-game'}:
        result['checks'] = [{'name': 'check-' + str(i), 'passed': True}
                            for i in range(validation.EXPECTED_COUNTS[name])]
    elif name in {'cliffs-contact', 'mountains-contact'}:
        library = 'cliff_kit' if name == 'cliffs-contact' else 'mountain_kit'
        result['checks'] = [{'name': item, 'approach': direction, 'passed': True}
                            for item in validation.kit_assets(root, library)
                            for direction in ['(0, 0, -1)', '(1, 0, 0)', '(0, 1, 0)']]
        result['world_sha256'] = validation.sha256(root / 'scenes/world/World.tscn')
        result['ship_prefab_sha256'] = validation.sha256(root / 'scenes/prefabs/Airship.tscn')
    elif name == 'road-surfaces':
        result.update(samples=40642, world_unchanged=True,
                      world_sha256=validation.sha256(root / 'scenes/world/World.tscn'))
        result['roads'] = [{'name': key, 'passed': True, 'sample_count': count,
                            'failed_samples': 0, 'maximum_height_error_metres': .02,
                            'glb_sha256': validation.sha256(root / item['path'])}
                           for (key, item), count in zip(validation.kit_assets(root, 'road_kit').items(), [14000, 14000, 12642])]
    elif name in {'tour-test', 'cliff-tour-test'}:
        result.update(waypoints_reached=validation.EXPECTED_COUNTS[name], samples=[{'time': 1}],
                      health=1, shield=1, minimum_clearance_metres=60, distance_metres=10000,
                      camera_obstruction_samples=0, world_sha256=validation.sha256(root / 'scenes/world/World.tscn'))
    elif name == 'stream-test':
        result.update(missing_terrain_or_collision_samples=0,
                      legs=[{'direction': direction, 'passed': True, 'distance_metres': 4001,
                             'missing_terrain_or_collision_samples': 0, 'samples': [{'time': 1}]}
                            for direction in ['east', 'west', 'north', 'south']])
    elif name == 'geology':
        result.pop('provenance')
        result['assets'] = [{'name': key, 'passed': True, 'nonmanifold_or_open_edges': 0,
                             'degenerate_faces': 0, 'images': 0, 'volume_relative_error': 0,
                             'glb_sha256': validation.sha256(root / item['path'])}
                            for key, item in validation.kit_assets(root, 'cliff_kit', 'mountain_kit').items()]
    return result


def png_fixture():
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1672, 941, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\0' + b'\0' * (1672 * 3)) * 941)) + chunk(b'IEND', b''))


class FakeRun(validation.ValidationRun):
    """Exercise the full driver orchestration with simulated process products."""
    def execute(self, command, stdout, stderr, cwd=None):
        stdout.write_text('fixture process\n')
        stderr.write_text('')
        name = stdout.stem
        sinks = {'game-test': 'game-validation.json', 'tour-test': 'flight-tour-validation.json',
                 'stream-test': 'stream-flight-validation.json', 'cliff-tour-test': 'cliff-tour-validation.json',
                 'cliffs-contact': 'cliff-flight-validation.json', 'mountains-contact': 'mountain-flight-validation.json',
                 'road-surfaces': 'road-surface-validation.json', 'geology': 'geology-asset-validation.json'}
        if name in sinks:
            validation.write_json(self.root / 'captures' / sinks[name], make_report(self.root, name, self.run_id))
        elif name.startswith('capture-') or name == 'packaged-opening':
            output = next(str(arg).removeprefix('--output=') for arg in command if str(arg).startswith('--output='))
            Path(output).write_bytes(png_fixture())
        elif name == 'reference-metrics':
            validation.write_json(self.root / 'reviews' / ('round-' + self.run_id + '-metrics.json'),
                                  {'round': self.run_id, 'completion_proven': False, 'size': [1672, 941],
                                   'reference_sha256': validation.sha256(self.root / 'assets/reference.jpg'),
                                   'render_sha256': validation.sha256(self.directory / 'images/opening.png')})
        elif name == 'export':
            Path(command[-1]).write_bytes(b'fixture exe')
            Path(command[-1]).with_suffix('.pck').write_bytes(b'fixture pack')
        elif name == 'packaged-game':
            output = next(str(arg).removeprefix('--validation-output=') for arg in command if str(arg).startswith('--validation-output='))
            validation.write_json(output, make_report(self.root, name, self.run_id, self.package))
        return 0


class ValidationContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='validation fixture ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        make_fixture(self.root)
        self.inputs = validation.snapshot_inputs(self.root, imported=True)
        self.run_id = 'unique-test-run'

    def check_report(self, name, report, package=None):
        now = time.time_ns()
        validation.validate_report(name, report, self.root, self.run_id, self.inputs,
                                   now - 5_000_000_000, now + 5_000_000_000, package)

    def test_all_source_contracts_accept_complete_fresh_evidence(self):
        for name in validation.EXPECTED_COUNTS:
            if name != 'packaged-game':
                with self.subTest(name=name):
                    self.check_report(name, make_report(self.root, name, self.run_id))

    def test_failed_child_cannot_hide_under_passed_summary(self):
        report = make_report(self.root, 'game-test', self.run_id)
        report['checks'][2]['passed'] = False
        with self.assertRaises(ValueError):
            self.check_report('game-test', report)

    def test_wrong_run_missing_provenance_wrong_hash_and_missing_passed_rejected(self):
        original = make_report(self.root, 'game-test', self.run_id)
        for change in ['run', 'hash', 'provenance', 'passed', 'timestamp']:
            report = copy.deepcopy(original)
            if change == 'run': report['provenance']['run_id'] = 'stale'
            if change == 'hash': report['provenance']['sha256']['res://scripts/game.gd'] = '0' * 64
            if change == 'provenance': report.pop('provenance')
            if change == 'passed': report.pop('passed')
            if change == 'timestamp': report['provenance']['utc'] = '2000-01-01T00:00:00'
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.check_report('game-test', report)

    def test_incomplete_counts_rejected_for_every_stage(self):
        for name in validation.EXPECTED_COUNTS:
            if name == 'packaged-game': continue
            report = make_report(self.root, name, self.run_id)
            if 'checks' in report: report['checks'].pop()
            elif 'waypoints_reached' in report: report['waypoints_reached'] -= 1
            elif 'legs' in report: report['legs'].pop()
            elif 'roads' in report: report['samples'] -= 7
            elif 'assets' in report: report['assets'].pop()
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.check_report(name, report)

    def test_duplicate_contact_direction_rejected(self):
        report = make_report(self.root, 'cliffs-contact', self.run_id)
        report['checks'][1]['approach'] = report['checks'][0]['approach']
        with self.assertRaises(ValueError): self.check_report('cliffs-contact', report)

    def test_geology_asset_hash_must_match_this_snapshot(self):
        report = make_report(self.root, 'geology', self.run_id)
        report['assets'][0]['glb_sha256'] = '0' * 64
        with self.assertRaises(ValueError): self.check_report('geology', report)

    def test_package_requires_37_and_exact_exe_pack_hashes(self):
        package = {'D:/unique run/Aether.exe': {'sha256': '1' * 64}, 'D:/unique run/Aether.pck': {'sha256': '2' * 64}}
        report = make_report(self.root, 'packaged-game', self.run_id, package)
        self.check_report('packaged-game', report, package)
        report['checks'].pop()
        with self.assertRaises(ValueError): self.check_report('packaged-game', report, package)
        report = make_report(self.root, 'packaged-game', self.run_id, package)
        report['provenance']['sha256']['D:/unique run/Aether.pck'] = '3' * 64
        with self.assertRaises(ValueError): self.check_report('packaged-game', report, package)

    def test_source_and_imported_changes_both_detected(self):
        for path in ['scripts/game.gd', '.godot/imported/fixture.scn', '.godot/imported/fixture.md5', 'assets/models/cliff_kit0.glb',
                     'assets/asset_catalog.json', 'materials/world.tres']:
            original = (self.root / path).read_bytes()
            (self.root / path).write_bytes(original + (b' ' if path.endswith('.json') else b'changed'))
            differences = validation.input_diff(self.inputs, validation.snapshot_inputs(self.root, imported=True))
            self.assertIn('res://' + path, differences)
            (self.root / path).write_bytes(original)

    def test_new_dynamic_resource_detected(self):
        put(self.root, 'assets/scatter/new-group.res')
        self.assertIn('res://assets/scatter/new-group.res',
                      validation.input_diff(self.inputs, validation.snapshot_inputs(self.root, imported=True)))

    def test_zero_exit_with_stdout_or_stderr_error_rejected(self):
        out, err = put(self.root, 'stdout.log', ''), put(self.root, 'stderr.log', '')
        for path in [out, err]:
            path.write_text('PASS 36/36\nSCRIPT ERROR: deliberately simulated\n')
            with self.assertRaises(ValueError): validation.validate_logs(out, err, 0)
            path.write_text('')

    def test_real_small_process_zero_exit_without_report_rejected(self):
        with redirect_stdout(io.StringIO()):
            run = validation.ValidationRun(self.root, 'missing')
            run.inputs = self.inputs
            with self.assertRaisesRegex(ValueError, 'missing or stale report'):
                run.stage('game-test', [sys.executable, '-c', 'print("PASS 36/36")'],
                          report=self.root / 'captures/game-validation.json')
        self.assertEqual(run.manifest['stages'][0]['status'], 'failed')

    def test_stale_report_is_preserved_but_rejected(self):
        report = self.root / 'captures/game-validation.json'
        validation.write_json(report, make_report(self.root, 'game-test', self.run_id))
        os.utime(report, (time.time() - 60, time.time() - 60))
        old = report.read_bytes()
        with redirect_stdout(io.StringIO()):
            run = validation.ValidationRun(self.root, 'stale')
            run.inputs = self.inputs
            with self.assertRaisesRegex(ValueError, 'missing or stale report'):
                run.stage('game-test', [sys.executable, '-c', 'print("PASS")'], report=report)
        self.assertEqual((run.directory / 'previous-reports/game-test.json').read_bytes(), old)

    def test_mutation_during_stage_fails(self):
        with redirect_stdout(io.StringIO()):
            run = validation.ValidationRun(self.root, 'mutation')
            run.inputs = self.inputs
            def mutate(command, out, err, cwd=None):
                out.write_text('PASS'); err.write_text('')
                put(self.root, 'materials/world.tres', 'changed during execution')
                return 0
            with patch.object(run, 'execute', side_effect=mutate), self.assertRaisesRegex(ValueError, 'dependencies changed'):
                run.stage('import-fixture', ['fixture'])

    def test_fresh_failed_report_is_archived_for_later_review(self):
        report = self.root / 'captures/game-validation.json'
        with redirect_stdout(io.StringIO()):
            run = validation.ValidationRun(self.root, 'failed-report')
            run.inputs = self.inputs
            def failed_report(command, out, err, cwd=None):
                out.write_text('PASS banner'); err.write_text('')
                validation.write_json(report, {'passed': False, 'details': 'deliberate fixture failure'})
                return 0
            with patch.object(run, 'execute', side_effect=failed_report), self.assertRaises(ValueError):
                run.stage('game-test', ['fixture'], report=report)
        self.assertFalse(validation.read_json(run.directory / 'reports/game-test.json')['passed'])

    def test_replaced_pack_after_accepted_stage_fails_final_evidence_check(self):
        class ReplacedPack(FakeRun):
            def stage(self, name, *args, **kwargs):
                super().stage(name, *args, **kwargs)
                if name == 'packaged-opening':
                    (self.directory / 'package/Aether.pck').write_bytes(b'replaced after acceptance')
        with redirect_stdout(io.StringIO()):
            run = ReplacedPack(self.root, 'replaced-package', export_windows=True)
            with self.assertRaisesRegex(ValueError, 'Evidence changed after validation'):
                run.run()
        self.assertFalse(run.manifest['passed'])

    def test_pipeline_lock_rejects_concurrent_run(self):
        lock = self.root / 'captures/.test.lock'
        with validation.exclusive_lock(lock):
            with self.assertRaises(OSError):
                with validation.exclusive_lock(lock):
                    self.fail('Second concurrent pipeline acquired lock')

    def test_package_launch_requires_absolute_pck_and_independent_cwd(self):
        package = self.root / 'isolated package'
        package.mkdir()
        exe, pack = package / 'Aether.exe', package / 'Aether.pck'
        valid = [exe, '--main-pack', pack, '--', '--game-test']
        validation.validate_package_launch(valid, package, package)
        cases = [([exe, '--', '--game-test'], package),
                 (valid, self.root),
                 ([exe, '--main-pack', 'Aether.pck', '--', '--game-test'], package),
                 ([exe, '--main-pack', self.root / 'Aether.pck', '--', '--game-test'], package),
                 ([exe, '--path', self.root, '--main-pack', pack, '--', '--game-test'], package)]
        for command, cwd in cases:
            with self.subTest(command=command, cwd=cwd), self.assertRaises(ValueError):
                validation.validate_package_launch(command, cwd, package)

    def test_real_small_process_uses_recorded_cwd(self):
        directory = self.root / 'independent working directory'
        directory.mkdir()
        with redirect_stdout(io.StringIO()):
            run = validation.ValidationRun(self.root, 'cwd')
            run.stage('cwd-fixture', [sys.executable, '-c', 'import os; print(os.getcwd())'], cwd=directory)
        self.assertEqual(Path((run.directory / 'cwd-fixture.log').read_text().strip()).resolve(), directory.resolve())
        self.assertEqual(Path(run.manifest['stages'][0]['cwd']), directory.resolve())

    def test_corrupt_or_truncated_image_rejected(self):
        image = put(self.root, 'capture.png', png_fixture())
        validation.validate_png(image)
        image.write_bytes(image.read_bytes()[:-12])
        with self.assertRaises(ValueError): validation.validate_png(image)

    def test_complete_simulated_windows_run_forces_current_source_capture_and_binds_everything(self):
        with redirect_stdout(io.StringIO()):
            run = FakeRun(self.root, 'same-label', export_windows=True, capture_views=False)
            run.run()
            another = FakeRun(self.root, 'same-label')
        self.assertNotEqual(run.directory, another.directory)
        self.assertTrue(run.manifest['passed'])
        self.assertFalse(run.manifest['visual_acceptance_proven'])
        self.assertTrue(run.manifest['source_package_image_sha256_equal'])
        for path in ['images/opening.png', 'images/packaged-opening.png', 'reports/packaged-game.json',
                     'package/Aether.exe', 'package/Aether.pck', 'inputs.json']:
            self.assertIn(path, run.manifest['artifacts'])
        self.assertTrue(all(row['run_id'] == run.run_id for row in run.manifest['stages']))
        for stage in run.manifest['stages']:
            if stage['name'] in {'packaged-game', 'packaged-opening'}:
                self.assertEqual(Path(stage['cwd']), run.directory / 'package')
                self.assertEqual(stage['command'][1:3], ['--main-pack', str(run.directory / 'package/Aether.pck')])
            else:
                self.assertEqual(Path(stage['cwd']), self.root.resolve())


if __name__ == '__main__':
    unittest.main(verbosity=2)

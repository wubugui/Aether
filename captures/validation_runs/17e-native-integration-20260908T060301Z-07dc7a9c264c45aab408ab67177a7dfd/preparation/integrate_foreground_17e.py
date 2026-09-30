"""Integrate the reviewed 17e foreground draft and verify affected native systems.

This is a scoped native asset refresh, not a world regeneration or release.
The independent review accepts local progress only; the complete visual goal
remains open. All prior source files and failed evidence are retained.
"""
from pathlib import Path
import json
import shutil
import sys

from validation_manifest import (
    ValidationRun, exclusive_lock, input_diff, read_json, require, sha256,
    snapshot_inputs, utc_now, write_json,
)
from validate_section_overlap import validate_section_overlap


def main():
    root = Path(__file__).resolve().parents[1]
    candidate_run = root/'captures/validation_runs/foreground-17e-20260908T055006Z-348ac27ec16f49c6bc196accd90eba32'
    source = candidate_run/'study-inputs'
    review = root/'reviews/round-17e-independent-review.md'
    gate_path = root/'reviews/round-17e-projected-surface-gate.json'
    items = read_json(source/'manifest.json')
    names = {'cliff_western_slab', 'cliff_front_columns'}
    require({x['name'] for x in items} == names and len(items) == 2, 'Unexpected candidate scope')
    require(read_json(candidate_run/'manifest.json')['passed'] is True, 'Candidate capture incomplete')
    require(review.is_file(), 'The completed independent review must be retained before integration')
    gate = read_json(gate_path)
    require(gate['passed'] is True, 'Candidate surface gate failed')
    kit_path = root/'assets/cliff_kit.json'
    kit = read_json(kit_path)
    native = {x['name']: x for x in kit}
    for item in items:
        original = native[item['name']]
        require(sha256(root/original['native_source']) == item['source_sha256'], 'Production source has changed; do not overwrite')
        require(sha256(root/original['path']) == item['source_glb_sha256'], 'Production GLB has changed; do not overwrite')
        for suffix, key in (('.glb', 'glb_sha256'), ('.blend', 'blend_sha256')):
            require(sha256(source/(item['name']+suffix)) == item[key], 'Frozen candidate changed')
    for entry in gate['assets']:
        candidate = next((x for x in items if x['name'] == entry['name']), None)
        actual = source/(entry['name']+'.glb') if candidate else root/entry['path']
        require(sha256(actual) == entry['sha256'], 'Surface-gate geometry changed')
    engine = root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run = ValidationRun(root, '17e-native-integration', False, True)
        run.manifest.update(scope='Two reviewed foreground assets, scoped native prefab/collision and affected foliage refresh, four GPU views and affected source checks. No Windows export or complete visual acceptance.',
            expected_counts={'game-test': 36, 'cliff-tour-test': 6, 'cliffs-contact': 21, 'road-surfaces': 40642, 'geology': 18},
            candidate_run=str(candidate_run), visual_acceptance_proven=False)
        try:
            backup = run.directory/'source-backup'
            before = snapshot_inputs(root, imported=False)
            for path in [kit_path] + [root/native[item['name']][key] for item in items for key in ('path', 'native_source')]:
                target = backup/path.relative_to(root)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                run.bind(target)
            for path in [Path(__file__), review, gate_path, source/'manifest.json']:
                target = run.directory/'preparation'/path.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                run.bind(target)
            write_json(run.directory/'preparation-inputs.json', {'files': before})
            run.bind(run.directory/'preparation-inputs.json')
            for item in items:
                destination = native[item['name']]
                for suffix, key in (('.glb', 'path'), ('.blend', 'native_source')):
                    shutil.copy2(source/(item['name']+suffix), root/destination[key])
                destination.update(vertices=item['vertices'], faces=item['triangles'],
                    volume_m3=item['volume_m3'], modeling_method='Authored geological sections; reviewed 17e foreground draft',
                    authoring_revision='17e', authoring_evidence=str(candidate_run.relative_to(root)))
            write_json(kit_path, kit)
            run.stage('import', [engine, '--headless', '--editor', '--path', root, '--import', '--quit'])
            run.stage('refresh-selected-cliffs', [engine, '--path', root, '--script', 'tools/install_cliff_kit.gd', '--']
                + ['--asset='+name for name in sorted(names)])
            refresh = (run.directory/'refresh-selected-cliffs.log').read_text(encoding='utf-8', errors='replace')
            require('CLIFF KIT INSTALLED 2' in refresh and 'terrain updated 0' in refresh, 'Scoped refresh did not positively complete')
            after = snapshot_inputs(root, imported=False)
            changes = input_diff(before, after)
            write_json(run.directory/'preparation-changes.json', changes)
            run.bind(run.directory/'preparation-changes.json')
            run.inputs = snapshot_inputs(root, imported=True)
            write_json(run.directory/'inputs.json', {'run_id': run.run_id, 'frozen_utc': utc_now(), 'files': run.inputs})
            run.bind(run.directory/'inputs.json')
            run.manifest['input_count'] = len(run.inputs)
            run.manifest['section_surface_gate'] = validate_section_overlap(root, gate_path, run.inputs)
            run.save()
            marker = '--validation-run='+run.run_id
            for view in ('opening', 'cliff-side', 'cliff-back', 'reverse'):
                output = run.directory/'images'/(view+'.png')
                run.stage('capture-'+view, [engine, '--path', root, '--', '--capture', '--view='+view, '--output='+str(output), marker], image=output)
            for name, sink in [('game-test', 'game-validation.json'), ('cliff-tour-test', 'cliff-tour-validation.json')]:
                run.stage(name, [engine, '--path', root, '--', '--'+name, marker], report=root/'captures'/sink)
            for name, script, sink in [
                ('cliffs-contact', 'verify_cliff_flight.gd', 'cliff-flight-validation.json'),
                ('cliff-ground-rims', 'verify_cliff_ground_rims.gd', 'cliff-ground-rim-validation.json'),
                ('road-surfaces', 'verify_road_surfaces.gd', 'road-surface-validation.json')]:
                run.stage(name, [engine, '--path', root, '--script', 'tools/'+script, '--', marker], report=root/'captures'/sink)
            run.stage('geology', [sys.executable, 'tools/verify_geology_assets.py'], report=root/'captures/geology-asset-validation.json')
            run.assert_inputs()
            require(len(run.manifest['stages']) == 12 and all(x['passed'] for x in run.manifest['stages']), 'Incomplete integration checks')
            for path, record in run.manifest['artifacts'].items():
                require(sha256(run.directory/path) == record['sha256'], 'Evidence changed: '+path)
            run.manifest.update(status='passed', passed=True, completed_utc=utc_now())
            run.save()
            print('NATIVE FOREGROUND INTEGRATION PASS '+str(run.directory), flush=True)
        except Exception as error:
            run.manifest.update(status='failed', passed=False, error=str(error), completed_utc=utc_now())
            run.save()
            raise


if __name__ == '__main__':
    main()

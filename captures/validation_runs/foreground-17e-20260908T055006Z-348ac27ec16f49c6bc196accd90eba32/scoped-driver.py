"""Freeze independent foreground assets and capture the actual Godot world."""
from pathlib import Path
import argparse
import shutil

from validation_manifest import (
    ValidationRun, exclusive_lock, read_json, require, sha256,
    snapshot_inputs, utc_now, write_json,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label', choices=['16a', '16b', '16c', '16d', '16e', '16f', '16g', '17a', '17b', '17c', '17d', '17e'])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / 'captures' / ('foreground_study_' + args.label)
    items = read_json(source / 'manifest.json')
    expected = {'cliff_western_slab', 'cliff_front_columns'} if args.label.startswith('17') else {'cliff_crown', 'cliff_front_columns', 'cliff_central_wall'}
    require(len(items) == len(expected) and {item['name'] for item in items} == expected, 'Unexpected candidate asset selection')
    builder = 'sculpt_foreground_17.py' if args.label.startswith('17') else 'sculpt_foreground_16.py'
    with exclusive_lock(root / 'captures/.validation-pipeline.lock'):
        run = ValidationRun(root, 'foreground-' + args.label, False, True)
        run.manifest['scope'] = 'Temporary native World assembly of selected independent Blender cliff candidates and their derived triangle colliders. Three raw GPU views; no production integration, gameplay acceptance or release.'
        run.manifest['selected_assets'] = sorted(expected)
        run.manifest['production_modified'] = False
        run.manifest['expected_counts'] = {}
        frozen = run.directory / 'study-inputs'
        frozen.mkdir()
        try:
            for item in items:
                for suffix, key in (('.glb', 'glb_sha256'), ('.blend', 'blend_sha256')):
                    original = source / (item['name'] + suffix)
                    require(sha256(original) == item[key], 'Candidate hash changed: ' + str(original))
                    shutil.copy2(original, frozen / original.name)
                    run.bind(frozen / original.name)
            for original, target in ((source / 'manifest.json', frozen / 'manifest.json'),
                                     (root / 'captures/preview_foreground_16.gd', frozen / 'preview.gd'),
                                     (Path(__file__), run.directory / 'scoped-driver.py'),
                                     (source / builder, frozen / builder)):
                shutil.copy2(original, target)
                run.bind(target)
            run.inputs = snapshot_inputs(root, imported=True)
            write_json(run.directory / 'inputs.json', {'run_id': run.run_id, 'frozen_utc': utc_now(), 'files': run.inputs})
            run.bind(run.directory / 'inputs.json')
            run.manifest['input_count'] = len(run.inputs)
            run.save()
            engine = root / '.tools/godot/Godot_v4.5.1-stable_win64.exe'
            for view in ('opening', 'cliff-side', 'cliff-back'):
                output = run.directory / 'images' / (view + '.png')
                run.stage('capture-' + view, [engine, '--path', root, '--script', frozen / 'preview.gd',
                          '--', '--capture', '--view=' + view, '--output=' + str(output),
                          '--study-dir=' + str(frozen), '--validation-run=' + run.run_id], image=output)
            run.assert_inputs()
            require(len(run.manifest['stages']) == 3 and all(stage['passed'] for stage in run.manifest['stages']), 'Incomplete candidate capture')
            for path, record in run.manifest['artifacts'].items():
                require(sha256(run.directory / path) == record['sha256'], 'Evidence changed: ' + path)
            run.manifest.update(status='passed', passed=True, completed_utc=utc_now())
            run.save()
            print('CANDIDATE VIEWS READY ' + str(run.directory), flush=True)
        except Exception as error:
            run.manifest.update(status='failed', passed=False, error=str(error), completed_utc=utc_now())
            run.save()
            raise


if __name__ == '__main__':
    main()

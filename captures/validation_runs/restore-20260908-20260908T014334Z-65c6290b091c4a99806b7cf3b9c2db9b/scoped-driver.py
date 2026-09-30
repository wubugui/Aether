"""Record a new-machine source run; preserve historical rendering and reports."""
from pathlib import Path
import json
import shutil

from validation_manifest import (
    ValidationRun, exclusive_lock, input_diff, require, sha256,
    snapshot_inputs, utc_now, write_json,
)


def main():
    root = Path(__file__).resolve().parents[1]
    engine = root / '.tools/godot/Godot_v4.5.1-stable_win64.exe'
    with exclusive_lock(root / 'captures/.validation-pipeline.lock'):
        run = ValidationRun(root, 'restore-20260908', False, True)
        run.manifest['scope'] = 'New-machine source import, four GPU views and 36 source game checks. No Windows release or visual acceptance.'
        run.manifest['release_validation'] = False
        run.manifest['expected_counts'] = {'game-test': 36}
        shutil.copy2(__file__, run.directory / 'scoped-driver.py')
        run.bind(run.directory / 'scoped-driver.py')
        try:
            before = snapshot_inputs(root, imported=False)
            write_json(run.directory / 'preparation-inputs.json', {'files': before})
            run.bind(run.directory / 'preparation-inputs.json')
            run.stage('import', [engine, '--headless', '--editor', '--path', root, '--import', '--quit'])
            after = snapshot_inputs(root, imported=False)
            changes = input_diff(before, after)
            run.manifest['preparation_changes'] = changes
            require(all(path.endswith(('.import', '.uid')) for path in changes), 'Unexpected source change during import')
            run.inputs = snapshot_inputs(root, imported=True)
            write_json(run.directory / 'inputs.json', {'run_id': run.run_id, 'frozen_utc': utc_now(), 'files': run.inputs})
            run.bind(run.directory / 'inputs.json')
            run.manifest['input_count'] = len(run.inputs)
            run.save()
            marker = '--validation-run=' + run.run_id
            for view in ('opening', 'cliff-side', 'cliff-back', 'reverse'):
                output = run.directory / 'images' / (view + '.png')
                run.stage('capture-' + view, [engine, '--path', root, '--', '--capture',
                          '--view=' + view, '--output=' + str(output), marker], image=output)
            run.stage('game-test', [engine, '--path', root, '--', '--game-test', marker],
                      report=root / 'captures/game-validation.json')
            from PIL import Image
            import numpy as np
            baseline = root / 'captures/validation_runs/10l-cliff-terrain-edit-20260905T222858Z-e09be6fff0384003802bf7994a07d749/images/opening.png'
            opening = run.directory / 'images/opening.png'
            original = np.asarray(Image.open(baseline).convert('RGB'), dtype=np.int16)
            restored = np.asarray(Image.open(opening).convert('RGB'), dtype=np.int16)
            require(original.shape == restored.shape, 'Restored viewport size changed')
            comparison = {'baseline': str(baseline), 'baseline_sha256': sha256(baseline),
                          'restored_sha256': sha256(opening),
                          'pixels_equal': bool(np.array_equal(original, restored)),
                          'mean_absolute_channel_difference': float(np.abs(original - restored).mean()),
                          'max_channel_difference': int(np.abs(original - restored).max()),
                          'note': 'GPU/driver comparison only; does not prove reference fidelity.'}
            write_json(run.directory / 'machine-render-comparison.json', comparison)
            run.bind(run.directory / 'machine-render-comparison.json')
            run.assert_inputs()
            require(len(run.manifest['stages']) == 6 and all(stage['passed'] for stage in run.manifest['stages']), 'Incomplete restore run')
            for path, record in run.manifest['artifacts'].items():
                require(sha256(run.directory / path) == record['sha256'], 'Evidence changed: ' + path)
            run.manifest.update(status='passed', passed=True, completed_utc=utc_now())
            run.save()
            print('RESTORED SOURCE PASS ' + str(run.directory), flush=True)
            print(json.dumps(comparison), flush=True)
        except Exception as error:
            run.manifest.update(status='failed', passed=False, error=str(error), completed_utc=utc_now())
            run.save()
            raise


if __name__ == '__main__':
    main()

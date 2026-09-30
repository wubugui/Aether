"""Build one temporary independent cloud asset and render unmodified GPU views."""
from pathlib import Path
import subprocess, sys
root = Path('D:/test6'); label = sys.argv[1]
assert label in ['14a', '14b', '14c', '14d']
startup = subprocess.STARTUPINFO(); startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow = 0
if '--build' in sys.argv:
    stem = root / 'captures' / f'round-{label}-cloud-build'
    assert not stem.with_suffix('.stdout.log').exists()
    with stem.with_suffix('.stdout.log').open('w') as out, stem.with_suffix('.stderr.log').open('w') as err:
        result = subprocess.run([str(root / '.tools/blender/blender-4.5.0-windows-x64/blender.exe'), '--background', '--python-exit-code', '1', '--python', str(root / 'captures' / f'model_cloud_{label}.py')], cwd=root, stdout=out, stderr=err, startupinfo=startup, timeout=150)
    assert result.returncode == 0
    assert (root / 'captures' / f'cloud_study_{label}' / 'manifest.json').exists()
    print('BUILT', label, flush=True)
for view in sys.argv[2:]:
    if view == '--build':continue
    assert view in ['opening', 'cloud-side', 'cloud-back']
    stem = root / 'captures' / f'round-{label}-study-{view}'
    assert not stem.with_suffix('.png').exists()
    with stem.with_suffix('.stdout.log').open('w') as out, stem.with_suffix('.stderr.log').open('w') as err:
        result = subprocess.run([str(root / '.tools/godot/Godot_v4.5.1-stable_win64.exe'), '--path', str(root), '--script', str(root / 'captures' / f'preview_cloud_{label}.gd'), '--', '--capture', '--view=' + view, '--output=' + str(stem.with_suffix('.png'))], cwd=root, stdout=out, stderr=err, startupinfo=startup, timeout=100)
    assert result.returncode == 0 and stem.with_suffix('.png').exists()
    text = stem.with_suffix('.stdout.log').read_text(errors='replace') + stem.with_suffix('.stderr.log').read_text(errors='replace')
    assert not any(s in text for s in ['SCRIPT ERROR', 'ERROR:'])
    print(stem.with_suffix('.png'), flush=True)

"""Restore project import cache through the actual display; never save a scene."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

import run_orbit61 as base


def main():
    assert os.environ.get('DISPLAY'), 'Actual cloud desktop required; no headless fallback'
    assert not (base.PROJECT / 'captures/request_editor_validation.flag').exists(), 'Preserve pending editor requests; do not trigger one during import'
    assert base.digest(base.GODOT) == 'db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
    before = base.source_manifest()
    output = Path(tempfile.mkdtemp(prefix='nearbay61-import-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-', dir=base.AETHER / 'cloud-evidence'))
    userdata = Path(tempfile.mkdtemp(prefix='nearbay61-import-', dir=base.ROOT / 'tools-feiting'))
    print(output, flush=True)
    base.atomic_json(output / 'input-sha256.json', before)
    (output / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', PYTHONDONTWRITEBYTECODE='1')
    for key, folder in [('XDG_DATA_HOME', 'data'), ('XDG_CACHE_HOME', 'cache'), ('XDG_CONFIG_HOME', 'config')]:
        path = userdata / folder
        path.mkdir()
        env[key] = str(path)
    command = [str(base.GODOT), '--path', str(base.PROJECT), '--editor', '--import', '--quit', '--rendering-method', 'gl_compatibility', '--audio-driver', 'Dummy']
    base.atomic_json(output / 'wrapper-report.json', {'status': 'starting', 'passed': False, 'command': command, 'scene_save_requested': False})
    process = base.child_run(command, output, env, 180, 'import')
    after = base.source_manifest()
    base.atomic_json(output / 'output-sha256.json', after)
    logs = '\n'.join(p.read_text(errors='replace') for p in output.glob('*.log'))
    errors = [line for line in logs.splitlines() if line.startswith(('ERROR:', 'SCRIPT ERROR:'))]
    renderer = [line for line in logs.splitlines() if any(word in line for word in ['OpenGL', 'Vulkan', 'llvmpipe', 'Rendering Device'])]
    passed = process['returncode'] == 0 and before == after and not errors
    report = {'status': 'finished', 'passed': passed, 'process': process, 'sources_unchanged': before == after, 'input_count': len(before), 'logged_errors': errors, 'renderer_lines': renderer, 'scene_save_requested': False, 'runtime_or_visual_acceptance': False, 'output': str(output), 'userdata': str(userdata)}
    base.atomic_json(output / 'wrapper-report.json', report)
    (output / 'exit-code.txt').write_text('0\n' if passed else '1\n')
    print(json.dumps(report, indent=2), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

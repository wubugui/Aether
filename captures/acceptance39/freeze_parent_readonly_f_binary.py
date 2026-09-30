"""Supplement missing binary mesh dependencies; never replace frozen inputs."""
from pathlib import Path
import hashlib, json
root = Path(r'E:\FeiTing')
dest = root / 'captures/acceptance39/parent-readonly-f/project'
manifest = []
for src in (root / 'assets/meshes').glob('*'):
    if not src.is_file(): continue
    rel = src.relative_to(root)
    target = dest / rel
    if target.exists():
        assert target.read_bytes() == src.read_bytes(), 'Frozen dependency differs: ' + str(rel)
        continue
    target.parent.mkdir(parents=True, exist_ok=True)
    content = src.read_bytes()
    target.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    assert hashlib.sha256(src.read_bytes()).hexdigest() == digest
    manifest.append({'path': str(rel), 'bytes': len(content), 'sha256': digest})
(dest.parent / 'binary-supplement.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
print(json.dumps({'files': len(manifest), 'bytes': sum(x['bytes'] for x in manifest)}))

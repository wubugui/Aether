"""Supplement binary-resource dependencies absent from textual closure."""
from pathlib import Path
from hashlib import sha256
import json

root = Path(__file__).resolve().parents[1]
base = root / 'captures/acceptance39/frozen-audit-f'
project = base / 'project'
manifest = json.loads((base/'snapshot-manifest.json').read_text(encoding='utf8'))
added = []
for folder in ['assets', 'addons']:
    for source in (root/folder).rglob('*'):
        if not source.is_file(): continue
        rel = source.relative_to(root)
        target = project/rel
        if target.exists(): continue
        content = source.read_bytes()
        digest = sha256(content).hexdigest()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        assert sha256(source.read_bytes()).hexdigest() == digest
        added.append({'path':rel.as_posix(), 'bytes':len(content), 'sha256':digest})
critical = [r for r in manifest['source_files'] if r['path'].endswith(('.gd','.gdshader','.tscn','.tres','.json','.godot'))]
changed = [r['path'] for r in critical if sha256((root/r['path']).read_bytes()).hexdigest()!=r['sha256']]
assert not changed, changed
manifest['source_files'].extend(added)
manifest['supplement_reason'] = 'Binary .res references are not exposed by text-only scan; include complete assets and editor addon directories.'
manifest['invalid_run'] = 'gpu-g: incomplete dependency snapshot; must not attribute its loading failures or visuals to source.'
(base/'snapshot-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps({'added_files':len(added),'bytes':sum(r['bytes'] for r in added),'critical_source_changed':changed}))

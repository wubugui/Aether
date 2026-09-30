"""Freeze runtime dependency closure without mutating shared project files."""
from pathlib import Path
import hashlib, json, re, shutil

root = Path(r'E:\FeiTing')
dest = root / 'captures/acceptance39/parent-readonly-f/project'
assert not dest.exists(), 'Do not overwrite an existing frozen validation project'
dest.mkdir(parents=True)
pending = ['project.godot', 'scenes/candidate39/Game39.tscn',
           'tools/verify_candidate39.gd', 'assets/world_layout.json',
           'assets/asset_catalog.json', 'assets/reference_views39.json']
pending += [str(p.relative_to(root)).replace('\\', '/')
            for p in (root / 'scenes/prefabs').glob('*.tscn')]
seen, manifest = set(), []
while pending:
    rel = pending.pop()
    if rel in seen: continue
    seen.add(rel)
    src = root / rel
    if not src.is_file(): continue
    content = src.read_bytes()
    target = dest / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    digest = hashlib.sha256(content).hexdigest()
    assert hashlib.sha256(src.read_bytes()).hexdigest() == digest, 'Source changed during capture: ' + rel
    manifest.append({'path': rel, 'bytes': len(content), 'sha256': digest})
    if src.suffix in ['.gd', '.tscn', '.tres', '.godot', '.import', '.cfg']:
        pending.extend(re.findall(r'res://([^"\s)]+)', content.decode('utf8', errors='replace')))
    if (root / (rel + '.import')).is_file(): pending.append(rel + '.import')
    if src.suffix == '.gd' and (root / (rel + '.uid')).is_file(): pending.append(rel + '.uid')

# The entry under verification is selected by the test, not project main_scene.
# A runtime closure includes dynamic prefab imports listed above; no full world
# generator or editor import process is run against the shared source project.
out = dest.parent
out.joinpath('manifest.json').write_text(json.dumps({
    'scope': 'Unmodified shared source bytes frozen for isolated read-only validation',
    'project': str(dest), 'files': sorted(manifest, key=lambda x: x['path'])
}, indent=2), encoding='utf8')
print(json.dumps({'files': len(manifest), 'bytes': sum(f['bytes'] for f in manifest),
                  'scene': next(f['sha256'] for f in manifest if f['path'] == 'scenes/candidate39/Game39.tscn'),
                  'project': str(dest)}))

"""Copy the current native candidate's dependency closure; never alter sources."""
import hashlib, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / 'captures/acceptance39/frozen-audit-f/project'
DEST.mkdir(parents=True, exist_ok=False)
queue = ['project.godot', 'scenes/candidate39/Game39.tscn', 'tools/verify_candidate39.gd']
# open_world dynamically constructs prefab resource paths from the catalog.
queue += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'scenes/prefabs').rglob('*.tscn')]
seen, rows, missing = set(), [], []
while queue:
    relative = queue.pop()
    if relative in seen: continue
    seen.add(relative)
    src = ROOT / relative
    if not src.is_file():
        missing.append(relative)
        continue
    content = src.read_bytes()
    before = hashlib.sha256(content).hexdigest()
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before, f'Source changed during copy: {relative}'
    rows.append({'path': relative, 'bytes': len(content), 'sha256': before})
    if src.suffix.lower() in ['.gd', '.gdshader', '.tscn', '.tres', '.godot', '.cfg', '.json']:
        text = content.decode('utf-8', errors='replace')
        for resource in re.findall(r'res://([^"\s\r\n]+)', text):
            # Ignore dynamic path prefixes; all prefabs are enumerated above.
            if not resource.endswith('/') and not resource.startswith('captures/'):
                queue.append(resource)
    # Preserve import metadata and its already-imported resources if used.
    sidecar = pathlib.Path(str(src) + '.import')
    if sidecar.is_file(): queue.append(sidecar.relative_to(ROOT).as_posix())
manifest = {'root': str(DEST), 'source_files': sorted(rows, key=lambda r:r['path']),
            'unresolved_literals': sorted(missing), 'mode': 'byte copies; shared source unmodified'}
(DEST.parent / 'snapshot-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps({'files':len(rows), 'bytes':sum(r['bytes'] for r in rows), 'missing':missing, 'root':str(DEST)}))

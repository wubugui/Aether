from pathlib import Path
import json,hashlib,collections,subprocess
R=Path('/workspace/scratch/a29d03198654/Aether').resolve()
O=Path(__file__).resolve().parent
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def classify(name):
    parts=Path(name).parts
    if 'shader_cache' in parts:return 'godot-generated-shader-cache'
    if '.godot' in parts:return 'godot-generated-import-and-editor-cache'
    if '__pycache__' in parts:return 'python-derived-bytecode'
    if name.endswith('.gz'):return 'superseded-gzip-original-raw-restored-from-xz'
    if '/fontconfig/' in name:return 'fontconfig-generated-cache'
    if '/logs/' in name and name.endswith('.log'):return 'godot-userdata-runtime-log'
    if '/extensions/.cache/compat.dat' in name:return 'blender-generated-extension-compat-cache'
    if name.endswith('/config/godot/editor_settings-4.5.tres'):return 'godot-generated-editor-settings'
    if any(k in parts for k in ('cache','xdg-cache','.cache')):return 'other-generated-cache'
    return 'unclassified-review-required'
cache={};result=[]
for p in sorted(R.glob('cloud-evidence/cloudbank58l-form-v3-*/protected-before.json')):
    expected=json.loads(p.read_text()); exact=[];different=[];missing=[];outside=[]
    for name,want in expected.items():
        path=Path(name)
        if not path.is_relative_to(R):outside.append(name);continue
        relative=str(path.relative_to(R))
        if not path.exists():missing.append(dict(path=relative,expected_sha256=want,category=classify(relative)));continue
        if name not in cache:cache[name]=(path.stat().st_size,digest(path))
        size,actual=cache[name]
        if actual==want:exact.append(dict(path=relative,bytes=size,sha256=actual))
        else:different.append(dict(path=relative,bytes=size,actual_sha256=actual,expected_sha256=want))
    row=dict(manifest=str(p.relative_to(R)),historical_count=len(expected),currently_exact_count=len(exact),currently_exact_bytes=sum(x['bytes'] for x in exact),missing_count=len(missing),missing_categories=dict(collections.Counter(x['category'] for x in missing)),missing=missing,different=different,outside_root=outside)
    result.append(row)
    print(json.dumps({k:v for k,v in row.items() if k not in ('missing','different')},indent=2));print('DIFFERENT',json.dumps(different,indent=2))
    print('UNCLASSIFIED',json.dumps([x for x in missing if x['category']=='unclassified-review-required'],indent=2))
missing={x['path']:x for row in result for x in row['missing']}
for row in result:
    row.pop('missing');row['missing_paths_catalog']='common-missing-protected-paths.json'
(O/'historical-protected-path-audit.json').write_text(json.dumps(result,indent=2)+'\n')
(O/'common-missing-protected-paths.json').write_text(json.dumps(list(missing.values()),indent=2)+'\n')

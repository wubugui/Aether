"""Pure, fail-closed path and identity gates for an already restored source."""
import os, sys
from pathlib import Path
sys.dont_write_bytecode = True
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
HERE = Path(__file__).resolve().parent
V2 = HERE.parent / 'recovery-v2'
sys.path.insert(0, str(V2))
import run_source62 as original
c, support, inherited = original.c, original.support, original.inherited
VERSION = 'north-ridge62-restore-read-v1'
RUN_REL = 'cloud-evidence/north-ridge62-recovery-v2-source-20261002T114825Z-lnt78w53'
ACTUAL_RUN = c.ROOT / RUN_REL
SOURCE_REL = 'source-assets/north-ridge62-authoring/recovery-v2/north-ridge62.blend'
RAW_REL = RUN_REL + '/outputs/build-raw.json'
EXPECTED = {
    SOURCE_REL: (10004835, 'dd1d3c12b8c3f98fdcd42a21057d519f1cac48eeab468cbc7721d1c1673ab502'),
    RAW_REL: (14837932, 'c941a75a43a5c4f88d4083c403cb9f3219752c49056405bed66840803b0f629b'),
    RUN_REL + '/outputs/verify-raw.json': (14837933, '9e476591b52fe1980bc9a55019914c6a555fa75dc97ad4e70bedb5194d037633'),
    RUN_REL + '/outputs/embedded-text-inputs/BINDINGS62.json': (5424727, '40bb1d7510384575421b4c8a588b48692ef5bced8e5cb02fa7439abab93cb310'),
}
STORAGE_PINS = {
    'native-storage.json': '33ed9807b334df2aae8f5e994a52e7900d3ce0bc234cb074e09a226d652beb06',
    'restore_native.py': 'fab4155f6a2fb0265d07814107a2bbeebe8f0093444a36347bd6e83e311e7f89',
}


def no_symlinks(path):
    path = Path(path)
    c.require(path.is_absolute() and '..' not in path.parts, 'Explicit absolute path without traversal required')
    for part in [path, *path.parents]:
        c.require(not part.is_symlink(), 'Symlink path/ancestor forbidden: ' + str(part))
    c.require(path.resolve(strict=True) == path, 'Existing normalized path required')
    return path


def tree_identity(root):
    root = no_symlinks(root)
    c.require(root.is_dir(), 'Directory required')
    files = inherited.file_manifest(root)  # Unchanged audited recursive SHA helper.
    dirs = [str(p.relative_to(root)) for p in sorted(root.rglob('*')) if p.is_dir()]
    return dict(files=files, directories=dirs)


def validate_layout(root, source, expected, canonical_root, source_rel):
    """Dependency-injected only for tiny pure fixtures; production passes fixed pins."""
    root, source = no_symlinks(root), no_symlinks(source)
    canonical_root = no_symlinks(canonical_root)
    c.require(not root.is_relative_to(canonical_root) and not canonical_root.is_relative_to(root),
              'Restore root must be separate from the original repository')
    c.require(source == root / source_rel and source.is_file(), 'Only explicit manifest-restored source may open')
    identity = tree_identity(root)
    c.require(set(identity['files']) == {str(root / p) for p in expected}, 'Exact four-file restored membership required')
    expected_dirs = set()
    for name in expected:
        rel = Path(name)
        c.require(not rel.is_absolute() and '..' not in rel.parts, 'Safe manifest relative path')
        expected_dirs.update(str(p) for p in rel.parents if str(p) != '.')
        path = root / rel
        size, digest = expected[name]
        c.require(path.stat().st_nlink == 1, 'Independent restored file: hardlinks forbidden')
        original_path = canonical_root / rel
        c.require(not original_path.exists() or not os.path.samefile(path, original_path), 'Original inode forbidden')
        c.require(path.stat().st_size == size and identity['files'][str(path)] == digest, 'Restored size/SHA mismatch: ' + name)
    c.require(set(identity['directories']) == expected_dirs, 'Exact restored directory membership required')
    return identity


def restore_identity(root, source):
    return validate_layout(root, source, EXPECTED, c.ROOT, SOURCE_REL)


def preparation_inputs(require_local_freeze=False):
    pins = original.frozen_inputs()  # All existing recovery-v2 gates and helper pins.
    for name, digest in STORAGE_PINS.items():
        path = ACTUAL_RUN / name
        c.require(c.sha(path) == digest, 'Actual storage contract changed: ' + name)
        pins[str(path)] = digest
    manifest = support.strict_json(ACTUAL_RUN / 'native-storage.json')
    c.require(manifest['version'] == 1 and len(manifest['files']) == 4, 'Actual storage schema')
    c.require({r['restore_path']: (r['bytes'], r['sha256']) for r in manifest['files']} == EXPECTED, 'Actual restoration identities')
    for item in manifest['files']:
        for part in item['parts']:
            path = no_symlinks(c.ROOT / part['path'])
            c.require(path.is_relative_to(ACTUAL_RUN / 'lossless-storage') and path.is_file(), 'Actual chunk path')
            c.require(path.stat().st_size == part['bytes'] and c.sha(path) == part['sha256'], 'Actual chunk size/SHA')
            pins[str(path)] = part['sha256']
    for name, (size, digest) in EXPECTED.items():
        path = no_symlinks(c.ROOT / name)
        c.require(path.is_file() and path.stat().st_size == size and c.sha(path) == digest, 'Actual original size/SHA: ' + name)
        pins[str(path)] = digest
    terminal = support.strict_json(V2 / 'source-terminal.json')
    c.require(terminal['passed'] is True and terminal['source_sha256'] == EXPECTED[SOURCE_REL][1], 'Actual source/fresh-read success gate')
    c.require(Path(terminal['run']) == ACTUAL_RUN, 'Actual successful run identity')
    pins[str(V2 / 'source-terminal.json')] = c.sha(V2 / 'source-terminal.json')
    if require_local_freeze:
        freeze = HERE / 'FINAL_SHA256.json'
        data = support.strict_json(freeze)
        needed = {str(p.relative_to(c.ROOT)) for p in HERE.glob('*.py')} | {str((HERE / 'README.md').relative_to(c.ROOT))}
        c.require(needed <= data['files'].keys(), 'Reviewed restore-read preparation must be frozen')
        for name, row in data['files'].items():
            path = no_symlinks(c.ROOT / name)
            c.require(path.is_relative_to(HERE) and path.is_file() and c.sha(path) == row['sha256'], 'Local frozen preparation identity')
            pins[str(path)] = row['sha256']
        pins[str(freeze)] = c.sha(freeze)
    return pins


def protected_identity():
    # Do NOT inherit recovery-v2's exclusions: canonical .blend and all previous
    # admission/terminal files are protected, including full directory membership.
    roots = [c.ROOT / p for p in ('source-assets', 'blender', 'assets', 'ref')]
    roots += [inherited.PROJECT, ACTUAL_RUN]
    return dict(trees={str(p): tree_identity(p) for p in roots},
                project_godot_sha256=c.sha(no_symlinks(c.ROOT / 'project.godot')))


def same_raw(actual, reference):
    c.require(type(actual.get('pid')) is int and type(reference.get('pid')) is int, 'Actual native PIDs')
    # Numeric PIDs may repeat across old runs/namespaces. Freshness is proved by
    # this wrapper's new Popen/wait4 record and exact opened restored filepath.
    omit = ('pid', 'cpu_affinity')
    # JSON comparison also distinguishes bool/int, int/float and signed zero;
    # plain Python equality would silently consider some of those equal.
    exact = lambda raw: c.json.dumps({k: v for k, v in raw.items() if k not in omit},
                                    sort_keys=True, separators=(',', ':'), allow_nan=False)
    c.require(exact(actual) == exact(reference), 'Entire actual raw differs outside PID/affinity')
    return True

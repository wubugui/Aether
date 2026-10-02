"""Bounded static preparation check; explicitly never imports bpy or runs Blender."""
import argparse
import ast
import json
from pathlib import Path
import resource
import sys
import time
import numpy as np

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent / 'revision-d/native-01'))
import common58d as c


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-preparation-report', action='store_true', required=True)
    parser.parse_args()
    start = time.monotonic()
    report_path, freeze_path = P / 'preparation-check58f2.json', P / 'preparation-freeze58f2.json'
    assert not report_path.exists() and not freeze_path.exists(), 'Keep prior preparation evidence'
    assert not (P / 'shared_patch58f2.blend').exists()
    scripts = ['patch58f.py', 'source58f.py', 'run_patch58f2.py', 'check_preparation58f2.py']
    syntax = []
    for name in scripts:
        ast.parse((P / name).read_bytes(), filename=name)
        syntax.append(dict(path=str((P / name).relative_to(c.ROOT)), sha256=c.sha(P / name), syntax_passed=True))
    frame = json.loads(c.PLAN.read_text())
    old = c.load_pure(P.parent / 'revision-f/patch58f.py').make_patch(frame)
    spec = c.load_pure(P / 'patch58f.py').make_patch(frame)
    original, revised = np.asarray(old['vertices']), np.asarray(spec['vertices'])
    changed = np.where(np.any(original != revised, axis=1))[0].tolist()
    assert changed == [113, 127, 133, 134, 138, 141, 142, 166, 180]
    failed = c.ROOT / 'cloud-evidence/cloudbank58f-patch-20261001T190306Z-xl109553/outputs/build-result58f.json'
    native = json.loads(failed.read_text())
    assert not native['passed']
    source = c.source_coordinates(revised, frame).astype(np.float32).astype(float)
    rows = []
    for camera in native['cameras']:
        matrix, projection = np.asarray(camera['matrix_world']), np.asarray(camera['projection'])
        points = np.c_[source, np.ones(len(source))] @ np.linalg.inv(matrix).T @ projection.T
        normal = (points[:, :2] / points[:, 3, None] + 1) / 2
        margin = float(min(normal.min(), 1 - normal.max()))
        depths = -(np.c_[source, np.ones(len(source))] @ np.linalg.inv(matrix).T)[:, 2]
        assert min(depths) > 0
        if camera['name'] == 'shared-side-back':
            assert margin >= .07
        rows.append(dict(name=camera['name'], bounds=[normal.min(axis=0), normal.max(axis=0)],
                         minimum_margin=margin, minimum_depth_m=float(min(depths)),
                         native_camera_not_reexecuted=True, static_prediction_only=True))
    manifests = [c.FREEZE,
        P.parent / 'revision-d/native-01/native-freeze58d-20261001T1620Z.json',
        P.parent / 'revision-d/preview-01/preview-freeze58d-20261001T1634Z.json',
        P.parent / 'revision-e/layout-freeze58e-20261001T1659Z.json',
        P.parent / 'revision-c-complete-freeze-20261001T1305Z.json',
        P.parent / 'revision-f/failure-freeze58f.json']
    protected = {}
    for path in manifests:
        protected.update(json.loads(path.read_text())['files'])
    assert all(c.sha(c.ROOT / path) == row['sha256'] for path, row in protected.items())
    report = dict(status='Prepared only; static scope/projection/syntax checks passed', passed=True,
        scripts=syntax, changed_vertex_ids=changed, world_xz_exact=np.array_equal(original[:, [0, 2]], revised[:, [0, 2]]),
        top_grid_exact=np.array_equal(original[:63], revised[:63]), faces_exact=old['faces'] == spec['faces'],
        edit_groups_exact=old['groups'] == spec['groups'], cameras_static_only=rows,
        failed_f_native_report_sha256=c.sha(failed), protected_file_count=len(protected),
        protected_unchanged=True, source_generated=False, blender_started=False, images=[],
        world_loaded=False, final_geometry_pass=False, visual_acceptance=False,
        elapsed_seconds=time.monotonic() - start,
        actual_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    c.write(report_path, report)
    paths = set(json.loads((P.parent / 'revision-f/preparation-freeze58f.json').read_text())['files'])
    paths.update(json.loads((P.parent / 'revision-f/failure-freeze58f.json').read_text())['files'])
    paths.update(str(path.relative_to(c.ROOT)) for path in manifests)
    paths.update(str((P / name).relative_to(c.ROOT)) for name in scripts + ['README.md', report_path.name])
    paths.add(str((P.parent / 'revision-f/failure-freeze58f.json').relative_to(c.ROOT)))
    files = {path: dict(bytes=(c.ROOT / path).stat().st_size, sha256=c.sha(c.ROOT / path)) for path in sorted(paths)}
    c.write(freeze_path, dict(status='F2 preparation only; Blender requires parent-scheduled window',
            files=files, file_count=len(files), world_loaded=False, final_geometry_pass=False, visual_acceptance=False))
    print(json.dumps(c.native(report), indent=2))


if __name__ == '__main__':
    main()

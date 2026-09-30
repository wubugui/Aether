"""Apply the existing production section-surface gate to a candidate assembly.

Read-only for all assets. This detects projected roof folds, not 3D collisions
or visual quality. A failure is retained and prevents treating manifold checks
alone as sufficient integration evidence.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
from shapely import union_all
from shapely.geometry import Polygon

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('label', choices=['16a', '16b', '16c', '16d', '16e', '16f', '16g', '17a', '17b', '17c', '17d', '17e'])
args = parser.parse_args()
output = root/'reviews'/('round-' + args.label + '-projected-surface-gate.json')
assert not output.exists(), output
syntax = ast.parse((root/'tools/verify_geology_assets.py').read_text())
reader = {}
exec(compile(ast.Module(body=[node for node in syntax.body if isinstance(node,
    (ast.Import, ast.ImportFrom, ast.FunctionDef))], type_ignores=[]), 'GLB reader definitions', 'exec'), reader)
items = {x['name']: x for x in json.loads((root/'captures'/('foreground_study_' + args.label)/'manifest.json').read_text())}
results = []
for kind in ['crown', 'western_slab', 'front_columns', 'shadow_buttress', 'central_wall']:
    name = 'cliff_' + kind
    item = items.get(name)
    path = root/item['path'] if item else root/'assets/models'/(name + '.glb')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if item:
        assert digest == item['glb_sha256']
    _, tri = reader['triangles'](path)
    normal = np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0])
    area = np.linalg.norm(normal, axis=1)
    downward = (tri[:,:,1].max(axis=1)>0) & (normal[:,1]/np.maximum(area,1e-9)<-.001)
    roof = tri[normal[:,1]>1e-6]
    polygons = [Polygon(t[:,[0,2]]) for t in roof]
    invalid = sum(not p.is_valid for p in polygons)
    overlap = sum(p.area for p in polygons)-union_all(polygons).area
    passed = invalid == 0 and not downward.any() and abs(overlap)<.001
    results.append({'name': name, 'path': str(path.relative_to(root)), 'candidate': bool(item),
        'passed': bool(passed), 'sha256': digest, 'roof_faces': len(polygons),
        'invalid_projected_faces': invalid, 'downward_nonfloor_faces': int(downward.sum()),
        'downward_triangle_indices': np.where(downward)[0].tolist(),
        'overlapping_projected_roof_area_m2': float(overlap)})
    print(name, 'PASS' if passed else 'FAIL', 'downward', int(downward.sum()), 'overlap_m2', overlap)
report = {'passed': all(x['passed'] for x in results), 'label': args.label,
    'scope': 'Existing five-section production height-surface gate, applied to candidate GLBs plus two unchanged production assets. Not a cross-asset collision or visual verdict.',
    'algorithm_source': 'captures/check_section_surface_overlaps.py', 'assets': results}
output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
raise SystemExit(0 if report['passed'] else 1)

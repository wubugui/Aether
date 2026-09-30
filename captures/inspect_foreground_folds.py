"""Locate candidate downward roof triangles against native control labels."""
import ast
import json
from pathlib import Path
import numpy as np
root = Path(__file__).resolve().parents[1]
syntax = ast.parse((root/'tools/verify_geology_assets.py').read_text())
reader = {}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'reader','exec'),reader)
prior = {x['name']:x for x in json.loads((root/'captures/foreground-16-source-inspection.json').read_text())}
items = {x['name']:x for x in json.loads((root/'captures/foreground_study_16f/manifest.json').read_text())}
gate = json.loads((root/'reviews/round-16f-projected-surface-gate.json').read_text())
for asset in gate['assets']:
    if not asset['candidate']:continue
    item = items[asset['name']]
    data = {str(x['index']):x['xyz'] for x in prior[asset['name']]['controls']}
    data.update({str(x['index']):x['after'] for x in item['controls']})
    for row in item.get('shelf_controls',[]):data['shelf'+str(row['column'])] = row['shelf_blender_xyz']
    for row in item.get('wall_bend_controls',[]):data['bend'+str(row['column'])] = row['bend_blender_xyz']
    labels = list(data)
    positions = np.array(list(data.values()))[:,[0,2,1]] * [1,1,-1]
    _,tri = reader['triangles'](root/asset['path'])
    print(asset['name'])
    for index in asset['downward_triangle_indices']:
        labels_here = []
        for point in tri[index]:
            distance = np.linalg.norm(positions-point,axis=1)
            j = int(np.argmin(distance))
            labels_here.append(labels[j] if distance[j]<1e-4 else 'rim-or-floor')
        print(index, labels_here, np.round(tri[index],3).tolist())

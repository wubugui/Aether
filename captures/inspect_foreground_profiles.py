"""Read fixed world/profile coordinates without starting either engine."""
import json
import math
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
catalog = {x['name']: x for x in json.loads((root/'assets/cliff_kit.json').read_text())}
native = json.loads((root/'captures/foreground-16-source-inspection.json').read_text())
candidates = {x['name']: x for x in json.loads((root/'captures/foreground_study_16c/manifest.json').read_text())}
focal = 941/(2*math.tan(math.radians(25)))
pitch = math.radians(-3.526)
def project(p):
    x,y,z = p - [0,145,250]
    cy = math.cos(pitch)*y + math.sin(pitch)*z
    cz = -math.sin(pitch)*y + math.cos(pitch)*z
    return [round(836+focal*x/-cz,1), round(470.5-focal*cy/-cz,1)]
for asset in native:
    name = asset['name']
    count = 8 if name == 'cliff_crown' else 4 if name == 'cliff_front_columns' else 5
    data = {x['index']: x['xyz'] for x in asset['controls']}
    for edit in candidates.get(name,{}).get('controls',[]):data[edit['index']] = edit['after']
    print(name)
    for i in range(count*4):
        xyz = np.array(data[i])[[0,2,1]] * [1,1,-1] + catalog[name]['position']
        print(i, 'world',np.round(xyz,2).tolist(), 'screen',project(xyz))

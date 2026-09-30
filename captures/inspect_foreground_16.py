"""Read native foreground controls; keep all authoring sources unchanged."""
from pathlib import Path
import bpy
import json

root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / 'assets/cliff_kit.json').read_text())
rows = []
for name in ('cliff_crown', 'cliff_western_slab', 'cliff_front_columns', 'cliff_central_wall'):
    item = next(item for item in catalog if item['name'] == name)
    bpy.ops.wm.open_mainfile(filepath=str(root / item['native_source']))
    obj = bpy.data.objects[name]
    rows.append({'name': name, 'location': list(obj.location), 'rotation': list(obj.rotation_euler),
                 'scale': list(obj.scale), 'matrix_world': [list(row) for row in obj.matrix_world],
                 'vertices': len(obj.data.vertices), 'faces': len(obj.data.polygons),
                 'vertex_groups': [group.name for group in obj.vertex_groups],
                 'attributes': [(attribute.name, attribute.domain) for attribute in obj.data.attributes],
                 'controls': [{'index': v.index, 'xyz': list(v.co)} for v in obj.data.vertices[:50]],
                 'faces_first': [{'indices': list(face.vertices), 'normal': list(face.normal)}
                                 for face in obj.data.polygons[:42]]})
output = root / 'captures/foreground-16-source-inspection.json'
assert not output.exists()
output.write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
print('NATIVE FOREGROUND INSPECTION ' + str(output), flush=True)

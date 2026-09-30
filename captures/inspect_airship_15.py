from pathlib import Path
import bpy,json
from mathutils import Vector
root=Path('D:/test6')
bpy.ops.wm.open_mainfile(filepath=str(root/'blender/Assets.blend'))
rows=[]
for o in bpy.data.collections['Airship'].objects:
    row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'scale':list(o.scale),'matrix_local':[list(r) for r in o.matrix_local]}
    if o.type=='MESH':
        row.update(vertices=len(o.data.vertices),faces=len(o.data.polygons),bounds=[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)])
    rows.append(row)
(root/'captures/airship-15-source-inspection.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=1),flush=True)

import bpy,json
from pathlib import Path
scene=bpy.context.scene
report={'file':bpy.data.filepath,'meshes':sum(o.type=='MESH' for o in bpy.data.objects),'objects':len(bpy.data.objects),'terrain_triangles':scene.get('terrain_triangles'),'placements':scene.get('placed_models'),'ship_world_position':list(bpy.data.objects['Airship'].matrix_world.translation),'camera_world_position':list(scene.camera.location),'collections':[c.name for c in bpy.data.collections]}
Path('D:/test6/captures/blender-world-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))

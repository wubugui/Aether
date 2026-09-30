import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
P=Path(__file__).resolve().parent
report={'method':'Orthographic vertical triangle ray coverage over a fixed world-space 3600 x 2000 rectangle, 180 x 100 cell centers, per native asset. Not a game camera or visual acceptance.','measurements':[]}
for file,prefix in [(P.parent/'hub-cloud41/cloud_sea41.blend','cloud_bank_41_'),(P/'cloud_bank44.blend','cloud_bank_44_')]:
 bpy.ops.wm.open_mainfile(filepath=str(file))
 for var in range(3):
  verts=[];faces=[]
  for o in bpy.data.collections[prefix+str(var)].objects:
   offset=len(verts);verts.extend([o.matrix_world@v.co for v in o.data.vertices]);faces.extend([tuple(offset+i for i in p.vertices) for p in o.data.polygons])
  tree=BVHTree.FromPolygons(verts,faces,all_triangles=True);hit=0
  for x in range(180):
   for y in range(100):
    if tree.ray_cast(Vector((-1800+(x+.5)*20,-1000+(y+.5)*20,-3000)),Vector((0,0,1)))[0] is not None:hit+=1
  report['measurements'].append({'asset':prefix+str(var),'vertical_occupied_area_estimate':hit*400,'hits':hit,'total_rays':18000})
(P/'bank44-footprint-rays.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

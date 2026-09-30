import bpy,bmesh,json,math,re,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
report={}
for label,file,prefix in [('original41',P.parent/'hub-cloud41/cloud_sea41.blend','cloud_sea_41'),('candidate46',P/'cloud_sea46.blend','cloud_sea_46')]:
 bpy.ops.wm.open_mainfile(filepath=str(file));out=[]
 for variant in range(3):
  obs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(f'{prefix}_{variant}_')]
  vs=[];fs=[]
  for o in obs:
   offset=len(vs);vs.extend([o.matrix_world@v.co for v in o.data.vertices]);fs.extend([tuple(offset+k for k in p.vertices) for p in o.data.polygons])
  tree=BVHTree.FromPolygons(vs,fs);bottom=[];top=[]
  for x in range(-900,901,30):
   for y in range(-900,901,30):
    hit=tree.ray_cast(Vector((x,y,-1000)),Vector((0,0,1)),2500)
    if hit[0] is not None:
     bottom.append(hit[0].z);up=tree.ray_cast(Vector((x,y,1000)),Vector((0,0,-1)),2500);top.append(up[0].z)
  bottom.sort();top.sort()
  out.append({'variant':variant,'parts':len(obs),'sampled_footprint_area':len(bottom)*900,'bottom_height_p10_p50_p90':[bottom[int((len(bottom)-1)*t)] for t in [.1,.5,.9]],'top_height_p10_p50_p90':[top[int((len(top)-1)*t)] for t in [.1,.5,.9]],'bounds_blender_xyz':[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]})
 report[label]=out
src=P.parent.parent/'project/scenes/candidate44/Game44.tscn';txt=src.read_text();instances=[]
for name,tr in re.findall(r'\[node name="(CloudSea_[^"]+)"[^\n]+\]\ntransform = Transform3D\(([^)]+)\)',txt):instances.append({'name':name,'transform':tr})
report['original25_world_anchors']=instances
report['original_scene_sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
report['evidence_boundary']='Mesh-derived CPU ray tests and saved scene transforms. Does not identify which asset covers a camera pixel. No hardware GPU or whole-world acceptance.'
(P/'geometry-comparison46.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

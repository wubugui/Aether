from pathlib import Path
import bpy,bmesh,json,math,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
rows=[]
for revision in ['c','d']:
 source=ROOT/f'source-assets/cloud-sea52h-revision-{revision}/cloud_sea52h_{revision}.blend';bpy.ops.wm.open_mainfile(filepath=str(source));ob=bpy.data.objects[f'CloudSea52h{revision.upper()}_v0_main_crown'];bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table();normals=[f.normal.copy() for f in bm.faces];areas=[f.calc_area() for f in bm.faces];neighbors=[{other.index for edge in f.edges for other in edge.link_faces if other!=f} for f in bm.faces];limit=math.cos(math.radians(2));best=[];best_area=0
 for seed in range(len(normals)):
  used={seed};queue=[seed];area=areas[seed]
  while queue:
   i=queue.pop()
   for j in neighbors[i]:
    if j not in used and normals[seed].dot(normals[j])>=limit:
     used.add(j);queue.append(j);area+=areas[j]
  if area>best_area:best_area=area;best=list(used)
 points=[v.co for i in best for v in bm.faces[i].verts];lo=[min(v[k] for v in points) for k in range(3)];hi=[max(v[k] for v in points) for k in range(3)]
 rows.append({'revision':revision,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'triangles':len(bm.faces),'largest_connected_two_degree_patch_triangles':len(best),'patch_area_m2':best_area,'whole_surface_area_m2':sum(areas),'patch_area_percent':100*best_area/sum(areas),'patch_bounds_xyz':[lo,hi]});bm.free()
out={'method':'For every final triangle, flood only adjacent triangles whose unit normal stays within2degrees of that seed normal. Report the maximum connected area. This measures broad near-planar surface extent, not visual style or cloud acceptance.','rows':rows,'rendered':False,'visual_acceptance':False}
(P/'connected-near-planar-patches.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

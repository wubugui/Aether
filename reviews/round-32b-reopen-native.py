from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];P=R/'captures/foreground_island_study_32b';source=P/'island_a.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));plan=json.loads((P/'design-plan.json').read_text());objects={};stats=[];bvhs={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);small=sum(f.calc_area()<=1e-10 for f in bm.faces);parts=0;remain=set(bm.verts)
 while remain:
  parts+=1;stack=[remain.pop()]
  while stack:
   a=stack.pop()
   for ed in a.link_edges:
    b=ed.other_vert(a)
    if b in remain:remain.remove(b);stack.append(b)
 bm.free();o.data.calc_loop_triangles();verts=[list(o.matrix_world@v.co) for v in o.data.vertices];tri=[list(t.vertices) for t in o.data.loop_triangles];bvhs[o.name]=BVHTree.FromPolygons([Vector(x) for x in verts],tri,all_triangles=True);stats.append({'name':o.name,'vertices':len(verts),'polygons':len(o.data.polygons),'triangles':len(tri),'nonmanifold_edges':bad,'tiny_faces':small,'signed_volume_m3':volume,'connected_components':parts,'matrix_world':[list(row) for row in o.matrix_world]});objects[o.name]={'vertices':verts,'polygons':[list(f.vertices) for f in o.data.polygons],'triangles':tri,'materials':[f.material_index for f in o.data.polygons]}
trees=[]
for x,y,scale in plan['trees_blender_xy_scale']:
 hits=[]
 for name,bvh in bvhs.items():
  loc,norm,face,dist=bvh.ray_cast(Vector((x,y,120)),Vector((0,0,-1)))
  if loc is not None:hits.append({'object':name,'z':loc.z,'normal':list(norm),'triangle':face})
 hits.sort(key=lambda a:a['z'],reverse=True);trees.append({'xy':[x,y],'scale':scale,'all_object_hits':hits,'highest':hits[0] if hits else None,'highest_is_footpath':bool(hits and 'paths' in hits[0]['object'])})
after=hashlib.sha256(source.read_bytes()).hexdigest();assert before==after and len(stats)==11
report={'scope':'Independent actual saved32b source opened in fresh background Blender; no builder rerun or source save. Native mesh validity and8planned tree-axis top hits across all11meshes.','source_sha256':before,'source_file_unchanged':before==after,'native':stats,'objects':objects,'planned_trees_actual_rays':trees,'native_closed_positive_pass':all(s['nonmanifold_edges']==0 and s['tiny_faces']==0 and s['signed_volume_m3']>0 for s in stats),'limits':['Native topology check is not exhaustive3D self-intersection.','Tree-axis hits only, not full tree-base contact/foliage clearance.','Full footprint terrain clipping performed independently on actualGLB in separate CPU script.']}
(R/'reviews/round-32b-reopened-source.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'native_objects':len(stats),'native_closed_positive_pass':report['native_closed_positive_pass'],'planned_tree_highest_hits':[{'xy':a['xy'],'highest':a['highest'],'on_path':a['highest_is_footpath']} for a in trees]},indent=2),flush=True)

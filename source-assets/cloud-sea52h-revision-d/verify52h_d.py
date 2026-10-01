import bpy,bmesh,json,hashlib,struct,math
from mathutils import Euler
from pathlib import Path
from collections import Counter
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_sea52h_d.blend'))
def geometry(ob):
 me=ob.data;me.calc_loop_triangles();verts=[v.co.copy() for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
 bm=bmesh.new();bm.from_mesh(me);todo=set(bm.verts);components=[]
 while todo:
  stack=[todo.pop()];count=0
  while stack:
   v=stack.pop();count+=1
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in todo:todo.remove(w);stack.append(w)
  components.append(count)
 tree=BVHTree.FromPolygons(verts,tris,all_triangles=True,epsilon=0)
 bad=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(tris[a])&set(tris[b]))]
 area=[(verts[t[1]]-verts[t[0]]).cross(verts[t[2]]-verts[t[0]]).length for t in tris]
 aspect=[max((verts[t[(k+1)%3]]-verts[t[k]]).length_squared for k in range(3))/max(a,1e-12) for t,a in zip(tris,area)]
 low=[min(v[k] for v in verts) for k in range(3)];high=[max(v[k] for v in verts) for k in range(3)]
 r={'name':ob.name,'vertices':len(verts),'triangles':len(tris),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'components':components,'signed_volume_m3':bm.calc_volume(signed=True),'nonadjacent_triangle_intersections':len(bad),'intersection_pairs':bad[:50],'zero_area_triangles':sum(a<1e-7 for a in area),'triangle_aspect_over20':sum(a>20 for a in aspect),'triangle_aspect_max':max(aspect),'bounds_blender_xyz':[low,high],'dimensions_m':[b-a for a,b in zip(low,high)]};bm.free()
 return r,verts,tris
rows=[];passed=True
for name,filename in [('CloudSea52hD_v0_main_crown','cloud_sea_52h_d_main_v0.glb')]:
 ob=bpy.data.objects[name];r,verts,tris=geometry(ob)
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(P/filename));imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH'];assert len(imported)==1
 im=imported[0];im.data.calc_loop_triangles();kd=KDTree(len(verts))
 for i,v in enumerate(verts):kd.insert(v,i)
 kd.balance();mapping=[];distances=[]
 for v in im.data.vertices:
  point,index,distance=kd.find(im.matrix_world@v.co);mapping.append(index);distances.append(distance)
 def canonical(t):return min(tuple(t),tuple(t[1:]+t[:1]),tuple(t[2:]+t[:2]))
 exact=Counter(canonical(list(t)) for t in tris)==Counter(canonical([mapping[i] for i in t.vertices]) for t in im.data.loop_triangles)
 data=(P/filename).read_bytes();size,kind=struct.unpack_from('<II',data,12);glb=json.loads(data[20:20+size]);assert len(glb['meshes'])==1
 pr=glb['meshes'][0]['primitives'][0];acc=glb['accessors'][pr['attributes']['POSITION']];lo,hi=r['bounds_blender_xyz'];expected=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]]
 axis_error=max(abs(a-b) for A,B in zip(expected,[acc['min'],acc['max']]) for a,b in zip(A,B))
 r['native_GLBlender_readback']={'max_vertex_error_m':max(distances),'all_oriented_triangle_correspondence_exact':exact,'triangles':len(im.data.loop_triangles),'axis_bounds_error_m':axis_error,'attributes':list(pr['attributes'])}
 r['passed']=not(r['boundary_edges'] or r['nonmanifold_edges'] or r['nonadjacent_triangle_intersections'] or r['zero_area_triangles']) and len(r['components'])==1 and r['signed_volume_m3']>0 and exact and max(distances)<.001 and axis_error<.001
 passed=passed and r['passed'];rows.append(r)
controls=[]
ob=bpy.data.objects['CONTROL52hD_continuous_density_skin'];r,verts,tris=geometry(ob);controls.append(r)
passed=passed and not(r['boundary_edges'] or r['nonmanifold_edges'] or r['nonadjacent_triangle_intersections'] or r['zero_area_triangles']) and len(r['components'])==1 and r['signed_volume_m3']>0
recipe=json.loads((P/'construction52h-d.json').read_text());density=bpy.data.objects['CONTROL52hD_density'];element_rows=[]
for i,row in enumerate(recipe['native_density_elements']):
 e=density.data.elements[i]
 expected_rotation=Euler([math.radians(x) for x in row['rotation_xyz_degrees']],'XYZ').to_quaternion()
 exact=e.type=='ELLIPSOID' and not e.use_negative and e.radius==row['radius'] and abs(e.stiffness-row['stiffness'])<.000001 and all(abs(e.co[k]-row['center_blender_m'][k])<.0001 for k in range(3)) and all(abs(e.rotation[k]-expected_rotation[k])<.000001 for k in range(4)) and all(abs(v-row['size_xyz'][i])<.000001 for i,v in enumerate([e.size_x,e.size_y,e.size_z]))
 element_rows.append({'role':row['role'],'native_element_index':i,'native_properties_readback_exact':exact})
 passed=passed and exact
passed=passed and len(density.data.elements)==9 and density.data.threshold==recipe['density_threshold'] and density.data.resolution==9 and all(abs(density.scale[k]-recipe['uniform_normalization'])<.000001 for k in range(3)) and all(abs(density.location[k]-(recipe['normalized_center'][k]-recipe['raw_center'][k]*recipe['uniform_normalization']))<.0001 for k in range(3))
controls.append({'native_density_object':density.name,'element_count':len(density.data.elements),'elements':element_rows})
out={'geometry_and_native_readback_passed':passed,'variants':rows,'authored_controls':controls,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'cloud_sea52h_d.blend',P/'cloud_sea_52h_d_main_v0.glb']},'visual_acceptance':False,'world_modified':False,'rendered':False}
(P/'geometry52h-d.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert passed

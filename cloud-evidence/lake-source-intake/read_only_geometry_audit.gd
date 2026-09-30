extends SceneTree
var report = {"meshes":[],"scatter":[],"routes":[],"terrain_samples":[],"other_meshes":[]}
var tris = []
func v(a:Vector3): return [a.x,a.y,a.z]
func walk(n:Node,t:Transform3D,p:String):
 if n is Node3D: t=t*n.transform
 p += "/"+str(n.name)
 if n is MeshInstance3D and n.mesh != null and ("/Terrain/" in p or "/Mountains/" in p or "/Road" in p or p.ends_with("/Ocean")):
  var b=t*n.mesh.get_aabb()
  if b.end.x>=0 and b.position.x<=2304 and b.end.z>=-3500 and b.position.z<=-768:
   report.meshes.append({"node":p,"origin":v(t.origin),"aabb_min":v(b.position),"aabb_max":v(b.end),"mesh":n.mesh.resource_path,"surfaces":n.mesh.get_surface_count()})
   if "/Terrain/" in p:
    var f=n.mesh.get_faces()
    for i in range(0,f.size(),3): tris.append([t*f[i],t*f[i+1],t*f[i+2],p])
 if n is MeshInstance3D and n.mesh!=null and "/World/" in p and not "/Terrain/" in p and not "/Mountains/" in p and not "/Clouds/" in p and not p.ends_with("/Ocean"):
  var b=t*n.mesh.get_aabb()
  if b.end.x>=0 and b.position.x<=2304 and b.end.z>=-3072 and b.position.z<=-768:report.other_meshes.append({"node":p,"aabb_min":v(b.position),"aabb_max":v(b.end)})
 if n is MultiMeshInstance3D and n.multimesh != null and "/Vegetation/" in p:
  var count=0
  for i in n.multimesh.instance_count:
   var x=(t*n.multimesh.get_instance_transform(i)).origin
   if x.x>=0 and x.x<=2304 and x.z>=-3072 and x.z<=-768:count+=1
  if count>0:report.scatter.append({"node":p,"resource":n.multimesh.resource_path,"count_in_region":count,"kind":n.get_meta("asset_kind","")})
 if n is Path3D and n.curve!=null:
  var points=[]
  for i in n.curve.point_count:points.append(v(t*n.curve.get_point_position(i)))
  report.routes.append({"node":p,"points":points})
 for c in n.get_children():walk(c,t,p)
func _initialize():
 var g=load("res://scenes/candidate47/Game47.tscn").instantiate()
 walk(g,Transform3D.IDENTITY,"")
 for x in [700.,1000.,1150.,1300.,1500.,1800.]:
  for z in [-950.,-1100.,-1250.,-1450.,-1650.,-1850.,-2100.,-2400.,-2700.]:
   var best=null
   var node=""
   for tri in tris:
    var a=Geometry3D.segment_intersects_triangle(Vector3(x,1200,z),Vector3(x,-200,z),tri[0],tri[1],tri[2])
    if a!=null and (best==null or a.y>best.y):best=a;node=tri[3]
   report.terrain_samples.append({"x":x,"z":z,"surface":v(best) if best!=null else null,"node":node})
 var f=FileAccess.open("/workspace/scratch/a29d03198654/Aether/cloud-evidence/lake-geometry-data.json",FileAccess.WRITE)
 f.store_string(JSON.stringify(report,"  "));f.close();g.free();quit()

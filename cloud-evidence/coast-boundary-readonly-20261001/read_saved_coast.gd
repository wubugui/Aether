extends SceneTree
const SOURCE = "res://scenes/candidate53d-west/Game53dWest.tscn"
const OUTPUT = "/workspace/scratch/a29d03198654/Aether/cloud-evidence/coast-boundary-readonly-20261001/native-coast.json"
var report = {"source":SOURCE,"mode":"headless; instantiated outside SceneTree; no ready/process/world generation; surface arrays expanded by indices; no scene/resource writes", "terrain":[],"collision":[],"other_meshes":[]}
func vec(v:Vector3):return [v.x,v.y,v.z]
func intersects(b:AABB):return b.end.x>=-4300 and b.position.x<=-1500 and b.end.z>=-5000 and b.position.z<=-1800
func walk(n:Node,t:Transform3D,p:String):
 if n is Node3D:t=t*n.transform
 p+="/"+str(n.name)
 if n is MeshInstance3D and n.mesh != null:
  var b=t*n.mesh.get_aabb()
  if intersects(b) and "/Terrain/" in p:
   var faces=[]
   for s in range(n.mesh.get_surface_count()):
    var a=n.mesh.surface_get_arrays(s)
    var vertices:PackedVector3Array=a[Mesh.ARRAY_VERTEX]
    var indices:PackedInt32Array=a[Mesh.ARRAY_INDEX]
    if indices.is_empty():
     for v in vertices:faces.append(vec(t*v))
    else:
     for index in indices:faces.append(vec(t*vertices[index]))
   report.terrain.append({"node":p,"mesh":n.mesh.resource_path,"min":vec(b.position),"max":vec(b.end),"origin":vec(t.origin),"faces":faces})
  elif intersects(b) and not ("Cloud" in p or "cloud" in p or "Weather" in p or "Ocean" in p or "Airship" in p):
   report.other_meshes.append({"node":p,"min":vec(b.position),"max":vec(b.end),"origin":vec(t.origin),"mesh":n.mesh.resource_path})
 if n is CollisionShape3D and n.shape is ConcavePolygonShape3D and "/Terrain/" in p:
  var faces=n.shape.get_faces()
  if not faces.is_empty():
   var b=AABB(t*faces[0],Vector3.ZERO)
   for v in faces:b=b.expand(t*v)
   if intersects(b):
    var a=[]
    for v in faces:a.append(vec(t*v))
    report.collision.append({"node":p,"shape":n.shape.resource_path,"min":vec(b.position),"max":vec(b.end),"faces":a})
 for child in n.get_children():walk(child,t,p)
func _initialize():
 var g=load(SOURCE).instantiate()
 walk(g,Transform3D.IDENTITY,"")
 report.source_sha256=FileAccess.get_sha256(SOURCE)
 var f=FileAccess.open(OUTPUT,FileAccess.WRITE)
 f.store_string(JSON.stringify(report));f.close()
 print("COAST_READONLY terrains=",report.terrain.size()," collision=",report.collision.size()," other_meshes=",report.other_meshes.size()," source_sha=",report.source_sha256)
 g.free();quit()

extends SceneTree
const SOURCE="res://scenes/candidate53d-west/Game53dWest.tscn"
const SHA="6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18"
const OUT="/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/intake/"
func v(p:Vector3):return [p.x,p.y,p.z]
func walk(n:Node,t:Transform3D,p:String,data:Dictionary,file:FileAccess):
 if n is Node3D:t=t*n.transform
 p+="/"+str(n.name)
 if n is CollisionShape3D and not n.disabled and n.get_parent() is CollisionObject3D and (n.get_parent().collision_layer & 4)!=0:
  var row={"path":p,"class":n.shape.get_class(),"layer":n.get_parent().collision_layer,"mask":n.get_parent().collision_mask,"origin":v(t.origin)}
  if "Ocean" in p or "ocean" in p:row.role="water_plane_excluded_from_dry_land";data.water_shapes.append(row)
  elif n.shape is ConcavePolygonShape3D:
   var faces=n.shape.get_faces();var bytes=PackedByteArray();bytes.resize(faces.size()*12);var lo=Vector3(INF,INF,INF);var hi=Vector3(-INF,-INF,-INF)
   for i in faces.size():
    var w=t*faces[i];lo=lo.min(w);hi=hi.max(w);bytes.encode_float(i*12,w.x);bytes.encode_float(i*12+4,w.y);bytes.encode_float(i*12+8,w.z)
   row.offset_bytes=file.get_position();row.vertices=faces.size();row.bounds=[v(lo),v(hi)];row.role="actual_saved_ground_collision_faces";file.store_buffer(bytes);data.land_shapes.append(row)
  else:data.unhandled_land_shapes.append(row)
 if n is MeshInstance3D and p.ends_with("/massif_cirque_wall/Model/massif_cirque_wall"):
  var faces=[]
  for a in n.mesh.get_faces():faces.append(v(t*a))
  data.cirque_mesh={"node":p,"origin":v(t.origin),"faces":faces,"resource":n.mesh.resource_path}
 for c in n.get_children():walk(c,t,p,data,file)
func _initialize():call_deferred("run")
func run():
 if FileAccess.get_sha256(SOURCE)!=SHA:quit(2);return
 var g=load(SOURCE).instantiate()
 var d={"source":SOURCE,"source_sha256":SHA,"mode":"Saved-native geometry only. No live tree and no headless MultiMesh reads. Every mask4land collider is traversed, regardless of tile index; only Ocean is excluded from dry-land support.","land_shapes":[],"water_shapes":[],"unhandled_land_shapes":[],"cirque_mesh":{}}
 var f=FileAccess.open(OUT+"land-world-faces-f32.bin",FileAccess.WRITE);f.big_endian=false;walk(g,Transform3D.IDENTITY,"",d,f);f.close()
 d.binary_sha256=FileAccess.get_sha256(OUT+"land-world-faces-f32.bin")
 f=FileAccess.open(OUT+"land53-inventory.json",FileAccess.WRITE);f.store_string(JSON.stringify(d));f.close()
 print("CIRQUE54_LAND_INTAKE shapes=",d.land_shapes.size()," water=",d.water_shapes," unhandled=",d.unhandled_land_shapes," cirque_triangles=",d.cirque_mesh.faces.size()/3)
 g.free()
 for i in range(8):await process_frame
 quit(0 if d.unhandled_land_shapes.is_empty() else 3)

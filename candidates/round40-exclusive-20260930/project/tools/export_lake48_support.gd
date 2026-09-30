extends SceneTree
func v(p:Vector3):return [p.x,p.y,p.z]
func tf(t:Transform3D):return [t.basis.x.x,t.basis.x.y,t.basis.x.z,t.basis.y.x,t.basis.y.y,t.basis.y.z,t.basis.z.x,t.basis.z.y,t.basis.z.z,t.origin.x,t.origin.y,t.origin.z]
func walk(n:Node,t:Transform3D,p:String,out:Dictionary):
 if n is Node3D:t=t*n.transform
 p+="/"+str(n.name)
 if n is MeshInstance3D and ("/Terrain/" in p or "/Mountains/" in p):
  if "/Mountains/" in p:
   var a=[]
   for x in n.mesh.get_faces():a.append(v(t*x))
   out.meshes[str(n.name)]={"node":p,"origin":v(t.origin),"faces":a}
 if false and n is MultiMeshInstance3D and "/Vegetation/" in p and (p.ends_with("_1_-2") or p.ends_with("_1_-3")):
  var a=[]
  for i in n.multimesh.instance_count:a.append({"index":i,"position":v((t*n.multimesh.get_instance_transform(i)).origin),"transform":tf(n.multimesh.get_instance_transform(i))})
  out.scatter.append({"node":p,"instances":a})
 for c in n.get_children():walk(c,t,p,out)
func _initialize():call_deferred("run")
func run():

 var g=load("res://scenes/candidate47/Game47.tscn").instantiate()
 var out={"meshes":{},"scatter":[]}
 walk(g,Transform3D.IDENTITY,"",out)
 var f=FileAccess.open("/workspace/scratch/a29d03198654/Aether/source-assets/lake48/support47.json",FileAccess.WRITE)
 f.store_string(JSON.stringify(out));f.close();g.free()
 for i in range(8):await process_frame
 quit()

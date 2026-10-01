extends SceneTree
const OUT="/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53/"
const TILES=["Ground_0_-2","Ground_0_-3","Ground_1_-2","Ground_1_-3","Ground_2_-2","Ground_2_-3"]
func v(p:Vector3):return [p.x,p.y,p.z]
func tf(t:Transform3D):return [t.basis.x.x,t.basis.x.y,t.basis.x.z,t.basis.y.x,t.basis.y.y,t.basis.y.z,t.basis.z.x,t.basis.z.y,t.basis.z.z,t.origin.x,t.origin.y,t.origin.z]
func walk(n:Node,t:Transform3D,p:String,out:Dictionary):
 if n is Node3D:t=t*n.transform
 p+="/"+str(n.name)
 if n is MeshInstance3D and n.mesh:
  if "/Mountains/" in p or ("/Terrain/" in p and n.name in TILES):
   var a=[]
   for x in n.mesh.get_faces():a.append(v(t*x))
   out.meshes[str(n.name)]={"node":p,"origin":v(t.origin),"transform":tf(t),"faces":a,"mesh_resource":n.mesh.resource_path,"material_override":n.material_override.resource_path if n.material_override else ""}
  elif "/Settlements/" in p:
   var pts=[]
   for x in n.mesh.get_faces():pts.append(t*x)
   if pts.size():
    var lo:Vector3=pts[0]
    var hi:Vector3=pts[0]
    for x in pts:
     lo=lo.min(x);hi=hi.max(x)
    if hi.x>150 and lo.x<2200 and hi.z>-2900 and lo.z<-1400:
     out.buildings.append({"node":p,"origin":v(t.origin),"min":v(lo),"max":v(hi)})
 if n is MultiMeshInstance3D and "/Vegetation/" in p:
  for tile in TILES:
   if p.ends_with(tile.replace("Ground","")):
    var a=[]
    if DisplayServer.get_name()!="headless":
     for i in n.multimesh.instance_count:a.append({"index":i,"position":v((t*n.multimesh.get_instance_transform(i)).origin),"transform":tf(n.multimesh.get_instance_transform(i))})
    out.scatter.append({"node":p,"count":n.multimesh.instance_count,"instances":a,"global_transform":tf(t)})
 for c in n.get_children():walk(c,t,p,out)
func _initialize():call_deferred("run")
func run():
 var g=load("res://scenes/candidate51b/Game51b.tscn").instantiate()
 if DisplayServer.get_name()!="headless":
  for i in range(3):await process_frame
  await RenderingServer.frame_post_draw
 var out={"scene":"res://scenes/candidate51b/Game51b.tscn","renderer":DisplayServer.get_name(),"meshes":{},"scatter":[],"buildings":[]}
 walk(g,Transform3D.IDENTITY,"",out)
 var dest=OUT+("base51b-headless.json" if DisplayServer.get_name()=="headless" else "base51b.json")
 var f=FileAccess.open(dest,FileAccess.WRITE)
 f.store_string(JSON.stringify(out));f.close();g.free()
 print("RIM53_EXPORT ",dest," meshes=",out.meshes.size()," scatter_groups=",out.scatter.size()," buildings=",out.buildings.size())
 for i in range(8):await process_frame
 quit()

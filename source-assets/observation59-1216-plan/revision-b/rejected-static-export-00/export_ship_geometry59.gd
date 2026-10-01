extends SceneTree
const OUT:="/workspace/scratch/a29d03198654/Aether/source-assets/observation59-1216-plan/revision-b/ship-static59.json"
func _initialize():call_deferred("run")
func run():
 var packed:PackedScene=load("res://scenes/candidate52f/Game52f.tscn")
 var state:=packed.get_state()
 var matrices:={"Airship":Transform3D.IDENTITY}
 var rows:=[]
 var allpoints:=[]
 for i in range(state.get_node_count()):
  var path:=str(state.get_node_path(i))
  if not path.begins_with("Airship/"):continue
  var parent:=path.get_base_dir()
  if not matrices.has(parent):push_error("Missing native parent "+parent);quit(2);return
  var local:=Transform3D.IDENTITY
  var mesh:Mesh
  var visible:=true
  for j in range(state.get_node_property_count(i)):
   var name:=str(state.get_node_property_name(i,j));var value=state.get_node_property_value(i,j)
   if name=="transform":local=value
   if name=="mesh":mesh=value
   if name=="visible":visible=value
  var pose:Transform3D=matrices[parent]*local;matrices[path]=pose
  if mesh==null:continue
  var pts:=[]
  var bounds:=AABB();var first:=true
  for surface in range(mesh.get_surface_count()):
   var arrays:=mesh.surface_get_arrays(surface)
   for vertex in arrays[Mesh.ARRAY_VERTEX]:
    var v:Vector3=pose*vertex;pts.append([v.x,v.y,v.z]);allpoints.append([v.x,v.y,v.z])
    if first:bounds=AABB(v,Vector3.ZERO);first=false
    else:bounds=bounds.expand(v)
  rows.append({"path":path,"visible_stored":visible,"vertices":pts,"aabb":str(bounds),"mesh_resource":mesh.resource_path})
 var f:=FileAccess.open(OUT,FileAccess.WRITE);f.store_string(JSON.stringify({"scene_sha256":FileAccess.get_sha256("res://scenes/candidate52f/Game52f.tscn"),"instantiated":false,"rendered":false,"rows":rows,"mesh_count":rows.size(),"all_vertex_count":allpoints.size(),"limits":"Stored SceneState geometry only. Actual visible subset/propeller rotation and original runtime matrices must be rechecked against the real world before use. No transforms or resources modified."}));f.close();print("STATIC59 ",rows.size()," meshes ",allpoints.size()," vertices");quit()

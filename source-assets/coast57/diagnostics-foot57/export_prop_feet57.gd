extends SceneTree
const SOURCE="res://scenes/candidate53d-west/Game53dWest.tscn"
const OUT="/workspace/scratch/a29d03198654/Aether/source-assets/coast57/diagnostics-foot57/prop-foot-geometry.json"
const TARGETS=["World/Vegetation/rock_-5_-5","World/Vegetation/oak_-5_-5_CoastalPines36b","World/Vegetation/poplar_-5_-5_CoastalPines36b"]
func vec(v:Vector3)->Array:return [v.x,v.y,v.z]
func _initialize():
 if FileAccess.get_sha256(SOURCE)!="6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18":quit(2);return
 var packed:PackedScene=load(SOURCE)
 var state=packed.get_state()
 var out={"source":SOURCE,"source_sha256":FileAccess.get_sha256(SOURCE),"mode":"SceneState target MultiMesh.mesh geometry only; no world instantiation, no buffer getter, no resource save", "groups":[]}
 for i in state.get_node_count():
  var path=str(state.get_node_path(i)).trim_prefix("./")
  if not TARGETS.has(path):continue
  var mm:MultiMesh
  for j in state.get_node_property_count(i):
   if state.get_node_property_name(i,j)=="multimesh":mm=state.get_node_property_value(i,j)
  if mm==null or mm.mesh==null:printerr("Missing actual mesh ",path);quit(3);return
  var mesh:Mesh=mm.mesh
  var row={"node":path,"multimesh":mm.resource_path,"mesh":mesh.resource_path,"bounds":{"position":vec(mesh.get_aabb().position),"size":vec(mesh.get_aabb().size)},"surfaces":[]}
  for surface in mesh.get_surface_count():
   var a=mesh.surface_get_arrays(surface)
   var vertices=[];var indices=[]
   for v in a[Mesh.ARRAY_VERTEX]:vertices.append(vec(v))
   if a[Mesh.ARRAY_INDEX]!=null:
    for ix in a[Mesh.ARRAY_INDEX]:indices.append(ix)
   var mat=mesh.surface_get_material(surface)
   row.surfaces.append({"surface":surface,"vertices":vertices,"indices":indices,"primitive":mesh.surface_get_primitive_type(surface),"format":mesh.surface_get_format(surface),"material_name":mat.resource_name if mat else "","material_path":mat.resource_path if mat else ""})
  out.groups.append(row)
 if out.groups.size()!=3:printerr("Expected three groups");quit(4);return
 var f=FileAccess.open(OUT,FileAccess.WRITE);f.store_string(JSON.stringify(out));f.close()
 print("PROP57_ACTUAL_MESH_GEOMETRY_EXPORTED groups=",out.groups.size(),"; never instantiated world or read headless MultiMesh buffer")
 quit()

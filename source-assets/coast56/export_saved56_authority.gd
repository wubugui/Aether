extends SceneTree
const SOURCE="res://scenes/candidate53d-west/Game53dWest.tscn"
const OUT="/workspace/scratch/a29d03198654/Aether/source-assets/coast56/native-authority/"
func v3(v):return [v.x,v.y,v.z]
func serialize_array(a):
 var out=[]
 if a==null:return null
 for v in a:
  if v is Vector3:out.append([v.x,v.y,v.z])
  elif v is Vector2:out.append([v.x,v.y])
  elif v is Color:out.append([v.r,v.g,v.b,v.a])
  else:out.append(v)
 return out
func _initialize():
 var packed:PackedScene=load(SOURCE)
 var state=packed.get_state()
 var mesh:ArrayMesh
 var shape:ConcavePolygonShape3D
 for i in state.get_node_count():
  var path=str(state.get_node_path(i))
  if "Ground_-4_-4" in path:print("TARGET_PATH ",path," name=",state.get_node_name(i))
  if path.ends_with("World/Terrain/Ground_-4_-4/Model/Ground_-4_-4") or path.ends_with("World/Terrain/Ground_-4_-4/Collision/Shape"):
   for j in state.get_node_property_count(i):
    var key=state.get_node_property_name(i,j)
    if key=="mesh":mesh=state.get_node_property_value(i,j)
    if key=="shape":shape=state.get_node_property_value(i,j)
 if mesh==null or shape==null:
  printerr("Target resource missing; mesh=",mesh," shape=",shape);quit(2);return
 var out={"source":SOURCE,"source_sha256":FileAccess.get_sha256(SOURCE),"mesh":mesh.resource_path,"shape":shape.resource_path,"origin":[-3072,0,-3072],"surfaces":[],"collider_faces":serialize_array(shape.get_faces())}
 for surface in mesh.get_surface_count():
  var arrays=mesh.surface_get_arrays(surface)
  var record={"format":mesh.surface_get_format(surface),"primitive":mesh.surface_get_primitive_type(surface),"arrays":[],"array_variant_types":[]}
  for a in arrays:
   record.arrays.append(serialize_array(a));record.array_variant_types.append(typeof(a))
  out.surfaces.append(record)
  var f=FileAccess.open(OUT+"surface_"+str(surface)+"_arrays.bin",FileAccess.WRITE);f.store_buffer(var_to_bytes(arrays));f.close()
 var f=FileAccess.open(OUT+"original_surfaces.bin",FileAccess.WRITE);f.store_buffer(var_to_bytes(mesh.get("_surfaces")));f.close()
 f=FileAccess.open(OUT+"collider_faces.bin",FileAccess.WRITE);f.store_buffer(var_to_bytes(shape.get_faces()));f.close()
 f=FileAccess.open(OUT+"authority.json",FileAccess.WRITE);f.store_string(JSON.stringify(out));f.close()
 print("COAST56_AUTHORITY_OK surfaces=",out.surfaces.size(),"vertices=",out.surfaces[0].arrays[0].size(),"indices=",out.surfaces[0].arrays[12].size(),"scene was never instantiated")
 quit()

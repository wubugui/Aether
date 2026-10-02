extends RefCounted
## Read-only visual-geometry query world. Never joins the player's World3D.
## Static surfaces use their actual indexed arrays, not Mesh.get_faces().
## Animated source meshes use explicitly conservative complete envelopes.
var space := RID()
var bodies: Array[RID] = []
var shapes: Array[Shape3D] = []
var labels := {}
var watches := []
var rows := []
var failures := []
var mesh_cache := {}
var owner_game
var domain := AABB()
var triangle_count := 0

func v(p: Vector3) -> Array:
 return [p.x,p.y,p.z]

func world_bounds(bounds: AABB, pose: Transform3D) -> AABB:
 var result := AABB(pose * bounds.get_endpoint(0),Vector3.ZERO)
 for i in range(1,8): result = result.expand(pose * bounds.get_endpoint(i))
 return result

func fail(message: String, details: Variant = null) -> bool:
 failures.append({"reason":message,"details":details})
 return false

func add_shape(shape: Shape3D, pose: Transform3D, label: String, method: String) -> void:
 shapes.append(shape)
 var body := PhysicsServer3D.body_create()
 PhysicsServer3D.body_set_mode(body,PhysicsServer3D.BODY_MODE_STATIC)
 PhysicsServer3D.body_set_space(body,space)
 PhysicsServer3D.body_set_collision_layer(body,1)
 PhysicsServer3D.body_set_collision_mask(body,0)
 PhysicsServer3D.body_add_shape(body,shape.get_rid())
 PhysicsServer3D.body_set_state(body,PhysicsServer3D.BODY_STATE_TRANSFORM,pose)
 bodies.append(body)
 labels[body.get_id()]={"source":label,"method":method}

func add_box(bounds: AABB, label: String, method: String) -> void:
 var box := BoxShape3D.new()
 box.size = bounds.size.max(Vector3.ONE*.001)
 add_shape(box,Transform3D(Basis.IDENTITY,bounds.get_center()),label,method)

func material_expansion(material: Material) -> float:
 if material == null: return 0.0
 if material.next_pass != null:
  fail("Unclassified material next_pass",material.resource_path)
  return -1.0
 if material is BaseMaterial3D:
  if material.billboard_mode != BaseMaterial3D.BILLBOARD_DISABLED:
   fail("Unclassified billboard material",material.resource_path)
   return -1.0
  return absf(material.grow_amount) if material.grow_enabled else 0.0
 if not material is ShaderMaterial or material.shader == null:
  fail("Unclassified material type",material.get_class())
  return -1.0
 var code: String = material.shader.code
 # Match assignments only. Reading VERTEX for world position is not movement.
 var pattern := RegEx.new()
 pattern.compile("\\bVERTEX(?:\\.[xyzwrgba]{1,4})?\\s*(?:[+*/-])?=")
 var remainder := code
 var expansion := 0.0
 var cloud_line := "VERTEX.x+=sin(world_time*.018)*9.;"
 var flag_line := "VERTEX.z+=sin(world_time*2.6+VERTEX.x*2.1)*.10*clamp((VERTEX.x-.95)/1.8,0.,1.);"
 if remainder.contains(cloud_line):
  remainder = remainder.replace(cloud_line,"")
  expansion = maxf(expansion,9.0)
 if remainder.contains(flag_line):
  remainder = remainder.replace(flag_line,"")
  expansion = maxf(expansion,.1)
 if pattern.search(remainder) != null:
  fail("Unclassified vertex assignment; no geometry coverage claim",material.shader.resource_path)
  return -1.0
 var matrix_pattern:=RegEx.new()
 matrix_pattern.compile("\\b(?:POSITION|MODEL_MATRIX|MODELVIEW_MATRIX|PROJECTION_MATRIX|VIEW_MATRIX)\\s*(?:[+*/-])?=")
 if matrix_pattern.search(remainder)!=null:
  fail("Unclassified shader position/matrix override",material.shader.resource_path)
  return -1.0
 return expansion

func indexed_shape(mesh: Mesh) -> Shape3D:
 var id := mesh.get_instance_id()
 if mesh_cache.has(id): return mesh_cache[id]
 if mesh is ArrayMesh and mesh.get_blend_shape_count() != 0:
  fail("Blend-shape mesh requires a separate deformation audit",mesh.resource_path)
  return null
 if mesh is ArrayMesh:
  if mesh.shadow_mesh!=null:
   fail("Candidate has alternate depth/shadow geometry requiring classification",mesh.resource_path)
   return null
  var native_surfaces: Array=mesh.get("_surfaces")
  for native_surface in native_surfaces:
   var lods: Variant=native_surface.get("lods",{})
   if lods!=null and not lods.is_empty():
    fail("Candidate has LOD indices requiring explicit all-LOD coverage",mesh.resource_path)
    return null
 var faces := PackedVector3Array()
 if not mesh is ArrayMesh and not mesh.get_class() in ["PlaneMesh","BoxMesh","CylinderMesh","SphereMesh","CapsuleMesh","TorusMesh","PrismMesh","QuadMesh"]:
  fail("Unclassified native mesh primitive",mesh.get_class())
  return null
 for surface in range(mesh.get_surface_count()):
  if mesh is ArrayMesh and mesh.surface_get_primitive_type(surface) != Mesh.PRIMITIVE_TRIANGLES:
   fail("Nontriangle candidate surface",[mesh.resource_path,surface])
   return null
  var arrays: Array = mesh.surface_get_arrays(surface)
  var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
  var indices := PackedInt32Array()
  if arrays[Mesh.ARRAY_INDEX]!=null: indices=arrays[Mesh.ARRAY_INDEX]
  if indices.is_empty():
   if vertices.size()%3 != 0:
    fail("Unindexed surface is not triangle aligned",mesh.resource_path)
    return null
   faces.append_array(vertices)
  else:
   if indices.size()%3 != 0:
    fail("Indexed surface is not triangle aligned",mesh.resource_path)
    return null
   for index in indices:
    if index<0 or index>=vertices.size():
     fail("Out-of-range actual native index",[mesh.resource_path,index])
     return null
    faces.append(vertices[index])
 if faces.is_empty():
  fail("Candidate contains no native drawn triangles",mesh.resource_path)
  return null
 var shape := ConcavePolygonShape3D.new()
 shape.backface_collision = true
 shape.set_faces(faces)
 triangle_count += faces.size()/3
 mesh_cache[id] = shape
 return shape

func add_mesh(mesh: Mesh, pose: Transform3D, label: String, expansion: float) -> bool:
 # Frobenius norm bounds arbitrary scale/shear amplification of deformation.
 var amplification := sqrt(pose.basis.x.length_squared()+pose.basis.y.length_squared()+pose.basis.z.length_squared())
 var bounds := world_bounds(mesh.get_aabb(),pose).grow(expansion*amplification+.002)
 if not bounds.intersects(domain): return true
 var row := {"source":label,"mesh":mesh.resource_path,"bounds_position":v(bounds.position),"bounds_size":v(bounds.size),"shader_local_expansion_m":expansion}
 if expansion>0:
  row.method="conservative complete mesh AABB plus full shader displacement"
  add_box(bounds,label,row.method)
 else:
  var shape := indexed_shape(mesh)
  if shape == null: return false
  row.method="actual native indexed triangle surfaces, double-sided query"
  add_shape(shape,pose,label,row.method)
 rows.append(row)
 return true

func ship_envelope() -> bool:
 var first := true
 var bounds := AABB()
 var count := 0
 var propeller_count := 0
 for mesh_node in owner_game.airship.find_children("*","MeshInstance3D",true,false):
  if mesh_node.mesh == null or not mesh_node.is_visible_in_tree(): continue
  for surface in range(mesh_node.mesh.get_surface_count()):
   var expansion:=material_expansion(mesh_node.get_active_material(surface))
   if expansion<0 or expansion>.5: return fail("Ship deformation exceeds explicit half-meter envelope",str(mesh_node.get_path()))
  count += 1
  var local: Transform3D = owner_game.airship.global_transform.affine_inverse()*mesh_node.global_transform
  # Half-meter pad contains flag's native .1m displacement as well.
  var part: AABB = world_bounds(mesh_node.mesh.get_aabb().grow(.5),local)
  if owner_game.propeller.is_ancestor_of(mesh_node):
   propeller_count += 1
   var to_prop: Transform3D = owner_game.propeller.global_transform.affine_inverse()*mesh_node.global_transform
   var prop_bounds: AABB = world_bounds(mesh_node.mesh.get_aabb().grow(.5),to_prop)
   var radial := 0.0
   for i in range(8):
    var corner: Vector3 = prop_bounds.get_endpoint(i)
    radial=maxf(radial,Vector2(corner.y,corner.z).length())
   var revolution := AABB(Vector3(prop_bounds.position.x,-radial,-radial),Vector3(prop_bounds.size.x,radial*2,radial*2))
   var to_ship: Transform3D = owner_game.airship.global_transform.affine_inverse()*owner_game.propeller.global_transform
   part=world_bounds(revolution,to_ship)
  bounds=part if first else bounds.merge(part)
  first=false
 if first or propeller_count==0: return fail("Missing complete visible ship/propeller envelope")
 # This item is anchored, no lift/bank. Grow full .08m native bob range.
 bounds=bounds.grow(.08)
 var world: AABB=world_bounds(bounds,owner_game.airship.global_transform)
 add_box(world,"Airship/all visible meshes + complete propeller revolution + flag + bob","conservative animated ship envelope; nearest hit is an envelope, not an exact pixel")
 rows.append({"source":"Airship","method":"conservative animated ship envelope","visible_mesh_count":count,"full_revolution_mesh_count":propeller_count,"bounds_position":v(world.position),"bounds_size":v(world.size)})
 return true

func prepare(game, query_domain: AABB) -> bool:
 owner_game=game
 domain=query_domain
 space=PhysicsServer3D.space_create()
 PhysicsServer3D.space_set_active(space,true)
 if not ship_envelope(): return false
 for node in game.find_children("*","GeometryInstance3D",true,false):
  if game.airship.is_ancestor_of(node): continue
  var visible: bool=node.is_visible_in_tree() and (node.layers & game.camera.cull_mask)!=0
  watches.append({"node":node,"transform":node.global_transform,"visible":visible,"layers":node.layers,"query_candidate":false,"expansion":0.0})
  if not visible: continue
  if not node is MeshInstance3D and not node is MultiMeshInstance3D:
   # Fail closed: unknown particle/procedural bounds need their own audit.
   return fail("Unclassified visible geometry type",[str(node.get_path()),node.get_class()])
  var mesh: Mesh=node.mesh if node is MeshInstance3D else (node.multimesh.mesh if node.multimesh!=null else null)
  if mesh==null: continue
  if node is MeshInstance3D and (node.get_node_or_null(node.skeleton) is Skeleton3D or node.get_blend_shape_count()>0):
   return fail("Unclassified skeleton/blend-shape candidate",str(node.get_path()))
  var expansion:=material_expansion(node.material_override)
  if expansion<0: return false
  for surface in range(mesh.get_surface_count()):
   var material: Material=mesh.surface_get_material(surface)
   if node is MeshInstance3D: material=node.get_active_material(surface)
   var extra:=material_expansion(material)
   if extra<0: return false
   expansion=maxf(expansion,extra)
  watches[-1].expansion=expansion
  var node_bounds: AABB=world_bounds(node.get_aabb(),node.global_transform).grow(expansion*node.global_basis.get_scale().length()+.002)
  watches[-1].query_candidate=node_bounds.intersects(domain)
  if node is MeshInstance3D:
   if not add_mesh(mesh,node.global_transform,str(node.get_path()),expansion): return false
  else:
   var count: int=node.multimesh.instance_count
   if node.multimesh.visible_instance_count>=0: count=mini(count,node.multimesh.visible_instance_count)
   watches[-1]["buffer_sha256"]=var_to_bytes(node.multimesh.buffer).hex_encode().sha256_text()
   watches[-1]["instance_count"]=node.multimesh.instance_count
   watches[-1]["visible_instance_count"]=node.multimesh.visible_instance_count
   for index in range(count):
    var pose: Transform3D=node.global_transform*node.multimesh.get_instance_transform(index)
    if not add_mesh(mesh,pose,str(node.get_path())+"#"+str(index),expansion): return false
 return true

func unchanged(check_buffers: bool) -> bool:
 for item in watches:
  var node=item.node
  if not is_instance_valid(node): return fail("Inventoried geometry was removed")
  var visible: bool=node.is_visible_in_tree() and (node.layers & owner_game.camera.cull_mask)!=0
  if node.global_transform!=item.transform or visible!=item.visible or node.layers!=item.layers:
   var current_bounds: AABB=world_bounds(node.get_aabb(),node.global_transform).grow(float(item.expansion)*node.global_basis.get_scale().length()+.002)
   if item.query_candidate or current_bounds.intersects(domain):
    return fail("Candidate geometry visibility/transform changed after stationary inventory",str(node.get_path()))
  if check_buffers and node is MultiMeshInstance3D and item.has("buffer_sha256"):
   if node.multimesh.instance_count!=item.instance_count or node.multimesh.visible_instance_count!=item.visible_instance_count or var_to_bytes(node.multimesh.buffer).hex_encode().sha256_text()!=item.buffer_sha256:
    return fail("Actual MultiMesh buffer changed after inventory",str(node.get_path()))
 return true

func accept_distant_new_node(node: GeometryInstance3D) -> bool:
 # Streaming may add distant native nodes. Do not call them local blockers,
 # but classify their deformation and watch for later entry into the domain.
 var visible: bool=node.is_visible_in_tree() and (node.layers & owner_game.camera.cull_mask)!=0
 if not node is MeshInstance3D and not node is MultiMeshInstance3D:
  return fail("Unclassified new geometry",[str(node.get_path()),node.get_class()])
 var mesh: Mesh=node.mesh if node is MeshInstance3D else (node.multimesh.mesh if node.multimesh!=null else null)
 if mesh==null: return fail("New geometry has no classifiable bounds",str(node.get_path()))
 var expansion:=material_expansion(node.material_override)
 if expansion<0: return false
 for surface in range(mesh.get_surface_count()):
  var material: Material=node.get_active_material(surface) if node is MeshInstance3D else mesh.surface_get_material(surface)
  var extra:=material_expansion(material)
  if extra<0: return false
  expansion=maxf(expansion,extra)
 var bounds: AABB=world_bounds(node.get_aabb(),node.global_transform).grow(expansion*node.global_basis.get_scale().length()+.002)
 if visible and bounds.intersects(domain): return fail("New visible candidate after frozen local inventory",str(node.get_path()))
 var item: Dictionary={"node":node,"transform":node.global_transform,"visible":visible,"layers":node.layers,"query_candidate":bounds.intersects(domain),"expansion":expansion}
 if node is MultiMeshInstance3D:
  item.buffer_sha256=var_to_bytes(node.multimesh.buffer).hex_encode().sha256_text()
  item.instance_count=node.multimesh.instance_count
  item.visible_instance_count=node.multimesh.visible_instance_count
 watches.append(item)
 return true

func decode(hit: Dictionary) -> Dictionary:
 if hit.is_empty(): return {}
 var rid: RID=hit.get("rid",RID())
 var result: Dictionary=labels.get(rid.get_id(),{"source":"unknown audit body"}).duplicate()
 if hit.has("position"): result.position=v(hit.position)
 result.face_index=hit.get("face_index",-1)
 return result

func close() -> void:
 for body in bodies: PhysicsServer3D.free_rid(body)
 bodies.clear()
 if space.is_valid(): PhysicsServer3D.free_rid(space)
 space=RID()
 shapes.clear()
 mesh_cache.clear()

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
var mesh_audits := {}
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
 # A script failure in a float-returning classifier would default to 0.0.
 # A failed Dictionary classifier defaults to {}, which this wrapper rejects.
 var result: Dictionary=classify_material(material)
 if result.get("ok")!=true or not (result.get("expansion") is float or result.get("expansion") is int):
  fail("Material audit did not return explicit successful classification",material.resource_path if material!=null else "null")
  return -1.0
 var expansion: float=result.expansion
 if not is_finite(expansion) or expansion<0:
  fail("Material audit returned invalid expansion",material.resource_path if material!=null else "null")
  return -1.0
 return expansion

func classify_material(material: Material) -> Dictionary:
 if material == null: return {"ok":true,"expansion":0.0}
 if material.next_pass != null:
  fail("Unclassified material next_pass",material.resource_path)
  return {}
 if material is BaseMaterial3D:
  if material.billboard_mode != BaseMaterial3D.BILLBOARD_DISABLED:
   fail("Unclassified billboard material",material.resource_path)
   return {}
  return {"ok":true,"expansion":absf(material.grow_amount) if material.is_grow_enabled() else 0.0}
 if not material is ShaderMaterial or material.shader == null:
  fail("Unclassified material type",material.get_class())
  return {}
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
  return {}
 var matrix_pattern:=RegEx.new()
 matrix_pattern.compile("\\b(?:POSITION|MODEL_MATRIX|MODELVIEW_MATRIX|PROJECTION_MATRIX|VIEW_MATRIX)\\s*(?:[+*/-])?=")
 if matrix_pattern.search(remainder)!=null:
  fail("Unclassified shader position/matrix override",material.shader.resource_path)
  return {}
 return {"ok":true,"expansion":expansion}

# Godot 4.5.1 only: static 3D vertex/normal/tangent/color/UV/index layouts.
# Position-only compressed arrays hit an upstream continue before ARRAY_VERTEX
# assignment (rendering_server.cpp:1330-1336). Decode that narrowly, never guess.
func surface_positions(raw: Dictionary, label: String) -> PackedVector3Array:
 var empty := PackedVector3Array()
 var allowed := RenderingServer.ARRAY_FLAG_FORMAT_CURRENT_VERSION | Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES | Mesh.ARRAY_FORMAT_VERTEX | Mesh.ARRAY_FORMAT_NORMAL | Mesh.ARRAY_FORMAT_TANGENT | Mesh.ARRAY_FORMAT_COLOR | Mesh.ARRAY_FORMAT_TEX_UV | Mesh.ARRAY_FORMAT_TEX_UV2 | Mesh.ARRAY_FORMAT_INDEX
 var format: int=raw.get("format",0)
 if format & ~allowed or (format & (RenderingServer.ARRAY_FLAG_FORMAT_VERSION_MASK << RenderingServer.ARRAY_FLAG_FORMAT_VERSION_SHIFT)) != RenderingServer.ARRAY_FLAG_FORMAT_CURRENT_VERSION or not (format & Mesh.ARRAY_FORMAT_VERTEX):
  fail("Unknown static 3D surface format",[label,format]); return empty
 if raw.get("primitive",-1)!=Mesh.PRIMITIVE_TRIANGLES or raw.get("2d",false):
  fail("Nontriangle or 2D native surface",label); return empty
 for key in ["skin_data","blend_shapes","bone_aabbs"]:
  if raw.has(key) and not raw[key].is_empty():
   fail("Deformed native surface requires separate audit",[label,key]); return empty
 var count: int=raw.get("vertex_count",0)
 var data: Variant=raw.get("vertex_data")
 var bounds: Variant=raw.get("aabb")
 if count<=0 or not data is PackedByteArray or not bounds is AABB or not bounds.position.is_finite() or not bounds.size.is_finite() or bounds.size.x<0 or bounds.size.y<0 or bounds.size.z<0:
  fail("Malformed native vertex data or bounds",label); return empty
 var compressed: bool=(format & Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)!=0
 var normals: bool=(format & Mesh.ARRAY_FORMAT_NORMAL)!=0
 var tangents: bool=(format & Mesh.ARRAY_FORMAT_TANGENT)!=0
 if compressed and tangents and not normals:
  fail("Unsupported compressed tangent layout",label); return empty
 var stride: int=8 if compressed else 12
 var normal_stride: int=(4 if normals else 0)+(4 if tangents and not compressed else 0)
 if data.size()!=count*(stride+normal_stride):
  fail("Native vertex byte length mismatch",label); return empty
 var result := PackedVector3Array()
 result.resize(count)
 for i in range(count):
  var offset: int=i*stride
  if compressed:
   var unit:=Vector3(data.decode_u16(offset)/65535.0,data.decode_u16(offset+2)/65535.0,data.decode_u16(offset+4)/65535.0)
   result[i]=(unit*bounds.size)+bounds.position
  else:
   result[i]=Vector3(data.decode_float(offset),data.decode_float(offset+4),data.decode_float(offset+8))
  if not result[i].is_finite():
   fail("Nonfinite actual vertex",[label,i]); return empty
 return result

func decoded_indices(data: Variant, count: int, vertex_count: int, label: String) -> PackedInt32Array:
 var result:=PackedInt32Array()
 var width: int=2 if vertex_count<=65536 else 4
 if not data is PackedByteArray or count<=0 or count%3!=0 or data.size()!=count*width:
  fail("Malformed native triangle index bytes",label); return result
 result.resize(count)
 for i in range(count):
  var index: int=data.decode_u16(i*width) if width==2 else data.decode_u32(i*width)
  if index>=vertex_count:
   fail("Out-of-range actual native index",[label,index]); return PackedInt32Array()
  result[i]=index
 return result

func indexed_faces(vertices: PackedVector3Array, indices: PackedInt32Array) -> PackedVector3Array:
 var faces:=PackedVector3Array()
 faces.resize(indices.size())
 for i in range(indices.size()): faces[i]=vertices[indices[i]]
 return faces

func oriented_triangles(faces: PackedVector3Array) -> Dictionary:
 # Exact float32-coordinate cyclic normalization permits fused vertices and
 # triangle ordering, preserving winding/multiplicity. Signed zeros are the
 # same geometric coordinate; normalize their byte representation, no epsilon.
 var result: Dictionary={}
 var vertex_keys: Dictionary={}
 for point in faces:
  if not vertex_keys.has(point):
   var canonical:=Vector3(0.0 if point.x==0.0 else point.x,0.0 if point.y==0.0 else point.y,0.0 if point.z==0.0 else point.z)
   vertex_keys[point]=var_to_bytes(canonical).hex_encode()
 for i in range(0,faces.size(),3):
  var a: String=vertex_keys[faces[i]]
  var b: String=vertex_keys[faces[i+1]]
  var c: String=vertex_keys[faces[i+2]]
  var candidates: Array[String]=[a+b+c,b+c+a,c+a+b]
  candidates.sort()
  var key: String=candidates[0]
  result[key]=int(result.get(key,0))+1
 return result

func audit_surface(mesh: ArrayMesh, surface: int, raw: Dictionary) -> Dictionary:
 var label:=mesh.resource_path+"/surface"+str(surface)
 var vertices:=surface_positions(raw,label)
 if vertices.is_empty(): return {}
 var arrays: Array=mesh.surface_get_arrays(surface)
 if arrays.size()!=Mesh.ARRAY_MAX:
  fail("Missing native surface arrays",label); return {}
 if arrays[Mesh.ARRAY_VERTEX] is PackedVector3Array:
  if arrays[Mesh.ARRAY_VERTEX]!=vertices:
   fail("Raw/native API vertex mismatch",label); return {}
 elif arrays[Mesh.ARRAY_VERTEX]!=null or not (int(raw.format)&Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES) or (int(raw.format)&Mesh.ARRAY_FORMAT_NORMAL):
  fail("Unclassified missing native vertex array",label); return {}
 var index_count: int=raw.get("index_count",0)
 var indices:=PackedInt32Array()
 if int(raw.format)&Mesh.ARRAY_FORMAT_INDEX:
  indices=decoded_indices(raw.get("index_data"),index_count,vertices.size(),label)
  if indices.is_empty(): return {}
  if not arrays[Mesh.ARRAY_INDEX] is PackedInt32Array or arrays[Mesh.ARRAY_INDEX]!=indices:
   fail("Raw/native API index mismatch",label); return {}
 else:
  if index_count!=0 or raw.has("index_data") or vertices.size()%3!=0:
   fail("Malformed unindexed native triangles",label); return {}
  indices.resize(vertices.size())
  for i in range(vertices.size()): indices[i]=i
 var levels: Dictionary={0.0:indexed_faces(vertices,indices)}
 var lods: Variant=raw.get("lods",[])
 if not lods is Array or lods.size()%2!=0 or (not lods.is_empty() and index_count==0):
  fail("Malformed native LOD list",label); return {}
 var previous:=0.0
 for i in range(0,lods.size(),2):
  if not (lods[i] is float or lods[i] is int) or not is_finite(float(lods[i])) or float(lods[i])<=previous or not lods[i+1] is PackedByteArray:
   fail("Invalid or nonincreasing LOD threshold",[label,i]); return {}
  var threshold: float=lods[i]
  var width: int=2 if vertices.size()<=65536 else 4
  var lod_indices:=decoded_indices(lods[i+1],lods[i+1].size()/width,vertices.size(),label+"/LOD"+str(threshold))
  if lod_indices.is_empty(): return {}
  levels[threshold]=indexed_faces(vertices,lod_indices)
  previous=threshold
 return {"aabb":raw.aabb,"levels":levels,"vertices":vertices.size(),"format":int(raw.format),"api_vertex_missing":arrays[Mesh.ARRAY_VERTEX]==null}

func audit_array_mesh(mesh: ArrayMesh) -> Dictionary:
 if Engine.get_version_info().hex!=0x040501:
  fail("Native geometry decoder requires Godot4.5.1",Engine.get_version_info()); return {}
 if mesh.get_blend_shape_count()!=0:
  fail("Blend-shape mesh requires a separate deformation audit",mesh.resource_path); return {}
 var raw: Array=mesh.get("_surfaces")
 if raw.size()!=mesh.get_surface_count() or raw.is_empty():
  fail("Missing complete native surfaces",mesh.resource_path); return {}
 var shadow: ArrayMesh=mesh.shadow_mesh
 var shadow_raw: Array=[]
 if shadow!=null:
  if shadow.shadow_mesh!=null or shadow.get_blend_shape_count()!=0 or shadow.get_surface_count()!=raw.size() or shadow.get_aabb()!=mesh.get_aabb():
   fail("Unclassified shadow mesh chain, deformation, surface count or AABB",mesh.resource_path); return {}
  shadow_raw=shadow.get("_surfaces")
  if shadow_raw.size()!=raw.size():
   fail("Missing complete shadow surfaces",mesh.resource_path); return {}
 var faces:=PackedVector3Array()
 var summaries:=[]
 for surface in range(raw.size()):
  var source:=audit_surface(mesh,surface,raw[surface])
  if source.is_empty(): return {}
  var partner: Dictionary={}
  if shadow!=null:
   partner=audit_surface(shadow,surface,shadow_raw[surface])
   if partner.is_empty(): return {}
   if partner.aabb!=source.aabb or partner.levels.keys()!=source.levels.keys():
    fail("Shadow surface AABB or complete LOD thresholds differ",[mesh.resource_path,surface]); return {}
  var levels:=[]
  for threshold in source.levels:
   var drawn: PackedVector3Array=source.levels[threshold]
   if shadow!=null and oriented_triangles(drawn)!=oriented_triangles(partner.levels[threshold]):
    fail("Shadow oriented triangle multiset differs",[mesh.resource_path,surface,threshold]); return {}
   faces.append_array(drawn)
   levels.append({"threshold":threshold,"triangles":drawn.size()/3,"source_faces_hex_text_sha256":drawn.to_byte_array().hex_encode().sha256_text()})
  summaries.append({"surface":surface,"source_format":source.format,"source_vertices":source.vertices,"shadow_vertices":partner.get("vertices",0),"shadow_api_vertex_missing":partner.get("api_vertex_missing",false),"levels":levels})
 return {"faces":faces,"surfaces":summaries,"shadow_equivalent":shadow!=null}

func indexed_shape(mesh: Mesh) -> Shape3D:
 var id := mesh.get_instance_id()
 if mesh_cache.has(id): return mesh_cache[id]
 var faces:=PackedVector3Array()
 if mesh is ArrayMesh:
  var audit:=audit_array_mesh(mesh)
  if audit.is_empty(): return null
  faces=audit.faces
  mesh_audits[id]={"mesh":mesh.resource_path,"surfaces":audit.surfaces,"shadow_equivalent":audit.shadow_equivalent,"all_base_and_lod_triangles":faces.size()/3}
 else:
  if not mesh.get_class() in ["PlaneMesh","BoxMesh","CylinderMesh","SphereMesh","CapsuleMesh","TorusMesh","PrismMesh","QuadMesh"]:
   fail("Unclassified native mesh primitive",mesh.get_class()); return null
  for surface in range(mesh.get_surface_count()):
   var arrays: Array=mesh.surface_get_arrays(surface)
   if arrays.size()!=Mesh.ARRAY_MAX or not arrays[Mesh.ARRAY_VERTEX] is PackedVector3Array:
    fail("Missing primitive vertices",mesh.get_class()); return null
   var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
   var indices:=PackedInt32Array()
   if arrays[Mesh.ARRAY_INDEX]!=null: indices=arrays[Mesh.ARRAY_INDEX]
   if indices.is_empty():
    if vertices.size()%3!=0:
     fail("Unindexed surface is not triangle aligned",mesh.resource_path); return null
    faces.append_array(vertices)
   else:
    if indices.size()%3!=0:
     fail("Indexed surface is not triangle aligned",mesh.resource_path); return null
    for index in indices:
     if index<0 or index>=vertices.size():
      fail("Out-of-range actual native index",[mesh.resource_path,index]); return null
     faces.append(vertices[index])
 if faces.is_empty():
  fail("Candidate contains no native drawn triangles",mesh.resource_path); return null
 var shape:=ConcavePolygonShape3D.new()
 shape.backface_collision=true
 shape.set_faces(faces)
 triangle_count+=faces.size()/3
 mesh_cache[id]=shape
 return shape

func add_mesh(mesh: Mesh, pose: Transform3D, label: String, expansion: float) -> bool:
 # Frobenius norm bounds arbitrary scale/shear amplification of deformation.
 var amplification := sqrt(pose.basis.x.length_squared()+pose.basis.y.length_squared()+pose.basis.z.length_squared())
 # Before source-bound pruning, require alternate geometry to share its bound.
 if mesh is ArrayMesh and mesh.shadow_mesh!=null and (mesh.shadow_mesh.get_aabb()!=mesh.get_aabb() or mesh.shadow_mesh.shadow_mesh!=null):
  return fail("Unclassified alternate geometry outside source pruning bound",mesh.resource_path)
 var bounds := world_bounds(mesh.get_aabb(),pose).grow(expansion*amplification+.002)
 if not bounds.intersects(domain): return true
 var row := {"source":label,"mesh":mesh.resource_path,"bounds_position":v(bounds.position),"bounds_size":v(bounds.size),"shader_local_expansion_m":expansion}
 var shape := indexed_shape(mesh)
 if shape == null: return false
 if mesh_audits.has(mesh.get_instance_id()): row.geometry_audit=mesh_audits[mesh.get_instance_id()]
 if expansion>0:
  row.method="conservative complete mesh AABB plus full shader displacement"
  add_box(bounds,label,row.method)
 else:
  row.method="actual native base and all LOD triangles, exact equivalent shadow coverage, double-sided query"
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
  if indexed_shape(mesh_node.mesh)==null: return false
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

func queued_ancestors(node: Node) -> Array:
 var result:=[]
 var parent: Node=node
 while parent!=null:
  if parent.is_queued_for_deletion(): result.append({"path":str(parent.get_path()),"instance_id":parent.get_instance_id()})
  parent=parent.get_parent()
 return result

func watch_entry(node: GeometryInstance3D, visible: bool, expansion: float, bounds: AABB) -> Dictionary:
 return {"node":node,"path":str(node.get_path()),"instance_id":node.get_instance_id(),"transform":node.global_transform,"visible":visible,"layers":node.layers,"query_candidate":bounds.intersects(domain),"expansion":expansion,"bounds_position":v(bounds.position),"bounds_size":v(bounds.size),"queued_ancestors_at_inventory":queued_ancestors(node)}

func watch_evidence(item: Dictionary) -> Dictionary:
 var result:=item.duplicate()
 result.erase("node")
 result.erase("transform")
 return result

func prepare(game, query_domain: AABB) -> bool:
 owner_game=game
 domain=query_domain
 space=PhysicsServer3D.space_create()
 PhysicsServer3D.space_set_active(space,true)
 if not ship_envelope(): return false
 for node in game.find_children("*","GeometryInstance3D",true,false):
  if game.airship.is_ancestor_of(node): continue
  var visible: bool=node.is_visible_in_tree() and (node.layers & game.camera.cull_mask)!=0
  var initial_bounds: AABB=world_bounds(node.get_aabb(),node.global_transform).grow(.002)
  var watch:=watch_entry(node,visible,0.0,initial_bounds)
  if not watch.queued_ancestors_at_inventory.is_empty(): return fail("Queued geometry cannot enter frozen inventory",watch_evidence(watch))
  watches.append(watch)
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
  watches[-1].bounds_position=v(node_bounds.position)
  watches[-1].bounds_size=v(node_bounds.size)
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
  if not is_instance_valid(node): return fail("Inventoried geometry was removed",watch_evidence(item))
  if not node.is_inside_tree(): return fail("Inventoried geometry left the tree",watch_evidence(item))
  var queued:=queued_ancestors(node)
  if not queued.is_empty():
   var evidence:=watch_evidence(item)
   evidence.current_queued_ancestors=queued
   return fail("Inventoried geometry is now queued for deletion",evidence)
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
 var item:=watch_entry(node,visible,expansion,bounds)
 if not item.queued_ancestors_at_inventory.is_empty(): return fail("Queued new geometry cannot enter frozen inventory",watch_evidence(item))
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
 mesh_audits.clear()

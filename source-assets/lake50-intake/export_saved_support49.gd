extends SceneTree
## Read-only PackedScene stored-state export. Never instantiates/saves the scene,
## never reads/writes any MultiMesh buffer, and never enters runtime world scripts.
const SOURCE := "res://scenes/candidate49/Game49.tscn"
const EXPECTED_SHA := "52d13fcb7ea412d3a0fae2eedb1d0f9c369dbe06c0da320d786c26c97c475ec8"
const OUT := "/workspace/scratch/a29d03198654/Aether/source-assets/lake50-intake/"
const BOUNDS := Vector4(768,-2304,1536,-768)
func _initialize() -> void: call_deferred("run")
func fail(message: String) -> void:
	push_error(message);quit(1)
func tf(t: Transform3D) -> Array:
	return [t.basis.x.x,t.basis.x.y,t.basis.x.z,t.basis.y.x,t.basis.y.y,t.basis.y.z,t.basis.z.x,t.basis.z.y,t.basis.z.z,t.origin.x,t.origin.y,t.origin.z]
func bytes_hash(bytes: PackedByteArray) -> String:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256);context.update(bytes)
	return context.finish().hex_encode()
func prop(state: SceneState,i: int,name: String,default: Variant=null) -> Variant:
	for j in range(state.get_node_property_count(i)):
		if str(state.get_node_property_name(i,j))==name: return state.get_node_property_value(i,j)
	return default
func run() -> void:
	if FileAccess.get_sha256(SOURCE)!=EXPECTED_SHA: fail("Actual saved49 SHA mismatch");return
	if FileAccess.file_exists(OUT+"support49-world-f32.bin"): fail("Refuse overwrite prior diagnostic export");return
	var packed: PackedScene=ResourceLoader.load(SOURCE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	if packed==null: fail("Saved49 failed read");return
	var state := packed.get_state()
	var transforms := {}
	var inventory := []
	var exclusions := []
	var binary := FileAccess.open(OUT+"support49-world-f32.bin",FileAccess.WRITE)
	if binary==null: fail("Diagnostic binary output failed");return
	var triangles := 0
	for i in range(state.get_node_count()):
		var path := str(state.get_node_path(i)).trim_prefix("./")
		var parent := path.get_base_dir()
		if path==".": parent=""
		elif parent.is_empty(): parent="."
		var local: Transform3D=prop(state,i,"transform",Transform3D.IDENTITY)
		var world: Transform3D=transforms.get(parent,Transform3D.IDENTITY)*local
		transforms[path]=world
		var kind := str(state.get_node_type(i))
		if kind!="MeshInstance3D" and kind!="MultiMeshInstance3D": continue
		var reason := ""
		var category := ""
		if kind=="MultiMeshInstance3D": reason="Excluded all instanced vegetation/cloud/weather scatter; no MultiMesh buffers read"
		elif path.begins_with("World/Terrain/"): category="Terrain"
		elif path.begins_with("World/Mountains/"): category="Mountains"
		elif path.begins_with("World/Cliffs/"): category="Cliffs"
		elif path.begins_with("World/LakeIslands49/"):
			var role := str(prop(state,i,"metadata/authoring_role",""))
			if role in ["rockroot","shoulder","wetshore","grasscap"]: category="LakeIslands49/"+role
			else: reason="Excluded island "+role+": tree trunks/branches/crowns and decorative grass tufts are not continuous lakebed support"
		elif path=="World/Ocean": reason="Excluded Ocean: target water plane cannot supply its own bottom depth"
		elif path.begins_with("World/Vegetation/") or path.begins_with("World/Clouds/") or path.begins_with("SkyRegion") or path.begins_with("Weather"):
			reason="Excluded vegetation canopy, clouds or weather particles; suspended geometry is not lakebed"
		else: reason="Excluded non-support scene category (airship, settlements, flight markers or other props); not Terrain/Mountains/Cliffs/island ground"
		if not reason.is_empty(): exclusions.append({"path":path,"class":kind,"reason":reason});continue
		var mesh: Mesh=prop(state,i,"mesh")
		if mesh==null: fail("Support mesh missing "+path);binary.close();return
		var local_faces := mesh.get_faces()
		var faces := PackedVector3Array()
		var lo := Vector3(INF,INF,INF);var hi := Vector3(-INF,-INF,-INF)
		for point in local_faces:
			var p := world*point
			faces.append(p);lo=lo.min(p);hi=hi.max(p)
		var record := {"path":path,"class":kind,"category":category,"mesh_resource_path":mesh.resource_path,"surface_count":mesh.get_surface_count(),"triangle_count":faces.size()/3,"world_transform":tf(world),"local_faces_raw_sha256":bytes_hash(local_faces.to_byte_array()),"world_faces_raw_sha256":bytes_hash(faces.to_byte_array()),"world_aabb_min":[lo.x,lo.y,lo.z],"world_aabb_max":[hi.x,hi.y,hi.z]}
		if hi.x<BOUNDS.x or lo.x>BOUNDS.z or hi.z<BOUNDS.y or lo.z>BOUNDS.w:
			record.reason="Support mesh outside diagnostic XZ domain; no projected overlap"
			exclusions.append(record);continue
		record.byte_offset=binary.get_position()
		record.byte_length=faces.size()*12
		binary.store_buffer(faces.to_byte_array())
		triangles+=faces.size()/3
		inventory.append(record)
	binary.close()
	var report := {"purpose":"Read-only actual Game49 support export for existing49 underwater-column diagnosis; no50 candidate","source":SOURCE,"source_sha256":EXPECTED_SHA,"packed_node_count":state.get_node_count(),"extraction":"SceneState stored transform chain; actual Mesh.get_faces() transformed to world float32. No scene instantiation, no runtime script, no scene/MM save.","domain_world_xz":[BOUNDS.x,BOUNDS.y,BOUNDS.z,BOUNDS.w],"sea_level_y":0,"vertex_binary":"support49-world-f32.bin","binary_layout":"Little-endian float32 world XYZ, three corners per triangle; per-mesh byte_offset/length","binary_sha256":FileAccess.get_sha256(OUT+"support49-world-f32.bin"),"exported_triangles":triangles,"included_meshes":inventory,"excluded_nodes":exclusions,"source_unchanged":FileAccess.get_sha256(SOURCE)==EXPECTED_SHA}
	var file := FileAccess.open(OUT+"support49-export.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	print("READONLY SUPPORT49 EXPORT meshes=",inventory.size()," triangles=",triangles," excluded_nodes=",exclusions.size())
	# Only read resource state; let deferred resource setup settle before exit.
	for j in range(3): await process_frame
	quit(0)

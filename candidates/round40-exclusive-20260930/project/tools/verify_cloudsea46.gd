extends SceneTree
const BASE := "res://scenes/candidate44/Game44.tscn"
const TARGET := "res://scenes/candidate46/Game46.tscn"
var resource_cache := {}
var game:Node3D
var baseline:Node3D
var output:=""
var captures:=[]
var mobility_checks:=[]
var checks:=[]
var failed:=false
func _initialize() -> void: call_deferred("run")
func stable_variant(value: Variant) -> Variant:
	# Godot 4.5.1 var_to_bytes(NodePath) contains non-deterministic alignment
	# padding. Preserve exact path text + explicit type, never those unused bytes.
	if value is NodePath: return {"__godot_variant_type__":TYPE_NODE_PATH,"path":str(value)}
	# Dictionary key ordering is not content. Make its representation stable
	# while retaining every key/value, including dictionaries nested in arrays.
	# The observed resource drift was NodePath padding, handled above.
	if value is Dictionary:
		var keys: Array = value.keys()
		keys.sort_custom(func(a: Variant,b: Variant) -> bool: return str(typeof(a))+":"+str(a)<str(typeof(b))+":"+str(b))
		var result := {}
		for key in keys: result[key]=stable_variant(value[key])
		return result
	if value is Array:
		var result := []
		for item in value: result.append(stable_variant(item))
		return result
	return value
func digest(value: Variant) -> String: return var_to_bytes(stable_variant(value)).hex_encode().sha256_text()
func frames(count:int) -> void:
	for i in range(count): await process_frame
func settle() -> void:
	await frames(3)
	await RenderingServer.frame_post_draw
func check(ok:bool,label:String,evidence:Variant=null) -> void:
	checks.append({"passed":ok,"name":label,"evidence":evidence})
	if not ok: failed=true
	print("PASS " if ok else "FAIL ",label)
func finish(reason:="") -> void:
	if not reason.is_empty(): check(false,reason)
	var data:={"passed":not failed,"functional_passed":not failed,"visual_acceptance":false,"hardware_gpu_acceptance":false,"renderer":RenderingServer.get_video_adapter_name(),"baseline":BASE,"candidate":TARGET,"checks":checks,"captures":captures,"mobility_checks":mobility_checks,"complete_flight_passed":false,"scope":"Focused46 geometry regression. Every production world layer remains enabled; not total-world visual acceptance."}
	if not output.is_empty():
		var f:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if f!=null: f.store_string(JSON.stringify(data,"  "));f.close()
	if DisplayServer.get_name()!="headless": await settle()
	if is_instance_valid(baseline): baseline.free()
	if is_instance_valid(game): game.queue_free()
	await frames(8)
	print("SEA46 VERIFIED" if not failed else "SEA46 FAILED")
	quit(1 if failed else 0)
func capture(label:String) -> void:
	await frames(18)
	await RenderingServer.frame_post_draw
	var im:Image=root.get_texture().get_image()
	var path:=output.path_join(label+".png")
	check(im.save_png(path)==OK,"Saved "+label)
	var pos:Vector3=game.camera.global_position
	captures.append({"name":label,"image":path,"sha256":FileAccess.get_sha256(path),"camera_transform":str(game.camera.global_transform),"position":[pos.x,pos.y,pos.z],"ground_clearance":pos.y-game.world.ground_height(pos),"camera_clear":camera_clear(pos),"fov":game.camera.fov,"reference":game.scene_environment.current_reference})
func camera_clear(position: Vector3) -> bool:
	var shape := SphereShape3D.new()
	shape.radius = maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = Transform3D(Basis.IDENTITY,position)
	query.collision_mask = 5
	query.exclude = [game.airship.get_rid()]
	return position.y-game.world.ground_height(position)>shape.radius and game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
func probe_translation(id: String, distance: float, original: bool) -> Dictionary:
	var start: Vector3 = game.camera.global_position
	var motion: Vector3 = game.camera.global_basis.x*distance
	var sphere := SphereShape3D.new()
	sphere.radius = maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = sphere
	query.transform = Transform3D(Basis.IDENTITY,start)
	query.motion = motion
	query.collision_mask = 5
	query.exclude = [game.airship.get_rid()]
	var travel: PackedFloat32Array = game.get_world_3d().direct_space_state.cast_motion(query)
	var ray := PhysicsRayQueryParameters3D.create(start,start+motion,5,[game.airship.get_rid()])
	var ray_hit := game.get_world_3d().direct_space_state.intersect_ray(ray)
	var start_clear := camera_clear(start)
	var end_clear := camera_clear(start+motion)
	var clear := start_clear and end_clear and travel.size()==2 and travel[0]>=1.0 and ray_hit.is_empty()
	var row := {"reference":id,"distance_m":distance,"original_350m":original,"passed":clear,"blocked":not clear,"start":str(start),"end":str(start+motion),"start_clear":start_clear,"end_clear":end_clear,"safe_fraction":travel[0] if travel.size()>0 else -1.0,"ray_collider":str(ray_hit.collider.get_path()) if not ray_hit.is_empty() else "none","capture":"","scope":"Camera sphere/ray path only; never a full physical flight pass"}
	mobility_checks.append(row)
	print("PATH CLEAR " if clear else "PATH BLOCKED ",id," ",distance,"m")
	return row
func test_translation(id: String) -> void:
	# Keep original 350m failure; fallback demonstrates only its own short path.
	var home: Transform3D = game.camera.transform
	var original := probe_translation(id,350.0,true)
	if original.passed:
		game.camera.global_position += game.camera.global_basis.x*350.0
		original.capture="sea46-"+id+"-translated-original-plus350m-clear"
		await capture(original.capture)
		game.camera.transform=home
		return
	for distance in [150.0,-150.0,75.0,-75.0,30.0,-30.0]:
		var result := probe_translation(id,distance,false)
		if not result.passed: continue
		game.camera.global_position += game.camera.global_basis.x*distance
		var direction := "plus" if distance>0 else "minus"
		result.capture="sea46-%s-supplemental-%s%dm-clear" % [id,direction,absi(int(distance))]
		await capture(result.capture)
		game.camera.transform=home
		return
	check(false,"No collision-clear camera path "+id)
	game.camera.transform=home
func run() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
	if output.is_empty() or DirAccess.dir_exists_absolute(output): print("SEA46 FAILED: new output directory required");quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	if DisplayServer.get_name()=="headless": await finish("Actual renderer required");return
	if not FileAccess.file_exists(TARGET): await finish("46 candidate missing");return
	baseline=load(BASE).instantiate()
	await settle()
	var before:=snapshot(baseline)
	check(before==snapshot(baseline),"Unmodified baseline double-snapshot control stable")
	if failed: await finish("Audit control drift");return
	game=load(TARGET).instantiate()
	await settle()
	check(before==snapshot(game),"Exact unrelated stored properties survive44 to46")
	var sea_count:=0
	for node in baseline.get_node("SkyRegion39").get_children():
		if not str(node.name).begins_with("CloudSea_"): continue
		sea_count+=1
		var newer:Node3D=game.get_node("SkyRegion39/"+str(node.name))
		var old_mesh:MeshInstance3D=node.find_children("*","MeshInstance3D",true,false)[0]
		var variant:=str(old_mesh.name).trim_prefix("cloud_sea_41_").get_slice("_",0)
		var meshes:=newer.find_children("*","MeshInstance3D",true,false)
		check(newer.transform==node.transform and meshes.size()==1,"Exact sea anchor "+str(node.name))
		if meshes.size()!=1: await finish("Sea mesh count invalid");return
		check(str(meshes[0].name).begins_with("cloud_sea_46_"+variant+"_"),"Variant identified from original mesh "+str(node.name))
		check(canonical(old_mesh.get_active_material(0))==canonical(meshes[0].get_active_material(0)),"Original44 material retained "+str(node.name))
	check(sea_count==25,"Exactly25 original sea roots")
	var floats:=0
	for pair in [["Rain",1800],["Snow",1200]]:
		var old_mm:MultiMesh=baseline.get_node("Weather42b/"+pair[0]).multimesh
		var mm:MultiMesh=game.get_node("Weather42b/"+pair[0]).multimesh
		floats+=mm.buffer.size()
		check(mm.instance_count==pair[1] and mm.buffer.size()==pair[1]*16 and mm.buffer==old_mm.buffer,"Exact persisted "+pair[0]+" buffer")
	check(floats==48000,"48000 precipitation floats retained")
	await settle();baseline.free()
	if failed: await finish("Pre-capture structural gate failed");return
	root.add_child(game);game.sound_enabled=false;game.test_frozen=true
	var weather:Node3D=game.get_node("Weather42b")
	weather.time_scale=0.0
	await frames(30)
	check(game.world.core.size()==208,"208 authored terrain tiles retained")
	check(game.world.layout.props.size()>=54797,"Authored scatter retained",game.world.layout.props.size())
	await capture("sea46-boot")
	for id in ["1216","1343","1128"]:
		game.observe_reference(id)
		weather.seek_time(.05)
		await frames(30)
		await RenderingServer.frame_post_draw
		await physics_frame
		var home:Transform3D=game.camera.global_transform
		await capture("sea46-"+id+"-front")
		game.camera.rotate_y(deg_to_rad(50));await capture("sea46-"+id+"-side")
		game.camera.global_transform=home;game.camera.rotate_y(PI);await capture("sea46-"+id+"-back")
		game.camera.global_transform=home
		await test_translation(id)
		game.camera.global_transform=home
	game.scene_environment.apply_reference("1343")
	var central:Node3D=game.get_node("SkyRegion39/CloudSea_0_0")
	for pair in [["above",Vector3(0,1200,800)],["below",Vector3(0,-370,500)]]:
		var pos:Vector3=central.global_position+pair[1]
		var clearance:float=pos.y-game.world.ground_height(pos)
		check(camera_clear(pos),"Collision-clear central sea "+pair[0]+" camera",clearance)
		if camera_clear(pos):
			game.camera.global_position=pos;game.camera.look_at(central.global_position,Vector3.UP)
			await capture("sea46-central-"+pair[0])
	await finish()
func canonical(value: Variant) -> Variant:
	if value is Resource:
		var id: int = value.get_instance_id()
		if resource_cache.has(id): return resource_cache[id]
		if value is Script: return [value.get_class(),value.resource_path,FileAccess.get_sha256(value.resource_path)]
		var state := {"class":value.get_class()}
		for property in value.get_property_list():
			var key: String = property.name
			if property.usage & PROPERTY_USAGE_STORAGE and key not in ["resource_path"]:
				state[key] = canonical(value.get(key))
		var result := digest(state)
		resource_cache[id] = result
		return result
	if value is Node: return str(value.name)
	if value is Array:
		var array := []
		for item in value: array.append(canonical(item))
		return array
	if value is Dictionary:
		var dictionary := {}
		for key in value: dictionary[key] = canonical(value[key])
		return dictionary
	return value
func snapshot(game: Node) -> Dictionary:
	resource_cache.clear()
	var data := {}
	var nodes: Array[Node] = [game]
	nodes.append_array(game.find_children("*","",true,false))
	for node in nodes:
		var path := str(game.get_path_to(node))
		if path.begins_with("SkyRegion39/CloudSea_") and path.split("/").size()>2: continue
		var row := {"class":node.get_class()}
		for property in node.get_property_list():
			var key: String = property.name
			if not property.usage & PROPERTY_USAGE_STORAGE or key in ["owner","scene_file_path"]: continue
			row[key] = canonical(node.get(key))
		if node is MultiMeshInstance3D and node.multimesh != null:
			var mm: MultiMesh = node.multimesh
			row.exact_multimesh_buffer = digest(mm.buffer)
			row.exact_multimesh_config = [mm.instance_count,mm.visible_instance_count,mm.transform_format,mm.use_colors,mm.use_custom_data]
		data[path] = row
	return data

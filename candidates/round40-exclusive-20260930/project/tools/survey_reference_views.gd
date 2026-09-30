extends SceneTree
## One saved world, all reference states; no replacement scenery or shaders.
var scene_path := ""
var output := ""
var side_back := false
var game: Node3D
var checks: Array = []
var captures: Array = []
var source_sha := ""
var world_id := 0
var environment_id := 0
var original_default := ""

func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await process_frame
func check(ok: bool, name: String, detail: Variant = null) -> void:
	checks.append({"passed":ok,"name":name,"detail":detail})
	print("PASS " if ok else "FAIL ",name)
func camera_clear() -> bool:
	var shape := SphereShape3D.new()
	shape.radius = maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape=shape
	query.transform=Transform3D(Basis.IDENTITY,game.camera.global_position)
	query.collision_mask=5
	query.exclude=[game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
func capture(name: String, identity: String) -> void:
	await frames(12)
	await physics_frame
	await RenderingServer.frame_post_draw
	var clear := camera_clear()
	check(clear,"Observation camera collision-free "+name)
	var image: Image=root.get_texture().get_image()
	var file_path:=output.path_join(name+".png")
	var error:=image.save_png(file_path)
	check(error==OK,"Rendered image saved "+name,error)
	var camera: Camera3D=game.camera
	captures.append({"name":name,"reference_identity":identity,"image":file_path,"sha256":FileAccess.get_sha256(file_path) if error==OK else "","camera_transform":str(camera.global_transform),"fov":camera.fov,"near":camera.near,"camera_clear":clear,"pixels":[image.get_width(),image.get_height()],"reference_state":game.scene_environment.current_reference,"weather_time":game.get_node("Weather42b").time_seconds,"world_instance":game.world.get_instance_id(),"environment_instance":game.get_node("Environment").environment.get_instance_id()})
func finish(code: int, reason: String) -> void:
	var adapter:=RenderingServer.get_video_adapter_name()
	var software:=DisplayServer.get_name()=="headless" or "llvmpipe" in adapter.to_lower() or "softpipe" in adapter.to_lower()
	var report:={"functional_passed":code==0,"reason":reason,"source_scene":scene_path,"source_sha256":source_sha,"renderer":adapter,"software_renderer":software,"hardware_gpu_acceptance":false,"visual_acceptance":false,"complete_flight_passed":false,"checks":checks,"captures":captures,"scope":"Reference survey of one unchanged saved world through its public observation/environment controls. Camera collision failures and screenshots are retained. Side/back are rotations, not flight validation. Weather is reproducibly held at 0.35 seconds using the existing controller. No script, geometry, material, environment resource or reference camera replacement."}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null: file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game): game.queue_free(); game=null
	await frames(8)
	print("REFERENCE SURVEY COMPLETE ",code==0," ",reason)
	quit(code)
func run() -> void:
	if DisplayServer.get_name()=="headless": push_error("Reference survey requires a rendering backend");quit(2);return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--scene="): scene_path=arg.trim_prefix("--scene=")
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
		if arg=="--side-back": side_back=true
	if not scene_path.begins_with("res://scenes/") or not FileAccess.file_exists(scene_path): push_error("Provide an existing saved native scene");quit(2);return
	if output.is_empty() or not output.is_absolute_path() or DirAccess.dir_exists_absolute(output): push_error("Provide a new absolute output directory");quit(2);return
	if DirAccess.make_dir_recursive_absolute(output)!=OK: push_error("Could not create evidence directory");quit(2);return
	source_sha=FileAccess.get_sha256(scene_path)
	original_default=ProjectSettings.get_setting("application/run/main_scene")
	var packed:=load(scene_path) as PackedScene
	if packed==null: await finish(2,"Scene failed to load");return
	game=packed.instantiate() as Node3D
	root.add_child(game)
	game.sound_enabled=false
	game.test_frozen=true
	await frames(30)
	world_id=game.world.get_instance_id()
	environment_id=game.get_node("Environment").environment.get_instance_id()
	check(game.world.core.size()==208,"208 authored terrain tiles retained")
	check(game.world.layout.props.size()>=54797,"Authored scatter count retained",game.world.layout.props.size())
	for pair in [["Rain",1800],["Snow",1200]]:
		var mm: MultiMesh=game.get_node("Weather42b/"+pair[0]).multimesh
		check(mm.instance_count==pair[1] and mm.buffer.size()==pair[1]*16,"Persisted weather buffer "+pair[0],mm.buffer.size())
	await capture("boot-controller-original","assets/reference.jpg")
	var ids: Array = []
	var weather: Node3D=game.get_node("Weather42b")
	weather.time_scale=0.0
	for entry in game.scene_environment.plan:
		var id:=str(entry.ref)
		check(not ids.has(id),"Unique reference "+id)
		ids.append(id)
		game.observe_reference(id)
		weather.seek_time(0.0)
		weather.seek_time(.35)
		check(game.world.get_instance_id()==world_id and game.get_node("Environment").environment.get_instance_id()==environment_id,"Same world and environment "+id)
		await capture("reference-"+id,"ref/"+id+".png")
		if side_back:
			var home: Transform3D=game.camera.transform
			game.camera.rotate_y(deg_to_rad(55))
			await capture("reference-"+id+"-side","ref/"+id+".png")
			game.camera.transform=home
			game.camera.rotate_y(PI)
			await capture("reference-"+id+"-back","ref/"+id+".png")
			game.camera.transform=home
	var expected_ids: Array = ["1125","1126","1128","1129","1131","1135","1216","1217","1218","1220","1274","1275","1276","1278","1332","1341","1342","1343","1344","1347"]
	var sorted_ids: Array = ids.duplicate()
	sorted_ids.sort()
	check(sorted_ids==expected_ids,"All exact 20 GOAL reference identities covered",ids)
	check(FileAccess.get_sha256(scene_path)==source_sha,"Saved source scene unchanged")
	check(str(ProjectSettings.get_setting("application/run/main_scene"))==original_default,"Project default unchanged")
	var passed:=true
	for row in checks: passed=passed and row.passed
	await finish(0 if passed else 1,"All captured; visual review and hardware GPU validation remain pending")

extends SceneTree
## Run twice, in separate new output dirs: default 45 and --baseline for 44.
## Same fixed cameras and frozen weather; material-only A/B evidence, not acceptance.
var game: Node3D
var output := ""
var baseline := false
var checks := []
var captures := []
var mobility_checks := []
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await process_frame
func check(ok: bool,label: String,evidence: Variant=null) -> void:
	checks.append({"passed":ok,"name":label,"evidence":evidence})
	print("PASS " if ok else "FAIL ",label)
func camera_clear(position: Vector3) -> bool:
	var shape := SphereShape3D.new()
	shape.radius = .12
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = Transform3D(Basis.IDENTITY,position)
	query.collision_mask = 5
	query.exclude = [game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
func capture(label: String) -> void:
	await frames(3)
	await RenderingServer.frame_post_draw
	var path := output.path_join(label+".png")
	var image: Image = root.get_texture().get_image()
	check(image.save_png(path)==OK,"Actual rendered capture "+label)
	captures.append({"name":label,"path":path,"sha256":FileAccess.get_sha256(path),"camera_transform":str(game.camera.transform),"fov":game.camera.fov,"reference":game.scene_environment.current_reference,"pixels":[image.get_width(),image.get_height()],"camera_clear":camera_clear(game.camera.global_position)})
func probe_translation(id: String, distance: float, original: bool) -> Dictionary:
	var start: Vector3 = game.camera.global_position
	var motion: Vector3 = game.camera.global_basis.x*distance
	var sphere := SphereShape3D.new()
	sphere.radius = .12
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
		original.capture="reference-"+id+"-translated-original-plus350m-clear"
		await capture(original.capture)
		game.camera.transform=home
		return
	for distance in [150.0,-150.0,75.0,-75.0,30.0,-30.0]:
		var result := probe_translation(id,distance,false)
		if not result.passed: continue
		game.camera.global_position += game.camera.global_basis.x*distance
		var direction := "plus" if distance>0 else "minus"
		result.capture="reference-%s-supplemental-%s%dm-clear" % [id,direction,absi(int(distance))]
		await capture(result.capture)
		game.camera.transform=home
		return
	print("NO CLEAR SUPPLEMENTAL PATH ",id)
	game.camera.transform=home
func verify_materials() -> void:
	var total := 0
	var valid := true
	var expected_mode := BaseMaterial3D.DIFFUSE_BURLEY if baseline else BaseMaterial3D.DIFFUSE_LAMBERT_WRAP
	for node in game.find_children("*","MeshInstance3D",true,false):
		var path := str(game.get_path_to(node))
		if not (path.begins_with("SkyRegion39/UpperCloudBank43_") or path.begins_with("SkyRegion39/DistantCloudBank41_") or path.begins_with("SkyRegion39/CloudSea_")): continue
		for surface in range(node.mesh.get_surface_count()):
			var material: Material = node.get_active_material(surface)
			total+=1
			valid=valid and material is StandardMaterial3D and material.diffuse_mode==expected_mode and material.roughness==1.0 and material.vertex_color_use_as_albedo and not material.emission_enabled and material.shading_mode!=BaseMaterial3D.SHADING_MODE_UNSHADED
	check(valid and total==1808,"Live target material type/mode/roughness/vertex colors",{"surface_count":total,"expected_diffuse_mode":expected_mode})
func run() -> void:
	if DisplayServer.get_name()=="headless":
		push_error("No headless rendering verification; --check-only is static parse only")
		quit(2);return
	for arg in OS.get_cmdline_user_args():
		if arg=="--baseline": baseline=true
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
	assert(not output.is_empty() and not DirAccess.dir_exists_absolute(output),"New output directory required")
	DirAccess.make_dir_recursive_absolute(output)
	var scene := "res://scenes/candidate44/Game44.tscn" if baseline else "res://scenes/candidate45/Game45.tscn"
	game=load(scene).instantiate()
	root.add_child(game)
	game.sound_enabled=false
	game.test_frozen=true
	var weather: Node3D = game.get_node("Weather42b")
	weather.time_scale=0.0
	await frames(30)
	await RenderingServer.frame_post_draw
	verify_materials()
	for id in ["1343","1128","1216","1342"]:
		game.observe_reference(id)
		weather.seek_time(.05)
		# Environment/Sky/light updates warm up separately from the 3-frame capture.
		await frames(30)
		await RenderingServer.frame_post_draw
		await physics_frame
		var home: Transform3D = game.camera.transform
		await capture("reference-"+id)
		if id!="1342":
			game.camera.rotate_y(deg_to_rad(55))
			await capture("reference-"+id+"-side")
			game.camera.transform=home
			game.camera.rotate_y(PI)
			await capture("reference-"+id+"-back")
			game.camera.transform=home
			await test_translation(id)
		game.camera.transform=home
	var passed := true
	for row in checks: passed=passed and row.passed
	var original_paths_clear := true
	var supplemental_path_available := {}
	for row in mobility_checks:
		if row.original_350m: original_paths_clear=original_paths_clear and row.passed
		if row.passed: supplemental_path_available[row.reference]=row.distance_m
	var adapter := RenderingServer.get_video_adapter_name()
	var report := {"material_render_checks_passed":passed,"original_350m_paths_all_clear":original_paths_clear,"complete_flight_passed":false,"mobility_checks":mobility_checks,"available_camera_paths_m":supplemental_path_available,"checks":checks,"captures":captures,"scene":scene,"scene_sha256":FileAccess.get_sha256(scene),"baseline":baseline,"renderer":adapter,"software_renderer":"llvmpipe" in adapter.to_lower() or "softpipe" in adapter.to_lower(),"visual_acceptance":false,"hardware_gpu_acceptance":false,"scope":"Paired 44/45 fixed-reference material-only comparison. 1343/1128/1216 front-side-back and 1342 front. Reference poses never moved to hide geometry. Original 350m blocked facts are retained independently of material/render checks. Ordered fallback camera sweeps are +150/-150/+75/-75/+30/-30m; only the first fully clear path gets a separately named supplemental image, proving that short path alone. 30-frame light warmup; each image 3 process frames plus post_draw; weather frozen at 0.05 in both runs."}
	var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	game.queue_free()
	await frames(8)
	quit(0 if passed else 1)

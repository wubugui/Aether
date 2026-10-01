extends "res://tools/build_lake_depth50.gd"
## Canonical saved49→50 scope, then frozen same-world original/disabled/restored
## and disabled/enabled/disabled controls. No snapshot substitutes for flight.
const FROZEN_WORLD_TIME := 0.35
var game: Node3D
var output := ""
var checks := []
var captures := []
var comparisons := []
var movement_checks := []
var source_water: ShaderMaterial
var depth_water: ShaderMaterial
var controller: Node3D
var original_uniform_names := []
var unchanged_fingerprint := ""
var candidate_sha := ""
var saved_weather := {}
var baseline_motion := {}
var control_modes := []
var baseline_camera_mask := 0
var baseline_ocean_layers := 0
var baseline_camera_count := 0
var freeze_physics_evidence := {}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
	call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await process_frame
func check(ok: bool,name: String,evidence: Variant=null) -> bool:
	checks.append({"passed":ok,"name":name,"evidence":evidence})
	print("PASS " if ok else "FAIL ",name)
	return ok
func freeze_tree(node: Node) -> void:
	# Disabling process_mode removes CollisionObject3D from PhysicsServer3D.
	# Disable callbacks only, preserving mode/disable_mode/shape/layer/RID state.
	node.set_process(false)
	node.set_physics_process(false)
	node.set_process_input(false)
	node.set_process_unhandled_input(false)
	node.set_process_unhandled_key_input(false)
	if node is AnimationPlayer: node.pause()
	if node is Timer: node.paused=true
	for child in node.get_children(): freeze_tree(child)
func collision_activity_state(scene: Node) -> Dictionary:
	var result := {}
	for node in scene.find_children("*","CollisionObject3D",true,false):
		result[str(scene.get_path_to(node))]={"process_mode":node.process_mode,"disable_mode":node.disable_mode,"can_process":node.can_process(),"collision_layer":node.collision_layer,"collision_mask":node.collision_mask,"rid":str(node.get_rid())}
	return result
func camera_clear(position: Vector3) -> bool:
	var shape := SphereShape3D.new();shape.radius=maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,position);query.collision_mask=5;query.exclude=[game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
func original_parameter_state(material: ShaderMaterial) -> Dictionary:
	resource_cache.clear()
	var data := {}
	for name in original_uniform_names: data[name]=canonical(material.get_shader_parameter(name))
	return data
func refresh_original_parameters() -> bool:
	for name in original_uniform_names: source_water.set_shader_parameter(name,depth_water.get_shader_parameter(name))
	return check(original_parameter_state(source_water)==original_parameter_state(depth_water),"All original Ocean uniforms equal for current reference")
func shot(label: String, view: Dictionary) -> Image:
	await frames(3);await physics_frame;await RenderingServer.frame_post_draw
	var image: Image=root.get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	var path := output.path_join(label+".png")
	check(image.save_png(path)==OK,"Actual rendered RGBA capture "+label)
	var clear := camera_clear(game.camera.global_position)
	check(clear,"Camera clear "+label)
	captures.append({"name":label,"path":path,"sha256":FileAccess.get_sha256(path),"rgba_data_digest":digest(image.get_data()),"size":[image.get_width(),image.get_height()],"view":view,"camera_transform":str(game.camera.global_transform),"fov":game.camera.fov,"camera_clear":clear,"world_instance":game.world.get_instance_id(),"explicitly_set_frozen_world_time":FROZEN_WORLD_TIME,"global_value_readback_not_used":true})
	return image
func compare_images(a: Image,b: Image,name: String,required_equal: bool) -> bool:
	var equal := a.get_size()==b.get_size() and a.get_format()==b.get_format() and a.get_data()==b.get_data()
	comparisons.append({"name":name,"pixel_exact_zero_diff":equal,"required_equal":required_equal,"rgba_size":[a.get_width(),a.get_height()],"method":"Every RGBA8 byte compared, not screenshot file hash or tolerance","a_data_digest":digest(a.get_data()),"b_data_digest":digest(b.get_data())})
	if required_equal: check(equal,"Required full RGBA zero-difference "+name)
	return equal
func probe_motion(reference: String, delta: Vector3,label: String,required: bool) -> void:
	var start: Vector3=game.camera.global_position
	var sphere := SphereShape3D.new();sphere.radius=maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape=sphere;query.transform=Transform3D(Basis.IDENTITY,start);query.motion=delta;query.collision_mask=5;query.exclude=[game.airship.get_rid()]
	var fractions: PackedFloat32Array=game.get_world_3d().direct_space_state.cast_motion(query)
	var hit := game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,start+delta,5,[game.airship.get_rid()]))
	var clear := camera_clear(start) and camera_clear(start+delta) and fractions.size()==2 and fractions[0]>=1.0 and hit.is_empty()
	var collider := str(game.get_path_to(hit.collider)) if not hit.is_empty() else "none"
	var prior: Dictionary=baseline_motion.get(reference+"/"+label,{})
	var no_regression: bool= not prior.is_empty() and clear==prior.passed and collider==prior.collider and fractions.size()==2 and fractions[0]==float(prior.safe_fraction)
	var row := {"reference":reference,"label":label,"required":required,"passed":clear,"safe_fraction":fractions[0] if fractions.size()>0 else -1,"collider":collider,"baseline49_passed":prior.get("passed"),"baseline49_safe_fraction":prior.get("safe_fraction"),"known_baseline_failure":not clear and no_regression,"no_new_regression":no_regression,"start":str(start),"end":str(start+delta),"scope":"Camera sphere and ray only; no full-airship certification"}
	movement_checks.append(row)
	check(no_regression,"Exact49 motion outcome retained "+reference+"/"+label,row)
func set_view(view: Dictionary) -> void:
	game.get_node("World/Ocean").material_override=depth_water
	controller.set_depth_enabled(false)
	game.observe_reference(str(view.reference))
	var weather: Node3D=game.get_node("Weather42b")
	weather.seek_time(0.0);weather.seek_time(.35)
	RenderingServer.global_shader_parameter_set("world_time",FROZEN_WORLD_TIME)
	if view.has("position"):
		game.camera.global_position=v3(view.position);game.camera.look_at(v3(view.target));game.camera.fov=view.get("fov",64.0)
	elif view.get("rotation","")=="side": game.camera.rotate_y(deg_to_rad(55))
	elif view.get("rotation","")=="back": game.camera.rotate_y(PI)
	await frames(6);await physics_frame;await RenderingServer.frame_post_draw
	refresh_original_parameters()
func controls_for_view(view: Dictionary) -> void:
	await set_view(view)
	var name: String=view.name
	var ocean: MeshInstance3D=game.get_node("World/Ocean")
	var pose: Transform3D=game.camera.global_transform
	var original_params := original_parameter_state(depth_water)
	# 49's genuine original material/code in the canonical-unchanged same world.
	ocean.material_override=source_water
	var a := await shot(name+"--A49-original",view)
	ocean.material_override=depth_water;controller.set_depth_enabled(false)
	var b := await shot(name+"--B50-depth-disabled",view)
	ocean.material_override=source_water
	var a2 := await shot(name+"--A49-restored",view)
	compare_images(a,b,name+"/49-original-vs50-disabled",true)
	compare_images(a,a2,name+"/49-A-vs49-A2",true)
	ocean.material_override=depth_water;controller.set_depth_enabled(true)
	var enabled := await shot(name+"--C50-depth-enabled",view)
	compare_images(b,enabled,name+"/50-disabled-vs50-enabled",bool(view.get("outside_domain_control",false)))
	controller.set_depth_enabled(false)
	var b2 := await shot(name+"--B50-disabled-restored",view)
	compare_images(b,b2,name+"/50-disabled-vs50-disabled-restored",true)
	check(game.camera.global_transform==pose,"Reference pose untouched across all material/depth controls "+name)
	check(original_params==original_parameter_state(depth_water) and original_params==original_parameter_state(source_water),"All original Ocean uniform values untouched during controls "+name)
	control_modes.append({"view":name,"normal_flag_false":true,"controller":controller.get_diagnostic_state(),"old_ocean_parameters_fingerprint":digest(original_params)})
func observations() -> void:
	root.size=Vector2i(1180,664)
	root.add_child(game)
	game.sound_enabled=false;game.test_frozen=true
	var weather: Node3D=game.get_node("Weather42b");weather.time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP)
	depth_water=game.get_node("World/Ocean").material_override
	var startup: Dictionary=controller.get_diagnostic_state()
	check(startup.get("bound",false) and startup.get("enabled",false) and startup.get("actual_uniform",false) and startup.get("texture_count",0)==5 and startup.get("failure","").is_empty(),"Default candidate binds five images and enables geographic depth",startup)
	var collision_before := collision_activity_state(game)
	freeze_tree(game)
	await physics_frame;await physics_frame
	var collision_after := collision_activity_state(game)
	freeze_physics_evidence={"collision_object_count":collision_before.size(),"before_fingerprint":digest(collision_before),"after_fingerprint":digest(collision_after),"unchanged":collision_before==collision_after,"freeze_method":"set_process(false)/set_physics_process(false), with input callbacks off; process_mode and disable_mode untouched"}
	check(collision_before==collision_after and collision_before.size()>0,"Freezing render comparison preserves every live physics object mode/layer/RID",freeze_physics_evidence)
	var world_id: int=game.world.get_instance_id()
	for reference in ["1128","1129"]:
		await set_view({"name":"reference-"+reference,"reference":reference})
		var expected := Vector3(1150,10,-1000) if reference=="1128" else Vector3(1300,7,-950)
		check(game.camera.global_position.is_equal_approx(expected),"Original fixed camera retained "+reference)
		probe_motion(reference,game.camera.global_basis.x*350.,"original-plus350m",true)
		probe_motion(reference,game.camera.global_basis.x*150.,"protected-plus150m",false)
		probe_motion(reference,-game.camera.global_basis.z*200.,"protected-approach200m",false)
		for rotation in ["front","side","back"]:
			await controls_for_view({"name":"reference-"+reference+"-"+rotation,"reference":reference,"rotation":rotation})
	var islands: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/source-assets/lake49/lake49-payload.json"))
	for camera in islands.nearshore_cameras:
		var view: Dictionary=camera.duplicate(true);view.reference="1128";view.name="nearshore-"+str(camera.name)
		await controls_for_view(view)
	for view in [{"name":"outside-domain-south-sea","reference":"1128","position":[-1500,80,500],"target":[-1500,0,2000],"fov":60,"outside_domain_control":true},{"name":"outside-domain-east","reference":"1128","position":[2400,150,-1100],"target":[3900,0,-1100],"fov":60,"outside_domain_control":true}]:
		await controls_for_view(view)
	check(game.world.get_instance_id()==world_id,"All A/B/A modes share the original physical world instance")
	check(game.camera.cull_mask==baseline_camera_mask and game.get_node("World/Ocean").layers==baseline_ocean_layers,"Runtime depth controller preserves original camera mask and Ocean layers")
	check(game.find_children("*","Camera3D",true,false).size()==baseline_camera_count and game.get_node(NEW_GROUP).get_child_count()==0,"No reflection camera, SubViewport or extra scene nodes created")
	game.get_node("World/Ocean").material_override=depth_water;controller.set_depth_enabled(true)
	check(controller.get_diagnostic_state().actual_uniform==true,"Live candidate restored to its authored enabled state")
func finish() -> void:
	var limited := failures.is_empty()
	for row in checks: limited=limited and row.passed
	var normal := comparisons.size()>0
	for row in comparisons:
		if row.required_equal: normal=normal and row.pixel_exact_zero_diff
	var requested := movement_checks.size()==6
	for row in movement_checks:
		if row.required: requested=requested and row.passed
	var report := {"limited_saved_state_and_runtime_passed":limited,"normal_pass_zero_diff":normal,"requested_motion_all_passed":requested,"total_acceptance_passed":false,"candidate":TARGET,"candidate_sha256":candidate_sha,"baseline":BASE,"baseline_sha256":BASE_SHA,"unaffected_graph_fingerprint":unchanged_fingerprint,"weather":saved_weather,"checks":checks,"failures":failures,"comparisons":comparisons,"captures":captures,"movement_checks":movement_checks,"control_modes":control_modes,"verifier_version":2,"freeze_physics_evidence":freeze_physics_evidence,"frozen_world_time":FROZEN_WORLD_TIME,"renderer":RenderingServer.get_video_adapter_name(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"complete_airship_flight_passed":false,"exit_code_scope":"0 means scoped saved-state/runtime/normal-zero-diff gates only, not requested-motion or visual acceptance","scope":"Frozen single canonical-unchanged world; genuine49 Ocean material→50-disabled→49-restored fullRGBA zero-diff, then50-disabled→enabled→disabled. All original uniforms refreshed per reference and unchanged within tests. Fixed1128/1129/side/back, four source-island nearshore cameras, two wholly outward-facing out-of-domain controls. No reflection, camera mask/layer or material-authority change. Original required350m failures remain separate."}
	if not output.is_empty():
		var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null: file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game): await settle();game.queue_free();game=null
	await frames(8)
	print("DEPTH50 V2 VERIFIED scoped=",limited," normal_zero_diff=",normal," required_motion=",requested," total_acceptance=false")
	quit(0 if limited and normal else 1)
func run() -> void:
	if not require(DisplayServer.get_name()!="headless","Real renderer required for50 verification"): quit(2);return
	if not require(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output),"New absolute output dir required"): quit(2);return
	DirAccess.make_dir_recursive_absolute(output);diagnostic_dir=output
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.file_exists(TARGET),"Baseline mismatch or candidate missing"): await finish();return
	candidate_sha=FileAccess.get_sha256(TARGET)
	var source_packed: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var target_packed: PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var source: Node3D=source_packed.instantiate();game=target_packed.instantiate()
	await settle()
	baseline_camera_mask=source.get_node("Camera").cull_mask
	baseline_ocean_layers=source.get_node("World/Ocean").layers
	baseline_camera_count=source.find_children("*","Camera3D",true,false).size()
	check(verify_new_inventory(game),"Only one new depth controller is present")
	var before := graph_state(source,source_packed);var after := graph_state(game,target_packed)
	check(before==graph_state(source,source_packed),"Fresh49 canonical double-snapshot stable")
	check(before==after,"All saved49 state except soleOcean binding unchanged in50",differences(before,after))
	unchanged_fingerprint=digest(before);saved_weather=weather_state(source)
	check(saved_weather==weather_state(game),"Exact48000 weather floats retained")
	var report: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DEST+"build-report-50.json"))
	check(report.get("depth_only_build_reload_passed",false) and report.get("candidate_sha256","")==candidate_sha,"Fresh50 hash matches successful independent build")
	check(report.get("unaffected_graph_fingerprint","")==unchanged_fingerprint,"Independent verifier agrees with untouched49 fingerprint")
	check(report.get("new_state_fingerprint","")==digest(new_state(game)),"SavedOcean/controller exact build fingerprints match")
	for asset in report.get("asset_inventory",[]): check(FileAccess.file_exists(asset.path) and FileAccess.get_sha256(asset.path)==asset.sha256,"Independent50 asset hash retained "+str(asset.path))
	check(FileAccess.get_sha256(CONTROLLER)==report.get("controller_script_sha256","") and FileAccess.get_sha256(WATER_SOURCE)==report.ocean_ledger.source_shader_file_sha256,"Authoring controller/shader inputs unchanged")
	source_water=source.get_node("World/Ocean").material_override.duplicate(false)
	for uniform in source_water.shader.get_shader_uniform_list(): original_uniform_names.append(str(uniform.name))
	var previous: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/cloud-evidence/lake49-20260930T234925Z-pYs5Nx/images/report.json"))
	check(previous.get("candidate_sha256","")==BASE_SHA,"Known49 motion evidence belongs to exact baseline")
	for row in previous.get("movement_checks",[]):
		if row.phase=="candidate49": baseline_motion[row.reference+"/"+row.label]=row
	await settle();source.free()
	await observations()
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(TARGET)==candidate_sha,"49/50 scene files remain unchanged after runtime A/B/A")
	await finish()

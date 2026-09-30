extends "res://tools/build_cloud_lake48.gd"
## Fresh-process saved-state comparison, live terrain/scatter cache checks, and
## fixed 1128/1129/1275/1276 observations of the same physical scene.
var game: Node3D
var output := ""
var baseline := false
var static_only := false
var checks := []
var captures := []
var movement_checks := []
var geometry_samples := []
var scene_sha := ""
var baseline_snapshot := {}
var unchanged_fingerprint := ""
var saved_weather := {}

func _initialize() -> void:
	parse_arguments()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
		if arg=="--baseline": baseline=true
		if arg=="--static-only": static_only=true
	call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await process_frame
func check(ok: bool, label: String, evidence: Variant=null) -> bool:
	checks.append({"passed":ok,"name":label,"evidence":evidence})
	print("PASS " if ok else "FAIL ",label)
	return ok
func triangle_height(mesh_node: MeshInstance3D, point: Vector3) -> float:
	var transform := world_transform(mesh_node)
	var local := transform.affine_inverse()*point
	var faces: PackedVector3Array=mesh_node.mesh.get_faces()
	var highest := -INF
	for i in range(0,faces.size(),3):
		var a := faces[i]
		var b := faces[i+1]
		var c := faces[i+2]
		var denominator := (b.z-c.z)*(a.x-c.x)+(c.x-b.x)*(a.z-c.z)
		if absf(denominator)<0.00000001: continue
		var wa := ((b.z-c.z)*(local.x-c.x)+(c.x-b.x)*(local.z-c.z))/denominator
		var wb := ((c.z-a.z)*(local.x-c.x)+(a.x-c.x)*(local.z-c.z))/denominator
		var wc := 1.0-wa-wb
		if minf(wa,minf(wb,wc))>=-0.0001:
			highest=maxf(highest,(transform*Vector3(local.x,a.y*wa+b.y*wb+c.y*wc,local.z)).y)
	return highest
func boundary_checks(source: Node3D, candidate: Node3D) -> void:
	var outer_max_error := 0.0
	var outer_missing := 0
	var seam_max_error := 0.0
	var seam_missing := 0
	for path in MESH_PATHS.slice(0,2):
		var old: MeshInstance3D=source.get_node(path)
		var current: MeshInstance3D=candidate.get_node(path)
		var origin := world_transform(current).origin
		for step in range(33):
			for x in [768.0,1536.0]:
				var p := Vector3(x,0,origin.z+float(step)*24.0)
				var a := triangle_height(old,p)
				var b := triangle_height(current,p)
				if not is_finite(a) or not is_finite(b): outer_missing+=1
				else: outer_max_error=maxf(outer_max_error,absf(a-b))
			var z := -768.0 if path.contains("Ground_1_-2") else -2304.0
			var p := Vector3(768.0+float(step)*24.0,0,z)
			var a := triangle_height(old,p)
			var b := triangle_height(current,p)
			if not is_finite(a) or not is_finite(b): outer_missing+=1
			else: outer_max_error=maxf(outer_max_error,absf(a-b))
	var south: MeshInstance3D=candidate.get_node(MESH_PATHS[0])
	var north: MeshInstance3D=candidate.get_node(MESH_PATHS[1])
	for step in range(65):
		var p := Vector3(768.0+float(step)*12.0,0,-1536.0)
		var a := triangle_height(south,p)
		var b := triangle_height(north,p)
		if not is_finite(a) or not is_finite(b): seam_missing+=1
		else: seam_max_error=maxf(seam_max_error,absf(a-b))
	check(outer_missing==0 and outer_max_error<0.03,"Untouched neighboring terrain boundary support within 3cm",{"max_error_m":outer_max_error,"missing_samples":outer_missing})
	check(seam_missing==0 and seam_max_error<0.03,"Edited two-tile shared seam within 3cm",{"max_error_m":seam_max_error,"missing_samples":seam_missing})
func sample_lake(scene: Node3D) -> void:
	var shared_paths: Array=MESH_PATHS.slice(0,2)
	for mountain in scene.get_node("World/Mountains").find_children("*","MeshInstance3D",true,false):
		shared_paths.append(str(scene.get_path_to(mountain)))
	for z in [-1050.0,-1150.0,-1300.0,-1450.0,-1600.0,-1750.0,-1900.0,-2050.0,-2130.0,-2170.0,-2200.0]:
		for x in [900.0,1025.0,1150.0,1275.0,1400.0]:
			var point := Vector3(x,0,z)
			var heights := {}
			var top := -INF
			var edited_top := -INF
			var top_entity := ""
			for path in shared_paths:
				var y := triangle_height(scene.get_node(path),point)
				if is_finite(y):
					heights[path.get_file()]=y
					if y>top: top=y;top_entity=path.get_file()
					if path in MESH_PATHS: edited_top=maxf(edited_top,y)
			geometry_samples.append({"x":x,"z":z,"surface_y":top if is_finite(top) else null,"top_entity":top_entity,"open_water_across_two_tiles_and_all_mountains":is_finite(top) and top<0,"four_edited_meshes_surface_y":edited_top if is_finite(edited_top) else null,"entity_heights":heights})
	# Actual shared mountain feet are included: the untouched northern foothills
	# close the basin near Z=-2170 even when edited tile geometry is below water.
	# This grid is diagnostic; it is not a proof of a continuous rectangular lake.
	for probe in payload.get("geometry_checks",[]):
		var point := Vector3(probe.x,0,probe.z)
		var top := -INF
		for path in shared_paths: top=maxf(top,triangle_height(scene.get_node(path),point))
		check(is_finite(top) and top>=float(probe.get("min_y",-10000)) and top<=float(probe.get("max_y",10000)),"Authored lake-height probe including unchanged mountain feet",{"requested":probe,"actual_y":top})
func runtime_cache_checks() -> void:
	var world: Node3D=game.get_node("World")
	for path in MESH_PATHS.slice(0,2):
		var ground: MeshInstance3D=game.get_node(path)
		var cell: Vector2i=world.cell_at(ground.global_position+Vector3(.01,0,.01))
		check(world.chunks.has(cell) and world.chunks[cell]==ground,"Runtime chunks use current native mesh "+str(cell))
		var all_match := true
		var max_error := 0.0
		for offset in [Vector3(128,0,120),Vector3(300,0,300),Vector3(450,0,540),Vector3(640,0,640)]:
			var point: Vector3=ground.global_transform*offset
			var actual: float=world.terrain_height(point)
			var raw := triangle_height(ground,point)
			all_match=all_match and is_finite(raw)
			if is_finite(raw): max_error=maxf(max_error,absf(actual-maxf(0,raw)))
		check(all_match and max_error<0.03,"Runtime height cache samples current triangles with sea clamp "+str(cell),{"max_error_m":max_error,"note":"terrain_height intentionally clamps bed below Y0 to zero; geometry samples report bed separately"})
		check(world.terrain_samples.has(cell) and world.terrain_samples[cell].triangles==ground.mesh.get_faces(),"Runtime terrain_samples exactly match native mesh "+str(cell))
	var index := 0
	var total_checked := 0
	var valid := true
	for grove in world.get_node("Vegetation").get_children():
		var path := str(game.get_path_to(grove))
		for i in range(grove.multimesh.instance_count):
			if SCATTER_COUNTS.has(str(grove.name)):
				var expected: Transform3D=grove.global_transform*grove.multimesh.get_instance_transform(i)
				valid=valid and world.prop_transforms.has(index) and world.prop_transforms[index]==expected
				total_checked+=1
			index+=1
	check(valid and total_checked==500,"Runtime prop bookkeeping reads all 500 current saved scatter transforms",{"target_instances":total_checked,"all_world_instances":index})
func camera_clear(position: Vector3) -> bool:
	var shape := SphereShape3D.new()
	shape.radius=maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape=shape
	query.transform=Transform3D(Basis.IDENTITY,position)
	query.collision_mask=5
	query.exclude=[game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
func capture(label: String, reference: String, supplemental := false) -> void:
	await frames(3)
	await physics_frame
	await RenderingServer.frame_post_draw
	var path := output.path_join(label+".png")
	var image: Image=root.get_texture().get_image()
	var clear := camera_clear(game.camera.global_position)
	check(image.save_png(path)==OK,"Actual rendered capture "+label)
	check(clear,"Camera collision-free "+label)
	captures.append({"name":label,"path":path,"sha256":FileAccess.get_sha256(path),"reference":reference,"supplemental":supplemental,"camera_transform":str(game.camera.global_transform),"fov":game.camera.fov,"camera_clear":clear,"pixels":[image.get_width(),image.get_height()],"world_instance":game.world.get_instance_id(),"weather_time":game.get_node("Weather42b").time_seconds})
func motion_probe(reference: String, delta: Vector3, label: String, required: bool) -> Dictionary:
	var start: Vector3=game.camera.global_position
	var shape := SphereShape3D.new()
	shape.radius=maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,start);query.motion=delta
	query.collision_mask=5;query.exclude=[game.airship.get_rid()]
	var fractions: PackedFloat32Array=game.get_world_3d().direct_space_state.cast_motion(query)
	var ray := PhysicsRayQueryParameters3D.create(start,start+delta,5,[game.airship.get_rid()])
	var hit := game.get_world_3d().direct_space_state.intersect_ray(ray)
	var clear := camera_clear(start) and camera_clear(start+delta) and fractions.size()==2 and fractions[0]>=1.0 and hit.is_empty()
	var result := {"reference":reference,"label":label,"required":required,"passed":clear,"start":str(start),"end":str(start+delta),"delta":str(delta),"safe_fraction":fractions[0] if fractions.size()>0 else -1,"collider":str(hit.collider.get_path()) if not hit.is_empty() else "none","scope":"Camera sphere/ray only, not complete physical airship flight"}
	movement_checks.append(result)
	return result
func move_and_capture(reference: String, delta: Vector3, label: String) -> bool:
	var probe := motion_probe(reference,delta,label,false)
	if not probe.passed: return false
	var original: Transform3D=game.camera.global_transform
	# Traverse the tested segment across frames; retain the original reference pose.
	for step in range(1,13):
		game.camera.global_position=original.origin+delta*float(step)/12.0
		await process_frame
	await capture("reference-"+reference+"-"+label,reference,true)
	game.camera.global_transform=original
	return true
func observations() -> void:
	root.add_child(game)
	game.sound_enabled=false;game.test_frozen=true
	var weather: Node3D=game.get_node("Weather42b")
	weather.time_scale=0.0
	await frames(30)
	await RenderingServer.frame_post_draw
	runtime_cache_checks()
	var world_id: int=game.world.get_instance_id()
	for reference in ["1128","1129","1275","1276"]:
		game.observe_reference(reference)
		weather.seek_time(0.0);weather.seek_time(.35)
		await frames(30)
		await RenderingServer.frame_post_draw
		await physics_frame
		var original: Transform3D=game.camera.global_transform
		await capture("reference-"+reference,reference)
		if reference in ["1128","1129"]:
			var expected := Vector3(1150,10,-1000) if reference=="1128" else Vector3(1300,7,-950)
			var fov := 64.0 if reference=="1128" else 66.0
			check(game.camera.global_position.is_equal_approx(expected) and is_equal_approx(game.camera.fov,fov),"Original fixed lake camera retained "+reference)
			game.camera.rotate_y(deg_to_rad(55))
			await capture("reference-"+reference+"-side",reference,true)
			game.camera.global_transform=original
			game.camera.rotate_y(PI)
			await capture("reference-"+reference+"-back",reference,true)
			game.camera.global_transform=original
			# Retain original +350m outcome, even when an alternative is clear.
			var original_probe := motion_probe(reference,game.camera.global_basis.x*350.0,"original-plus350m",true)
			if original_probe.passed: await move_and_capture(reference,game.camera.global_basis.x*350.0,"original-plus350m-clear")
			else:
				for distance in [150.0,-150.0,75.0,-75.0,30.0,-30.0]:
					if await move_and_capture(reference,game.camera.global_basis.x*distance,"supplemental-lateral-%s%dm" % ["plus" if distance>0 else "minus",absi(int(distance))]): break
			await move_and_capture(reference,-game.camera.global_basis.z*200.0,"supplemental-lake-approach200m")
			game.camera.global_transform=original
		check(game.world.get_instance_id()==world_id,"Same physical world retained "+reference)
	# Explicit supplementary inspection; never substitutes for either reference.
	game.observe_reference("1128");weather.seek_time(0.0);weather.seek_time(.35)
	game.camera.global_position=Vector3(1150,800,-1550)
	game.camera.look_at(Vector3(1150,0,-1551));game.camera.fov=70
	await frames(30)
	await capture("lake-supplemental-overhead","1128",true)
	game.camera.global_position=Vector3(1150,2,-1080)
	game.camera.look_at(Vector3(1110,0,-1800));game.camera.fov=64
	await capture("lake-supplemental-low-water","1128",true)
func finish() -> void:
	var passed := failures.is_empty()
	for row in checks: passed=passed and row.passed
	var adapter := RenderingServer.get_video_adapter_name()
	var report := {"passed":passed,"baseline_render":baseline,"static_only":static_only,"candidate":TARGET,"candidate_sha256":FileAccess.get_sha256(TARGET),"render_scene":BASE if baseline else TARGET,"render_scene_sha256":scene_sha,"unaffected_fingerprint":unchanged_fingerprint,"weather":saved_weather,"checks":checks,"failures":failures,"geometry_samples":geometry_samples,"movement_checks":movement_checks,"captures":captures,"renderer":adapter,"software_renderer":"llvmpipe" in adapter.to_lower() or "softpipe" in adapter.to_lower(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"complete_flight_passed":false,"scope":"Fresh saved-scene canonical47 scope and 48000-float weather comparison; all 500 scatter transform/cache check; real live terrain_samples checked against native mesh with intended Y0 clamp. Unchanged original 1128/1129 and nearby 1275/1276 cameras plus separately named side/back/lateral/shore/overhead/low-water diagnostics. Camera movement does not certify full airship collision or visual/reference acceptance."}
	if not output.is_empty():
		var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null: file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game): game.queue_free();game=null
	await frames(8)
	print("LAKE48 VERIFICATION COMPLETE ",passed)
	quit(0 if passed else 1)
func run() -> void:
	if not require(DisplayServer.get_name()!="headless","Lake verification requires a real renderer; --check-only parses only"):
		quit(2);return
	if not require(not output.is_empty() and output.is_absolute_path() and not DirAccess.dir_exists_absolute(output),"New absolute --output-dir required",output): quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	diagnostic_dir=output
	if not require(FileAccess.file_exists(BASE) and FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.file_exists(TARGET),"Missing candidate or baseline SHA mismatch") or not load_payload(): await finish();return
	var source: Node3D=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	var candidate: Node3D=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	await settle()
	if not preflight(source,true) or not preflight(candidate,false) or not verify_payload_result(candidate): source.free();candidate.free();await finish();return
	baseline_snapshot=snapshot(source)
	var control := snapshot(source)
	check(baseline_snapshot==control,"Canonical47 unmodified double-snapshot control")
	var candidate_snapshot := snapshot(candidate)
	check(baseline_snapshot==candidate_snapshot,"Fresh candidate equals canonical47 outside exact permitted edits",differences(baseline_snapshot,candidate_snapshot))
	unchanged_fingerprint=digest(baseline_snapshot)
	saved_weather=weather_state(source)
	check(not saved_weather.is_empty() and saved_weather==weather_state(candidate),"All 48000 saved weather floats unchanged")
	var build_report: Variant=JSON.parse_string(FileAccess.get_file_as_string(DEST+"build-report-48.json"))
	if check(build_report is Dictionary,"Successful build report present"):
		check(build_report.get("passed",false) and build_report.get("candidate_sha256","")==FileAccess.get_sha256(TARGET),"Candidate hash matches successful verified build")
		check(build_report.get("edited_targets",{})==targets_state(candidate),"Saved edited resources match build fingerprints")
		for asset in build_report.get("independent_assets",[]): check(FileAccess.file_exists(asset.path) and FileAccess.get_sha256(asset.path)==asset.sha256,"Independent asset intact "+str(asset.path))
	boundary_checks(source,candidate)
	sample_lake(candidate)
	game=source if baseline else candidate
	if baseline: candidate.free()
	else: source.free()
	scene_sha=FileAccess.get_sha256(BASE if baseline else TARGET)
	if not static_only: await observations()
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(BASE if baseline else TARGET)==scene_sha,"Source scene files unchanged by verification")
	await finish()

extends "res://tools/build_cloud_lake49.gd"
## Independent saved-geometry and A/B live-motion verification. Inherited original
## +350m failure is retained; limited geometry pass NEVER becomes total acceptance.
var game: Node3D
var output := ""
var static_only := false
var phase := ""
var checks := []
var captures := []
var movement_checks := []
var root_checks := []
var tree_checks := []
var unchanged_fingerprint := ""
var saved_weather := {}
var motion_regressions := []
var baseline_motions := {}
var baseline_camera_checks := {}
var candidate_scene_sha := ""
var bed_bvh := {}
var bed_inventory := {}

func _initialize() -> void:
	parse_arguments()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
		if arg=="--static-only": static_only=true
	call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await process_frame
func check(ok: bool, label: String, evidence: Variant=null) -> bool:
	checks.append({"passed":ok,"name":label,"evidence":evidence})
	print("PASS " if ok else "FAIL ",label)
	return ok
func world_faces(node: MeshInstance3D) -> PackedVector3Array:
	var faces := node.mesh.get_faces()
	var transform := world_transform(node)
	for i in range(faces.size()): faces[i]=transform*faces[i]
	return faces
func point_key(point: Vector3) -> String:
	return "%.5f,%.5f,%.5f" % [point.x,point.y,point.z]
func closed_root(faces: PackedVector3Array) -> Dictionary:
	var edges := {}
	var vertices := {}
	var volume := 0.0
	var volume_origin := faces[0] if not faces.is_empty() else Vector3.ZERO
	var degenerate := 0
	for i in range(0,faces.size(),3):
		var a := faces[i];var b := faces[i+1];var c := faces[i+2]
		if (c-a).cross(b-a).length_squared()<.00000000000001: degenerate+=1
		volume+=(a-volume_origin).dot((b-volume_origin).cross(c-volume_origin))/6.0
		var names := [point_key(a),point_key(b),point_key(c)]
		for name in names: vertices[name]=true
		for j in range(3):
			var edge: Array=[names[j],names[(j+1)%3]]
			edge.sort()
			var key: String=edge[0]+"|"+edge[1]
			edges[key]=int(edges.get(key,0))+1
	var bad := []
	for edge in edges:
		if edges[edge]!=2: bad.append({"edge":edge,"uses":edges[edge]})
	return {"closed_two_manifold_edges":bad.is_empty(),"boundary_or_nonmanifold_edges":bad,"vertex_count":vertices.size(),"triangle_count":faces.size()/3,"signed_clockwise_volume_m3":volume,"degenerate_triangles":degenerate,"passed":bad.is_empty() and degenerate==0 and volume< -1.0}
func triangle_rows(faces: PackedVector3Array) -> Array:
	var rows := []
	for i in range(0,faces.size(),3):
		var a := faces[i];var b := faces[i+1];var c := faces[i+2]
		rows.append({"a":a,"b":b,"c":c,"bounds":Vector4(minf(a.x,minf(b.x,c.x)),minf(a.z,minf(b.z,c.z)),maxf(a.x,maxf(b.x,c.x)),maxf(a.z,maxf(b.z,c.z))),"center":(a+b+c)/3.0})
	return rows
func bvh_build(rows: Array) -> Dictionary:
	if rows.is_empty(): return {}
	var bounds: Vector4=rows[0].bounds
	for row in rows:
		bounds=Vector4(minf(bounds.x,row.bounds.x),minf(bounds.y,row.bounds.y),maxf(bounds.z,row.bounds.z),maxf(bounds.w,row.bounds.w))
	if rows.size()<=12: return {"bounds":bounds,"triangles":rows}
	var axis := 0 if bounds.z-bounds.x>=bounds.w-bounds.y else 2
	rows.sort_custom(func(a: Variant,b: Variant) -> bool: return a.center[axis]<b.center[axis])
	var middle := rows.size()/2
	return {"bounds":bounds,"left":bvh_build(rows.slice(0,middle)),"right":bvh_build(rows.slice(middle))}
func bvh_height(tree: Dictionary, point: Vector3) -> float:
	if tree.is_empty(): return -INF
	var bounds: Vector4=tree.bounds
	if point.x<bounds.x-.001 or point.x>bounds.z+.001 or point.z<bounds.y-.001 or point.z>bounds.w+.001: return -INF
	if not tree.has("triangles"): return maxf(bvh_height(tree.left,point),bvh_height(tree.right,point))
	var top := -INF
	for triangle in tree.triangles:
		var a: Vector3=triangle.a;var b: Vector3=triangle.b;var c: Vector3=triangle.c
		var denominator := (b.z-c.z)*(a.x-c.x)+(c.x-b.x)*(a.z-c.z)
		if absf(denominator)<.00000001: continue
		var wa := ((b.z-c.z)*(point.x-c.x)+(c.x-b.x)*(point.z-c.z))/denominator
		var wb := ((c.z-a.z)*(point.x-c.x)+(a.x-c.x)*(point.z-c.z))/denominator
		var wc := 1.0-wa-wb
		if minf(wa,minf(wb,wc))>=-.00001: top=maxf(top,a.y*wa+b.y*wb+c.y*wc)
	return top
func prepare_bed_bvh(scene: Node3D) -> void:
	var rows := []
	var paths: Array=BED_PATHS.duplicate()
	for node in scene.get_node("World/Mountains").find_children("*","MeshInstance3D",true,false): paths.append(str(scene.get_path_to(node)))
	for path in paths:
		var faces := world_faces(scene.get_node(path))
		var selected := PackedVector3Array()
		for i in range(0,faces.size(),3):
			var a := faces[i];var b := faces[i+1];var c := faces[i+2]
			if maxf(a.x,maxf(b.x,c.x))<760 or minf(a.x,minf(b.x,c.x))>1550 or maxf(a.z,maxf(b.z,c.z))< -2220 or minf(a.z,minf(b.z,c.z))> -1000: continue
			selected.append(a);selected.append(b);selected.append(c)
		if not selected.is_empty():
			rows.append_array(triangle_rows(selected))
			bed_inventory[path]={"saved_triangle_count":faces.size()/3,"relevant_triangle_count":selected.size()/3,"world_faces_sha256":digest(faces)}
	bed_bvh=bvh_build(rows)
	check(not bed_bvh.is_empty(),"Independent BVH uses actual saved Game48 lakebed and intersecting mountain triangles",bed_inventory)
func geometry_checks(scene: Node3D) -> void:
	prepare_bed_bvh(scene)
	for island in payload.islands:
		var root_path := ""
		for entry in island.meshes:
			if str(entry.get("role","")).replace("_","")=="rockroot": root_path=mesh_path(island.name,entry.name)
		var node: MeshInstance3D=scene.get_node(root_path)
		var faces := world_faces(node)
		var root_info := closed_root(faces)
		root_info.island=island.name
		root_info.path=root_path
		root_info.world_faces_sha256=digest(faces)
		check(root_info.passed,"Actual saved closed clockwise rockroot "+island.name,root_info)
		var vertices := {}
		for point in faces: vertices[point_key(point)]=point
		var burial_checks := []
		for sample in island.bedroot_samples:
			var point := v3(sample.world)
			var nearest := INF
			for vertex in vertices.values(): nearest=minf(nearest,point.distance_to(vertex))
			var bed := bvh_height(bed_bvh,point)
			var burial := bed-point.y if is_finite(bed) else -INF
			var ok := nearest<.002 and is_finite(bed) and burial>=.15
			var row := {"root_vertex_world":[point.x,point.y,point.z],"actual_saved_root_nearest_vertex_m":nearest,"actual_saved_bed_bvh_y":bed if is_finite(bed) else null,"actual_burial_m":burial if is_finite(burial) else null,"authored_bed_y":sample.get("actual_bed_y"),"authored_burial_m":sample.get("burial_m"),"passed":ok}
			burial_checks.append(row)
			check(ok,"Actual rockroot extends below existing saved lakebed "+island.name,row)
		root_info.bedroot_checks=burial_checks
		root_checks.append(root_info)
		for tree in island.trees:
			var foot := v3(tree.foot_world)
			var support: MeshInstance3D=scene.get_node(mesh_path(island.name,tree.support_mesh))
			var support_bvh := bvh_build(triangle_rows(world_faces(support)))
			var top := bvh_height(support_bvh,foot)
			var trunk_name := str(tree.get("trunk_mesh",""))
			if trunk_name.is_empty():
				for entry in island.meshes:
					if str(entry.name).contains(str(tree.name)) and str(entry.get("role","")).contains("trunk"): trunk_name=entry.name
			var trunk := scene.get_node_or_null(mesh_path(island.name,trunk_name)) as MeshInstance3D
			var actual_base := INF
			var nearest_axis := INF
			var bottom_points := []
			if trunk!=null:
				var trunk_faces := world_faces(trunk)
				for point in trunk_faces: actual_base=minf(actual_base,point.y)
				var seen := {}
				for point in trunk_faces:
					if point.y<=actual_base+.003 and not seen.has(point_key(point)):
						seen[point_key(point)]=true
						nearest_axis=minf(nearest_axis,Vector2(point.x-foot.x,point.z-foot.z).length())
						var beneath := bvh_height(support_bvh,point)
						bottom_points.append({"world":[point.x,point.y,point.z],"support_y":beneath if is_finite(beneath) else null,"vertical_gap_m":point.y-beneath if is_finite(beneath) else null})
			var base_supported := not bottom_points.is_empty()
			for point in bottom_points: base_supported=base_supported and point.support_y!=null and absf(float(point.vertical_gap_m))<=.8
			var ok := is_finite(top) and absf(foot.y-top)<=.2 and trunk!=null and absf(actual_base-foot.y)<=.8 and nearest_axis<3.0 and base_supported
			var row := {"island":island.name,"tree":tree.name,"foot_world":tree.foot_world,"support_mesh":str(scene.get_path_to(support)),"saved_support_bvh_height":top if is_finite(top) else null,"actual_trunk_mesh":trunk_name,"actual_trunk_base_y":actual_base if is_finite(actual_base) else null,"bottom_ring_support":bottom_points,"passed":ok}
			tree_checks.append(row)
			check(ok,"Modeled pine actual trunk base supported by saved mesh BVH "+tree.name,row)
	check(tree_checks.size()==7,"Exactly seven independently checked modeled pines",tree_checks.size())

const SCATTER_COUNTS := {"oak_1_-2":48,"poplar_1_-2":20,"bush_1_-2":17,"rock_1_-2":26,"oak_1_-3":227,"poplar_1_-3":94,"pine_1_-3":2,"bush_1_-3":23,"rock_1_-3":43}
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
func runtime_cache_checks() -> void:
	var world: Node3D=game.get_node("World")
	for path in BED_PATHS:
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
	query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,position)
	query.collision_mask=5;query.exclude=[game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
func capture(label: String, reference: String, supplemental := false, require_clear := true) -> void:
	await frames(3)
	await physics_frame
	await RenderingServer.frame_post_draw
	var path := output.path_join(phase+"--"+label+".png")
	var image: Image=root.get_texture().get_image()
	var clear := camera_clear(game.camera.global_position)
	check(image.save_png(path)==OK,"Actual rendered capture "+phase+"/"+label)
	if require_clear: check(clear,"Camera collision-free "+phase+"/"+label)
	if phase=="baseline48": baseline_camera_checks[label]=clear
	elif baseline_camera_checks.has(label):
		check(not baseline_camera_checks[label] or clear,"No extra camera obstruction versus Game48 "+label)
	captures.append({"phase":phase,"name":label,"path":path,"sha256":FileAccess.get_sha256(path),"reference":reference,"supplemental":supplemental,"camera_transform":str(game.camera.global_transform),"fov":game.camera.fov,"camera_clear":clear,"pixels":[image.get_width(),image.get_height()],"world_instance":game.world.get_instance_id(),"weather_time":game.get_node("Weather42b").time_seconds})
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
	var start_clear := camera_clear(start)
	var end_clear := camera_clear(start+delta)
	var clear := start_clear and end_clear and fractions.size()==2 and fractions[0]>=1.0 and hit.is_empty()
	var collider := str(game.get_path_to(hit.collider)) if not hit.is_empty() else "none"
	var result := {"phase":phase,"reference":reference,"label":label,"required":required,"passed":clear,"start":str(start),"end":str(start+delta),"delta":str(delta),"start_clear":start_clear,"end_clear":end_clear,"safe_fraction":fractions[0] if fractions.size()>0 else -1,"collider":collider,"scope":"Camera sphere/ray only; not complete physical airship flight"}
	var key := reference+"/"+label
	if phase=="baseline48": baseline_motions[key]=result.duplicate(true)
	else:
		var prior: Dictionary=baseline_motions.get(key,{})
		result.baseline_passed=prior.get("passed",false)
		result.baseline_safe_fraction=prior.get("safe_fraction",null)
		result.known_inherited_failure=not clear and not prior.get("passed",true) and collider==prior.get("collider","")
		result.new_regression=prior.is_empty() or (prior.get("passed",false) and not clear) or float(result.safe_fraction)<float(prior.get("safe_fraction",0.0))-.0001
		if result.new_regression: motion_regressions.append(result.duplicate(true))
		check(not result.new_regression,"No new obstruction on unchanged "+key,result)
		if label in ["protected-plus150m","protected-approach200m"]:
			check(prior.get("passed",false) and clear,"Previously clear protected motion remains clear "+key,result)
	movement_checks.append(result)
	return result
func traverse_and_capture(reference: String, delta: Vector3, label: String, probe: Dictionary) -> void:
	if not probe.passed: return
	var original: Transform3D=game.camera.global_transform
	for step in range(1,13):
		game.camera.global_position=original.origin+delta*float(step)/12.0
		await process_frame
	await capture("reference-"+reference+"-"+label,reference,true)
	game.camera.global_transform=original
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
			check(game.camera.global_position.is_equal_approx(expected) and is_equal_approx(game.camera.fov,fov),"Original fixed lake camera retained "+phase+"/"+reference)
			game.camera.rotate_y(deg_to_rad(55))
			await capture("reference-"+reference+"-side",reference,true)
			game.camera.global_transform=original
			game.camera.rotate_y(PI)
			await capture("reference-"+reference+"-back",reference,true)
			game.camera.global_transform=original
			# Always probe the SAME required +350m, plus the known-clear 150/200m.
			# No shortening, shifted route or fallback can turn its failure into pass.
			for motion in [["original-plus350m",game.camera.global_basis.x*350.0,true],["protected-plus150m",game.camera.global_basis.x*150.0,false],["protected-approach200m",-game.camera.global_basis.z*200.0,false]]:
				var probe := motion_probe(reference,motion[1],motion[0],motion[2])
				await traverse_and_capture(reference,motion[1],motion[0],probe)
			game.camera.global_transform=original
		check(game.world.get_instance_id()==world_id,"Same physical world retained "+phase+"/"+reference)
	game.observe_reference("1128");weather.seek_time(0.0);weather.seek_time(.35)
	game.camera.global_position=Vector3(1150,800,-1550)
	game.camera.look_at(Vector3(1150,0,-1551));game.camera.fov=70
	await frames(30)
	await capture("lake-supplemental-overhead","1128",true)
	if phase=="candidate49":
		check(group_inventory(game)==expected_inventory,"All new mesh/collider nodes remain in runtime tree")
		# New islands get their own explicitly supplementary nearshore and orbit views.
		for camera in payload.get("nearshore_cameras",[]):
			if not finite_values(camera.get("position"),3) or not finite_values(camera.get("target"),3):
				check(false,"Invalid authored supplementary camera",camera);continue
			game.camera.global_position=v3(camera.position)
			game.camera.look_at(v3(camera.target));game.camera.fov=float(camera.get("fov",64))
			await capture("new-"+str(camera.name),"1128",true)
		for island in payload.islands:
			var center := v3(island.anchor)+Vector3(0,4,0)
			var radius := 95.0 if island.name!="foreground_rock" else 34.0
			for side in [["east",Vector3(radius,27,0)],["back",Vector3(0,22,-radius)],["west",Vector3(-radius,25,0)]]:
				game.camera.global_position=center+side[1]
				game.camera.look_at(center);game.camera.fov=60
				await capture("new-"+island.name+"-orbit-"+side[0],"1128",true)
func finish() -> void:
	var static_pass := failures.is_empty()
	for row in checks: static_pass=static_pass and row.passed
	var limited_pass := static_pass and not static_only
	var required_count := 0
	var requested_pass := not static_only
	var inherited_failures := []
	for row in movement_checks:
		if row.phase!="candidate49": continue
		if row.required:
			required_count+=1
			requested_pass=requested_pass and row.passed
		if row.get("known_inherited_failure",false): inherited_failures.append(row)
	requested_pass=requested_pass and required_count==2
	var adapter := RenderingServer.get_video_adapter_name()
	var report := {"static_saved_geometry_passed":static_pass,"limited_geometry_runtime_passed":limited_pass,"requested_motion_all_passed":requested_pass,"total_acceptance_passed":false,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":candidate_scene_sha,"static_only":static_only,"unaffected_fingerprint":unchanged_fingerprint,"weather":saved_weather,"checks":checks,"failures":failures,"closed_root_and_burial_checks":root_checks,"tree_base_bvh_checks":tree_checks,"lakebed_bvh_source_inventory":bed_inventory,"movement_checks":movement_checks,"known_baseline_motion_failures":inherited_failures,"new_motion_regressions":motion_regressions,"no_new_motion_regression":not static_only and motion_regressions.is_empty() and movement_checks.size()==12,"captures":captures,"renderer":adapter,"software_renderer":"llvmpipe" in adapter.to_lower() or "softpipe" in adapter.to_lower(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"complete_flight_passed":false,"exit_code_scope":"0 means limited geometry/runtime verification only. Inspect requested_motion_all_passed and total_acceptance_passed independently.","scope":"Independent saved-scene canonical47 full old Game48 state, exact weather48000 and 500 scatter transforms/runtime cache. Actual saved source triangles/colliders compared; closed roots and actual lakebed burial; seven pine bases independently queried using BVH of saved support triangles. Baseline48 and candidate49 exact reference cameras and required350/protected150/200m paths compared in one fresh process. Required inherited350 failures remain failures. Additional nearshore/orbit images cannot replace fixed reference acceptance. Total visual/full-world/full-airship acceptance remains false."}
	if not output.is_empty():
		var file := FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null: file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game):
		await settle()
		game.queue_free();game=null
	await frames(8)
	print("LAKE49 VERIFICATION limited_geometry_runtime_passed=",limited_pass," requested_motion_all_passed=",requested_pass," total_acceptance_passed=false")
	quit(0 if (limited_pass or (static_only and static_pass)) else 1)
func run() -> void:
	if not require(DisplayServer.get_name()!="headless","Lake verification requires real renderer; --check-only is parse only"):
		quit(2);return
	if not require(not output.is_empty() and output.is_absolute_path() and not DirAccess.dir_exists_absolute(output),"New absolute --output-dir required",output): quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	diagnostic_dir=output
	if not require(FileAccess.file_exists(BASE) and FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.file_exists(TARGET),"Missing candidate or changed baseline") or not load_payload(): await finish();return
	candidate_scene_sha=FileAccess.get_sha256(TARGET)
	var source_packed: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var candidate_packed: PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var source: Node3D=source_packed.instantiate()
	var candidate: Node3D=candidate_packed.instantiate()
	await settle()
	if not verify_payload_result(candidate): source.free();candidate.free();await finish();return
	var before := graph_state(source,source_packed)
	check(before==graph_state(source,source_packed),"Canonical47 unmodified full Game48 graph double-snapshot control")
	var after := graph_state(candidate,candidate_packed)
	check(before==after,"Fresh saved candidate49 retains exact full Game48 graph outside new group",differences(before,after))
	unchanged_fingerprint=digest(before)
	saved_weather=weather_state(source)
	check(not saved_weather.is_empty() and saved_weather==weather_state(candidate),"All48000 saved weather floats unchanged")
	var report: Variant=JSON.parse_string(FileAccess.get_file_as_string(DEST+"build-report-49.json"))
	if check(report is Dictionary,"Successful49 build report present"):
		check(report.get("build_saved_reload_passed",false) and report.get("candidate_sha256","")==candidate_scene_sha,"Candidate hash matches verified49 build")
		check(report.get("unaffected_fingerprint","")==unchanged_fingerprint,"Build and independent verifier agree on unchanged Game48 raw canonical fingerprint")
		check(report.get("new_group_fingerprint","")==digest(target_state(candidate)),"Saved new-group resources match build fingerprints")
		for asset in report.get("independent_assets",[]): check(FileAccess.file_exists(asset.path) and FileAccess.get_sha256(asset.path)==asset.sha256,"Independent new asset intact "+str(asset.path))
		for source_link in report.get("source_files",[]): check(FileAccess.file_exists(source_link.absolute_path) and FileAccess.get_sha256(source_link.absolute_path)==source_link.sha256,"Linked Blender/GLB source unchanged "+str(source_link.source_link))
	geometry_checks(candidate)
	if static_only:
		source.free();game=candidate
	else:
		phase="baseline48";game=source
		await observations()
		await settle()
		game.queue_free();game=null
		await frames(8)
		phase="candidate49";game=candidate
		await observations()
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(TARGET)==candidate_scene_sha,"Both source scene files remain unchanged after verification")
	await finish()

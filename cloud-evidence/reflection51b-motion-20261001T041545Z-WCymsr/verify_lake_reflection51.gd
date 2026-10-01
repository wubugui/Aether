extends "res://tools/build_lake_reflection51.gd"
## Saved51off verifier. Whole ready-material A/B/A, clip-only main/shadow gate,
## then real shared-World3D reflection texture and reversible motion diagnostics.
const FROZEN_TIME := 0.35
var game: Node3D
var output := ""
var checks := []
var captures := []
var comparisons := []
var movement_checks := []
var live_rows := {}
var material_pairs := {}
var stored_rows := []
var source_ocean: ShaderMaterial
var new_ocean: ShaderMaterial
var controller: Node3D
var depth_controller: Node3D
var original_camera_mask := 0
var original_ocean_layers := 0
var candidate_camera_mask := 0
var candidate_sha := ""
var unchanged_fingerprint := ""
var normal_pass := false
var clip_only_pass := false
var reflection_checks := []
var freeze_evidence := {}
var baseline_motions := {}
var mode_history := []
var build_report := {}
var normal_only := false
var uniform_sync_ledger := []
var current_reference := ""
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
		if arg=="--normal-only": normal_only=true
	call_deferred("run")
func frames(count: int) -> void:
	for i in range(count): await process_frame
func check(ok: bool,label: String,evidence: Variant=null) -> bool:
	checks.append({"passed":ok,"name":label,"evidence":evidence})
	print("PASS " if ok else "FAIL ",label)
	return ok
func freeze_tree(node: Node) -> void:
	node.set_process(false);node.set_physics_process(false)
	node.set_process_input(false);node.set_process_unhandled_input(false);node.set_process_unhandled_key_input(false)
	if node is AnimationPlayer: node.pause()
	if node is Timer: node.paused=true
	for child in node.get_children(): freeze_tree(child)
func collision_activity(scene: Node) -> Dictionary:
	var data := {}
	for node in scene.find_children("*","CollisionObject3D",true,false):
		data[str(scene.get_path_to(node))]=[node.process_mode,node.disable_mode,node.can_process(),node.collision_layer,node.collision_mask,str(node.get_rid())]
	return data
func camera_clear(position: Vector3) -> bool:
	var sphere := SphereShape3D.new();sphere.radius=maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape=sphere;query.transform=Transform3D(Basis.IDENTITY,position);query.collision_mask=5;query.exclude=[game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
func pair_for(material: Material) -> Dictionary:
	if material==null: return {}
	return material_pairs.get(material.resource_path,{})
func prepare_pairs(source: Node) -> bool:
	var source_by_key := {}
	for spec in binding_specs: source_by_key[spec.path+"|"+spec.property]=spec
	for row in build_report.binding_ledger:
		var key: String=row.path+"|"+row.property
		if not check(source_by_key.has(key),"Original binding source exists "+key): return false
		var spec: Dictionary=source_by_key[key]
		var old: Material=spec.source_material
		var current: ShaderMaterial=game.get_node(row.path).get(row.property)
		if not check(current!=null and current.resource_path==row.new_material_path and digest(canonical(old))==row.source_material_fingerprint,"Exact old/new material mapping "+key): return false
		if not material_pairs.has(current.resource_path): material_pairs[current.resource_path]={"original":old,"converted":current}
		stored_rows.append({"path":row.path,"property":row.property,"original":old,"converted":current})
	source_ocean=source.get_node("World/Ocean").material_override.duplicate(false)
	new_ocean=game.get_node("World/Ocean").material_override
	return check(material_pairs.size()==114,"Exact114 original/converted material pairs available for whole-world controls")
func register_live_row(path: String,property: String,material: Material) -> void:
	var pair := pair_for(material)
	if pair.is_empty(): return
	live_rows[path+"|"+property]={"path":path,"property":property,"original":pair.original,"converted":material}
func collect_ready_bindings() -> bool:
	live_rows.clear()
	for node in game.find_children("*","GeometryInstance3D",true,false):
		var path := str(game.get_path_to(node))
		if node.material_override!=null: register_live_row(path,"material_override",node.material_override)
		if node is MeshInstance3D and node.mesh!=null:
			for surface in range(node.mesh.get_surface_count()):
				var material: Material=node.get_surface_override_material(surface)
				if material!=null: register_live_row(path,"surface_material_override/"+str(surface),material)
	var failures_here := []
	var present := 0
	var generated_present := 0
	for entry in runtime_scope:
		var node := game.get_node_or_null(entry.path)
		if node==null:
			if not entry.runtime_generated: failures_here.append({"path":entry.path,"error":"missing persisted target"})
			continue
		present+=1
		if entry.runtime_generated: generated_present+=1
		var materials := []
		if node is MeshInstance3D:
			for surface in range(node.mesh.get_surface_count()): materials.append(node.get_active_material(surface))
		elif node is MultiMeshInstance3D:
			for surface in range(node.multimesh.mesh.get_surface_count()): materials.append(node.material_override if node.material_override!=null else node.multimesh.mesh.surface_get_material(surface))
		for material in materials:
			if pair_for(material).is_empty(): failures_here.append({"path":entry.path,"error":"ready active material not one of exact114 copies","material":material.resource_path if material!=null else "null"})
	return check(failures_here.is_empty() and present>=308,"Every persisted scoped ready node uses expected converted material; invisible Rain/Snow included",{"present":present,"planned_generated_present":generated_present,"actual_live_binding_count":live_rows.size(),"failures":failures_here})
func sync_original_uniforms() -> bool:
	var ok := true
	var count := 0
	for path in material_pairs:
		var pair: Dictionary=material_pairs[path]
		var original: Material=pair.original
		var current: ShaderMaterial=pair.converted
		if original is ShaderMaterial:
			for uniform in original.shader.get_shader_uniform_list():
				var name: String=uniform.name
				original.set_shader_parameter(name,current.get_shader_parameter(name));count+=1
				ok=ok and canonical(original.get_shader_parameter(name))==canonical(current.get_shader_parameter(name))
		else: ok=ok and current.get_shader_parameter("albedo")==original.albedo_color
		var row := {"reference":current_reference,"converted_material":path,"original_class":original.get_class(),"next_pass_null":original.next_pass==null,"uniforms":[]}
		if original is ShaderMaterial:
			for uniform in original.shader.get_shader_uniform_list():
				var name: String=uniform.name
				row.uniforms.append({"name":name,"original":canonical(original.get_shader_parameter(name)),"converted":canonical(current.get_shader_parameter(name)),"equal":canonical(original.get_shader_parameter(name))==canonical(current.get_shader_parameter(name))})
		else: row.native_albedo_equal=current.get_shader_parameter("albedo")==original.albedo_color
		uniform_sync_ledger.append(row)
	var ocean_row := {"reference":current_reference,"converted_material":new_ocean.resource_path,"original_class":"ShaderMaterial","uniforms":[]}
	for uniform in source_ocean.shader.get_shader_uniform_list():
		var name: String=uniform.name
		source_ocean.set_shader_parameter(name,new_ocean.get_shader_parameter(name));count+=1
		var old_value: Variant=canonical(source_ocean.get_shader_parameter(name))
		var new_value: Variant=canonical(new_ocean.get_shader_parameter(name))
		ok=ok and old_value==new_value
		ocean_row.uniforms.append({"name":name,"original":old_value,"converted":new_value,"equal":old_value==new_value})
	uniform_sync_ledger.append(ocean_row)
	return check(ok,"All original runtime shader uniforms and native albedos synchronized before full-binding A/B/A",{"copied_uniform_values":count,"material_pairs":material_pairs.size()})
func apply_bindings(original: bool) -> void:
	controller.set_effect_flags(false,false)
	for row in stored_rows:
		var node := game.get_node_or_null(row.path)
		if node!=null: node.set(row.property,row.original if original else row.converted)
	for row in live_rows.values():
		var node := game.get_node_or_null(row.path)
		if node!=null: node.set(row.property,row.original if original else row.converted)
	game.get_node("World/Ocean").material_override=source_ocean if original else new_ocean
	# The retained50 controller must point at the currently active Ocean material.
	depth_controller.water=game.get_node("World/Ocean").material_override
	depth_controller.set_depth_enabled(false)
	var texture_cache_ok: bool=depth_controller.water==game.get_node("World/Ocean").material_override and depth_controller.textures.size()==5
	for index in range(depth_controller.textures.size()):
		var uniform_name := "lake50_height" if index==0 else "lake50_patch"+str(index-1)
		texture_cache_ok=texture_cache_ok and depth_controller.water.get_shader_parameter(uniform_name)==depth_controller.textures[index]
	check(texture_cache_ok,"Retained50 water cache targets current Ocean and all five identical textures",{"original_mode":original})
	game.get_node("World/Ocean").layers=original_ocean_layers if original else WATER_LAYER
	game.camera.cull_mask=original_camera_mask if original else candidate_camera_mask
	controller.refresh_now()
	mode_history.append({"original_bindings":original,"saved_authority_and_direct_fields":stored_rows.size(),"ready_geometry_fields":live_rows.size(),"camera_mask":game.camera.cull_mask,"ocean_layers":game.get_node("World/Ocean").layers})
func original_parameter_state() -> Dictionary:
	resource_cache.clear()
	var result := {}
	for path in material_pairs:
		var pair: Dictionary=material_pairs[path]
		if pair.original is ShaderMaterial:
			var values := {}
			for uniform in pair.original.shader.get_shader_uniform_list(): values[str(uniform.name)]=canonical(pair.converted.get_shader_parameter(uniform.name))
			result[path]=values
		else: result[path]=canonical(pair.converted.get_shader_parameter("albedo"))
	var water := {}
	for uniform in source_ocean.shader.get_shader_uniform_list(): water[str(uniform.name)]=canonical(new_ocean.get_shader_parameter(uniform.name))
	result["Ocean"]=water
	return result
func shot(label: String,reference: String,reflect_texture := false) -> Image:
	for i in range(4): controller.refresh_now();await process_frame
	await physics_frame;await RenderingServer.frame_post_draw
	var image: Image=controller.viewport.get_texture().get_image() if reflect_texture else root.get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	var path := output.path_join(label+".png")
	check(image.save_png(path)==OK,"Actual rendered "+("reflection texture " if reflect_texture else "main ")+label)
	if not reflect_texture: check(camera_clear(game.camera.global_position),"Live physics camera-clear "+label)
	captures.append({"name":label,"path":path,"sha256":FileAccess.get_sha256(path),"rgba_digest":digest(image.get_data()),"reference":reference,"is_reflection_texture":reflect_texture,"size":[image.get_width(),image.get_height()],"main_camera_transform":str(game.camera.get_camera_transform()),"controller":controller.get_diagnostic_state(),"frozen_world_time":FROZEN_TIME})
	return image
func compare(a: Image,b: Image,label: String,required_equal: bool) -> bool:
	var equal := a.get_size()==b.get_size() and a.get_format()==b.get_format() and a.get_data()==b.get_data()
	comparisons.append({"name":label,"pixel_exact_zero_diff":equal,"required_equal":required_equal,"method":"Full RGBA8 byte equality; no tolerance or masked region"})
	if required_equal: check(equal,"Required whole-image zero-difference "+label)
	return equal
func prepare_view(reference: String) -> bool:
	current_reference=reference
	apply_bindings(false)
	depth_controller.set_depth_enabled(false)
	game.observe_reference(reference)
	var weather: Node3D=game.get_node("Weather42b")
	weather.seek_time(0.0);weather.seek_time(FROZEN_TIME)
	weather._process(0.0)
	RenderingServer.global_shader_parameter_set("world_time",FROZEN_TIME)
	depth_controller.set_depth_enabled(false);controller.set_effect_flags(false,false)
	await frames(5);await physics_frame;await RenderingServer.frame_post_draw
	return collect_ready_bindings() and sync_original_uniforms()
func probe_motion(reference: String,delta: Vector3,label: String,required: bool) -> void:
	var start: Vector3=game.camera.global_position
	var shape := SphereShape3D.new();shape.radius=maxf(.12,game.camera.near)
	var query := PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,start);query.motion=delta;query.collision_mask=5;query.exclude=[game.airship.get_rid()]
	var fractions: PackedFloat32Array=game.get_world_3d().direct_space_state.cast_motion(query)
	var hit := game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,start+delta,5,[game.airship.get_rid()]))
	var clear := camera_clear(start) and camera_clear(start+delta) and fractions.size()==2 and fractions[0]>=1.0 and hit.is_empty()
	var collider := str(game.get_path_to(hit.collider)) if not hit.is_empty() else "none"
	var prior: Dictionary=baseline_motions.get(reference+"/"+label,{})
	var same: bool=not prior.is_empty() and clear==prior.passed and collider==prior.collider and fractions.size()==2 and fractions[0]==float(prior.safe_fraction)
	var row := {"reference":reference,"label":label,"required":required,"passed":clear,"safe_fraction":fractions[0] if fractions.size() else -1,"collider":collider,"known_baseline_failure":not clear and same,"no_new_regression":same,"scope":"Camera sphere/ray only"}
	movement_checks.append(row);check(same,"Exact50 motion result retained "+reference+"/"+label,row)
func normal_controls(reference: String) -> bool:
	if not await prepare_view(reference): return false
	var pose: Transform3D=game.camera.global_transform
	var parameters := original_parameter_state()
	apply_bindings(true)
	var a := await shot(reference+"--A50-all-original-bindings",reference)
	apply_bindings(false)
	var b := await shot(reference+"--B51-all-converted-clip-off-reflection-off",reference)
	apply_bindings(true)
	var a2 := await shot(reference+"--A50-all-original-restored",reference)
	var equal := compare(a,b,reference+"/whole-ready-original-vs-all-converted-off",true)
	equal=compare(a,a2,reference+"/whole-ready-original-A-vs-A2",true) and equal
	if not equal:
		normal_pass=false;clip_only_pass=false;return false
	apply_bindings(false);controller.set_effect_flags(true,false)
	var clip := await shot(reference+"--C51-clip-on-reflection-off",reference)
	var clip_equal := compare(b,clip,reference+"/clip-only-main-and-shadow-no-change",true)
	controller.set_effect_flags(false,false)
	var restored := await shot(reference+"--B51-converted-off-restored",reference)
	clip_equal=compare(b,restored,reference+"/all-converted-off-restored",true) and clip_equal
	check(parameters==original_parameter_state(),"All preexisting shader uniforms/native albedos unchanged across controls "+reference)
	check(game.camera.global_transform==pose,"Primary camera optical pose unchanged across normal controls "+reference)
	if not clip_equal: clip_only_pass=false
	return equal and clip_equal
func check_reflection_state(label: String) -> bool:
	var state: Dictionary=controller.get_diagnostic_state()
	var size: Vector2i=Vector2i(game.camera.get_viewport().get_visible_rect().size)
	var valid: bool=state.get("failure","").is_empty() and state.same_world3d and state.texture_bound and state.reflection_effective and state.ocean_layers==WATER_LAYER and state.water_recursion_excluded and (int(state.primary_cull_mask)&MARKER)==0 and (int(state.reflection_cull_mask)&MARKER)!=0 and controller.viewport.size==size
	for material in controller.clipping_materials:
		valid=valid and material.get_shader_parameter("lake51_reflection_clip_enabled")==true and material.get_shader_parameter("lake51_reflection_plane_y")==0.0
	reflection_checks.append({"name":label,"passed":valid,"state":state,"actual_main_viewport_size":size})
	return check(valid,"Shared-world reflection configuration "+label,state)
func reflection_controls() -> bool:
	for reference in ["1128","1129"]:
		if not await prepare_view(reference): return false
		depth_controller.set_depth_enabled(true)
		controller.set_effect_flags(true,false)
		var off := await shot(reference+"--D51-depth-on-reflection-off",reference)
		controller.set_effect_flags(true,true)
		var on := await shot(reference+"--E51-depth-on-reflection-on",reference)
		var reflected := await shot(reference+"--E51-live-reflection-texture",reference,true)
		check_reflection_state(reference)
		var changed := not compare(off,on,reference+"/reflection-actually-changes-main-water",false)
		check(changed,"Reflection-enabled branch changes rendered water "+reference)
		check(not reflected.is_empty(),"Actual reflected viewport image available "+reference)
		var pose: Transform3D=game.camera.global_transform
		game.camera.rotate_y(deg_to_rad(35))
		controller.refresh_now()
		await shot(reference+"--E51-side-main",reference)
		await shot(reference+"--E51-side-reflection-texture",reference,true)
		game.camera.global_transform=pose;controller.refresh_now()
	# Controlled motion of the existing ship, with full restore, in the SAME world.
	if not await prepare_view("1128"): return false
	depth_controller.set_depth_enabled(true);controller.set_effect_flags(true,true)
	var original_ship: Transform3D=game.airship.global_transform
	var original_camera: Transform3D=game.camera.global_transform
	game.airship.global_position=game.camera.global_position-game.camera.global_basis.z*90.0+Vector3(0,15,0)
	await physics_frame
	var ship_a := await shot("dynamic-ship-A-main","1128")
	var reflection_a := await shot("dynamic-ship-A-reflection","1128",true)
	var staged_ship: Transform3D=game.airship.global_transform
	game.airship.global_position+=Vector3(24,4,-12)
	await physics_frame
	await shot("dynamic-ship-B-moved-main","1128")
	var reflection_b := await shot("dynamic-ship-B-moved-reflection","1128",true)
	check(not compare(reflection_a,reflection_b,"same-world-existing-ship-movement-updates-reflection",false),"Actual existing ship movement changes live reflected pixels")
	game.airship.global_transform=staged_ship
	await physics_frame
	var ship_a2 := await shot("dynamic-ship-A2-restored-main","1128")
	var reflection_a2 := await shot("dynamic-ship-A2-restored-reflection","1128",true)
	compare(ship_a,ship_a2,"staged-ship-main-A-A2",true)
	compare(reflection_a,reflection_a2,"staged-ship-reflection-A-A2",true)
	game.camera.global_position+=game.camera.global_basis.x*30.0
	controller.refresh_now();await physics_frame
	await shot("dynamic-camera-plus30-main","1128")
	var shifted := await shot("dynamic-camera-plus30-reflection","1128",true)
	check(not compare(reflection_a2,shifted,"camera-movement-updates-live-reflection",false),"Actual camera translation changes live reflected pixels")
	game.camera.global_transform=original_camera;game.airship.global_transform=original_ship;controller.refresh_now();await physics_frame
	check(game.camera.global_transform==original_camera and game.airship.global_transform==original_ship,"Supplementary ship/camera test restores every changed transform")
	return true
func observations() -> void:
	root.size=Vector2i(1180,664)
	root.add_child(game);game.sound_enabled=false;game.test_frozen=true
	game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	check(not controller.clip_enabled and not controller.reflection_enabled,"Saved51 diagnostic defaults keep clip/reflection off")
	var before := collision_activity(game);freeze_tree(game);await physics_frame;await physics_frame
	var after := collision_activity(game)
	freeze_evidence={"count":before.size(),"unchanged":before==after,"before_fingerprint":digest(before),"after_fingerprint":digest(after)}
	if not check(before==after and before.size()>0,"Freeze retains active collision modes/layers/RIDs",freeze_evidence): return
	for reference in ["1128","1129"]:
		if not await prepare_view(reference): return
		probe_motion(reference,game.camera.global_basis.x*350.,"original-plus350m",true)
		probe_motion(reference,game.camera.global_basis.x*150.,"protected-plus150m",false)
		probe_motion(reference,-game.camera.global_basis.z*200.,"protected-approach200m",false)
	normal_pass=true;clip_only_pass=true
	var normal_references := ["1128","1129"] if normal_only else ["1128","1129","1343","1342","1341","1275","1344"]
	for reference in normal_references:
		if not await normal_controls(reference):
			print("REFLECTION51 STOP: whole-material normal/clip-only zero-diff gate failed; reflection visuals not accepted")
			return
	if not normal_only: await reflection_controls()
	apply_bindings(false);controller.set_effect_flags(false,false);depth_controller.set_depth_enabled(true)
	check(not controller.clip_enabled and not controller.reflection_enabled and depth_controller.depth_enabled,"Runtime restored to saved51off diagnostic profile")
func finish() -> void:
	var scoped := failures.is_empty()
	for row in checks: scoped=scoped and row.passed
	var requested := movement_checks.size()==6
	for row in movement_checks:
		if row.required: requested=requested and row.passed
	var report := {"scoped_saved_state_runtime_passed":scoped,"normal_pass_zero_diff":normal_pass,"clip_only_zero_diff":clip_only_pass,"requested_motion_all_passed":requested,"total_acceptance_passed":false,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":candidate_sha,"unaffected_graph_fingerprint":unchanged_fingerprint,"checks":checks,"failures":failures,"captures":captures,"comparisons":comparisons,"movement_checks":movement_checks,"freeze_physics":freeze_evidence,"material_pair_count":material_pairs.size(),"stored_binding_count":stored_rows.size(),"latest_ready_binding_count":live_rows.size(),"mode_history":mode_history,"normal_only":normal_only,"uniform_sync_ledger":uniform_sync_ledger,"reflection_checks":reflection_checks,"renderer":RenderingServer.get_video_adapter_name(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"complete_flight_passed":false,"scope":"Fresh saved50-vs51 canonical exact-property scope; same-world full original ready material bindings vs114 official/injected copies with depth/clip/reflection off; clip-only main/shadow zero-diff gate; then true shared-World3D reflection viewport and existing ship/camera motion. Source50/51 and all authoritative assets unchanged. Saved51off remains diagnostic. Required350m inherited failures remain failures."}
	if not output.is_empty():
		var f:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if f!=null:f.store_string(JSON.stringify(report,"  "));f.close()
	if is_instance_valid(game): await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51 VERIFIED scoped=",scoped," normal_zero_diff=",normal_pass," clip_only_zero_diff=",clip_only_pass," required_motion=",requested," total=false")
	quit(0 if scoped and normal_pass and clip_only_pass else 1)
func run() -> void:
	if not require(DisplayServer.get_name()!="headless","51 verifier requires real renderer"): quit(2);return
	if not require(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output),"New absolute output directory required"):quit(2);return
	DirAccess.make_dir_recursive_absolute(output);diagnostic_dir=output
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.file_exists(TARGET),"Source50 SHA mismatch or51 absent"):await finish();return
	candidate_sha=FileAccess.get_sha256(TARGET)
	var source_packed: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var candidate_packed: PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var source: Node3D=source_packed.instantiate();game=candidate_packed.instantiate();await settle()
	if not discover_bindings(source): source.free();await finish();return
	original_camera_mask=source.get_node("Camera").cull_mask;original_ocean_layers=source.get_node("World/Ocean").layers;candidate_camera_mask=game.get_node("Camera").cull_mask
	var before:=graph_state(source,source_packed);var after:=graph_state(game,candidate_packed)
	check(before==graph_state(source,source_packed),"Fresh50 canonical double-snapshot stable")
	check(before==after,"All50 stored state unchanged outside exact51 property whitelist",differences(before,after))
	unchanged_fingerprint=digest(before)
	check(weather_state(source)==weather_state(game),"All48000 saved weather floats remain exact")
	check(verify_new_inventory(game),"Only exact reflection controller/viewport/camera subtree added")
	build_report=JSON.parse_string(FileAccess.get_file_as_string(DEST+"build-report-51.json"))
	check(build_report.get("build_saved_reload_passed",false) and build_report.get("candidate_sha256","")==candidate_sha,"51 hash matches real-renderer saved/reloaded build")
	check(build_report.get("unaffected_graph_fingerprint","")==unchanged_fingerprint and build_report.get("new_state_fingerprint","")==digest(new_state(game)),"Independent verifier matches all build state fingerprints")
	check(build_report.exact_property_masks==property_masks,"Exact node/property whitelist independently reproduced")
	for asset in build_report.asset_inventory: check(FileAccess.get_sha256(asset.path)==asset.sha256,"Independent51 asset retained "+str(asset.path))
	check(FileAccess.get_sha256(CONTROLLER)==build_report.controller_script_sha256,"51 controller source unchanged")
	if not prepare_pairs(source): source.free();await finish();return
	var previous: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/cloud-evidence/depth50-verify-v2-20261001T010738Z-G3enLm/images/report.json"))
	check(previous.get("candidate_sha256","")==BASE_SHA,"Baseline motion evidence belongs to exact50")
	for row in previous.movement_checks: baseline_motions[row.reference+"/"+row.label]=row
	await settle();source.free()
	await observations()
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(TARGET)==candidate_sha,"Both saved50/51 scene files unchanged by verification")
	await finish()

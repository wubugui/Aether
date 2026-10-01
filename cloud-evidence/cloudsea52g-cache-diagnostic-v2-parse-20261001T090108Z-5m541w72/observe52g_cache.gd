extends "/workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52g/runtime-d-ab/observe52g_d_ab.gd"
## One variable: exact-geometry resource rebind. No D geometry or light toggle.
var cache_clones := {}
var cache_clone_rows := []
var cache_rebind_rows := []
var cache_phase_rows := []
var cache_baseline_viewport := {}
var cache_complete := false
var cache_intervention_returned := false
var cache_baseline_repeat_exact: Variant = null
var cache_restored_pixels_exact: Variant = null
var cache_restored_repeat_exact: Variant = null

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
	lab_view="front";version="52g-cache-diagnostic";call_deferred("run")

func cache_report() -> Dictionary:
	return {"diagnostic_complete":cache_complete,"diagnostic_checks_passed":cache_complete and not failed,"stage":lab_stage,
		"scene":LAB_SCENE,"scene_sha256":candidate_sha,"renderer":RenderingServer.get_video_adapter_name(),
		"scope":"Only ten original52e v0 mains rebound to byte-equivalent mesh clones and immediately to retained originals, before any frame; no D source loaded",
		"target_paths":lab_targets,"clone_rows":cache_clone_rows,"rebind_rows":cache_rebind_rows,"phase_rows":cache_phase_rows,
		"captures":captures,"checks":checks,"restore_rows":lab_restore_rows,"live_cloud_bindings":live_cloud_bindings,
		"baseline_native_digest":lab_baseline_digest,"intervention_returned":cache_intervention_returned,"restoration_complete":lab_restore_complete,
		"original_resources_kept":lab_original_resources.size(),"baseline_repeat_pixels_exact":cache_baseline_repeat_exact,
		"A0_R0_pixels_exact":cache_restored_pixels_exact,"restored_repeat_pixels_exact":cache_restored_repeat_exact,
		"pixel_difference_is_a_diagnostic_result_not_waived_acceptance":true,"single_full_world":true,"scene_saved":false,
		"geometry_shape_changed":false,"material_changed":false,"lighting_changed":false,"D_source_loaded":false,
		"visual_acceptance":false,"hardware_gpu_acceptance":false,"complete_flight_passed":false,"shadow_root_cause_proven":false}

func write_partial(stage:String,_pending:Dictionary={}) -> void:
	lab_stage=stage
	if not output.is_empty() and DirAccess.dir_exists_absolute(output):lab_atomic(output.path_join("partial-report.json"),cache_report())

func cache_viewport() -> Dictionary:
	return {"requested_window_size":root.size,"content_scale_size":root.content_scale_size,"content_scale_mode":root.content_scale_mode,
		"content_scale_aspect":root.content_scale_aspect,"content_scale_factor":root.content_scale_factor,
		"capture_readback_size":Vector2i(int(captures[-1].size[0]),int(captures[-1].size[1])),
		"texture_metadata_dimensions":Vector2i(root.get_texture().get_width(),root.get_texture().get_height()),
		"visible_rect":root.get_visible_rect(),"stretch_transform":root.get_stretch_transform(),
		"camera_visible_rect":game.camera.get_viewport().get_visible_rect(),"camera_projection":game.camera.get_camera_projection(),
		"msaa_3d":root.msaa_3d,"use_taa":root.use_taa,"screen_space_aa":root.screen_space_aa}

func cache_prepare_clones() -> bool:
	for path in lab_targets:
		var original:Mesh=lab_originals[path].mesh;var id:=original.get_instance_id()
		if not cache_clones.has(id):cache_clones[id]=original.duplicate(false) as Mesh
		var clone:Mesh=cache_clones[id]
		var geometry_exact:bool=audit.digest(lab_geometry(original))==audit.digest(lab_geometry(clone))
		var materials_exact:=original.get_surface_count()==clone.get_surface_count()
		for i in range(original.get_surface_count()):materials_exact=materials_exact and original.surface_get_material(i)==clone.surface_get_material(i)
		var row:={"path":path,"original_mesh_id":id,"clone_mesh_id":clone.get_instance_id(),"distinct_resource_and_rid":clone!=original and clone.get_rid()!=original.get_rid(),
			"all_geometry_native_bytes_exact":geometry_exact,"surface_material_identities_exact":materials_exact}
		cache_clone_rows.append(row)
		if not check(row.distinct_resource_and_rid and geometry_exact and materials_exact,"Exact geometry/material clone "+path):return false
	return true

func cache_rebind() -> bool:
	# No await here. The renderer receives both resource changes; no frame shows
	# altered geometry because the clone is exact and original is restored here.
	for path in lab_targets:
		var node:MeshInstance3D=game.get_node(path);var saved:Dictionary=lab_originals[path]
		var clone:Mesh=cache_clones[saved.mesh.get_instance_id()]
		node.mesh=clone
		var clone_bound:bool=node.mesh==clone and node.get_active_material(0)==saved.active_material
		node.mesh=saved.mesh
		var row:={"path":path,"clone_was_bound":clone_bound,"original_identity_restored":node.mesh==saved.mesh,
			"all_components_untouched_exact":audit.digest(lab_components(node))==audit.digest(saved.components),
			"flags_exact":audit.digest(audit.mesh_flags(node))==audit.digest(saved.flags),"active_material_identity_exact":node.get_active_material(0)==saved.active_material}
		cache_rebind_rows.append(row)
		if not check(clone_bound and row.original_identity_restored and row.all_components_untouched_exact and row.flags_exact and row.active_material_identity_exact,"Only exact resource rebind "+path):return false
	# Read-only proof: do not call component setters, even with equal values.
	if not cache_prove_restore():return false
	cache_intervention_returned=true;return true

func cache_prove_restore() -> bool:
	lab_restore_rows.clear();var ok:=true
	for path in lab_targets:
		var node:MeshInstance3D=game.get_node(path);var saved:Dictionary=lab_originals[path]
		if node.mesh!=saved.mesh:node.mesh=saved.mesh
		var actual:=lab_components(node);var component_rows:=[];var all_equal:=true
		for key in saved.components:
			var before:Variant=saved.components[key];var after:Variant=actual[key]
			var exact:bool=typeof(before)==typeof(after) and var_to_bytes(before)==var_to_bytes(after)
			component_rows.append({"component":key,"exact":exact,"native_type":type_string(typeof(before)),"before_bytes":var_to_bytes(before).hex_encode(),"restored_bytes":var_to_bytes(after).hex_encode()});all_equal=all_equal and exact
		var row:={"path":path,"all_components_exact":all_equal,"components":component_rows,"mesh_resource_identity_restored":node.mesh==saved.mesh,
			"flags_typed_exact":audit.digest(audit.mesh_flags(node))==audit.digest(saved.flags),"active_material_identity_exact":node.get_active_material(0)==saved.active_material}
		lab_restore_rows.append(row);ok=ok and all_equal and row.mesh_resource_identity_restored and row.flags_typed_exact and row.active_material_identity_exact
	lab_restore_complete=ok and lab_restore_rows.size()==10
	return check(lab_restore_complete,"Ten exact original mesh/component/material restores; no component setters")

func cache_capture(phase:String) -> bool:
	lab_phase=phase;meshes_world.clear();collect_cloud_triangles();check_live_clouds(phase)
	await capture("1216-front-"+phase,"1216","front")
	var state:=lab_state();var viewport:=cache_viewport();var digest:=audit.digest(state)
	if phase=="A0":lab_baseline=state;lab_baseline_digest=digest;cache_baseline_viewport=viewport;lab_save_baseline()
	var native_exact:bool=digest==lab_baseline_digest
	var viewport_exact:bool=audit.digest(viewport)==audit.digest(cache_baseline_viewport)
	var projection:Projection=game.camera.get_camera_projection()
	var requested_exact:bool=root.size==Vector2i(1180,664)
	var content_config_exact:bool=root.content_scale_size==Vector2i(1672,941) and root.content_scale_mode==Window.CONTENT_SCALE_MODE_CANVAS_ITEMS and root.content_scale_aspect==Window.CONTENT_SCALE_ASPECT_KEEP and root.content_scale_factor==1.0
	var readback_exact:bool=viewport.capture_readback_size==Vector2i(1179,664) and int(floor(664.0*1672.0/941.0))==1179
	# Godot4.5.1 ViewportTexture::get_width/height applies the Window stretch
	# to internal viewport size. get_image() instead reads the real RS texture.
	var stretch_scale:Vector2=root.get_stretch_transform().get_scale()
	var expected_metadata:=Vector2i(int(1179.0*stretch_scale.x),int(664.0*stretch_scale.y))
	var metadata_exact:bool=viewport.texture_metadata_dimensions==expected_metadata and expected_metadata==Vector2i(831,468)
	var projection_exact:bool=abs(projection.y.y/projection.x.x-1672.0/941.0)<0.000001
	var dimensions_contract:bool=requested_exact and content_config_exact and readback_exact and metadata_exact and projection_exact
	var row:={"phase":phase,"native_full_exact":native_exact,"full_native_digest":digest,"node_count":state.nodes.size(),
		"viewport_exact":viewport_exact,"viewport_typed_digest":audit.digest(viewport),"viewport_values":audit.canonical(viewport),
		"dimensions_contract_exact":dimensions_contract,"actual_dimensions":[int(viewport.capture_readback_size.x),int(viewport.capture_readback_size.y)],
		"texture_metadata_dimensions":[int(viewport.texture_metadata_dimensions.x),int(viewport.texture_metadata_dimensions.y)],
		"metadata_expected_from_engine_formula":[expected_metadata.x,expected_metadata.y],
		"requested_size_exact":requested_exact,"content_config_exact":content_config_exact,"actual_readback_size_exact":readback_exact,"texture_metadata_formula_exact":metadata_exact,"projection_aspect_exact":projection_exact,
		"requested_dimensions":[1180,664],"expected_dimensions_from_fixed_project":[1179,664],
		"stored_differences":lab_changes(lab_baseline.nodes,state.nodes),"runtime_differences":lab_changes(lab_baseline.runtime,state.runtime)}
	cache_phase_rows.append(row)
	check(native_exact,"Full unmasked native state exact "+phase)
	check(viewport_exact,"Viewport configuration and metadata stable "+phase)
	check(requested_exact and content_config_exact,"Requested Window and fixed project content dimensions exact "+phase)
	check(readback_exact,"Actual captured Image readback1179x664 exact "+phase)
	check(metadata_exact,"ViewportTexture metadata831x468 matches engine stretch formula "+phase)
	check(projection_exact,"Camera projection aspect matches fixed1672x941 content "+phase)
	write_partial("phase_"+phase+"_completed")
	return not failed

func finish() -> void:
	if lab_have_originals and not lab_restore_complete:cache_prove_restore()
	cache_complete=not failed and cache_intervention_returned and captures.size()==4 and cache_phase_rows.size()==4 and cache_rebind_rows.size()==10 and lab_restore_complete
	check(cache_complete,"Diagnostic functions/captures/restoration complete; pixel equality separately reported")
	write_partial("finished");lab_atomic(output.path_join("report.json"),cache_report())
	cache_clones.clear();lab_baseline.clear();lab_originals.clear();lab_original_resources.clear();audit.resource_cache.clear()
	if is_instance_valid(game):game.queue_free()
	await frames(8);quit(0 if cache_complete and not failed else 1)

func run() -> void:
	if not check(DisplayServer.get_name()!="headless","Actual renderer only when parent launches GUI diagnostic"):quit(2);return
	if not check(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output),"Fresh diagnostic output required"):quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	if not lab_validate_gate():await finish();return
	candidate_sha=FileAccess.get_sha256(LAB_SCENE);default_sha=FileAccess.get_sha256("res://project.godot")
	var packed:PackedScene=ResourceLoader.load(LAB_SCENE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	game=packed.instantiate();packed=null
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node("World/LakeReflection51")
	var collisions:=collision_state(game);freeze_tree(game);await physics_frame;await physics_frame
	check(collisions==collision_state(game),"Callback freeze preserves live physics state")
	await prepare_view("1216")
	for i in range(5):controller.refresh_now();await process_frame
	await RenderingServer.frame_post_draw
	if not lab_prepare_originals() or not cache_prepare_clones():await finish();return
	if not await cache_capture("A0"):await finish();return
	if not await cache_capture("A1"):await finish();return
	cache_baseline_repeat_exact=captures[0].rgba_digest==captures[1].rgba_digest
	if not cache_rebind():await finish();return
	if not await cache_capture("R0"):await finish();return
	if not await cache_capture("R1"):await finish();return
	cache_restored_pixels_exact=captures[0].rgba_digest==captures[2].rgba_digest
	cache_restored_repeat_exact=captures[2].rgba_digest==captures[3].rgba_digest
	check(FileAccess.get_sha256(LAB_SCENE)==LAB_SHA and FileAccess.get_sha256("res://project.godot")==default_sha,"Fixed scene/default file bytes unchanged")
	await finish()

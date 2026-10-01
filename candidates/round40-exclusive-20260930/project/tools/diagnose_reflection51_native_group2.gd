extends "res://tools/diagnose_reflection51_groups.gd"
## Narrow runtime-only diagnostic. Exactly the 32 native group2 materials vary.
## Original assets, Ocean, custom shaders, camera masks, layers and scenes stay unchanged.
const GROUP2_FEATURE := "3f17e41d2d8b4db1b376b27d02c1a44b8764f8d1e911907c62e065bcef0e3ca9"
var group2_variants := {}
var variant_ledger := []
var group2_baseline_state := {}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
	call_deferred("run")
func original_actual_state() -> Dictionary:
	resource_cache.clear()
	var result := {}
	for path in material_pairs: result[path]=canonical(material_pairs[path].original)
	result["Ocean"]=canonical(source_ocean)
	return result
func make_group2_variants() -> bool:
	var ok := true
	var template_path: String=ProjectSettings.globalize_path("res://").path_join("../../../source-assets/reflection50/official-native-conversions/native_group_02_shader.tres").simplify_path()
	var template: ShaderMaterial=ResourceLoader.load(template_path,"ShaderMaterial",ResourceLoader.CACHE_MODE_IGNORE)
	if not check(template!=null,"Official group2 template loads without conversion or source edits"):return false
	for row in build_report.material_ledger:
		if row.get("native_feature_sha256","")!=GROUP2_FEATURE:continue
		var path: String=row.new_material_path
		var pair: Dictionary=material_pairs[path]
		var original: StandardMaterial3D=pair.original
		var converted: ShaderMaterial=pair.converted
		var rid_copy := original.duplicate(false) as StandardMaterial3D
		var plain := template.duplicate(false) as ShaderMaterial
		plain.resource_name=original.resource_name
		plain.resource_local_to_scene=original.resource_local_to_scene
		plain.set_shader_parameter("albedo",original.albedo_color)
		resource_cache.clear()
		var clone_equal: bool=canonical(rid_copy)==canonical(original)
		var parameters := []
		var params_equal := true
		for uniform in template.shader.get_shader_uniform_list():
			var name: String=uniform.name
			var same: bool=canonical(plain.get_shader_parameter(name))==canonical(converted.get_shader_parameter(name))
			params_equal=params_equal and same
			parameters.append({"name":name,"plain":canonical(plain.get_shader_parameter(name)),"converted":canonical(converted.get_shader_parameter(name)),"equal":same})
		var template_sha_ok: bool=FileAccess.get_sha256(template_path)==row.official_template_sha256 and template.shader.code.sha256_text()==row.old_shader_sha256
		var disabled: bool=converted.get_shader_parameter("lake51_reflection_clip_enabled")==false
		ok=check(clone_equal and params_equal and template_sha_ok and disabled and original.next_pass==null,"Group2 exact RID copy and official unmodified template parameter equivalence "+path) and ok
		group2_variants[path]={"rid":rid_copy,"plain":plain,"injected":converted}
		variant_ledger.append({"path":path,"source":original.resource_path,"original_fingerprint":digest(canonical(original)),"rid_copy_exact":clone_equal,"original_rid":str(original.get_rid()),"duplicate_rid":str(rid_copy.get_rid()),"native_feature_sha256":GROUP2_FEATURE,"template_path":template_path,"template_file_sha256":FileAccess.get_sha256(template_path),"template_shader_sha256":template.shader.code.sha256_text(),"injected_shader_sha256":converted.shader.code.sha256_text(),"parameters_equal":params_equal,"parameters":parameters,"clip_disabled":disabled})
	return check(group2_variants.size()==32 and ok,"Exactly32 known native group2 variants prepared")
func apply_group2(mode: String) -> int:
	apply_bindings(true)
	var count := 0
	for row in stored_rows:
		var path: String=row.converted.resource_path
		if group2_variants.has(path):game.get_node(row.path).set(row.property,group2_variants[path][mode]);count+=1
	for row in live_rows.values():
		var path: String=row.converted.resource_path
		var node := game.get_node_or_null(row.path)
		if node!=null and group2_variants.has(path):node.set(row.property,group2_variants[path][mode]);count+=1
	check(game.get_node("World/Ocean").material_override==source_ocean and game.get_node("World/Ocean").layers==original_ocean_layers and game.camera.cull_mask==original_camera_mask,"Original Ocean, camera mask and water layer retained in "+mode)
	return count
func observations() -> void:
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	var before:=collision_activity(game);freeze_tree(game);await physics_frame;await physics_frame
	check(before==collision_activity(game),"Native group2 diagnostic preserves active physics")
	if not await prepare_view("1128"):return
	if not make_group2_variants():return
	group2_baseline_state=original_actual_state()
	apply_bindings(true);reference_image=await shot("group2-A-original","1128")
	var captured := {}
	for mode in ["rid","plain","injected"]:
		var assignments := apply_group2(mode)
		var image := await shot("group2-"+mode,"1128")
		captured[mode]=image
		var delta := pixel_delta(reference_image,image)
		group_results.append({"name":mode,"compared_to":"original_StandardMaterial3D","native_feature_sha256":GROUP2_FEATURE,"materials":group2_variants.size(),"binding_assignments":assignments,"pixel_delta":delta})
		print("NATIVE_GROUP2_DELTA ",mode," pixels=",delta.changed_pixels," max=",delta.get("max_channel_delta",0)," bounds=",delta.get("bounds",[]))
	var injection_delta := pixel_delta(captured.plain,captured.injected)
	group_results.append({"name":"official-plain-vs-injected","compared_to":"official_unmodified_template","pixel_delta":injection_delta})
	print("NATIVE_GROUP2_DELTA plain-vs-injected pixels=",injection_delta.changed_pixels," max=",injection_delta.get("max_channel_delta",0))
	apply_bindings(true)
	var restored:=await shot("group2-A2-original-restored","1128")
	check(pixel_delta(reference_image,restored).changed_pixels==0,"Group2 test restores original rendered image exactly")
	check(group2_baseline_state==original_actual_state(),"All original material uniforms/properties unchanged through narrow diagnostic")
	apply_bindings(false);depth_controller.set_depth_enabled(true);controller.set_effect_flags(false,false)
func finish() -> void:
	var valid := failures.is_empty()
	for row in checks:valid=valid and row.passed
	var report := {"diagnostic_instrumentation_passed":valid,"candidate_sha256":candidate_sha,"source_scene_unchanged":FileAccess.get_sha256(TARGET)==candidate_sha,"purpose":"Exactly32 native group2 materials: original StandardMaterial3D versus identical StandardMaterial3D RID clones, unmodified official4.5.1 template with exact parameters, and current clipped shader with clipping disabled. All other bindings remain original; A/A2 restoration is mandatory.","groups":group_results,"variant_ledger":variant_ledger,"checks":checks,"failures":failures,"captures":captures,"uniform_sync_ledger":uniform_sync_ledger,"new_candidate_written":false,"mainpass_acceptance":false,"visual_acceptance":false,"total_acceptance_passed":false,"renderer":RenderingServer.get_video_adapter_name()}
	if not output.is_empty():
		var f:=FileAccess.open(output.path_join("native-group2-report.json"),FileAccess.WRITE)
		if f!=null:f.store_string(JSON.stringify(report,"  "));f.close()
	if is_instance_valid(game):await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51 NATIVE GROUP2 COMPLETE instrumentation=",valid," trials=",group_results.size());quit(0 if valid else 1)

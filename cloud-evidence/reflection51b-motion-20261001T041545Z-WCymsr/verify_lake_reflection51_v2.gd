extends "res://tools/verify_lake_reflection51.gd"
## Independent v2 diagnostic. Original-vs-new-resource differences remain findings.
## The newly authorized strict gate is identical original material copies versus
## converted materials. Shader RID/code stay original in the copy baseline.
var copy_materials := {}
var copy_ocean: ShaderMaterial
var copy_ledger := []
var original_resource_differences := []
var copy_resource_differences := []
var completed_normal_references := []
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg=="--normal-only":normal_only=true
	call_deferred("run")
func pixel_delta(a: Image,b: Image) -> Dictionary:
	var aa := a.get_data();var bb := b.get_data()
	if a.get_size()!=b.get_size() or aa.size()!=bb.size(): return {"same_size":false,"changed_pixels":-1}
	if aa==bb: return {"same_size":true,"changed_pixels":0,"max_channel_delta":0,"points":[],"bounds":[]}
	var width := a.get_width();var count := 0;var maximum := 0
	var min_x := width;var max_x := -1;var min_y := a.get_height();var max_y := -1
	var points := []
	for index in range(0,aa.size(),4):
		var changed := false
		for channel in range(4):
			var delta := absi(int(aa[index+channel])-int(bb[index+channel]));maximum=maxi(maximum,delta);changed=changed or delta!=0
		if changed:
			var pixel := index/4;var x := pixel%width;var y := pixel/width
			count+=1;min_x=mini(min_x,x);max_x=maxi(max_x,x);min_y=mini(min_y,y);max_y=maxi(max_y,y)
			if points.size()<1000: points.append({"x":x,"y":y,"original":[aa[index],aa[index+1],aa[index+2],aa[index+3]],"trial":[bb[index],bb[index+1],bb[index+2],bb[index+3]]})
	return {"same_size":true,"changed_pixels":count,"max_channel_delta":maximum,"bounds":[min_x,min_y,max_x,max_y],"points":points,"points_truncated":count>1000}
func original_actual_state() -> Dictionary:
	resource_cache.clear()
	var state := {}
	for path in material_pairs:state[path]=canonical(material_pairs[path].original)
	state["Ocean"]=canonical(source_ocean)
	return state
func update_exact_clone(original: Material,copy: Material,label: String) -> bool:
	# Retain clone Material identity while matching all stored values at each ref.
	for property in original.get_property_list():
		var name: String=property.name
		if property.usage & PROPERTY_USAGE_STORAGE and name!="resource_path":copy.set(name,original.get(name))
	if original is ShaderMaterial:
		for uniform in original.shader.get_shader_uniform_list():copy.set_shader_parameter(uniform.name,original.get_shader_parameter(uniform.name))
	resource_cache.clear()
	var equal: bool=canonical(original)==canonical(copy)
	var shared_shader: bool=not original is ShaderMaterial or original.shader==copy.shader
	var row := {"reference":current_reference,"material":label,"class":original.get_class(),"original_fingerprint":digest(canonical(original)),"copy_fingerprint":digest(canonical(copy)),"canonical_equal":equal,"original_rid":str(original.get_rid()),"copy_rid":str(copy.get_rid()),"different_material_rid":original.get_rid()!=copy.get_rid(),"same_original_shader_object":shared_shader,"next_pass_null":original.next_pass==null and copy.next_pass==null,"shader_copy_strategy":"Material duplicate(false); original Shader object/RID and code retained"}
	if original is ShaderMaterial:row.original_shader_sha256=original.shader.code.sha256_text()
	copy_ledger.append(row)
	return check(equal and shared_shader and row.different_material_rid and row.next_pass_null,"Exact same-value material copy baseline "+label,row)
func prepare_copy_baseline() -> bool:
	var valid := true
	for path in material_pairs:
		var original: Material=material_pairs[path].original
		if not copy_materials.has(path):copy_materials[path]=original.duplicate(false)
		valid=update_exact_clone(original,copy_materials[path],path) and valid
	if copy_ocean==null:copy_ocean=source_ocean.duplicate(false)
	valid=update_exact_clone(source_ocean,copy_ocean,"Ocean") and valid
	return check(valid and copy_materials.size()==114,"All114 original materials plus Ocean have exact copy baselines")
func apply_copy_baseline() -> void:
	apply_bindings(true)
	for row in stored_rows:game.get_node(row.path).set(row.property,copy_materials[row.converted.resource_path])
	for row in live_rows.values():
		var node:=game.get_node_or_null(row.path)
		if node!=null:node.set(row.property,copy_materials[row.converted.resource_path])
	game.get_node("World/Ocean").material_override=copy_ocean
	depth_controller.water=copy_ocean;depth_controller.set_depth_enabled(false)
	var textures_equal: bool=depth_controller.water==game.get_node("World/Ocean").material_override and depth_controller.textures.size()==5
	for index in range(depth_controller.textures.size()):
		var uniform_name := "lake50_height" if index==0 else "lake50_patch"+str(index-1)
		textures_equal=textures_equal and copy_ocean.get_shader_parameter(uniform_name)==depth_controller.textures[index]
	check(textures_equal and game.camera.cull_mask==original_camera_mask and game.get_node("World/Ocean").layers==original_ocean_layers,"Copy baseline preserves original camera/layers and current depth-controller five-texture cache")
func normal_controls(reference: String) -> bool:
	if not await prepare_view(reference):return false
	if not prepare_copy_baseline():normal_pass=false;clip_only_pass=false;return false
	var pose: Transform3D=game.camera.global_transform
	var original_state := original_actual_state()
	apply_bindings(true)
	var a:=await shot(reference+"--A50-original-bindings",reference)
	apply_copy_baseline()
	var c:=await shot(reference+"--C50-identical-material-copies",reference)
	apply_bindings(false)
	var b:=await shot(reference+"--B51-converted-off",reference)
	apply_bindings(true)
	var a2:=await shot(reference+"--A50-original-restored",reference)
	var old_delta := pixel_delta(a,b)
	var identity_delta := pixel_delta(a,c)
	var conversion_delta := pixel_delta(c,b)
	original_resource_differences.append({"reference":reference,"original_vs_converted":old_delta,"original_vs_identical_copies":identity_delta,"original_zero_diff":old_delta.changed_pixels==0,"accepted_as_original_zero_diff":false,"tolerance":0,"interpretation":"Measured original-resource difference retained. Identical Material identity replacement can itself change pixels; precise renderer sorting mechanism is not yet proven."})
	copy_resource_differences.append({"reference":reference,"identical_material_copies_vs_converted":conversion_delta,"required_zero_diff":true})
	print("ORIGINAL_RESOURCE_DELTA ",reference," original-vs-converted=",old_delta.changed_pixels," original-vs-copies=",identity_delta.changed_pixels," copied-baseline-vs-converted=",conversion_delta.changed_pixels)
	compare(a,b,reference+"/original-vs-converted-MEASURED-NOT-ACCEPTED",false)
	var equal:=compare(c,b,reference+"/identical-original-copies-vs-converted-off",true)
	equal=compare(a,a2,reference+"/original-A-vs-A2",true) and equal
	if not equal:normal_pass=false;clip_only_pass=false;return false
	apply_bindings(false);controller.set_effect_flags(true,false)
	var clip:=await shot(reference+"--D51-clip-only",reference)
	var clip_equal:=compare(b,clip,reference+"/clip-only-main-and-shadow-no-change",true)
	controller.set_effect_flags(false,false)
	var restored:=await shot(reference+"--B51-converted-off-restored",reference)
	clip_equal=compare(b,restored,reference+"/converted-off-restored",true) and clip_equal
	check(original_state==original_actual_state(),"All original material properties and uniforms unchanged through controls "+reference)
	check(game.camera.global_transform==pose,"Primary camera optical pose unchanged across v2 controls "+reference)
	if not clip_equal:clip_only_pass=false;return false
	completed_normal_references.append(reference)
	return true
func finish() -> void:
	var scoped:=failures.is_empty()
	for row in checks:scoped=scoped and row.passed
	var requested:=movement_checks.size()==6
	for row in movement_checks:
		if row.required:requested=requested and row.passed
	var expected_references:=2 if normal_only else 7
	var original_zero:=original_resource_differences.size()==expected_references
	for row in original_resource_differences:original_zero=original_zero and row.original_zero_diff
	var copy_pass:=normal_pass and completed_normal_references.size()==expected_references
	var report:={"version":2,"scoped_copy_baseline_runtime_passed":scoped and copy_pass and clip_only_pass,"normal_pass_zero_diff":original_zero,"original_resource_normal_pass_zero_diff":original_zero,"copied_material_baseline_conversion_zero_diff":copy_pass,"clip_only_zero_diff":clip_only_pass,"requested_motion_all_passed":requested,"total_acceptance_passed":false,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":candidate_sha,"unaffected_graph_fingerprint":unchanged_fingerprint,"checks":checks,"failures":failures,"captures":captures,"comparisons":comparisons,"original_resource_differences":original_resource_differences,"copy_resource_differences":copy_resource_differences,"copy_baseline_ledger":copy_ledger,"completed_normal_references":completed_normal_references,"movement_checks":movement_checks,"freeze_physics":freeze_evidence,"material_pair_count":material_pairs.size(),"stored_binding_count":stored_rows.size(),"latest_ready_binding_count":live_rows.size(),"mode_history":mode_history,"normal_only":normal_only,"uniform_sync_ledger":uniform_sync_ledger,"reflection_checks":reflection_checks,"renderer":RenderingServer.get_video_adapter_name(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"complete_flight_passed":false,"dynamic_waterline_straddling_clip_verified":false,"arbitrary_future_stream_instances_verified":false,"scope":"Independent v2, original v1 evidence unchanged. Every ref records original-vs-converted and original-vs-copy full RGBA differences. Authorized strict gate uses all114 same-value original Material clones plus Ocean (original Shader objects retained) versus converted resources, followed by original A/A2 restoration and clip-only zero-diff. Seven reference/weather controls then limited shared-world reflection and existing ship/camera motion. No tolerance or pixel masking. Original-resource equivalence is separately false if any pixel differs; identity replacement effect is not claimed as proven renderer sorting causation. Saved51off retains known edge artifact; inherited required350m failures remain failures.","exit_policy":"exit0 means only copied-resource conversion, restore, clip-only and scoped runtime checks passed; it never overrides original-resource difference, motion failures, visual limits or total_acceptance=false"}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game):await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51 V2 VERIFIED scoped=",scoped," copied_baseline_zero_diff=",copy_pass," original_zero_diff=",original_zero," clip_only_zero_diff=",clip_only_pass," required_motion=",requested," total=false")
	quit(0 if scoped and copy_pass and clip_only_pass else 1)

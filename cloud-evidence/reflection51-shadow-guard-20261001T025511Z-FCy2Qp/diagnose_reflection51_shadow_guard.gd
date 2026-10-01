extends "res://tools/diagnose_reflection51_groups.gd"
## Runtime-only guard substitution on existing Shader objects/RIDs. No material
## replacement or asset save. Restore every original shader byte before exit.
const OLD_MARKER := "(CAMERA_VISIBLE_LAYERS & 524288u) != 0u"
const GUARDED_MARKER := "(CAMERA_VISIBLE_LAYERS & 524288u) != 0u && (CAMERA_VISIBLE_LAYERS & 262144u) == 0u"
var guard_sources := []
var guard_ledger := []
var source_codes_restored := false
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
	call_deferred("run")
func prepare_guard() -> bool:
	var seen := {}
	var valid := true
	for material in controller.clipping_materials:
		var shader: Shader=material.shader
		if seen.has(shader.get_instance_id()):continue
		seen[shader.get_instance_id()]=true
		var code:=shader.code
		if not check(code.count(OLD_MARKER)==1 and not code.contains(GUARDED_MARKER),"Exactly one original camera-marker predicate "+shader.resource_path):valid=false;continue
		var guarded:=code.replace(OLD_MARKER,GUARDED_MARKER)
		var exact:=guarded.replace(GUARDED_MARKER,OLD_MARKER)==code
		valid=check(exact,"Guard insertion inverse restores exact original shader bytes") and valid
		var row:={"shader":shader,"original":code,"guarded":guarded,"rid":str(shader.get_rid()),"path":shader.resource_path,"file_sha256":FileAccess.get_sha256(shader.resource_path)}
		guard_sources.append(row)
		guard_ledger.append({"path":row.path,"file_sha256":row.file_sha256,"original_code_sha256":code.sha256_text(),"guarded_code_sha256":guarded.sha256_text(),"shader_rid":row.rid,"old_predicate":OLD_MARKER,"new_predicate":GUARDED_MARKER,"exact_reverse":exact})
	return check(valid and not guard_sources.is_empty(),"All active clipping Shader objects prepared without material replacement",{"unique_shader_objects":guard_sources.size(),"materials":controller.clipping_materials.size()})
func set_guard(enabled: bool) -> void:
	for row in guard_sources:
		row.shader.code=row.guarded if enabled else row.original
		check(str(row.shader.get_rid())==row.rid,"Existing shader RID retained during runtime guard switch "+row.path)
	if not enabled:
		source_codes_restored=true
		for row in guard_sources:source_codes_restored=source_codes_restored and row.shader.code==row.original and FileAccess.get_sha256(row.path)==row.file_sha256
func observations() -> void:
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	var before:=collision_activity(game);freeze_tree(game);await physics_frame;await physics_frame
	check(before==collision_activity(game),"Guard diagnostic preserves active physics")
	if not await prepare_view("1343"):return
	apply_bindings(false)
	if not prepare_guard():return
	var sun:=game.get_node("Sun") as DirectionalLight3D
	var shadow_enabled:=sun.shadow_enabled
	controller.set_effect_flags(false,false)
	var off:=await shot("1343-old-shader-clip-off","1343")
	controller.set_effect_flags(true,false)
	var old_on:=await shot("1343-old-shader-clip-on","1343")
	var old_delta:=pixel_delta(off,old_on)
	group_results.append({"name":"old-clip-toggle","pixel_delta":old_delta})
	set_guard(true)
	var guard_on:=await shot("1343-guarded-shader-clip-on","1343")
	var guard_delta:=pixel_delta(off,guard_on)
	group_results.append({"name":"old-off-vs-guarded-on","pixel_delta":guard_delta,"required_zero":true})
	check(guard_delta.changed_pixels==0,"Guarded clip-on restores exact original clip-off main/shadow pixels")
	controller.set_effect_flags(false,false)
	var guard_off:=await shot("1343-guarded-shader-clip-off","1343")
	check(pixel_delta(off,guard_off).changed_pixels==0,"Guarded clip-off is exact original clip-off")
	set_guard(false)
	var restored:=await shot("1343-old-shader-clip-off-restored","1343")
	check(source_codes_restored and pixel_delta(off,restored).changed_pixels==0,"All original shader bytes/RIDs/files and clip-off image exactly restored")
	check(sun.shadow_enabled==shadow_enabled,"Original Sun shadow flag never changed by guard diagnostic")
	print("SHADOW_GUARD_DELTA old_clip=",old_delta.changed_pixels," guarded_clip=",guard_delta.changed_pixels)
	# Supplementary existing-geometry reflection control. Keep controller reflection
	# active while directly toggling only clip uniforms, with guard active. This is
	# evidence of actual reflected-pixel clipping, not a complete waterline suite.
	if guard_delta.changed_pixels==0 and await prepare_view("1128"):
		set_guard(true);depth_controller.set_depth_enabled(true);controller.set_effect_flags(true,true)
		for material in controller.clipping_materials:material.set_shader_parameter("lake51_reflection_clip_enabled",false)
		var uncut:=await shot("1128-guarded-reflection-existing-geometry-unclipped","1128",true)
		for material in controller.clipping_materials:material.set_shader_parameter("lake51_reflection_clip_enabled",true)
		var cut:=await shot("1128-guarded-reflection-existing-geometry-clipped","1128",true)
		var clip_delta:=pixel_delta(uncut,cut)
		group_results.append({"name":"guarded-reflection-existing-geometry-unclipped-vs-clipped","pixel_delta":clip_delta,"waterline_straddling_fixture_verified":false})
		check(clip_delta.changed_pixels>0,"Guard still changes actual reflection pixels when below-plane clipping is enabled")
		check((controller.reflection_camera.cull_mask & MARKER)!=0 and (controller.reflection_camera.cull_mask & WATER_LAYER)==0 and controller.effective_reflection,"Real reflection camera satisfies marker-present/water-absent guard")
		controller.set_effect_flags(false,false);set_guard(false)
	check(source_codes_restored,"Final all original shader bytes and asset files restored")
	depth_controller.set_depth_enabled(true)
func finish() -> void:
	# Recover runtime originals even after an instrumentation failure.
	if not guard_sources.is_empty():set_guard(false)
	var valid:=failures.is_empty()
	for row in checks:valid=valid and row.passed
	var report:={"diagnostic_instrumentation_passed":valid,"candidate_sha256":candidate_sha,"source_scene_unchanged":FileAccess.get_sha256(TARGET)==candidate_sha,"source_shader_bytes_restored":source_codes_restored,"purpose":"Runtime predicate guard requires marker19 set AND water18 clear, preserving shader/material RIDs and all other code. Five1343 main/shadow controls, original source restoration, optional1128 actual reflection clipping toggle. No saved asset or Sun change.","groups":group_results,"guard_ledger":guard_ledger,"checks":checks,"failures":failures,"captures":captures,"new_candidate_written":false,"mainpass_acceptance":false,"visual_acceptance":false,"total_acceptance_passed":false,"dynamic_waterline_straddling_clip_verified":false,"renderer":RenderingServer.get_video_adapter_name()}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("shadow-guard-report.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game):await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51 SHADOW GUARD COMPLETE instrumentation=",valid);quit(0 if valid else 1)

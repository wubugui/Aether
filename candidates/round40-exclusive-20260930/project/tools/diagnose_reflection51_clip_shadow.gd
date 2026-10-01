extends "res://tools/diagnose_reflection51_groups.gd"
## Same converted material objects throughout; only clip flag and diagnostic Sun
## shadow flag vary. Five images at1343. No resource/scene changes or copies.
var shadow_original := false
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
	call_deferred("run")
func clip_shot(label: String) -> Image:
	var result:=await shot(label,"1343")
	check(controller.viewport.render_target_update_mode==SubViewport.UPDATE_DISABLED and not controller.effective_reflection,"Reflection viewport disabled during "+label,{"update_mode":controller.viewport.render_target_update_mode,"reflection_enabled":controller.reflection_enabled,"clip_enabled":controller.clip_enabled})
	return result
func observations() -> void:
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	var before:=collision_activity(game);freeze_tree(game);await physics_frame;await physics_frame
	check(before==collision_activity(game),"Clip/shadow diagnostic preserves active physics")
	if not await prepare_view("1343"):return
	apply_bindings(false)
	var params:=original_parameter_state()
	var sun:=game.get_node("Sun") as DirectionalLight3D
	shadow_original=sun.shadow_enabled
	controller.set_effect_flags(false,false)
	var off:=await clip_shot("1343-original-shadow-clip-off")
	controller.set_effect_flags(true,false)
	var on:=await clip_shot("1343-original-shadow-clip-on")
	var normal_delta:=pixel_delta(off,on)
	group_results.append({"name":"original-shadow-clip-off-vs-on","original_sun_shadow_enabled":shadow_original,"pixel_delta":normal_delta})
	print("CLIP_SHADOW_DELTA original-shadow pixels=",normal_delta.changed_pixels," max=",normal_delta.get("max_channel_delta",0))
	sun.shadow_enabled=false;controller.set_effect_flags(false,false)
	var no_shadow_off:=await clip_shot("1343-shadow-disabled-clip-off")
	controller.set_effect_flags(true,false)
	var no_shadow_on:=await clip_shot("1343-shadow-disabled-clip-on")
	var disabled_delta:=pixel_delta(no_shadow_off,no_shadow_on)
	group_results.append({"name":"shadow-disabled-clip-off-vs-on","pixel_delta":disabled_delta,"production_fix":false})
	print("CLIP_SHADOW_DELTA shadow-disabled pixels=",disabled_delta.changed_pixels," max=",disabled_delta.get("max_channel_delta",0))
	sun.shadow_enabled=shadow_original;controller.set_effect_flags(false,false)
	var restored:=await clip_shot("1343-original-shadow-clip-off-restored")
	check(sun.shadow_enabled==shadow_original and pixel_delta(off,restored).changed_pixels==0,"Original Sun shadow flag and clip-off image exactly restored")
	check(params==original_parameter_state(),"Every preexisting shader uniform/native albedo remains unchanged")
	depth_controller.set_depth_enabled(true)
func finish() -> void:
	var valid:=failures.is_empty()
	for row in checks:valid=valid and row.passed
	var report:={"diagnostic_instrumentation_passed":valid,"candidate_sha256":candidate_sha,"source_scene_unchanged":FileAccess.get_sha256(TARGET)==candidate_sha,"purpose":"1343 same converted material objects, clip off/on with original Sun shadows; clip off/on with shadows disabled; then exact original-shadow clip-off restoration. Shadow disabling is diagnostic only, never a production fix. No copied or edited material resources.","groups":group_results,"original_sun_shadow_enabled":shadow_original,"checks":checks,"failures":failures,"captures":captures,"uniform_sync_ledger":uniform_sync_ledger,"new_candidate_written":false,"mainpass_acceptance":false,"visual_acceptance":false,"total_acceptance_passed":false,"renderer":RenderingServer.get_video_adapter_name()}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("clip-shadow-report.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game):await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51 CLIP SHADOW COMPLETE instrumentation=",valid);quit(0 if valid else 1)

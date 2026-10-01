extends "res://tools/verify_lake_reflection51b.gd"
## Independent reflection/movement evidence. Never marks known1344 pixel gate passed.
const PRIOR_FULL := "/workspace/scratch/a29d03198654/Aether/cloud-evidence/reflection51b-verify-full-20261001T032554Z-975juK/images/report.json"
var prior_gate := {}
func observations() -> void:
	prior_gate=JSON.parse_string(FileAccess.get_file_as_string(PRIOR_FULL))
	if not check(prior_gate.candidate_sha256==candidate_sha and not prior_gate.copied_material_baseline_conversion_zero_diff,"Known1344 conversion gate failure belongs to exact saved51b"):return
	root.size=Vector2i(1180,664)
	root.add_child(game);game.sound_enabled=false;game.test_frozen=true
	game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	check(controller.clip_enabled and controller.reflection_enabled and is_equal_approx(controller.optical_overscan,1.08),"Actual saved51b loads enabled with overscan1.08")
	var before:=collision_activity(game);freeze_tree(game);await physics_frame;await physics_frame
	freeze_evidence={"count":before.size(),"unchanged":before==collision_activity(game)}
	if not check(freeze_evidence.unchanged,"Live collisions retained during callback freeze"):return
	for reference in ["1128","1129"]:
		if not await prepare_view(reference):return
		probe_motion(reference,game.camera.global_basis.x*350.,"original-plus350m",true)
		probe_motion(reference,game.camera.global_basis.x*150.,"protected-plus150m",false)
		probe_motion(reference,-game.camera.global_basis.z*200.,"protected-approach200m",false)
	await reflection_controls()
	# Additional fixed-pose reverse observations expose screen-edge/coast behavior.
	for reference in ["1128","1129"]:
		if not await prepare_view(reference):return
		depth_controller.set_depth_enabled(true);controller.set_effect_flags(true,true)
		var pose:Transform3D=game.camera.global_transform
		game.camera.rotate_y(PI);controller.refresh_now()
		await shot(reference+"--back-main",reference)
		await shot(reference+"--back-reflection-texture",reference,true)
		game.camera.global_transform=pose;controller.refresh_now()
		check(game.camera.global_transform==pose,"Reverse observation restores original camera "+reference)
	apply_bindings(false);controller.set_effect_flags(true,true);depth_controller.set_depth_enabled(true)
func finish() -> void:
	var scoped:=failures.is_empty()
	for row in checks:scoped=scoped and row.passed
	var requested:=movement_checks.size()==6
	for row in movement_checks:
		if row.required:requested=requested and row.passed
	var report:={"limited_reflection_motion_runtime_passed":scoped,"candidate":B_TARGET,"candidate_sha256":candidate_sha,"known_full_verifier_report":PRIOR_FULL,"known_full_verifier_report_sha256":FileAccess.get_sha256(PRIOR_FULL),"conversion_pixel_gate_passed":false,"known_conversion_failure_reference":"1344","known_conversion_difference_pixels":2,"requested_motion_all_passed":requested,"total_acceptance_passed":false,"checks":checks,"failures":failures,"captures":captures,"comparisons":comparisons,"reflection_checks":reflection_checks,"movement_checks":movement_checks,"freeze_physics":freeze_evidence,"transition_checks":transition_checks,"normal_pass_retested":false,"hardware_gpu_acceptance":false,"visual_acceptance":false,"dynamic_waterline_straddling_clip_verified":false,"arbitrary_future_stream_instances_verified":false,"renderer":RenderingServer.get_video_adapter_name(),"scope":"Independent actual saved51b shared-world reflection, current ship/camera translation, side/back observations and exact restorations; two-hop asset audit still runs. Does not waive known1344 two-pixel conversion failure, inherited350m route failures, fullvisual or reference-composition gaps."}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("reflection-motion-report.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game):await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51B MOTION ONLY COMPLETE limited=",scoped," known_conversion_gate=false total=false")
	quit(0 if scoped else 1)

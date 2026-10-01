extends "res://tools/verify_cloudsea52e.gd"
## Recovery observes only one saved candidate. No repeat51b load/audit/render/save.
const CANDIDATE_SHA := "5abbabf7487766412592f0b93ccd12c01e7bbb70f28e96ffd829e7ae78919079"
const BUILD_SHA := "7d2c041c17f0d4cf712adcb5e9a1d2b0f4a19dc057c11b6f9e55b2990fa0f177"
const PRIOR51_REPORT_SHA := "524758d2803c6fc2d201a6568a4ab8d4b55bc309879dcf2d15258640a6e87d4e"
const PRIOR_RUN := "/workspace/scratch/a29d03198654/Aether/cloud-evidence/cloudsea52e-paired-20261001T050129Z-geTptG/"
var subset:=""
var build_report_sha:=""
var baseline_observation_sha:=""
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--subset="):subset=arg.trim_prefix("--subset=")
	version="52e";call_deferred("run")
func load_single_candidate() -> Node3D:
	# PackedScene's local reference leaves scope before _ready/runtime streaming.
	var packed:PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	return packed.instantiate()
func finish() -> void:
	var expected:=3 if subset=="close" else 4
	var ok:=not failed and captures.size()==expected
	write_partial("subset_finished")
	var data:={"limited_remaining_subset_passed":ok,"run_complete":true,"subset":subset,"version":"52e","baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":candidate_sha,"candidate_build_report_sha256":build_report_sha,"prior51b_observation_report_sha256":baseline_observation_sha,"prior_interrupted_run":PRIOR_RUN,"prior52e_exit_code":137,"prior52e_runtime_json_missing":true,"prior9_reference_images_reobserved":false,"full_structural_audit_repeated":false,"saved_build_and_prior_console_audit_reused":true,"checks":checks,"captures":captures,"movements":movements,"live_cloud_bindings":live_cloud_bindings,"renderer":RenderingServer.get_video_adapter_name(),"visual_acceptance":false,"hardware_gpu_acceptance":false,"complete_flight_passed":false,"total_acceptance_passed":false,"original350m_gate_passed":false,"prior1344_conversion_gate_passed":false,"scope":"Only remaining3 close or4 climb saved52e camera observations in a fresh single-candidate process. Reuses immutable successful real-renderer build audit and exact prior51b report. Does not load51b or redo large native graph audits. Each capture atomically checkpoints actual runtime data. The original interrupted9 reference images lack runtimeJSON; this recovery cannot repair or pretend to reproduce that missing state. Exit137 root cause remains unknown."}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(data,"  "));file.flush();file.close()
	if DisplayServer.get_name()!="headless":await settle()
	if is_instance_valid(game):game.queue_free()
	await frames(8)
	print("52E REMAINING ",subset," completed=",ok," original_pair_complete=false")
	quit(0 if ok else 1)
func run() -> void:
	if not check(DisplayServer.get_name()!="headless","Actual renderer required"):quit(2);return
	if not check(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output) and subset in ["close","climb"],"New output and bounded remaining subset required"):quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	if not check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(TARGET)==CANDIDATE_SHA,"Exact immutable51b/52e files;51b never loaded"):await finish();return
	candidate_sha=CANDIDATE_SHA
	var build_path:="res://scenes/candidate52e/build-report-52e.json"
	build_report_sha=FileAccess.get_sha256(build_path)
	report52=JSON.parse_string(FileAccess.get_file_as_string(build_path))
	var prior:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PRIOR_RUN+"51b/report.json"))
	baseline_observation_sha=FileAccess.get_sha256(PRIOR_RUN+"51b/report.json")
	check(build_report_sha==BUILD_SHA and baseline_observation_sha==PRIOR51_REPORT_SHA,"Exact previously verified build and baseline report hashes")
	check(report52.build_saved_reload_passed and report52.candidate_sha256==CANDIDATE_SHA and report52.baseline_sha256==BASE_SHA,"Saved52e build/audit exact immutable input")
	check(prior.limited_structural_runtime_passed and prior.candidate_sha256==CANDIDATE_SHA and prior.captures.size()==16,"Existing16-image51b report exact input; no rerender")
	check(FileAccess.get_file_as_string(PRIOR_RUN+"52e.exit-code.txt").strip_edges()=="137" and not FileAccess.file_exists(PRIOR_RUN+"52e/report.json"),"Original interrupted52e retains137 and missing runtimeJSON")
	if failed:await finish();return
	game=load_single_candidate();await settle()
	prepare_supplemental_recipes(game)
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true
	game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node("World/LakeReflection51")
	var collisions:=collision_state(game);freeze_tree(game);await physics_frame;await physics_frame
	check(collisions==collision_state(game),"Single-candidate callback freeze preserves collision activity")
	collect_cloud_triangles();write_partial("single_candidate_ready")
	var last_climb:Variant=null
	for recipe in recipes:
		if recipe.kind!=subset:continue
		await prepare_view(recipe.reference)
		game.camera.global_position=recipe.position;game.camera.look_at(recipe.target,Vector3.UP)
		await capture(recipe.name,recipe.reference,recipe.kind)
		if subset=="climb":
			if last_climb!=null:probe_path(last_climb,recipe.position,"staged-climb-to-"+recipe.name);write_partial("path_complete")
			last_climb=recipe.position
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(TARGET)==CANDIDATE_SHA and FileAccess.get_sha256(build_path)==build_report_sha,"Immutable scene/build files unchanged after limited observations")
	await finish()

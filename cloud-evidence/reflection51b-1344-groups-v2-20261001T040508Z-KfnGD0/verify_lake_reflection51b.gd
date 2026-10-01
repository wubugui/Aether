extends "res://tools/verify_lake_reflection51_v2.gd"
## Frozen51b verifier:51->51b strict graph audit,50 originals for material pixels.
const B_BASE := "res://scenes/candidate51/Game51.tscn"
const B_BASE_SHA := "53e07e91b1bfafd0160749c5d90022d73029287cd36c51d54683339451a75408"
const B_TARGET := "res://scenes/candidate51b/Game51b.tscn"
const B_REPORT := "res://scenes/candidate51b/build-report-51b.json"
const B_CONTROLLER := "res://scripts/lake_reflection51b.gd"
const OLD_MARKER := "(CAMERA_VISIBLE_LAYERS & 524288u) != 0u"
const NEW_MARKER := "(CAMERA_VISIBLE_LAYERS & 524288u) != 0u && (CAMERA_VISIBLE_LAYERS & 262144u) == 0u"
const NativeAudit=preload("res://tools/reflection51b_saved_audit.gd")
var transition_fingerprint := ""
var transition_checks := []
var old51_report := {}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg=="--normal-only":normal_only=true
	call_deferred("run")
func verify_transition_materials() -> bool:
	var valid := true
	var old_rows := {}
	for row in old51_report.material_ledger:old_rows[row.new_material_path]=row
	var new_paths := {}
	var shader_aliases := {}
	var shader_reverse_aliases := {}
	var unique_shader_codes := {}
	for row in build_report.material_ledger:
		var a: ShaderMaterial=ResourceLoader.load(row.prior51_material_path,"ShaderMaterial",ResourceLoader.CACHE_MODE_REUSE)
		var b: ShaderMaterial=ResourceLoader.load(row.new_material_path,"ShaderMaterial",ResourceLoader.CACHE_MODE_REUSE)
		resource_cache.clear()
		var params_equal: bool=a!=null and b!=null and resource_except(a,["shader"])==resource_except(b,["shader"])
		var shader_flags_equal: bool=resource_except(a.shader,["code"])==resource_except(b.shader,["code"])
		var guard_exact: bool=a.shader.code.count(OLD_MARKER)==1 and b.shader.code==a.shader.code.replace(OLD_MARKER,NEW_MARKER) and b.shader.code.replace(NEW_MARKER,OLD_MARKER)==a.shader.code
		var old_shader_path: String=a.shader.resource_path
		var new_shader_path: String=b.shader.resource_path
		var alias_ok: bool=(not shader_aliases.has(old_shader_path) or shader_aliases[old_shader_path]==new_shader_path) and (not shader_reverse_aliases.has(new_shader_path) or shader_reverse_aliases[new_shader_path]==old_shader_path)
		shader_aliases[old_shader_path]=new_shader_path;shader_reverse_aliases[new_shader_path]=old_shader_path;unique_shader_codes[b.shader.code.sha256_text()]=true
		valid=check(alias_ok,"Original shader resource alias topology preserved "+old_shader_path) and valid
		var prior: Dictionary=old_rows.get(row.prior51_material_path,{})
		var lineage: bool=not prior.is_empty() and row.source_fingerprint==prior.source_fingerprint and row.prior51_material_fingerprint==prior.new_fingerprint and row.prior51_material_fingerprint==digest(canonical(a)) and row.new_fingerprint==digest(canonical(b))
		var details:={"source50_fingerprint":row.source_fingerprint,"old51_path":row.prior51_material_path,"new51b_path":row.new_material_path,"all_old_material_values_equal":params_equal,"shader_noncode_flags_equal":shader_flags_equal,"only_exact_reversible_guard":guard_exact,"two_hop_lineage_exact":lineage}
		transition_checks.append(details)
		valid=check(params_equal and shader_flags_equal and guard_exact and lineage,"Independent two-hop material/guard proof "+row.new_material_path,details) and valid
		new_paths[row.new_material_path]=true
	var old_bindings := {}
	for row in old51_report.binding_ledger:old_bindings[row.path+"|"+row.property]=row
	for row in build_report.binding_ledger:
		var prior: Dictionary=old_bindings.get(row.path+"|"+row.property,{})
		valid=check(not prior.is_empty() and row.source_material_fingerprint==prior.source_material_fingerprint and row.prior51_material_path==prior.new_material_path and new_paths.has(row.new_material_path),"Exact50 original fingerprint retained through binding "+row.path+"/"+row.property) and valid
	valid=check(shader_aliases.size()==12 and shader_reverse_aliases.size()==12 and unique_shader_codes.size()==11,"Exactly12 independent shader resources and11unique codes preserve original sharing") and valid
	return check(valid and new_paths.size()==114 and build_report.binding_ledger.size()==248,"All114 materials/248 fields retain exact50-through51 provenance")
func observations() -> void:
	root.size=Vector2i(1180,664)
	root.add_child(game);game.sound_enabled=false;game.test_frozen=true
	game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	check(controller.clip_enabled and controller.reflection_enabled and is_equal_approx(controller.optical_overscan,1.08),"Saved51b defaults enable guarded reflection with optical overscan1.08")
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
			print("REFLECTION51B STOP: whole-material normal/clip-only zero-diff gate failed; reflection visuals not accepted")
			return
	if not normal_only: await reflection_controls()
	apply_bindings(false);controller.set_effect_flags(true,true);depth_controller.set_depth_enabled(true)
	check(controller.clip_enabled and controller.reflection_enabled and depth_controller.depth_enabled,"Runtime restored to saved51b default-on profile")
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
	var report:={"version":"51b-two-hop","scoped_copy_baseline_runtime_passed":scoped and copy_pass and clip_only_pass,"normal_pass_zero_diff":original_zero,"original_resource_normal_pass_zero_diff":original_zero,"copied_material_baseline_conversion_zero_diff":copy_pass,"clip_only_zero_diff":clip_only_pass,"requested_motion_all_passed":requested,"total_acceptance_passed":false,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":B_TARGET,"candidate_sha256":candidate_sha,"unaffected_graph_fingerprint":unchanged_fingerprint,"transition51_to51b_fingerprint":transition_fingerprint,"baseline51_sha256":B_BASE_SHA,"transition_checks":transition_checks,"checks":checks,"failures":failures,"captures":captures,"comparisons":comparisons,"original_resource_differences":original_resource_differences,"copy_resource_differences":copy_resource_differences,"copy_baseline_ledger":copy_ledger,"completed_normal_references":completed_normal_references,"movement_checks":movement_checks,"freeze_physics":freeze_evidence,"material_pair_count":material_pairs.size(),"stored_binding_count":stored_rows.size(),"latest_ready_binding_count":live_rows.size(),"mode_history":mode_history,"normal_only":normal_only,"uniform_sync_ledger":uniform_sync_ledger,"reflection_checks":reflection_checks,"renderer":RenderingServer.get_video_adapter_name(),"hardware_gpu_acceptance":false,"visual_acceptance":false,"complete_flight_passed":false,"dynamic_waterline_straddling_clip_verified":false,"arbitrary_future_stream_instances_verified":false,"scope":"Independent saved51b verifier with two-hop lineage. Full51-to51b graph exact outside independently reproduced248 binding fields and five controller fields; Ocean canonical unmasked. All11450 original material fingerprints verified through immutable51 ledger and51b mapping. Runtime seven-ref native-conversion controls still use actual50 original materials and same-value copies, never converted51 as original. Every original identity difference retained separately; copy-vs-converted, original A/A2 and clip-only require full RGBA zero-diff. Guard/overscan/default-on51b source assets immutable. Limited actual reflection/ship/camera checks follow; dynamic straddling, arbitrary future streams and hardware/fullvisual remain unproven. Required350m inherited failures remain failures.","exit_policy":"exit0 means only copied-resource conversion, restore, clip-only and scoped runtime checks passed; it never overrides original-resource difference, motion failures, visual limits or total_acceptance=false"}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	if is_instance_valid(game):await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51B VERIFIED scoped=",scoped," copied_baseline_zero_diff=",copy_pass," original_zero_diff=",original_zero," clip_only_zero_diff=",clip_only_pass," required_motion=",requested," total=false")
	quit(0 if scoped and copy_pass and clip_only_pass else 1)
func run() -> void:
	if not require(DisplayServer.get_name()!="headless","51b verifier requires real renderer"):quit(2);return
	if not require(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output),"New absolute output directory required"):quit(2);return
	DirAccess.make_dir_recursive_absolute(output);diagnostic_dir=output
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(B_BASE)==B_BASE_SHA and FileAccess.file_exists(B_TARGET),"Baseline50/51 SHA mismatch or51b absent"):await finish();return
	candidate_sha=FileAccess.get_sha256(B_TARGET)
	build_report=JSON.parse_string(FileAccess.get_file_as_string(B_REPORT))
	old51_report=JSON.parse_string(FileAccess.get_file_as_string("res://scenes/candidate51/build-report-51.json"))
	if not check(build_report.get("build_saved_reload_passed",false) and build_report.get("candidate_sha256","")==candidate_sha and build_report.get("baseline_sha256","")==B_BASE_SHA and build_report.get("source50_baseline_sha256","")==BASE_SHA,"51b saved/reloaded report matches both immutable baselines"):await finish();return
	var source50_packed: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var source51_packed: PackedScene=ResourceLoader.load(B_BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var candidate_packed: PackedScene=ResourceLoader.load(B_TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var source50: Node3D=source50_packed.instantiate();var source51: Node3D=source51_packed.instantiate();game=candidate_packed.instantiate();await settle()
	if not discover_bindings(source50):source50.free();source51.free();await finish();return
	original_camera_mask=source50.get_node("Camera").cull_mask;original_ocean_layers=source50.get_node("World/Ocean").layers;candidate_camera_mask=game.get_node("Camera").cull_mask
	var original_graph:=graph_state(source50,source50_packed)
	check(original_graph==graph_state(source50,source50_packed),"Fresh50 canonical double snapshot stable")
	check(original_graph==graph_state(game,candidate_packed),"Full50 stored state exact outside original51 binding/camera/water whitelist")
	unchanged_fingerprint=digest(original_graph)
	var audit:=NativeAudit.new()
	audit.property_masks={NEW_GROUP:["script","clip_enabled","reflection_enabled","optical_overscan","clipping_materials"]}
	for row in old51_report.binding_ledger:
		if not audit.property_masks.has(row.path):audit.property_masks[row.path]=[]
		if not row.property in audit.property_masks[row.path]:audit.property_masks[row.path].append(row.property)
	check(audit.property_masks==build_report.exact_property_masks,"Independent51-to51b exact whitelist reproduced")
	var before: Dictionary=audit.graph_state(source51,source51_packed)
	var after: Dictionary=audit.graph_state(game,candidate_packed)
	check(before==after,"Every51 stored node/resource/owner/group/connection/MM unchanged outside exact51b whitelist",differences(before,after))
	transition_fingerprint=audit.digest(before)
	check(transition_fingerprint==build_report.unaffected_graph_fingerprint and audit.digest(audit.changed_state(game))==build_report.changed_state_fingerprint,"Independent51b retained/intended state fingerprints match real-renderer build")
	check(weather_state(source50)==weather_state(game) and weather_state(source51)==weather_state(game),"All48000 weather floats identical across50/51/51b")
	check(verify_new_inventory(game),"Exactly original three reflection nodes, no new duplicate world")
	check(FileAccess.get_sha256(B_CONTROLLER)==build_report.controller_source_sha256 and game.get_node(NEW_GROUP).get_script().resource_path==B_CONTROLLER,"Independent51b controller source/path exact")
	for asset in build_report.independent_assets:check(FileAccess.get_sha256(asset.path)==asset.sha256,"Independent51b asset unchanged "+asset.path)
	for asset in build_report.source51_assets:check(FileAccess.get_sha256(asset.path)==asset.sha256,"Immutable51 source asset unchanged "+asset.path)
	if not verify_transition_materials() or not prepare_pairs(source50):await settle();source50.free();source51.free();await finish();return
	var previous: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/cloud-evidence/depth50-verify-v2-20261001T010738Z-G3enLm/images/report.json"))
	check(previous.get("candidate_sha256","")==BASE_SHA,"Motion reference evidence belongs to exact50")
	for row in previous.movement_checks:baseline_motions[row.reference+"/"+row.label]=row
	await settle();source50.free();source51.free()
	await observations()
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(B_BASE)==B_BASE_SHA and FileAccess.get_sha256(B_TARGET)==candidate_sha,"All saved50/51/51b scenes unchanged by verification")
	for asset in build_report.independent_assets:check(FileAccess.get_sha256(asset.path)==asset.sha256,"51b asset remains unchanged after runtime "+asset.path)
	for asset in build_report.source51_assets:check(FileAccess.get_sha256(asset.path)==asset.sha256,"51 asset remains unchanged after runtime "+asset.path)
	await finish()

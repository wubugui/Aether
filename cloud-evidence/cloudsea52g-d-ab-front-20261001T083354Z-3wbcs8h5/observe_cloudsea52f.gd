extends "res://tools/verify_cloudsea52e.gd"
## Bounded single-candidate observations after independent saved-state audit.
const F_BASE:="res://scenes/candidate52e/Game52e.tscn"
const F_BASE_SHA:="5abbabf7487766412592f0b93ccd12c01e7bbb70f28e96ffd829e7ae78919079"
const F_TARGET:="res://scenes/candidate52f/Game52f.tscn"
const F_BUILD:="res://scenes/candidate52f/build-report-52f.json"
const F_AUDIT:="res://scenes/candidate52f/verified-saved-52f.json"
var subset:=""
var build_sha:=""
var audit_sha:=""
var default_sha:=""
var extra_recipes:=[]
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--subset="):subset=arg.trim_prefix("--subset=")
	version="52f";call_deferred("run")
func load_single_candidate() -> Node3D:
	var packed:PackedScene=ResourceLoader.load(F_TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	return packed.instantiate()
func write_partial(stage:String,pending:Dictionary={}) -> void:
	if output.is_empty() or not DirAccess.dir_exists_absolute(output):return
	var path:=output.path_join("partial-report.json")
	var data:={"run_complete":false,"stage":stage,"subset":subset,"version":"52f","baseline":F_BASE,"baseline_sha256":F_BASE_SHA,"candidate":F_TARGET,"candidate_sha256":candidate_sha,"build_sha256":build_sha,"fresh_native_audit_sha256":audit_sha,"checks":checks,"captures":captures,"movements":movements,"live_cloud_bindings":live_cloud_bindings,"pending_capture":pending,"renderer":RenderingServer.get_video_adapter_name(),"visual_acceptance":false,"hardware_gpu_acceptance":false,"complete_flight_passed":false,"total_acceptance_passed":false}
	var file:=FileAccess.open(path+".tmp",FileAccess.WRITE)
	if file==null:failed=true;push_error("52f partial report open failed");return
	file.store_string(JSON.stringify(data,"  "));file.flush();file.close()
	if DirAccess.rename_absolute(path+".tmp",path)!=OK:failed=true;push_error("52f atomic partial commit failed")
func check_live_clouds(reference:String) -> void:
	var rows:=[];var material_ids:={};var valid:=true;var old_count:=0;var new_count:=0
	for anchor in game.get_node("SkyRegion39").get_children():
		if not str(anchor.name).begins_with("CloudSea_"):continue
		for mesh in anchor.find_children("*","MeshInstance3D",true,false):
			var material:Material=mesh.get_active_material(0)
			var same_world:bool=mesh.is_inside_tree() and mesh.get_world_3d()==game.get_world_3d()
			var standard:bool=material is StandardMaterial3D
			var lit:bool=standard and material.diffuse_mode==BaseMaterial3D.DIFFUSE_LAMBERT_WRAP and material.vertex_color_use_as_albedo and material.shading_mode==BaseMaterial3D.SHADING_MODE_PER_PIXEL
			valid=valid and same_world and mesh.is_visible_in_tree() and lit and mesh.get_instance().is_valid()
			material_ids[material.get_instance_id()]=true
			if str(mesh.name).begins_with("CloudSea52f_"):new_count+=1
			elif str(mesh.name).begins_with("CloudSea52e_"):old_count+=1
			rows.append({"path":str(game.get_path_to(mesh)),"same_world":same_world,"visible":mesh.is_visible_in_tree(),"lit_vertex_color_wrap":lit,"renderer_instance_valid":mesh.get_instance().is_valid(),"uses_shared_sun_ambient_fog":true})
	check(valid and old_count==75 and new_count==50 and rows.size()==125 and material_ids.size()==3,"125 live parts/75old+50new use3 original materials in sameWorld3D "+reference)
	live_cloud_bindings.append({"reference":reference,"old":old_count,"new":new_count,"material_count":material_ids.size(),"rows":rows})
func prepare_low_recipes() -> void:
	var anchor:Node3D=game.get_node("SkyRegion39/CloudSea_0_0")
	var transform:Transform3D=audit.source_transform(anchor)
	for suffix in ["low_saddle","low_drift"]:
		var mesh:MeshInstance3D=anchor.get_node("CloudSea52f_v2_"+suffix)
		var bounds:AABB=mesh.mesh.get_aabb();var center:Vector3=mesh.transform*bounds.get_center()
		extra_recipes.append({"name":"under-"+suffix,"reference":"1343","position":transform*(center+Vector3(0,-bounds.size.y*.5-90,bounds.size.z*.2)),"target":transform*center,"kind":"under"})
		if suffix=="low_drift":extra_recipes.append({"name":"near-low-drift-side","reference":"1343","position":transform*(center+Vector3(bounds.size.x*.5+130,-bounds.size.y*.1,0)),"target":transform*center,"kind":"under"})
	extra_recipes.append({"name":"low-corridor-y475","reference":"1216","position":transform*Vector3(850,-225,0),"target":transform*Vector3(0,-30,0),"kind":"under"})
func capture(label:String,reference:String,view:String) -> void:
	await super.capture(label,reference,view)
	var projection:Projection=game.camera.get_camera_projection()
	var columns:=[]
	for v in [projection.x,projection.y,projection.z,projection.w]:columns.append([v.x,v.y,v.z,v.w])
	if not captures.is_empty():
		captures[-1].camera_projection_columns=columns
		captures[-1].camera_keep_aspect=game.camera.keep_aspect
		captures[-1].world_chunk_count=game.world.chunks.size()
		captures[-1].world_core_count=game.world.core.size()
	write_partial("capture_complete_with_projection")
func finish() -> void:
	var expected:=4 if subset in ["climb","under"] else 3
	var ok:=not failed and captures.size()==expected
	write_partial("subset_finished")
	var data:={"limited_subset_runtime_passed":ok,"run_complete":true,"subset":subset,"version":"52f","baseline":F_BASE,"baseline_sha256":F_BASE_SHA,"candidate":F_TARGET,"candidate_sha256":candidate_sha,"build_sha256":build_sha,"fresh_native_audit_sha256":audit_sha,"checks":checks,"captures":captures,"movements":movements,"live_cloud_bindings":live_cloud_bindings,"renderer":RenderingServer.get_video_adapter_name(),"single_candidate_only":true,"large_native_audit_repeated_during_capture":false,"visual_acceptance":false,"hardware_gpu_acceptance":false,"complete_flight_passed":false,"total_acceptance_passed":false,"old52e_interrupted_pair_repaired":false,"original350m_gate_passed":false,"prior1344_conversion_gate_passed":false,"scope":"Bounded real saved52f shared-world camera observations. Exactly75 old crowns+50 additive low bodies use original3 material aliases and shared lighting. Each actualPNG atomically recorded. No full2-scene graph retained during _ready/captures. Low bodies can descend to476m; covering an island/root is not success. No cloud shape acceptance, no claim to repair1343/1344 other sky clouds, no player flight. Old52e137 failure and missing9 runtime rows remain unchanged."}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(data,"  "));file.close()
	if DisplayServer.get_name()!="headless":await settle()
	if is_instance_valid(game):game.queue_free()
	await frames(8);print("CLOUDSEA52F OBSERVED ",subset," limited=",ok);quit(0 if ok else 1)
func run() -> void:
	if not check(DisplayServer.get_name()!="headless","Actual renderer required"):quit(2);return
	if not check(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output) and subset in ["1128","1343","1216","close","climb","under"],"New output and bounded subset required"):quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	if not check(FileAccess.get_sha256(F_BASE)==F_BASE_SHA and FileAccess.file_exists(F_TARGET) and FileAccess.file_exists(F_AUDIT),"Exact52e and independently audited52f required"):await finish();return
	candidate_sha=FileAccess.get_sha256(F_TARGET);build_sha=FileAccess.get_sha256(F_BUILD);audit_sha=FileAccess.get_sha256(F_AUDIT);default_sha=FileAccess.get_sha256("res://project.godot")
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(F_BUILD))
	var native:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(F_AUDIT))
	var runner_gate:bool=native.get("audit_version","")=="v3" and native.get("runner_log_gate_passed",false) and native.get("runner_final_gate_passed",false)
	if runner_gate:
		var process_path:String=native.get("process_report_path","")
		runner_gate=FileAccess.file_exists(process_path) and FileAccess.get_sha256(process_path)==native.get("process_report_sha256","")
		if runner_gate:
			var process:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(process_path))
			runner_gate=process.get("python_returncode",-1)==0 and process.get("log_errors",["missing"]).is_empty() and process.get("frozen_inputs_unchanged",false) and process.get("runner_final_gate_passed",false) and process.get("runner_audit_gate_errors",["missing"]).is_empty()
	check(runner_gate,"Final external runner gate proves process0/error-free complete native audit")
	check(build.build_saved_reload_passed and native.saved_native_audit_passed and build.candidate_sha256==candidate_sha and native.candidate_sha256==candidate_sha and native.build_report_sha256==build_sha and build.baseline_sha256==F_BASE_SHA,"Build+fresh audit correspond to this exact52f")
	if failed:await finish();return
	game=load_single_candidate();await settle()
	prepare_supplemental_recipes(game);prepare_low_recipes()
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node("World/LakeReflection51")
	var collisions:=collision_state(game);freeze_tree(game);await physics_frame;await physics_frame
	check(collisions==collision_state(game),"Callback freeze preserves live collision activity")
	collect_cloud_triangles();write_partial("single_candidate_ready")
	if subset in ["1128","1343","1216"]:
		await prepare_view(subset)
		var home:Transform3D=game.camera.global_transform
		await capture(subset+"-front",subset,"front")
		game.camera.rotate_y(deg_to_rad(50));await capture(subset+"-side",subset,"side50")
		game.camera.global_transform=home;game.camera.rotate_y(PI);await capture(subset+"-back",subset,"back180")
		game.camera.global_transform=home
		var start:Vector3=game.camera.global_position
		probe_path(start,start+game.camera.global_basis.x*350.,subset+"-original-plus350m",true);write_partial("original_path_recorded")
	else:
		var selected:Array=extra_recipes if subset=="under" else recipes
		var last_climb:Variant=null
		for recipe in selected:
			if recipe.kind!=subset:continue
			await prepare_view(recipe.reference)
			game.camera.global_position=recipe.position;game.camera.look_at(recipe.target,Vector3.UP)
			await capture(recipe.name,recipe.reference,recipe.kind)
			if subset=="climb":
				if last_climb!=null:probe_path(last_climb,recipe.position,"staged-climb-to-"+recipe.name);write_partial("climb_path_recorded")
				last_climb=recipe.position
		if subset=="under":
			for span in [[475.,650.],[650.,850.]]:probe_path(Vector3(4050,span[0],3000),Vector3(4050,span[1],3000),"low-corridor-%d-to-%d" % [int(span[0]),int(span[1])])
			write_partial("low_paths_recorded")
	check(FileAccess.get_sha256(F_BASE)==F_BASE_SHA and FileAccess.get_sha256(F_TARGET)==candidate_sha and FileAccess.get_sha256(F_BUILD)==build_sha and FileAccess.get_sha256(F_AUDIT)==audit_sha and FileAccess.get_sha256("res://project.godot")==default_sha,"Saved scenes/build/audit/default unchanged")
	await finish()

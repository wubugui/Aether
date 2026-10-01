extends SceneTree
## Three-frame supplementary side observation. Original reference camera untouched.
const SCENE := "res://scenes/candidate51b/Game51b.tscn"
const SHA := "b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1"
const AUDIT := "/workspace/scratch/a29d03198654/Aether/cloud-evidence/reflection51b-motion-20261001T041545Z-WCymsr/images/reflection-motion-report.json"
const MARGIN := 0.12
var game:Node3D
var side_camera:Camera3D
var controller:Node3D
var output:=""
var checks:=[]
var captures:=[]
var trials:=[]
var original_camera:Camera3D
var original_camera_transform:Transform3D
var original_ship_transform:Transform3D
var original_camera_fov:=0.0
var original_controller_camera:Camera3D
var old_controller_process:=false
var bbox_points:=PackedVector3Array()
var selected_pose:={}
func _initialize():
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
	call_deferred("run")
func check(value:bool,label:String,details:Variant=null)->bool:
	checks.append({"passed":value,"name":label,"details":details});print("PASS " if value else "FAIL ",label);return value
func frames(n:int):
	for i in range(n):await process_frame
func freeze(node:Node):
	node.set_process(false);node.set_physics_process(false);node.set_process_input(false);node.set_process_unhandled_input(false)
	if node is AnimationPlayer:node.pause()
	if node is Timer:node.paused=true
	for child in node.get_children():freeze(child)
func points_at_ship()->PackedVector3Array:
	var points:=PackedVector3Array()
	for mesh in game.airship.find_children("*","MeshInstance3D",true,false):
		if mesh.mesh==null or not mesh.is_visible_in_tree():continue
		# Conservative0.5m padding also covers the small procedural flag motion.
		var box:AABB=mesh.get_aabb().grow(.5)
		for i in range(8):points.append(mesh.global_transform*box.get_endpoint(i))
	return points
func mirrored(points:PackedVector3Array)->PackedVector3Array:
	var result:=PackedVector3Array()
	for point in points:result.append(Vector3(point.x,-point.y,point.z))
	return result
func projection_bounds(camera:Camera3D,points:PackedVector3Array)->Dictionary:
	var lo:=Vector2(INF,INF);var hi:=Vector2(-INF,-INF);var positive:=true
	var view:=camera.get_camera_transform().affine_inverse();var projection:=camera.get_camera_projection()
	for point in points:
		var local:=view*point;var clip:=projection*Vector4(local.x,local.y,local.z,1)
		if clip.w<=camera.near:positive=false;continue
		var uv:=Vector2(clip.x/clip.w*.5+.5,.5-clip.y/clip.w*.5)
		lo=lo.min(uv);hi=hi.max(uv)
	return {"min":[lo.x,lo.y],"max":[hi.x,hi.y],"min_margin":minf(minf(lo.x,lo.y),minf(1-hi.x,1-hi.y)),"all_forward":positive,"count":points.size(),"fits":positive and lo.x>=MARGIN and lo.y>=MARGIN and hi.x<=1-MARGIN and hi.y<=1-MARGIN}
func camera_clear(position:Vector3)->bool:
	var q:=PhysicsShapeQueryParameters3D.new();var sphere:=SphereShape3D.new();sphere.radius=.5
	q.shape=sphere;q.transform=Transform3D(Basis.IDENTITY,position);q.collision_mask=5;q.exclude=[game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(q).is_empty()
func sight_clear(position:Vector3,points:PackedVector3Array,virtual_points:bool)->bool:
	var box:=AABB(points[0],Vector3.ZERO)
	for point in points:box=box.expand(point)
	for i in range(8):
		var ray:=PhysicsRayQueryParameters3D.create(position,box.get_endpoint(i),5,[game.airship.get_rid()])
		var hit:=game.get_world_3d().direct_space_state.intersect_ray(ray)
		if not hit.is_empty() and (not virtual_points or hit.position.y>.05):return false
	return true
func select_pose(motion:Vector3)->bool:
	bbox_points=points_at_ship()
	var all:=bbox_points.duplicate();all.append_array(mirrored(bbox_points))
	var moved:=PackedVector3Array()
	for point in bbox_points:moved.append(point+motion)
	all.append_array(moved);all.append_array(mirrored(moved))
	var box:=AABB(all[0],Vector3.ZERO)
	for point in all:box=box.expand(point)
	var target:=box.get_center();target.y=0
	var side:Vector3=game.airship.global_basis.z;side.y=0;side=side.normalized()
	var candidates:=[]
	for sign_value in [1.0,-1.0]:
		var distance:=20.0
		for iteration in range(35):
			var position:Vector3=target+side*sign_value*distance+Vector3.UP*12.0
			side_camera.global_position=position;side_camera.look_at(target)
			var bounds:=projection_bounds(side_camera,all)
			var valid:bool=bounds.fits and camera_clear(position)
			if valid:valid=sight_clear(position,bbox_points,false) and sight_clear(position,moved,false) and sight_clear(position,mirrored(bbox_points),true) and sight_clear(position,mirrored(moved),true)
			trials.append({"side_sign":sign_value,"distance":distance,"position":str(position),"projection":bounds,"accepted":valid})
			if valid:
				candidates.append({"transform":side_camera.global_transform,"distance":distance,"target":target,"side_sign":sign_value,"bounds":bounds});break
			distance*=1.1
	if candidates.is_empty():return check(false,"No clear side pose fits complete real and virtual ship bounds with12percent margin",trials)
	var chosen:Dictionary=candidates[0]
	for option in candidates:
		if option.distance<chosen.distance:chosen=option
	side_camera.global_transform=chosen.transform;controller.main_camera=side_camera;side_camera.make_current();controller.refresh_now()
	selected_pose={"camera_transform":str(side_camera.global_transform),"target":str(chosen.target),"distance":chosen.distance,"side_sign":chosen.side_sign,"fov":side_camera.fov,"near":side_camera.near,"far":side_camera.far,"keep_aspect":side_camera.keep_aspect,"required_margin":MARGIN,"combined_original_moved_and_mirrored_bounds":chosen.bounds,"selection":"Actual118visible-mesh local AABB corners transformed to world with0.5m padding; both ship poses and their Y0 mirrors fit; actual physics camera and silhouette-corner sight checks"}
	return check(true,"Selected actual-bounds side pose, preserving original camera and ship pose",selected_pose)
func capture(label:String)->Dictionary:
	for i in range(8):controller.refresh_now();await process_frame
	await physics_frame;await RenderingServer.frame_post_draw
	var ship_points:=points_at_ship();var virtual_points:=mirrored(ship_points)
	var main_real:=projection_bounds(side_camera,ship_points);var main_mirror:=projection_bounds(side_camera,virtual_points)
	var raw_real:=projection_bounds(controller.reflection_camera,ship_points)
	check(main_real.fits and main_mirror.fits and raw_real.fits,"Entire padded ship and reflected silhouette have12percent viewport margin "+label,{"main_ship":main_real,"main_virtual_mirror":main_mirror,"raw_reflection_ship":raw_real})
	check(controller.effective_reflection and controller.viewport.world_3d==game.get_world_3d(),"Live reflection shares actual World3D "+label)
	var main:Image=root.get_texture().get_image();main.convert(Image.FORMAT_RGBA8)
	var raw:Image=controller.viewport.get_texture().get_image();raw.convert(Image.FORMAT_RGBA8)
	var file:=output.path_join(label+".png");check(main.save_png(file)==OK,"Saved actual full-silhouette image "+label)
	captures.append({"name":label,"path":file,"sha256":FileAccess.get_sha256(file),"main_ship_bounds":main_real,"main_mirror_bounds":main_mirror,"raw_reflection_bounds":raw_real,"ship_transform":str(game.airship.global_transform),"camera_transform":str(side_camera.global_transform),"main_size":str(main.get_size()),"raw_size":str(raw.get_size())})
	return {"main":main.get_data(),"raw":raw.get_data()}
func finish():
	if is_instance_valid(game) and original_camera!=null:
		game.airship.global_transform=original_ship_transform
		controller.main_camera=original_controller_camera;original_camera.make_current();controller.refresh_now()
		check(game.airship.global_transform==original_ship_transform and original_camera.global_transform==original_camera_transform and original_camera.fov==original_camera_fov,"Original reference1129 ship/camera transforms and FOV restored exactly")
		if is_instance_valid(side_camera):side_camera.queue_free()
	var passed:=true
	for row in checks:passed=passed and row.passed
	var report:={"limited_full_silhouette_dynamic_passed":passed,"candidate_sha256":SHA,"scene_unchanged":FileAccess.get_sha256(SCENE)==SHA,"prior_full_audit":AUDIT,"prior_audit_sha256":FileAccess.get_sha256(AUDIT),"checks":checks,"selected_pose":selected_pose,"camera_trials":trials,"captures":captures,"supplementary_only":true,"reference1128_1129_camera_changed":false,"temporary_pose_saved":false,"conversion_pixel_gate_passed":false,"requested350m_motion_passed":false,"reference_composition_acceptance":false,"total_acceptance_passed":false,"scope":"Three actual side-view A/B/A2 images of original1129 ship pose plus8m longitudinal/.75m upward movement. New runtime camera selected using actual padded visible-mesh bounds for complete ship and Y0 mirror in main and reflection frusta. Original fixed camera is never transformed. No scene/asset save; previous immutable audit reused, not rerun."}
	if not output.is_empty():
		var f:=FileAccess.open(output.path_join("full-silhouette-report.json"),FileAccess.WRITE)
		if f!=null:f.store_string(JSON.stringify(report,"  "));f.close()
	if is_instance_valid(game):
		await frames(3);await RenderingServer.frame_post_draw;game.queue_free();await frames(8)
	print("FULL SHIP REFLECTION SUPPLEMENT complete=",passed," total=false");quit(0 if passed else 1)
func run():
	if DisplayServer.get_name()=="headless":quit(2);return
	if not output.is_absolute_path() or DirAccess.dir_exists_absolute(output):quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	if not check(FileAccess.get_sha256(SCENE)==SHA,"Exact saved51b scene identity"):await finish();return
	var audit:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(AUDIT))
	if not check(audit.candidate_sha256==SHA and audit.limited_reflection_motion_runtime_passed,"Reuse completed matching structural/reflection audit"):await finish();return
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://scenes/candidate51b/build-report-51b.json"))
	for asset in build.independent_assets:
		if not check(FileAccess.get_sha256(asset.path)==asset.sha256,"Unchanged51b asset "+asset.path):await finish();return
	if not check(FileAccess.get_sha256("res://scripts/lake_reflection51b.gd")==build.controller_source_sha256,"Unchanged51b controller"):await finish();return
	root.size=Vector2i(1180,664)
	game=load(SCENE).instantiate();root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0
	await frames(20);await RenderingServer.frame_post_draw
	game.observe_reference("1129");game.get_node("Weather42b").seek_time(0);game.get_node("Weather42b").seek_time(.35);game.get_node("Weather42b")._process(0)
	RenderingServer.global_shader_parameter_set("world_time",.35)
	await frames(5);freeze(game);await physics_frame
	original_camera=game.camera;original_camera_transform=original_camera.global_transform;original_camera_fov=original_camera.fov;original_ship_transform=game.airship.global_transform
	controller=game.get_node("World/LakeReflection51");original_controller_camera=controller.main_camera
	game.get_node("World/LakeDepth50").set_depth_enabled(true);controller.set_effect_flags(true,true)
	side_camera=Camera3D.new();side_camera.name="SupplementFullShipCamera";side_camera.fov=55;side_camera.near=.35;side_camera.far=original_camera.far;side_camera.keep_aspect=original_camera.keep_aspect;side_camera.cull_mask=original_camera.cull_mask
	side_camera.environment=original_camera.environment;side_camera.attributes=original_camera.attributes;game.add_child(side_camera)
	var motion:Vector3=game.airship.global_basis.x.normalized()*8.0+Vector3.UP*.75
	if not select_pose(motion):await finish();return
	if not check(not game.airship.test_move(original_ship_transform,motion),"Actual existing ship collision shapes permit supplemental8m motion"):await finish();return
	var a:=await capture("supplement-A-original-ship")
	game.airship.global_transform=Transform3D(original_ship_transform.basis,original_ship_transform.origin+motion);await physics_frame
	var b:=await capture("supplement-B-moved-ship")
	game.airship.global_transform=original_ship_transform;await physics_frame
	var a2:=await capture("supplement-A2-restored-ship")
	check(a.main!=b.main and a.raw!=b.raw,"Actual ship movement changes main and reflected pixels")
	check(a.main==a2.main and a.raw==a2.raw,"Original full ship and raw reflection restore pixel-exactly")
	check(FileAccess.get_sha256(SCENE)==SHA,"Saved51b file remains unchanged")
	await finish()

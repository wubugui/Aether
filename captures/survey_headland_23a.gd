extends SceneTree
## Screen anchors are design constraints; original ground is independently ray measured.
var game:Node3D
func _initialize() -> void:call_deferred("survey")
func point(a:Array) -> Vector3:return Vector3(a[0],a[1],a[2])
func hit(at:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(at.x,300,at.z),Vector3(at.x,-50,at.z),4)
	var result:=game.get_world_3d().direct_space_state.intersect_ray(query);assert(not result.is_empty())
	return {"position":[result.position.x,result.position.y,result.position.z],"collider":str(result.collider.get_path()),"normal":[result.normal.x,result.normal.y,result.normal.z]}
func survey() -> void:
	var source:="";var output:="";var identity:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--survey="):source=arg.trim_prefix("--survey=")
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
	assert(not source.is_empty() and not output.is_empty() and not identity.is_empty())
	assert(not FileAccess.file_exists(output.path_join("headland.json")))
	var prior:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(source))
	assert(prior.world_sha256==FileAccess.get_sha256("res://scenes/world/World.tscn"))
	game=load("res://scenes/game.tscn").instantiate();game.set_script(null);game.get_node("World").set_script(null)
	game.get_node("Airship").visible=false;root.add_child(game);game.get_node("Airship").set_physics_process(false)
	await physics_frame;await physics_frame;await physics_frame
	var camera:Camera3D=game.get_node("Camera");camera.position=point(prior.camera.position);camera.rotation=point(prior.camera.rotation);camera.fov=prior.camera.fov
	var definitions:Array=[
		["foreground rock toe",Vector2(1450,910),[3.,6.,10.]],
		["foreground low waterfront houses",Vector2(1470,850),[7.,10.,13.]],
		["foreground upper houses",Vector2(1560,810),[12.,16.,20.]],
		["middle bay village",Vector2(1490,680),[4.,7.,10.]],
		["middle headland shoulder",Vector2(1600,610),[14.,22.,30.]],
		["far sheltered working quay",Vector2(1320,525),[2.,4.,6.]],
		["far coastal light chain",Vector2(1180,485),[2.,5.,8.]]]
	var anchors:Array=[]
	for definition in definitions:
		var screen:Vector2=definition[1];var origin:Vector3=camera.project_ray_origin(screen);var direction:Vector3=camera.project_ray_normal(screen)
		for height in definition[2]:
			assert(direction.y<0.);var distance:float=(float(height)-origin.y)/direction.y;assert(distance>0)
			var designed:Vector3=origin+direction*distance;var probes:Array=[]
			for offset in [Vector3.ZERO,Vector3(-5,0,-5),Vector3(5,0,-5),Vector3(-5,0,5),Vector3(5,0,5)]:probes.append(hit(designed+offset))
			var reprojection:Vector2=camera.unproject_position(designed)
			anchors.append({"role":definition[0],"screen_target_px":[screen.x,screen.y],"assumed_design_y":height,"proposed_position":[designed.x,designed.y,designed.z],"ray_distance_m":distance,"reprojection_error_px":reprojection.distance_to(screen),"original_ground_probes":probes})
	var grid:Array=[]
	for z in range(-2105,-1664,15):
		for x in range(-2390,-1969,15):grid.append(hit(Vector3(x,0,z)))
	for i in range(20):await process_frame
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("reference-before.png"))==OK)
	var file:=FileAccess.open(output.path_join("headland.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"run_id":identity,"world_sha256":prior.world_sha256,"source_reference_record":source,"camera":prior.camera,"keep_aspect":camera.keep_aspect,"viewport_size":[root.size.x,root.size.y],"anchors":anchors,"grid":grid,"scope":"Proposed reference screen anchors at several assumed design heights. Exact original-game positions are not inferred. Projection and original World ground are measured in native Godot; local terrain/geometry unchanged."},"  "));file.close()
	print("HEADLAND PROJECTION SURVEY ",anchors.size()," anchor-height alternatives and ",grid.size()," terrain samples");quit()

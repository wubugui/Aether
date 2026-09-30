extends SceneTree
## Read the native northwest coast before placing islands; never generate or save terrain.
func _initialize() -> void:call_deferred("survey")
func survey() -> void:
	var output:=""
	var identity:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
	assert(not output.is_empty() and not identity.is_empty())
	assert(not FileAccess.file_exists(output.path_join("survey.json")))
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	game.set_script(null)
	var world:Node3D=game.get_node("World")
	world.set_script(null)
	game.get_node("Airship").visible=false
	root.add_child(game)
	game.get_node("Airship").set_physics_process(false)
	await physics_frame;await physics_frame;await physics_frame
	var points:Array=[]
	for z in range(-3200,-999,50):
		for x in range(-3200,-399,50):
			var query:=PhysicsRayQueryParameters3D.create(Vector3(x,1800,z),Vector3(x,-500,z),4)
			var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
			points.append({"x":x,"z":z,"height":null if hit.is_empty() else hit.position.y,"collider":null if hit.is_empty() else str(hit.collider.get_path())})
	var camera:Camera3D=game.get_node("Camera")
	camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=3200;camera.far=10000
	camera.position=Vector3(-1800,2200,-2100)
	camera.look_at(Vector3(-1800,0,-2100),Vector3.FORWARD)
	for i in range(20):await process_frame
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("topdown.png"))==OK)
	var tower:Node3D=world.get_node("Settlements/lighthouse_57220")
	camera.projection=Camera3D.PROJECTION_PERSPECTIVE;camera.fov=65
	camera.position=tower.global_position+Vector3(-180,150,220)
	camera.look_at(tower.global_position+Vector3(-100,0,-100))
	for i in range(20):await process_frame
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("coast-oblique.png"))==OK)
	var file:=FileAccess.open(output.path_join("survey.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"run_id":identity,"scope":"Read-only native terrain mask-4 survey at 50m spacing and actual world cameras. Null means no authored terrain collision at this sample, not ocean-depth proof. No generated terrain, scene writes or original-reference geographical claims.","world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"lighthouse_model_sha256":FileAccess.get_sha256("res://assets/models/lighthouse.glb"),"ocean_y":0,"native_lighthouse_position":[tower.position.x,tower.position.y,tower.position.z],"grid_x":[-3200,-400],"grid_z":[-3200,-1000],"spacing_m":50,"samples":points},"  "));file.close()
	print("NATIVE COAST SURVEY PASS ",points.size()," terrain samples / 2 actual GPU views")
	quit()

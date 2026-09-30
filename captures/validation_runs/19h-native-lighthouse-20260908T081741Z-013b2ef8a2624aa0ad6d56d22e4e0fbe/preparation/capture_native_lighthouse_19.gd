extends SceneTree
## Photograph the persisted prefab at both existing world placements.
func _initialize() -> void:call_deferred("capture")
func capture() -> void:
	var output:=""
	var view:="front"
	var site:="harbor"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
		if arg.begins_with("--view="):view=arg.trim_prefix("--view=")
		if arg.begins_with("--site="):site=arg.trim_prefix("--site=")
	assert(not output.is_empty() and not FileAccess.file_exists(output))
	assert(site in ["harbor","remote"])
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	game.set_script(null)
	var tower:Node3D=game.get_node("World/Settlements/"+("lighthouse_57152" if site=="harbor" else "lighthouse_57220"))
	game.get_node("Airship").visible=false
	root.add_child(game)
	game.get_node("Airship").set_physics_process(false)
	assert(tower.surface_material==null)
	var parts:=tower.get_node("Model").find_children("*","MeshInstance3D",true,false)
	assert(parts.size()==24)
	var camera:Camera3D=game.get_node("Camera")
	var anchor:Vector3=tower.global_position
	var offsets:={"front":Vector3(33,24,39),"back":Vector3(-31,28,-39),"gallery":Vector3(12,25,14),"context":Vector3(85,49,98),"door":Vector3(13,5,-6)}
	assert(offsets.has(view))
	camera.position=anchor+offsets[view]
	camera.look_at(anchor+Vector3(0,23 if view=="gallery" else 13,0))
	if view=="door":camera.look_at(anchor+Vector3(3,1.8,-1.2))
	camera.fov=50
	for i in range(50):await process_frame
	await RenderingServer.frame_post_draw
	var result:=root.get_texture().get_image().save_png(output)
	print("NATIVE LIGHTHOUSE ",site," ",view," meshes=",parts.size()," position=",anchor," image_status=",result)
	quit(result)

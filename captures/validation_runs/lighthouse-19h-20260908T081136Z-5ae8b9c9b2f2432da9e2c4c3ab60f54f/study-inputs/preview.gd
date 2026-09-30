extends SceneTree
## Runtime-only substitution at the existing world's harbor lighthouse.
func _initialize() -> void:call_deferred("preview")
func preview() -> void:
	var directory:=""
	var output:=""
	var view:="front"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--study-dir="):directory=arg.trim_prefix("--study-dir=")
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
		if arg.begins_with("--view="):view=arg.trim_prefix("--view=")
	assert(not directory.is_empty() and not output.is_empty())
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	game.set_script(null)
	var old:Node3D=game.get_node("World/Settlements/lighthouse_57152")
	var placement:Transform3D=old.transform
	old.get_parent().remove_child(old);old.free()
	var document:=GLTFDocument.new()
	var state:=GLTFState.new()
	assert(document.append_from_file(directory.path_join("lighthouse.glb"),state)==OK)
	var tower:Node3D=document.generate_scene(state)
	tower.name="Lighthouse19Candidate";tower.transform=placement
	tower.set_script(load("res://scripts/asset_instance.gd"))
	tower.asset_kind="lighthouse"
	game.get_node("World/Settlements").add_child(tower)
	var parts:=tower.find_children("*","MeshInstance3D",true,false)
	for part in parts:part.create_trimesh_collision()
	game.get_node("Airship").visible=false
	root.add_child(game)
	game.get_node("Airship").set_physics_process(false)
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
	print("LIGHTHOUSE STUDY ",view," meshes=",parts.size()," position=",anchor," image_status=",result)
	quit(result)

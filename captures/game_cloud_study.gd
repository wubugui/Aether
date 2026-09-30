extends "res://scripts/game.gd"
func capture_scene() -> void:
	var view:="opening";var output:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--view="):view=arg.trim_prefix("--view=")
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
	if view=="opening":
		super.capture_scene();return
	assert(view in ["cloud-side","cloud-back"] and not output.is_empty())
	for i in range(80):await get_tree().process_frame
	set_process(false);set_physics_process(false)
	var center:Vector3=world.get_node("Clouds/cloud_primary_57323").global_position
	camera.position=center+Vector3(-510,70,190) if view=="cloud-side" else center+Vector3(90,140,-590)
	camera.look_at(center+Vector3(5,0,0))
	await RenderingServer.frame_post_draw
	var result:=get_viewport().get_texture().get_image().save_png(output)
	print("GAME CAPTURE ",view," ",output," status=",result)
	get_tree().quit(result)

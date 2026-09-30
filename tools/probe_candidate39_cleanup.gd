extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var path := "res://captures/candidate_opening38/Game38.tscn"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--scene="): path = arg.trim_prefix("--scene=")
	var scene: Node = load(path).instantiate()
	print("PROBE SOURCE ",path," child count ",scene.find_children("*","Node",true,false).size())
	scene.free()
	await process_frame
	await process_frame
	Node.print_orphan_nodes()
	quit()

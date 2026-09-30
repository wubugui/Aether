extends SceneTree
func _initialize() -> void:
	for path in ["res://assets/world.glb", "res://assets/airship.glb", "res://assets/propeller.glb"]:
		var model: Node = load(path).instantiate()
		root.add_child(model)
		model.print_tree_pretty()
		model.queue_free()
	quit()

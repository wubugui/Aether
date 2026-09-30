extends SceneTree
## Candidate-only assembly. The saved World and production prefabs stay intact.

func _initialize() -> void:
	call_deferred("preview")

func preview() -> void:
	var directory := ""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--study-dir="):
			directory = argument.trim_prefix("--study-dir=")
	assert(not directory.is_empty(), "A frozen study directory is required")
	var items: Array = JSON.parse_string(FileAccess.get_file_as_string(directory.path_join("manifest.json")))
	assert(items.size() == 3)
	var game: Node3D = load("res://scenes/game.tscn").instantiate()
	for item in items:
		var asset: Node3D = game.get_node("World/Cliffs/" + item.name)
		var prior: Node3D = asset.get_node("Model")
		var pose := prior.transform
		asset.remove_child(prior)
		prior.free()
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		assert(document.append_from_file(directory.path_join(item.name + ".glb"), state) == OK)
		var model: Node3D = document.generate_scene(state)
		model.name = "Model"
		model.transform = pose
		asset.add_child(model)
		var faces := PackedVector3Array()
		for mesh in model.find_children("*", "MeshInstance3D", true, false):
			var local_to_asset := Transform3D.IDENTITY
			var current: Node3D = mesh
			while current != asset:
				local_to_asset = current.transform * local_to_asset
				current = current.get_parent()
			for vertex in mesh.mesh.get_faces():
				faces.append(local_to_asset * vertex)
		assert(not faces.is_empty())
		var shape := ConcavePolygonShape3D.new()
		shape.backface_collision = true
		shape.set_faces(faces)
		asset.get_node("Collision/Shape").shape = shape
		print("FOREGROUND CANDIDATE INSTANCED ", item.name, " collision_faces=", faces.size() / 3)
	root.add_child(game)

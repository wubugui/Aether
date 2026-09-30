extends SceneTree
## Temporary GLB replacements only; Godot remains the world assembly authority.
func _initialize() -> void:
	call_deferred("preview")
func preview() -> void:
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	var models:Array=JSON.parse_string(FileAccess.get_file_as_string("D:/test6/captures/mountain_study_11a/manifest.json"))
	for item in models:
		var asset:Node3D=game.get_node("World/Mountains/"+item.name)
		var prior:Node3D=asset.get_node("Model");var pose:=prior.transform
		asset.remove_child(prior);prior.free()
		var document:=GLTFDocument.new();var state:=GLTFState.new()
		assert(document.append_from_file("D:/test6/captures/mountain_study_11a/"+item.name+".glb",state)==OK)
		var model:Node3D=document.generate_scene(state);model.name="Model";model.transform=pose;asset.add_child(model)
		var faces:=PackedVector3Array()
		for mesh in model.find_children("*","MeshInstance3D",true,false):
			for p in mesh.mesh.get_faces():faces.append(p)
		var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(faces)
		asset.get_node("Collision/Shape").shape=shape
	root.add_child(game)

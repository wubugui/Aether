extends SceneTree
func _initialize() -> void:call_deferred("preview")
func preview() -> void:
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	game.set_script(load("res://captures/game_cloud_study.gd"))
	var items:Array=JSON.parse_string(FileAccess.get_file_as_string("D:/test6/captures/cloud_study_14b/manifest.json"))
	for item in items:
		var asset:Node3D=game.get_node("World/Clouds/"+item.instance)
		var material:=ShaderMaterial.new();material.shader=load("res://captures/cloud_surface_14b.gdshader");asset.surface_material=material
		var prior:Node3D=asset.get_node("Model");var pose:=prior.transform
		asset.remove_child(prior);prior.free()
		var document:=GLTFDocument.new();var state:=GLTFState.new()
		assert(document.append_from_file("D:/test6/captures/cloud_study_14b/"+item.name+".glb",state)==OK)
		var model:Node3D=document.generate_scene(state);model.name="Model";model.transform=pose;asset.add_child(model)
	root.add_child(game)

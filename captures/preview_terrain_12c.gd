extends SceneTree
## Read-only terrain material study, expressed in actual world-space biomes.
func _initialize() -> void:call_deferred("preview")
func preview() -> void:
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	var shader:=Shader.new();shader.code=FileAccess.get_file_as_string("res://captures/terrain_grade_12c.gdshader")
	var material:=ShaderMaterial.new();material.shader=shader
	for tile in game.get_node("World/Terrain").get_children():tile.surface_material=material
	root.add_child(game)

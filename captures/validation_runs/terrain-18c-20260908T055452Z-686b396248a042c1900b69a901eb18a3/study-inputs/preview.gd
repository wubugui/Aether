extends SceneTree
## Temporary real-world terrain material study. Does not save resources.
var study_material:ShaderMaterial
func _initialize() -> void:call_deferred("preview")
func preview() -> void:
	var study_dir:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--study-dir="):study_dir=arg.trim_prefix("--study-dir=")
	assert(not study_dir.is_empty())
	var shader:=Shader.new()
	shader.code=FileAccess.get_file_as_string(study_dir.path_join("terrain.gdshader"))
	assert(not shader.code.is_empty())
	study_material=ShaderMaterial.new();study_material.shader=shader
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	var tiles:=game.get_node("World/Terrain").get_children()
	for tile in tiles:tile.surface_material=study_material
	node_added.connect(apply_streamed_material)
	root.add_child(game)
	print("TERRAIN STUDY MATERIAL APPLIED ",tiles.size()," native tiles; generated terrain uses same study material")
func apply_streamed_material(node:Node) -> void:
	if node is MeshInstance3D and node.name.begins_with("Generated_ground_"):
		node.material_override=study_material

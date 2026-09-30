extends SceneTree
func _initialize() -> void:
	var scene=load("res://assets/open_world.glb").instantiate()
	var math=load("res://scripts/world_math.gd").new()
	math.configure(JSON.parse_string(FileAccess.get_file_as_string("res://assets/world_layout.json")))
	for node in scene.find_children("*","MeshInstance3D",true,false):
		if node.name!="Ground_6_2":continue
		var arrays=node.mesh.surface_get_arrays(0)
		var ids:PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
		var v:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var point:Vector3=(v[ids[0]]+v[ids[1]]+v[ids[2]])/3+node.position
		var normal:Vector3=arrays[Mesh.ARRAY_NORMAL][0]
		var imported:Color=arrays[Mesh.ARRAY_COLOR][0]
		var generated:Color=math.terrain_color(point,normal)
		print("IMPORT COLOR ",imported," GENERATED ",generated," GENERATED AS SRGB ",generated.linear_to_srgb()," POSITION ",point)
		print("WINDING NORMAL ",(v[ids[1]]-v[ids[0]]).cross(v[ids[2]]-v[ids[0]]).normalized()," STORED NORMAL ",normal)
	scene.free()
	quit()

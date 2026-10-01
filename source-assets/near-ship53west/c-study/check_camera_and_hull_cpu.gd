extends SceneTree
## Lightweight headless numerical/API check; no scene or rendered viewport.
func _initialize(): call_deferred("run")
func run():
	var parent := Node3D.new(); root.add_child(parent)
	var camera := Camera3D.new(); parent.add_child(camera)
	var rows := []
	for spec in [[Vector3(1150,10,-1000),Vector3(1150,160,-2600)], [Vector3(1300,7,-950),Vector3(1000,120,-2400)]]:
		camera.position = spec[0]; camera.look_at(spec[1])
		var matrix := camera.transform; var original_global := camera.global_transform
		var position := camera.position; var rotation := camera.rotation; var scale := camera.scale
		var after_getters := camera.transform
		camera.position.y = 2.0; camera.rotation.x = deg_to_rad(2.0)
		camera.position = position; camera.scale = scale; camera.look_at(spec[1])
		rows.append({"local_matrix_exact": camera.transform == matrix, "global_matrix_exact": camera.global_transform == original_global,
			"position_exact": camera.position == position, "rotation_exact": camera.rotation == rotation, "scale_exact": camera.scale == scale,
			"original_rotation": [rotation.x,rotation.y,rotation.z], "restored_rotation": [camera.rotation.x,camera.rotation.y,camera.rotation.z], "original_scale": [scale.x,scale.y,scale.z], "restored_scale": [camera.scale.x,camera.scale.y,camera.scale.z], "after_getters_matrix_bytes": var_to_bytes(after_getters).hex_encode(), "matrix_bytes": var_to_bytes(matrix).hex_encode(), "restored_matrix_bytes": var_to_bytes(camera.transform).hex_encode()})
	var points := PackedVector3Array()
	for x in [-1,0,1]:
		for y in [-1,0,1]:
			for z in [-1,0,1]: points.append(Vector3(x,y,z))
	var shape := ConvexPolygonShape3D.new(); shape.points = points
	var mesh: ArrayMesh = shape.get_debug_mesh(); var unique := {}
	for surface in range(mesh.get_surface_count()):
		var arrays := mesh.surface_get_arrays(surface)
		for vertex in arrays[Mesh.ARRAY_VERTEX]: unique[vertex] = true
	var ok := unique.size() == 8
	for row in rows:
		ok = ok and row.local_matrix_exact and row.global_matrix_exact and row.position_exact and row.rotation_exact and row.scale_exact
	print(JSON.stringify({"passed": ok, "camera_restore": rows, "convex_input_points": points.size(), "convex_unique_support_vertices": unique.size(), "full_game_loaded": false, "renderer_used": false}, "  "))
	parent.free(); quit(0 if ok else 1)

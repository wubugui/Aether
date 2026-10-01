extends SceneTree
## Tiny headless Node3D numerical probe. Never loads the game or a renderer.
func record(node: Node3D) -> Dictionary:
	var t := node.global_transform
	var scale := node.scale
	return {"basis": [t.basis.x.x, t.basis.x.y, t.basis.x.z, t.basis.y.x, t.basis.y.y, t.basis.y.z, t.basis.z.x, t.basis.z.y, t.basis.z.z], "scale": [scale.x, scale.y, scale.z], "rotation": [node.rotation.x, node.rotation.y, node.rotation.z], "local_bytes": var_to_bytes(node.transform).hex_encode()}
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var parent := Node3D.new()
	root.add_child(parent)
	var node := Node3D.new()
	parent.add_child(node)
	node.position = Vector3(1150, 35.2008857727051, -1119.47607421875)
	node.rotation.y = 1.6
	var original := node.global_transform
	var original_local := node.transform
	var original_scale := node.scale
	var original_rotation := node.rotation
	var original_position := node.position
	var a := record(node)
	node.global_transform = Transform3D(Basis(Vector3.UP, 0).scaled(original_scale), Vector3(1163.467, 16.8059, -1041.704))
	node.global_transform = original
	var restored_matrix := record(node)
	var exact_matrix: bool = node.global_transform == original
	var exact_derived_scale: bool = node.scale == original_scale
	node.position = original_position
	node.rotation = original_rotation
	node.scale = original_scale
	var restored_components := record(node)
	print(JSON.stringify({"source": "Three nodes only; no PackedScene, game, assets or rendered viewport", "A": a, "matrix_restore": restored_matrix, "matrix_restore_exact_global": exact_matrix, "matrix_restore_exact_derived_scale": exact_derived_scale,
		"component_restore": restored_components, "component_restore_exact_global": node.global_transform == original, "component_restore_exact_local": node.transform == original_local, "component_restore_exact_scale": node.scale == original_scale, "component_restore_exact_rotation": node.rotation == original_rotation}, "  "))
	parent.free()
	quit()

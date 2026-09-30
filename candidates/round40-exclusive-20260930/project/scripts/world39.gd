@tool
extends "res://scripts/open_world.gd"
## Candidate-specific materials also govern terrain/vegetation streamed later.
@export var stream_terrain_material: Material
@export var stream_world_material: Material
@export var stream_cloud_material: Material

func apply_chunk_data(cell: Vector2i, data: Dictionary) -> MeshInstance3D:
	var mesh := super.apply_chunk_data(cell, data)
	if stream_terrain_material != null: mesh.material_override = stream_terrain_material
	return mesh

func add_multimesh(kind: String, cell: Vector2i, entries: Array) -> MultiMeshInstance3D:
	var node := super.add_multimesh(kind, cell, entries)
	var chosen: Material = stream_cloud_material if kind.begins_with("cloud") else stream_world_material
	if chosen != null: node.material_override = chosen
	return node

func new_model(entry: Array) -> Node3D:
	var node := super.new_model(entry)
	if stream_world_material != null:
		if node.get_script() == load("res://scripts/asset_instance.gd"):
			node.surface_material = stream_world_material
		for mesh in node.find_children("*", "MeshInstance3D", true, false):
			mesh.material_override = stream_world_material
	return node

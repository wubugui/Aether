@tool
extends Node3D
## Reusable engine prefab. The imported model, material and collider are
## children/resources of this scene; world transforms are saved by Godot.
@export var asset_kind := ""
@export var surface_material: Material

func _ready() -> void:
	if surface_material:
		for node in find_children("*","MeshInstance3D",true,false):node.material_override=surface_material

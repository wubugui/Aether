@tool
extends CharacterBody3D
## Engine-owned player prefab: editable visual models, solid collision shapes
## and animated propeller. The game controller supplies the flight inputs.
@export var hull_material:Material=preload("res://materials/ship.tres")
@export var cloth_material:Material=preload("res://materials/flag.tres")

func _ready() -> void:
	for part in $Visuals.find_children("*","MeshInstance3D",true,false):
		if part.get_meta("persistent_material40",false): continue
		part.material_override=cloth_material if part.name=="Flag" else hull_material

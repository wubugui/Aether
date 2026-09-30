@tool
extends Marker3D
## Move this marker in Godot to author a docking destination.
@export var port_id := ""
@export var display_name := ""
@export var landmark_style := ""
@export var ground_offset := 19.0
@export var inner_radius := 46.0
@export var outer_radius := 100.0

func definition() -> Dictionary:
	return {"id":port_id,"name":display_name,"style":landmark_style,"x":global_position.x,"z":global_position.z,"pad_y":global_position.y,"ground":global_position.y-ground_offset,"inner_radius":inner_radius,"outer_radius":outer_radius}

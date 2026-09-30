extends "res://tools/assemble_world.gd"
## Read native Godot placement for Blender's terrain-drape authoring pass.
func build() -> void:
	var world:Node3D=load("res://scenes/world/World.tscn").instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var result:Array=[]
	for part in world.get_node("LandDetails").get_children():
		var transform:=transform_to(part,world)
		result.append({"name":str(part.name),"asset":part.get_node("Model").scene_file_path.trim_prefix("res://"),
			"basis":[[transform.basis.x.x,transform.basis.y.x,transform.basis.z.x],[transform.basis.x.y,transform.basis.y.y,transform.basis.z.y],[transform.basis.x.z,transform.basis.y.z,transform.basis.z.z]],
			"origin":[transform.origin.x,transform.origin.y,transform.origin.z]})
	var file:=FileAccess.open("res://assets/land_detail_authoring.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close()
	world.free();print("READ NATIVE LAND DETAIL PLACEMENTS ",result.size());quit()

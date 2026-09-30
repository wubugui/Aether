extends "res://tools/assemble_world.gd"
## Read native saved curves; moving their parent remains part of the geometry.
func build() -> void:
	var world:Node3D=load("res://scenes/world/World.tscn").instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var result:Array=[]
	for route in world.get_node("Routes").get_children():
		var transform:=transform_to(route,world);var points:Array=[]
		for p in route.curve.get_baked_points():
			var q:Vector3=transform*p;points.append([q.x,q.y,q.z])
		result.append({"name":str(route.name),"points":points,"width":route.get_meta("width_metres",2.0)})
	var file:=FileAccess.open("res://assets/road_routes.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close()
	world.free();print("EXPORTED NATIVE ROAD CURVES ",result.size());quit()

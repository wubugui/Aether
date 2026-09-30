extends "res://tools/install_cliff_kit.gd"
## Preserve the cottage's old anchor clearance; follow only its changed support.
func build() -> void:
	assert(DisplayServer.get_name()!="headless")
	backup_directory="res://captures/edit_backups/10l-cottage-"+Time.get_datetime_string_from_system().replace(":","-")
	var path:="res://scenes/world/World.tscn";backup_file(path)
	var audit:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://captures/round-10d-readonly-support.json"))
	var record:Dictionary={}
	for sample in audit.affected_samples:
		if sample.object=="Settlements/cottage_57181" and sample.detail=="origin":record=sample;break
	assert(not record.is_empty())
	var world:Node3D=load(path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);world.set_script(null);root.add_child(world)
	await physics_frame;await physics_frame
	var cottage:Node3D=world.get_node("Settlements/cottage_57181")
	var p:Vector3=cottage.global_position
	assert(p.distance_to(Vector3(record.point[0],record.point[1],record.point[2]))<.001,"Cottage was independently moved; preserve that edit")
	var query:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4)
	var hit:=world.get_world_3d().direct_space_state.intersect_ray(query);assert(not hit.is_empty())
	var delta:float=hit.position.y-float(record.baseline.height)
	cottage.global_position.y+=delta
	world.set_script(WorldScript);save_scene(world,path)
	var report:={"node":"Settlements/cottage_57181","old_anchor":p,"new_anchor":cottage.global_position,"support_delta_metres":delta,"backup":backup_directory,"scope":"Preserves the original origin-to-ground offset; does not force all bottom AABB corners above ground."}
	var file:=FileAccess.open("res://captures/round-10l-cottage-seating.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("COTTAGE SUPPORT ADJUSTED ",delta," m; all other native placements retained")
	world.free();await process_frame;quit()

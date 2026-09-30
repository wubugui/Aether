extends "res://tools/install_cliff_kit.gd"
## Explicit level-authoring operation after terrain sculpting. Preserves X/Z,
## rotation, scale, instance boundaries and optional authored ground clearance.
## Saves a backup first; it never runs while playing or reopening the editor.

func ground_below(world:Node3D,point:Vector3) -> float:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(point.x,2200,point.z),Vector3(point.x,-100,point.z),4)
	var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
	return hit.position.y if not hit.is_empty() else NAN

func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	backup_directory="res://captures/edit_backups/ground-landmarks-"+Time.get_datetime_string_from_system().replace(":","-")
	var path:="res://scenes/world/World.tscn";backup_file(path)
	var world:Node3D=load(path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	world.set_script(null);root.add_child(world)
	await physics_frame
	await physics_frame
	var changes:Array=[];var submerged:Array=[]
	for landmark in world.get_node("Settlements").get_children():
		var floor_y:=ground_below(world,landmark.global_position)
		if is_nan(floor_y):continue
		if floor_y<.5:submerged.append(str(landmark.name));continue
		var bottom:=INF
		for part in landmark.get_node("Model").find_children("*","MeshInstance3D",true,false):
			var box:AABB=part.get_aabb()
			for i in range(8):bottom=minf(bottom,(part.global_transform*box.get_endpoint(i)).y)
		if is_inf(bottom):continue
		var offset:float=landmark.get_meta("ground_clearance",0.0)
		var delta:=floor_y+offset-bottom
		if absf(delta)<.02:continue
		landmark.global_position.y+=delta
		changes.append({"node":str(landmark.name),"vertical_change":delta,"ground_y":floor_y})
	for port in world.get_node("Ports").get_children():
		var floor_y:=ground_below(world,port.global_position)
		if not is_nan(floor_y):port.global_position.y=floor_y+port.ground_offset
	world.set_script(WorldScript);save_scene(world,path)
	var report:={"changes":changes,"submerged_landmarks_requiring_relocation":submerged,"backup":backup_directory}
	var file:=FileAccess.open("res://captures/landmark-grounding.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("LANDMARKS GROUNDED ",changes.size()," submerged ",submerged)
	world.free();await process_frame;quit()

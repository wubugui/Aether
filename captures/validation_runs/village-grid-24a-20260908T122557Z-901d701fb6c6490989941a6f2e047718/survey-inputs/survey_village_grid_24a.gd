extends SceneTree
func _initialize()->void:call_deferred("survey")
func survey()->void:
	var source:="";var output:="";var identity:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--source="):source=arg.trim_prefix("--source=")
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
	assert(not source.is_empty() and not output.is_empty() and not FileAccess.file_exists(output))
	var game:Node3D=load("res://scenes/game.tscn").instantiate();game.set_script(null);game.get_node("World").set_script(null)
	game.get_node("Airship").visible=false;game.get_node("Airship").set_physics_process(false);root.add_child(game)
	var document:=GLTFDocument.new();var state:=GLTFState.new();assert(document.append_from_file(source.path_join("mainland_headland.glb"),state)==OK)
	var coast:Node3D=document.generate_scene(state);coast.name="SurveyedHeadland23g";coast.position=Vector3(-2180,0,-1830);game.add_child(coast)
	for mesh in coast.find_children("*","MeshInstance3D",true,false):
		mesh.create_trimesh_collision()
		for body in mesh.find_children("*","StaticBody3D",true,false):body.collision_layer=256
	await physics_frame;await physics_frame;await physics_frame
	var grids:Array=[]
	for bounds in [["foreground",-2280,-2200,-1800,-1710],["bay",-2265,-2190,-1920,-1835]]:
		var samples:Array=[]
		for z in range(bounds[3],bounds[4]+1):
			for x in range(bounds[1],bounds[2]+1):
				var query:=PhysicsRayQueryParameters3D.create(Vector3(x,150,z),Vector3(x,-20,z),256)
				var hit:=game.get_world_3d().direct_space_state.intersect_ray(query)
				samples.append({"position":[x,null if hit.is_empty() else hit.position.y,z],"normal":null if hit.is_empty() else [hit.normal.x,hit.normal.y,hit.normal.z]})
		grids.append({"name":bounds[0],"bounds":[bounds[1],bounds[2],bounds[3],bounds[4]],"spacing_m":1.,"samples":samples})
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify({"run_id":identity,"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"headland_glb_sha256":FileAccess.get_sha256(source.path_join("mainland_headland.glb")),"grids":grids,"scope":"Actual native collision rays on unchanged23g headland with original World present. One-metre candidate design grid, not finished path width or full terrain clearance proof."},"  "));file.close()
	print("VILLAGE GRID READY ",grids.size());quit()

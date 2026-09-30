extends SceneTree
var game:Node3D
func _initialize() -> void:call_deferred("survey")
func survey() -> void:
	var layout_path:="";var reference_path:="";var output:="";var identity:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--layout="):layout_path=arg.trim_prefix("--layout=")
		if arg.begins_with("--reference="):reference_path=arg.trim_prefix("--reference=")
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
	assert(not layout_path.is_empty() and not reference_path.is_empty() and not output.is_empty())
	assert(not FileAccess.file_exists(output))
	var layout:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(layout_path));var reference:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(reference_path))
	assert(reference.world_sha256==FileAccess.get_sha256("res://scenes/world/World.tscn"))
	game=load("res://scenes/game.tscn").instantiate();game.set_script(null);game.get_node("World").set_script(null)
	game.get_node("Airship").visible=false;root.add_child(game);game.get_node("Airship").set_physics_process(false)
	await physics_frame;await physics_frame;await physics_frame
	var samples:Array=[]
	for index in range(layout.vertices.size()):
		var at:Array=layout.vertices[index]
		var query:=PhysicsRayQueryParameters3D.create(Vector3(at[0],300,at[2]),Vector3(at[0],-100,at[2]),4)
		var ground:=game.get_world_3d().direct_space_state.intersect_ray(query);assert(not ground.is_empty())
		var bed:Dictionary=ground
		if str(ground.collider.get_path()).contains("SeaCollision"):
			query.exclude=[ground.rid];bed=game.get_world_3d().direct_space_state.intersect_ray(query)
		samples.append({"index":index,"position":[at[0],ground.position.y,at[2]],"collider":str(ground.collider.get_path()),"bed_y":null if bed.is_empty() else bed.position.y,"bed_collider":null if bed.is_empty() else str(bed.collider.get_path())})
	var file:=FileAccess.open(output,FileAccess.WRITE)
	file.store_string(JSON.stringify({"run_id":identity,"world_sha256":reference.world_sha256,"layout_sha256":FileAccess.get_sha256(layout_path),"samples":samples,"scope":"Original World surface and, where needed, SeaCollision-excluded terrain bed at every Blender layout vertex. No candidate terrain has been loaded or old ground changed."},"  "));file.close()
	print("HEADLAND VERTEX GROUND SURVEY ",samples.size());quit()

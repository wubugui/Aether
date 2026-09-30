extends SceneTree
var output:String
func _initialize()->void:call_deferred("check")
func first_mesh(node:Node)->MeshInstance3D:
	if node is MeshInstance3D:return node
	for child in node.get_children():
		var found:=first_mesh(child)
		if found!=null:return found
	return null
func point(v:Vector3)->Array:return [v.x,v.y,v.z]
func capture(name:String)->void:
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join(name+".png"))==OK)
func check()->void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
	assert(not output.is_empty())
	var packed:PackedScene=load("res://captures/candidate_highcoast36c/World36c.tscn")
	assert(packed!=null)
	var author:Node3D=packed.instantiate()
	assert(author.get_script()==load("res://scripts/open_world.gd"))
	assert(author.get_node("Terrain").get_child_count()==208)
	var original_direct_bodies:int=0
	for node in author.get_children():
		if node is StaticBody3D:original_direct_bodies+=1
	assert(original_direct_bodies==0)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://captures/highcoast_study_36b/model-report.json"))
	var tiles:Array=[]
	for row in plan.native_tiles:
		var node:Node3D=author.get_node("Terrain/"+str(row.name))
		assert(node.get_script()==load("res://scripts/asset_instance.gd"))
		assert(node.has_node("Model") and node.has_node("Collision/Shape"))
		assert(node.get_child_count()==2)
		var mesh:=first_mesh(node.get_node("Model"))
		var shape:ConcavePolygonShape3D=node.get_node("Collision/Shape").shape
		assert(mesh.mesh.get_faces()==shape.get_faces())
		tiles.append({"name":str(node.name),"triangles":shape.get_faces().size()/3,"standard_paths":true})
	var evidence:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://captures/validation_runs/highcoast-36b-20260909T015215Z-0c71bb650bcf43d890987772791f1dff/images/storm-high.png.json"))
	var path_removals:Array=evidence.harbor_study.stone_paths.vegetation_adjustments
	var removed_count:int=0
	for row in path_removals:removed_count+=row.removed_from_temporary_copy.size()
	var expected_count:int=54800-removed_count
	var total:int=0;var pine_count:int=0;var selected_name:String=""
	for grove in author.get_node("Vegetation").get_children():
		assert(grove.owner==author)
		assert(grove.get_script()==load("res://scripts/scatter_group.gd"))
		assert(grove.model_scene!=null)
		total+=grove.multimesh.instance_count
		if str(grove.name).ends_with("_CoastalPines36b"):
			pine_count+=1;selected_name=str(grove.name)
			assert(grove.get_meta("asset_kind")=="pine")
	assert(total==expected_count and pine_count>0)
	author.free()
	# Fresh actual Game initialization exercises the existing physical flight
	# controller. No --game-test flag or unrelated full test suite is invoked.
	var game:Node3D=load("res://captures/candidate_highcoast36c/Game36c.tscn").instantiate()
	root.add_child(game)
	game.test_frozen=true;game.sound_enabled=false
	var world:Node3D=game.get_node("World")
	assert(world.is_processing())
	assert(world.chunks.size()>=208 and world.layout.props.size()==expected_count)
	world.set_process(false)
	for i in range(40):await process_frame
	var grove:MultiMeshInstance3D=world.get_node("Vegetation/"+selected_name)
	grove.selected_instance=0;grove.read_selected()
	assert(grove.selected_transform==grove.multimesh.get_instance_transform(0))
	var source:MultiMesh=grove.multimesh
	grove.apply_selected()
	assert(grove.multimesh!=source and grove.multimesh.get_instance_transform(0)==source.get_instance_transform(0))
	# Applying an unchanged transform is enough for this bounded helper check;
	# extraction modifies authoring membership and needs its own editor review.
	await capture("candidate-start")
	game.testing=true;game.test_override_input=true;game.test_input=Vector3(-.18,.12,1.)
	game.photo_mode=false;game.test_frozen=false;game.anchored=false;game.throttle=.55
	var start:Vector3=game.airship.position
	var samples:Array=[]
	for i in range(240):
		await physics_frame
		if i%30==0:samples.append({"frame":i,"position":point(game.airship.position),"velocity":point(game.airship.velocity),"clearance":game.clearance})
	game.test_frozen=true
	var finish:Vector3=game.airship.position
	assert(start.distance_to(finish)>10.)
	await capture("candidate-flight")
	var result:Dictionary={"native_world":"res://captures/candidate_highcoast36c/World36c.tscn","native_game":"res://captures/candidate_highcoast36c/Game36c.tscn","tile_checks":tiles,"scatter_total":total,"expected_scatter_total":expected_count,"retained_harbor_path_removals":path_removals,"new_pine_groups":pine_count,"persistent_root_scatter_bodies":original_direct_bodies,"world_ready":true,"world_processing_before_test_freeze":true,"scatter_read_apply_no_change_checked":selected_name,"flight_start":point(start),"flight_end":point(finish),"flight_distance_m":start.distance_to(finish),"flight_samples":samples,"passed":true,"scope":"Fresh native World/Game reload, 14 tile mesh/shape equality, authored scatter helpers and 240 physics frames through existing test input. Not complete route, reference visual or whole-world acceptance."}
	var file:=FileAccess.open(output.path_join("candidate-reopen.json"),FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "));file.close()
	print("36g CANDIDATE REOPEN READY ",start.distance_to(finish))
	game.queue_free();await process_frame;await process_frame
	quit()

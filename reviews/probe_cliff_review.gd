extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var world:Node3D=load("res://scenes/world/World.tscn").instantiate()
	root.add_child(world)
	await physics_frame
	await physics_frame
	await process_frame
	world.set_process(false)
	var point:=Vector3(139.4779017603547,39.511622788330016,-26.333991483658366)
	var samples:Array=[]
	for segment in [[point+Vector3.UP*.05,Vector3(point.x,-99,point.z),"down_from_free_space"],[Vector3(point.x,2200,point.z),Vector3(point.x,-99,point.z),"down_from_sky"],[point,point+Vector3.UP*150,"up_from_free_space"]]:
		var query:=PhysicsRayQueryParameters3D.create(segment[0],segment[1],4)
		query.hit_back_faces=true
		var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
		var sample:Dictionary={"kind":segment[2],"hit":not hit.is_empty()}
		if not hit.is_empty():
			sample.position=[hit.position.x,hit.position.y,hit.position.z]
			sample.collider_path=str(hit.collider.get_path())
			sample.normal=[hit.normal.x,hit.normal.y,hit.normal.z]
		samples.append(sample)
	var sphere:=SphereShape3D.new();sphere.radius=4.0
	var overlap:=PhysicsShapeQueryParameters3D.new();overlap.shape=sphere;overlap.transform=Transform3D(Basis.IDENTITY,point);overlap.collision_mask=5
	var obstructions:=world.get_world_3d().direct_space_state.intersect_shape(overlap)
	var report:Dictionary={"world_hash":FileAccess.get_sha256("res://scenes/world/World.tscn"),"ground_script_hash":FileAccess.get_sha256("res://scripts/open_world.gd"),"probe_point":[point.x,point.y,point.z],"ground_height_result":world.ground_height(point),"radius4_obstructions":obstructions.size(),"rays":samples,"read_only":true}
	var out:=FileAccess.open("res://reviews/cliff-runtime-probe.json",FileAccess.WRITE);out.store_string(JSON.stringify(report,"\t"));out.close()
	print("CLIFF RUNTIME READ-ONLY PROBE ",JSON.stringify(report))
	world.queue_free();await process_frame
	quit()

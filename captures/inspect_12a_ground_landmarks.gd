extends SceneTree
func _initialize() -> void:call_deferred("inspect")
func inspect() -> void:
	var world:Node3D=load("res://scenes/world/World.tscn").instantiate();world.set_script(null);root.add_child(world)
	var camera:=Camera3D.new();root.add_child(camera);camera.position=Vector3(0,145,250);camera.rotation.x=atan2(-4.,64.9);camera.fov=50.;camera.current=true
	root.size=Vector2i(1672,941)
	await physics_frame
	await physics_frame
	var rows:Array=[]
	for uv in [Vector2(345,565),Vector2(735,685),Vector2(900,696),Vector2(675,769),Vector2(420,487),Vector2(495,760),Vector2(870,680),Vector2(940,710),Vector2(580,700)]:
		var origin:=camera.project_ray_origin(uv);var q:=PhysicsRayQueryParameters3D.create(origin,origin+camera.project_ray_normal(uv)*6000,4)
		var hit:=world.get_world_3d().direct_space_state.intersect_ray(q)
		var row:Dictionary={"pixel":[uv.x,uv.y]}
		if not hit.is_empty():row.merge({"position":[hit.position.x,hit.position.y,hit.position.z],"normal":[hit.normal.x,hit.normal.y,hit.normal.z],"collider":str(hit.collider.get_path())})
		rows.append(row);print(row)
	var output:=FileAccess.open("res://captures/round-12a-ground-landmarks.json",FileAccess.WRITE);output.store_string(JSON.stringify(rows,"\t"));output.close()
	world.free();camera.free();quit()

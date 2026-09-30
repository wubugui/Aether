extends "res://tools/install_cliff_kit.gd"
## Explicit level-design pass. Curve3D routes remain natively editable in Godot.
func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	backup_directory="res://captures/edit_backups/road-routes-"+Time.get_datetime_string_from_system().replace(":","-")
	var path:="res://scenes/world/World.tscn";backup_file(path)
	var world:Node3D=load(path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);world.set_script(null);root.add_child(world)
	root.size=Vector2i(1672,941)
	var camera:=Camera3D.new();root.add_child(camera);camera.position=Vector3(0,145,250);camera.rotation_degrees.x=-3.5;camera.fov=50;camera.current=true
	await physics_frame;await physics_frame
	var route_group:Node3D=world.get_node_or_null("Routes")
	if not route_group:route_group=category(world,"Routes")
	var pixels:=[Vector2(794,966),Vector2(798,916),Vector2(816,871),Vector2(833,826),Vector2(867,786),Vector2(895,751),Vector2(911,706),Vector2(932,678),Vector2(917,654),Vector2(903,642)]
	var main:Array[Vector3]=[Vector3(120,0,480),Vector3(45,0,290),Vector3(-28,0,260),Vector3(-36,0,210),Vector3(-7,0,160)]
	for pixel in pixels:
		var query:=PhysicsRayQueryParameters3D.create(camera.position,camera.position+camera.project_ray_normal(pixel)*6000,4)
		var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
		assert(not hit.is_empty(),"Road control misses actual ground")
		main.append(hit.position)
	var definitions:Array=[
		{"name":"Trail_Crownreach","points":main,"width":2.4},
		{"name":"Trail_Amberfield","points":[Vector3(120,0,480),Vector3(400,0,470),Vector3(560,0,380),Vector3(790,0,450),Vector3(1050,0,650),Vector3(1320,0,880)],"width":2.0},
		{"name":"Trail_HillHamlet","points":[main[-6],Vector3(2,0,-176),Vector3(-4,0,-221)],"width":1.35}]
	for definition in definitions:
		var route:Path3D=route_group.get_node_or_null(NodePath(definition.name))
		if not route:route=Path3D.new();route.name=definition.name;route_group.add_child(route)
		var curve:=Curve3D.new();curve.bake_interval=2
		var points:Array=definition.points
		for i in range(points.size()):
			var p:Vector3=points[i]
			var query:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4)
			var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
			assert(not hit.is_empty());p.y=hit.position.y
			var tangent:Vector3=(points[mini(i+1,points.size()-1)]-points[maxi(i-1,0)])*.14;tangent.y=0
			curve.add_point(p,-tangent,tangent)
		route.curve=curve;route.set_meta("width_metres",definition.width)
	world.set_script(WorldScript);save_scene(world,path)
	world.free();camera.free();print("AUTHORED THREE NATIVE GODOT ROAD CURVES");await process_frame;quit()

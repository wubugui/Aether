extends SceneTree
var output: String
func _initialize()->void: call_deferred("run")
func xyz(v:Vector3)->Array:return [v.x,v.y,v.z]
func run()->void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--output-dir="):output=a.trim_prefix("--output-dir=")
	var game:Node3D=load("res://captures/candidate_highcoast36c/Game36c.tscn").instantiate()
	game.set_script(load("res://scripts/game.gd"))
	game.save_path="user://crownreach37_inspection_unused.json"
	var daylight:Node3D=load("res://scenes/game.tscn").instantiate()
	game.get_node("Environment").environment=daylight.get_node("Environment").environment.duplicate(true)
	var sun:DirectionalLight3D=game.get_node("Sun")
	var day_sun:DirectionalLight3D=daylight.get_node("Sun")
	sun.transform=day_sun.transform;sun.light_color=day_sun.light_color;sun.light_energy=day_sun.light_energy
	daylight.free()
	root.add_child(game)
	game.set_process(false);game.set_physics_process(false);game.sound_enabled=false
	game.airship.hide();game.hud.hide()
	var world:Node3D=game.get_node("World")
	world.set_process(false)
	var castle:Node3D=world.get_node("Settlements/castle_57174")
	var views:Array=[
		["opening",Vector3(0,145,250),Vector3(0,83.837,-750),50.0],
		["castle-front",Vector3(109,62,-197),Vector3(43.288,30,-282.521),55.0],
		["castle-back",Vector3(-36,66,-365),Vector3(43.288,30,-282.521),55.0],
		["castle-river",Vector3(40,198,-155),Vector3(40,15,-360),65.0]]
	var rows:Array=[]
	for view in views:
		game.camera.position=view[1];game.camera.look_at(view[2]);game.camera.fov=view[3]
		world.update_focus(view[1],true)
		for i in range(16):await process_frame
		await RenderingServer.frame_post_draw
		var path:String=output.path_join(view[0]+".png")
		assert(root.get_texture().get_image().save_png(path)==OK)
		rows.append({"image":path,"position":xyz(view[1]),"target":xyz(view[2]),"fov":view[3]})
	var probes:Array=[]
	for x in [-27.0,0.0,27.0]:
		for z in [-21.0,0.0,19.0]:
			var p:Vector3=castle.to_global(Vector3(x,0,z))
			probes.append({"point":xyz(p),"ground":world.ground_height(p)})
	var report:Dictionary={"source_game":"res://captures/candidate_highcoast36c/Game36c.tscn","daylight_source":"res://scenes/game.tscn","castle_transform":str(castle.transform),"views":rows,"ground_probes":probes,"scope":"Same candidate world, daytime inspection only; no geometry changed. Camera snapshots, not physical flight."}
	var f:=FileAccess.open(output.path_join("intake.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));f.close()
	game.queue_free();await process_frame;await process_frame;quit()

extends RefCounted
var checks: Array = []
var game: Node3D
func check(ok:bool,label:String,details:Variant=null) -> void:
	checks.append({"passed":ok,"name":label,"details":details})
	print("PASS " if ok else "FAIL ",label," ",details if details!=null else "")

func key(code:Key,pressed:bool) -> void:
	var event:=InputEventKey.new()
	event.physical_keycode=code
	event.keycode=code
	event.pressed=pressed
	Input.parse_input_event(event)

func frames(count:int) -> void:
	for i in range(count):await game.get_tree().physics_frame

func run(g:Node3D) -> void:
	game=g
	game.test_frozen=true
	await frames(4)
	check(is_instance_valid(game.hud) and game.hud.is_inside_tree() and is_instance_valid(game.hud.ui_font),"flight HUD initializes with live instruments and navigation font")
	check(game.world.core.size()==208,"208 complete world-space Blender terrain chunks")
	check(game.world.model_meshes.size()==39,"39 independent native environment prefabs, including the western mesa")
	if OS.has_feature("template"):
		check(not ResourceLoader.exists("res://assets/open_world.glb") and not FileAccess.file_exists("res://assets/reference.jpg"),"Windows package excludes historical whole-world models and reference image")
	check(game.world.terrain_bodies.size()>=9,"terrain has active physics colliders",game.world.terrain_bodies.size())
	check(game.get_node("Airship/EnvelopeCollision").shape is ConvexPolygonShape3D,"airship collider generated from actual balloon geometry")
	var points:=[Vector2(240,-96),Vector2(1060,-2940),Vector2(1450,-3270),Vector2(2670,1200),Vector2(-1650,2870),Vector2(768.1,-900),Vector2(767.9,-900),Vector2(5375.9,1650),Vector2(5376.1,1650)]
	for point in points:
		# Query from clear air above both terrain and independent massif meshes.
		var pos:=Vector3(point.x,1500,point.y)
		game.world.update_focus(pos,true)
		await frames(3)
		var query:=PhysicsRayQueryParameters3D.create(Vector3(point.x,2200,point.y),Vector3(point.x,-100,point.y),1)
		var hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(query)
		var expected:float=game.world.ground_height(pos)
		check(not hit.is_empty() and absf(hit.get("position",Vector3.ZERO).y-expected)<.25,"actual mesh / collision / height agreement at "+str(point),{"expected":expected,"actual":hit.get("position",Vector3.ZERO).y})
	game.reset_flight()
	# Deliberately put the old camera behind the assembled cliffs. The actual
	# smoothed camera must stay visible from the player, even while orbiting.
	game.airship.position=Vector3(150,50,50)
	game.world.update_focus(game.airship.position,true)
	await frames(3)
	for angle in [PI,PI*.65,PI*1.35]:
		game.camera.position=Vector3(150,55,-110)
		game.orbit=Vector2(angle,0)
		var target:Vector3=game.airship.position+Vector3(4.15,4.2,1.1)
		var before_ray:=PhysicsRayQueryParameters3D.create(target,game.camera.position,1,[game.airship.get_rid()])
		var before_hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(before_ray)
		game.update_camera(1.0/60)
		var after_ray:=PhysicsRayQueryParameters3D.create(target,game.camera.position,1,[game.airship.get_rid()])
		var after_hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(after_ray)
		check(not before_hit.is_empty() and after_hit.is_empty(),"smoothed camera corrects actual assembled cliff obstruction at orbit "+str(angle))
	game.reset_flight()
	game.test_frozen=false
	key(KEY_W,true);key(KEY_E,true);key(KEY_D,true)
	await frames(70)
	key(KEY_W,false);key(KEY_E,false);key(KEY_D,false)
	check(game.speed>5 and game.throttle>.2,"physical W throttle input accelerates the body",game.speed)
	check(game.altitude>140 and game.heading<-.2,"E ascent and D steering work",[game.altitude,game.heading])
	check(game.airship.position.distance_to(game.HOME_SHIP)>10,"actual world-space flight displacement",game.airship.position.distance_to(game.HOME_SHIP))
	await frames(80)
	check(game.airship.velocity.normalized().dot(-game.airship.global_basis.x)>.95,"forward velocity follows the modeled ship nose")
	key(KEY_SPACE,true);key(KEY_SPACE,false)
	await frames(100)
	check(game.speed<.5 and game.anchored,"Space brakes to a stable hover",game.speed)
	# Ground collision must stop a real descent, without a position clamp.
	game.test_frozen=true
	game.airship.position=Vector3(-520,32,60)
	game.airship.velocity=Vector3.ZERO
	game.vertical_speed=0
	game.throttle=0
	game.world.update_focus(game.airship.position,true)
	await frames(4)
	game.test_frozen=false
	key(KEY_Q,true)
	await frames(140)
	key(KEY_Q,false)
	check(game.airship.position.y>3.0,"sea collision prevents descending through the world",game.airship.position.y)
	check(game.shield<1,"impact produces damage feedback",game.shield)
	game.test_frozen=true
	# Port interaction must enforce approach conditions and alter game state.
	game.airship.position=game.HOME_SHIP
	check(not game.try_dock(),"cannot refill fuel away from a dock")
	var port:Dictionary=game.world.ports[0]
	game.airship.position=Vector3(port.x,port.pad_y+6,port.z)
	game.world.update_focus(game.airship.position,true)
	await frames(3)
	game.speed=25
	check(not game.try_dock(),"dock rejects an unsafe approach speed")
	game.speed=0
	game.fuel=.05;game.health=.3;game.shield=.2
	check(game.try_dock(),"low-speed docking succeeds")
	check(game.fuel==1 and game.health==1 and game.shield==1 and game.completed.has(port.id),"dock repairs, refuels and records exploration progress")
	var dock_ray:=PhysicsRayQueryParameters3D.create(Vector3(port.x,port.pad_y+30,port.z),Vector3(port.x,port.pad_y-5,port.z),1)
	var dock_hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(dock_ray)
	check(not dock_hit.is_empty() and absf(dock_hit.position.y-port.pad_y)<1,"dock platform is a physical modeled surface")
	var ring:Node3D=game.world.rings[0]
	game.airship.global_position=ring.global_position-Vector3.UP*3
	game.check_rings()
	check(game.collected_rings.has("0") and not ring.visible,"3D flight ring grants progress and disappears")
	# A far location outside the Blender-authored square is physically generated.
	var remote:=Vector3(8250,700,1770)
	game.airship.position=remote
	game.world.update_focus(remote,true)
	await frames(4)
	check(game.world.chunks.has(game.world.cell_at(remote)) and game.world.generated_chunks>0,"terrain continues outside the initial region",game.world.generated_chunks)
	var remote_ray:=PhysicsRayQueryParameters3D.create(Vector3(remote.x,2200,remote.z),Vector3(remote.x,-100,remote.z),1)
	var remote_hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(remote_ray)
	check(not remote_hit.is_empty() and absf(remote_hit.position.y-game.world.ground_height(remote))<.25,"streamed terrain has matching collision")
	var streamed:MeshInstance3D=game.world.chunks[game.world.cell_at(remote)]
	var stream_arrays:Array=streamed.mesh.surface_get_arrays(0)
	var stream_vertices:PackedVector3Array=stream_arrays[Mesh.ARRAY_VERTEX]
	var stream_normals:PackedVector3Array=stream_arrays[Mesh.ARRAY_NORMAL]
	check((stream_vertices[1]-stream_vertices[0]).cross(stream_vertices[2]-stream_vertices[0]).normalized().dot(stream_normals[0])<-.99,"streamed terrain uses the same outward normals and front-face winding as imported Blender terrain")
	# Whole-turn camera movement, not a fixed screenshot camera.
	game.orbit=Vector2(PI,.2)
	var old_camera:Vector3=game.camera.position
	game.update_camera(1)
	check(game.camera.position.distance_to(old_camera)>30,"camera can orbit to the opposite side of the ship")
	game.reset_flight()
	check(game.airship.position==game.HOME_SHIP and game.throttle==0,"rescue resets position and motion")
	game.save_path="user://skyfarer_automated_test.json"
	game.testing=false
	game.fuel=.43
	game.save_progress()
	game.fuel=.1
	game.airship.position+=Vector3(90,50,90)
	game.load_progress(true)
	game.testing=true
	check(absf(game.fuel-.43)<.001 and game.airship.position.distance_to(game.HOME_SHIP)<.01,"save and restore persist flight state using an isolated test file")
	var failures:=checks.filter(func(c):return not c.passed)
	var report:={"passed":failures.is_empty(),"checks":checks,"core_chunks":game.world.core.size(),"model_placements":game.world.layout.props.size()}
	report["provenance"]=preload("res://scripts/validation_context.gd").snapshot()
	var output:="res://captures/game-validation.json"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--validation-output="):output=arg.trim_prefix("--validation-output=")
	var file:=FileAccess.open(output,FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	print("GAME VALIDATION: ",checks.size()-failures.size(),"/",checks.size()," passed")
	game.get_tree().quit(0 if failures.is_empty() else 1)

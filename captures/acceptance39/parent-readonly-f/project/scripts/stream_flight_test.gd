extends RefCounted
## Four independent continuous flights across each authored world boundary.
func run(game:Node3D) -> void:
	var routes:=[{"name":"east","start":Vector3(4700,1050,1700),"direction":Vector3.RIGHT},{"name":"west","start":Vector3(-4000,1050,1700),"direction":Vector3.LEFT},{"name":"north","start":Vector3(1800,1050,-6900),"direction":Vector3.FORWARD},{"name":"south","start":Vector3(1800,1050,3900),"direction":Vector3.BACK}]
	var legs:Array=[]
	var passed:=true
	var total_missing:=0
	for route in routes:
		game.test_frozen=true
		game.airship.position=route.start
		game.airship.velocity=Vector3.ZERO
		game.vertical_speed=0
		game.heading=atan2(route.direction.z,-route.direction.x)-deg_to_rad(13)
		game.throttle=1
		game.anchored=false
		game.world.update_focus(game.airship.position,true)
		for i in range(4):await game.get_tree().physics_frame
		game.test_override_input=true
		game.test_input=Vector3(0,0,1)
		game.test_frozen=false
		var records:Array=[]
		var missing:=0
		var began:float=game.elapsed
		while game.airship.position.distance_to(route.start)<4000 and game.elapsed-began<80:
			await game.get_tree().create_timer(.75).timeout
			var p:Vector3=game.airship.position
			var cell:Vector2i=game.world.cell_at(p)
			var ready:bool=game.world.chunks.has(cell) and game.world.terrain_bodies.has(cell)
			if not ready:missing+=1
			records.append({"position":[p.x,p.y,p.z],"speed":game.speed,"terrain_and_collision_loaded":ready})
		var leg_passed:bool=game.airship.position.distance_to(route.start)>=4000 and missing==0 and game.health==1 and game.shield==1
		passed=passed and leg_passed
		total_missing+=missing
		legs.append({"direction":route.name,"passed":leg_passed,"distance_metres":game.airship.position.distance_to(route.start),"missing_terrain_or_collision_samples":missing,"samples":records})
		print("STREAM LEG ",route.name," ","PASS" if leg_passed else "FAIL"," missing=",missing)
	var report:={"passed":passed,"method":"Four independent continuous physical flights, each 4 km, east / west / north / south across the authored world boundary. Set starting position once per leg; no repositioning during flight.","distance_metres":game.travelled,"missing_terrain_or_collision_samples":total_missing,"generated_chunks":game.world.generated_chunks,"legs":legs}
	var file:=FileAccess.open("res://captures/stream-flight-validation.json",FileAccess.WRITE)
	report["provenance"]=preload("res://scripts/validation_context.gd").snapshot()
	file.store_string(JSON.stringify(report,"  "))
	print("STREAM FLIGHT ","PASS" if passed else "FAIL"," distance=",game.travelled," missing=",total_missing," generated=",game.world.generated_chunks)
	game.get_tree().quit(0 if passed else 1)

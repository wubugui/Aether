extends RefCounted
## Sustained physical flight: no teleportation between the seven waypoints.
func run(game:Node3D) -> void:
	var records:Array=[]
	var start:float=game.elapsed
	var minimum_clearance:=INF
	while game.tour_visited<7 and game.elapsed-start<240:
		await game.get_tree().create_timer(1.0).timeout
		var p:Vector3=game.airship.position
		minimum_clearance=minf(minimum_clearance,game.clearance)
		records.append({"time":game.elapsed-start,"position":[p.x,p.y,p.z],"speed":game.speed,"clearance":game.clearance,"waypoint":game.tour_waypoint})
	var passed:bool=game.tour_visited>=7 and game.travelled>9000 and minimum_clearance>15 and game.health==1 and game.shield==1
	var report:Dictionary={"passed":passed,"method":"Same physical flight controller as manual play, seven 3D waypoints, no teleportation; test clock accelerated 8x","waypoints_reached":game.tour_visited,"distance_metres":game.travelled,"duration_game_seconds":game.elapsed-start,"minimum_clearance_metres":minimum_clearance,"health":game.health,"shield":game.shield,"samples":records}
	var file:=FileAccess.open("res://captures/flight-tour-validation.json",FileAccess.WRITE)
	report["provenance"]=preload("res://scripts/validation_context.gd").snapshot()
	file.store_string(JSON.stringify(report,"  "))
	print("FLIGHT TOUR ","PASS" if passed else "FAIL"," distance=",game.travelled," reached=",game.tour_visited," clearance=",minimum_clearance)
	game.get_tree().quit(0 if passed else 1)

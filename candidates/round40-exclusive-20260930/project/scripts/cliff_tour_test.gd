extends RefCounted
## Continuous flight around the assembled cliff group using the same inputs,
## physical controller, collisions and camera as normal play.
func run(game:Node3D) -> void:
	Engine.time_scale=4
	game.test_override_input=true
	var route:=[Vector3(50,105,110),Vector3(15,105,-90),Vector3(170,120,-165),Vector3(285,120,-50),Vector3(250,100,145),Vector3(60,110,160)]
	var index:=0;var start:float=game.elapsed;var distance_start:float=game.travelled
	var samples:Array=[];var minimum:=INF;var camera_blocked:=0
	while index<route.size() and game.elapsed-start<180:
		var delta:Vector3=route[index]-game.airship.position
		var heading:=atan2(delta.z,-delta.x)-deg_to_rad(13)
		game.test_input=Vector3(clampf(wrapf(heading-game.heading,-PI,PI)*2,-1,1),clampf(delta.y*.045,-1,1),clampf((.32-game.throttle)*5,-1,1))
		game.orbit=Vector2(sin((game.elapsed-start)*.12)*PI,.15)
		await game.get_tree().create_timer(.2).timeout
		await RenderingServer.frame_post_draw
		var p:Vector3=game.airship.position;minimum=minf(minimum,game.clearance)
		var target:Vector3=p+Vector3(4.15,4.2,1.1).rotated(Vector3.UP,game.heading)
		var ray:=PhysicsRayQueryParameters3D.create(target,game.camera.position,1,[game.airship.get_rid()])
		var hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(ray)
		if not hit.is_empty():camera_blocked+=1
		samples.append({"time":game.elapsed-start,"position":[p.x,p.y,p.z],"clearance":game.clearance,"speed":game.speed,"waypoint":index,"camera_clear":hit.is_empty()})
		if p.distance_to(route[index])<36:index+=1
	var distance:float=game.travelled-distance_start
	var passed:bool=index==route.size() and distance>650 and minimum>10 and game.health==1 and game.shield==1 and camera_blocked==0
	var result:={"passed":passed,"method":"Continuous physical flight from normal spawn around all sides of the assembled cliff group. No waypoint teleportation. Same input/controller/camera as manual play, clock 4x.","waypoints_reached":index,"distance_metres":distance,"minimum_clearance_metres":minimum,"camera_obstruction_samples":camera_blocked,"health":game.health,"shield":game.shield,"samples":samples,"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn")}
	result["provenance"]=preload("res://scripts/validation_context.gd").snapshot()
	var file:=FileAccess.open("res://captures/cliff-tour-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close()
	print("ASSEMBLED CLIFF TOUR ","PASS" if passed else "FAIL"," waypoints=",index," distance=",distance," minimum_clearance=",minimum," blocked_camera_samples=",camera_blocked)
	game.get_tree().quit(0 if passed else 1)

extends SceneTree
var game:Node3D
func _initialize() -> void:call_deferred("survey")
func probe(at:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(at.x,300,at.z),Vector3(at.x,-30,at.z),4)
	return game.get_world_3d().direct_space_state.intersect_ray(query)
func sample(at:Vector3) -> Dictionary:
	var hit:=probe(at)
	assert(not hit.is_empty())
	return {"position":[hit.position.x,hit.position.y,hit.position.z],"collider":str(hit.collider.get_path()),"normal":[hit.normal.x,hit.normal.y,hit.normal.z]}
func survey() -> void:
	var output:="";var identity:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
	assert(not output.is_empty() and not identity.is_empty() and not FileAccess.file_exists(output.path_join("survey.json")))
	game=load("res://scenes/game.tscn").instantiate();game.set_script(null);game.get_node("World").set_script(null)
	game.get_node("Airship").visible=false;root.add_child(game);game.get_node("Airship").set_physics_process(false)
	await physics_frame;await physics_frame;await physics_frame
	var shore:Array=[];var houses:Array=[];var house_trials:Array=[];var piers:Array=[]
	var yaw:float=-.98;var basis:=Basis(Vector3.UP,yaw)
	for z in [-2080.,-2110.,-2140.,-2195.,-2230.,-2265.,-2300.,-2335.,-2440.,-2470.,-2500.,-2530.,-2590.,-2630.,-2670.,-2710.]:
		var last_sea:Dictionary={};var first_land:Dictionary={}
		for x in range(-2850,-2069,5):
			var value:=sample(Vector3(x,0,z))
			if str(value.collider).contains("SeaCollision"):last_sea=value
			elif not last_sea.is_empty():first_land=value;break
		assert(not last_sea.is_empty() and not first_land.is_empty())
		var left:float=last_sea.position[0];var right:float=first_land.position[0]
		for i in range(10):
			var at:=(left+right)*.5;var value:=sample(Vector3(at,0,z))
			if str(value.collider).contains("SeaCollision"):left=at
			else:right=at
		var shoreline_x:=(left+right)*.5
		shore.append({"z":z,"sea_bracket":last_sea,"land_bracket":first_land,"refined_boundary_x":shoreline_x,"boundary_bracket_m":right-left})
		var accepted:int=0
		for inland in [16.,28.,42.,58.,76.,96.]:
			var at:=Vector3(shoreline_x+inland,0,z);var points:Array=[];var minimum:=10000.;var maximum:=-10000.;var on_land:=true
			for x in [-3.9,0.,3.9]:
				for zz in [-5.4,0.,5.4]:
					var value:=sample(at+basis*Vector3(x,0,zz));points.append(value)
					if str(value.collider).contains("SeaCollision"):on_land=false
					minimum=minf(minimum,value.position[1]);maximum=maxf(maximum,value.position[1])
			var okay:bool=on_land and maximum-minimum<.46
			var trial:={"x":at.x,"z":at.z,"inland_m":inland,"sample_relief_m":maximum-minimum,"candidate_accepted":okay,"ground_samples":points}
			house_trials.append(trial)
			if okay and accepted<2:
				at.y=maximum+.02
				houses.append({"position":[at.x,at.y,at.z],"yaw":yaw,"ground_samples":points,"scope":"Nine original-ground points under the unscaled keeper foundation bound; not full footprint, entrance or walking proof."})
				accepted+=1
		# Select a pier back-edge where the actual shore reaches deck minus0.2m.
		if z in [-2110.,-2265.,-2500.,-2670.]:
			left=shoreline_x;right=shoreline_x+24.
			for i in range(14):
				var x:=(left+right)*.5;var value:=sample(Vector3(x,0,z))
				if float(value.position[1])<2.15:left=x
				else:right=x
			var entry:=Vector3((left+right)*.5,0,z)
			var center:Vector3=entry+basis*Vector3(0,0,8.)
			var landing:Vector3=center+basis*Vector3(0,0,11.)
			var checks:Array=[]
			for x in [-2.2,0.,2.2]:checks.append(sample(entry+basis*Vector3(x,0,0)))
			piers.append({"entry":[entry.x,0,entry.z],"pier_center":[center.x,0,center.z],"landing_center":[landing.x,0,landing.z],"yaw":yaw,"deck_y":2.35,"entry_ground_samples":checks,"tip_original_ground":sample(landing),"scope":"Piles extend below sea surface; seabed anchoring not established."})
	var camera:Camera3D=game.get_node("Camera");camera.position=Vector3(-2620,150,-2090);camera.look_at(Vector3(-2390,8,-2265));camera.fov=60
	for i in range(25):await process_frame
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("harbor-before.png"))==OK)
	var report:={"run_id":identity,"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"scope":"Read-only actual scene physics survey at16 coast transects, proposed house 3x3 foundations and four pier entrances. Candidate placement evidence only; no geometry modification or visual acceptance.","shore_transects":shore,"house_trials":house_trials,"houses":houses,"piers":piers}
	var file:=FileAccess.open(output.path_join("survey.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	print("HARBOR SITE SURVEY ",shore.size()," transects ",houses.size()," selected houses ",piers.size()," piers")
	quit()

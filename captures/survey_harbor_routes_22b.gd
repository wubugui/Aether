extends SceneTree
var game:Node3D
func _initialize() -> void:call_deferred("survey")
func point(values:Array) -> Vector3:return Vector3(values[0],values[1],values[2])
func hit(at:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(at.x,300,at.z),Vector3(at.x,-30,at.z),4)
	var result:=game.get_world_3d().direct_space_state.intersect_ray(query);assert(not result.is_empty())
	return {"position":[result.position.x,result.position.y,result.position.z],"collider":str(result.collider.get_path())}
func survey() -> void:
	var source:="";var output:="";var identity:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--survey="):source=arg.trim_prefix("--survey=")
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
	assert(not source.is_empty() and not output.is_empty() and not identity.is_empty())
	assert(not FileAccess.file_exists(output.path_join("routes.json")))
	var prior:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(source))
	assert(prior.world_sha256==FileAccess.get_sha256("res://scenes/world/World.tscn"))
	game=load("res://scenes/game.tscn").instantiate();game.set_script(null);game.get_node("World").set_script(null)
	game.get_node("Airship").visible=false;root.add_child(game);game.get_node("Airship").set_physics_process(false)
	await physics_frame;await physics_frame;await physics_frame
	var ramps:Array=[];var routes:Array=[]
	for index in range(prior.piers.size()):
		var pier:Dictionary=prior.piers[index];var entry:=point(pier.entry);var basis:=Basis(Vector3.UP,float(pier.yaw));var ramp_rows:Array=[]
		for j in range(13):
			var row:Array=[];var distance:float=j*.20
			for x in [-2.2,-1.1,0.,1.1,2.2]:row.append(hit(entry+basis*Vector3(x,0,-distance)))
			ramp_rows.append({"inland_distance":distance,"samples":row})
		ramps.append({"pier_index":index,"entry":pier.entry,"yaw":pier.yaw,"deck_y":2.35,"rows":ramp_rows})
		var nearest:Dictionary={};var best:=100000.
		for house in prior.houses:
			var porch:=point(house.position)+Basis(Vector3.UP,float(house.yaw))*Vector3(0,0,6.30)
			var d:=Vector2(porch.x-entry.x,porch.z-entry.z).length()
			if d<best:best=d;nearest=house
		var endpoint:=point(nearest.position)+Basis(Vector3.UP,float(nearest.yaw))*Vector3(0,0,6.30)
		var start:=entry-basis*Vector3(0,0,2.4)
		var delta:Vector3=endpoint-start;delta.y=0
		var cross:=Vector3(-delta.z,0,delta.x).normalized();var count:int=ceili(delta.length()/.40);var rows:Array=[]
		for j in range(count+1):
			var at:Vector3=start+delta*float(j)/float(count);var samples:Array=[]
			for offset in [-1.5,0.,1.5]:samples.append(hit(at+cross*offset))
			rows.append({"distance_m":delta.length()*float(j)/float(count),"samples":samples})
		routes.append({"pier_index":index,"house_position":nearest.position,"house_yaw":nearest.yaw,"house_low_step_top_y":float(nearest.position[1])+.18,"start":[start.x,0,start.z],"end":[endpoint.x,0,endpoint.z],"width_m":3.,"length_m":delta.length(),"rows":rows,"scope":"Direct route corridor before stair/path design; sample coordinates are authored-world measurements, route topology is a design proposal."})
	var camera:Camera3D=game.get_node("Camera");camera.position=Vector3(-2500,72,-2190);camera.look_at(Vector3(-2350,12,-2265));camera.fov=55
	for i in range(20):await process_frame
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("routes-before.png"))==OK)
	var file:=FileAccess.open(output.path_join("routes.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"run_id":identity,"world_sha256":prior.world_sha256,"source_survey_run":prior.run_id,"ramps":ramps,"routes":routes,"scope":"Actual terrain transects for new native Blender apron and path/stair geometry; no existing terrain or scene modified."},"  "));file.close()
	print("HARBOR ROUTE SURVEY ",ramps.size()," aprons ",routes.size()," corridors");quit()

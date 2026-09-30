extends SceneTree
## Proposed continuous approach paths, measured on unchanged original terrain.
var game:Node3D
func _initialize() -> void:call_deferred("survey")
func point(a:Array) -> Vector3:return Vector3(a[0],a[1],a[2])
func hit(at:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(at.x,300,at.z),Vector3(at.x,-30,at.z),4)
	var result:=game.get_world_3d().direct_space_state.intersect_ray(query);assert(not result.is_empty())
	assert(not str(result.collider.get_path()).contains("SeaCollision"))
	return {"position":[result.position.x,result.position.y,result.position.z],"collider":str(result.collider.get_path())}
func survey() -> void:
	var source:="";var output:="";var identity:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--survey="):source=arg.trim_prefix("--survey=")
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
	assert(not source.is_empty() and not output.is_empty() and not identity.is_empty())
	assert(not FileAccess.file_exists(output.path_join("paths.json")))
	var prior:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(source))
	assert(prior.world_sha256==FileAccess.get_sha256("res://scenes/world/World.tscn"))
	game=load("res://scenes/game.tscn").instantiate();game.set_script(null);game.get_node("World").set_script(null)
	game.get_node("Airship").visible=false;root.add_child(game);game.get_node("Airship").set_physics_process(false)
	await physics_frame;await physics_frame;await physics_frame
	var paths:Array=[]
	for index in range(prior.piers.size()):
		var pier:Dictionary=prior.piers[index];var entry:=point(pier.entry);var basis:=Basis(Vector3.UP,float(pier.yaw))
		var nearest:Dictionary={};var best:=100000.
		for house in prior.houses:
			var porch:=point(house.position)+Basis(Vector3.UP,float(house.yaw))*Vector3(0,0,6.40)
			var d:=Vector2(porch.x-entry.x,porch.z-entry.z).length()
			if d<best:best=d;nearest=house
		var endpoint:=point(nearest.position)+Basis(Vector3.UP,float(nearest.yaw))*Vector3(0,0,6.40);endpoint.y=0.
		var handle:float=20. if best>70. else minf(12.,best*.20)
		var p1:Vector3=entry-basis*Vector3(0,0,handle)
		var p2:Vector3=endpoint+Basis(Vector3.UP,float(nearest.yaw))*Vector3(0,0,handle)
		var dense:Array[Vector3]=[];var distances:Array[float]=[0.];var total:=0.
		for j in range(2001):
			var t:float=float(j)/2000.;var at:Vector3=entry.bezier_interpolate(p1,p2,endpoint,t);dense.append(at)
			if j>0:total+=at.distance_to(dense[j-1]);distances.append(total)
		var rows:Array=[];var count:int=ceili(total/.40);var cursor:=1
		for j in range(count+1):
			var d:float=total*float(j)/float(count)
			while cursor<2000 and distances[cursor]<d:cursor+=1
			var fraction:float=(d-distances[cursor-1])/(distances[cursor]-distances[cursor-1]);var t:float=(float(cursor-1)+fraction)/2000.
			var at:Vector3=entry.bezier_interpolate(p1,p2,endpoint,t)
			var tangent:Vector3=entry.bezier_derivative(p1,p2,endpoint,t).normalized();var transverse:=Vector3(-tangent.z,0,tangent.x)
			var width:float=lerpf(4.4,3.,smoothstep(0.,5.,d))
			width=lerpf(width,2.,smoothstep(total-5.,total,d))
			var samples:Array=[]
			for ratio in [-.5,-.25,0.,.25,.5]:samples.append(hit(at+transverse*width*float(ratio)))
			rows.append({"distance_m":d,"center":[at.x,0,at.z],"tangent":[tangent.x,0,tangent.z],"width_m":width,"samples":samples})
		paths.append({"pier_index":index,"entry":pier.entry,"end":[endpoint.x,0,endpoint.z],"house_position":nearest.position,"house_yaw":nearest.yaw,"deck_y":2.35,"house_low_step_top_y":float(nearest.position[1])+.18,"length_m":total,"rows":rows,"controls":[pier.entry,[p1.x,0,p1.z],[p2.x,0,p2.z],[endpoint.x,0,endpoint.z]],"scope":"Cubic centerline is a proposed authored village approach. Five real original-ground samples per section; start tangent aligns with pier, end tangent and2m width align with existing lowest door step."})
	var camera:Camera3D=game.get_node("Camera");camera.position=Vector3(-2435,48,-2245);camera.look_at(Vector3(-2365,10,-2285));camera.fov=58
	for i in range(20):await process_frame
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("paths-before.png"))==OK)
	var file:=FileAccess.open(output.path_join("paths.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"run_id":identity,"world_sha256":prior.world_sha256,"source_survey_run":prior.run_id,"paths":paths,"scope":"Original ground measurements for four connected approach designs. No stair, path or terrain was modified."},"  "));file.close()
	print("HARBOR PATH SURVEY ",paths.size());quit()

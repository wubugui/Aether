extends SceneTree
## Runtime-only assembly of local Blender assets in the existing northwest sea.
var game:Node3D
var region:Node3D
var directory:=""
var placements:Array=[]
var islands:Dictionary={}
var site_checks:Array=[]
func _initialize() -> void:call_deferred("preview")
func model(name:String,position:Vector3,yaw:float=0.,scale_value:float=1.) -> Node3D:
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	assert(document.append_from_file(directory.path_join(name+".glb"),state)==OK)
	var node:Node3D=document.generate_scene(state)
	node.name=name+"_"+str(region.get_child_count());node.position=position
	node.rotation.y=yaw;node.scale=Vector3.ONE*scale_value
	region.add_child(node)
	for part in node.find_children("*","MeshInstance3D",true,false):
		part.create_trimesh_collision()
		for body in part.find_children("*","StaticBody3D",true,false):body.collision_layer=1 if name=="keeper_house" else 5
	return node
func ground(point:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(point.x,200,point.z),Vector3(point.x,-20,point.z),4)
	return game.get_world_3d().direct_space_state.intersect_ray(query)
func attach_building(kind:String,island_name:String,offset:Vector3,yaw:float=0.,scale_value:float=1.) -> Node3D:
	if island_name in ["island_c","island_d"]:
		offset=Vector3(1.5,0,.8) if kind=="lighthouse" else offset*.72
	var at:Vector3=islands[island_name].to_global(offset)
	yaw+=islands[island_name].rotation.y
	var hit:=ground(at);assert(not hit.is_empty())
	assert(str(hit.collider.get_path()).contains(str(islands[island_name].name)))
	at.y=hit.position.y
	var node:Node3D
	if kind=="lighthouse":
		node=load("res://scenes/prefabs/lighthouse.tscn").instantiate()
		node.name="Lighthouse_"+island_name;node.position=at;node.rotation.y=yaw;region.add_child(node)
	else:node=model(kind,at,yaw,scale_value)
	placements.append({"kind":kind,"island":island_name,"position":[at.x,at.y,at.z],"yaw":yaw,"scale":scale_value,"support":str(hit.collider.get_path())})
	return node
func preview() -> void:
	var output:="";var view:="archipelago";var identity:="";var label:="20c"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--study-dir="):directory=arg.trim_prefix("--study-dir=")
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
		if arg.begins_with("--view="):view=arg.trim_prefix("--view=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
		if arg.begins_with("--label="):label=arg.trim_prefix("--label=")
	assert(not directory.is_empty() and not output.is_empty() and not identity.is_empty())
	assert(not FileAccess.file_exists(output))
	game=load("res://scenes/game.tscn").instantiate();game.set_script(null)
	game.get_node("Airship").visible=false;root.add_child(game)
	game.get_node("Airship").set_physics_process(false)
	region=Node3D.new();region.name="LanternCoastStudy";game.add_child(region)
	if label in ["20k","20l"]:
		await physics_frame;await physics_frame;await physics_frame
		var proposed:=Vector3(-2372,0,-1812)
		var existing:=ground(proposed)
		assert(not existing.is_empty() and str(existing.collider.get_path()).contains("SeaCollision"))
		site_checks.append({"site":"island_d","position":[proposed.x,existing.position.y,proposed.z],"original_collider":str(existing.collider.get_path()),"scope":"Original center sea surface before candidate assembly; proposed geography, not original-map reconstruction proof."})
		islands["island_d"]=model("island_c",proposed,2.0)
		islands.island_d.name="IslandD_CVariant"
		placements.append({"kind":"island_c","instance":"island_d","position":[proposed.x,0,proposed.z],"yaw":2.0})
	for item in [["island_a",Vector3(-2350,0,-1650)],["island_b",Vector3(-2700,0,-2200)],["island_c",Vector3(-3050,0,-2650)]]:
		islands[item[0]]=model(item[0],item[1])
		placements.append({"kind":item[0],"position":[item[1].x,0,item[1].z]})
	var reef_locations:Array=[
		["reef_ridge",-2470,-1560,.3,1.0],["reef_low",-2380,-1490,.8,.8],
		["reef_spire",-2230,-1730,-.3,.8],["reef_ridge",-2500,-1740,-.5,1.1],
		["reef_low",-2510,-1870,.5,.65],["reef_spire",-2530,-1970,.2,1.0],
		["reef_ridge",-2740,-1940,-.8,1.0],["reef_low",-2470,-2080,.4,1.3],
		["reef_ridge",-2780,-2390,.2,.7],["reef_low",-2870,-2410,.7,1.1],
		["reef_spire",-3010,-2400,-.2,1.0],["reef_low",-2930,-2590,.8,.8],
		["reef_ridge",-3180,-2740,-.3,1.3]]
	for item in reef_locations:
		model(item[0],Vector3(item[1],0,item[2]),item[3],item[4])
		placements.append({"kind":item[0],"position":[item[1],0,item[2]],"yaw":item[3],"scale":item[4]})
	await physics_frame;await physics_frame;await physics_frame
	attach_building("lighthouse","island_a",Vector3(-3,0,-6),.25)
	attach_building("lighthouse","island_b",Vector3(0,0,-2),-.12)
	attach_building("lighthouse","island_c",Vector3(1,0,-1),.1)
	if label in ["20k","20l"]:
		attach_building("lighthouse","island_d",Vector3(1,0,-1),.1)
		attach_building("keeper_house","island_d",Vector3(-12,0,14),-.15,.7)
	var house:Node3D=attach_building("keeper_house","island_a",Vector3(-22,0,2))
	attach_building("keeper_house","island_a",Vector3(19,0,6),-.15,.85)
	attach_building("keeper_house","island_b",Vector3(-15,0,3),.08,.8)
	var c_house:=Vector3(15,0,15) if label=="20e" else (Vector3(9,0,4) if label=="20d" else Vector3(12,0,2))
	if label in ["20f","20g","20h","20i","20j","20k","20l"]:c_house=Vector3(-12,0,14)
	var c_house_node:Node3D=attach_building("keeper_house","island_c",c_house,-.15,.7)
	var tree_locations:Array=[[-33,-18,.85],[-42,-5,.72],[-28,30,.8],[18,-20,1.0],[32,12,.78],[45,-8,.7],[4,28,.84]]
	if label in ["20d","20e","20f","20g","20h","20i","20j","20k","20l"]:tree_locations=[[-35,-9,.72],[-40,-4,.9],[-34,2,.55],[-31,14,.8],[-26,20,.65],[16,-21,.95],[23,-18,.70],[30,-14,.6],[39,5,.8],[42,11,.55],[18,22,.7]]
	for island_name in islands:
		var factor:float=1.0 if island_name=="island_a" else (.7 if island_name=="island_b" else .36)
		for item in tree_locations:
			var at:Vector3=islands[island_name].to_global(Vector3(item[0]*factor,0,item[1]*factor))
			var hit:=ground(at)
			if hit.is_empty() or hit.normal.y<.65:continue
			if not str(hit.collider.get_path()).contains(str(islands[island_name].name)):continue
			if label in ["20i","20j","20k","20l"] and str(hit.collider.get_path()).contains("footpath"):continue
			var near_building:=false
			if label in ["20g","20h","20i","20j","20k","20l"]:
				for building in region.get_children():
					var is_house:bool=str(building.name).begins_with("keeper_house_")
					if not is_house and not str(building.name).begins_with("Lighthouse_"):continue
					var local_point:Vector3=building.to_local(at)
					if absf(local_point.x)<(5.2 if is_house else 6.) and absf(local_point.z)<(7.6 if is_house else 6.):near_building=true
			if near_building:continue
			var tree:Node3D=load("res://scenes/prefabs/pine.tscn").instantiate()
			tree.name="IslandPine_"+str(region.get_child_count());at.y=hit.position.y
			tree.position=at;tree.scale=Vector3.ONE*float(item[2]);region.add_child(tree)
			placements.append({"kind":"existing_native_pine","island":island_name,"position":[at.x,at.y,at.z],"scale":item[2]})
	await physics_frame;await physics_frame
	var footing:Array=[]
	for node in region.get_children():
		var building:bool=str(node.name).begins_with("Lighthouse_") or str(node.name).begins_with("keeper_house_")
		if not building:continue
		var points:Array=[]
		var wide:float=3.9 if str(node.name).begins_with("keeper") else 4.015
		var depth:float=5.4 if str(node.name).begins_with("keeper") else 4.015
		var bottom:float=-.65 if str(node.name).begins_with("keeper") else -.5
		for x in [-wide,0.,wide]:
			for z in [-depth,0.,depth]:
				var at:Vector3=node.to_global(Vector3(x,bottom,z))
				var hit:=ground(at)
				points.append({"position":[at.x,at.y,at.z],"gap_m":null if hit.is_empty() else at.y-hit.position.y,"collider":null if hit.is_empty() else str(hit.collider.get_path())})
		footing.append({"building":str(node.name),"scope":"Bounding footprint 3x3 samples, not an all-surface contact proof.","samples":points})
	var camera:Camera3D=game.get_node("Camera")
	var origin:Vector3=islands.island_a.position
	match view:
		"archipelago":
			camera.position=origin+(Vector3(135,88,150) if label in ["20d","20e","20f","20g","20h","20i","20j","20k","20l"] else Vector3(-82,88,160))
			camera.look_at(origin+(Vector3(-300,18,-475) if label in ["20d","20e","20f","20g","20h","20i","20j","20k","20l"] else Vector3(-125,18,-180)));camera.fov=65
		"island-front":camera.position=origin+Vector3(140,85,155);camera.look_at(origin+Vector3(0,15,0));camera.fov=60
		"island-back":camera.position=origin+Vector3(-135,80,-160);camera.look_at(origin+Vector3(0,14,0));camera.fov=60
		"shoreline":camera.position=origin+Vector3(108,21,92);camera.look_at(origin+Vector3(35,8,15));camera.fov=55
		"house-front":camera.position=house.global_position+Vector3(12,7,16);camera.look_at(house.global_position+Vector3(0,3,0));camera.fov=55
		"house-back":camera.position=house.global_position+Vector3(-13,9,-17);camera.look_at(house.global_position+Vector3(0,3,0));camera.fov=55
		"c-site":camera.position=c_house_node.global_position+Vector3(-20,14,25);camera.look_at(c_house_node.global_position+Vector3(5,3,-5));camera.fov=58
		"b-site":camera.position=islands.island_b.position+Vector3(65,48,68);camera.look_at(islands.island_b.position+Vector3(0,12,0));camera.fov=60
		"paths":camera.position=origin+Vector3(50,48,45);camera.look_at(origin+Vector3(-6,25,2));camera.fov=65
		"reference-coast":camera.position=origin+Vector3(58,56,42);camera.look_at(origin+Vector3(-600,50,-950));camera.fov=70
		"reference-coast-near":camera.position=origin+Vector3(72,60,18);camera.look_at(origin+Vector3(-600,54,-950));camera.fov=70
		"d-site":camera.position=islands.island_d.position+Vector3(60,43,64);camera.look_at(islands.island_d.position+Vector3(0,12,0));camera.fov=60
		"dock-front","dock-back","boat-close","path-approach","paths-overview","path-door","path0-curve":pass
		"headland-front","headland-back","headland-bay","headland-seam":pass
		"village-foreground","village-bay","village-door","village-upper":pass
		"cloud-back":camera.position=Vector3(-4354.38293,650.,-4383.21798);camera.look_at(Vector3(-3754.38293,810.,-3533.21798));camera.fov=65
		"lamp-close":camera.position=region.get_node("Lighthouse_island_a").global_position+Vector3(9,23,13);camera.look_at(region.get_node("Lighthouse_island_a").global_position+Vector3(0,19.60,0));camera.fov=45
		"beam-side":camera.position=region.get_node("Lighthouse_island_a").global_position+Vector3(460,144.6,-170);camera.look_at(region.get_node("Lighthouse_island_a").global_position+Vector3(120,19.6,-220));camera.fov=70
		_:assert(false)
	var environment_mode:="day"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--environment="):environment_mode=arg.trim_prefix("--environment=")
	var harbor_adapter=load(directory.path_join("harbor_assembly_22g.gd")).new()
	var harbor_report:Dictionary=harbor_adapter.configure(game,directory,environment_mode=="night",camera,view)
	var headland_adapter=load(directory.path_join("headland_runtime_23g.gd")).new()
	headland_adapter.configure(game,directory,environment_mode=="night",camera,view)
	await physics_frame;await physics_frame;await physics_frame
	var headland_report:Dictionary=headland_adapter.finish()
	var village_adapter=load(directory.path_join("village_paving_runtime_26b.gd")).new()
	village_adapter.configure(game,directory,camera,view)
	var adapter=load(directory.path_join("coast_environment_27f.gd")).new()
	var environment_report:Dictionary=adapter.configure(game,region,directory.path_join("new-environment27f"),environment_mode=="night")
	await physics_frame;await physics_frame;await physics_frame


	var lantern_adapter=load(directory.path_join("lantern_lighting_28h.gd")).new()
	var lantern_report:Dictionary=lantern_adapter.configure(game,region,directory.path_join("lantern-optics"),environment_mode=="night")
	var village_report:Dictionary={"unchanged_geometry_basis":"26b","evidence":"round-26b-root-evidence.json","scope":"Roads and ground are byte-identical26b assets; already checked collisions are not resampled for this cloud/water-only edit."}
	var sample_time:=0.
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--study-time="):sample_time=float(arg.trim_prefix("--study-time="))
	RenderingServer.global_shader_parameter_set("world_time",sample_time)
	environment_report["sampled_world_time"]=sample_time

	var ref_position:Vector3=camera.position;var ref_rotation:Vector3=camera.rotation;var ref_fov:float=camera.fov
	var views:Array=["night-reference"] if environment_mode=="night" else ["day-reference","day-d-front","day-d-back","day-c-front"]
	for camera_name in views:
		if str(camera_name).ends_with("reference"):
			camera.position=ref_position;camera.rotation=ref_rotation;camera.fov=ref_fov
		elif camera_name=="day-d-front":
			camera.position=islands.island_d.to_global(Vector3(65,40,70));camera.look_at(islands.island_d.to_global(Vector3(0,10,0)));camera.fov=55
		elif camera_name=="day-d-back":
			camera.position=islands.island_d.to_global(Vector3(-70,35,-65));camera.look_at(islands.island_d.to_global(Vector3(0,10,0)));camera.fov=55
		else:
			camera.position=islands.island_c.to_global(Vector3(65,40,70));camera.look_at(islands.island_c.to_global(Vector3(0,10,0)));camera.fov=55
		for i in range(40):await process_frame
		await RenderingServer.frame_post_draw
		var target:String=output.get_base_dir().path_join(camera_name+".png")
		assert(root.get_texture().get_image().save_png(target)==OK)
		var report:={"run_id":identity,"view":view,"production_modified":false,"scope":"Actual temporary 3D geometry in existing world; lighting mode recorded in environment_study, no full reference acceptance.","placements":placements,"footing_samples":footing,"camera":{"position":[camera.position.x,camera.position.y,camera.position.z],"rotation":[camera.rotation.x,camera.rotation.y,camera.rotation.z],"fov":camera.fov},"region_mesh_nodes":region.find_children("*","MeshInstance3D",true,false).size(),"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"lighthouse_sha256":FileAccess.get_sha256("res://assets/models/lighthouse.glb")}
		report["lantern_lighting"]=lantern_report
		report["site_checks"]=site_checks
		report["environment_study"]=environment_report
		report["harbor_study"]=harbor_report
		report["headland_study"]=headland_report
		report["village_paving_study"]=village_report
		report["view"]=camera_name
		report["island_geometry_revision"]="30d"
		report["island_c_glb_sha256"]=FileAccess.get_sha256(directory.path_join("island_c.glb"))
		var file:=FileAccess.open(target+".json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	print("30d ISLAND VIEWS ",views)
	quit()

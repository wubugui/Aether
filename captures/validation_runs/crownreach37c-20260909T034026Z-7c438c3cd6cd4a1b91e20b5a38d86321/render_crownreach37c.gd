extends SceneTree
var output:String
var scatter_changes:Array=[]
var held:Array=[]
func _initialize()->void:call_deferred("run")
func xyz(v:Vector3)->Array:return [v.x,v.y,v.z]
func own(node:Node,scene:Node)->void:
	node.scene_file_path=""
	for c in node.get_children():c.owner=scene;own(c,scene)
func own_boundaries(node:Node,scene:Node)->void:
	for c in node.get_children():
		c.owner=scene
		if c.scene_file_path.is_empty():own_boundaries(c,scene)
func save_scene(node:Node,path:String)->void:
	node.scene_file_path="";own_boundaries(node,node)
	var p:=PackedScene.new();assert(p.pack(node)==OK);assert(ResourceSaver.save(p,path)==OK)
func clear_entry(world:Node3D)->void:
	var corridor:=AABB(Vector3(40.1,18.,-281.),Vector3(6.4,9.0,25.0))
	for grove in world.get_node("Vegetation").get_children():
		var kind:String=grove.get_meta("asset_kind")
		if kind not in ["oak","poplar","pine","bush","rock"]:continue
		var source:MultiMesh=grove.multimesh
		var keep:Array[Transform3D]=[];var removed:Array=[]
		for i in range(source.instance_count):
			var tr:Transform3D=source.get_instance_transform(i)
			var actual:Transform3D=grove.transform*tr
			if absf(actual.origin.x-43.288)>20 or absf(actual.origin.z+269)>30:
				keep.append(tr);continue
			var box:AABB=actual*source.mesh.get_aabb()
			if box.intersects(corridor):
				removed.append({"index":i,"kind":kind,"position":xyz(actual.origin),"bounds":str(box)})
			else:keep.append(tr)
		if not removed.is_empty():
			var copy:MultiMesh=source.duplicate();copy.instance_count=keep.size()
			for i in range(keep.size()):copy.set_instance_transform(i,keep[i])
			grove.multimesh=copy
			scatter_changes.append({"grove":str(grove.name),"before":source.instance_count,"after":copy.instance_count,"removed":removed,"reason":"Actual instance mesh AABB intersects gate approach; retained grove authoring helper."})
func gather(node:Node,parent:Transform3D,faces:PackedVector3Array,rows:Array)->void:
	var t:Transform3D=parent
	if node is Node3D:t=parent*node.transform
	if node is MeshInstance3D:
		node.material_override=load("res://materials/world.tres")
		var local:PackedVector3Array=node.mesh.get_faces()
		for p in local:faces.append(t*p)
		rows.append({"name":str(node.name),"triangles":local.size()/3})
	for c in node.get_children():gather(c,t,faces,rows)
func run()->void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--output-dir="):output=a.trim_prefix("--output-dir=")
	var doc:=GLTFDocument.new();var state:=GLTFState.new()
	assert(doc.append_from_file("res://captures/crownreach_study_37c/castle.glb",state)==OK)
	var model:Node3D=doc.generate_scene(state);model.name="Model"
	var castle:=Node3D.new();castle.name="castle_57174"
	castle.set_script(load("res://scripts/asset_instance.gd"));castle.asset_kind="castle";castle.surface_material=load("res://materials/world.tres")
	castle.add_child(model)
	var faces:=PackedVector3Array();var rows:Array=[];gather(model,Transform3D.IDENTITY,faces,rows)
	var body:=StaticBody3D.new();body.name="Collision";body.collision_layer=1;body.collision_mask=2;castle.add_child(body)
	var shape:=ConcavePolygonShape3D.new();shape.set_faces(faces)
	var collider:=CollisionShape3D.new();collider.name="Shape";collider.shape=shape;body.add_child(collider)
	own(castle,castle)
	var packed:=PackedScene.new();assert(packed.pack(castle)==OK)
	var native:String=output.path_join("castle37c.tscn").replace("\\","/")
	assert(ResourceSaver.save(packed,native)==OK)
	# Use the saved prefab instance in World, keeping its independent
	# scene boundary and editable asset owner instead of embedding a copy.
	castle.free();castle=load(native).instantiate()
	model=castle.get_node("Model")
	var game:Node3D=load("res://captures/candidate_highcoast36c/Game36c.tscn").instantiate()
	# Assemble into a fresh unready World so saved scatter drives its later
	# collision bookkeeping. No transient runtime bodies enter the candidate.
	var world:Node3D=game.get_node("World")
	var old:Node3D=world.get_node("Settlements/castle_57174")
	castle.position=old.position;var parent:Node=old.get_parent()
	var idx:int=old.get_index();parent.remove_child(old);old.free();parent.add_child(castle);parent.move_child(castle,idx)
	clear_entry(world)
	var native_world:String=output.path_join("World37c.tscn").replace("\\","/")
	save_scene(world,native_world)
	game.remove_child(world);world.free()
	world=load(native_world).instantiate();world.name="World";game.add_child(world)
	var native_game:String=output.path_join("Game37c.tscn").replace("\\","/")
	save_scene(game,native_game)
	game.free();game=load(native_game).instantiate()
	root.add_child(game);game.set_process(false);game.set_physics_process(false)
	world=game.get_node("World")
	game.sound_enabled=false;game.airship.hide();game.hud.hide();world.set_process(false)
	castle=world.get_node("Settlements/castle_57174");model=castle.get_node("Model")
	var daylight:Node3D=load("res://scenes/game.tscn").instantiate();held.append(daylight)
	held.append(game.get_node("Environment").environment)
	game.get_node("Environment").environment=daylight.get_node("Environment").environment
	var sun:DirectionalLight3D=game.get_node("Sun");var ds:DirectionalLight3D=daylight.get_node("Sun")
	sun.transform=ds.transform;sun.light_color=ds.light_color;sun.light_energy=ds.light_energy
	for cloud in world.get_node("Clouds").find_children("*","MeshInstance3D",true,false):
		held.append(cloud.material_override);cloud.material_override=load("res://materials/cloud.tres")
	var storm:Node3D=game.get_node_or_null("SpatialStormFront35c")
	if storm:storm.hide()
	var views:Array=[
		["castle-front",Vector3(109,62,-197),Vector3(43.288,30,-282.521),55.0],
		["gate-low",Vector3(43.288,21.6,-261),Vector3(43.288,21.1,-283),65.0]]
	var records:Array=[]
	for view in views:
		game.camera.position=view[1];game.camera.look_at(view[2]);game.camera.fov=view[3]
		world.update_focus(view[1],true)
		for i in range(16):await process_frame
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png(output.path_join(view[0]+".png"))==OK)
		records.append({"image":view[0]+".png","position":xyz(view[1]),"target":xyz(view[2]),"fov":view[3]})
	var route:Array=[]
	game.airship.show();game.hud.show();game.testing=true;game.test_override_input=true
	game.test_input=Vector3(0,0,1);game.test_frozen=false;game.photo_mode=false
	game.airship.position=Vector3(160,80,-280);game.airship.velocity=Vector3.ZERO
	game.heading=-deg_to_rad(13);game.throttle=1.0;game.anchored=false
	game.set_process(true);game.set_physics_process(true)
	var flight_start:Vector3=game.airship.position
	var collision_frames:int=0
	for i in range(300):
		await physics_frame
		if game.airship.get_slide_collision_count()>0:collision_frames+=1
		if i%30==0:route.append({"frame":i,"position":xyz(game.airship.position),"velocity":xyz(game.airship.velocity),"clearance":game.clearance})
	game.test_frozen=true;game.set_process(false);game.set_physics_process(false)
	var flight_end:Vector3=game.airship.position
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("flight-end.png"))==OK)
	var paving:Array=[]
	for node in model.find_children("*","MeshInstance3D",true,false):
		if str(node.name).begins_with("Courtyard paving") or str(node.name).begins_with("Courtyard_paving"):
			var box:AABB=node.mesh.get_aabb()
			var p:Vector3=node.to_global(Vector3(box.position.x+box.size.x*.5,box.position.y,box.position.z+box.size.z*.5))
			var top:Vector3=node.to_global(Vector3(box.position.x+box.size.x*.5,box.end.y,box.position.z+box.size.z*.5))
			paving.append({"name":str(node.name),"bottom_center":xyz(p),"terrain":world.ground_height(p),"gap_m":p.y-world.ground_height(p),"top_above_ground":top.y-world.ground_height(top)})
	var gate:Array=[]
	await physics_frame
	for x in [0.0,2.6,-2.6]:
		var start:Vector3=castle.to_global(Vector3(x,1.7,16));var end:Vector3=castle.to_global(Vector3(x,1.7,6))
		var query:=PhysicsRayQueryParameters3D.create(start,end,1)
		var hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(query)
		gate.append({"x":x,"hit":not hit.is_empty(),"collider":str(hit.collider.get_path()) if not hit.is_empty() else ""})
	var f:=FileAccess.open(output.path_join("castle37c.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"native_scene":native,"mesh_parts":rows,"collision_triangles":faces.size()/3,"views":records,"paving_center_probes":paving,"scatter_changes":scatter_changes,"native_world":native_world,"native_game":native_game,"gate_rays":gate,"physical_flight_samples":route,"flight_start":xyz(flight_start),"flight_end":xyz(flight_end),"flight_displacement_m":flight_start.distance_to(flight_end),"collision_frames":collision_frames,"world_processing_during_flight":world.is_processing(),"scope":"Saved standalone castle prefab, fresh full native Game object reload, two local daylight views and 300 existing-controller physics frames over the central castle. World streaming frozen; not whole-world flight or reference acceptance."},"  "));f.close()
	game.queue_free();await process_frame;await process_frame
	daylight.free();held.clear();await process_frame;await process_frame;quit()

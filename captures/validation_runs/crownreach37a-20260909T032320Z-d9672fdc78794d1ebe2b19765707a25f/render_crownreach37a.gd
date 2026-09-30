extends SceneTree
var output:String
var held:Array=[]
func _initialize()->void:call_deferred("run")
func xyz(v:Vector3)->Array:return [v.x,v.y,v.z]
func own(node:Node,scene:Node)->void:
	node.scene_file_path=""
	for c in node.get_children():c.owner=scene;own(c,scene)
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
	assert(doc.append_from_file("res://captures/crownreach_study_37a/castle.glb",state)==OK)
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
	var native:String=output.path_join("castle37a.tscn").replace("\\","/")
	assert(ResourceSaver.save(packed,native)==OK)
	var game:Node3D=load("res://captures/candidate_highcoast36c/Game36c.tscn").instantiate()
	# Keep the existing candidate driver and weather resource owners alive;
	# freeze its processing only after its normal initialization.
	root.add_child(game);game.set_process(false);game.set_physics_process(false)
	game.sound_enabled=false;game.airship.hide();game.hud.hide()
	var daylight:Node3D=load("res://scenes/game.tscn").instantiate();held.append(daylight)
	held.append(game.get_node("Environment").environment)
	game.get_node("Environment").environment=daylight.get_node("Environment").environment
	var sun:DirectionalLight3D=game.get_node("Sun");var ds:DirectionalLight3D=daylight.get_node("Sun")
	sun.transform=ds.transform;sun.light_color=ds.light_color;sun.light_energy=ds.light_energy
	var world:Node3D=game.get_node("World");world.set_process(false)
	var old:Node3D=world.get_node("Settlements/castle_57174")
	castle.position=old.position;var parent:Node=old.get_parent();parent.remove_child(old);old.free();parent.add_child(castle)
	world.landmarks.erase(old);world.landmarks.append(castle)
	var storm:Node3D=game.get_node_or_null("SpatialStormFront35c")
	if storm:storm.hide()
	var views:Array=[
		["opening",Vector3(0,145,250),Vector3(0,83.837,-750),50.0],
		["castle-front",Vector3(109,62,-197),Vector3(43.288,30,-282.521),55.0],
		["castle-back",Vector3(-36,66,-365),Vector3(43.288,30,-282.521),55.0],
		["castle-river",Vector3(40,198,-155),Vector3(40,15,-360),65.0],
		["gate-low",Vector3(43.288,23,-260),Vector3(43.288,21.1,-283),65.0]]
	var records:Array=[]
	for view in views:
		game.camera.position=view[1];game.camera.look_at(view[2]);game.camera.fov=view[3]
		world.update_focus(view[1],true)
		for i in range(16):await process_frame
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png(output.path_join(view[0]+".png"))==OK)
		records.append({"image":view[0]+".png","position":xyz(view[1]),"target":xyz(view[2]),"fov":view[3]})
	var paving:Array=[]
	for node in model.find_children("*","MeshInstance3D",true,false):
		if str(node.name).begins_with("Courtyard paving") or str(node.name).begins_with("Courtyard_paving"):
			var box:AABB=node.mesh.get_aabb()
			var p:Vector3=node.to_global(Vector3(box.position.x+box.size.x*.5,box.position.y,box.position.z+box.size.z*.5))
			paving.append({"name":str(node.name),"bottom_center":xyz(p),"terrain":world.ground_height(p),"gap_m":p.y-world.ground_height(p)})
	var gate:Array=[]
	await physics_frame
	for x in [0.0,2.6,-2.6]:
		var start:Vector3=castle.to_global(Vector3(x,1.7,16));var end:Vector3=castle.to_global(Vector3(x,1.7,9))
		var query:=PhysicsRayQueryParameters3D.create(start,end,1)
		var hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(query)
		gate.append({"x":x,"hit":not hit.is_empty(),"collider":str(hit.collider.get_path()) if not hit.is_empty() else ""})
	var f:=FileAccess.open(output.path_join("castle37a.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"native_scene":native,"mesh_parts":rows,"collision_triangles":faces.size()/3,"views":records,"paving_center_probes":paving,"gate_rays":gate,"scope":"New castle asset in existing candidate World; daytime camera observations and limited support/portal checks, not flight or reference acceptance."},"  "));f.close()
	game.queue_free();await process_frame;await process_frame
	daylight.free();held.clear();await process_frame;await process_frame;quit()

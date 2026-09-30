extends SceneTree
func _initialize() -> void:call_deferred("run")
func mesh_in(node:Node) -> MeshInstance3D:
	if node is MeshInstance3D:return node
	for child in node.get_children():
		var result:=mesh_in(child)
		if result:return result
	return null
func ray(world:Node3D,a:Vector3,b:Vector3)->Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(a,b,4);query.hit_back_faces=true
	return world.get_world_3d().direct_space_state.intersect_ray(query)
func run() -> void:
	var path:="res://scenes/world/World.tscn";var before_hash:=FileAccess.get_sha256(path)
	var world:Node3D=load(path).instantiate();root.add_child(world)
	await physics_frame;await physics_frame;await process_frame
	world.set_process(false)
	var modules:Array=[]
	for cliff in world.get_node("Cliffs").get_children():
		var model:=mesh_in(cliff.get_node("Model"));var shape:CollisionShape3D=cliff.get_node("Collision/Shape")
		var rendered:=model.mesh.get_faces();var collision:PackedVector3Array=shape.shape.get_faces()
		var max_error:=0.0;var minimum_y:=INF;var maximum_y:=-INF;var center:=Vector3.ZERO
		for p in rendered:
			var v:=model.to_global(p);minimum_y=minf(minimum_y,v.y);maximum_y=maxf(maximum_y,v.y);center+=v
		center/=rendered.size()
		if rendered.size()!=collision.size():max_error=INF
		else:
			for i in range(rendered.size()):max_error=maxf(max_error,model.to_global(rendered[i]).distance_to(shape.to_global(collision[i])))
		var point:=Vector3(center.x,maximum_y+40,center.z);var hit:=ray(world,point,Vector3(point.x,-100,point.z))
		var floor_height:float=world.ground_height(point)
		modules.append({"name":cliff.name,"render_collider_max_error":max_error,"global_bottom_y":minimum_y,"global_top_y":maximum_y,"collision_layer":cliff.get_node("Collision").collision_layer,"ground_height":floor_height,"downward_hit_y":hit.position.y if not hit.is_empty() else -999,"downward_hit_path":str(hit.collider.get_path()) if not hit.is_empty() else ""})
	var old_point:=Vector3(139.477905273438,39.5116233825684,-26.3339920043945)
	var below:=ray(world,Vector3(old_point.x,-50,old_point.z),Vector3(old_point.x,180,old_point.z))
	var above:=ray(world,Vector3(old_point.x,180,old_point.z),Vector3(old_point.x,-50,old_point.z))
	var previous:Node3D=load("res://captures/World-before-cliff-kit.tscn").instantiate()
	var saved_current:Node3D=load(path).instantiate()
	var category_checks:Array=[]
	for group in ["Settlements","Ports","Clouds","FlightRings","LandDetails","Vegetation"]:
		var changed:=0;var missing:=0
		for child in previous.get_node(group).get_children():
			var current:=saved_current.get_node(group).get_node_or_null(NodePath(child.name))
			if not current:missing+=1
			elif child is Node3D and not child.transform.is_equal_approx(current.transform):changed+=1
		category_checks.append({"group":group,"old_count":previous.get_node(group).get_child_count(),"current_count":saved_current.get_node(group).get_child_count(),"moved_node_transforms":changed,"missing_old_nodes":missing})
	previous.free();saved_current.free()
	var report:Dictionary={"world_sha256":before_hash,"script_sha256":FileAccess.get_sha256("res://scripts/open_world.gd"),"module_checks":modules,"old_gap_upward_hit_y":below.position.y if not below.is_empty() else -999,"old_gap_upward_hit_path":str(below.collider.get_path()) if not below.is_empty() else "","old_gap_downward_hit_y":above.position.y if not above.is_empty() else -999,"preserved_node_transforms":category_checks,"world_unchanged_by_review":FileAccess.get_sha256(path)==before_hash,"note":"Headless read-only physics and scene data inspection; no MultiMesh save or authoring mutation."}
	var out:=FileAccess.open("res://reviews/cliff-runtime-review-v2.json",FileAccess.WRITE);out.store_string(JSON.stringify(report,"\t"));out.close()
	print("CLIFF RUNTIME V2 ",JSON.stringify(report));world.queue_free();await process_frame;quit()

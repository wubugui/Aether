extends SceneTree
## Read native terrain contacts below the candidate's actual base vertices.
func _initialize() -> void:call_deferred("probe")
func relative_transform(node:Node3D,ancestor:Node3D) -> Transform3D:
	var result:=node.transform
	var parent:=node.get_parent()
	while parent!=ancestor:
		assert(parent is Node3D)
		result=parent.transform*result;parent=parent.get_parent()
	return result
func probe() -> void:
	var label:="19f"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--label="):label=arg.trim_prefix("--label=")
	assert(label in ["19f","19g","19h"])
	var source:="res://captures/lighthouse_study_"+label+"/lighthouse.glb"
	var bottom:float=-.5 if label in ["19g","19h"] else 0.
	var output:="res://reviews/round-"+label+"-footing-probe.json"
	assert(not FileAccess.file_exists(output))
	var document:=GLTFDocument.new()
	var state:=GLTFState.new()
	assert(document.append_from_file(source,state)==OK)
	var model:Node3D=document.generate_scene(state)
	var points:Dictionary={}
	var treads:Dictionary={}
	for node in model.find_children("*","MeshInstance3D",true,false):
		var transform:=relative_transform(node,model)
		for surface in range(node.mesh.get_surface_count()):
			var arrays:Array=node.mesh.surface_get_arrays(surface)
			for vertex in arrays[Mesh.ARRAY_VERTEX]:
				var p:Vector3=transform*vertex
				if absf(p.y-bottom)<.001:points[p.snapped(Vector3.ONE*.0001)]=true
				if label=="19h":
					for height in [.44,.58,.7164]:
						if absf(p.y-height)<.001:treads[p.snapped(Vector3.ONE*.0001)]=true
	model.free()
	assert(points.size()>8)
	if label=="19h":
		assert(treads.size()==12)
		for height in [.44,.58,.7164]:
			var center:=Vector3.ZERO
			var count:=0
			for p in treads:
				if absf(p.y-height)<.001:center+=p;count+=1
			assert(count==4);treads[center/4.]=true
	var world:Node3D=load("res://scenes/world/World.tscn").instantiate()
	world.set_script(null);root.add_child(world)
	await physics_frame;await physics_frame;await physics_frame
	var records:Array=[]
	for instance in world.get_node("Settlements").get_children():
		if instance.get("asset_kind")!="lighthouse":continue
		var samples:Array=[]
		for p in points:
			var wp:Vector3=instance.global_transform*p
			var query:=PhysicsRayQueryParameters3D.create(wp+Vector3.UP*500,wp-Vector3.UP*100,4)
			var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
			assert(not hit.is_empty())
			samples.append({"local":[p.x,p.y,p.z],"terrain_y":hit.position.y,"gap_m":wp.y-hit.position.y})
		var tread_samples:Array=[]
		for p in treads:
			var wp:Vector3=instance.global_transform*p
			var query:=PhysicsRayQueryParameters3D.create(wp+Vector3.UP*500,wp-Vector3.UP*100,4)
			var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
			assert(not hit.is_empty())
			tread_samples.append({"local":[p.x,p.y,p.z],"terrain_y":hit.position.y,"gap_m":wp.y-hit.position.y})
		records.append({"instance":str(instance.name),"origin":[instance.position.x,instance.position.y,instance.position.z],"samples":samples,"tread_samples":tread_samples})
	assert(records.size()==2)
	var file:=FileAccess.open(output,FileAccess.WRITE)
	file.store_string(JSON.stringify({"scope":"GPU physics terrain-mask-4 rays below actual candidate foundation/step base vertices at both existing native placements; no resource writes. Does not assert that every step top is above the sloping terrain.","label":label,"footing_bottom_m":bottom,"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"candidate_sha256":FileAccess.get_sha256(source),"instances":records},"  "));file.close()
	print("FOOTING SAMPLED ",records.size()," instances x ",points.size()," actual base vertices")
	quit()

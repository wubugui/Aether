extends SceneTree
func _initialize() -> void:call_deferred("verify")
func xyz(v:Vector3) -> Array:return [v.x,v.y,v.z]
func verify() -> void:
	assert(DisplayServer.get_name()!="headless")
	var old_path:="res://captures/edit_backups/2026-09-08T14-03-19-2182/assets/scatter/Grounded_rock_0_-1.res"
	var path:="res://assets/scatter/Grounded_rock_0_-1.res"
	var old:MultiMesh=ResourceLoader.load(old_path,"MultiMesh",ResourceLoader.CACHE_MODE_IGNORE_DEEP)
	var current:MultiMesh=ResourceLoader.load(path,"MultiMesh",ResourceLoader.CACHE_MODE_IGNORE_DEEP)
	assert(old.instance_count==current.instance_count)
	var world:Node3D=load("res://scenes/world/World.tscn").instantiate()
	world.set_script(null);root.add_child(world)
	var group:MultiMeshInstance3D
	for node in world.get_node("Vegetation").get_children():
		if node.multimesh.resource_path==path:group=node;break
	assert(group!=null)
	await physics_frame
	await physics_frame
	var changes:Array=[]
	for i in range(current.instance_count):
		var a:Transform3D=old.get_instance_transform(i)
		var b:Transform3D=current.get_instance_transform(i)
		if a.is_equal_approx(b):continue
		assert(a.basis.is_equal_approx(b.basis))
		assert(absf(a.origin.x-b.origin.x)<.0001 and absf(a.origin.z-b.origin.z)<.0001)
		var p:Vector3=group.global_transform*b.origin
		var ray:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4)
		var hit:Dictionary=world.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty() and absf(hit.position.y-p.y)<.01)
		changes.append({"index":i,"before_local_xyz":xyz(a.origin),"after_local_xyz":xyz(b.origin),
			"after_world_xyz":xyz(p),"unchanged_basis_xz":true,"surface_error_m":absf(hit.position.y-p.y)})
	assert(changes.size()==1)
	var report:={"passed":true,"scope":"GPU read-only MultiMesh comparison and actual native collision surface ray. No scene/resources saved.",
		"source_sha256":FileAccess.get_sha256(old_path),"current_sha256":FileAccess.get_sha256(path),
		"group":str(group.name),"asset_kind":str(group.get_meta("asset_kind","")),"instance_count":current.instance_count,"changes":changes}
	var output:="res://reviews/round-17e-rock-refresh-verification.json"
	assert(not FileAccess.file_exists(output))
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("ROCK REFRESH VERIFICATION PASS ",JSON.stringify(report))
	world.queue_free();old=null;current=null;group=null
	await process_frame
	await process_frame
	quit(0)

extends SceneTree
func _initialize() -> void:
	call_deferred("inspect")
func bounds(n: Node3D) -> AABB:
	var box := AABB()
	var first := true
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var t := Transform3D.IDENTITY
		var p: Node = m
		while p != n:
			t = p.transform * t
			p = p.get_parent()
		var b: AABB = t * m.mesh.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box
func inspect() -> void:
	var data := {"assets":[], "old_upper":[], "world_clouds":[]}
	for i in range(3):
		var doc := GLTFDocument.new()
		var state := GLTFState.new()
		assert(doc.append_from_file("res://assets/upper43/upper_cloud43_%d.glb" % i,state)==OK)
		var asset := doc.generate_scene(state)
		data.assets.append({"variant":i,"parts":asset.find_children("*","MeshInstance3D",true,false).size(),"bounds":str(bounds(asset))})
		asset.free()
	var game: Node3D = load("res://scenes/candidate42c/Game42c.tscn").instantiate()
	for n in game.get_node("SkyRegion39").get_children():
		if str(n.name).begins_with("UpperCloudBank41_"):
			data.old_upper.append({"name":str(n.name),"transform":str(n.transform),"local_bounds":str(bounds(n)),"world_bounds":str(n.transform*bounds(n))})
	for n in game.get_node("World/Clouds").get_children():
		data.world_clouds.append({"name":str(n.name),"transform":str(n.transform),"local_bounds":str(bounds(n)),"world_bounds":str(n.transform*bounds(n))})
	var f := FileAccess.open("res://../evidence/upper43-bounds-audit.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(data,"  "))
	game.free()
	quit()

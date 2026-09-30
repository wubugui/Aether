extends RefCounted

func own_boundaries(node:Node,scene:Node)->void:
	for child in node.get_children():
		child.owner=scene
		if child.scene_file_path.is_empty():own_boundaries(child,scene)

func flatten_local(node:Node,scene:Node)->void:
	node.scene_file_path=""
	for child in node.get_children():
		child.owner=scene
		flatten_local(child,scene)

func first_mesh(node:Node)->MeshInstance3D:
	if node is MeshInstance3D:return node
	for child in node.get_children():
		var found:=first_mesh(child)
		if found!=null:return found
	return null

func pack(node:Node,path:String)->void:
	var packed:=PackedScene.new()
	assert(packed.pack(node)==OK)
	assert(ResourceSaver.save(packed,path)==OK)

func save_candidate(game:Node3D,folder:String,output:String)->Dictionary:
	# A fresh, unready World has no runtime-generated scatter collision bodies.
	var clean:Node3D=load("res://scenes/world/World.tscn").instantiate()
	clean.scene_file_path=""
	var live:Node3D=game.get_node("World")
	var native:String=output.path_join("native-scenes")
	var report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(output.path_join("highcoast-runtime.json")))
	for row in report.tiles:
		var old:Node3D=clean.get_node("Terrain/"+str(row.name))
		var replacement:Node3D=load(str(row.native_scene)).instantiate()
		replacement.name=old.name;replacement.transform=old.transform
		for key in old.get_meta_list():replacement.set_meta(key,old.get_meta(key))
		var index:int=old.get_index();var parent:Node=old.get_parent()
		parent.remove_child(old);old.free();parent.add_child(replacement);parent.move_child(replacement,index)
	# Preserve actual live scatter resources/visibility, including preceding
	# harbor edits, but copy no transient collision caches or temporary bodies.
	for actual in live.get_node("Vegetation").get_children():
		var target:MultiMeshInstance3D=clean.get_node_or_null("Vegetation/"+str(actual.name))
		if target==null:
			target=MultiMeshInstance3D.new();target.name=actual.name
			clean.get_node("Vegetation").add_child(target)
		var kind:String=str(actual.get_meta("asset_kind"))
		target.set_script(load("res://scripts/scatter_group.gd"))
		target.model_scene=load("res://scenes/prefabs/"+kind+".tscn")
		target.set_meta("asset_kind",kind)
		target.transform=actual.transform;target.multimesh=actual.multimesh
		target.material_override=actual.material_override;target.visible=actual.visible
		target.visibility_range_end=actual.visibility_range_end
	# Keep actual surface overrides as authoring fields so AssetInstance._ready
	# does not silently restore the production material on candidate reload.
	for section in ["Terrain","Settlements","Cliffs","Mountains","LandDetails"]:
		var parent:Node=clean.get_node_or_null(section)
		if parent==null:continue
		for target in parent.get_children():
			var actual:Node=live.get_node_or_null(section+"/"+str(target.name))
			if actual==null:continue
			var mesh:=first_mesh(actual)
			if mesh!=null and target.get_script()==load("res://scripts/asset_instance.gd"):
				target.surface_material=mesh.material_override
	for target in clean.find_children("*","GeometryInstance3D",true,false):
		var actual:Node=live.get_node_or_null(clean.get_path_to(target))
		if actual is GeometryInstance3D:target.material_override=actual.material_override
	own_boundaries(clean,clean)
	var world_path:String=native.path_join("World36b.tscn")
	pack(clean,world_path);clean.free()
	# Start from the existing native Game so the flight controls remain intact.
	var candidate:Node3D=load("res://scenes/game.tscn").instantiate()
	candidate.scene_file_path=""
	var original:Node=candidate.get_node("World");candidate.remove_child(original);original.free()
	var saved_world:Node=load(world_path).instantiate();saved_world.name="World";candidate.add_child(saved_world)
	candidate.set_script(load(folder.path_join("candidate_game_36b.gd")))
	candidate.candidate_weather_folder=folder.get_base_dir().path_join("storm35c")
	for name in ["Sun","Environment"]:
		var old:Node=candidate.get_node(name);candidate.remove_child(old);old.free()
		var copy:Node=game.get_node(name).duplicate();copy.name=name;candidate.add_child(copy)
		flatten_local(copy,candidate)
	var copied:Array=[]
	for actual in game.get_children():
		if str(actual.name) in ["World","Airship","Camera","Sun","Environment","SpatialStormFront35c"]:continue
		if not actual is Node3D:continue
		var copy:Node3D=actual.duplicate();copy.name=actual.name;candidate.add_child(copy)
		flatten_local(copy,candidate);copied.append(str(copy.name))
		for asset in copy.find_children("*","Node3D",true,false):
			if asset.get_script()==load("res://scripts/asset_instance.gd"):
				var mesh:=first_mesh(asset)
				if mesh!=null:asset.surface_material=mesh.material_override
	own_boundaries(candidate,candidate)
	var game_path:String=native.path_join("Game36b.tscn")
	pack(candidate,game_path);candidate.free()
	var result:Dictionary={"world_path":world_path,"game_path":game_path,"world_sha256":FileAccess.get_sha256(world_path),"game_sha256":FileAccess.get_sha256(game_path),"retained_external_regions":copied,"scope":"Fresh native World, authored scatter helpers and existing flight Game; runtime weather controller recreated at launch. Requires fresh-process reopen check."}
	var handle:=FileAccess.open(output.path_join("candidate-scenes.json"),FileAccess.WRITE);handle.store_string(JSON.stringify(result,"  "));handle.close()
	return result

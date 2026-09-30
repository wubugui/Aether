extends "res://tools/install_cliff_kit.gd"
## Assemble separately modeled trails; keep the Curve3D authoring routes.
func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	backup_directory="res://captures/edit_backups/road-kit-"+Time.get_datetime_string_from_system().replace(":","-")
	var path:="res://scenes/world/World.tscn";backup_file(path)
	var world:Node3D=load(path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);world.set_script(null)
	var details:Node3D=world.get_node("LandDetails")
	var legacy:Node=details.get_node_or_null("Roads")
	if legacy:legacy.free()
	for item in JSON.parse_string(FileAccess.get_file_as_string("res://assets/road_kit.json")):
		var prefab_path:String="res://scenes/environment/"+item.name+".tscn"
		var prefab:PackedScene
		if FileAccess.file_exists(prefab_path):prefab=load(prefab_path)
		else:prefab=make_prefab(item.name,"res://"+item.path,prefab_path,false)
		if not details.has_node(NodePath(item.name)):
			var instance:Node3D=prefab.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);instance.name=item.name;details.add_child(instance)
	world.set_script(WorldScript);save_scene(world,path);world.free()
	print("ASSEMBLED THREE INDEPENDENT ROAD SCENES; native curves retained");await process_frame;quit()

extends "res://tools/assemble_world.gd"
## Refresh derived geometry while preserving native prefab edits and layout.
var backup_directory:String
var backed_up:Dictionary={}
const CliffRefresh=preload("res://tools/cliff_refresh.gd")

func backup_file(path:String) -> void:
	if path.contains("::") or backed_up.has(path) or not FileAccess.file_exists(path):return
	var relative:=path.trim_prefix("res://")
	var target:=backup_directory+"/"+relative
	DirAccess.make_dir_recursive_absolute(target.get_base_dir())
	assert(DirAccess.copy_absolute(path,target)==OK)
	backed_up[path]=true

func refresh_prefab(kind:String,model_path:String,path:String,resource_root:="res://assets") -> PackedScene:
	if not FileAccess.file_exists(path):return make_prefab(kind,model_path,path,true,true)
	backup_file(path)
	var scene:Node3D=ResourceLoader.load(path,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE_DEEP).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var model:Node3D=scene.get_node("Model")
	var collider:CollisionShape3D=scene.get_node("Collision/Shape")
	# Preserve native node transforms, material overrides and custom fields.
	# Only this generated triangle shape follows the current imported geometry.
	if collider.shape is ConcavePolygonShape3D:
		var faces:=PackedVector3Array()
		var inverse:=transform_to(collider,scene).affine_inverse()
		var nodes:Array[Node]=model.find_children("*","MeshInstance3D",true,false)
		if model is MeshInstance3D:nodes.append(model)
		for node in nodes:
			var local:=inverse*transform_to(node,scene)
			for point in node.mesh.get_faces():faces.append(local*point)
		var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(faces)
		var shape_path:=resource_root+"/collision/"+kind+".res";backup_file(shape_path)
		assert(ResourceSaver.save(shape,shape_path)==OK);shape.take_over_path(shape_path);collider.shape=shape
	var mesh_path:=resource_root+"/meshes/"+kind+".res";backup_file(mesh_path)
	assert(ResourceSaver.save(find_mesh(model).mesh,mesh_path)==OK)
	save_scene(scene,path);scene.free()
	return ResourceLoader.load(path,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE_DEEP)

func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	backup_directory="res://captures/edit_backups/"+Time.get_datetime_string_from_system().replace(":","-")+"-"+str(Time.get_ticks_msec())
	var world_path:="res://scenes/world/World.tscn";backup_file(world_path)
	backup_file("res://assets/asset_catalog.json")
	var updated:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/terrain_updates.json"))
	var selected:Array[String]=[]
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--asset="):selected.append(arg.trim_prefix("--asset="))
	# An ordinary asset refresh touches only its own prefab and grounded props.
	if not selected.is_empty():updated=[]
	var kit:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/cliff_kit.json"))
	if FileAccess.file_exists("res://assets/mountain_kit.json"):kit.append_array(JSON.parse_string(FileAccess.get_file_as_string("res://assets/mountain_kit.json")))
	if not selected.is_empty():
		for kind in selected:assert(kit.any(func(item):return item.name==kind),"Unknown cliff/mountain asset: "+kind)
		kit=kit.filter(func(item):return item.name in selected)
	var catalog:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/asset_catalog.json"))
	# Imported meshes may already contain the new model. The still-old derived
	# colliders are the authoritative old footprint, before any resource writes.
	var previous_world:Node3D=ResourceLoader.load(world_path,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE_DEEP).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	previous_world.set_script(null);root.add_child(previous_world)
	var previous:=CliffRefresh.snapshot(previous_world,kit)
	previous_world.free()
	for item in updated:refresh_prefab(item.name,"res://"+item.path,"res://scenes/terrain/"+item.name+".tscn")
	for item in kit:
		prefabs[item.name]=refresh_prefab(item.name,"res://"+item.path,"res://scenes/prefabs/"+item.name+".tscn")
		var found:=false
		for entry in catalog:
			if entry.name==item.name:entry.merge(item,true);found=true;break
		if not found:catalog.append(item)
	var file:=FileAccess.open("res://assets/asset_catalog.json",FileAccess.WRITE);file.store_string(JSON.stringify(catalog,"\t"));file.close()
	# Fresh dependencies avoid mutating an allocated MultiMesh in the resource
	# cache while reloading transform_format/colors before instance_count.
	var world:Node3D=ResourceLoader.load(world_path,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE_DEEP).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	world.set_script(null);root.add_child(world)
	var matches:=CliffRefresh.matching_instances(world,kit)
	for item in kit:
		# A copied, renamed or reparented instance already represents this asset.
		if not matches[item.name].is_empty():continue
		var group_name:String=item.get("category","Cliffs")
		var cliffs:Node3D=world.get_node_or_null(NodePath(group_name))
		if not cliffs:cliffs=category(world,group_name)
		var origin:=Vector3(item.position[0],item.position[1],item.position[2])
		var instance:Node3D=prefabs[item.name].instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
		instance.name=item.name;cliffs.add_child(instance)
		instance.position=origin;instance.set_meta("asset_origin",origin)
	var refreshed:=CliffRefresh.finish(world,kit,previous)
	var changed_bounds:Array=refreshed.changed_bounds
	var regions:Dictionary={}
	for tile in world.get_node("Terrain").get_children():
		if not updated.any(func(item):return tile.scene_file_path=="res://scenes/terrain/"+item.name+".tscn"):continue
		var low:=Vector2(INF,INF);var high:=Vector2(-INF,-INF)
		for corner in [Vector3.ZERO,Vector3(768,0,0),Vector3(0,0,768),Vector3(768,0,768)]:
			var p:Vector3=tile.to_global(corner);low=low.min(Vector2(p.x,p.z));high=high.max(Vector2(p.x,p.z))
		for z in range(floori(low.y/768),floori(high.y/768)+1):
			for x in range(floori(low.x/768),floori(high.x/768)+1):
				var key:=Vector2i(x,z)
				if not regions.has(key):regions[key]=[]
				regions[key].append(tile)
	await physics_frame
	await physics_frame
	var moved:=0;var changed_groups:=0;var removed_count:=0
	for grove in world.get_node("Vegetation").get_children():
		var reseated:=CliffRefresh.reseat_grove(world,grove,regions,changed_bounds)
		var data:MultiMesh=reseated.data
		moved+=reseated.moved;removed_count+=reseated.removed
		if data:
			# A separate owned file also handles embedded Inspector resources
			# and avoids changing a grove sharing the former resource.
			var path:="res://assets/scatter/Grounded_"+str(grove.name)+".res"
			backup_file(grove.multimesh.resource_path);backup_file(path)
			assert(ResourceSaver.save(data,path)==OK);data.take_over_path(path);grove.multimesh=data;changed_groups+=1
	world.set_script(WorldScript);save_scene(world,world_path)
	print("CLIFF KIT INSTALLED ",kit.size()," independent complete prefabs across ",refreshed.instance_count," instances; terrain updated ",updated.size(),"; foliage reseated ",moved," in ",changed_groups," groups; removed from new water ",removed_count,"; backup ",backup_directory)
	world.free();prefabs.clear();meshes.clear()
	await process_frame
	await process_frame
	quit()

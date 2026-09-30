extends "res://tools/assemble_world.gd"
## One-shot landscape composition. Measurements only select locations in
## the native scene; saved transforms are ordinary editable 3D tree groups.
## Runtime never reads image coordinates or reruns this authoring script.
const SPECS=[
	["NearMeadowOak","oak",759,879,38,0,1],
	["EastMeadowCopse","oak",977,773,29,27,5],
	["WestShoreOaks","oak",508,754,27,17,3],
	["WestRoadCopse","oak",582,720,20,24,6],
	["MiddleMeadowTrees","oak",719,709,14,30,7],
	["CitadelOrchard","oak",917,658,9,48,16],
	["EastRoadTrees","oak",1088,691,13,35,12],
	["WestVillageWoods","oak",365,620,15,28,15],
	["WesternValleyWoods","oak",568,565,9,70,38],
	["MesaUpperValley","pine",325,534,8,45,25],
	["EasternShoreWoods","oak",1469,605,13,56,32],
	["LakeBendWoods","oak",1282,586,10,42,22],
	["AlpineValleyWoods","pine",1066,565,8,44,26],
	["NearMeadowShrubs","bush",966,780,8,37,9]
]

func ground(world:Node3D,p:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4)
	return world.get_world_3d().direct_space_state.intersect_ray(query)

func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	root.size=Vector2i(1672,941)
	# Read the camera's saved properties without instantiating another world
	# and its sky radiance textures just to copy five transform values.
	var camera:=Camera3D.new()
	var camera_section:=false
	for line in FileAccess.get_file_as_string("res://scenes/game.tscn").split("\n"):
		if line.begins_with("[node "):camera_section=line.begins_with('[node name="Camera" ')
		if not camera_section or not line.contains(" = "):continue
		var fields:=line.split(" = ",true,1);var property:=fields[0].strip_edges()
		if property in ["position","rotation","rotation_degrees","fov","near","far"]:camera.set(property,str_to_var(fields[1]))
	root.add_child(camera)
	var world_path:="res://scenes/world/World.tscn"
	var backup:="res://captures/edit_backups/groves-"+Time.get_datetime_string_from_system().replace(":","-")
	DirAccess.make_dir_recursive_absolute(backup)
	assert(DirAccess.copy_absolute(world_path,backup+"/World.tscn")==OK)
	var world:Node3D=load(world_path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	world.set_script(null);root.add_child(world)
	await physics_frame
	await physics_frame
	var vegetation:Node3D=world.get_node("Vegetation")
	for old in vegetation.get_children():
		if old.get_meta("authored_grove",false):vegetation.remove_child(old);old.free()
	var report:Array=[];var exclusions:Array=[]
	var focal:float=941.0/(2.0*tan(deg_to_rad(camera.fov*.5)))
	for spec in SPECS:
		var pixel:=Vector2(spec[2],spec[3])
		var ray:=PhysicsRayQueryParameters3D.create(camera.project_ray_origin(pixel),camera.project_ray_origin(pixel)+camera.project_ray_normal(pixel)*18000,4)
		var hit:=world.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty(),"Missing 3D ground at "+str(spec[0]))
		var center:Vector3=hit.position
		var depth:float=-camera.to_local(center).z
		var radius:float=float(spec[5])*depth/focal
		var kind:String=spec[1]
		var render_mesh:Mesh=load("res://assets/meshes/"+kind+".res")
		var model_height:float=render_mesh.get_aabb().size.y
		var desired_height:float=float(spec[4])*depth/focal
		var scale:float=desired_height/model_height
		var rng:=RandomNumberGenerator.new();rng.seed=hash(str(spec[0]))
		var transforms:Array[Transform3D]=[]
		for i in range(int(spec[6])):
			var angle:=rng.randf()*TAU;var r:float=0.0 if i==0 else sqrt(rng.randf())*radius
			var point:=center+Vector3(cos(angle)*r,0,sin(angle)*r*.72)
			var surface:=ground(world,point)
			if surface.is_empty() or surface.position.y<1 or surface.normal.y<.65:continue
			point=surface.position
			var instance_scale:float=scale*(1.0 if i==0 else rng.randf_range(.76,1.13))
			point.y-=render_mesh.get_aabb().position.y*instance_scale
			var basis:=Basis(Vector3.UP,rng.randf()*TAU).scaled(Vector3.ONE*instance_scale)
			transforms.append(Transform3D(basis,point-center))
		assert(not transforms.is_empty(),"Grove has no valid ground: "+str(spec[0]))
		var multi:=MultiMesh.new();multi.transform_format=MultiMesh.TRANSFORM_3D;multi.mesh=render_mesh;multi.instance_count=transforms.size()
		for i in range(transforms.size()):multi.set_instance_transform(i,transforms[i])
		var path:="res://assets/scatter/Authored_"+str(spec[0])+".res"
		if FileAccess.file_exists(path):assert(DirAccess.copy_absolute(path,backup+"/"+path.get_file())==OK)
		assert(ResourceSaver.save(multi,path)==OK);multi.take_over_path(path)
		var grove:=MultiMeshInstance3D.new();grove.name="Authored_"+str(spec[0]);grove.set_script(preload("res://scripts/scatter_group.gd"))
		grove.model_scene=load("res://scenes/prefabs/"+kind+".tscn");grove.multimesh=multi;grove.material_override=WORLD_MATERIAL
		grove.position=center;grove.visibility_range_end=4200;grove.set_meta("asset_kind",kind);grove.set_meta("authored_grove",true)
		vegetation.add_child(grove)
		exclusions.append({"center":center,"radius":maxf(radius,desired_height*.5)})
		report.append({"name":spec[0],"kind":kind,"position_metres":[center.x,center.y,center.z],"radius_metres":radius,"tree_height_metres":desired_height,"count":transforms.size()})
	var removed:=0
	for grove in vegetation.get_children():
		if grove.get_meta("authored_grove",false):continue
		var keep:Array[int]=[]
		for i in range(grove.multimesh.instance_count):
			var transform:Transform3D=grove.multimesh.get_instance_transform(i)
			var p:Vector3=grove.to_global(transform.origin);var discard:=false
			for area in exclusions:
				if Vector2(p.x-area.center.x,p.z-area.center.z).length()<area.radius:discard=true;break
			if discard:removed+=1
			else:keep.append(i)
		if keep.size()==grove.multimesh.instance_count:continue
		var path:="res://assets/scatter/Composed_"+str(grove.name)+".res"
		if FileAccess.file_exists(grove.multimesh.resource_path):assert(DirAccess.copy_absolute(grove.multimesh.resource_path,backup+"/"+grove.multimesh.resource_path.get_file())==OK)
		var source:MultiMesh=grove.multimesh
		var data:=MultiMesh.new();data.transform_format=MultiMesh.TRANSFORM_3D;data.mesh=source.mesh
		data.use_colors=source.use_colors;data.use_custom_data=source.use_custom_data;data.instance_count=keep.size()
		for i in range(keep.size()):
			data.set_instance_transform(i,source.get_instance_transform(keep[i]))
			if source.use_colors:data.set_instance_color(i,source.get_instance_color(keep[i]))
			if source.use_custom_data:data.set_instance_custom_data(i,source.get_instance_custom_data(keep[i]))
		assert(ResourceSaver.save(data,path)==OK);data.take_over_path(path);grove.multimesh=data
	world.set_script(WorldScript);save_scene(world,world_path)
	var file:=FileAccess.open("res://assets/vegetation_composition.json",FileAccess.WRITE);file.store_string(JSON.stringify({"groves":report,"removed_seed_instances":removed,"method":"Native Godot ground rays and saved editable world-space transforms. Authoring only; no runtime image coordinates."},"\t"));file.close()
	print("AUTHORED VEGETATION GROVES ",report.size(),"; removed seed instances ",removed)
	# SceneTree owns these nodes. Let its normal shutdown release the active
	# viewport and sky cache together, just as the playable scene does.
	quit()

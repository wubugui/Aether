extends "res://tools/install_cliff_kit.gd"
## Real renderer + physics regression; all writable resources stay in a unique
## captures fixture directory supplied by the Python runner. Never calls build().
var fixture_directory:String
var checks:Array=[]
var test_positions:Array[Vector3]=[]

func check(ok:bool,name:String,details:Variant=null) -> void:
	checks.append({"name":name,"passed":ok,"details":details})
	print("PASS " if ok else "FAIL ",name," ",details if details!=null else "")

func fixture_world(path:String) -> Node3D:
	var world:Node3D=ResourceLoader.load(path,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE_DEEP).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	root.add_child(world);return world

func hit_at(world:Node3D,p:Vector3) -> Dictionary:
	return world.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p.x,200,p.z),Vector3(p.x,-10,p.z),4))

func grove_position(grove:MultiMeshInstance3D,index:int) -> Vector3:
	return (grove.global_transform*grove.multimesh.get_instance_transform(index)).origin

func build() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--fixture-directory="):fixture_directory=arg.trim_prefix("--fixture-directory=")
	assert(fixture_directory.begins_with("res://captures/cliff_refresh_regressions/"))
	for child in ["collision","meshes","backups"]:DirAccess.make_dir_recursive_absolute(fixture_directory+"/"+child)
	backup_directory=fixture_directory+"/backups"
	check(DisplayServer.get_name()!="headless","real GPU backend",DisplayServer.get_name())
	var marker:=GDScript.new();marker.source_code="extends Node3D\n@export var asset_kind:String=\"cliff_fixture\"\n@export var custom_note:String=\"native edit survives\"\n"
	assert(marker.reload()==OK);assert(ResourceSaver.save(marker,fixture_directory+"/marker.gd")==OK)
	var source:=BoxMesh.new();source.size=Vector3(24,8,24)
	assert(ResourceSaver.save(source,fixture_directory+"/source.tres")==OK);source.take_over_path(fixture_directory+"/source.tres")
	var asset:=Node3D.new();asset.name="cliff_fixture";asset.set_script(marker)
	asset.set_meta("asset_origin",Vector3.ZERO);asset.set_meta("user_note","keep metadata")
	var model:=MeshInstance3D.new();model.name="Model";model.mesh=source;model.position.y=6;asset.add_child(model)
	var material:=StandardMaterial3D.new();material.albedo_color=Color(.71,.28,.45);material.roughness=.37;model.material_override=material
	var body:=StaticBody3D.new();body.name="Collision";body.collision_layer=5;body.collision_mask=2;asset.add_child(body)
	var collider:=CollisionShape3D.new();collider.name="Shape";collider.position=Vector3(.6,.2,-.8);body.add_child(collider)
	var points:=PackedVector3Array()
	for p in source.get_faces():points.append(collider.transform.affine_inverse()*model.transform*p)
	var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(points)
	assert(ResourceSaver.save(shape,fixture_directory+"/collision/cliff_fixture.res")==OK);shape.take_over_path(fixture_directory+"/collision/cliff_fixture.res");collider.shape=shape
	var prefab_path:=fixture_directory+"/fixture.tscn";save_scene(asset,prefab_path);asset.free()
	var prefab:PackedScene=ResourceLoader.load(prefab_path,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE_DEEP)
	var world:=Node3D.new();world.name="FixtureWorld";root.add_child(world)
	var ground:=StaticBody3D.new();ground.name="Ground";ground.collision_layer=4;ground.collision_mask=0;world.add_child(ground)
	var ground_shape:=CollisionShape3D.new();var slab:=BoxShape3D.new();slab.size=Vector3(600,2,600);ground_shape.shape=slab;ground_shape.position.y=1;ground.add_child(ground_shape)
	var ground_mesh:=MeshInstance3D.new();var slab_mesh:=BoxMesh.new();slab_mesh.size=slab.size;ground_mesh.mesh=slab_mesh;ground_mesh.position.y=1;ground.add_child(ground_mesh)
	var normal:=Node3D.new();normal.name="Cliffs";world.add_child(normal)
	var original:Node3D=prefab.instantiate();original.name="cliff_fixture";normal.add_child(original);original.position=Vector3(-35,0,0)
	var group:=Node3D.new();group.name="UserDistrict";world.add_child(group);group.position=Vector3(45,0,20);group.rotation.y=.61;group.scale=Vector3(1.2,.9,1.1)
	var copy:Node3D=prefab.instantiate();copy.name="RenamedOutcrop";group.add_child(copy);copy.position=Vector3(8,0,-5);copy.rotation.y=.37;copy.scale=Vector3(1.35,1.2,.8)
	copy.set("custom_note","copy edited by user");copy.set_meta("user_note","moved to another group")
	var independent:Node3D=prefab.instantiate();independent.name="UnpackedNativeCopy";independent.scene_file_path="";world.add_child(independent);independent.position=Vector3(-65,0,45);independent.rotation.y=.18;independent.scale=Vector3(.8,1.1,1.2)
	var instance_paths:Array[String]=[];var original_transforms:Dictionary={};var authored_fields:Dictionary={}
	for instance in [original,copy,independent]:
		var path:=str(world.get_path_to(instance));instance_paths.append(path);original_transforms[path]=instance.global_transform
		authored_fields[path]=[instance.get("custom_note"),instance.get_meta("user_note")]
		test_positions.append(instance.to_global(Vector3(10.5,10,10.5)))
	var vegetation:=Node3D.new();vegetation.name="Vegetation";world.add_child(vegetation)
	var grove:=MultiMeshInstance3D.new();grove.name="EditedGrove";vegetation.add_child(grove);grove.position=Vector3(3,.2,-4);grove.rotation.y=.24;grove.scale=Vector3(.9,1.1,1.2);grove.set_meta("asset_kind","oak")
	var data:=MultiMesh.new();data.transform_format=MultiMesh.TRANSFORM_3D;data.use_colors=true;data.use_custom_data=true;var tree:=BoxMesh.new();tree.size=Vector3(1,2,1);data.mesh=tree;data.instance_count=4
	test_positions.append(Vector3(170,17,170))
	for i in range(4):
		var tr:=Transform3D(Basis(Vector3.UP,.17*i).scaled(Vector3(1+.1*i,1,1)),test_positions[i])
		data.set_instance_transform(i,grove.global_transform.affine_inverse()*tr)
		data.set_instance_color(i,Color(.1+i*.1,.3,.5,1));data.set_instance_custom_data(i,Color(.7,.2+i*.1,.4,1))
	grove.multimesh=data
	var unrelated:=MultiMeshInstance3D.new();unrelated.name="SharedUnrelated";vegetation.add_child(unrelated);unrelated.multimesh=data;unrelated.position=Vector3(-220,0,-220)
	var camera:=Camera3D.new();camera.name="Camera";world.add_child(camera);camera.position=Vector3(80,115,155);camera.look_at(Vector3(0,0,20));camera.current=true
	var sun:=DirectionalLight3D.new();world.add_child(sun);sun.rotation=Vector3(-.8,-.4,0)
	var world_path:=fixture_directory+"/world.tscn";save_scene(world,world_path);world.free()
	# Simulate the real ordering: imported geometry is already smaller, while
	# the derived collider and planted instances still describe the old model.
	var smaller:=BoxMesh.new();smaller.size=Vector3(6,8,6)
	assert(ResourceSaver.save(smaller,fixture_directory+"/source.tres")==OK);smaller.take_over_path(fixture_directory+"/source.tres")
	world=fixture_world(world_path)
	await physics_frame;await physics_frame
	var kit:Array=[{"name":"cliff_fixture","prefab_path":prefab_path,"position":[0,0,0],"original_origin":[0,0,0]}]
	var before:=CliffRefresh.snapshot(world,kit)
	check(before.instances.size()==3,"all canonical, renamed/reparented prefab and asset_kind-only instances discovered",before.instances.size())
	for i in range(3):
		var hit:=hit_at(world,test_positions[i])
		check(not hit.is_empty() and absf(hit.position.y-test_positions[i].y)<.02,"old derived collider still supports planted instance "+str(i))
	world.free()
	refresh_prefab("cliff_fixture",fixture_directory+"/source.tres",prefab_path,fixture_directory)
	world=fixture_world(world_path)
	var updated:=CliffRefresh.finish(world,kit,before)
	await physics_frame;await physics_frame;await process_frame
	check(updated.instance_count==3,"geometry refresh covers all three edited instances")
	grove=world.get_node("Vegetation/EditedGrove");unrelated=world.get_node("Vegetation/SharedUnrelated")
	var old_data:MultiMesh=grove.multimesh
	for i in range(3):
		check(CliffRefresh.in_footprints(test_positions[i],before.bounds) and not CliffRefresh.in_footprints(test_positions[i],updated.new_bounds),"shrunken-model sample is in old footprint only "+str(i))
		var hit:=hit_at(world,test_positions[i])
		check(not hit.is_empty() and absf(hit.position.y-2)<.02,"actual new physics exposes lower ground at former cliff foot "+str(i))
	var negative:=CliffRefresh.reseat_grove(world,grove,{},updated.new_bounds)
	check(negative.moved==0,"negative control: new bounds alone misses all old-footprint trees")
	var canonical_bounds:Array=[]
	for record in before.instances:
		if record.path==instance_paths[0]:canonical_bounds.append_array(record.bounds)
	var canonical_only:=CliffRefresh.reseat_grove(world,grove,{},canonical_bounds)
	check(canonical_only.moved==1,"negative control: canonical node-only lookup misses both edited copies")
	var result:=CliffRefresh.reseat_grove(world,grove,{},updated.changed_bounds)
	check(result.moved==3 and result.removed==0,"old/new union reseats all three trees without deleting them",{"moved":result.moved,"removed":result.removed})
	grove.multimesh=result.data
	for i in range(4):
		var p:=grove_position(grove,i)
		check(absf(p.y-(2 if i<3 else 17))<.02 and Vector2(p.x,p.z).distance_to(Vector2(test_positions[i].x,test_positions[i].z))<.002,"correct ground height and preserved horizontal placement "+str(i),str(p))
		check(grove.multimesh.get_instance_transform(i).basis.is_equal_approx(old_data.get_instance_transform(i).basis),"scatter scale/rotation preserved "+str(i))
		check(grove.multimesh.get_instance_color(i).is_equal_approx(old_data.get_instance_color(i)) and grove.multimesh.get_instance_custom_data(i).is_equal_approx(old_data.get_instance_custom_data(i)),"scatter color/custom data preserved "+str(i))
	check(unrelated.multimesh==old_data and grove.multimesh!=old_data,"shared unrelated MultiMesh remains unchanged")
	for path in instance_paths:
		var instance:Node3D=world.get_node(path)
		check(instance.global_transform.is_equal_approx(original_transforms[path]) and instance.get("custom_note")==authored_fields[path][0] and instance.get_meta("user_note")==authored_fields[path][1],"native instance transform and authored fields preserved "+path)
		check(instance.get_node("Model").material_override.albedo_color.is_equal_approx(Color(.71,.28,.45)) and instance.get_node("Collision").collision_mask==2 and instance.get_node("Collision/Shape").position.is_equal_approx(Vector3(.6,.2,-.8)),"material/collider overrides preserved "+path)
	assert(ResourceSaver.save(grove.multimesh,fixture_directory+"/scatter.res")==OK);grove.multimesh.take_over_path(fixture_directory+"/scatter.res")
	save_scene(world,world_path);world.free();world=fixture_world(world_path)
	await physics_frame;await physics_frame;await process_frame
	grove=world.get_node("Vegetation/EditedGrove")
	for i in range(4):check(absf(grove_position(grove,i).y-(2 if i<3 else 17))<.02,"saved and reloaded GPU MultiMesh placement "+str(i))
	for path in instance_paths:
		var instance:Node3D=world.get_node(path)
		check(instance.get("custom_note")==authored_fields[path][0] and instance.get_meta("user_note")==authored_fields[path][1],"per-instance edited fields survive final save/reload "+path)
	check(CliffRefresh.reseat_grove(world,grove,{},updated.changed_bounds).moved==0,"second refresh is idempotent after save/reload")
	kit[0].position=[1,0,2]
	CliffRefresh.finish(world,kit,before)
	for path in instance_paths:
		var instance:Node3D=world.get_node(path);var prior:Transform3D=original_transforms[path]
		check(instance.global_transform.basis.is_equal_approx(prior.basis) and instance.global_transform.origin.distance_to(prior*Vector3(1,0,2))<.002,"origin compensation respects full rotated/scaled hierarchy "+path)
	check(backed_up.has(prefab_path) and backed_up.has(fixture_directory+"/collision/cliff_fixture.res"),"fixture prefab and derived collision backed up before refresh")
	await process_frame;await process_frame
	root.get_texture().get_image().save_png(fixture_directory+"/fixture.png")
	var report:={"passed":checks.all(func(c):return c.passed),"checks":checks,"display_server":DisplayServer.get_name(),"renderer":RenderingServer.get_video_adapter_name(),"frames_drawn":Engine.get_frames_drawn(),"scope":"Actual GPU, physics rays, temporary prefab refresh, old/new footprints, transformed copies, GPU MultiMesh persistence. Production assets never passed to the installer."}
	var output:=FileAccess.open(fixture_directory+"/gpu-report.json",FileAccess.WRITE);output.store_string(JSON.stringify(report,"\t"));output.close()
	world.free();quit(0 if report.passed else 1)

extends "res://tools/install_cliff_kit.gd"
## A native Godot level-design edit. Models remain separate prefab instances.
func survey(u:float,v:float,height:float) -> Vector3:
	var f:=941.0/(2*tan(deg_to_rad(25)));var pitch:=deg_to_rad(-3.5)
	var x:float=(u-836)/f;var y:float=(470.5-v)/f
	var ray:=Vector3(x,cos(pitch)*y+sin(pitch),sin(pitch)*y-cos(pitch))
	return Vector3(0,145,250)+ray*((height-145)/ray.y)

func ground(world:Node3D,p:Vector3) -> float:
	var ray:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4)
	var hit:=world.get_world_3d().direct_space_state.intersect_ray(ray)
	return hit.position.y if not hit.is_empty() else 0.0

func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	backup_directory="res://captures/edit_backups/level-design-"+Time.get_datetime_string_from_system().replace(":","-")
	var path:="res://scenes/world/World.tscn";backup_file(path)
	var world:Node3D=load(path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	world.set_script(null);root.add_child(world)
	await physics_frame
	await physics_frame
	var hamlets:=[survey(838,745,22),survey(908,660,18),survey(1113,683,21)]
	var houses:Array[Node3D]=[]
	for node in world.get_node("Settlements").get_children():
		if node.asset_kind=="cottage" and node.position.x>-200 and node.position.x<350 and node.position.z>-540 and node.position.z<220:houses.append(node)
		if node.asset_kind=="castle":node.scale=Vector3(1.2,.52,.78)
	for i in range(houses.size()):
		var house:Node3D=houses[i];var row:=i/3
		var p:Vector3=hamlets[i%3]+Vector3((row%3-1)*9.5,0,(row/3)*10.5)
		p.y=ground(world,p)-.15;house.position=p
		house.scale=Vector3.ONE*(.50+.06*(i%3));house.rotation.y=0 if i%2==0 else PI*.5
	# Place the optional flight challenges on a coherent southern route.
	# They remain real, always visible world objects; the opening view faces north.
	var route:=[Vector2(120,330),Vector2(155,440),Vector2(330,550),Vector2(570,665),Vector2(890,760),Vector2(1170,815),Vector2(1430,920),Vector2(1260,1250),Vector2(700,1550),Vector2(100,1800),Vector2(-350,2030),Vector2(-680,2100)]
	var rings:=world.get_node("FlightRings").get_children()
	rings.sort_custom(func(a,b):return a.get_meta("ring_index")<b.get_meta("ring_index"))
	for i in range(rings.size()):
		var p:=Vector3(route[i].x,0,route[i].y);p.y=ground(world,p)+80
		rings[i].position=p
	var geography=preload("res://scripts/world_math.gd").new()
	var removed:=0;var changed:=0
	for grove in world.get_node("Vegetation").get_children():
		if not grove.get_meta("asset_kind") in ["oak","pine","poplar"]:continue
		var keep:Array[int]=[];var source:MultiMesh=grove.multimesh
		for i in range(source.instance_count):
			var p:Vector3=(grove.global_transform*source.get_instance_transform(i)).origin
			if p.z<-600 and p.z>-3400 and absf(p.x)<2500 and geography.noise_at(p.x*.22+945,p.z*.22-217)<.16:removed+=1;continue
			keep.append(i)
		if keep.size()==source.instance_count:continue
		var data:=MultiMesh.new();data.transform_format=MultiMesh.TRANSFORM_3D;data.mesh=source.mesh;data.instance_count=keep.size()
		for i in range(keep.size()):data.set_instance_transform(i,source.get_instance_transform(keep[i]))
		var resource_path:="res://assets/scatter/Arranged_"+str(grove.name)+".res"
		backup_file(source.resource_path);backup_file(resource_path)
		assert(ResourceSaver.save(data,resource_path)==OK);data.take_over_path(resource_path);grove.multimesh=data;changed+=1
	world.set_script(WorldScript);save_scene(world,path)
	print("NATIVE LEVEL DESIGN: ",houses.size()," cottages in 3 hamlets, 12 southern flight rings, ",removed," trees removed to open northern meadows in ",changed," groups; backup ",backup_directory)
	world.free()
	await process_frame
	await process_frame
	quit()

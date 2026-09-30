extends SceneTree
## One-shot Godot editor build. Outputs native reusable scenes and a native
## World.tscn. Reimporting Blender models never runs this scene assembly step.
const InstanceScript=preload("res://scripts/asset_instance.gd")
const PortScript=preload("res://scripts/world_port.gd")
const WorldScript=preload("res://scripts/open_world.gd")
const WORLD_MATERIAL=preload("res://materials/world.tres")
const CLOUD_MATERIAL=preload("res://materials/cloud.tres")
var prefabs:Dictionary={}
var meshes:Dictionary={}
var stats:Dictionary={"terrain_prefabs":0,"asset_prefabs":0,"world_instances":0,"scattered_models":0,"multimeshes":0}

func _initialize() -> void:
	call_deferred("build")

func own_all(node:Node,scene:Node) -> void:
	for child in node.get_children():
		child.owner=scene
		# Keep the imported/prefab instance boundary. Descendants keep their
		# original owner so the world never embeds or duplicates their meshes.
		if child.scene_file_path.is_empty():own_all(child,scene)

func save_scene(node:Node,path:String) -> PackedScene:
	own_all(node,node)
	var packed:=PackedScene.new()
	assert(packed.pack(node)==OK,"Cannot pack "+path)
	assert(ResourceSaver.save(packed,path)==OK,"Cannot save "+path)
	return load(path)

func find_mesh(node:Node) -> MeshInstance3D:
	if node is MeshInstance3D:return node
	for child in node.get_children():
		var found:=find_mesh(child)
		if found:return found
	return null

func transform_to(node:Node3D,ancestor:Node3D) -> Transform3D:
	var transform:=node.transform
	var parent:=node.get_parent()
	while parent!=ancestor and parent is Node3D:
		transform=parent.transform*transform;parent=parent.get_parent()
	return transform

func make_prefab(kind:String,model_path:String,path:String,solid:bool,terrain:=false) -> PackedScene:
	var scene:=Node3D.new();scene.name=kind
	scene.set_script(InstanceScript);scene.asset_kind=kind
	scene.surface_material=CLOUD_MATERIAL if kind.begins_with("cloud") else (preload("res://materials/cliff.tres") if kind.begins_with("cliff_") or kind.begins_with("massif_") else WORLD_MATERIAL)
	var model:Node3D=load(model_path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	model.name="Model";scene.add_child(model)
	for node in model.find_children("*","MeshInstance3D",true,false):node.material_override=scene.surface_material
	if model is MeshInstance3D:model.material_override=scene.surface_material
	if solid:
		var body:=StaticBody3D.new();body.name="Collision";body.collision_layer=5 if terrain else 1;body.collision_mask=2;scene.add_child(body)
		var collider:=CollisionShape3D.new();collider.name="Shape";body.add_child(collider)
		if kind in ["oak","pine","poplar"]:
			var shape:=CapsuleShape3D.new();shape.radius=2.4;shape.height=11;collider.shape=shape;collider.position.y=5.5
		else:
			var faces:=PackedVector3Array()
			var nodes:Array[Node]=model.find_children("*","MeshInstance3D",true,false)
			if model is MeshInstance3D:nodes.append(model)
			for node in nodes:
				var local:=transform_to(node,scene)
				for p in node.mesh.get_faces():faces.append(local*p)
			var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(faces);collider.shape=shape
		var collision_path:="res://assets/collision/"+kind+".res"
		assert(ResourceSaver.save(collider.shape,collision_path)==OK)
		collider.shape=load(collision_path)
	var packed:=save_scene(scene,path)
	var mesh_path:="res://assets/meshes/"+kind+".res"
	assert(ResourceSaver.save(find_mesh(model).mesh,mesh_path)==OK)
	meshes[kind]=load(mesh_path)
	scene.free()
	return packed

func category(root:Node3D,label:String) -> Node3D:
	var node:=Node3D.new();node.name=label;root.add_child(node);return node

func build() -> void:
	if DisplayServer.get_name()=="headless":
		push_error("Assembly needs the real rendering backend to serialize MultiMesh transforms. Run this editor build without --headless.")
		quit(1);return
	for path in ["scenes/world","scenes/prefabs","scenes/terrain","scenes/environment","assets/scatter","assets/meshes","assets/collision"]:DirAccess.make_dir_recursive_absolute("res://"+path)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/world_layout.json"))
	var modules:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/world_modules.json"))
	var catalog:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/asset_catalog.json"))
	build_airship()
	for item in catalog:
		var kind:String=item.name
		prefabs[kind]=make_prefab(kind,"res://"+item.path,"res://scenes/prefabs/"+kind+".tscn",not kind.begins_with("cloud") and not kind in ["bush","mill_rotor","sky_ring"],kind.begins_with("cliff_") or kind.begins_with("massif_"))
		stats.asset_prefabs+=1
	var world:=Node3D.new();world.name="World"
	var terrain:=category(world,"Terrain");var details:=category(world,"LandDetails")
	var settlements:=category(world,"Settlements");var vegetation:=category(world,"Vegetation")
	var clouds:=category(world,"Clouds");var rings:=category(world,"FlightRings")
	var ports:=category(world,"Ports")
	var cliffs:=category(world,"Cliffs")
	if FileAccess.file_exists("res://assets/cliff_kit.json"):
		for item in JSON.parse_string(FileAccess.get_file_as_string("res://assets/cliff_kit.json")):
			var instance:Node3D=prefabs[item.name].instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
			cliffs.add_child(instance);instance.name=item.name
			instance.position=Vector3(item.position[0],item.position[1],item.position[2])
			instance.set_meta("asset_origin",instance.position)
	if FileAccess.file_exists("res://assets/mountain_kit.json"):
		var mountains:=category(world,"Mountains")
		for item in JSON.parse_string(FileAccess.get_file_as_string("res://assets/mountain_kit.json")):
			var instance:Node3D=prefabs[item.name].instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
			mountains.add_child(instance);instance.name=item.name
			instance.position=Vector3(item.position[0],item.position[1],item.position[2])
			instance.set_meta("asset_origin",instance.position)
	for name in modules:
		var entry:Dictionary=modules[name];var is_terrain:bool=name.begins_with("Ground_")
		var path:String="res://scenes/"+("terrain/" if is_terrain else "environment/")+name+".tscn"
		var packed:=make_prefab(name,"res://"+entry.path,path,is_terrain,is_terrain)
		var instance:Node3D=packed.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);instance.name=name
		(terrain if is_terrain else details).add_child(instance)
		instance.position=Vector3(entry.position[0],entry.position[1],entry.position[2])
		if is_terrain:
			instance.set_meta("terrain_cell",Vector2i(data.chunks[name].x,data.chunks[name].z));stats.terrain_prefabs+=1
		stats.world_instances+=1
	var groups:Dictionary={}
	var cloud_names:=["cloud_primary","cloud_middle","cloud_low","cloud_edge","cloud_wisp","cloud"]
	var cloud_index:=0;var ring_index:=0
	for i in range(data.props.size()):
		var p:Array=data.props[i];var kind:String=p[0]
		if kind=="cloud":
			if cloud_index<cloud_names.size():kind=cloud_names[cloud_index]
			cloud_index+=1
		if kind in ["oak","pine","poplar","rock","bush"]:
			var cell:=Vector2i(floori(p[1]/768),floori(p[3]/768))
			var key:="%s_%s_%s" % [kind,cell.x,cell.y]
			if not groups.has(key):groups[key]={"kind":kind,"cell":cell,"entries":[]}
			groups[key].entries.append(p)
		else:
			var instance:Node3D=prefabs[kind].instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
			var parent:=clouds if kind.begins_with("cloud") else (rings if kind=="sky_ring" else settlements)
			parent.add_child(instance);instance.name=kind+"_%s"%i
			instance.position=Vector3(p[1],p[2],p[3]);instance.scale=Vector3.ONE*p[4];instance.rotation.y=p[5]
			if kind=="sky_ring":instance.set_meta("ring_index",ring_index);ring_index+=1
			stats.world_instances+=1
	for key in groups:
		var group:Dictionary=groups[key];var multi:=MultiMesh.new();multi.transform_format=MultiMesh.TRANSFORM_3D
		multi.mesh=meshes[group.kind];multi.instance_count=group.entries.size()
		var origin:=Vector3(group.cell.x*768,0,group.cell.y*768)
		for i in range(group.entries.size()):
			var p:Array=group.entries[i]
			multi.set_instance_transform(i,Transform3D(Basis(Vector3.UP,p[5]).scaled(Vector3.ONE*p[4]),Vector3(p[1],p[2],p[3])-origin))
		assert(absf(multi.get_instance_transform(0).basis.determinant())>.001,"Missing render-backend instance buffer: "+key)
		var path:String="res://assets/scatter/"+key+".res";assert(ResourceSaver.save(multi,path)==OK)
		var grove:=MultiMeshInstance3D.new();grove.set_script(preload("res://scripts/scatter_group.gd"))
		grove.model_scene=prefabs[group.kind];grove.name=key;grove.multimesh=load(path);grove.position=origin
		grove.material_override=WORLD_MATERIAL;grove.visibility_range_end=3200
		grove.set_meta("asset_kind",group.kind);vegetation.add_child(grove)
		stats.scattered_models+=multi.instance_count;stats.multimeshes+=1
	for p in data.ports:
		var marker:=Marker3D.new();marker.set_script(PortScript);marker.name=p.id
		marker.port_id=p.id;marker.display_name=p.name;marker.landmark_style=p.style
		marker.ground_offset=p.pad_y-p.ground;marker.inner_radius=p.inner_radius;marker.outer_radius=p.outer_radius
		marker.position=Vector3(p.x,p.pad_y,p.z);ports.add_child(marker)
	# Water is an engine plane, shader and collision surface, not a Blender world.
	var ocean:=MeshInstance3D.new();ocean.name="Ocean"
	var plane:=PlaneMesh.new();plane.size=Vector2(100000,100000);ocean.mesh=plane
	var water:=ShaderMaterial.new();water.shader=preload("res://scripts/open_water.gdshader");ocean.material_override=water
	ocean.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var sea_body:=StaticBody3D.new();sea_body.name="SeaCollision";sea_body.collision_layer=5;sea_body.collision_mask=2;ocean.add_child(sea_body)
	var sea_shape:=CollisionShape3D.new();sea_shape.name="Shape";var boundary:=WorldBoundaryShape3D.new();boundary.plane=Plane(Vector3.UP,0);sea_shape.shape=boundary;sea_body.add_child(sea_shape)
	var sea_prefab:=save_scene(ocean,"res://scenes/environment/Ocean.tscn");ocean.free();world.add_child(sea_prefab.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE))
	world.set_script(WorldScript)
	save_scene(world,"res://scenes/world/World.tscn")
	world.free()
	var report:=FileAccess.open("res://captures/godot-assembly.json",FileAccess.WRITE);report.store_string(JSON.stringify(stats,"\t"))
	print("GODOT NATIVE WORLD ASSEMBLED ",JSON.stringify(stats))
	prefabs.clear();meshes.clear()
	await process_frame
	await process_frame
	quit()

func build_airship() -> void:
	var ship:=CharacterBody3D.new();ship.name="Airship";ship.set_script(preload("res://scripts/airship_body.gd"))
	ship.collision_layer=2;ship.collision_mask=1;ship.motion_mode=CharacterBody3D.MOTION_MODE_FLOATING
	ship.max_slides=8;ship.safe_margin=.07
	var visuals:=Node3D.new();visuals.name="Visuals";ship.add_child(visuals)
	var model:Node3D=load("res://assets/airship.glb").instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);model.name="Model";visuals.add_child(model)
	var propeller:Node3D=load("res://assets/propeller.glb").instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);propeller.name="Propeller";visuals.add_child(propeller)
	propeller.position=Vector3(7.05,4.10,0);propeller.rotation=Vector3(.15,.34906585,0);propeller.scale=Vector3.ONE*1.22
	var envelope:MeshInstance3D=model.find_child("Envelope",true,false)
	var gas_shape:=CollisionShape3D.new();gas_shape.name="EnvelopeCollision";gas_shape.shape=envelope.mesh.create_convex_shape();ship.add_child(gas_shape)
	var hull:=CollisionShape3D.new();hull.name="HullCollision";var shape:=BoxShape3D.new();shape.size=Vector3(8.3,3.1,2.8)
	hull.shape=shape;hull.position=Vector3(0,-2.3,0);ship.add_child(hull)
	for part in visuals.find_children("*","MeshInstance3D",true,false):
		part.material_override=preload("res://materials/flag.tres") if part.name=="Flag" else preload("res://materials/ship.tres")
	save_scene(ship,"res://scenes/prefabs/Airship.tscn");ship.free()

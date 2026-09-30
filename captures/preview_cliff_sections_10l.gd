extends SceneTree
## Read-only modeling study. All replacements occur in this process's memory.
func _initialize() -> void:
	call_deferred("preview")

func preview() -> void:
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	replace_model(game,"cliff_front_columns","prototype")
	replace_model(game,"cliff_western_slab","western_slab")
	replace_model(game,"cliff_crown","crown")
	replace_model(game,"cliff_central_wall","central_wall")
	replace_model(game,"cliff_shadow_buttress","shadow_buttress")
	for cell in ["Ground_0_0","Ground_0_-1"]:
		replace_asset(game.get_node("World/Terrain/"+cell),"D:/test6/captures/round-10d-"+cell+".glb")
	replace_asset(game.get_node("World/Cliffs/cliff_eastern_plateau"),"D:/test6/captures/cliff_sections_10l_eastern_plateau.glb")
	root.add_child(game)
	await physics_frame
	await physics_frame
	for uv in [Vector2(1200,790),Vector2(1230,810),Vector2(1270,798),Vector2(1310,785),Vector2(1235,720)]:
		var cam:Camera3D=game.get_node("Camera")
		var p:Vector3=cam.project_ray_origin(uv)
		var r:=PhysicsRayQueryParameters3D.create(p,p+cam.project_ray_normal(uv)*500,4)
		var hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(r)
		print("MODEL STUDY OCCLUSION ",uv," ",hit.get("collider")," ",hit.get("position"))
		if hit.has("collider"):print(hit.collider.get_path())

func replace_model(game:Node3D,kind:String,suffix:String) -> void:
	var asset:Node3D=game.get_node("World/Cliffs/"+kind)
	replace_asset(asset,"D:/test6/captures/cliff_sections_10d_"+suffix+".glb")

func replace_asset(asset:Node3D,file:String) -> void:
	var prior:Node3D=asset.get_node("Model")
	var transform:Transform3D=prior.transform
	asset.remove_child(prior);prior.free()
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	assert(document.append_from_file(file,state)==OK)
	var model:Node3D=document.generate_scene(state)
	model.name="Model";model.transform=transform;asset.add_child(model)
	# Derived collision changes with this geometry in this temporary instance.
	var faces:=PackedVector3Array()
	for mesh in model.find_children("*","MeshInstance3D",true,false):
		for p in mesh.mesh.get_faces():faces.append(p)
	var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(faces)
	asset.get_node("Collision/Shape").shape=shape

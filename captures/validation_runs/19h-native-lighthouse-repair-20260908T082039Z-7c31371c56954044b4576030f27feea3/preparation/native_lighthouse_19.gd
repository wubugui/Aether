extends SceneTree
## Scoped derived-resource installation / independent reopened native checks.
func _initialize() -> void:call_deferred("run")
func relative_transform(node:Node3D,ancestor:Node3D) -> Transform3D:
	var value:=node.transform
	var parent:=node.get_parent()
	while parent!=ancestor:
		assert(parent is Node3D);value=parent.transform*value;parent=parent.get_parent()
	return value
func mesh_nodes(model:Node3D) -> Array[Node]:
	return model.find_children("*","MeshInstance3D",true,false)
func model_faces(scene:Node3D) -> PackedVector3Array:
	var faces:=PackedVector3Array()
	var collider:Node3D=scene.get_node("Collision/Shape")
	var inverse:=relative_transform(collider,scene).affine_inverse()
	for node in mesh_nodes(scene.get_node("Model")):
		var transform:=inverse*relative_transform(node,scene)
		for point in node.mesh.get_faces():faces.append(transform*point)
	return faces
func run() -> void:
	var mode:=""
	var output:=""
	var identity:=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--mode="):mode=arg.trim_prefix("--mode=")
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
		if arg.begins_with("--validation-run="):identity=arg.trim_prefix("--validation-run=")
	assert(mode in ["install","check"] and not output.is_empty() and not identity.is_empty())
	assert(not FileAccess.file_exists(output))
	var scene:Node3D=load("res://scenes/prefabs/lighthouse.tscn").instantiate()
	assert(scene.surface_material==null)
	var nodes:=mesh_nodes(scene.get_node("Model"));assert(nodes.size()==24)
	var faces:=model_faces(scene)
	if mode=="install":
		var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(faces)
		assert(ResourceSaver.save(shape,"res://assets/collision/lighthouse.res")==OK)
		var combined:=ArrayMesh.new()
		for node in nodes:
			var transform:=relative_transform(node,scene)
			var normal_transform:=transform.basis.inverse().transposed()
			for surface in range(node.mesh.get_surface_count()):
				var arrays:Array=node.mesh.surface_get_arrays(surface)
				var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
				var normals:PackedVector3Array=arrays[Mesh.ARRAY_NORMAL]
				for i in range(vertices.size()):vertices[i]=transform*vertices[i]
				for i in range(normals.size()):normals[i]=(normal_transform*normals[i]).normalized()
				arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals
				arrays[Mesh.ARRAY_TANGENT]=null
				combined.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
				combined.surface_set_material(combined.get_surface_count()-1,node.mesh.surface_get_material(surface))
		assert(combined.get_surface_count()==24)
		assert(ResourceSaver.save(combined,"res://assets/meshes/lighthouse.res")==OK)
		var file:=FileAccess.open(output,FileAccess.WRITE)
		file.store_string(JSON.stringify({"run_id":identity,"mode":mode,"passed":true,"mesh_nodes":nodes.size(),"combined_surfaces":combined.get_surface_count(),"collision_triangles":faces.size()/3},"  "));file.close()
		print("LIGHTHOUSE DERIVED RESOURCES INSTALLED 24 surfaces / ",faces.size()/3," triangles")
		scene.free();quit();return
	var shape:ConcavePolygonShape3D=scene.get_node("Collision/Shape").shape
	assert(shape.backface_collision)
	var actual:=shape.get_faces();assert(actual.size()==faces.size())
	var max_error:=0.
	for i in range(faces.size()):max_error=maxf(max_error,faces[i].distance_to(actual[i]))
	assert(max_error<.0001)
	var combined:Mesh=load("res://assets/meshes/lighthouse.res");assert(combined.get_surface_count()==24)
	scene.free()
	var world:Node3D=load("res://scenes/world/World.tscn").instantiate()
	world.set_script(null);root.add_child(world)
	await physics_frame;await physics_frame;await physics_frame
	var records:Array=[]
	for instance in world.get_node("Settlements").get_children():
		if instance.get("asset_kind")!="lighthouse":continue
		assert(instance.surface_material==null)
		var part_nodes:=mesh_nodes(instance.get_node("Model"));assert(part_nodes.size()==24)
		var transparent:=0
		for node in part_nodes:
			assert(node.material_override==null)
			for surface in range(node.mesh.get_surface_count()):
				var mat:Material=node.get_active_material(surface)
				assert(mat is StandardMaterial3D)
				if mat.transparency==BaseMaterial3D.TRANSPARENCY_ALPHA:transparent+=1
		assert(transparent==13)
		var contacts:Array=[]
		for y in [5.,12.]:
			for i in range(8):
				var angle:float=TAU*(float(i)+.5)/8.
				var start:Vector3=instance.to_global(Vector3(cos(angle)*12,y,sin(angle)*12))
				var finish:Vector3=instance.to_global(Vector3(0,y,0))
				var query:=PhysicsRayQueryParameters3D.create(start,finish,1)
				var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
				assert(not hit.is_empty() and hit.collider==instance.get_node("Collision"))
				contacts.append({"height":y,"angle":angle,"hit":[hit.position.x,hit.position.y,hit.position.z]})
		records.append({"instance":str(instance.name),"position":[instance.position.x,instance.position.y,instance.position.z],"mesh_nodes":24,"transparent_surfaces":transparent,"collision_contacts":contacts})
	assert(records.size()==2)
	var file:=FileAccess.open(output,FileAccess.WRITE)
	file.store_string(JSON.stringify({"run_id":identity,"mode":mode,"passed":true,"scope":"Reopened native prefab/material ownership, whole-model derived collision identity and 32 local wall contact rays on two unchanged placements. Not complete flight or visual acceptance.","collision_vertex_error_max_m":max_error,"collision_triangles":faces.size()/3,"combined_surfaces":combined.get_surface_count(),"instances":records,"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"model_sha256":FileAccess.get_sha256("res://assets/models/lighthouse.glb")},"  "));file.close()
	print("NATIVE LIGHTHOUSE CHECK PASS 2 instances / 32 wall rays / material ownership / collision identity")
	quit()

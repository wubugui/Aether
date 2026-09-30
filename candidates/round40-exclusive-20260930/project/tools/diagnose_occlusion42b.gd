extends SceneTree
func _initialize() -> void:call_deferred('run')
func run() -> void:
	var game: Node3D=load('res://scenes/candidate42b/Game42b.tscn').instantiate()
	root.add_child(game);game.test_frozen=true;game.sound_enabled=false
	for i in range(15):await process_frame
	for id in ['1276','1344']:
		game.observe_reference(id)
		var origin: Vector3=game.camera.global_position
		var direction: Vector3=-game.camera.global_basis.z
		var hits: Array=[]
		for mesh in game.find_children('*','MeshInstance3D',true,false):
			if not mesh.is_visible_in_tree() or mesh.mesh==null:continue
			var inverse: Transform3D=mesh.global_transform.affine_inverse()
			var local_origin: Vector3=inverse*origin
			var local_direction: Vector3=inverse.basis*direction
			var box: AABB=mesh.get_aabb()
			if not box.has_point(local_origin) and box.intersects_segment(local_origin,local_origin+local_direction*60)==null:continue
			var faces: PackedVector3Array=mesh.mesh.get_faces()
			var nearest:=INF
			for i in range(0,faces.size(),3):
				var point: Variant=Geometry3D.ray_intersects_triangle(local_origin,local_direction,faces[i],faces[i+1],faces[i+2])
				if point!=null:nearest=minf(nearest,origin.distance_to(mesh.to_global(point)))
			if nearest<60:hits.append({'path':str(mesh.get_path()),'distance':nearest})
		print('OCCLUSION ',id,' ',JSON.stringify(hits))
	game.queue_free();for i in range(4):await process_frame
	quit()

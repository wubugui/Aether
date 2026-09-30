extends SceneTree
func _initialize() -> void: call_deferred('run')
func run() -> void:
	var game: Node3D = load('res://scenes/candidate42b/Game42b.tscn').instantiate()
	root.add_child(game);game.test_frozen=true;game.sound_enabled=false
	for i in range(15):await physics_frame
	var rows: Array = []
	for entry in game.scene_environment.plan:
		game.observe_reference(str(entry.ref))
		await physics_frame
		var ground: float = game.world.ground_height(game.camera.position)
		var sphere := SphereShape3D.new();sphere.radius=.3
		var query := PhysicsShapeQueryParameters3D.new();query.shape=sphere
		query.transform=Transform3D(Basis.IDENTITY,game.camera.global_position);query.collision_mask=5;query.exclude=[game.airship.get_rid()]
		var hits := game.get_world_3d().direct_space_state.intersect_shape(query)
		var names: Array = []
		for hit in hits:names.append(str(hit.collider.get_path()))
		rows.append({'ref':entry.ref,'camera':str(game.camera.global_position),'ground_height':ground,'height_above_ground':game.camera.position.y-ground,'colliders':names})
		print(entry.ref,' camera=',game.camera.position,' ground=',ground,' hits=',names)
	var file := FileAccess.open('res://../evidence/view-clearance42b.json',FileAccess.WRITE)
	if file == null:file=FileAccess.open('E:/FeiTing/candidates/round40-exclusive-20260930/evidence/view-clearance42b.json',FileAccess.WRITE)
	file.store_string(JSON.stringify(rows,'  '));file.close()
	game.queue_free();for i in range(4):await process_frame
	quit()

extends "res://tools/verify_cloud_lake49.gd"
## Pure unsaved-object logic test. No scene load/save, Sky, MultiMesh, runtime or
## visual acceptance. Safe under headless because it never produces an asset.
func _initialize() -> void:
	parse_arguments()
	call_deferred("test_logic")
func test_logic() -> void:
	if not load_payload(): quit(1);return
	var test_game := Node3D.new()
	test_game.name="Skyfarer"
	var world := Node3D.new()
	world.name="World"
	test_game.add_child(world);world.owner=test_game
	test_game.add_to_group("test_persistent",true)
	var packed := PackedScene.new()
	packed.pack(test_game)
	var before := graph_state(test_game,packed)
	check(add_islands(test_game),"Pure unsaved island assembly")
	check(verify_payload_result(test_game),"Pure unsaved geometry matches authoring payload")
	check(graph_state(test_game,packed)==before,"Pure additive graph preserves dummy baseline")
	var packed_after := PackedScene.new()
	packed_after.pack(test_game)
	check(graph_state(test_game,packed_after)==before,"Packed SceneState dot-slash new paths are masked precisely")
	world.add_to_group("must_detect_old_group_change",true)
	var packed_bad := PackedScene.new()
	packed_bad.pack(test_game)
	check(graph_state(test_game,packed_bad)!=before,"Old persistent group changes are still detected")
	world.remove_from_group("must_detect_old_group_change")
	var supports_ok := true
	for island in payload.islands:
		for entry in island.meshes:
			if str(entry.role).replace("_","")=="rockroot":
				var info := closed_root(world_faces(test_game.get_node(mesh_path(island.name,entry.name))))
				check(info.passed,"Unsaved closed clockwise root "+island.name,info)
				print(JSON.stringify(info))
		for tree in island.trees:
			var support := bvh_build(triangle_rows(world_faces(test_game.get_node(mesh_path(island.name,tree.support_mesh)))))
			var top := bvh_height(support,v3(tree.foot_world))
			var error := absf(top-float(tree.foot_world[1]))
			check(is_finite(top) and error<.2,"Pure support BVH height "+tree.name,{"error_m":error,"height":top})
	var passed := failures.is_empty() and supports_ok
	for row in checks: passed=passed and row.passed
	test_game.free()
	print("LAKE49 HEADLESS PURE LOGIC ONLY passed=",passed,"; NO NATIVE SCENE SAVED OR RENDER ACCEPTANCE")
	quit(0 if passed else 1)

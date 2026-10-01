extends "res://tools/build_lake_depth50.gd"
## Pure source-resource logic test; no scene instantiation or resource saves.
func _initialize() -> void: call_deferred("test_logic")
func test_logic() -> void:
	var packed: PackedScene=load(BASE)
	var state := packed.get_state()
	var source: ShaderMaterial
	for i in range(state.get_node_count()):
		if str(state.get_node_path(i)).trim_prefix("./")!="World/Ocean": continue
		for j in range(state.get_node_property_count(i)):
			if str(state.get_node_property_name(i,j))=="material_override": source=state.get_node_property_value(i,j)
	var before := digest(canonical(source))
	var copy := prepare_water(source)
	resource_cache.clear()
	var good := copy!=null and before==digest(canonical(source)) and failures.is_empty()
	var test_game := Node3D.new();test_game.name="Dummy50"
	var world := Node3D.new();world.name="World";test_game.add_child(world);world.owner=test_game
	var ocean := MeshInstance3D.new();ocean.name="Ocean";ocean.mesh=PlaneMesh.new();ocean.material_override=source;world.add_child(ocean);ocean.owner=test_game
	var other := MeshInstance3D.new();other.name="Other";other.mesh=PlaneMesh.new();other.material_override=source;world.add_child(other);other.owner=test_game
	var packed_dummy := PackedScene.new();packed_dummy.pack(test_game)
	var control := graph_state(test_game,packed_dummy)
	ocean.material_override=copy
	good=good and control==graph_state(test_game,packed_dummy)
	ocean.layers=262144
	good=good and control!=graph_state(test_game,packed_dummy)
	ocean.layers=1
	other.material_override=copy
	good=good and control!=graph_state(test_game,packed_dummy)
	other.material_override=source
	good=good and control==graph_state(test_game,packed_dummy)
	test_game.free()
	print("DEPTH50 PURE SOURCE LOGIC passed=",good," code_only_two_insertions=",ocean_ledger.get("stripped_source_exact",false)," old_uniforms=",ocean_ledger.get("old_uniforms",{}).size()," new_uniforms=",ocean_ledger.get("new_uniform_names",[])," NO_SCENE_OR_MM_SAVE")
	for i in range(3): await process_frame
	quit(0 if good else 1)

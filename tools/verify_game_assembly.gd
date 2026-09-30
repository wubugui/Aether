extends SceneTree
## Meaningful engine persistence test on a disposable copy, never on the user's
## authored World.tscn. Uses the same PackedScene save/load path as the editor.
var checks:Array=[]
func _initialize() -> void:call_deferred("run")
func check(ok:bool,label:String) -> void:
	checks.append({"passed":ok,"name":label});print("PASS " if ok else "FAIL ",label)
func own(node:Node,scene:Node) -> void:
	for child in node.get_children():
		child.owner=scene
		if child.scene_file_path.is_empty():own(child,scene)
func run() -> void:
	if DisplayServer.get_name()=="headless":
		push_error("Run persistence validation using the actual game rendering backend, without --headless.")
		quit(1);return
	var original_hash:=FileAccess.get_sha256("res://scenes/world/World.tscn")
	var text:=FileAccess.get_file_as_string("res://scenes/world/World.tscn")
	check(not text.contains("open_world.glb") and not text.contains('[sub_resource type="ArrayMesh"'),"World contains engine instances without embedded world geometry")
	var scene:PackedScene=load("res://scenes/world/World.tscn")
	var world:Node3D=scene.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	check(world.get_node("Terrain").get_child_count()==208,"208 independently reusable terrain scenes")
	var all_tiles:=true
	for tile in world.get_node("Terrain").get_children():
		all_tiles=all_tiles and tile.scene_file_path.begins_with("res://scenes/terrain/") and tile.has_node("Model") and tile.has_node("Collision/Shape")
	check(all_tiles,"Every terrain tile retains a model import and Godot collision resource")
	var houses:=world.get_node("Settlements").get_children().filter(func(n):return n.asset_kind=="cottage")
	var house:Node3D=houses[0];var house_path:=world.get_path_to(house)
	house.position+=Vector3(17,2,-9);var changed_house:=house.position
	var marker:Node3D=world.get_node("Ports/hearth");marker.position+=Vector3(11,3,-7);var changed_port:=marker.position
	var duplicate:Node3D=load("res://scenes/prefabs/cottage.tscn").instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	duplicate.name="QA_Independent_Cottage";duplicate.position=changed_house+Vector3(28,0,0)
	world.get_node("Settlements").add_child(duplicate)
	var grove:MultiMeshInstance3D
	for node in world.get_node("Vegetation").get_children():
		if node.position.x==0 and node.position.z==0 and node.get_meta("asset_kind")=="oak":grove=node;break
	assert(grove!=null)
	var grove_path:=world.get_path_to(grove)
	check(absf(grove.multimesh.get_instance_transform(0).basis.determinant())>.001,"Saved vegetation has nonzero physical scale")
	check(not grove.multimesh.get_instance_transform(0).origin.is_equal_approx(grove.multimesh.get_instance_transform(1).origin),"Saved vegetation retains distinct instance positions")
	grove.multimesh=preload("res://scripts/scatter_group.gd").copy_data(grove.multimesh)
	var transform:=grove.multimesh.get_instance_transform(0);transform.origin+=Vector3(4,0,6)
	grove.multimesh.set_instance_transform(0,transform);grove.position+=Vector3(8,0,-5)
	var expected_tree:=grove.transform*transform
	assert(ResourceSaver.save(grove.multimesh,"res://captures/assembly_test_grove.res")==OK)
	grove.multimesh=load("res://captures/assembly_test_grove.res")
	own(world,world);var packed:=PackedScene.new();assert(packed.pack(world)==OK)
	assert(ResourceSaver.save(packed,"res://captures/assembly_world_test.tscn")==OK)
	world.free()
	var reopened:Node3D=ResourceLoader.load("res://captures/assembly_world_test.tscn","PackedScene",ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	check(reopened.get_node(house_path).position.is_equal_approx(changed_house),"House move survives save and reopen")
	check(reopened.get_node("Ports/hearth").position.is_equal_approx(changed_port),"Dock marker move survives save and reopen")
	var copy:Node3D=reopened.get_node("Settlements/QA_Independent_Cottage")
	check(copy.scene_file_path=="res://scenes/prefabs/cottage.tscn" and copy.has_node("Collision/Shape"),"Copied prefab remains independent with its own collider")
	var reopened_grove:MultiMeshInstance3D=reopened.get_node(grove_path)
	var actual_tree:=reopened_grove.transform*reopened_grove.multimesh.get_instance_transform(0)
	check(actual_tree.is_equal_approx(expected_tree),"Saved MultiMesh instance and parent edits persist")
	root.add_child(reopened);reopened.set_process(false)
	await physics_frame;await physics_frame
	check(absf(reopened.ports[0].x-changed_port.x)<.001 and absf(reopened.ports[0].pad_y-changed_port.y)<.001,"Runtime reads edited port from scene rather than old layout JSON")
	reopened.update_focus(actual_tree.origin+Vector3.UP*20,true)
	await physics_frame;await physics_frame
	var found:=false
	for index in reopened.prop_colliders:
		var body:StaticBody3D=reopened.prop_colliders[index]
		if body.global_transform.is_equal_approx(actual_tree):found=true;break
	check(found,"Vegetation collision follows the saved MultiMesh transform")
	check(copy.get_node("Collision").global_position.is_equal_approx(copy.global_position),"Copied house collider follows the engine scene instance")
	check(reopened.get_node(house_path).position.is_equal_approx(changed_house),"Game startup preserves editor-authored house placement")
	check(FileAccess.get_sha256("res://scenes/world/World.tscn")==original_hash,"Persistence test leaves authored world unchanged")
	reopened.queue_free();await process_frame;await process_frame
	var passed:bool=checks.all(func(c):return c.passed)
	var report:=FileAccess.open("res://captures/game-assembly-validation.json",FileAccess.WRITE)
	report.store_string(JSON.stringify({"passed":passed,"checks":checks,"world_sha256":original_hash},"\t"))
	print("ASSEMBLY VALIDATION ",passed)
	quit(0 if passed else 1)

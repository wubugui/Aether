@tool
extends EditorPlugin
var panel:VBoxContainer
var busy:=false
var checks:Array=[]
var request_clock:=0.0

func _process(delta:float) -> void:
	request_clock+=delta
	if request_clock<.5 or busy:return
	request_clock=0
	var request:="res://captures/request_editor_validation.flag"
	if FileAccess.file_exists(request):
		DirAccess.remove_absolute(request)
		call_deferred("validate_editor")

func _enter_tree() -> void:
	get_tree().set_meta("skyfarer_editor_tools",self)
	panel=VBoxContainer.new();panel.name="Skyfarer"
	var title:=Label.new();title.text="Native game scenes";panel.add_child(title)
	for entry in [["Open World",func():EditorInterface.open_scene_from_path("res://scenes/world/World.tscn")],["Open Airship",func():EditorInterface.open_scene_from_path("res://scenes/prefabs/Airship.tscn")],["Validate editor workflow",validate_editor]]:
		var button:=Button.new();button.text=entry[0];button.pressed.connect(entry[1]);panel.add_child(button)
	add_control_to_dock(DOCK_SLOT_RIGHT_UL,panel)
	if "--editor-assembly-test" in OS.get_cmdline_user_args():call_deferred("validate_editor")

func _exit_tree() -> void:
	get_tree().remove_meta("skyfarer_editor_tools")
	if panel:remove_control_from_docks(panel);panel.queue_free()

func apply_scatter(node:MultiMeshInstance3D,data:MultiMesh) -> void:
	var undo:=get_undo_redo();undo.create_action("Edit scatter instance",UndoRedo.MERGE_DISABLE,node.owner)
	undo.add_do_property(node,"multimesh",data);undo.add_undo_property(node,"multimesh",node.multimesh)
	undo.commit_action();EditorInterface.mark_scene_as_unsaved()

func extract_scatter(node:MultiMeshInstance3D,data:MultiMesh,instance:Node3D,destination:Node3D,transform:Transform3D) -> void:
	var undo:=get_undo_redo();undo.create_action("Extract editable prefab",UndoRedo.MERGE_DISABLE,node.owner)
	undo.add_do_method(destination,"add_child",instance,true)
	undo.add_do_property(instance,"owner",node.owner);undo.add_do_property(instance,"global_transform",transform)
	undo.add_do_property(node,"multimesh",data);undo.add_undo_property(node,"multimesh",node.multimesh)
	undo.add_undo_method(destination,"remove_child",instance);undo.add_do_reference(instance)
	undo.commit_action();EditorInterface.mark_scene_as_unsaved()
	# The Inspector owns the button that invoked this action. Rebuild it only
	# after that button has finished emitting its pressed signal.
	call_deferred("focus_prefab",instance)

func focus_prefab(instance:Node) -> void:
	if not is_instance_valid(instance):return
	EditorInterface.get_selection().clear();EditorInterface.get_selection().add_node(instance);EditorInterface.inspect_object(instance)

func check(ok:bool,label:String) -> void:
	checks.append({"passed":ok,"name":label});print("EDITOR PASS " if ok else "EDITOR FAIL ",label)

func pause_frames(count:int) -> void:
	for i in range(count):await get_tree().process_frame

func inspector_button(label:String) -> Button:
	for button in EditorInterface.get_inspector().find_children("*","Button",true,false):
		if button.text==label:return button
	return null

func validate_editor() -> void:
	if busy:return
	busy=true;checks=[]
	var deadline:=Time.get_ticks_msec()+60000
	while EditorInterface.get_resource_filesystem().is_scanning() and Time.get_ticks_msec()<deadline:await pause_frames(1)
	await get_tree().create_timer(2.0).timeout
	var original:="res://scenes/world/World.tscn";var scratch:="res://captures/editor_layout_test.tscn"
	var original_hash:=FileAccess.get_sha256(original)
	check(DirAccess.copy_absolute(original,scratch)==OK,"Create disposable copy without editing authored world")
	EditorInterface.get_resource_filesystem().update_file(scratch)
	EditorInterface.open_scene_from_path(scratch)
	deadline=Time.get_ticks_msec()+60000
	while Time.get_ticks_msec()<deadline:
		var current:=EditorInterface.get_edited_scene_root()
		if current and current.scene_file_path==scratch:break
		await pause_frames(1)
	var world:=EditorInterface.get_edited_scene_root()
	if not world or world.scene_file_path!=scratch:
		check(false,"Editor opens disposable world scene");finish(original_hash);return
	check(world.get_node("Terrain").get_child_count()==208,"Actual editor scene tree exposes 208 terrain instances")
	var houses:=world.get_node("Settlements").get_children().filter(func(n):return n.asset_kind=="cottage")
	var house:Node3D=houses[0];var house_path:=world.get_path_to(house)
	EditorInterface.get_selection().clear();EditorInterface.get_selection().add_node(house);EditorInterface.inspect_object(house)
	await pause_frames(8)
	check(EditorInterface.get_inspector().get_edited_object()==house and house in EditorInterface.get_selection().get_selected_nodes(),"Local scene tree selection and Inspector show the house instance")
	var desired:=house.position+Vector3(7,1,-4)
	var undo:=get_undo_redo();undo.create_action("QA move house",UndoRedo.MERGE_DISABLE,world)
	undo.add_do_property(house,"position",desired);undo.add_undo_property(house,"position",house.position);undo.commit_action()
	EditorInterface.mark_scene_as_unsaved()
	var grove:MultiMeshInstance3D
	for node in world.get_node("Vegetation").get_children():
		if node.position.x==0 and node.position.z==0 and node.get_meta("asset_kind")=="oak":grove=node;break
	var grove_path:=world.get_path_to(grove);grove.selected_instance=0
	EditorInterface.get_selection().clear();EditorInterface.get_selection().add_node(grove);EditorInterface.inspect_object(grove)
	await pause_frames(15)
	var read:=inspector_button("Read selected instance");var apply:=inspector_button("Apply selected transform")
	check(read!=null and apply!=null,"Scatter actions are real Inspector buttons")
	var edited_tree:Transform3D=grove.multimesh.get_instance_transform(0)
	edited_tree.origin+=Vector3(3,0,-2)
	if read and apply:
		read.pressed.emit();grove.selected_transform=edited_tree;apply.pressed.emit()
		check(grove.multimesh.get_instance_transform(0).is_equal_approx(edited_tree),"Inspector Apply button edits the selected instance through UndoRedo")
	var expected_count:int=grove.multimesh.instance_count
	var extract:=inspector_button("Extract to editable prefab")
	check(extract!=null,"Extract prefab action is exposed in Inspector")
	var extracted_name:=""
	if extract:
		grove.selected_instance=1
		extract.pressed.emit();await pause_frames(3)
		var selected:Array[Node]=EditorInterface.get_selection().get_selected_nodes()
		if selected.size()==1:extracted_name=selected[0].name
		check(grove.multimesh.instance_count==expected_count-1 and selected.size()==1 and selected[0].has_node("Collision/Shape"),"Inspector Extract button creates an independently editable prefab and removes its scattered copy")
	check(EditorInterface.save_scene()==OK,"Actual editor Save Scene succeeds")
	await pause_frames(4)
	EditorInterface.get_base_control().get_viewport().get_texture().get_image().save_png("res://captures/editor-assembly-inspector.png")
	# Reimport the individual cottage model through the editor's real importer.
	var fs:=EditorInterface.get_resource_filesystem();var imported:=[false]
	var callback:=func(_paths):imported[0]=true
	fs.resources_reimported.connect(callback,CONNECT_ONE_SHOT)
	fs.reimport_files(PackedStringArray(["res://assets/models/cottage.glb"]))
	deadline=Time.get_ticks_msec()+60000
	while not imported[0] and Time.get_ticks_msec()<deadline:await pause_frames(1)
	check(imported[0],"Godot editor reimports the independent Blender cottage model")
	EditorInterface.reload_scene_from_path(scratch);await pause_frames(30)
	world=EditorInterface.get_edited_scene_root()
	check(world.get_node(house_path).position.is_equal_approx(desired),"House transform survives editor save, GLB reimport and scene reload")
	grove=world.get_node(grove_path)
	check(grove.multimesh.get_instance_transform(0).is_equal_approx(edited_tree) and grove.multimesh.instance_count==expected_count-1,"Inspector scatter edits survive editor save and reload")
	check(not extracted_name.is_empty() and world.has_node("Settlements/"+extracted_name),"Extracted prefab survives save and reload")
	check(FileAccess.get_sha256(original)==original_hash,"Editor QA and model reimport leave the authored world untouched")
	finish(original_hash)
	EditorInterface.open_scene_from_path("res://scenes/game.tscn")

func finish(original_hash:String) -> void:
	var passed:bool=checks.all(func(c):return c.passed)
	var file:=FileAccess.open("res://captures/editor-assembly-validation.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":passed,"checks":checks,"world_sha256":original_hash},"\t"))
	print("ACTUAL EDITOR VALIDATION ",passed);busy=false
	if "--editor-qa-exit" in OS.get_cmdline_user_args():get_tree().quit(0 if passed else 1)

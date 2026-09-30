@tool
extends MultiMeshInstance3D
## Editor-facing scatter resource. Explicit copies avoid MultiMesh.duplicate()
## applying its buffer before allocating the new instance count in Godot 4.5.
@export var model_scene:PackedScene
@export var selected_instance:int=0
@export var selected_transform:=Transform3D.IDENTITY
@export_tool_button("Read selected instance") var read_button=read_selected
@export_tool_button("Apply selected transform") var apply_button=apply_selected
@export_tool_button("Extract to editable prefab") var extract_button=extract_selected

static func copy_data(source:MultiMesh,omit:=-1) -> MultiMesh:
	var copy:=MultiMesh.new();copy.transform_format=source.transform_format
	copy.use_colors=source.use_colors;copy.use_custom_data=source.use_custom_data;copy.mesh=source.mesh
	copy.instance_count=source.instance_count-(1 if omit>=0 else 0)
	var target:=0
	for i in range(source.instance_count):
		if i==omit:continue
		copy.set_instance_transform(target,source.get_instance_transform(i))
		if source.use_colors:copy.set_instance_color(target,source.get_instance_color(i))
		if source.use_custom_data:copy.set_instance_custom_data(target,source.get_instance_custom_data(i))
		target+=1
	return copy

func valid_selection() -> bool:return multimesh and selected_instance>=0 and selected_instance<multimesh.instance_count
func read_selected() -> void:
	if valid_selection():selected_transform=multimesh.get_instance_transform(selected_instance)
func apply_selected() -> void:
	if not valid_selection():return
	var data:=copy_data(multimesh)
	data.set_instance_transform(selected_instance,selected_transform)
	if Engine.is_editor_hint() and get_tree().has_meta("skyfarer_editor_tools"):
		get_tree().get_meta("skyfarer_editor_tools").apply_scatter(self,data)
	else:multimesh=data
	multimesh.emit_changed();update_gizmos()
func extract_selected() -> void:
	if not valid_selection() or not model_scene or not owner:return
	var destination:=owner.get_node_or_null("Settlements")
	if not destination:return
	var instance:Node3D=model_scene.instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE)
	var transform:=global_transform*multimesh.get_instance_transform(selected_instance)
	var data:=copy_data(multimesh,selected_instance)
	if Engine.is_editor_hint() and get_tree().has_meta("skyfarer_editor_tools"):
		get_tree().get_meta("skyfarer_editor_tools").extract_scatter(self,data,instance,destination,transform)
		return
	destination.add_child(instance,true);instance.owner=owner
	instance.global_transform=transform
	multimesh=data;multimesh.emit_changed();update_gizmos()

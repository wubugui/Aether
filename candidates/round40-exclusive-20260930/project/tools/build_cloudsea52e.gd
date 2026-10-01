extends SceneTree
## Build off-tree with the real renderer, preserving all original scene ownership.
const BASE := "res://scenes/candidate51b/Game51b.tscn"
const BASE_SHA := "b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1"
const DEST := "res://scenes/candidate52e/"
const TARGET := DEST+"Game52e.tscn"
const ASSETS := "res://assets/clouds52e/"
const SOURCE := "/workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52e/"
const Audit=preload("res://tools/cloudsea52e_audit.gd")
var audit := Audit.new()
var game: Node3D
var reloaded: Node3D
var sources: Array[Node3D]=[]
var output := ""
var report := {"build_saved_reload_passed":false,"visual_acceptance":false,"hardware_gpu_acceptance":false,"failures":[],"inventory":[],"source_assets":[]}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--report-dir="):output=arg.trim_prefix("--report-dir=")
	call_deferred("build")
func settle() -> void:
	for i in range(3):await process_frame
	await RenderingServer.frame_post_draw
func require(ok: bool,message: String,details: Variant=null) -> bool:
	if not ok:report.failures.append({"error":message,"details":details});push_error(message)
	return ok
func finish(ok: bool) -> void:
	report.build_saved_reload_passed=ok
	report.renderer=RenderingServer.get_video_adapter_name()
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("build-report-52e.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	if ok:
		var file:=FileAccess.open(DEST+"build-report-52e.json",FileAccess.WRITE)
		file.store_string(JSON.stringify(report,"  "));file.close()
	if DisplayServer.get_name()!="headless":await settle()
	for node in sources:
		if is_instance_valid(node):node.free()
	if is_instance_valid(game):game.free()
	if is_instance_valid(reloaded):reloaded.free()
	for i in range(8):await process_frame
	print("CLOUDSEA52E BUILD_SAVED_RELOAD ",ok)
	quit(0 if ok else 1)
func build() -> void:
	if not require(DisplayServer.get_name()!="headless","52e requires real renderer; never headless-save full MM scene"):quit(2);return
	if not require(output.is_absolute_path() and DirAccess.dir_exists_absolute(output),"Existing absolute report directory required"):await finish(false);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and not FileAccess.file_exists(TARGET),"Immutable51b mismatch or52e already exists; refuse overwrite"):await finish(false);return
	var source_manifest_path:="/workspace/scratch/a29d03198654/Aether/cloud-evidence/cloudsea52e-integration-preparation/integration-manifest.json"
	if not require(FileAccess.file_exists(source_manifest_path),"Validated52e integration-manifest missing"):await finish(false);return
	var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(source_manifest_path))
	if not require(manifest.get("source_verified",false) and manifest.get("variants",[]).size()==3,"Source validation gate failed"):await finish(false);return
	report.baseline=BASE;report.baseline_sha256=BASE_SHA
	report.project_default_sha256=FileAccess.get_sha256("res://project.godot")
	report.source_manifest_sha256=FileAccess.get_sha256(source_manifest_path)
	for evidence in manifest.source_evidence:
		if not require(FileAccess.get_sha256(SOURCE+evidence.filename)==evidence.sha256,"Immutable source verification evidence changed",evidence.filename):await finish(false);return
	var packed_base: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	game=packed_base.instantiate();await settle()
	var full_before:=audit.full_snapshot(game)
	var weather:=audit.weather_state(game)
	if not require(weather.Rain.valid and weather.Snow.valid,"Original weather buffers invalid"):await finish(false);return
	var bindings:=audit.material_bindings(game)
	var region:Node3D=game.get_node("SkyRegion39")
	var expression:=RegEx.new();expression.compile("^cloud_sea_46_([012])_continuous_crown$")
	var root_nodes:=[]
	for node in region.get_children():
		if not str(node.name).begins_with("CloudSea_"):continue
		var children:=node.get_children()
		if not require(children.size()==1 and children[0] is MeshInstance3D,"Expected one actual46 mesh per51b root",str(node.name)):await finish(false);return
		var old:MeshInstance3D=children[0]
		var matched:=expression.search(str(old.name))
		if not require(matched!=null and old.get_child_count()==0 and old.get_script()==null and old.get_groups().is_empty(),"Unexpected original cloud payload",str(old.name)):await finish(false);return
		var material:Material=old.get_active_material(0)
		if not require(material!=null and old.mesh.get_surface_count()==1,"Missing original active sea material"):await finish(false);return
		var variant:=int(matched.get_string(1))
		var row:={"root":str(game.get_path_to(node)),"variant":variant,"root_transform":audit.transform_values(node.transform),"removed_path":str(game.get_path_to(old)),"old_node_flags":audit.mesh_flags(old),"material_class":material.get_class(),"material_fingerprint":audit.canonical(material),"material_original_path":material.resource_path,"new_meshes":[]}
		root_nodes.append(node);report.inventory.append(row);audit.excluded_paths[row.removed_path]=true
		for part in ["main_ridge","offset_shoulder","low_tail"]:audit.excluded_paths[row.root+"/CloudSea52e_v%d_%s" % [variant,part]]=true
	if not require(root_nodes.size()==25,"Expected exactly25 CloudSea roots"):await finish(false);return
	var before:=audit.graph_state(game,packed_base)
	if not require(before==audit.graph_state(game,packed_base),"Unmodified native graph double snapshot drift"):await finish(false);return
	DirAccess.make_dir_recursive_absolute(ASSETS)
	for variant in range(3):
		var spec:Dictionary=manifest.variants[variant]
		var name:="cloud_sea_52e_%d.glb" % variant
		var src:=SOURCE+name;var dst:=ASSETS+name
		if not require(spec.variant==variant and spec.filename==name and FileAccess.get_sha256(src)==spec.sha256,"52e immutable source hash/variant mismatch",src):await finish(false);return
		if not require(not FileAccess.file_exists(dst),"Refuse overwrite source asset copy",dst):await finish(false);return
		if not require(DirAccess.copy_absolute(src,ProjectSettings.globalize_path(dst))==OK and FileAccess.get_sha256(dst)==spec.sha256,"Exact GLB copy failed",dst):await finish(false);return
		var doc:=GLTFDocument.new();var state:=GLTFState.new()
		if not require(doc.append_from_file(dst,state)==OK,"GLB parse failed",dst):await finish(false);return
		var source:Node3D=doc.generate_scene(state)
		if not require(source!=null,"GLB scene failed",dst):await finish(false);return
		sources.append(source)
		var meshes:=source.find_children("*","MeshInstance3D",true,false)
		if not require(meshes.size()==3,"Source must contain3 real mesh nodes",dst):await finish(false);return
		var names:=[]
		for mesh in meshes:names.append(str(mesh.name))
		names.sort();var expected:Array=spec.mesh_names.duplicate();expected.sort()
		if not require(names==expected,"Actual GLB node names differ from verified manifest",names):await finish(false);return
		report.source_assets.append({"source":src,"copy":dst,"sha256":spec.sha256,"axis_mapping":manifest.axis_mapping,"actual_imported_nodes":names})
	for i in range(root_nodes.size()):
		var node:Node3D=root_nodes[i];var row:Dictionary=report.inventory[i]
		var old:MeshInstance3D=node.get_child(0);var owner_node:Node=old.owner
		var material:Material=old.get_active_material(0)
		var meshes:=sources[row.variant].find_children("*","MeshInstance3D",true,false)
		meshes.sort_custom(func(a:Node,b:Node)->bool:return str(a.name)<str(b.name))
		for source in meshes:
			var mesh:MeshInstance3D=old.duplicate(0)
			mesh.name=source.name;mesh.mesh=source.mesh;mesh.transform=audit.source_transform(source)
			mesh.material_override=material
			node.add_child(mesh);mesh.owner=owner_node;mesh.scene_file_path=""
			if not require(audit.mesh_flags(mesh)==row.old_node_flags,"Copied original node flags changed",str(mesh.name)):await finish(false);return
			audit.resource_cache.clear()
			row.new_meshes.append({"path":str(game.get_path_to(mesh)),"source_node":str(source.name),"transform":audit.transform_values(mesh.transform),"mesh_fingerprint":audit.canonical(mesh.mesh),"material_fingerprint":audit.canonical(mesh.get_active_material(0)),"node_flags":audit.mesh_flags(mesh)})
		node.remove_child(old);old.free()
	if not require(before==audit.graph_state(game,packed_base),"Unrelated graph changed before packing"):await finish(false);return
	if not require(bindings==audit.material_bindings(game),"Guard binding/controller paths changed"):await finish(false);return
	var packed:=PackedScene.new()
	if not require(packed.pack(game)==OK,"52e native pack failed"):await finish(false);return
	DirAccess.make_dir_recursive_absolute(DEST)
	if not require(ResourceSaver.save(packed,TARGET)==OK,"52e native save failed"):await finish(false);return
	var reload_packed:PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	reloaded=reload_packed.instantiate();await settle()
	if not require(before==audit.graph_state(reloaded,reload_packed),"Reload changed unrelated node/resource/owner/order/group/connection"):await finish(false);return
	if not require(weather==audit.weather_state(reloaded) and bindings==audit.material_bindings(reloaded),"Reload changed48000MM/guard/controller bindings"):await finish(false);return
	for row in report.inventory:
		var node:Node3D=reloaded.get_node(row.root)
		if not require(node.get_child_count()==3 and audit.transform_values(node.transform)==row.root_transform,"Root anchor/count changed",row.root):await finish(false);return
		for spec in row.new_meshes:
			var mesh:MeshInstance3D=reloaded.get_node(spec.path)
			audit.resource_cache.clear()
			if not require(audit.transform_values(mesh.transform)==spec.transform and audit.canonical(mesh.mesh)==spec.mesh_fingerprint and audit.canonical(mesh.get_active_material(0))==row.material_fingerprint and audit.mesh_flags(mesh)==spec.node_flags,"New mesh/source transform/material mismatch after reload",spec.path):await finish(false);return
	var changes:=audit.exact_changes(full_before,audit.full_snapshot(reloaded))
	if not require(changes.removed_nodes.size()==25 and changes.added_nodes.size()==75 and changes.changed_properties.is_empty(),"Unexpected actual scene changes",changes):await finish(false);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256("res://project.godot")==report.project_default_sha256,"Protected baseline/default changed"):await finish(false);return
	report.candidate=TARGET;report.candidate_sha256=FileAccess.get_sha256(TARGET)
	report.actual_changes=changes;report.unaffected_graph_fingerprint=audit.digest(before);report.weather=weather
	report.guard_binding_count=bindings.size()-1;report.controller_clipping_paths=bindings.controller_exact_clipping_paths
	report.scope="Only25 exact46 mesh child nodes replaced by75 actual52e GLB mesh children. All25 roots and every other stored property, resource semantic, ownership, sibling order, persistent group, connection, editable instance and48000 weather floats retained. Actual51b CloudSea StandardMaterial3D wrap materials preserved; CloudSea had zero51b guard bindings. Existing248 guarded fields and114 controller material paths remain exact. No controller, weather, terrain, defaults or old sources changed. Export transforms derive from actual imported node chains, not inferred bounds. Bounds never prove nonintersection."
	await finish(true)

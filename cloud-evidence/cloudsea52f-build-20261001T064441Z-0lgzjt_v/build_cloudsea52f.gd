extends SceneTree
## Additive source52f integration; real-renderer off-tree save only.
const BASE := "res://scenes/candidate52e/Game52e.tscn"
const BASE_SHA := "5abbabf7487766412592f0b93ccd12c01e7bbb70f28e96ffd829e7ae78919079"
const DEST := "res://scenes/candidate52f/"
const TARGET := DEST+"Game52f.tscn"
const ASSETS := "res://assets/clouds52f/"
const SOURCE := "/workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52f/variants/"
const MANIFEST := "/workspace/scratch/a29d03198654/Aether/cloud-evidence/cloudsea52f-integration-preparation/integration-manifest.json"
const Audit=preload("res://tools/cloudsea52e_audit.gd")
var audit:=Audit.new()
var game:Node3D
var sources:Array[Node3D]=[]
var output:=""
var report:={"build_saved_reload_passed":false,"visual_acceptance":false,"hardware_gpu_acceptance":false,"failures":[],"inventory":[],"source_assets":[]}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--report-dir="):output=arg.trim_prefix("--report-dir=")
	call_deferred("build")
func settle() -> void:
	for i in range(3):await process_frame
	await RenderingServer.frame_post_draw
func require(ok:bool,label:String,details:Variant=null) -> bool:
	if not ok:report.failures.append({"error":label,"details":details});push_error(label)
	return ok
func finish(ok:bool) -> void:
	report.build_saved_reload_passed=ok;report.renderer=RenderingServer.get_video_adapter_name()
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("build-report-52f.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	if ok:
		var file:=FileAccess.open(DEST+"build-report-52f.json",FileAccess.WRITE)
		file.store_string(JSON.stringify(report,"  "));file.close()
	if DisplayServer.get_name()!="headless":await settle()
	for source in sources:
		if is_instance_valid(source):source.free()
	if is_instance_valid(game):game.free()
	for i in range(8):await process_frame
	print("CLOUDSEA52F BUILD_SAVED_RELOAD ",ok);quit(0 if ok else 1)
func build() -> void:
	if not require(DisplayServer.get_name()!="headless","Real renderer required; no headless MM save"):quit(2);return
	if not require(output.is_absolute_path() and DirAccess.dir_exists_absolute(output),"Existing absolute report directory required"):await finish(false);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and not FileAccess.file_exists(TARGET),"Immutable52e mismatch or52f already saved; refuse overwrite"):await finish(false);return
	var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	if not require(manifest.source_verified and manifest.variants.size()==3,"Verified additive source manifest required"):await finish(false);return
	for evidence in manifest.source_evidence:
		if not require(FileAccess.get_sha256(SOURCE+evidence.filename)==evidence.sha256,"Source evidence changed",evidence.filename):await finish(false);return
	report.baseline=BASE;report.baseline_sha256=BASE_SHA;report.project_default_sha256=FileAccess.get_sha256("res://project.godot");report.source_manifest_sha256=FileAccess.get_sha256(MANIFEST)
	var packed_base:PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	game=packed_base.instantiate();await settle()
	var full_before:=audit.full_snapshot(game)
	var weather:=audit.weather_state(game);var bindings:=audit.material_bindings(game)
	if not require(weather.Rain.valid and weather.Snow.valid,"Original48000MM valid"):await finish(false);return
	var roots:=[];var counts:=[0,0,0]
	var expression:=RegEx.new();expression.compile("^CloudSea52e_v([012])_(low_tail|main_ridge|offset_shoulder)$")
	for node in game.get_node("SkyRegion39").get_children():
		if not str(node.name).begins_with("CloudSea_"):continue
		if not require(node.get_child_count()==3,"52e root must retain3 original meshes",str(node.name)):await finish(false);return
		var variant:=-1;var old_paths:=[];var material:Material
		for child in node.get_children():
			var found:=expression.search(str(child.name))
			if not require(child is MeshInstance3D and found!=null and child.get_child_count()==0 and child.get_script()==null,"Unexpected original52e payload",str(child.name)):await finish(false);return
			var value:=int(found.get_string(1))
			if not require(variant==-1 or variant==value,"Mixed original variant"):await finish(false);return
			variant=value;old_paths.append(str(game.get_path_to(child)))
			if material==null:material=child.get_active_material(0)
			if not require(material!=null and child.get_active_material(0)==material,"Root original material aliases differ"):await finish(false);return
		counts[variant]+=1;roots.append(node)
		var row:={"root":str(game.get_path_to(node)),"variant":variant,"root_transform":audit.transform_values(node.transform),"retained_old_paths":old_paths,"old_node_flags":audit.mesh_flags(node.get_child(0)),"material_fingerprint":audit.canonical(material),"material_class":material.get_class(),"new_meshes":[]}
		report.inventory.append(row)
		for suffix in ["low_drift","low_saddle"]:audit.excluded_paths[row.root+"/CloudSea52f_v%d_%s" % [variant,suffix]]=true
	if not require(roots.size()==25 and counts==[10,10,5],"Exact original25roots variant10/10/5",counts):await finish(false);return
	var before:=audit.graph_state(game,packed_base)
	if not require(before==audit.graph_state(game,packed_base),"Unmodified double graph snapshot stable"):await finish(false);return
	DirAccess.make_dir_recursive_absolute(ASSETS)
	for variant in range(3):
		var spec:Dictionary=manifest.variants[variant]
		var name:="cloud_sea_52f_additions_%d.glb" % variant;var src:=SOURCE+name;var dst:=ASSETS+name
		if not require(spec.variant==variant and spec.filename==name and FileAccess.get_sha256(src)==spec.sha256,"Exact additions source required",src):await finish(false);return
		if FileAccess.file_exists(dst):
			if not require(FileAccess.get_sha256(dst)==spec.sha256,"Existing independent copy differs; refuse overwrite",dst):await finish(false);return
		elif not require(DirAccess.copy_absolute(src,ProjectSettings.globalize_path(dst))==OK,"Copy additive GLB failed",dst):await finish(false);return
		if not require(FileAccess.get_sha256(dst)==spec.sha256,"Copied additive GLB hash differs",dst):await finish(false);return
		var doc:=GLTFDocument.new();var state:=GLTFState.new()
		if not require(doc.append_from_file(dst,state)==OK,"Parse additive GLB failed",dst):await finish(false);return
		var source:Node3D=doc.generate_scene(state)
		if not require(source!=null,"Generate additive native scene failed",dst):await finish(false);return
		sources.append(source)
		var meshes:=source.find_children("*","MeshInstance3D",true,false);var names:=[]
		for mesh in meshes:names.append(str(mesh.name))
		names.sort()
		if not require(names==spec.mesh_names and names.size()==2,"Exactly2 expected source meshes",names):await finish(false);return
		report.source_assets.append({"source":src,"copy":dst,"sha256":spec.sha256,"actual_meshes":names,"axis_mapping":manifest.axis_mapping})
	for i in range(roots.size()):
		var node:Node3D=roots[i];var row:Dictionary=report.inventory[i];var original:MeshInstance3D=node.get_child(0)
		var source_meshes:=sources[row.variant].find_children("*","MeshInstance3D",true,false)
		source_meshes.sort_custom(func(a:Node,b:Node)->bool:return str(a.name)<str(b.name))
		for source in source_meshes:
			var mesh:MeshInstance3D=original.duplicate(0)
			mesh.name=source.name;mesh.mesh=source.mesh;mesh.transform=audit.source_transform(source);mesh.material_override=original.get_active_material(0)
			node.add_child(mesh);mesh.owner=original.owner;mesh.scene_file_path=""
			if not require(audit.mesh_flags(mesh)==row.old_node_flags,"New render flags differ",str(mesh.name)):await finish(false);return
			audit.resource_cache.clear()
			row.new_meshes.append({"path":str(game.get_path_to(mesh)),"transform":audit.transform_values(mesh.transform),"mesh_fingerprint":audit.canonical(mesh.mesh),"material_fingerprint":audit.canonical(mesh.get_active_material(0)),"node_flags":audit.mesh_flags(mesh)})
	if not require(before==audit.graph_state(game,packed_base) and bindings==audit.material_bindings(game),"Old75clouds or unrelated graph/guard bindings changed"):await finish(false);return
	var packed:=PackedScene.new()
	if not require(packed.pack(game)==OK,"52f pack failed"):await finish(false);return
	DirAccess.make_dir_recursive_absolute(DEST)
	if not require(ResourceSaver.save(packed,TARGET)==OK,"52f save failed"):await finish(false);return
	# Release both PackedScene graphs, original tree and imported nodes before reload.
	await settle();game.free();game=null
	for source in sources:source.free()
	sources.clear();roots.clear();packed=null;packed_base=null;audit.resource_cache.clear()
	for i in range(8):await process_frame
	var reload_packed:PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	game=reload_packed.instantiate();await settle()
	if not require(before==audit.graph_state(game,reload_packed),"Reload changed old stored graph/ownership/groups/order/connections"):await finish(false);return
	if not require(weather==audit.weather_state(game) and bindings==audit.material_bindings(game),"Reload changed48000MM/248guard/114paths"):await finish(false);return
	for row in report.inventory:
		var node:Node3D=game.get_node(row.root)
		if not require(node.get_child_count()==5 and audit.transform_values(node.transform)==row.root_transform,"Exact5 children/root placement required",row.root):await finish(false);return
		var old:MeshInstance3D=game.get_node(row.retained_old_paths[0])
		for spec in row.new_meshes:
			var mesh:MeshInstance3D=game.get_node(spec.path);audit.resource_cache.clear()
			if not require(audit.canonical(mesh.mesh)==spec.mesh_fingerprint and audit.transform_values(mesh.transform)==spec.transform and audit.mesh_flags(mesh)==spec.node_flags and mesh.get_active_material(0)==old.get_active_material(0),"New52f source/transform/flags/material alias changed",spec.path):await finish(false);return
	var changes:=audit.exact_changes(full_before,audit.full_snapshot(game))
	if not require(changes.removed_nodes.is_empty() and changes.changed_properties.is_empty() and changes.added_nodes.size()==50,"Expected exactly50 adds, no removal/common property changes",changes):await finish(false);return
	if not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256("res://project.godot")==report.project_default_sha256,"Protected52e/default changed"):await finish(false);return
	report.candidate=TARGET;report.candidate_sha256=FileAccess.get_sha256(TARGET);report.actual_changes=changes;report.unaffected_graph_fingerprint=audit.digest(before)
	report.weather=weather;report.variant_counts=counts;report.guard_binding_count=bindings.size()-1;report.controller_clipping_paths=bindings.controller_exact_clipping_paths
	report.scope="Only50 additive52f low meshes at25 unchanged52e roots; all75 existing crown nodes/meshes/materials/paths and every unrelated stored property,ownership,order,group,connection,editable-instance and48000MM floats exact.248 guarded fields and114 ordered paths unchanged. Native source transforms derive from actual GLB ancestors. Real-renderer off-tree save, resource graphs released before reload. Low undersides extend to~476m worldY; coverage diagnostics and covering island roots are not visual/flight success."
	await finish(true)

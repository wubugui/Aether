extends SceneTree
## Independent native audit with sequential scene lifetimes; no scene saves/_ready.
const BASE:="res://scenes/candidate52e/Game52e.tscn"
const BASE_SHA:="5abbabf7487766412592f0b93ccd12c01e7bbb70f28e96ffd829e7ae78919079"
const TARGET:="res://scenes/candidate52f/Game52f.tscn"
const REPORT:="res://scenes/candidate52f/build-report-52f.json"
const VERIFIED:="res://scenes/candidate52f/verified-saved-52f.json"
const Audit=preload("res://tools/cloudsea52e_audit.gd")
var audit:=Audit.new()
var checks:=[]
var failed:=false
var output:=""
var candidate_sha:=""
var saved_report_sha:=""
var graph_fingerprint:=""
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--report-dir="):output=arg.trim_prefix("--report-dir=")
	call_deferred("run")
func check(ok:bool,label:String,evidence:Variant=null) -> bool:
	checks.append({"passed":ok,"name":label,"evidence":evidence})
	if not ok:failed=true
	print("PASS " if ok else "FAIL ",label)
	return ok
func settle() -> void:
	for i in range(3):await process_frame
	await RenderingServer.frame_post_draw
func inspect(path:String,newer:bool) -> Dictionary:
	var packed:PackedScene=ResourceLoader.load(path,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var game:Node3D=packed.instantiate();await settle()
	var root_count:=0;var old_count:=0;var new_count:=0;var counts:=[0,0,0];var old_materials:={}
	var expression:=RegEx.new();expression.compile("^CloudSea52e_v([012])_(low_tail|main_ridge|offset_shoulder)$")
	for root_node in game.get_node("SkyRegion39").get_children():
		if not str(root_node.name).begins_with("CloudSea_"):continue
		root_count+=1
		var originals:=[];var variant:=-1
		for mesh in root_node.get_children():
			var match_result:=expression.search(str(mesh.name))
			if match_result==null:continue
			var v:=int(match_result.get_string(1))
			check(variant==-1 or variant==v,"Consistent original variant "+str(root_node.name));variant=v
			originals.append(mesh)
		if not check(originals.size()==3 and variant>=0,"Exactly3 untouched52e original meshes "+str(root_node.name)):continue
		counts[variant]+=1;old_count+=originals.size()
		var material:Material=originals[0].get_active_material(0);old_materials[material.get_instance_id()]=true
		for mesh in originals:check(mesh.get_active_material(0)==material,"Original three material aliases "+str(game.get_path_to(mesh)))
		for suffix in ["low_drift","low_saddle"]:
			var new_path:=str(game.get_path_to(root_node))+"/CloudSea52f_v%d_%s" % [variant,suffix]
			audit.excluded_paths[new_path]=true
			if not newer:continue
			var mesh:=game.get_node_or_null(new_path) as MeshInstance3D
			if not check(mesh!=null,"Expected real additive mesh "+new_path):continue
			new_count+=1
			check(mesh.mesh!=null and mesh.mesh.get_surface_count()==1 and mesh.get_active_material(0)==material,"New mesh shares exact original active material "+new_path)
			check(audit.mesh_flags(mesh)==audit.mesh_flags(originals[0]),"New mesh preserves original render flags "+new_path)
		check(root_node.get_child_count()==(5 if newer else 3),"Exact child count "+str(root_node.name))
	check(root_count==25 and old_count==75 and new_count==(50 if newer else 0) and counts==[10,10,5] and old_materials.size()==3,"Exact25roots/75old/50new/3materials and10-10-5 allocation",{"roots":root_count,"old":old_count,"new":new_count,"counts":counts,"materials":old_materials.size()})
	var graph:=audit.graph_state(game,packed)
	check(graph==audit.graph_state(game,packed),"Unmodified double snapshot stable "+path)
	var result:={"graph":graph,"full":audit.full_snapshot(game),"weather":audit.weather_state(game),"bindings":audit.material_bindings(game),"new_state":{}}
	if newer:
		for new_path in audit.excluded_paths:
			var mesh:=game.get_node_or_null(new_path) as MeshInstance3D
			if mesh==null:continue
			audit.resource_cache.clear()
			result.new_state[new_path]={"transform":audit.transform_values(mesh.transform),"mesh_fingerprint":audit.canonical(mesh.mesh),"material_fingerprint":audit.canonical(mesh.get_active_material(0)),"node_flags":audit.mesh_flags(mesh)}
	await settle();game.free();packed=null;audit.resource_cache.clear()
	for i in range(8):await process_frame
	return result
func finish() -> void:
	var report:={"saved_native_audit_passed":not failed,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":candidate_sha,"build_report_sha256":saved_report_sha,"unaffected_graph_fingerprint":graph_fingerprint,"checks":checks,"renderer":RenderingServer.get_video_adapter_name(),"sequential_scene_lifetimes":true,"visual_acceptance":false,"hardware_gpu_acceptance":false,"scope":"Fresh independent exact native52e-to52f graph audit; exact50additive paths rederived from retained52e mesh names, not builder whitelist. All75 old clouds/25roots/materials/owners/groups/connections/order/48000MM/248guard/114paths retained. Each off-tree scene and its PackedScene are freed before loading the next; no _ready, scene save or pixel acceptance."}
	for path in [output.path_join("native-audit-report.json"),VERIFIED if not failed else output.path_join("native-audit-failed.json")]:
		var file:=FileAccess.open(path,FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	print("CLOUDSEA52F FRESH_NATIVE_AUDIT ",not failed);quit(1 if failed else 0)
func run() -> void:
	if not check(DisplayServer.get_name()!="headless","Actual renderer for exact MM audit"):quit(2);return
	if not check(output.is_absolute_path() and DirAccess.dir_exists_absolute(output),"Existing report directory required"):quit(2);return
	if not check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.file_exists(TARGET),"Immutable52e and saved52f exist"):await finish();return
	candidate_sha=FileAccess.get_sha256(TARGET);saved_report_sha=FileAccess.get_sha256(REPORT)
	var build:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(REPORT))
	if not check(build.build_saved_reload_passed and build.baseline_sha256==BASE_SHA and build.candidate_sha256==candidate_sha,"Real-renderer build report matches exact candidate"):await finish();return
	var before:Dictionary=await inspect(BASE,false)
	var after:Dictionary=await inspect(TARGET,true)
	check(before.graph==after.graph,"All original stored properties/ownership/order/groups/connections/resources preserved")
	graph_fingerprint=audit.digest(before.graph)
	check(graph_fingerprint==build.unaffected_graph_fingerprint,"Independent retained graph fingerprint matches saved build")
	var changes:=audit.exact_changes(before.full,after.full)
	check(changes==build.actual_changes and changes.added_nodes.size()==50 and changes.removed_nodes.is_empty() and changes.changed_properties.is_empty(),"Exact50adds no removed or changed old nodes")
	check(before.weather==after.weather and before.weather.Rain.valid and before.weather.Snow.valid,"48000MM floats exact")
	check(before.bindings==after.bindings,"248 guarded fields and114 ordered controller material paths exact")
	for root_row in build.inventory:
		for spec in root_row.new_meshes:
			var expected:Dictionary=spec.duplicate(true);expected.erase("path")
			check(after.new_state.get(spec.path,{})==expected,"Exact source mesh/transform/material state "+spec.path)
	for asset in build.source_assets:check(FileAccess.get_sha256(asset.source)==asset.sha256 and FileAccess.get_sha256(asset.copy)==asset.sha256,"Actual additions source/copied GLB immutable "+asset.copy)
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(TARGET)==candidate_sha and FileAccess.get_sha256(REPORT)==saved_report_sha,"Native audit did not change scene/build files")
	before.clear();after.clear();audit.resource_cache.clear()
	await finish()

extends "res://tools/verify_cloudsea52f_saved.gd"
## V3 requires every typed component and raw-source check to return and finish.
var component_proof:=[]
var source_proof:=[]
var component_function_returned:=false
var source_function_returned:=false
var expected_component_paths:=[]
var expected_flag_count:=0
var recorded_flag_count:=0
var completed_component_paths:={}
var proof_path:=""
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
	var result:={"graph":graph,"full":audit.full_snapshot(game),"weather":audit.weather_state(game),"bindings":audit.material_bindings(game),"new_state":{},"native_geometry":{}}
	if newer:
		for new_path in audit.excluded_paths:
			var mesh:=game.get_node_or_null(new_path) as MeshInstance3D
			if mesh==null:continue
			audit.resource_cache.clear()
			result.new_state[new_path]={"transform":audit.transform_values(mesh.transform),"mesh_fingerprint":audit.canonical(mesh.mesh),"material_fingerprint":audit.canonical(mesh.get_active_material(0)),"node_flags":audit.mesh_flags(mesh)}
			if not result.native_geometry.has(str(mesh.name)):result.native_geometry[str(mesh.name)]=geometry_state(mesh.mesh)
	await settle();game.free();packed=null;audit.resource_cache.clear()
	for i in range(8):await process_frame
	return result
func geometry_state(mesh:Mesh) -> Dictionary:
	audit.resource_cache.clear()
	var surfaces:=[]
	for i in range(mesh.get_surface_count()):
		var arrays:Array=mesh.surface_get_arrays(i)
		var counts:=[]
		for array in arrays:counts.append(array.size() if array!=null else -1)
		surfaces.append({"all_native_arrays_sha256":audit.digest(arrays),"array_slot_counts":counts,"surface_material_fingerprint":audit.canonical(mesh.surface_get_material(i))})
	return {"full_native_resource_fingerprint":audit.canonical(mesh),"resource_flags":audit.resource_except(mesh,["_surfaces"]),"surfaces":surfaces}
func compare_components(before:Dictionary,after:Dictionary,build:Dictionary) -> bool:
	for root_row in build.inventory:
		var original_path:String=root_row.retained_old_paths[0]
		var original:Dictionary=before.full[original_path]
		for spec in root_row.new_meshes:
			var actual:Dictionary=after.new_state.get(spec.path,{})
			if not check(not actual.is_empty(),"Additive native state exists "+spec.path):continue
			var flags:Dictionary=actual.node_flags;var flag_rows:=[];var native_flags_exact:=true
			for key in flags:
				var native_equal:bool=original.has(key) and typeof(flags[key])==typeof(original[key]) and flags[key]==original[key]
				native_flags_exact=native_flags_exact and native_equal
				var reported:Variant=spec.node_flags.get(key)
				var compatible:bool=typeof(flags[key])==typeof(reported)
				flag_rows.append({"property":key,"native_type":type_string(typeof(flags[key])),"original52e_native_type":type_string(typeof(original.get(key))),"report_json_type":type_string(typeof(reported)),"native_vs_original_exact":native_equal,"native_vs_json_same_type":compatible,"native_vs_json_typed_equal":flags[key]==reported if compatible else false,"native_json_encoding":JSON.stringify(flags[key]),"report_json_encoding":JSON.stringify(reported)})
			var roundtrip:Variant=JSON.parse_string(JSON.stringify(flags))
			var proof:={"path":spec.path,"mesh_fingerprint_exact":actual.mesh_fingerprint==spec.mesh_fingerprint,"material_fingerprint_exact":actual.material_fingerprint==spec.material_fingerprint,"transform_exact":actual.transform==spec.transform,"all_flags_native_vs52e_exact":native_flags_exact,"all_flags_json_transport_exact":roundtrip==spec.node_flags,"old_v1_direct_dictionary_equal":actual==spec,"flags":flag_rows}
			# Old check removed path before dictionary equality. Reproduce exactly.
			var prior_expected:Dictionary=spec.duplicate(true);prior_expected.erase("path")
			proof.old_v1_direct_dictionary_equal=actual==prior_expected
			component_proof.append(proof)
			recorded_flag_count+=flag_rows.size()
			completed_component_paths[spec.path]=true
			check(proof.mesh_fingerprint_exact,"Exact stored source mesh fingerprint "+spec.path)
			check(proof.material_fingerprint_exact,"Exact stored original material fingerprint "+spec.path)
			check(proof.transform_exact,"Exact stored source transform "+spec.path)
			check(native_flags_exact,"Every render flag native-equals immutable52e original "+spec.path)
			check(proof.all_flags_json_transport_exact,"Prior report flags are exact JSON encoding of native flags "+spec.path)
	component_function_returned=true
	return component_proof.size()==50 and completed_component_paths.size()==50 and recorded_flag_count==expected_flag_count
func compare_actual_glbs(after:Dictionary,build:Dictionary) -> bool:
	var source_count:=0
	for asset in build.source_assets:
		if not check(FileAccess.get_sha256(asset.source)==asset.sha256 and FileAccess.get_sha256(asset.copy)==asset.sha256,"Real additions source/copy byte hashes exact "+asset.copy):continue
		var doc:=GLTFDocument.new();var state:=GLTFState.new()
		if not check(doc.append_from_file(asset.copy,state)==OK,"Fresh rawGLB parse "+asset.copy):continue
		var node:Node3D=doc.generate_scene(state)
		if not check(node!=null,"Fresh rawGLB native scene "+asset.copy):continue
		var meshes:=node.find_children("*","MeshInstance3D",true,false)
		check(meshes.size()==2,"Raw additionsGLB contains exactly2 meshes "+asset.copy)
		for mesh in meshes:
			var name:String=str(mesh.name);var actual:=geometry_state(mesh.mesh);var saved:Dictionary=after.native_geometry.get(name,{})
			var source_transform:=audit.transform_values(audit.source_transform(mesh));var all_placements:=true;var placements:=0
			for path in after.new_state:
				if str(path).get_file()==name:all_placements=all_placements and after.new_state[path].transform==source_transform;placements+=1
			var source_rows:=[]
			for i in range(actual.surfaces.size()):
				var saved_surface:Dictionary=saved.get("surfaces",[])[i] if i<saved.get("surfaces",[]).size() else {}
				source_rows.append({"surface":i,"all_array_bytes_exact":actual.surfaces[i].all_native_arrays_sha256==saved_surface.get("all_native_arrays_sha256"),"array_counts_exact":actual.surfaces[i].array_slot_counts==saved_surface.get("array_slot_counts"),"surface_material_exact":actual.surfaces[i].surface_material_fingerprint==saved_surface.get("surface_material_fingerprint")})
			var row:={"source":asset.copy,"node":name,"actual_source_native":actual,"saved_native":saved,"full_resource_exact":actual==saved,"native_source_transform":source_transform,"placement_count":placements,"all_placement_transforms_exact":all_placements,"surfaces":source_rows}
			source_proof.append(row);source_count+=1
			check(actual==saved,"Actual rawGLB full native geometry/arrays/resource flags exact "+name,row)
			check(all_placements and placements in [5,10],"All saved placement transforms equal actual imported source "+name)
		await settle();node.free();doc=null;state=null;audit.resource_cache.clear()
	source_function_returned=true
	return check(source_count==6 and source_proof.size()==6,"All6 actual source meshes independently verified")
func finish() -> void:
	var complete:=component_function_returned and source_function_returned and component_proof.size()==50 and completed_component_paths.size()==50 and expected_component_paths.size()==50 and recorded_flag_count==expected_flag_count and expected_flag_count>0 and source_proof.size()==6
	check(complete,"V3 all50 components/all flags/6 sources and both functions completed",{"component_function_returned":component_function_returned,"source_function_returned":source_function_returned,"expected_component_count":expected_component_paths.size(),"recorded_component_count":component_proof.size(),"unique_completed_paths":completed_component_paths.size(),"expected_flags":expected_flag_count,"recorded_flags":recorded_flag_count,"source_count":source_proof.size()})
	proof_path=output.path_join("component-and-raw-glb-proof-v3.json")
	var proof:={"audit_version":"v3","component_function_returned":component_function_returned,"source_function_returned":source_function_returned,"expected_component_count":expected_component_paths.size(),"component_count":component_proof.size(),"expected_flag_count":expected_flag_count,"recorded_flag_count":recorded_flag_count,"source_count":source_proof.size(),"complete":complete,"components":component_proof,"actual_glb_comparisons":source_proof,"geometry_tolerance_added":false,"full_native_geometry_equality_required":true,"passed":not failed and complete,"candidate_sha256":candidate_sha}
	var file:=FileAccess.open(proof_path,FileAccess.WRITE)
	if file!=null:file.store_string(JSON.stringify(proof,"  "));file.close()
	check(FileAccess.file_exists(proof_path),"V3 component/rawsource proof saved")
	var report:={"audit_version":"v3","saved_native_audit_passed":not failed and complete,"runner_log_gate_passed":false,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":candidate_sha,"build_report_sha256":saved_report_sha,"unaffected_graph_fingerprint":graph_fingerprint,"component_count":component_proof.size(),"expected_component_count":expected_component_paths.size(),"expected_flag_count":expected_flag_count,"recorded_flag_count":recorded_flag_count,"source_count":source_proof.size(),"both_comparison_functions_returned":component_function_returned and source_function_returned,"complete":complete,"proof_path":proof_path,"proof_sha256":FileAccess.get_sha256(proof_path),"checks":checks,"renderer":RenderingServer.get_video_adapter_name(),"visual_acceptance":false,"hardware_gpu_acceptance":false,"scope":"Exact native graph and50 additive states; every nativeflag compares to actual52e. LossyJSON transport audited separately.6 fresh realGLB meshes/arrays/flags/materials and50 transforms require exact equality. Godot only writes this pending result; external runner may issue the observation gate after process0, immutable inputs and noSCRIPT ERROR/ERROR/leaks. V1/v2 failed runs remain failed."}
	file=FileAccess.open(output.path_join("native-audit-report.json"),FileAccess.WRITE)
	if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	print("CLOUDSEA52F V3_PENDING_EXTERNAL_LOG_GATE ",not failed and complete)
	quit(1 if failed or not complete else 0)
func run() -> void:
	if not check(DisplayServer.get_name()!="headless","Actual renderer for exact MM/nativeGLB audit"):quit(2);return
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
			expected_component_paths.append(spec.path)
			expected_flag_count+=spec.node_flags.size()
	check(expected_component_paths.size()==50 and after.new_state.size()==50,"Exactly50 component paths before comparison")
	var components_result:Variant=compare_components(before,after,build)
	check(typeof(components_result)==TYPE_BOOL and components_result==true and component_function_returned,"Component comparison explicitly returned complete")
	before.clear();after.erase("full");after.erase("graph");after.erase("weather");after.erase("bindings");audit.resource_cache.clear()
	var sources_result:Variant=await compare_actual_glbs(after,build)
	check(typeof(sources_result)==TYPE_BOOL and sources_result==true and source_function_returned,"RawGLB comparison explicitly returned complete")
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(TARGET)==candidate_sha and FileAccess.get_sha256(REPORT)==saved_report_sha,"V2 did not alter saved scenes/build report")
	after.clear();audit.resource_cache.clear();await finish()

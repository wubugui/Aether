extends "res://tools/observe_cloudsea52f.gd"
## Runtime-only A0 / rebound-original A / D / exact-restored A2. One unchanged full world.
const LAB_ROOT := "/workspace/scratch/a29d03198654/Aether"
const LAB_DIR := LAB_ROOT+"/source-assets/cloud-sea52h-runtime-d/"
const LAB_SCENE := "res://scenes/candidate52f/Game52f.tscn"
const LAB_SHA := "201f667747406b1414a298a6b5433ac1550d8b447dff8f6cb6823d94d2acbd7c"
const LAB_CONTRACT := LAB_ROOT+"/source-assets/cloud-sea52h-runtime-d/temporary-world-comparison-contract.json"
const LAB_GLB := LAB_ROOT+"/source-assets/cloud-sea52h-revision-d/cloud_sea_52h_d_main_v0.glb"
const LAB_GLB_SHA := "0f8b70fef06f0e183b0c86138ae8e398ff699e202d0acd00f2233d8e4d9ec0aa"
var lab_view := ""
var lab_stage := "initializing"
var lab_phase := ""
var lab_targets: Array[String] = []
var lab_originals := {}
var lab_source_mesh: Mesh
var lab_source_transform := Transform3D.IDENTITY
var lab_source_geometry := {}
var lab_source_proof := {}
var lab_baseline := {}
var lab_baseline_digest := ""
var lab_phase_proofs := []
var lab_restore_rows := []
var lab_original_resources := []
var lab_gate := {}
var lab_completed := false
var lab_restore_complete := false
var lab_phase_returned := {"A0":false,"A":false,"D":false,"A2":false}
var lab_pixel_proof := {}
var lab_have_originals := false
var lab_source_returned := false
var lab_state_returned := false

const LAB_GEOMETRY := LAB_ROOT+"/source-assets/cloud-sea52h-revision-d/geometry52h-d.json"
const LAB_d5e824e71279cb65b2d4f599b65d8a2fa17dc9c0f41a651fb41c7c1f3a8eda3f := "d5e824e71279cb65b2d4f599b65d8a2fa17dc9c0f41a651fb41c7c1f3a8eda3f"
var cache_clones := {}
var cache_clone_rows := []
var cache_rebind_rows := []
var cache_intervention_returned := false
var cache_baseline_viewport := {}
var lab_initial_material_map := {}
var lab_viewport_rows := []
var lab_closed_source_proof := {}

func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--view="):lab_view=arg.trim_prefix("--view=")
	version="52h-d-runtime-ab";call_deferred("run")

func lab_atomic(path:String,data:Dictionary) -> bool:
	var file:=FileAccess.open(path+".tmp",FileAccess.WRITE)
	if file==null:failed=true;push_error("Cannot open atomic AB report "+path);return false
	file.store_string(JSON.stringify(data,"  "));file.flush();file.close()
	if DirAccess.rename_absolute(path+".tmp",path)!=OK:failed=true;push_error("Cannot commit atomic AB report "+path);return false
	return true

func write_partial(stage:String,pending:Dictionary={}) -> void:
	lab_stage=stage
	if output.is_empty() or not DirAccess.dir_exists_absolute(output):return
	lab_atomic(output.path_join("partial-report.json"),lab_report(false,pending))

func lab_report(complete:bool,pending:Dictionary={}) -> Dictionary:
	var non_scope_proven:bool=lab_phase_proofs.size()==4 and lab_phase_proofs[1].get("full_original_state_exact",false) and lab_phase_proofs[2].get("all_non_scope_typed_exact",false) and lab_phase_proofs[3].get("full_A2_state_exact",false)
	return {"run_complete":complete,"view":lab_view,"stage":lab_stage,"phase":lab_phase,"scene":LAB_SCENE,"scene_sha256":candidate_sha,
		"replacement_source":LAB_GLB,"replacement_sha256":LAB_GLB_SHA,"target_paths":lab_targets,"target_count":lab_targets.size(),
		"checks":checks,"captures":captures,"live_cloud_bindings":live_cloud_bindings,"source_proof":lab_source_proof,"closed_source_proof":lab_closed_source_proof,"phase_proofs":lab_phase_proofs,"viewport_rows":lab_viewport_rows,
		"clone_rows":cache_clone_rows,"rebind_rows":cache_rebind_rows,"equal_geometry_rebind_returned":cache_intervention_returned,
		"restore_rows":lab_restore_rows,"phase_functions_returned":lab_phase_returned,"source_function_returned":lab_source_returned,
		"state_comparison_functions_returned":lab_state_returned,"original_resources_kept":lab_original_resources.size(),
		"intrinsic_mesh_signal_scope":"Only source identity of exact mesh.changed -> same MeshInstance3D::_mesh_changed(flags0,no binds/no unbinds) follows the replacement mesh. All other connections protected; A and A2 fully unmasked.",
		"restoration_complete":lab_restore_complete,"baseline_native_digest":lab_baseline_digest,"pixel_proof":lab_pixel_proof,
		"A0_preserved":lab_phase_returned.A0,"A0_A_residual_is_explicit":true,"old52g_failure_unchanged":true,"shadow_root_cause_proven":false,
		"saved52f_external_audit_gate":lab_gate,"pending_capture":pending,"renderer":RenderingServer.get_video_adapter_name(),
		"native_provisional_passed":complete and lab_completed and not failed,"external_runner_gate_passed":false,
		"single_full_world":true,"scene_saved":false,"lights_or_materials_changed":false if non_scope_proven else null,"visual_acceptance":false,
		"hardware_gpu_acceptance":false,"complete_flight_passed":false,"old_lower_cloud_and_route_failures_resolved":false}

func lab_bool(value:Variant) -> bool:
	return typeof(value)==TYPE_BOOL and value==true

func lab_validate_gate() -> bool:
	if not check(FileAccess.get_sha256(LAB_SCENE)==LAB_SHA,"Exact fixed Game52f required"):return false
	var native:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(F_AUDIT))
	var process_path:String=native.get("process_report_path","")
	var ok:bool=native.get("audit_version","")=="v3" and lab_bool(native.get("runner_log_gate_passed")) and lab_bool(native.get("runner_final_gate_passed"))
	ok=ok and native.get("candidate_sha256","")==LAB_SHA and native.get("build_report_sha256","")==FileAccess.get_sha256(F_BUILD)
	ok=ok and FileAccess.file_exists(process_path) and FileAccess.get_sha256(process_path)==native.get("process_report_sha256","")
	if ok:
		var process:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(process_path))
		ok=int(process.get("python_returncode",-1))==0 and process.get("log_errors",["missing"]).is_empty() and lab_bool(process.get("frozen_inputs_unchanged")) and lab_bool(process.get("runner_final_gate_passed")) and process.get("runner_audit_gate_errors",["missing"]).is_empty()
	lab_gate={"passed":ok,"audit_sha256":FileAccess.get_sha256(F_AUDIT),"build_sha256":FileAccess.get_sha256(F_BUILD),"external_process_report":process_path,"external_process_report_sha256":FileAccess.get_sha256(process_path) if FileAccess.file_exists(process_path) else ""}
	return check(ok,"Existing52f v3 external process/error/completeness gate bound to exact scene")

func lab_geometry(mesh:Mesh) -> Dictionary:
	audit.resource_cache.clear();var surfaces:=[];var triangles:=0
	for i in range(mesh.get_surface_count()):
		var arrays:Array=mesh.surface_get_arrays(i);var counts:=[]
		for array in arrays:counts.append(array.size() if array!=null else -1)
		triangles+=arrays[Mesh.ARRAY_INDEX].size()/3 if arrays[Mesh.ARRAY_INDEX]!=null and arrays[Mesh.ARRAY_INDEX].size()>0 else arrays[Mesh.ARRAY_VERTEX].size()/3
		surfaces.append({"all_native_array_bytes_sha256":audit.digest(arrays),"array_slot_counts":counts,"surface_material":audit.canonical(mesh.surface_get_material(i))})
	return {"native_resource":audit.canonical(mesh),"surfaces":surfaces,"triangles":triangles,"bounds":mesh.get_aabb()}

func lab_load_source() -> bool:
	if not check(FileAccess.get_sha256(LAB_GLB)==LAB_GLB_SHA,"Exact approved real D GLB bytes"):return false
	var doc:=GLTFDocument.new();var state:=GLTFState.new()
	if not check(doc.append_from_file(LAB_GLB,state)==OK,"Fresh realGLB parse without project import/save"):return false
	var source:Node3D=doc.generate_scene(state)
	if not check(source!=null,"Actual imported GLB hierarchy available"):return false
	var found:=source.find_children("*","MeshInstance3D",true,false)
	if source is MeshInstance3D:found.push_front(source)
	var ok:=check(found.size()==1 and str(found[0].name)=="CloudSea52hD_v0_main_crown","Exactly one expected D main mesh")
	if ok:
		var node:MeshInstance3D=found[0]
		lab_source_mesh=node.mesh;lab_source_transform=audit.source_transform(node);lab_source_geometry=lab_geometry(lab_source_mesh)
		ok=check(lab_source_mesh.get_surface_count()==1 and int(lab_source_geometry.triangles)==1834,"Raw source contains actual1834 triangle main")
		lab_source_proof={"passed":ok,"raw_node":str(node.name),"raw_node_local_transform":audit.transform_values(node.transform),
			"actual_full_ancestor_transform":audit.transform_values(lab_source_transform),"ancestor_transform_exact_bytes":var_to_bytes(lab_source_transform).hex_encode(),
			"actual_geometry":lab_source_geometry,"source_node_attached_to_world":false}
	source.free();doc=null;state=null;lab_source_returned=true
	return ok

func lab_components(node:Node3D) -> Dictionary:
	return {"position":node.position,"rotation":node.rotation,"rotation_order":node.rotation_order,"scale":node.scale,"local_transform":node.transform,"global_transform":node.global_transform}

func lab_runtime_value(value:Variant) -> Variant:
	if value is Node:return {"node_instance_id":value.get_instance_id()}
	if value is Resource:return audit.canonical(value)
	if value is Callable:return {"callable_object_id":value.get_object_id(),"method":str(value.get_method()),"bound":lab_runtime_value(value.get_bound_arguments()),"unbind_count":value.get_unbound_arguments_count()}
	if value is Signal:return {"signal_object_id":value.get_object_id(),"name":str(value.get_name())}
	if value is Dictionary:
		var result:={}
		for key in value:result[key]=lab_runtime_value(value[key])
		return result
	if value is Array:
		var result:=[]
		for item in value:result.append(lab_runtime_value(item))
		return result
	if value is Object:
		var fields:={}
		for property in value.get_property_list():
			if property.usage & PROPERTY_USAGE_STORAGE:fields[str(property.name)]=audit.canonical(value.get(property.name))
		return {"object_class":value.get_class(),"instance_id":value.get_instance_id(),"stored_fields":fields}
	return value

func lab_state() -> Dictionary:
	var stored:Dictionary=audit.full_snapshot(game);var runtime:={};var order:=[]
	var nodes:Array[Node]=[game];nodes.append_array(game.find_children("*","",true,false))
	for node in nodes:
		var path:=str(game.get_path_to(node));order.append(path)
		var row:={"class":node.get_class(),"instance_id":node.get_instance_id(),"owner":node.owner.get_instance_id() if node.owner!=null else 0,
			"parent":node.get_parent().get_instance_id() if node.get_parent()!=null else 0,"groups":node.get_groups(),"scene_file_path":node.scene_file_path,
			"process":node.is_processing(),"physics":node.is_physics_processing(),"input":node.is_processing_input(),"unhandled_input":node.is_processing_unhandled_input()}
		var incoming:=[]
		for connection in node.get_incoming_connections():
			var signal_value:Signal=connection.signal;var callable_value:Callable=connection.callable
			incoming.append({"source_id":signal_value.get_object_id(),"signal":str(signal_value.get_name()),"target_id":callable_value.get_object_id(),"method":str(callable_value.get_method()),"flags":connection.flags,"bound":audit.canonical(callable_value.get_bound_arguments()),"unbind_count":callable_value.get_unbound_arguments_count()})
		row.incoming_connections=incoming
		var script_variables:={}
		for property in node.get_property_list():
			if property.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:script_variables[str(property.name)]=lab_runtime_value(node.get(property.name))
		row.all_script_variables=script_variables
		if node is Node3D:row.components=lab_components(node);row.visible=node.visible
		if node is MeshInstance3D:
			var surface_ids:=[];var active_ids:=[]
			if node.mesh!=null:
				for i in range(node.mesh.get_surface_count()):
					var sm:Material=node.mesh.surface_get_material(i);var am:Material=node.get_active_material(i)
					surface_ids.append(sm.get_instance_id() if sm!=null else 0);active_ids.append(am.get_instance_id() if am!=null else 0)
			row.mesh_binding={"mesh_id":node.mesh.get_instance_id() if node.mesh!=null else 0,"surface_material_ids":surface_ids}
			row.active_material_ids=active_ids;row.material_override_id=node.material_override.get_instance_id() if node.material_override!=null else 0
		if node is CollisionObject3D:row.physics=[node.collision_layer,node.collision_mask,node.disable_mode,node.can_process(),str(node.get_rid())]
		if node is Camera3D:row.actual_camera_projection=node.get_camera_projection()
		runtime[path]=row
	var gameplay:={}
	for name in ["throttle","speed","heading","altitude","clearance","fuel","shield","health","anchored","docked","dock_id","photo_mode","reference_observation","testing","test_frozen","test_override_input","test_input","auto_pilot","vertical_speed","elapsed","travelled","focus_timer","impact_timer","cockpit","orbit","zoom","score","completed","collected_rings","target_port","last_safe_port","notice","notification_time"]:gameplay[name]=audit.canonical(game.get(name))
	gameplay.body_velocity=game.airship.velocity
	return {"nodes":stored,"runtime":runtime,"order":order,"weather":audit.weather_state(game),"guarded_bindings":audit.material_bindings(game),"environment":environment_state(),"gameplay":gameplay,"world_chunk_count":game.world.chunks.size(),"world_core_count":game.world.core.size()}

func lab_mesh_connection_exact(value:Dictionary,path:String) -> bool:
	var row:Dictionary=value.runtime[path]
	var expected:={"source_id":row.mesh_binding.mesh_id,"signal":"changed","target_id":row.instance_id,"method":"MeshInstance3D::_mesh_changed","flags":0,"bound":[],"unbind_count":0}
	var matches:=0
	for connection in row.incoming_connections:
		if audit.digest(connection)==audit.digest(expected):matches+=1
	return matches==1

func lab_masked(value:Dictionary) -> Dictionary:
	var result:Dictionary=value.duplicate(true)
	for path in lab_targets:
		var original_binding:Dictionary=value.runtime[path]
		var expected_connection:={"source_id":original_binding.mesh_binding.mesh_id,"signal":"changed","target_id":original_binding.instance_id,"method":"MeshInstance3D::_mesh_changed","flags":0,"bound":[],"unbind_count":0}
		for connection in result.runtime[path].incoming_connections:
			if audit.digest(connection)==audit.digest(expected_connection):connection.source_id="<exact-current-mesh-resource>"
		result.nodes[path].erase("mesh");result.runtime[path].erase("mesh_binding")
		if var_to_bytes(lab_originals[path].components.local_transform)!=var_to_bytes(lab_source_transform):
			for key in ["transform","position","rotation","rotation_degrees","quaternion","scale"]:result.nodes[path].erase(key)
			for key in ["position","rotation","scale","local_transform","global_transform"]:result.runtime[path].components.erase(key)
	return result

func lab_changes(a:Dictionary,b:Dictionary) -> Array:
	var result:=[]
	for path in a:
		if not b.has(path):result.append({"path":path,"kind":"removed"});continue
		for key in a[path]:
			if not b[path].has(key) or audit.digest(a[path][key])!=audit.digest(b[path][key]):
				result.append({"path":path,"property":key,"before_native_type":type_string(typeof(a[path][key])),"after_native_type":type_string(typeof(b[path].get(key))),"before_typed_digest":audit.digest(a[path][key]),"after_typed_digest":audit.digest(b[path].get(key))})
		for key in b[path]:
			if not a[path].has(key):result.append({"path":path,"property":key,"kind":"added_property"})
	for path in b:
		if not a.has(path):result.append({"path":path,"kind":"added"})
	return result

func lab_save_baseline() -> void:
	var data:=var_to_bytes(audit.stable_variant(lab_baseline))
	var path:=output.path_join("A0-native-baseline.bin");var file:=FileAccess.open(path,FileAccess.WRITE)
	if not check(file!=null,"Single full typed baseline file writable"):return
	file.store_buffer(data);file.flush();file.close()
	lab_atomic(output.path_join("A0-native-baseline-summary.json"),{"typed_state_digest":lab_baseline_digest,"binary_sha256":FileAccess.get_sha256(path),"binary_bytes":data.size(),"nodes":lab_baseline.nodes.size(),"scope_paths":lab_targets,"native_only_comparison":true,"json_flags_never_compared_to_native":true})

func lab_prepare_originals() -> bool:
	var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(LAB_CONTRACT))
	if not check(manifest.get("baseline_sha256","")==LAB_SHA and manifest.get("replacement_glb_sha256","")==LAB_GLB_SHA,"Contract binds fixed scene and exact D source"):return false
	for value in manifest.get("target_paths",[]):lab_targets.append(str(value))
	if not check(lab_targets.size()==10,"Exactly ten contracted v0 main paths"):return false
	var unique:={}
	for path in lab_targets:
		var node:=game.get_node_or_null(path) as MeshInstance3D
		if not check(node!=null and not unique.has(path) and str(node.name)=="CloudSea52e_v0_main_ridge","Unique original main target "+path):return false
		unique[path]=true
		if not check(node.mesh!=null and node.mesh.get_surface_count()==1 and node.material_override!=null,"Single-surface target with original active override "+path):return false
		lab_originals[path]={"mesh":node.mesh,"components":lab_components(node),"flags":audit.mesh_flags(node),"active_material":node.get_active_material(0),"original_geometry":lab_geometry(node.mesh)}
		lab_original_resources.append(node.mesh)
	lab_have_originals=true;return true

func lab_apply_d() -> bool:
	lab_restore_complete=false
	for path in lab_targets:
		var node:MeshInstance3D=game.get_node(path)
		node.mesh=lab_source_mesh
		if var_to_bytes(node.transform)!=var_to_bytes(lab_source_transform):node.transform=lab_source_transform
	return true

func lab_restore() -> bool:
	if not lab_have_originals:return false
	lab_restore_rows.clear();var ok:=true
	for path in lab_targets:
		var node:MeshInstance3D=game.get_node(path);var saved:Dictionary=lab_originals[path];var c:Dictionary=saved.components
		node.mesh=saved.mesh
		# Restore original components, never infer them from a rounded global matrix.
		node.rotation_order=c.rotation_order;node.rotation=c.rotation;node.scale=c.scale;node.position=c.position
		var actual:=lab_components(node);var component_rows:=[];var all_equal:=true
		for key in c:
			var same_type:bool=typeof(c[key])==typeof(actual[key])
			var exact:bool=same_type and var_to_bytes(c[key])==var_to_bytes(actual[key])
			component_rows.append({"component":key,"native_type":type_string(typeof(c[key])),"exact":exact,"before_bytes":var_to_bytes(c[key]).hex_encode(),"restored_bytes":var_to_bytes(actual[key]).hex_encode()});all_equal=all_equal and exact
		var mesh_exact:bool=node.mesh==saved.mesh
		var flags_exact:bool=audit.digest(audit.mesh_flags(node))==audit.digest(saved.flags)
		var material_exact:bool=node.get_active_material(0)==saved.active_material
		var row:={"path":path,"all_components_exact":all_equal,"mesh_resource_identity_restored":mesh_exact,"flags_typed_exact":flags_exact,"active_material_identity_exact":material_exact,"components":component_rows}
		lab_restore_rows.append(row);ok=ok and all_equal and mesh_exact and flags_exact and material_exact
	lab_restore_complete=ok
	return check(ok and lab_restore_rows.size()==10,"All10 original mesh identities/local-global/component states/materials/flags restored exactly")

func lab_phase_capture(phase:String) -> bool:
	lab_phase=phase;meshes_world.clear();collect_cloud_triangles();check_live_clouds(phase)
	await capture("1216-front-"+phase,"1216","front")
	var state:Dictionary=lab_state();var proof:={"phase":phase,"full_native_digest":audit.digest(state),"node_count":state.nodes.size()}
	var connection_rows:=[]
	for path in lab_targets:
		var exact:bool=lab_mesh_connection_exact(state,path)
		connection_rows.append({"path":path,"exact_current_mesh_changed_callback":exact})
		check(exact,"Exact intrinsic mesh.changed callback and target "+phase+" "+path)
	proof.mesh_connection_rows=connection_rows
	if phase=="A0":
		lab_baseline=state;lab_baseline_digest=audit.digest(state);lab_save_baseline()
		proof.exact_original_baseline=true
	else:
		var masked_exact:bool=audit.digest(lab_masked(state))==audit.digest(lab_masked(lab_baseline))
		proof.all_non_scope_typed_exact=masked_exact;proof.actual_stored_property_changes=lab_changes(lab_baseline.nodes,state.nodes)
		proof.runtime_differences=lab_changes(lab_baseline.runtime,state.runtime)
		check(masked_exact,"All non-scope stored/native/resource/graph/gameplay/weather/lighting/camera state exact "+phase)
		var target_rows:=[]
		for path in lab_targets:
			var node:MeshInstance3D=game.get_node(path);var saved:Dictionary=lab_originals[path]
			var flags_exact:bool=audit.digest(audit.mesh_flags(node))==audit.digest(saved.flags)
			var material_exact:bool=node.get_active_material(0)==saved.active_material
			var source_exact:bool=audit.digest(lab_geometry(node.mesh))==audit.digest(lab_source_geometry) if phase=="D" else node.mesh==saved.mesh
			var transform_exact:bool=var_to_bytes(node.transform)==var_to_bytes(lab_source_transform) if phase=="D" else audit.digest(lab_components(node))==audit.digest(saved.components)
			target_rows.append({"path":path,"flags_native_typed_exact":flags_exact,"original_active_material_identity_exact":material_exact,"actual_source_or_restored_mesh_exact":source_exact,"actual_ancestor_or_restored_components_exact":transform_exact,"intrinsic_mesh_change_connection_exact":lab_mesh_connection_exact(state,path)})
			check(flags_exact and material_exact and source_exact and transform_exact,"Typed target/resource/source-transform exact "+phase+" "+path)
		proof.targets=target_rows
		if phase=="D":
			var changed_mesh_paths:=[]
			for row in proof.actual_stored_property_changes:
				if row.get("property","")=="mesh":changed_mesh_paths.append(row.path)
			changed_mesh_paths.sort();var expected:=lab_targets.duplicate();expected.sort()
			proof.exact_ten_mesh_changes=changed_mesh_paths==expected
			check(proof.exact_ten_mesh_changes,"Exactly10 stored main mesh replacements")
		else:
			proof.full_original_state_exact=audit.digest(state)==lab_baseline_digest
			check(proof.full_original_state_exact,"Complete unmasked "+phase+" native state equals A0, including every scale component")
			if phase=="A2":proof.full_A2_state_exact=proof.full_original_state_exact
		lab_state_returned=true
	lab_check_viewport(phase)
	lab_phase_proofs.append(proof);lab_phase_returned[phase]=true;write_partial("phase_"+phase+"_completed")
	return not failed

func capture(label:String,reference:String,view:String) -> void:
	# Camera/lighting are already fixed. ReflectionViewport UPDATE_ALWAYS renders
	# changed geometry without repeatedly mutating controller.sync_count or state.
	await frames(5);await physics_frame;await RenderingServer.frame_post_draw
	var im:Image=root.get_texture().get_image();im.convert(Image.FORMAT_RGBA8)
	var path:=output.path_join(label+".png")
	write_partial("saving_capture",{"name":label,"path":path,"phase":lab_phase,"png_written":false})
	check(im.save_png(path)==OK,"Actual rendered "+label)
	var pos:Vector3=game.camera.global_position;var clear:=physical_clear(pos)
	check(clear,"Physical camera sphere clear "+label)
	var projection:Projection=game.camera.get_camera_projection();var columns:=[]
	for v in [projection.x,projection.y,projection.z,projection.w]:columns.append([v.x,v.y,v.z,v.w])
	captures.append({"name":label,"phase":lab_phase,"path":path,"sha256":FileAccess.get_sha256(path),"rgba_digest":audit.digest(im.get_data()),
		"reference":reference,"view":view,"camera_transform":audit.transform_values(game.camera.get_camera_transform()),"camera_fov":game.camera.fov,
		"camera_near":game.camera.near,"camera_far":game.camera.far,"camera_keep_aspect":game.camera.keep_aspect,"camera_projection_columns":columns,
		"target_camera_geometry":lab_camera_geometry(pos),"size":[im.get_width(),im.get_height()],"environment":environment_state(),"physical_camera_clear":clear,"cloud_center":cloud_center_state(pos),
		"layers_hidden_for_capture":false,"reflection_requested":controller.reflection_enabled,"clip_enabled":controller.clip_enabled,
		"optical_overscan":controller.optical_overscan,"reflection_sync_count":controller.sync_count,
		"world_chunk_count":game.world.chunks.size(),"world_core_count":game.world.core.size()})
	write_partial("capture_complete")

func finish() -> void:
	if lab_have_originals and not lab_restore_complete:lab_restore()
	var all_returned:bool=lab_phase_returned.A0 and lab_phase_returned.A and lab_phase_returned.D and lab_phase_returned.A2 and lab_source_returned and lab_state_returned and cache_intervention_returned
	lab_completed=all_returned and captures.size()==4 and lab_phase_proofs.size()==4 and lab_targets.size()==10 and lab_restore_rows.size()==10 and lab_restore_complete and not failed
	check(lab_completed,"All4 actual captures and normal-return source/rebind/state/restore proofs complete")
	write_partial("finished")
	if not output.is_empty() and DirAccess.dir_exists_absolute(output):lab_atomic(output.path_join("report.json"),lab_report(true))
	cache_clones.clear();lab_baseline.clear();lab_originals.clear();lab_original_resources.clear();lab_source_mesh=null;audit.resource_cache.clear()
	if is_instance_valid(game):game.queue_free()
	await frames(8);print("CLOUDSEA52H_D_AB_PENDING_EXTERNAL_GATE ",lab_completed," view=",lab_view);quit(0 if lab_completed else 1)

func run() -> void:
	if not check(DisplayServer.get_name()!="headless","Actual renderer required, parent-owned execution"):quit(2);return
	if not check(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output) and lab_view=="front","Fresh output and only bounded1216 front required"):quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	if not lab_validate_gate() or not lab_validate_closed_source():await finish();return
	candidate_sha=FileAccess.get_sha256(LAB_SCENE);default_sha=FileAccess.get_sha256("res://project.godot")
	if not lab_load_source():await finish();return
	var packed:PackedScene=ResourceLoader.load(LAB_SCENE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	game=packed.instantiate();packed=null
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node("World/LakeReflection51")
	var collisions:=collision_state(game);freeze_tree(game);await physics_frame;await physics_frame
	check(collisions==collision_state(game),"Callback freeze preserves live physics state")
	await prepare_view("1216")
	for i in range(5):controller.refresh_now();await process_frame
	await RenderingServer.frame_post_draw
	if not lab_prepare_originals() or not cache_prepare_clones():await finish();return
	write_partial("single_world_frozen_and_sources_ready")
	if not await lab_phase_capture("A0"):await finish();return
	if not cache_rebind():await finish();return
	if not await lab_phase_capture("A"):await finish();return
	lab_apply_d()
	if not await lab_phase_capture("D"):await finish();return
	if not lab_restore():await finish();return
	if not await lab_phase_capture("A2"):await finish();return
	lab_pixel_proof={"A0_A_rgba_exact":captures[0].rgba_digest==captures[1].rgba_digest,"A0_A_png_exact":captures[0].sha256==captures[1].sha256,
		"A_A2_rgba_exact":captures[1].rgba_digest==captures[3].rgba_digest,"A_A2_png_exact":captures[1].sha256==captures[3].sha256,
		"D_differs_from_A":captures[1].rgba_digest!=captures[2].rgba_digest,"A0_preserved_and_not_pixel_acceptance_baseline":true,"strict_pixel_tolerance":0}
	check(lab_pixel_proof.A_A2_rgba_exact and lab_pixel_proof.A_A2_png_exact and lab_pixel_proof.D_differs_from_A,"Strict actual A2 restores stabilized original A pixels and D visibly differs",lab_pixel_proof)
	check(FileAccess.get_sha256(LAB_SCENE)==LAB_SHA and FileAccess.get_sha256(LAB_GLB)==LAB_GLB_SHA and FileAccess.get_sha256("res://project.godot")==default_sha,"SavedGame52f/source/default never changed")
	await finish()


func cache_prepare_clones() -> bool:
	for path in lab_targets:
		var original:Mesh=lab_originals[path].mesh;var id:=original.get_instance_id()
		if not cache_clones.has(id):cache_clones[id]=original.duplicate(false) as Mesh
		var clone:Mesh=cache_clones[id]
		var geometry_exact:bool=audit.digest(lab_geometry(original))==audit.digest(lab_geometry(clone))
		var materials_exact:=original.get_surface_count()==clone.get_surface_count()
		for i in range(original.get_surface_count()):materials_exact=materials_exact and original.surface_get_material(i)==clone.surface_get_material(i)
		var row:={"path":path,"original_mesh_id":id,"clone_mesh_id":clone.get_instance_id(),"distinct_resource_and_rid":clone!=original and clone.get_rid()!=original.get_rid(),
			"all_geometry_native_bytes_exact":geometry_exact,"surface_material_identities_exact":materials_exact}
		cache_clone_rows.append(row)
		if not check(row.distinct_resource_and_rid and geometry_exact and materials_exact,"Exact geometry/material clone "+path):return false
	return true

func cache_rebind() -> bool:
	# No await here. The renderer receives both resource changes; no frame shows
	# altered geometry because the clone is exact and original is restored here.
	for path in lab_targets:
		var node:MeshInstance3D=game.get_node(path);var saved:Dictionary=lab_originals[path]
		var clone:Mesh=cache_clones[saved.mesh.get_instance_id()]
		node.mesh=clone
		var clone_bound:bool=node.mesh==clone and node.get_active_material(0)==saved.active_material
		node.mesh=saved.mesh
		var row:={"path":path,"clone_was_bound":clone_bound,"original_identity_restored":node.mesh==saved.mesh,
			"all_components_untouched_exact":audit.digest(lab_components(node))==audit.digest(saved.components),
			"flags_exact":audit.digest(audit.mesh_flags(node))==audit.digest(saved.flags),"active_material_identity_exact":node.get_active_material(0)==saved.active_material}
		cache_rebind_rows.append(row)
		if not check(clone_bound and row.original_identity_restored and row.all_components_untouched_exact and row.flags_exact and row.active_material_identity_exact,"Only exact resource rebind "+path):return false
	# Read-only proof: do not call component setters, even with equal values.
	if not cache_prove_restore():return false
	cache_intervention_returned=true;return true

func cache_prove_restore() -> bool:
	lab_restore_rows.clear();var ok:=true
	for path in lab_targets:
		var node:MeshInstance3D=game.get_node(path);var saved:Dictionary=lab_originals[path]
		if node.mesh!=saved.mesh:node.mesh=saved.mesh
		var actual:=lab_components(node);var component_rows:=[];var all_equal:=true
		for key in saved.components:
			var before:Variant=saved.components[key];var after:Variant=actual[key]
			var exact:bool=typeof(before)==typeof(after) and var_to_bytes(before)==var_to_bytes(after)
			component_rows.append({"component":key,"exact":exact,"native_type":type_string(typeof(before)),"before_bytes":var_to_bytes(before).hex_encode(),"restored_bytes":var_to_bytes(after).hex_encode()});all_equal=all_equal and exact
		var row:={"path":path,"all_components_exact":all_equal,"components":component_rows,"mesh_resource_identity_restored":node.mesh==saved.mesh,
			"flags_typed_exact":audit.digest(audit.mesh_flags(node))==audit.digest(saved.flags),"active_material_identity_exact":node.get_active_material(0)==saved.active_material}
		lab_restore_rows.append(row);ok=ok and all_equal and row.mesh_resource_identity_restored and row.flags_typed_exact and row.active_material_identity_exact
	lab_restore_complete=ok and lab_restore_rows.size()==10
	return check(lab_restore_complete,"Ten exact original mesh/component/material restores; no component setters")

func cache_viewport() -> Dictionary:
	return {"requested_window_size":root.size,"content_scale_size":root.content_scale_size,"content_scale_mode":root.content_scale_mode,
		"content_scale_aspect":root.content_scale_aspect,"content_scale_factor":root.content_scale_factor,
		"capture_readback_size":Vector2i(int(captures[-1].size[0]),int(captures[-1].size[1])),
		"texture_metadata_dimensions":Vector2i(root.get_texture().get_width(),root.get_texture().get_height()),
		"visible_rect":root.get_visible_rect(),"stretch_transform":root.get_stretch_transform(),
		"camera_visible_rect":game.camera.get_viewport().get_visible_rect(),"camera_projection":game.camera.get_camera_projection(),
		"msaa_3d":root.msaa_3d,"use_taa":root.use_taa,"screen_space_aa":root.screen_space_aa}

func lab_check_viewport(phase:String) -> void:
	var viewport:=cache_viewport()
	if phase=="A0":cache_baseline_viewport=viewport
	var viewport_exact:bool=audit.digest(viewport)==audit.digest(cache_baseline_viewport)
	var projection:Projection=game.camera.get_camera_projection()
	var requested_exact:bool=root.size==Vector2i(1180,664)
	var content_config_exact:bool=root.content_scale_size==Vector2i(1672,941) and root.content_scale_mode==Window.CONTENT_SCALE_MODE_CANVAS_ITEMS and root.content_scale_aspect==Window.CONTENT_SCALE_ASPECT_KEEP and root.content_scale_factor==1.0
	var readback_exact:bool=viewport.capture_readback_size==Vector2i(1179,664) and int(floor(664.0*1672.0/941.0))==1179
	# Godot4.5.1 ViewportTexture::get_width/height applies the Window stretch
	# to internal viewport size. get_image() instead reads the real RS texture.
	var stretch_scale:Vector2=root.get_stretch_transform().get_scale()
	var expected_metadata:=Vector2i(int(1179.0*stretch_scale.x),int(664.0*stretch_scale.y))
	var metadata_exact:bool=viewport.texture_metadata_dimensions==expected_metadata and expected_metadata==Vector2i(831,468)
	var projection_exact:bool=abs(projection.y.y/projection.x.x-1672.0/941.0)<0.000001
	var dimensions_contract:bool=requested_exact and content_config_exact and readback_exact and metadata_exact and projection_exact

	lab_viewport_rows.append({"phase":phase,"viewport_exact":viewport_exact,"viewport_typed_digest":audit.digest(viewport),"viewport_values":audit.canonical(viewport),"dimensions_contract_exact":dimensions_contract,
		"actual_dimensions":[int(viewport.capture_readback_size.x),int(viewport.capture_readback_size.y)],"texture_metadata_dimensions":[int(viewport.texture_metadata_dimensions.x),int(viewport.texture_metadata_dimensions.y)],
		"metadata_expected_from_engine_formula":[expected_metadata.x,expected_metadata.y],"requested_dimensions":[1180,664],"expected_dimensions_from_fixed_project":[1179,664],
		"requested_size_exact":requested_exact,"content_config_exact":content_config_exact,"actual_readback_size_exact":readback_exact,"texture_metadata_formula_exact":metadata_exact,"projection_aspect_exact":projection_exact})
	check(viewport_exact,"Viewport configuration and metadata stable "+phase)
	check(requested_exact and content_config_exact,"Requested Window and fixed project content dimensions exact "+phase)
	check(readback_exact,"Actual captured Image readback1179x664 exact "+phase)
	check(metadata_exact,"ViewportTexture metadata831x468 matches engine stretch formula "+phase)
	check(projection_exact,"Camera projection aspect matches fixed1672x941 content "+phase)

func check_live_clouds(reference:String) -> void:
	super.check_live_clouds(reference)
	var materials:={}
	for row in live_cloud_bindings[-1].rows:
		var node:MeshInstance3D=game.get_node(row.path);var material:Material=node.get_active_material(0)
		row.active_material_id=material.get_instance_id();row.active_material_typed_digest=audit.digest(audit.canonical(material))
		materials[row.path]={"instance_id":row.active_material_id,"typed_digest":row.active_material_typed_digest}
	if reference=="1216":lab_initial_material_map=materials
	var exact:bool=not lab_initial_material_map.is_empty() and audit.digest(materials)==audit.digest(lab_initial_material_map)
	live_cloud_bindings[-1].all_initial_material_identities_and_values_exact=exact
	check(exact,"All125 active material identities/values equal initialization "+reference)

func lab_validate_closed_source() -> bool:
	if not check(FileAccess.get_sha256(LAB_GEOMETRY)==LAB_GEOMETRY_SHA,"Exact native geometry/readback proof bytes"):return false
	var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(LAB_GEOMETRY))
	var row:Dictionary=proof.variants[0]
	var readback:Dictionary=row.native_GLBlender_readback
	var ok:bool=lab_bool(proof.geometry_and_native_readback_passed) and lab_bool(row.passed) and proof.variants.size()==1 and int(row.triangles)==1834 and row.components.size()==1 and int(row.components[0])==919
	ok=ok and int(row.boundary_edges)==0 and int(row.nonmanifold_edges)==0 and int(row.nonadjacent_triangle_intersections)==0 and int(row.zero_area_triangles)==0 and float(row.signed_volume_m3)>0.0
	ok=ok and lab_bool(readback.all_oriented_triangle_correspondence_exact) and float(readback.max_vertex_error_m)==0.0 and float(readback.axis_bounds_error_m)==0.0 and proof.source_sha256.get("cloud_sea_52h_d_main_v0.glb","")==LAB_GLB_SHA
	lab_closed_source_proof={"passed":ok,"geometry_report_sha256":LAB_GEOMETRY_SHA,"bound_glb_sha256":LAB_GLB_SHA,"closed_manifold_component_count":1,"triangles":1834,"self_intersections":0,"native_glb_readback_exact":true if ok else false}
	return check(ok,"Closed continuous D source proof bound to exact exported GLB")

func lab_closest_triangle(p:Vector3,a:Vector3,b:Vector3,c:Vector3) -> Vector3:
	var ab:=b-a;var ac:=c-a;var ap:=p-a;var d1:=ab.dot(ap);var d2:=ac.dot(ap)
	if d1<=0.0 and d2<=0.0:return a
	var bp:=p-b;var d3:=ab.dot(bp);var d4:=ac.dot(bp)
	if d3>=0.0 and d4<=d3:return b
	var vc:=d1*d4-d3*d2
	if vc<=0.0 and d1>=0.0 and d3<=0.0:return a+ab*(d1/(d1-d3))
	var cp:=p-c;var d5:=ab.dot(cp);var d6:=ac.dot(cp)
	if d6>=0.0 and d5<=d6:return c
	var vb:=d5*d2-d1*d6
	if vb<=0.0 and d2>=0.0 and d6<=0.0:return a+ac*(d2/(d2-d6))
	var va:=d3*d6-d5*d4
	if va<=0.0 and d4-d3>=0.0 and d5-d6>=0.0:return b+(c-b)*((d4-d3)/((d4-d3)+(d5-d6)))
	var denominator:=1.0/(va+vb+vc)
	return a+ab*(vb*denominator)+ac*(vc*denominator)

func lab_camera_geometry(pos:Vector3) -> Dictionary:
	var rows:=[];var counts:={"inside":0,"outside":0,"boundary":0,"ambiguous":0}
	var directions:=[Vector3(.941,.233,.242).normalized(),Vector3(-.337,.871,.356).normalized(),Vector3(.271,-.419,.867).normalized()]
	for mesh in meshes_world:
		if not lab_targets.has(mesh.path):continue
		var points:PackedVector3Array=mesh.triangles;var nearest_squared:=INF;var nearest_point:=Vector3.ZERO;var nearest_index:=-1
		for i in range(0,points.size(),3):
			var q:=lab_closest_triangle(pos,points[i],points[i+1],points[i+2]);var distance:=pos.distance_squared_to(q)
			if distance<nearest_squared:nearest_squared=distance;nearest_point=q;nearest_index=i/3
		var ray_rows:=[];var odd:=0
		for direction in directions:
			var hits:Array=mesh_hits(mesh,pos,direction,100000.0);var inside:bool=hits.size()%2==1
			if inside:odd+=1
			ray_rows.append({"direction":[direction.x,direction.y,direction.z],"unique_crossings":hits.size(),"odd_parity":inside,"first_crossing_m":hits[0] if not hits.is_empty() else null})
		var nearest:=sqrt(nearest_squared);var classification:="boundary" if nearest<=.025 else ("inside" if odd==3 else ("outside" if odd==0 else "ambiguous"))
		counts[classification]+=1
		var node:MeshInstance3D=game.get_node(mesh.path)
		rows.append({"path":mesh.path,"classification":classification,"nearest_surface_m":nearest,"nearest_surface_point_world":[nearest_point.x,nearest_point.y,nearest_point.z],"nearest_triangle_index":nearest_index,
			"actual_world_triangles":points.size()/3,"actual_world_triangle_bytes_digest":audit.digest(points),"actual_global_transform":audit.transform_values(node.global_transform),"ray_tests":ray_rows,
			"actual_D_resource_bound":node.mesh==lab_source_mesh,"D_closed_source_proof_applies":lab_phase=="D" and node.mesh==lab_source_mesh and lab_closed_source_proof.get("passed",false)})
	var complete:bool=rows.size()==10 and counts.ambiguous==0
	check(complete,"Actual camera inside/outside/boundary triangle diagnostics complete "+lab_phase)
	return {"complete":complete,"phase":lab_phase,"camera_world":[pos.x,pos.y,pos.z],"boundary_epsilon_m":.025,"ray_hit_dedup_m":.001,"counts":counts,"rows":rows,
		"outside_all_ten_target_volumes":complete and counts.outside==10,"method":"Closest actual world-triangle surface distance plus three nonparallel ray-parity votes for each retained closed volume; no physical collider inference","is_ship_or_sphere_clearance_proof":false}

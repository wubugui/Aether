"""Prepare the independent D observer from the retained strict native-state machinery."""
from pathlib import Path
import json,hashlib,re
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
base=ROOT/'source-assets/cloud-sea52g/runtime-d-ab/observe52g_d_ab.gd'
cache=ROOT/'source-assets/cloud-sea52g/runtime-cache-diagnostic-v2/observe52g_cache.gd'
s=base.read_text();cs=cache.read_text()
def replace_func(text,name,new):
 pattern=r'(?ms)^func '+re.escape(name)+r'\([^\n]*\).*?(?=^func |\Z)'
 matches=list(re.finditer(pattern,text));assert len(matches)==1,name
 return text[:matches[0].start()]+new.rstrip()+'\n\n'+text[matches[0].end():]
def get_func(text,name):
 m=re.search(r'(?ms)^func '+re.escape(name)+r'\([^\n]*\).*?(?=^func |\Z)',text);assert m,name
 return m.group().strip()+'\n'
s=s.replace('## Runtime-only A/B/A2 in one fixed52f tree. No PackedScene save or layer hiding.','## Runtime-only A0 / rebound-original A / D / exact-restored A2. One unchanged full world.')
s=s.replace('/source-assets/cloud-sea52g/runtime-d-ab/','/source-assets/cloud-sea52h-runtime-d/')
s=s.replace('/source-assets/cloud-sea52g/revision-d-combination/temporary-world-comparison-contract.json','/source-assets/cloud-sea52h-runtime-d/temporary-world-comparison-contract.json')
s=s.replace('/source-assets/cloud-sea52g/revision-d-combination/cloud_sea_52g_d_main_only.glb','/source-assets/cloud-sea52h-revision-d/cloud_sea_52h_d_main_v0.glb')
s=s.replace('a399fac8726ab341757a7249d17773e14a28002337eb86ae5e159d9436438624','0f8b70fef06f0e183b0c86138ae8e398ff699e202d0acd00f2233d8e4d9ec0aa')
s=s.replace('CloudSea52g_d_v0_main_crown','CloudSea52hD_v0_main_crown').replace('2200','1834').replace('52g-d-runtime-ab','52h-d-runtime-ab')
s=s.replace('var lab_phase_returned := {"A":false,"B":false,"A2":false}', 'var lab_phase_returned := {"A0":false,"A":false,"D":false,"A2":false}')
s=s.replace('func lab_apply_b()', 'func lab_apply_d()').replace('func lab_apply_d() -> bool:\n', 'func lab_apply_d() -> bool:\n\tlab_restore_complete=false\n')
extra_vars='''const LAB_GEOMETRY := LAB_ROOT+"/source-assets/cloud-sea52h-revision-d/geometry52h-d.json"
const LAB_GEOMETRY_SHA := "__GEOMETRY_DIGEST__"
var cache_clones := {}
var cache_clone_rows := []
var cache_rebind_rows := []
var cache_intervention_returned := false
var cache_baseline_viewport := {}
var lab_initial_material_map := {}
var lab_viewport_rows := []
var lab_closed_source_proof := {}
'''.replace('__GEOMETRY_DIGEST__',hashlib.sha256((ROOT/'source-assets/cloud-sea52h-revision-d/geometry52h-d.json').read_bytes()).hexdigest())
s=s.replace('func _initialize()',extra_vars+'\nfunc _initialize()',1)
s=replace_func(s,'lab_report','''func lab_report(complete:bool,pending:Dictionary={}) -> Dictionary:
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
''')
# Full typed baseline remains A0, saved once. A must equal it unmasked after rebind.
s=s.replace('"A-native-baseline.bin"','"A0-native-baseline.bin"').replace('"A-native-baseline-summary.json"','"A0-native-baseline-summary.json"')
s=replace_func(s,'lab_phase_capture','''func lab_phase_capture(phase:String) -> bool:
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
''')
s=s.replace('"size":[im.get_width(),im.get_height()],"environment"', '"target_camera_geometry":lab_camera_geometry(pos),"size":[im.get_width(),im.get_height()],"environment"')
s=replace_func(s,'finish','''func finish() -> void:
	if lab_have_originals and not lab_restore_complete:lab_restore()
	var all_returned:bool=lab_phase_returned.A0 and lab_phase_returned.A and lab_phase_returned.D and lab_phase_returned.A2 and lab_source_returned and lab_state_returned and cache_intervention_returned
	lab_completed=all_returned and captures.size()==4 and lab_phase_proofs.size()==4 and lab_targets.size()==10 and lab_restore_rows.size()==10 and lab_restore_complete and not failed
	check(lab_completed,"All4 actual captures and normal-return source/rebind/state/restore proofs complete")
	write_partial("finished")
	if not output.is_empty() and DirAccess.dir_exists_absolute(output):lab_atomic(output.path_join("report.json"),lab_report(true))
	cache_clones.clear();lab_baseline.clear();lab_originals.clear();lab_original_resources.clear();lab_source_mesh=null;audit.resource_cache.clear()
	if is_instance_valid(game):game.queue_free()
	await frames(8);print("CLOUDSEA52H_D_AB_PENDING_EXTERNAL_GATE ",lab_completed," view=",lab_view);quit(0 if lab_completed else 1)
''')
s=replace_func(s,'run','''func run() -> void:
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
	lab_pixel_proof={"A0_A_rgba_exact":captures[0].rgba_digest==captures[1].rgba_digest,"A0_A_png_exact":captures[0].sha256==captures[1].sha256,"A0_preserved_and_not_pixel_acceptance_baseline":true,"strict_pixel_tolerance":0}
	write_partial("A0_A_rebind_residual_recorded")
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
''')
s+='\n'+get_func(cs,'cache_prepare_clones')+'\n'+get_func(cs,'cache_rebind')+'\n'+get_func(cs,'cache_prove_restore')+'\n'+get_func(cs,'cache_viewport')
# Extract the already-proven viewport contract without the unrelated cache-state
# comparison. The real captured Image and stretched metadata remain separate.
vc=get_func(cs,'cache_capture');start=vc.index('\tvar projection:Projection=');end=vc.index('\tvar row:=')
body=vc[start:end]
s+='''
func lab_check_viewport(phase:String) -> void:
	var viewport:=cache_viewport()
	if phase=="A0":cache_baseline_viewport=viewport
	var viewport_exact:bool=audit.digest(viewport)==audit.digest(cache_baseline_viewport)
'''+body+'''
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
'''
(P/'observe52h_d_ab.gd').write_text(s)
contract=json.loads((ROOT/'source-assets/cloud-sea52g/revision-d-combination/temporary-world-comparison-contract.json').read_text())
contract.update(status='Prepared for explicitly authorized single1216-front D trial; not a visual pass',replacement_glb='source-assets/cloud-sea52h-revision-d/cloud_sea_52h_d_main_v0.glb',replacement_glb_sha256='0f8b70fef06f0e183b0c86138ae8e398ff699e202d0acd00f2233d8e4d9ec0aa',replacement_glb_node='CloudSea52hD_v0_main_crown',replacement_mesh_triangles=1834,phase_order=['A0','A','D','A2'],material_proof_order=['1216','A0','A','D','A2'],geometry_report_sha256=hashlib.sha256((ROOT/'source-assets/cloud-sea52h-revision-d/geometry52h-d.json').read_bytes()).hexdigest(),viewport_requested=[1180,664],viewport_actual_readback=[1179,664],viewport_texture_metadata=[831,468],actual_camera_triangle_classification_required=True,strict_A_A2_RGBA_tolerance=0)
contract['only_expected_scene_change']='Ten existing main mesh resources, plus only a necessary actual GLB ancestor transform; root and other115 meshes stay exact'
contract['preserve'][1]='target node paths and ownership; original local/global/component values restored exactly after D'
contract['do_not_use']='Canceled C runtime; old52g failure is preserved; no rejected54 payload'
(P/'temporary-world-comparison-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
print('Independent D observer and exact four-phase contract prepared')

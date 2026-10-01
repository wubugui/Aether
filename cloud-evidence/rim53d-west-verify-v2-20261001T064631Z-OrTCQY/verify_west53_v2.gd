extends "/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53/integration-west53/build_west53.gd"
## Fresh-process native reload + actual ready/collision/scatter and fixed-view evidence.
const MOTION_SOURCE="/workspace/scratch/a29d03198654/Aether/cloud-evidence/reflection51b-motion-20261001T041545Z-WCymsr/images/reflection-motion-report.json"
var baseline_node:Node3D
var build_report:Dictionary
var front_only=false
var checks=[]
var baseline_probes_path=""
var baseline_proof:Dictionary={} 
func _initialize():
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--report-dir="):output=arg.trim_prefix("--report-dir=")
  if arg=="--front-only":front_only=true
  if arg.begins_with("--baseline-probes="):baseline_probes_path=arg.trim_prefix("--baseline-probes=")
 call_deferred("verify")
func check(ok:bool,label:String,details:Variant=null)->bool:
 checks.append({"passed":ok,"label":label,"details":details});print("PASS " if ok else "FAIL ",label)
 return require(ok,label,details)
func finish_verifier(ok:bool):
 report.verification_passed=ok;report.checks=checks;report.renderer=RenderingServer.get_video_adapter_name();report.visual_acceptance=false;report.hardware_gpu_acceptance=false
 if not output.is_empty():
  var f=FileAccess.open(output+"/verify-report-west53-v2.json",FileAccess.WRITE)
  if f!=null:f.store_string(JSON.stringify(report,"  "));f.close()
 if DisplayServer.get_name()!="headless":await settle()
 if is_instance_valid(baseline_node):baseline_node.free()
 if is_instance_valid(game):
  if game.is_inside_tree():game.queue_free()
  else:game.free()
 await frames(8);print("WEST53 V2_FRESH_VERIFICATION ",ok);quit(0 if ok else 1)
func freeze(n:Node):
 n.set_process(false);n.set_physics_process(false);n.set_process_input(false);n.set_process_unhandled_input(false);n.set_process_unhandled_key_input(false)
 if n is AnimationPlayer:n.pause()
 if n is Timer:n.paused=true
 for c in n.get_children():freeze(c)
func collision_state()->Dictionary:
 var out={}
 for n in game.find_children("*","CollisionObject3D",true,false):out[str(game.get_path_to(n))]=[n.process_mode,n.disable_mode,n.can_process(),n.collision_layer,n.collision_mask,str(n.get_rid())]
 return out
func probe(x:float,z:float)->Dictionary:
 return game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,1500,z),Vector3(x,-100,z),4))
func runtime_support()->bool:
 var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SOURCE+"runtime-probes.json"))
 var probes:Dictionary=original.duplicate(true)
 var corrections=[]
 for i in probes.buildings.size():
  var proof:Dictionary=baseline_proof.rows[i];var row:Dictionary=probes.buildings[i]
  var same_ray=Vector3(row.x,1500,row.z)==Vector3(proof.x,1500,proof.z)
  if not check(int(proof.index)==i and float(proof.index)==float(i) and same_ray and proof.source_region==row.node and int(proof.mask)==4,"Exact original building ray identity "+str(i)):return false
  row.old_partial_expected_y=row.expected_y;row.expected_y=proof.full_scene_baseline_physics_y
  if absf(row.expected_y-row.old_partial_expected_y)>=.03:corrections.append({"index":i,"region":row.node,"x":row.x,"z":row.z,"old_expected_y":row.old_partial_expected_y,"full_baseline_expected_y":row.expected_y,"baseline_collider":proof.collider})
 report.support_expectation_revision={"old_probe_file":SOURCE+"runtime-probes.json","old_probe_sha256":FileAccess.get_sha256(SOURCE+"runtime-probes.json"),"full_baseline_report":baseline_probes_path,"full_baseline_report_sha256":FileAccess.get_sha256(baseline_probes_path),"all171_rays_replaced_by_independent_full_baseline":true,"old_expected_errors_over_original_3cm_threshold":corrections,"threshold_m":.03,"geometry_or_resource_changed":false}
 var support_rows=[];var max_error=0.0;var ground_max=0.0;var missing=0
 for category in ["mountain","buildings"]:
  for row in probes[category]:
   var hit=probe(row.x,row.z)
   if hit.is_empty():missing+=1;continue
   var error=absf(hit.position.y-row.expected_y);max_error=maxf(max_error,error)
   var ground=game.get_node("World").ground_height(Vector3(row.x,1500,row.z));ground_max=maxf(ground_max,absf(ground-row.expected_y))
   support_rows.append({"kind":category,"x":row.x,"z":row.z,"expected_y":row.expected_y,"physics_y":hit.position.y,"ground_height_from_above":ground,"collider":str(game.get_path_to(hit.collider))})
 var scatter_rows=[];var unchanged=0;var changed=0;var scatter_max=0.0;var transform_max=0.0
 for row in probes.scatter:
  var n:MultiMeshInstance3D=game.get_node(row.node_path);var pose=n.global_transform*n.multimesh.get_instance_transform(int(row.index));var p=vec(row.position);var position_error=pose.origin.distance_to(p);transform_max=maxf(transform_max,position_error)
  var hit=probe(p.x,p.z)
  if hit.is_empty():missing+=1;continue
  var error=absf(hit.position.y-row.expected_support_y);scatter_max=maxf(scatter_max,error)
  if row.status=="unchanged":unchanged+=1
  else:changed+=1
  scatter_rows.append({"path":row.node_path,"index":row.index,"status":row.status,"position_error_m":position_error,"support_error_m":error,"actual_support_y":hit.position.y,"expected_support_y":row.expected_support_y})
 # Runtime cache must read the actual updated saved MultiMesh transforms at the original indices.
 var cache_ok=true;var global_index=0;var cache_count=0;var world=game.get_node("World")
 for grove in world.get_node("Vegetation").get_children():
  if not grove is MultiMeshInstance3D:continue
  var path=str(game.get_path_to(grove))
  for i in grove.multimesh.instance_count:
   if manifest.all_six_tile_scatter_counts.has(path):
    cache_count+=1;cache_ok=cache_ok and world.prop_transforms.has(global_index) and world.prop_transforms[global_index]==grove.global_transform*grove.multimesh.get_instance_transform(i)
   global_index+=1
 report.runtime_support={"mountain_building_rows":support_rows,"scatter_rows":scatter_rows,"missing":missing,"max_geometry_error_m":max_error,"ground_height_max_error_m":ground_max,"scatter_support_max_error_m":scatter_max,"scatter_position_max_error_m":transform_max,"unchanged_instances":unchanged,"changed_instances":changed,"runtime_cache_count":cache_count,"runtime_cache_exact":cache_ok}
 var summary=report.runtime_support.duplicate(false);summary.mountain_building_rows=[];summary.scatter_rows=[]
 return check(missing==0 and max_error<.03 and ground_max<.03 and scatter_max<.03 and transform_max<.002 and unchanged==1141 and changed==120 and cache_ok and cache_count==1261,"Actual layer4 support, ground_height-from-above and1261 saved/cache instances",summary)
func motion(reference:String,delta:Vector3,label:String,prior:Dictionary)->Dictionary:
 var camera=game.camera;var sphere=SphereShape3D.new();sphere.radius=maxf(.12,camera.near)
 var q=PhysicsShapeQueryParameters3D.new();q.shape=sphere;q.transform=Transform3D(Basis.IDENTITY,camera.global_position);q.motion=delta;q.collision_mask=5;q.exclude=[game.airship.get_rid()]
 var fraction=game.get_world_3d().direct_space_state.cast_motion(q);var ray=game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(camera.global_position,camera.global_position+delta,5,[game.airship.get_rid()]))
 q.motion=Vector3.ZERO
 var start_clear=game.get_world_3d().direct_space_state.intersect_shape(q).is_empty();q.transform.origin+=delta;q.motion=Vector3.ZERO
 var end_clear=game.get_world_3d().direct_space_state.intersect_shape(q).is_empty()
 var passed=start_clear and end_clear and fraction.size()==2 and fraction[0]>=1.0 and ray.is_empty()
 var collider=str(game.get_path_to(ray.collider)) if not ray.is_empty() else "none"
 var row={"reference":reference,"label":label,"passed":passed,"safe_fraction":fraction[0] if fraction.size() else -1,"collider":collider,"required_full_flight":false,"scope":"Camera sphere/ray only"}
 var key=reference+"/"+label;var old:Dictionary=prior.get(key,{})
 row.exact_prior51b_result_retained=not old.is_empty() and row.passed==old.passed and row.safe_fraction==old.safe_fraction and row.collider==old.collider
 check(row.exact_prior51b_result_retained,"Original51b camera-motion result retained "+key,row)
 return row
func capture(reference:String,label:String):
 var controller=game.get_node("World/LakeReflection51");controller.refresh_now();await frames(3);await physics_frame;controller.refresh_now();await RenderingServer.frame_post_draw
 var image=root.get_texture().get_image();var path=output+"/"+reference+"--"+label+".png";var err=image.save_png(path)
 check(err==OK,"Saved actual native candidate PNG "+reference+"/"+label)
 report.captures.append({"reference":reference,"label":label,"file":path,"sha256":FileAccess.get_sha256(path),"size":[image.get_width(),image.get_height()],"camera":str(game.camera.global_transform),"fov":game.camera.fov,"controller":controller.get_diagnostic_state()})
func verify():
 if DisplayServer.get_name()=="headless":quit(2);return
 report={"verification_passed":false,"failures":[],"captures":[],"motions":[],"visual_acceptance":false,"known_1344_conversion_pixel_gate_passed":false,"known_350m_route_failure_not_waived":true,"full_physical_airship_flight_verified":false,"arbitrary_future_stream_instances_verified":false}
 if not require(output.is_absolute_path() and DirAccess.dir_exists_absolute(output),"Existing report directory required"):await finish_verifier(false);return
 if not require(baseline_probes_path.is_absolute_path() and FileAccess.file_exists(baseline_probes_path),"Independent full51b baseline probe report required"):await finish_verifier(false);return
 var binding:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SOURCE+"verification-v2/baseline-proof-binding.json"))
 if not require(baseline_probes_path==binding.absolute_path and FileAccess.get_sha256(baseline_probes_path)==binding.sha256,"Independent full baseline report path/SHA changed"):await finish_verifier(false);return
 baseline_proof=JSON.parse_string(FileAccess.get_file_as_string(baseline_probes_path))
 if not require(baseline_proof.get("passed",false) and baseline_proof.get("all_171_rays_complete",false) and baseline_proof.get("freeze_preserves_physics",false) and baseline_proof.get("baseline_sha256","")==BASE_SHA and baseline_proof.get("probe_input_sha256","")==FileAccess.get_sha256(SOURCE+"runtime-probes.json") and baseline_proof.get("rows",[]).size()==171,"Full baseline proof missing, incomplete, wrong source or different original rays"):await finish_verifier(false);return
 if not require(FileAccess.file_exists(DEST+"build-report-west53.json"),"Successful saved build report required"):await finish_verifier(false);return
 build_report=JSON.parse_string(FileAccess.get_file_as_string(DEST+"build-report-west53.json"));manifest=JSON.parse_string(FileAccess.get_file_as_string(SOURCE+"integration-manifest.json"));payload=JSON.parse_string(FileAccess.get_file_as_string(SOURCE+"integration-payload.json"))
 if not check(build_report.build_saved_reload_passed and FileAccess.get_sha256(TARGET)==build_report.candidate_sha256 and FileAccess.get_sha256(BASE)==BASE_SHA,"Exact successful saved candidate and baseline SHA"):await finish_verifier(false);return
 if not check(FileAccess.get_sha256(SOURCE+"integration-manifest.json")==build_report.manifest_sha256,"Exact build manifest"):await finish_verifier(false);return
 for e in manifest.immutable_inputs:
  if not require(FileAccess.get_sha256(e.path)==e.sha256,"Immutable source/guard asset changed",e.path):await finish_verifier(false);return
 for e in build_report.inventory:
  if not require(FileAccess.get_sha256(e.path)==e.sha256,"Saved independent asset changed",e.path):await finish_verifier(false);return
 for part in PARTS:audit.added_paths[MODEL+"/"+part]=true
 audit.shape_edits[SHAPE]=true
 for e in payload.scatter:
  if not audit.scatter_edits.has(e.node_path):audit.scatter_edits[e.node_path]={}
  audit.scatter_edits[e.node_path][int(e.index)]=e
 var bp:PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);baseline_node=bp.instantiate();await settle()
 var cp:PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=cp.instantiate();await settle()
 if not check(audit.graph_state(baseline_node,bp)==audit.graph_state(game,cp),"Fresh native graph preserves every unmasked property, byte slot, owner, order, group and connection"):await finish_verifier(false);return
 if not check(audit.material_bindings(baseline_node)==audit.material_bindings(game) and audit.weather_state(baseline_node)==audit.weather_state(game),"Fresh248guard bindings/114materials/48000weather floats exact"):await finish_verifier(false);return
 audit.resource_cache.clear()
 if not check(audit.canonical(game.get_node(ORIGINAL).mesh)==build_report.original_root_mesh_fingerprint,"Original native root ArrayMesh exact"):await finish_verifier(false);return
 if not verify_targets(game):await finish_verifier(false);return
 report.saved_native_verified=true;report.candidate=TARGET;report.candidate_sha256=build_report.candidate_sha256;report.source_depth_proof=manifest.water_proof
 await settle();baseline_node.free();baseline_node=null
 bp=null;cp=null;audit.resource_cache.clear()
 await frames(8)
 root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
 await frames(20);await RenderingServer.frame_post_draw
 var before=collision_state();freeze(game);await physics_frame;await physics_frame
 if not check(before==collision_state(),"Callback freeze preserves collision modes/layers/RIDs"):await finish_verifier(false);return
 var mat:ShaderMaterial=game.get_node(ASSET).get("surface_material");var controller=game.get_node("World/LakeReflection51")
 for name in ["massif_west_spur"]+PARTS:
  var n:MeshInstance3D=game.get_node(MODEL+"/"+name)
  if not check(n.material_override==mat and n.get_active_material(0)==mat and controller.clipping_materials.has(mat),"Actual ready binding uses existing dual-guard material "+name):await finish_verifier(false);return
 if not runtime_support():await finish_verifier(false);return
 var prior_report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(MOTION_SOURCE));var prior={}
 for row in prior_report.movement_checks:prior[row.reference+"/"+row.label]=row
 report.prior_motion_report_sha256=FileAccess.get_sha256(MOTION_SOURCE)
 for reference in ["1128","1129"]:
  game.observe_reference(reference);var weather=game.get_node("Weather42b");weather.seek_time(0.0);weather.seek_time(.35);weather._process(0.0);RenderingServer.global_shader_parameter_set("world_time",.35)
  game.get_node("World/LakeDepth50").set_depth_enabled(true);controller.set_effect_flags(true,true);controller.refresh_now();await frames(5);await physics_frame;await RenderingServer.frame_post_draw
  var expected=Vector3(1150,10,-1000) if reference=="1128" else Vector3(1300,7,-950)
  check(game.camera.global_position.is_equal_approx(expected) and is_equal_approx(game.camera.fov,64.0 if reference=="1128" else 66.0),"Original fixed reference camera "+reference)
  for spec in [[game.camera.global_basis.x*350.,"original-plus350m"],[game.camera.global_basis.x*150.,"protected-plus150m"],[-game.camera.global_basis.z*200.,"protected-approach200m"]]:report.motions.append(motion(reference,spec[0],spec[1],prior))
  await capture(reference,"front-native")
  if not front_only:
   var pose:Transform3D=game.camera.global_transform;game.camera.rotate_y(deg_to_rad(55));await capture(reference,"side-native");game.camera.global_transform=pose;game.camera.rotate_y(PI);await capture(reference,"back-native");game.camera.global_transform=pose
   var approach=report.motions[-1]
   if approach.passed:game.camera.global_position-=game.camera.global_basis.z*200.;await capture(reference,"approach200m-native");game.camera.global_transform=pose
 if not front_only:
  for reference in ["1275","1276"]:
   game.observe_reference(reference);var weather=game.get_node("Weather42b");weather.seek_time(0.0);weather.seek_time(.35);weather._process(0.0);RenderingServer.global_shader_parameter_set("world_time",.35);controller.refresh_now();await frames(5);await capture(reference,"front-native")
 if not check(FileAccess.get_sha256(TARGET)==build_report.candidate_sha256 and FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256("res://project.godot")==build_report.project_default_sha256,"Saved candidate, baseline and default unchanged after live run"):await finish_verifier(false);return
 report.front_only=front_only;report.protected_camera_routes_passed=true
 for row in report.motions:
  if row.label!="original-plus350m":report.protected_camera_routes_passed=report.protected_camera_routes_passed and row.passed
 report.scope="West-only saved native scene; five meshes/1780 collision triangles;120 updated and1141 unchanged neighbor instances. Old water resources unchanged with continuous dry-footprint proof and exact saved geometry mapping. Known1344/350m/full-flight/full-reference failures remain unresolved."
 await finish_verifier(report.failures.is_empty())

extends SceneTree
const Audit=preload("../visible_geometry61.gd")
const Sequence=preload("../native_sequence61.gd")
const Telemetry=preload("../orbit_telemetry61.gd")

class EmptyIdentity:
 extends "../visible_geometry61.gd"
 func multimesh_identity(_node: MultiMeshInstance3D) -> Dictionary:
  return {} # Failed Dictionary-returning calls cannot become accepted identity.

var checks:=[]
var failed:=false
var output: String
var scene: Node3D
var camera: Camera3D
const EMPTY_SHA256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

func diagnostic(name: String, stage: String) -> void:
 print("ORBIT61_CASE ",name," ",stage)

func record(name: String, ok: bool, details: Variant=null) -> void:
 diagnostic(name,"passed" if ok else "failed")
 checks.append({"name":name,"passed":ok,"details":details})
 if not ok: failed=true

func _initialize() -> void:
 output=OS.get_cmdline_user_args()[0]
 call_deferred("run")

func fixture(hidden: bool=false, distant: bool=false, null_binding: bool=false, empty_mode: String="") -> Dictionary:
 var node:=MultiMeshInstance3D.new()
 node.name="MM_"+str(scene.get_child_count())
 var mm: MultiMesh=null
 var mesh: Mesh=null
 if not null_binding:
  mm=MultiMesh.new()
  if empty_mode!="fresh":
   mm.transform_format=MultiMesh.TRANSFORM_3D
   mm.use_colors=true;mm.use_custom_data=true
   if empty_mode!="null_mesh":
    mesh=BoxMesh.new();mm.mesh=mesh
   mm.instance_count=0 if empty_mode=="zero_instances" else 2
   if mm.instance_count>0:
    mm.set_instance_transform(0,Transform3D.IDENTITY)
    mm.set_instance_transform(1,Transform3D(Basis.IDENTITY,Vector3(2,0,0)))
    mm.set_instance_color(0,Color.WHITE);mm.set_instance_color(1,Color.WHITE)
    mm.set_instance_custom_data(0,Color(0,0,0,0));mm.set_instance_custom_data(1,Color(0,0,0,0))
   if empty_mode=="zero_visible": mm.visible_instance_count=0
  node.multimesh=mm
 node.visible=not hidden
 if distant: node.position=Vector3(1000,0,0)
 scene.add_child(node)
 var guard=Audit.new()
 guard.owner_game={"camera":camera};guard.domain=AABB(Vector3.ONE*-5,Vector3.ONE*10)
 var watch: Dictionary=guard.watch_entry(node,not hidden,0.0,guard.geometry_bounds(node))
 var bound: bool=guard.bind_multimesh_identity(watch)
 guard.watches.append(watch)
 # Retain resources independently of the node. In pinned GLES3, setting mesh
 # null leaves the prior server RID; dropping the last Mesh reference would
 # invalidate it until a later global dirty-instance drain (including free()).
 return {"node":node,"guard":guard,"watch":watch,"baseline_ok":bound,"held_multimesh":mm,"held_mesh":mesh}

func dispose_fixture(f: Dictionary) -> void:
 if not is_instance_valid(f.node): return
 # Keep both old and mutated resources alive through restoration and node free.
 var changed_mm: MultiMesh=f.node.multimesh
 var changed_mesh: Mesh=changed_mm.mesh if changed_mm!=null else null
 if f.held_multimesh!=null: f.held_multimesh.mesh=f.held_mesh
 f.node.multimesh=f.held_multimesh
 f.node.free()
 # These locals intentionally retain references until after native node teardown.
 if changed_mm!=null: changed_mm=null
 if changed_mesh!=null: changed_mesh=null

func check_guard(name: String, mutate: Callable, hidden: bool=false, distant: bool=false) -> void:
 diagnostic(name,"begin")
 var f:=fixture(hidden,distant)
 var baseline: bool=f.baseline_ok and f.guard.unchanged(true,"fixture_baseline",10)
 diagnostic(name,"mutate")
 mutate.call(f.node)
 diagnostic(name,"witness")
 var rejected: bool=not f.guard.unchanged(true,"late_process",11)
 record(name,baseline and rejected and not f.guard.failures.is_empty(),f.guard.failures)
 diagnostic(name,"restore_and_dispose")
 dispose_fixture(f)

func stable_empty(f: Dictionary, expected_reason: String, expected_floats: int) -> bool:
 var identity: Dictionary=f.watch.get("multimesh_identity",{})
 return f.baseline_ok and f.guard.unchanged(true,"late_process",11) and f.guard.unchanged(true,"physics",12) and identity.get("ok")==true and identity.get("mesh_binding_matches")==true and identity.non_rendered_reason==expected_reason and identity.has_drawable_bounds==false and identity.mesh_surface_count==null and identity.mesh_aabb_hex==null and identity.multimesh_aabb_hex==null and identity.buffer_float_count==expected_floats and identity.buffer_byte_count==4*expected_floats and (expected_floats!=0 or identity.buffer_sha256==EMPTY_SHA256) and f.watch.has_drawable_bounds==false and f.watch.bounds_position==null and f.watch.bounds_size==null and not f.watch.query_candidate and not f.watch.before.effective_query_candidate

func run() -> void:
 record("real_display_gl_backend_required",DisplayServer.get_name()=="X11" and RenderingServer.get_current_rendering_method()=="gl_compatibility" and RenderingServer.get_current_rendering_driver_name() in ["opengl3","opengl3_es","opengl3_angle"])
 scene=Node3D.new();root.add_child(scene)
 camera=Camera3D.new();scene.add_child(camera)
 var stable:=fixture()
 record("full_buffer_baseline_passes",stable.baseline_ok and stable.guard.unchanged(true,"late_process",10))
 record("actual_native_setter_getter_round_trip",stable.node.multimesh.get_instance_transform(1).origin==Vector3(2,0,0) and stable.node.multimesh.get_instance_color(0).is_equal_approx(Color.WHITE) and stable.node.multimesh.get_instance_custom_data(0).is_equal_approx(Color(0,0,0,0)))
 var identity: Dictionary=stable.watch.multimesh_identity
 record("identity_covers_all_transform_color_custom_slots",identity.ok and identity.bound and identity.instance_count==2 and identity.transform_format==MultiMesh.TRANSFORM_3D and identity.use_colors and identity.use_custom_data and identity.buffer_float_count==40 and identity.buffer_byte_count==160 and identity.buffer_sha256.length()==64 and identity.mesh_instance_id!=0 and identity.multimesh_instance_id!=0 and is_instance_id_valid(identity.mesh_instance_id) and is_instance_id_valid(identity.multimesh_instance_id) and instance_from_id(identity.mesh_instance_id)==stable.node.multimesh.mesh and instance_from_id(identity.multimesh_instance_id)==stable.node.multimesh and identity.mesh_binding_matches and identity.cpu_mesh_rid==identity.server_mesh_rid,identity)
 record("late_witness_is_explicit_and_frame_associated",stable.guard.last_identity_witness.get("ok")==true and stable.guard.last_identity_witness.phase=="late_process" and stable.guard.last_identity_witness.process_frame==10 and stable.guard.last_identity_witness.multimesh_full_buffer_count==1,stable.guard.last_identity_witness)
 check_guard("actual_transform_mutation_rejected",func(n): n.multimesh.set_instance_transform(1,Transform3D(Basis.IDENTITY,Vector3(3,0,0))))
 check_guard("actual_color_buffer_mutation_rejected",func(n): n.multimesh.set_instance_color(0,Color.RED))
 check_guard("actual_custom_buffer_mutation_rejected",func(n): n.multimesh.set_instance_custom_data(0,Color(1,0,0,0)))
 check_guard("instance_count_mutation_rejected",func(n): n.multimesh.instance_count=1)
 check_guard("visible_count_mutation_rejected",func(n): n.multimesh.visible_instance_count=1)
 check_guard("null_multimesh_rebinding_rejected_without_dereference",func(n): n.multimesh=null)
 check_guard("equivalent_multimesh_resource_rebinding_rejected",func(n): n.multimesh=n.multimesh.duplicate())
 check_guard("mesh_binding_replacement_rejected",func(n): n.multimesh.mesh=BoxMesh.new())
 check_guard("null_mesh_binding_rejected_without_dereference",func(n): n.multimesh.mesh=null)
 check_guard("custom_aabb_mutation_rejected",func(n): n.multimesh.custom_aabb=AABB(Vector3.ONE*-10,Vector3.ONE*20))
 check_guard("hidden_buffer_mutation_is_not_exempt",func(n): n.multimesh.set_instance_custom_data(0,Color(1,0,0,0)),true)
 check_guard("outside_domain_buffer_mutation_is_not_exempt",func(n): n.multimesh.set_instance_custom_data(0,Color(1,0,0,0)),false,true)
 check_guard("hidden_visible_count_mutation_is_not_exempt",func(n): n.multimesh.visible_instance_count=0,true)
 check_guard("visibility_gate_retained",func(n): n.visible=false)
 check_guard("transform_gate_retained",func(n): n.position=Vector3(1,0,0))
 check_guard("queued_removal_gate_retained",func(n): n.queue_free())
 var missing:=fixture();missing.watch.erase("multimesh_identity")
 record("missing_baseline_is_rejected",not missing.guard.unchanged(true,"late_process",11))
 diagnostic("explicit_null_baseline_can_stay_null","begin")
 var null_case:=fixture(true,false,true)
 record("explicit_null_baseline_can_stay_null",null_case.baseline_ok and null_case.guard.unchanged(true,"late_process",11))
 diagnostic("null_to_bound_resource_change_is_rejected","mutate")
 null_case.node.multimesh=MultiMesh.new()
 record("null_to_bound_resource_change_is_rejected",not null_case.guard.unchanged(true,"late_process",12))
 dispose_fixture(null_case)
 var empty:=EmptyIdentity.new()
 record("empty_identity_cannot_be_accepted",not empty.bind_multimesh_identity(stable.watch))
 var transient:=fixture()
 var original: PackedFloat32Array=transient.node.multimesh.buffer
 transient.node.multimesh.set_instance_custom_data(0,Color(1,0,0,0))
 var late_rejected: bool=not transient.guard.unchanged(true,"late_process",11)
 transient.node.multimesh.buffer=original
 var final_equal: bool=transient.guard.unchanged(true,"final",12)
 record("late_mutation_rejected_even_when_final_buffer_restored",late_rejected and final_equal,transient.guard.failures)
 diagnostic("actual_removal_gate_retained","begin")
 var removed:=fixture()
 diagnostic("actual_removal_gate_retained","free_with_resources_retained")
 removed.node.free()
 record("actual_removal_gate_retained",not removed.guard.unchanged(true,"late_process",11))
 var fresh:=fixture(false,true)
 record("new_distant_MM_classified_and_watched",fresh.guard.accept_distant_new_node(fresh.node))
 fresh.node.multimesh.set_instance_custom_data(0,Color(1,0,0,0))
 record("new_distant_MM_later_mutation_rejected",not fresh.guard.unchanged(true,"late_process",12))

 diagnostic("fresh_empty_resource_has_empty_hash_and_no_coverage","begin")
 var fresh_empty:=fixture(false,false,false,"fresh")
 record("fresh_empty_resource_has_empty_hash_and_no_coverage",stable_empty(fresh_empty,"null_mesh",0),fresh_empty.watch.multimesh_identity)
 fresh_empty.node.multimesh.instance_count=1
 record("fresh_empty_count_change_is_rejected",not fresh_empty.guard.unchanged(true,"late_process",13))
 dispose_fixture(fresh_empty)
 diagnostic("zero_instance_bound_mesh_has_empty_hash_and_no_coverage","begin")
 var zero_instances:=fixture(false,false,false,"zero_instances")
 record("zero_instance_bound_mesh_has_empty_hash_and_no_coverage",stable_empty(zero_instances,"zero_instances",0),zero_instances.watch.multimesh_identity)
 zero_instances.node.multimesh.use_colors=false
 record("zero_instance_layout_change_is_rejected",not zero_instances.guard.unchanged(true,"late_process",13))
 dispose_fixture(zero_instances)
 diagnostic("never_bound_null_mesh_keeps_full_buffer_watch_without_coverage","begin")
 var never_bound:=fixture(false,false,false,"null_mesh")
 record("never_bound_null_mesh_keeps_full_buffer_watch_without_coverage",stable_empty(never_bound,"null_mesh",40),never_bound.watch.multimesh_identity)
 never_bound.node.multimesh.set_instance_custom_data(0,Color(1,0,0,0))
 record("null_mesh_full_buffer_mutation_is_rejected",not never_bound.guard.unchanged(true,"late_process",13))
 dispose_fixture(never_bound)
 diagnostic("zero_visible_instances_keep_full_buffer_watch_without_coverage","begin")
 var zero_visible:=fixture(false,false,false,"zero_visible")
 record("zero_visible_instances_keep_full_buffer_watch_without_coverage",stable_empty(zero_visible,"zero_visible_instances",40),zero_visible.watch.multimesh_identity)
 zero_visible.node.multimesh.visible_instance_count=1
 record("zero_visible_becoming_drawable_is_rejected",not zero_visible.guard.unchanged(true,"late_process",13))
 dispose_fixture(zero_visible)
 diagnostic("stale_cpu_null_binding_is_rejected_before_bounds","begin")
 var stale:=fixture()
 stale.node.multimesh.mesh=null
 var stale_binding: Dictionary=stale.guard.multimesh_binding_identity(stale.node)
 record("stale_cpu_null_binding_is_rejected_before_bounds",stale_binding.get("ok")==false and stale_binding.cpu_mesh_rid==0 and stale_binding.server_mesh_rid==stale.held_mesh.get_rid().get_id() and not stale.guard.bind_multimesh_identity(stale.watch),stale_binding)
 stale.node.multimesh.mesh=stale.held_mesh
 record("restored_cpu_server_binding_matches_original_identity",stale.guard.unchanged(true,"restored",14))
 dispose_fixture(stale)
 diagnostic("new_empty_binding_is_classified_without_finite_coverage","begin")
 var new_empty:=fixture(false,false,false,"fresh")
 new_empty.guard.watches.clear()
 record("new_empty_binding_is_classified_without_finite_coverage",new_empty.guard.accept_distant_new_node(new_empty.node) and new_empty.guard.unchanged(true,"late_process",11) and new_empty.guard.watches.size()==1 and new_empty.guard.watches[0].bounds_position==null and not new_empty.guard.watches[0].query_candidate)
 new_empty.node.multimesh.mesh=BoxMesh.new()
 record("new_empty_mesh_binding_change_is_rejected",not new_empty.guard.unchanged(true,"late_process",12))
 # Freshly bound mesh must stay alive until the MM itself is released; restoring
 # a CPU-null mesh would deliberately recreate the pinned GLES3 stale-RID state.
 var new_empty_mesh: Mesh=new_empty.node.multimesh.mesh
 new_empty.node.free()
 record("new_empty_bound_mesh_retained_through_removal",is_instance_valid(new_empty_mesh))

 var seq=Sequence.new()
 record("sequence_initial_sample_audit",seq.sample(10) and seq.audit(10))
 record("begin_event_with_empty_pending",seq.begin_event(10))
 record("no_process_cannot_complete_event",not seq.event_ready())
 record("new_process_alone_cannot_complete_event",seq.sample(11) and not seq.event_ready())
 record("capture_cannot_precede_its_physics_audit",not seq.capture_ready(11))
 record("new_process_exact_audit_allows_next_event",seq.audit(11) and seq.event_ready() and seq.complete_event())
 record("capture_ready_only_after_same_frame_audit",seq.capture_ready(11))
 record("second_event_requires_newer_process_again",seq.begin_event(11) and not seq.event_ready() and seq.sample(12) and seq.audit(12) and seq.complete_event())
 record("later_capture_frame_cannot_pass_early",not seq.capture_ready(13) and seq.sample(13) and not seq.capture_ready(13) and seq.audit(13) and seq.capture_ready(13))
 var pending=Sequence.new();pending.sample(10)
 record("pending_segment_blocks_input",not pending.begin_event(10))
 var duplicate=Sequence.new();duplicate.sample(10)
 record("duplicate_process_frame_rejected",not duplicate.sample(10))
 var skipped=Sequence.new();skipped.sample(10)
 record("missing_process_frame_rejected",not skipped.sample(12))
 var wrong=Sequence.new();wrong.sample(10)
 record("wrong_segment_audit_rejected",not wrong.audit(11))
 var double_audit=Sequence.new();double_audit.sample(10);double_audit.audit(10)
 record("duplicate_audit_rejected",not double_audit.audit(10))
 var active=Sequence.new();active.begin_event(10)
 record("overlapping_input_event_rejected",not active.begin_event(10))
 var early=Sequence.new();early.begin_event(10)
 record("missing_process_complete_event_rejected",not early.complete_event())
 var same=Sequence.new();same.begin_event(10);same.sample(10);same.audit(10)
 record("same_frame_process_does_not_satisfy_strict_newer_requirement",not same.event_ready())
 var backlog=Sequence.new();backlog.begin_event(10);backlog.sample(11);backlog.sample(12);backlog.audit(11)
 record("unflushed_later_segment_blocks_next_input",not backlog.event_ready() and backlog.audit(12) and backlog.complete_event())
 var clocking=Telemetry.new();var t: int=clocking.begin("fixture_operation");clocking.end("fixture_operation",t);clocking.process(.01);clocking.process(.02)
 var timing: Dictionary=clocking.snapshot()
 record("telemetry_distinguishes_engine_delta_from_wall_and_never_accepts",timing.diagnostic_only and is_equal_approx(timing.engine_process_delta_seconds_sum,.03) and timing.timers.fixture_operation.calls==1 and timing.counters.late_process_callbacks==2 and timing.open_operation_elapsed_seconds.is_empty(),timing)
 scene.queue_free();await process_frame;await process_frame
 var result: Dictionary={"version":"orbit61-continuous-v6","engine":Engine.get_version_info(),"passed":not failed,"checks":checks,"display_backend":DisplayServer.get_name(),"rendering_method":RenderingServer.get_current_rendering_method(),"rendering_driver":RenderingServer.get_current_rendering_driver_name(),"world_loaded":false,"scope":"Small real-display GL compatibility fixture: actual native MultiMesh setters/readbacks and production sequence helpers only. No game/full world, game input, saved framebuffer, production timing or continuous orbit acceptance.","coverage_limit":"Mutation restored between all process/physics observations is not detected. Mesh same-resource contents/materials/ship geometry are not generally frozen by the MM guard."}
 var file:=FileAccess.open(output,FileAccess.WRITE)
 file.store_string(JSON.stringify(result,"  ")+"\n");file.close()
 print("ORBIT61_CONTINUOUS_V6 ",not failed," checks=",checks.size())
 quit(1 if failed else 0)

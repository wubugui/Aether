extends SceneTree
const Audit=preload("../visible_geometry61.gd")
const Lifecycle=preload("../fixture_lifecycle61.gd")

class EmptyClassification:
 extends "../visible_geometry61.gd"
 func classify_material(_material: Material) -> Dictionary:
  return {} # Same return shape as a failed Dictionary-returning GDScript call.

class NonfiniteClassification:
 extends "../visible_geometry61.gd"
 func classify_material(_material: Material) -> Dictionary:
  return {"ok":true,"expansion":NAN}

var checks:=[]
var failed:=false
var output: String

func record(name: String, ok: bool, details: Variant=null) -> void:
 checks.append({"name":name,"passed":ok,"details":details})
 if not ok: failed=true

func _initialize() -> void:
 output=OS.get_cmdline_user_args()[0]
 call_deferred("run")

func mesh_node(label: String, parent: Node3D, position: Vector3=Vector3.ZERO) -> MeshInstance3D:
 var node:=MeshInstance3D.new()
 node.name=label
 node.mesh=BoxMesh.new()
 node.position=position
 parent.add_child(node)
 return node

func run() -> void:
 var audit=Audit.new()
 var material:=StandardMaterial3D.new()
 record("null_material_explicit_zero",audit.material_expansion(null)==0.0)
 material.grow_amount=.25
 record("grow_disabled_despite_positive_amount",not material.is_grow_enabled() and audit.material_expansion(material)==0.0)
 material.grow=true
 record("grow_enabled_positive",material.is_grow_enabled() and audit.material_expansion(material)==.25)
 material.grow_amount=-.25
 record("grow_enabled_negative_absolute_envelope",audit.material_expansion(material)==.25)
 var empty=EmptyClassification.new()
 record("empty_classifier_result_fails_closed",empty.material_expansion(material)<0 and not empty.failures.is_empty(),empty.failures)
 var nonfinite=NonfiniteClassification.new()
 record("nonfinite_classifier_result_fails_closed",nonfinite.material_expansion(material)<0 and not nonfinite.failures.is_empty(),nonfinite.failures)
 material.grow=false
 material.next_pass=StandardMaterial3D.new()
 record("next_pass_still_rejected",audit.material_expansion(material)<0)
 material.next_pass=null
 material.billboard_mode=BaseMaterial3D.BILLBOARD_ENABLED
 record("billboard_still_rejected",audit.material_expansion(material)<0)
 var shader_material:=ShaderMaterial.new()
 shader_material.shader=Shader.new()
 shader_material.shader.code="shader_type spatial; void vertex(){ VERTEX.x += 1.0; }"
 record("unknown_vertex_assignment_still_rejected",audit.material_expansion(shader_material)<0)
 shader_material.shader.code="shader_type spatial; void vertex(){ POSITION = vec4(VERTEX, 1.0); }"
 record("unknown_position_override_still_rejected",audit.material_expansion(shader_material)<0)

 var scene:=Node3D.new()
 scene.name="FixtureLifecycleOnly"
 root.add_child(scene)
 var camera:=Camera3D.new()
 scene.add_child(camera)
 var stable:=mesh_node("StableNear",scene)
 var stable_pose:=stable.global_transform
 var retired:=Node3D.new()
 retired.name="RetiredTile"
 scene.add_child(retired)
 var old_geometry:=mesh_node("OldGeometry",retired)
 var old_id:=old_geometry.get_instance_id()
 var retired_id:=retired.get_instance_id()
 retired.queue_free()
 var lifecycle=Lifecycle.new()
 var snapshot: Dictionary=lifecycle.queued_snapshot(scene)
 record("queued_parent_identifies_nonqueued_geometry_descendant",snapshot.queued_nodes.size()==1 and snapshot.affected_geometry.size()==1 and not snapshot.affected_geometry[0].self_queued and snapshot.affected_geometry[0].instance_id==old_id and snapshot.affected_geometry[0].queued_ancestors[0].instance_id==retired_id,snapshot)
 var paused:=func() -> bool: return is_instance_valid(stable) and stable.global_transform==stable_pose
 var drained: Dictionary=await lifecycle.drain(scene,paused)
 record("fixture_drain_waits_for_actual_parent_and_geometry_deletion",drained.get("ok",false) and drained.waited_process_frames>=1 and not is_instance_id_valid(old_id) and not is_instance_id_valid(retired_id),drained)
 record("persistent_fixture_geometry_unchanged",is_instance_valid(stable) and stable.global_transform==stable_pose)
 var rejected: Dictionary=await lifecycle.drain(scene,func() -> bool: return false)
 record("changed_pause_guard_rejects_before_baseline",not rejected.get("ok",false),rejected)

 var guard=Audit.new()
 guard.owner_game={"camera":camera}
 guard.domain=AABB(Vector3.ONE*-5,Vector3.ONE*10)
 var near_bounds: AABB=guard.world_bounds(stable.get_aabb(),stable.global_transform)
 var watched: Dictionary=guard.watch_entry(stable,true,0.0,near_bounds)
 guard.watches.append(watched)
 record("post_drain_baseline_valid",guard.unchanged(true) and watched.query_candidate)
 var saved_path: String=watched.path
 var saved_id: int=watched.instance_id
 stable.queue_free()
 record("baseline_queued_deletion_rejected_with_saved_identity",not guard.unchanged(true) and guard.failures[-1].details.path==saved_path and guard.failures[-1].details.instance_id==saved_id,guard.failures)
 await process_frame
 await process_frame
 guard.failures.clear()
 record("baseline_actual_deletion_rejected_with_saved_identity",not guard.unchanged(true) and guard.failures[-1].reason=="Inventoried geometry was removed" and guard.failures[-1].details.path==saved_path and guard.failures[-1].details.instance_id==saved_id,guard.failures)
 var far:=mesh_node("DistantStillWatched",scene,Vector3(1000,0,0))
 var far_guard=Audit.new()
 far_guard.owner_game={"camera":camera};far_guard.domain=guard.domain
 var far_watch: Dictionary=far_guard.watch_entry(far,true,0.0,far_guard.world_bounds(far.get_aabb(),far.global_transform))
 far_guard.watches.append(far_watch)
 far.free()
 record("distant_baseline_deletion_is_not_exempt",not far_watch.query_candidate and not far_guard.unchanged(true),far_guard.failures)
 var queued_parent:=Node3D.new()
 queued_parent.name="QueuedDistantParent";scene.add_child(queued_parent)
 var queued_child:=mesh_node("NewDistantChild",queued_parent,Vector3(1000,0,0))
 queued_parent.queue_free()
 var new_guard=Audit.new()
 new_guard.owner_game={"camera":camera};new_guard.domain=guard.domain
 record("new_geometry_under_queued_parent_is_rejected",not new_guard.accept_distant_new_node(queued_child),new_guard.failures)
 scene.queue_free()
 await process_frame
 await process_frame
 var result: Dictionary={"version":"orbit61-material-lifecycle-v3","engine":Engine.get_version_info(),"passed":not failed,"checks":checks,"scope":"Synthetic material and node-lifecycle fixture only. No game/world resource, MultiMesh access, input events, render or orbit claim."}
 var file:=FileAccess.open(output,FileAccess.WRITE)
 file.store_string(JSON.stringify(result,"  ")+"\n");file.close()
 print("ORBIT61_MATERIAL_LIFECYCLE ",not failed," checks=",checks.size())
 quit(1 if failed else 0)

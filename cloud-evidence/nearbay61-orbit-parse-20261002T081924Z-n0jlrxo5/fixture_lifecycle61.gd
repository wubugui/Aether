extends RefCounted
## Only drains deletions already produced by the explicit orbit fixture.
## Does not pause processing, change a node, or exempt later inventory changes.
const MAX_PROCESS_FRAMES := 8
const MAX_WALL_MSEC := 15000

func identity(node: Node) -> Dictionary:
 return {"path":str(node.get_path()),"instance_id":node.get_instance_id(),"class":node.get_class()}

func queued_snapshot(scene_root: Node) -> Dictionary:
 var nodes: Array[Node]=[scene_root]
 nodes.append_array(scene_root.find_children("*","",true,false))
 var queued:=[]
 var geometry:=[]
 for node in nodes:
  if node.is_queued_for_deletion(): queued.append(identity(node))
  if not node is GeometryInstance3D: continue
  var ancestors:=[]
  var parent: Node=node
  while parent!=null:
   if parent.is_queued_for_deletion(): ancestors.append(identity(parent))
   if parent==scene_root: break
   parent=parent.get_parent()
  if not ancestors.is_empty():
   var row:=identity(node)
   row.queued_ancestors=ancestors
   row.self_queued=node.is_queued_for_deletion()
   geometry.append(row)
 return {"queued_nodes":queued,"affected_geometry":geometry,"process_frame":Engine.get_process_frames(),"physics_frame":Engine.get_physics_frames()}

func drain(scene_root: Node, paused_fixture_unchanged: Callable) -> Dictionary:
 var began:=Time.get_ticks_msec()
 var tracked: Dictionary={}
 var samples:=[]
 var report: Dictionary={"ok":false,"max_process_frames":MAX_PROCESS_FRAMES,"max_wall_msec":MAX_WALL_MSEC,"samples":samples,"waited_process_frames":0,"wall_msec":0}
 var tree: SceneTree=scene_root.get_tree()
 for step in range(MAX_PROCESS_FRAMES+1):
  report.waited_process_frames=step
  report.wall_msec=Time.get_ticks_msec()-began
  if not is_instance_valid(scene_root) or not paused_fixture_unchanged.call():
   report.reason="Native paused fixture changed while draining queued deletions"
   return report
  var snapshot:=queued_snapshot(scene_root)
  samples.append(snapshot)
  for row in snapshot.queued_nodes+snapshot.affected_geometry: tracked[row.instance_id]=row
  var still_alive:=[]
  for id in tracked:
   if is_instance_id_valid(id): still_alive.append(tracked[id])
  report.tracked_identities=tracked.values()
  report.still_alive=still_alive
  if report.wall_msec>=MAX_WALL_MSEC:
   report.reason="Fixture queued deletion drain exceeded its bounded wall wait"
   return report
  # At least one actual process boundary; no guessed fixed delay or forced free.
  if step>0 and still_alive.is_empty() and snapshot.queued_nodes.is_empty() and snapshot.affected_geometry.is_empty():
   report.ok=true
   report.reason="All recorded fixture queued nodes and geometry descendants are actually gone"
   return report
  if step==MAX_PROCESS_FRAMES or report.wall_msec>=MAX_WALL_MSEC:
   report.reason="Fixture queued deletion drain exceeded its bounded wait"
   return report
  await tree.process_frame
 return report

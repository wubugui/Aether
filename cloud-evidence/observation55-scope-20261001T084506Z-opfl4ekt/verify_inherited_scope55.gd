extends SceneTree
const BASE := "res://scenes/candidate53d-west/Game53dWest.tscn"
const CANDIDATE := "res://scenes/candidate55-observation/Game55Observation.tscn"
const AUDIT = preload("res://tools/reflection51b_saved_audit.gd")
var output := OS.get_environment("OBSERVATION55_OUT")
var checks: Array = []
func _initialize(): call_deferred("run")
func check(ok: bool, label: String, detail: Variant = null):
 checks.append({"passed":ok,"label":label,"detail":detail})
 if not ok: push_error(label)
func effective_graph(game: Node) -> Dictionary:
 var result := {"order":[],"owners":{},"groups":{},"connections":[],"scene_paths":{}}
 var nodes: Array[Node]=[game]
 nodes.append_array(game.find_children("*","",true,false))
 for node in nodes:
  var path := str(game.get_path_to(node))
  result.order.append(path)
  result.owners[path]=str(game.get_path_to(node.owner)) if node.owner else "<none>"
  var groups := []
  for group in node.get_groups():
   if node.is_in_group(group): groups.append(str(group))
  groups.sort(); result.groups[path]=groups
  if node!=game: result.scene_paths[path]=node.scene_file_path
  for signal_info in node.get_signal_list():
   for connection in node.get_signal_connection_list(signal_info.name):
    if not (int(connection.flags) & Object.CONNECT_PERSIST): continue
    var callback: Callable=connection.callable
    var target: Object=callback.get_object()
    var target_path := str(game.get_path_to(target)) if target is Node else str(target.get_class())
    result.connections.append([path,str(signal_info.name),target_path,str(callback.get_method()),connection.flags,callback.get_bound_arguments(),callback.get_unbound_arguments_count()])
 result.connections.sort_custom(func(a,b):return str(a)<str(b))
 return result
func run():
 var audit = AUDIT.new()
 audit.property_masks={".":["script","improved_lake_observation"]}
 var packed: PackedScene=load(BASE)
 var original: Node=packed.instantiate()
 var base_state: Dictionary=audit.snapshot(original)
 var base_graph: Dictionary=effective_graph(original)
 var base_count := base_state.size()
 for i in range(3):await process_frame
 await RenderingServer.frame_post_draw
 original.free(); packed=null
 audit.resource_cache.clear()
 var candidate_packed: PackedScene=load(CANDIDATE)
 var game: Node=candidate_packed.instantiate()
 var candidate_state: Dictionary=audit.snapshot(game)
 var changed := []
 for path in base_state:
  if not candidate_state.has(path) or base_state[path]!=candidate_state[path]: changed.append(path)
 for path in candidate_state:
  if not base_state.has(path):changed.append(path)
 check(base_state==candidate_state,"Every stored property and exact MultiMesh buffer unchanged except root script/opt-in export",changed)
 var graph: Dictionary=effective_graph(game)
 check(base_graph==graph,"Effective inherited node order, owners, actual groups, persistent connections and child scene paths unchanged")
 check(game.get_script().resource_path=="res://scripts/game55_observation.gd" and game.improved_lake_observation,"Only intended root subclass is active")
 var state := candidate_packed.get_state()
 check(state.get_base_scene_state()!=null,"Native scene inheritance retains original53west base")
 var weather := {}
 for pair in [["Rain",1800],["Snow",1200]]:
  var mm:MultiMesh=game.get_node("Weather42b/"+pair[0]).multimesh
  var valid:bool=mm.instance_count==pair[1] and mm.buffer.size()==pair[1]*16 and mm.get_instance_transform(0).basis.determinant()!=0
  weather[pair[0]]={"count":mm.instance_count,"floats":mm.buffer.size(),"valid":valid}
  check(valid,"Real renderer retains saved "+pair[0]+" buffers")
 for i in range(3):await process_frame
 await RenderingServer.frame_post_draw
 game.free();candidate_packed=null;audit=null
 for i in range(8):await process_frame
 var passed:=true
 for row in checks:passed=passed and row.passed
 var report := {"checks":checks,"node_count":base_count,"weather":weather,"passed_provisional":passed,"visual_acceptance":false,"scope":"Native inherited scene readback, no scene tree startup or saved world mutation"}
 FileAccess.open(output.path_join("scope-report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
 quit(0 if passed else 1)

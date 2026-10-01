extends "res://tools/reflection51b_saved_audit.gd"
## Only four named added leaves, one collider's faces, and120 translation slots may differ.
var added_paths := {}
func snapshot(game: Node, mask_edits := true) -> Dictionary:
 var out: Dictionary=super.snapshot(game,mask_edits)
 if not mask_edits:return out
 for path in added_paths:out.erase(path)
 for path in scatter_edits:
  var mm:MultiMesh=game.get_node(path).multimesh
  var buffer:PackedFloat32Array=mm.buffer
  var stride:=12+(4 if mm.use_colors else 0)+(4 if mm.use_custom_data else 0)
  for index in scatter_edits[path]:
   for offset in [3,7,11]:buffer[int(index)*stride+offset]=0.0
  # Replace the inherited broad mask with translation-only float masking.
  out[path].exact_multimesh_buffer=digest(buffer)
 return out
func graph_state(game:Node,packed:PackedScene,mask_new:=true)->Dictionary:
 var out:Dictionary=super.graph_state(game,packed,mask_new)
 if mask_new:
  var order:=[]
  for path in out.order:
   if not added_paths.has(path):order.append(path)
  out.order=order
  for field in ["owners","groups","scene_paths"]:
   for path in added_paths:out[field].erase(path)
 out.packed_resource_flags=resource_except(packed,["_bundled"])
 return out
func full_snapshot(game:Node)->Dictionary:return super.snapshot(game,false)
func exact_changes(a:Dictionary,b:Dictionary)->Dictionary:
 var out:={"removed_nodes":[],"added_nodes":[],"changed_properties":[]}
 for path in a:
  if not b.has(path):out.removed_nodes.append(path);continue
  for key in a[path]:
   if not b[path].has(key) or a[path][key]!=b[path][key]:out.changed_properties.append({"path":path,"property":key})
  for key in b[path]:
   if not a[path].has(key):out.changed_properties.append({"path":path,"property":key})
 for path in b:
  if not a.has(path):out.added_nodes.append(path)
 out.removed_nodes.sort();out.added_nodes.sort()
 return out
func source_transform(n:Node)->Transform3D:
 var chain:=[]
 while n!=null:chain.push_front(n);n=n.get_parent()
 var result:=Transform3D.IDENTITY
 for item in chain:
  if item is Node3D:result=result*item.transform
 return result
func weather_state(g:Node)->Dictionary:
 resource_cache.clear();var out:={}
 for pair in [["Rain",1800],["Snow",1200]]:
  var mm:MultiMesh=g.get_node("Weather42b/"+pair[0]).multimesh
  out[pair[0]]={"count":mm.instance_count,"floats":mm.buffer.size(),"valid":mm.instance_count==pair[1] and mm.buffer.size()==pair[1]*16 and mm.get_instance_transform(0).basis.determinant()!=0,"buffer_sha256":digest(mm.buffer),"canonical":canonical(mm)}
 return out
func material_bindings(g:Node)->Dictionary:
 resource_cache.clear();var out:={};var report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://scenes/candidate51b/build-report-51b.json"))
 for row in report.binding_ledger:
  var m:Material=g.get_node(row.path).get(row.property)
  out[row.path+"|"+row.property]=[m.resource_path,canonical(m),m.shader.resource_path if m is ShaderMaterial else ""]
 var paths:=[]
 for m in g.get_node(CTRL).get("clipping_materials"):paths.append(m.resource_path)
 out.controller_exact_clipping_paths=paths
 return out

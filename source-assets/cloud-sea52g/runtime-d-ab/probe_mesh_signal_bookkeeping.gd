extends SceneTree
func rows(node:Node)->Array:
 var out:=[]
 for c in node.get_incoming_connections():
  out.append({"source":c.signal.get_object_id(),"signal":str(c.signal.get_name()),"target":c.callable.get_object_id(),"method":str(c.callable.get_method()),"flags":c.flags,"unbind":c.callable.get_unbound_arguments_count()})
 return out
func _initialize()->void:
 var node:=MeshInstance3D.new();var a:=BoxMesh.new();var b:=SphereMesh.new()
 node.mesh=a;var before:=rows(node);node.mesh=b;var after:=rows(node);node.mesh=a;var restored:=rows(node)
 print(JSON.stringify({"original_mesh_id":a.get_instance_id(),"replacement_mesh_id":b.get_instance_id(),"A":before,"B":after,"A2":restored,"restored_exact":before==restored},"  "))
 node.free();quit(0)

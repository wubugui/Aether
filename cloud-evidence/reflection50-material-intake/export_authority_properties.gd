extends SceneTree
func _initialize():
 var state=load('res://scenes/candidate49/Game49.tscn').get_state();var rows=[]
 for i in state.get_node_count():
  var path=str(state.get_node_path(i)).trim_prefix('./')
  for j in state.get_node_property_count(i):
   var value=state.get_node_property_value(i,j)
   if value is Material:
    var row={'node_path':path,'property':str(state.get_node_property_name(i,j)),'class':value.get_class(),'resource_path':value.resource_path,'instance_id':value.get_instance_id(),'resource_name':value.resource_name}
    if value is ShaderMaterial:row['shader_sha256']=value.shader.code.sha256_text();row['shader_code']=value.shader.code
    rows.append(row)
 var f=FileAccess.open('/workspace/scratch/a29d03198654/Aether/cloud-evidence/reflection50-material-intake/saved49-material-properties.json',FileAccess.WRITE);f.store_string(JSON.stringify(rows,'  '));f.close()
 print('STORED MATERIAL BINDINGS ',rows.size());quit()

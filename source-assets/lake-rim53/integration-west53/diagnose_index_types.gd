extends SceneTree
func _initialize():
 var d="/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53/integration-west53/"
 var p=JSON.parse_string(FileAccess.get_file_as_string(d+"integration-payload.json"));var m=JSON.parse_string(FileAccess.get_file_as_string(d+"integration-manifest.json"));var groups={}
 for e in p.scatter:
  if not groups.has(e.node_path):groups[e.node_path]={}
  groups[e.node_path][int(e.index)]=true
 var total=0
 for path in groups:
  var actual=groups[path].keys();actual.sort();var raw=m.scatter_groups[path];var normalized=[];var integral=true
  for value in raw:
   integral=integral and is_finite(value) and value==float(int(value));normalized.append(int(value))
  print(JSON.stringify({"path":path,"actual_type":typeof(actual[0]),"manifest_type":typeof(raw[0]),"actual_count":actual.size(),"manifest_count":raw.size(),"raw_equal":actual==raw,"integral":integral,"normalized_equal":actual==normalized,"actual":actual,"expected_normalized":normalized}))
  total+=actual.size()
 print("TOTAL ",total);quit()

extends SceneTree
const SOURCE="res://scenes/candidate53d-west/Game53dWest.tscn"
const OUT="/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/intake/cirque-saved53-native-attributes.json"
func _initialize():
 var packed=load(SOURCE);var saved=packed.instantiate();var node=saved.get_node("World/Mountains/massif_cirque_wall/Model/massif_cirque_wall");var mesh=node.mesh;var surfaces=[]
 var path=[];var current=node
 while current!=null:
  if current is Node3D:path.push_front(current.transform)
  current=current.get_parent()
 var transform=Transform3D.IDENTITY
 for local in path:transform=transform*local
 for s in mesh.get_surface_count():
  var a=mesh.surface_get_arrays(s);var rows=[];var indices=a[Mesh.ARRAY_INDEX]
  for i in (indices.size() if indices!=null and indices.size()>0 else a[Mesh.ARRAY_VERTEX].size()):
   var vi=indices[i] if indices!=null and indices.size()>0 else i;var p=transform*a[Mesh.ARRAY_VERTEX][vi];var n=a[Mesh.ARRAY_NORMAL][vi];var c=a[Mesh.ARRAY_COLOR][vi]
   rows.append({"position":[p.x,p.y,p.z],"normal":[n.x,n.y,n.z],"color":[c.r,c.g,c.b,c.a]})
  surfaces.append({"index":s,"triangles":rows.size()/3,"expanded_attributes":rows})
 var f=FileAccess.open(OUT,FileAccess.WRITE);f.store_string(JSON.stringify({"source":SOURCE,"source_sha256":FileAccess.get_sha256(SOURCE),"surfaces":surfaces}));f.close();print("CIRQUE_ATTRIBUTES_EXPORTED ",surfaces.size());saved.free();packed=null;quit()

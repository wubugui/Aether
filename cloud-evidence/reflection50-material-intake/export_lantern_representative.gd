extends SceneTree
func _initialize():
 var packed=load('res://scenes/candidate49/Game49.tscn')
 var material=load('res://scenes/candidate49/Game49.tscn::StandardMaterial3D_em4ct') as StandardMaterial3D
 if material==null:push_error('Missing exact stored lantern material');quit(1);return
 var feature={}
 for prop in material.get_property_list():
  var key=str(prop.name)
  if prop.usage & PROPERTY_USAGE_STORAGE and key not in ['resource_path','resource_name','resource_local_to_scene','script','albedo_color']:feature[key]=encoded(material.get(key))
 var sha=JSON.stringify(feature).sha256_text()
 if sha!='f6f9fba84836f2ed0b40104a75a4ec4574e97ddd7aa51b7a5825a12a41584a3a':push_error('Lantern exact feature mismatch '+sha);quit(2);return
 var path='res://assets/reflection50_intake/native_group_04_lantern.tres'
 if FileAccess.file_exists(path):push_error('Refuse overwrite '+path);quit(3);return
 var err=ResourceSaver.save(material.duplicate(false),path)
 print('LANTERN REPRESENTATIVE ',sha,' saved=',err,' source49=',FileAccess.get_sha256('res://scenes/candidate49/Game49.tscn'))
 quit(0 if err==OK else 4)
func encoded(value):
 if value is Resource:return {"type":value.get_class(),"path":value.resource_path}
 if value is Color:return [value.r,value.g,value.b,value.a]
 if value is Vector2:return [value.x,value.y]
 if value is Vector3:return [value.x,value.y,value.z]
 if value is Vector4:return [value.x,value.y,value.z,value.w]
 if value is Dictionary:
  var d={}
  for k in value:d[str(k)]=encoded(value[k])
  return d
 if value is Array:
  var a=[]
  for v in value:a.append(encoded(v))
  return a
 return value

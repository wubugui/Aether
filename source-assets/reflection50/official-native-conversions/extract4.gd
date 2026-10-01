extends SceneTree
func _initialize():
 var inventory=[]
 for i in range(4,5):
  var source="res://holder%02d.tres"%i
  var h=load(source)
  var m=h.get("material")
  if not m is ShaderMaterial:push_error("Official conversion missing");quit(1);return
  var target="res://outputs/native_group_%02d_shader.tres"%i
  if FileAccess.file_exists(target):push_error("Refuse overwrite");quit(1);return
  if ResourceSaver.save(m,target)!=OK:quit(1);return
  var shader_path="res://outputs/native_group_%02d.gdshader"%i
  var f=FileAccess.open(shader_path,FileAccess.WRITE);f.store_string(m.shader.code);f.close()
  inventory.append({"group":i,"holder_sha256":FileAccess.get_sha256(source),"material_sha256":FileAccess.get_sha256(target),"shader_sha256":FileAccess.get_sha256(shader_path),"method":"Official Godot4.5.1 Inspector Convert to ShaderMaterial; saved holder then extracted original generated resource"})
 var f=FileAccess.open("res://outputs/conversion-manifest-group04.json",FileAccess.WRITE);f.store_string(JSON.stringify(inventory,"  "));f.close();print(JSON.stringify(inventory));quit()

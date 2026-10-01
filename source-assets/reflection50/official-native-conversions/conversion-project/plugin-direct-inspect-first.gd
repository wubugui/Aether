@tool
extends EditorPlugin
var index := 1
var waiting := false
var source: StandardMaterial3D
func _enter_tree():call_deferred("stage")
func stage():
 if index>3:
  print("ALL THREE OFFICIAL CONVERSIONS CAPTURED")
  set_process(false)
  return
 var path="res://inputs/native_group_%02d.tres"%index
 source=load(path).duplicate(true)
 source.resource_name="CONVERT GROUP %02d USING INSPECTOR MENU"%index
 EditorInterface.inspect_object(source)
 waiting=true
 print("AWAITING OFFICIAL UI CONVERT ",index)
func _process(_delta):
 if not waiting:return
 var edited=EditorInterface.get_inspector().get_edited_object()
 if edited is ShaderMaterial:
  waiting=false
  var path="res://outputs/native_group_%02d_shader.tres"%index
  if FileAccess.file_exists(path):push_error("Refuse overwrite captured conversion");set_process(false);return
  var error=ResourceSaver.save(edited,path)
  if error!=OK:push_error("Save conversion failed");set_process(false);return
  var shader_path="res://outputs/native_group_%02d.gdshader"%index
  var f=FileAccess.open(shader_path,FileAccess.WRITE);f.store_string(edited.shader.code);f.close()
  print("OFFICIAL CONVERSION SAVED ",index," ",path," shader ",edited.shader.code.sha256_text())
  index+=1
  call_deferred("stage")

extends SceneTree
func _initialize():
 var shader=load('res://assets/reflection51/lake_water_reflection51.gdshader') as Shader
 var ledger=JSON.parse_string(FileAccess.get_file_as_string('/workspace/scratch/a29d03198654/Aether/source-assets/reflection51/water-shader-ledger.json'))
 if shader==null or shader.code.sha256_text()!=ledger.reflection51_shader_sha256:push_error('51 water shader source hash mismatch');quit(1);return
 var base=shader.code.replace(ledger.global_insertion,'').replace(ledger.normal_insertion,'').replace(ledger.fragment_tail_insertion,'')
 if base.sha256_text()!=ledger.base_depth50_shader_sha256:push_error('51 water source not reversible to50');quit(2);return
 var original=load('res://assets/lake_depth50/water_depth_shader.tres') as Shader
 if original==null or original.code!=base:push_error('51 base differs from actual saved50 shader');quit(3);return
 var new_list=shader.get_shader_uniform_list();var old_list=original.get_shader_uniform_list();var by_name={}
 for u in new_list:by_name[str(u.name)]=u
 for u in old_list:
  if not by_name.has(str(u.name)) or by_name[str(u.name)]!=u:push_error('Changed old uniform schema '+str(u.name));quit(4);return
 var controller=load('res://scripts/lake_reflection51.gd').new()
 for axis in [Vector3.RIGHT,Vector3.UP,Vector3.FORWARD]:
  if controller.reflected_y(controller.reflected_y(axis))!=axis:push_error('Reflection involution failed');quit(5);return
 controller.free()
 print('REFLECTION51 source/actual50 reverse/old uniform schema/pose reflection helper passed (no GUI, no saved scene): old=',old_list.size(),' new=',new_list.size())
 quit(0)

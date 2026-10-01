extends SceneTree
## Four bare Node3D controls only. No project scene, world, mesh, collision or renderer.
var camera:Node3D
var ship:Node3D
var plan:Dictionary={}
var lake:Dictionary
var cloud:Dictionary
var rows:Array=[]
var results:Dictionary={}
func _initialize():call_deferred("run")
func state()->Dictionary:
 return {"camera_hex":var_to_bytes(camera.transform).hex_encode(),"ship_hex":var_to_bytes(ship.transform).hex_encode(),"camera_rotation_hex":var_to_bytes(camera.rotation).hex_encode(),"camera_scale_hex":var_to_bytes(camera.scale).hex_encode(),"camera_scale":[camera.scale.x,camera.scale.y,camera.scale.z]}
func note(label:String):
 var item=state();item.label=label;rows.append(item)
func observe(id:String):
 var info:Dictionary=plan[id].camera
 camera.position=Vector3(info.x,info.y_abs,info.z);camera.look_at(Vector3(info.tx,info.ty_abs,info.tz))
 ship.rotation.y=float(plan[id].airship.yaw)
 if id=="1128":
  camera.position.y=float(lake.camera_y);var angles=camera.rotation;angles.x=deg_to_rad(float(lake.camera_pitch_degrees));camera.rotation=angles
  var a=ship.rotation;a.y=float(lake.ship_yaw);ship.rotation=a;ship.position=Vector3(lake.ship_position[0],lake.ship_position[1],lake.ship_position[2])
 elif id=="1216":
  var a=ship.rotation;a.y=float(cloud.ship_yaw);ship.rotation=a;ship.position=Vector3(cloud.ship_position[0],cloud.ship_position[1],cloud.ship_position[2])
 note("observe_"+id)
func reset_nodes():
 if is_instance_valid(camera):camera.free();ship.free()
 camera=Node3D.new();ship=Node3D.new();root.add_child(camera);root.add_child(ship)
 camera.transform=Transform3D(Basis(Vector3(1,0,0),Vector3(0,0.9981348,0.06104854),Vector3(0,-0.06104854,0.9981348)),Vector3(0,145,250))
 camera.rotation_degrees=Vector3(-3.5,0,0);ship.rotation_degrees=Vector3(0,13,0)
func save_camera()->Dictionary:return {"transform":camera.transform,"position":camera.position,"rotation":camera.rotation,"scale":camera.scale,"rotation_order":camera.rotation_order}
func restore_camera(saved:Dictionary):
 camera.transform=saved.transform;camera.rotation_order=saved.rotation_order;camera.rotation=saved.rotation;camera.scale=saved.scale;camera.position=saved.position
 assert(var_to_bytes(camera.transform)==var_to_bytes(saved.transform))
 assert(var_to_bytes(camera.rotation)==var_to_bytes(saved.rotation))
 assert(var_to_bytes(camera.scale)==var_to_bytes(saved.scale))
func result()->Dictionary:
 var out=state();out.camera_exact=out.camera_hex==lake.expected_camera_transform_hex;out.ship_exact=out.ship_hex==lake.expected_ship_transform_hex
 out.expected_camera_hex=lake.expected_camera_transform_hex;out.expected_ship_hex=lake.expected_ship_transform_hex
 return out
func sequence(restore:bool):
 observe("1131")
 for ref in ["1131","1347"]:
  observe(ref);var saved=save_camera();var original=camera.global_transform
  for angle in [0.0,PI/2.0,PI]:
   var pose=original;pose.basis=original.basis.rotated(Vector3.UP,angle);camera.global_transform=pose;note(ref+"_angle_"+str(angle))
   if restore:restore_camera(saved);note(ref+"_restored")
 observe("1131");var saved=save_camera()
 for view in [[Vector3(-3470,26,-3620),Vector3(-3260,12,-3630)],[Vector3(-3075,145,-3895),Vector3(-3190,52,-3660)]]:
  camera.position=view[0];camera.look_at(view[1]);note("local_diagnostic")
  if restore:restore_camera(saved);note("local_restored")
 observe("1128")
func run():
 for entry in JSON.parse_string(FileAccess.get_file_as_string("res://assets/reference_views42.json")):plan[entry.ref]=entry
 lake=JSON.parse_string(FileAccess.get_file_as_string("res://assets/observation55/lake_observation_poses.json"))["1128"]
 cloud=JSON.parse_string(FileAccess.get_file_as_string("res://assets/observation60/cloud_observation_pose.json"))["1216"]
 reset_nodes();observe("1128");results.pristine=result()
 reset_nodes();observe("1216");observe("1216");observe("1128");observe("1128");results.control60=result()
 reset_nodes();sequence(false);results.original61_sequence=result()
 reset_nodes();sequence(true);results.restored61_sequence=result()
 var out={"scope":"Bare Node3D arithmetic reproduction; no world, no mesh, no GUI. All original pose bytes remain the authority.","results":results,"trace":rows}
 var file=FileAccess.open(OS.get_environment("COAST61_PROBE_OUT"),FileAccess.WRITE);file.store_string(JSON.stringify(out,"  "));file.close()
 camera.free();ship.free();print("BARE_NODE61_PROBE_COMPLETE");quit(0)

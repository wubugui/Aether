extends SceneTree
func _initialize():
 call_deferred("run")
func run():
 var poses: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/observation55/lake_observation_poses.json"))
 var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/source-assets/observation55/camera-component-fixture.json"))
 var failures=[]
 for id in ["1128","1129"]:
  var camera=Camera3D.new();root.add_child(camera)
  var seed:Dictionary=fixture[id]
  camera.rotation_order=int(seed.rotation_order)
  camera.position=Vector3(seed.position[0],seed.position[1],seed.position[2])
  camera.rotation=Vector3(seed.rotation[0],seed.rotation[1],seed.rotation[2])
  camera.scale=Vector3(seed.scale[0],seed.scale[1],seed.scale[2])
  var pose:Dictionary=poses[id];var angles=camera.rotation
  camera.position.y=pose.camera_y;angles.x=deg_to_rad(pose.camera_pitch_degrees);camera.rotation=angles
  var ship=Node3D.new();root.add_child(ship);var v=pose.ship_position
  ship.position=Vector3(v[0],v[1],v[2]);ship.rotation=Vector3(0,pose.ship_yaw,0)
  var cam_exact=var_to_bytes(camera.transform).hex_encode()==pose.expected_camera_transform_hex
  var ship_exact=var_to_bytes(ship.transform).hex_encode()==pose.expected_ship_transform_hex
  print(id," camera_exact=",cam_exact," ship_exact=",ship_exact," scale=",ship.scale)
  if not cam_exact or not ship_exact or ship.scale!=Vector3.ONE:failures.append(id)
  camera.free();ship.free()
 quit(0 if failures.is_empty() else 1)

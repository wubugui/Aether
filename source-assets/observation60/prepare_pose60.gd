extends SceneTree
const R:="/workspace/scratch/a29d03198654/Aether/"
func _initialize():call_deferred("run")
func run():
 var state:Dictionary=bytes_to_var(FileAccess.get_file_as_bytes(R+"cloud-evidence/observation59b-renderer-20261001T113543Z-g67v9sl9/images/states/1216--B-full.bin"))
 var expected:Transform3D
 var camera:Transform3D
 for row in state.nodes:
  if row.path=="Airship":expected=row.transform
  if row.path=="Camera":camera=row.transform
 var proposal:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(R+"source-assets/observation59-1216-plan/revision-b/proposal.json"))
 var seed:Dictionary=proposal.best_five[0]
 var body:=Node3D.new()
 var yaw:=Basis(Vector3.UP,deg_to_rad(seed.yaw_degrees)).get_euler(body.rotation_order).y
 body.position=Vector3(seed.position_world[0],seed.position_world[1],seed.position_world[2]);body.rotation=Vector3(0,yaw,0)
 var ok:=var_to_bytes(body.transform)==var_to_bytes(expected) and body.scale==Vector3.ONE
 print("POSE60_EXACT_59B ",ok)
 if not ok:body.free();quit(2);return
 var record:={"1216":{"ship_position":[body.position.x,body.position.y,body.position.z],"ship_yaw":yaw,"expected_ship_transform_hex":var_to_bytes(expected).hex_encode(),"expected_camera_transform_hex":var_to_bytes(camera).hex_encode(),"source_run":"observation59b-renderer-20261001T113543Z-g67v9sl9","scope":"Only ship local position/yaw. Original camera/FOV, full geometry/scale, all world state and existing1128/1129 lake poses remain. Limited composition improvement, not reference acceptance."}}
 var f:=FileAccess.open("res://assets/observation60/cloud_observation_pose.json",FileAccess.WRITE);f.store_string(JSON.stringify(record,"  ",true,true));f.close();body.free();quit()

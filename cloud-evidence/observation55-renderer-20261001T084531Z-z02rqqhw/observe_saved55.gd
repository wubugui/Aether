extends "res://tools/observe_camera_ship53west_c.gd"
var pose_rows := []
func write_report(complete: bool) -> void:
 if output.is_empty():return
 var report := {"version":"55-native-inherited-observation","complete":complete,"stage":stage,"failures":failures,"checks":checks,"captures":captures,"poses":pose_rows,"passed_provisional":complete and failures.is_empty() and pose_rows.size()==2,"visual_acceptance":false,"scope":"Read saved independent inherited55 scene, real same-world main and water reflection. Toggle original observation fallback. No flight claim."}
 FileAccess.open(output.path_join("observation55-report.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"\t"))
func run() -> void:
 if not output.is_absolute_path() or DirAccess.dir_exists_absolute(output):quit(2);return
 DirAccess.make_dir_recursive_absolute(output)
 root.size=Vector2i(1180,664)
 game=load("res://scenes/candidate55-observation/Game55Observation.tscn").instantiate()
 root.add_child(game);game.test_frozen=true
 await frames(8);await RenderingServer.frame_post_draw
 controller=game.get_node("World/LakeReflection51")
 freeze(game);await physics_frame
 var poses:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/observation55/lake_observation_poses.json"))
 measurements=JSON.parse_string(FileAccess.get_file_as_string(C_DIR+"reference-main-and-mirror-measurements.json"))
 for reference in ["1128","1129"]:
  current_reference=reference
  game.improved_lake_observation=false
  game.observe_reference(reference)
  var original_camera55:Transform3D=game.camera.transform
  var original_ship55:Transform3D=game.airship.transform
  var original_heading55:float=game.heading
  var original_scale55:Vector3=game.camera.scale
  game.improved_lake_observation=true
  game.observe_reference(reference)
  var weather=game.get_node("Weather42b")
  weather.seek_time(0.0);weather.seek_time(0.35);weather._process(0.0)
  RenderingServer.global_shader_parameter_set("world_time",0.35)
  controller.refresh_now();await frames(3);await physics_frame
  check(var_to_bytes(game.airship.transform).hex_encode()==poses[reference].expected_ship_transform_hex,"Saved55 exact C ship transform "+reference)
  check(var_to_bytes(game.camera.transform).hex_encode()==poses[reference].expected_camera_transform_hex,"Saved55 exact C camera transform "+reference)
  check(game.camera.scale==original_scale55 and game.airship.scale==Vector3.ONE,"Saved55 preserves original camera and ship scale "+reference)
  check(game.heading==game.airship.rotation.y-deg_to_rad(13),"Saved55 synchronizes ordinary flight heading "+reference)
  if not collect_ship():await finish();return
  var body:=clearance(game.airship.global_transform)
  var water:=camera_and_water_clearance({"ship_pose":game.airship.global_transform,"camera_pose":game.camera.global_transform})
  var capture55:=await capture(reference,"saved55")
  check(body.passed and water.passed and capture55.both_full_ship_and_mirror_inside_frusta,"Saved55 full ship mirror and physical clearance "+reference,{"body":body,"water":water})
  var saved_camera:Transform3D=game.camera.transform
  var saved_ship:Transform3D=game.airship.transform
  game.improved_lake_observation=false;game.observe_reference(reference)
  check(game.camera.transform==original_camera55 and game.airship.transform==original_ship55 and game.heading==original_heading55,"Disabled option restores original native observation "+reference)
  game.improved_lake_observation=true;game.observe_reference(reference)
  check(game.camera.transform==saved_camera and game.airship.transform==saved_ship,"Repeated saved observation is exact "+reference)
  pose_rows.append({"reference":reference,"body":body,"water":water,"saved_camera_transform":str(saved_camera),"saved_ship_transform":str(saved_ship),"full_visibility":capture55.both_full_ship_and_mirror_inside_frusta})
 await finish()

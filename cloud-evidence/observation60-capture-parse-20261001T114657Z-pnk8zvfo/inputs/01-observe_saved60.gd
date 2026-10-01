extends "res://tools/observe_camera_ship53west_c.gd"
var pose_rows60:=[]
var repeated60:={}
func write_report(complete:bool)->void:
 if output.is_empty():return
 var report:={"version":"60-native-observation","complete":complete,"stage":stage,"checks":checks,"failures":failures,"captures":captures,"poses":pose_rows60,"repeat":repeated60,"passed_provisional":complete and failures.is_empty() and pose_rows60.size()==3,"world":"Native60 inherits56 coast and55/53west lakes, not52f research clouds","visual_acceptance":false,"hardware_gpu_acceptance":false,"flight_tested":false,"scene_saved_by_verifier":false}
 FileAccess.open(output.path_join("report60.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
func cloud_clear60()->Dictionary:
 var box:AABB=game.airship.global_transform*visual_box
 var hits60:=[];var count:=0
 for parent in game.get_node("SkyRegion39").get_children():
  if not str(parent.name).begins_with("CloudSea_"):continue
  for mesh in parent.find_children("*","MeshInstance3D",true,false):
   if mesh.mesh:
    count+=1
    if box.intersects(mesh.global_transform*mesh.mesh.get_aabb()):hits60.append(str(game.get_path_to(mesh)))
 return {"passed":count==25 and hits60.is_empty(),"actual_original_cloud_meshes":count,"conservative_overlap_paths":hits60,"scope":"Full padded boat/propeller AABB separate from original25CloudSea bounds; no failed52f cloud merge"}
func settle60()->void:
 var weather=game.get_node("Weather42b");weather.seek_time(0.0);weather.seek_time(0.35);weather._process(0.0)
 RenderingServer.global_shader_parameter_set("world_time",0.35);controller.refresh_now();await frames(3);await physics_frame
func run()->void:
 if not output.is_absolute_path() or DirAccess.dir_exists_absolute(output):quit(2);return
 DirAccess.make_dir_recursive_absolute(output)
 source_hashes=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("OBSERVATION60_INPUTS")))
 for path in source_hashes:
  if not check(FileAccess.get_sha256(path)==source_hashes[path],"Pinned input "+path):await finish();return
 root.size=Vector2i(1180,664)
 game=load("res://scenes/candidate60-observation/Game60Observation.tscn").instantiate();root.add_child(game);game.test_frozen=true
 await frames(8);await RenderingServer.frame_post_draw
 controller=game.get_node("World/LakeReflection51");freeze(game);await physics_frame
 var cloud_pose:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/observation60/cloud_observation_pose.json"))["1216"]
 var lakes:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/observation55/lake_observation_poses.json"))
 for reference in ["1216","1128","1129"]:
  current_reference=reference
  game.improved_cloud_observation=false;game.observe_reference(reference);await settle60()
  var base_camera:Transform3D=game.camera.transform;var base_ship:Transform3D=game.airship.transform;var base_heading:float=game.heading
  var original_camera_scale:Vector3=game.camera.scale;var original_ship_scale:Vector3=game.airship.scale
  game.improved_cloud_observation=true;game.observe_reference(reference);await settle60()
  var expected:Dictionary=cloud_pose if reference=="1216" else lakes[reference]
  if not check(var_to_bytes(game.airship.transform).hex_encode()==expected.expected_ship_transform_hex and var_to_bytes(game.camera.transform).hex_encode()==expected.expected_camera_transform_hex,"Exact accepted-study ship/camera transforms "+reference):await finish();return
  if not check(game.airship.scale==original_ship_scale and game.camera.scale==original_camera_scale and game.heading==game.airship.rotation.y-deg_to_rad(13),"Original scale and synchronized flight heading "+reference):await finish();return
  if not collect_ship():await finish();return
  var body:=clearance(game.airship.global_transform)
  var extra:Dictionary=cloud_clear60() if reference=="1216" else camera_and_water_clearance({"ship_pose":game.airship.global_transform,"camera_pose":game.camera.global_transform})
  var saved:=await capture(reference,"saved60")
  var full_visible:bool=saved.ship_projection.inside if reference=="1216" else saved.both_full_ship_and_mirror_inside_frusta
  if not check(body.passed and extra.passed and full_visible,"Actual complete boat and relevant solid/cloud/water clearance "+reference,{"body":body,"extra":extra}):await finish();return
  var saved_camera:Transform3D=game.camera.transform;var saved_ship:Transform3D=game.airship.transform
  game.improved_cloud_observation=false;game.observe_reference(reference);await settle60()
  if not check(game.camera.transform==base_camera and game.airship.transform==base_ship and game.heading==base_heading,"Disable returns exact inherited56 observation "+reference):await finish();return
  if reference=="1216":await capture(reference,"disabled-original56")
  game.improved_cloud_observation=true;game.observe_reference(reference);await settle60()
  if not check(game.camera.transform==saved_camera and game.airship.transform==saved_ship,"Repeat enabled pose exact "+reference):await finish();return
  if reference=="1216":
   var again:=await capture(reference,"enabled-repeat")
   repeated60={"main_RGBA_exact":again.main.pixel_sha256==saved.main.pixel_sha256,"raw_reflection_RGBA_exact":again.reflection.pixel_sha256==saved.reflection.pixel_sha256}
   if not check(repeated60.main_RGBA_exact and repeated60.raw_reflection_RGBA_exact,"Enabled/disabled/enabled actual pixels restore exactly"):await finish();return
  else:
   if not check(base_camera==saved_camera and base_ship==saved_ship,"Cloud option leaves existing lake pose unchanged "+reference):await finish();return
  pose_rows60.append({"reference":reference,"body":body,"extra":extra,"full_visible":full_visible})
 await finish()

func clearance(pose: Transform3D) -> Dictionary:
 var space: PhysicsDirectSpaceState3D = game.get_world_3d().direct_space_state
 var volumes: Array = native_shapes.duplicate()
 var box := BoxShape3D.new()
 box.size = visual_box.size
 volumes.append({"name": "all_visible_meshes_plus_padding_and_propeller_revolution", "shape": box, "local": Transform3D(Basis.IDENTITY, visual_box.get_center())})
 var rows := []
 var clear := true
 var min_drop := INF
 for mask in [int(game.airship.collision_mask), 5]:
  for volume in volumes:
   var q := PhysicsShapeQueryParameters3D.new()
   q.shape = volume.shape
   q.transform = pose * volume.local
   q.margin = game.airship.safe_margin
   q.collision_mask = mask
   q.exclude = [game.airship.get_rid()]
   var overlap := space.intersect_shape(q, 32)
   q.motion = Vector3.DOWN * 2000.0
   var fraction := space.cast_motion(q)
   var drop: float = fraction[0] * 2000.0 if fraction.size() == 2 else -1.0
   var supported := fraction.size() == 2 # No hit certifies the whole bounded downward sweep; no support surface is inferred.
   var valid := overlap.is_empty() and supported and drop >= 0.25
   clear = clear and valid
   min_drop = minf(min_drop, drop)
   rows.append({"volume": volume.name, "shape_type": volume.shape.get_class(), "mask": mask, "overlaps": hits(overlap), "downward_safe_fraction": Array(fraction), "conservative_vertical_clearance_m": drop, "actual_solid_found_below_500m": supported, "passed": valid})
 var world_box: AABB = pose * visual_box
 var support := []
 for offset in [Vector2(0, 0), Vector2(-0.5, -0.5), Vector2(-0.5, 0.5), Vector2(0.5, -0.5), Vector2(0.5, 0.5)]:
  var start: Vector3 = world_box.get_center() + Vector3(offset.x * world_box.size.x, 0, offset.y * world_box.size.z)
  start.y = world_box.position.y + 0.1
  var ray := PhysicsRayQueryParameters3D.create(start, start + Vector3.DOWN * 500, 5, [game.airship.get_rid()])
  var hit := space.intersect_ray(ray)
  support.append({"ray_from": v3(start), "hit": not hit.is_empty(), "support_y": hit.position.y if not hit.is_empty() else null, "bottom_gap_m": world_box.position.y - hit.position.y if not hit.is_empty() else null, "collider": str(hit.collider.get_path()) if not hit.is_empty() else "none"})
 var sight_hits := []
 for i in range(8):
  var endpoint: Vector3 = pose * visual_box.get_endpoint(i)
  var ray := PhysicsRayQueryParameters3D.create(game.camera.global_position, endpoint, 5, [game.airship.get_rid()])
  var hit := space.intersect_ray(ray)
  if not hit.is_empty(): sight_hits.append({"corner": i, "collider": str(hit.collider.get_path()), "position": v3(hit.position)})
 var local_camera: Vector3 = pose.affine_inverse() * game.camera.global_position
 var nearest_local := local_camera.clamp(visual_box.position, visual_box.end)
 var camera_gap: float = game.camera.global_position.distance_to(pose * nearest_local)
 clear = clear and sight_hits.is_empty() and camera_gap > maxf(2.0, game.camera.near + 0.5)
 return {"passed": clear, "volumes": rows, "minimum_conservative_vertical_clearance_m": min_drop, "cast_length_m": 2000.0, "no_hit_means_bounded_clearance_not_found_support": true,
  "footprint_support_rays": support, "silhouette_sightline_hits": sight_hits, "camera_to_padded_envelope_m": camera_gap,
  "camera_to_ship_origin_m": game.camera.global_position.distance_to(pose.origin), "world_visible_box": str(world_box),
  "scope": "Actual intersect_shape and whole-volume downward casts against loaded native solids, masks1/5; five support rays and eight silhouette sightlines. This proves pose clearance/support distances, not travel from A to B or flown control."}


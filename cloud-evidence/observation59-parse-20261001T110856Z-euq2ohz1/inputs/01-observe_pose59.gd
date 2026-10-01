extends "res://tools/observe_near_ship53west_v2.gd"
## One fixed-camera, unchanged-scale ship pose study. No save or flight claim.
const SCENE59 := "res://scenes/candidate52f/Game52f.tscn"
const SHA59 := "201f667747406b1414a298a6b5433ac1550d8b447dff8f6cb6823d94d2acbd7c"
const PREP59 := ROOT + "/source-assets/observation59-1216-plan/"
var completed59 := false
var optical59 := []
var material59 := []

func cloud_clear59(pose: Transform3D) -> Dictionary:
 var hull:AABB=pose*visual_box
 var rows:=[]
 var count:=0
 for parent in game.get_node("SkyRegion39").get_children():
  if not str(parent.name).begins_with("CloudSea_"):continue
  for mesh in parent.find_children("*","MeshInstance3D",true,false):
   if mesh.mesh==null:continue
   count+=1
   var box:AABB=mesh.global_transform*mesh.mesh.get_aabb()
   if hull.intersects(box):rows.append({"path":str(game.get_path_to(mesh)),"world_aabb":str(box)})
 var result:={"passed":count==125 and rows.is_empty(),"tested_meshes":count,"overlapping_conservative_bounds":rows,"ship_full_envelope":str(hull),"scope":"Conservative bounding-volume separation from all125 original closed CloudSea meshes; any AABB overlap fails without assuming optical clearance. This is not a flight route."}
 optical59.append(result)
 return result

func materials59() -> Array:
 var values:=[]
 for parent in game.get_node("SkyRegion39").get_children():
  if not str(parent.name).begins_with("CloudSea_"):continue
  for mesh in parent.find_children("*","MeshInstance3D",true,false):
   if mesh.mesh==null:continue
   var m:Material=mesh.get_active_material(0)
   var props:={}
   if m:
    for entry in m.get_property_list():
     if int(entry.usage)&PROPERTY_USAGE_STORAGE:props[entry.name]=m.get(entry.name)
   values.append([str(game.get_path_to(mesh)),m.get_instance_id() if m else 0,digest(props)])
 return values

func write_report(complete: bool) -> void:
 if output.is_empty():return
 var row:={"version":"59-fixed1216-camera-ship-pose-study","stage":stage,"complete":complete,"passed_provisional":complete and completed59 and failures.is_empty(),"candidate":SCENE59,"candidate_sha256":SHA59,"renderer":RenderingServer.get_video_adapter_name(),"checks":checks,"failures":failures,"captures":captures,"selections":selections,"comparisons":comparisons,"optical_cloud_bounds":optical59,"state_artifacts":state_artifacts,"restoration_diagnostics":restoration_diagnostics,"scene_saved":false,"camera_changed":false,"ship_scaled":false,"presets_modified":false,"geometry_changed":false,"actual_flight_tested":false,"F2_continuity_tested":false,"visual_acceptance":false,"hardware_gpu_acceptance":false,"scope":"A/B/A2 temporary same-ship position/yaw in unchanged52f research world. Exact tracked native state and actual main/reflection pixel restoration. Existing failed cloud geometry stays unchanged. Not combined with58 or56. Body/full-propeller envelope collision tests,2000m downward clearance and125cloud bounding separation; no optical-cloud traversal or wholeGOAL claim."}
 var f:=FileAccess.open(output.path_join("report59.json.tmp"),FileAccess.WRITE)
 f.store_string(JSON.stringify(row,"  "));f.flush();f.close()
 DirAccess.rename_absolute(output.path_join("report59.json.tmp"),output.path_join("report59.json"))

func finish() -> void:
 restore()
 for path in source_hashes:check(FileAccess.get_sha256(path)==source_hashes[path],"Source preserved "+path)
 stage="complete" if completed59 and failures.is_empty() else "failed"
 write_report(true)
 native_shapes.clear()
 if is_instance_valid(game):game.queue_free()
 await frames(8)
 quit(0 if completed59 and failures.is_empty() else 1)

func run() -> void:
 if not output.is_absolute_path() or DirAccess.dir_exists_absolute(output):quit(2);return
 DirAccess.make_dir_recursive_absolute(output)
 checkpoint("identity")
 if not check(DisplayServer.get_name()!="headless","Actual renderer required"):await finish();return
 var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("POSE59_INPUT_MANIFEST")))
 for path in manifest:
  source_hashes[path]=manifest[path]
  if not check(FileAccess.get_sha256(path)==source_hashes[path],"Pinned input "+path):await finish();return
 if not check(FileAccess.get_sha256(SCENE59)==SHA59,"Pinned saved52f research world"):await finish();return
 var proposal:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PREP59+"proposal.json"))
 var seed:Dictionary=proposal.best_five[0]
 root.size=Vector2i(1180,664)
 game=load(SCENE59).instantiate();root.add_child(game);game.test_frozen=true
 await frames(8);await RenderingServer.frame_post_draw
 controller=game.get_node("World/LakeReflection51")
 var live:=collisions();freeze(game);await physics_frame
 if not check(collisions()==live,"Callbacks frozen without altering active collision state"):await finish();return
 current_reference="1216";game.observe_reference(current_reference)
 var weather=game.get_node("Weather42b");weather.seek_time(0.0);weather.seek_time(0.35);weather._process(0.0)
 RenderingServer.global_shader_parameter_set("world_time",0.35);controller.refresh_now()
 await frames(3);await physics_frame
 original_ship=game.airship.global_transform;original_camera=game.camera.global_transform;original_fov=game.camera.fov
 original_scale=game.airship.scale;original_local=game.airship.transform;original_position=game.airship.position;original_rotation=game.airship.rotation;original_rotation_order=game.airship.rotation_order
 if not check(game.camera.global_position==Vector3(3000,1150,4300) and original_fov==62.0,"Original1216 camera/FOV fixed"):await finish();return
 have_original=true;original_state=snapshot(false).duplicate(true);snapshot_before=digest(original_state);save_state("A-original-full",original_state);collision_before=collisions()
 var unaffected:=invariants(true);material59=materials59()
 if not collect_ship():await finish();return
 var a:=await capture("1216","A-original")
 if not check(clearance(original_ship).passed and cloud_clear59(original_ship).passed,"OriginalA actual full-envelope solid and cloud clearance"):await finish();return
 var chosen:=Transform3D(Basis(Vector3.UP,deg_to_rad(float(seed.yaw_degrees))).scaled(original_scale),Vector3(seed.position_world[0],seed.position_world[1],seed.position_world[2]))
 if not check(clearance(chosen).passed and cloud_clear59(chosen).passed,"CandidateB actual full-envelope solid and cloud clearance"):await finish();return
 var local:Transform3D=game.airship.get_parent_node_3d().global_transform.affine_inverse()*chosen
 game.airship.position=local.origin;game.airship.rotation=Vector3(original_rotation.x,local.basis.get_euler(original_rotation_order).y,original_rotation.z)
 controller.refresh_now();await physics_frame
 if not check(game.airship.scale==original_scale and game.camera.global_transform==original_camera and game.camera.fov==original_fov and invariants(true)==unaffected and collisions()==collision_before and materials59()==material59,"B changes only ship position/yaw, exact camera/scale/material/tracked-state preservation"):await finish();return
 var proj:=projection(game.airship.global_transform)
 selections.append({"seed":seed,"actual_projection":proj,"pose":str(game.airship.global_transform),"actual_mesh_vertices":local_points.size()})
 if not check(proj.inside and clearance(game.airship.global_transform).passed and cloud_clear59(game.airship.global_transform).passed,"Actual placed full geometry fits camera and is conservatively clear"):await finish();return
 var b:=await capture("1216","B-side-study");save_state("B-full",snapshot(false))
 if not restore():await finish();return
 await physics_frame
 var a2:=await capture("1216","A2-restored")
 var result:={"main_RGBA_exact":a.main.pixel_sha256==a2.main.pixel_sha256,"reflection_RGBA_exact":a.reflection.pixel_sha256==a2.reflection.pixel_sha256,"B_main_changed":a.main.pixel_sha256!=b.main.pixel_sha256,"full_tracked_state_exact":invariants(false)==snapshot_before,"all125materials_exact":materials59()==material59}
 comparisons.append(result)
 if not check(result.main_RGBA_exact and result.reflection_RGBA_exact and result.B_main_changed and result.full_tracked_state_exact and result.all125materials_exact,"Strict A/A2 native and real main/reflection pixels restored"):await finish();return
 completed59=true;await finish()

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
			var supported := fraction.size() == 2 and fraction[0] < 1.0
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
	return {"passed": clear, "volumes": rows, "minimum_conservative_vertical_clearance_m": min_drop,
		"footprint_support_rays": support, "silhouette_sightline_hits": sight_hits, "camera_to_padded_envelope_m": camera_gap,
		"camera_to_ship_origin_m": game.camera.global_position.distance_to(pose.origin), "world_visible_box": str(world_box),
		"scope": "Actual intersect_shape and whole-volume downward casts against loaded native solids, masks1/5; five support rays and eight silhouette sightlines. This proves pose clearance/support distances, not travel from A to B or flown control."}


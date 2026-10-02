extends SceneTree
## Four fixed observations, no player flight and no automatic visual acceptance.
var game: Node3D
var trial: Node3D
var output := ""
var report := {"version":"cloud58k-world-trial-v1", "passed":false, "captures":[], "checks":[],
 "visual_acceptance":false, "hardware_gpu_acceptance":false, "flight_acceptance":false}
var failed := false
var cloud_triangles: Array = []
const ROOTS := ["CloudSea_0_0", "CloudSea_0_1", "CloudSea_1_0", "CloudSea_1_1"]

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-dir="): output = arg.trim_prefix("--output-dir=")
 call_deferred("run")

func check(ok: bool, label: String) -> bool:
 report.checks.append({"passed":ok, "label":label})
 if not ok: failed = true; push_error(label)
 return ok

func save_report(stage: String) -> void:
 report.stage = stage
 var f := FileAccess.open(output.path_join("report.json.tmp"), FileAccess.WRITE)
 if f == null: failed = true; return
 f.store_string(JSON.stringify(report, "\t", true, true)); f.flush(); f.close()
 if DirAccess.rename_absolute(output.path_join("report.json.tmp"), output.path_join("report.json")) != OK: failed = true

func freeze(n: Node) -> void:
 n.set_process(false); n.set_physics_process(false)
 n.set_process_input(false); n.set_process_unhandled_input(false); n.set_process_unhandled_key_input(false)
 if n is AnimationPlayer: n.pause()
 if n is Timer: n.paused = true
 for c in n.get_children(): freeze(c)

func witness() -> Dictionary:
 # No all-world mesh decoding. Record unchanged node transforms/visibility and
 # resource bindings around the synchronous single-unit switch only.
 var result := {}
 for n in game.find_children("*", "Node3D", true, false):
  if n == trial or trial.is_ancestor_of(n): continue
  var row := [var_to_bytes(n.transform).hex_encode(), n.visible]
  if n is MeshInstance3D: row.append(n.mesh.get_instance_id() if n.mesh else 0); row.append(n.material_override.get_instance_id() if n.material_override else 0)
  if n is MultiMeshInstance3D: row.append(n.multimesh.get_instance_id() if n.multimesh else 0)
  result[str(game.get_path_to(n))] = row
 return result

func toggle(on: bool) -> bool:
 var before := witness()
 if on:
  if not check(trial.activate(), "Activate only pinned K trial"): return false
 else: trial.deactivate()
 var after := witness()
 var path: String = "SkyRegion39/" + trial.OLD_PATH
 var old: Array = before[path].duplicate()
 old[1] = not on
 before[path] = old
 return check(before == after, "Synchronous switch preserves every other node transform/visibility/resource binding")

func collect_relevant_triangles() -> void:
 cloud_triangles.clear()
 for name in ROOTS:
  var r: Node3D = game.get_node("SkyRegion39/" + name)
  if not check(r.get_child_count() == 1 and r.get_child(0) is MeshInstance3D, "One actual old46 cloud child " + name): return
  var mesh: MeshInstance3D = r.get_child(0)
  var arrays: Array = mesh.mesh.surface_get_arrays(0)
  if not check(arrays[Mesh.ARRAY_VERTEX] is PackedVector3Array and arrays[Mesh.ARRAY_INDEX] is PackedInt32Array, "Actual indexed cloud arrays " + name): return
  var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
  var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
  var triangles := PackedVector3Array(); triangles.resize(indices.size())
  for i in range(indices.size()): triangles[i] = mesh.global_transform * vertices[indices[i]]
  cloud_triangles.append({"path":str(game.get_path_to(mesh)), "node":mesh, "triangles":triangles})

func nearest(origin: Vector3, target: Vector3, triangles: PackedVector3Array) -> Variant:
 var distance := origin.distance_to(target)
 var direction := (target-origin)/distance
 var best := INF
 for i in range(0,triangles.size(),3):
  var hit: Variant = Geometry3D.ray_intersects_triangle(origin,direction,triangles[i],triangles[i+1],triangles[i+2])
  if hit != null:
   var d: float = origin.distance_to(hit)
   if d < distance and d < best: best = d
 return null if is_inf(best) else best

func occlusion_samples() -> Dictionary:
 var arrays: Array = trial.shell.mesh.surface_get_arrays(0)
 var v: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
 var ix: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
 var rows := []; var counts := {}
 # Twelve fixed authored triangle-centroid rays, actual indexed geometry only.
 # These sparse cloud-only rays never represent all-world pixel coverage.
 for face in [0,32,64,96,128,160,192,224,256,288,320,352]:
  var target: Vector3 = trial.shell.global_transform * ((v[ix[face*3]]+v[ix[face*3+1]]+v[ix[face*3+2]])/3.0)
  var hits := []
  for cloud in cloud_triangles:
   if not cloud.node.is_visible_in_tree(): continue
   var d: Variant = nearest(game.camera.global_position,target,cloud.triangles)
   if d != null:
    hits.append({"path":cloud.path,"distance_m":d})
    counts[cloud.path] = int(counts.get(cloud.path,0))+1
  rows.append({"k_face":face, "target":[target.x,target.y,target.z], "hits":hits})
 return {"scope":"12 explicit K face-centroid segments through four relevant visible old cloud meshes; actual indexed arrays; no AABB hit claim; no all-world/ship/self visibility proof", "counts":counts,"rows":rows}

func capture(label: String) -> void:
 var mirror: Node3D = game.get_node("World/LakeReflection51")
 for i in range(3):
  mirror.refresh_now()
  await process_frame
 await RenderingServer.frame_post_draw
 var camera: Camera3D = game.camera
 var image: Image = root.get_texture().get_image()
 var path := output.path_join(label + ".png")
 if not check(image != null and not image.is_empty() and image.save_png(path) == OK, "Save actual normal-material PNG " + label): return
 var projection: Projection = camera.get_camera_projection()
 var projected := []; var a: Array = trial.shell.mesh.surface_get_arrays(0)
 for vertex in a[Mesh.ARRAY_VERTEX]:
  var world: Vector3 = trial.shell.global_transform * vertex
  var screen: Vector2 = camera.unproject_position(world)
  projected.append([screen.x,screen.y,camera.is_position_behind(world)])
 report.captures.append({"name":label,"image_sha256":FileAccess.get_sha256(path),"image_bytes":FileAccess.get_file_as_bytes(path).size(),
  "requested_window_size":[1180,664], "actual_window_size":[root.size.x,root.size.y],
  "actual_visible_rect_size":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],
  "actual_texture_size":[root.get_texture().get_width(),root.get_texture().get_height()],
  "actual_content_scale_size":[root.content_scale_size.x,root.content_scale_size.y],
  "actual_final_transform":var_to_bytes(root.get_final_transform()).hex_encode(),
  "resolution":[image.get_width(),image.get_height()],"camera_transform":var_to_bytes(camera.global_transform).hex_encode(),
  "camera_transform_text":str(camera.global_transform), "camera_projection":var_to_bytes(projection).hex_encode(),
  "fov":camera.fov,"near":camera.near,"far":camera.far,"world_k_projected_vertices":projected,
  "projection_coordinate_space":"Camera3D.unproject_position viewport coordinates, not assumed PNG pixels",
  "trial":trial.state(), "actual_triangle_occlusion":occlusion_samples(),
  "reference":game.scene_environment.current_reference,"weather_time":game.get_node("Weather42b").time_seconds,
  "pixel_visibility_passed":false})
 save_report("captured_"+label)

func finish() -> void:
 report.passed = not failed and report.captures.size() == 4
 save_report("completed" if report.passed else "failed")
 if is_instance_valid(game): game.free()
 await process_frame
 quit(0 if report.passed else 1)

func run() -> void:
 if output.is_empty() or not output.is_absolute_path() or DirAccess.dir_exists_absolute(output): quit(2); return
 DirAccess.make_dir_recursive_absolute(output)
 report.pid = OS.get_process_id(); report.engine = Engine.get_version_info()
 report.renderer = RenderingServer.get_video_adapter_name()
 if not check(DisplayServer.get_name() != "headless", "Actual graphical renderer required"): await finish(); return
 root.size = Vector2i(1180,664)
 game = load("res://cloud_k_trial/CloudKTrial.tscn").instantiate()
 root.add_child(game)
 game.sound_enabled = false; game.test_frozen = true
 trial = game.get_node("SkyRegion39/CloudKTrial")
 if not check(not trial.enabled and trial.unit == null, "Default opt-in disabled before observation"): await finish(); return
 game.observe_reference("1216")
 game.get_node("Weather42b").time_scale = 0.0
 game.get_node("Weather42b").seek_time(0.0)
 game.get_node("Weather42b").seek_time(0.35)
 game.get_node("Weather42b")._process(0.0)
 RenderingServer.global_shader_parameter_set("world_time",0.35)
 freeze(game)
 collect_relevant_triangles()
 if failed: await finish(); return
 # Prepare and validate K, then immediately restore old unit for paired baseline.
 if not toggle(true) or not toggle(false): await finish(); return
 var front: Transform3D = game.camera.global_transform
 report.front_camera_is_inherited_1216 = game.camera.global_position == Vector3(3000,1150,4300) and game.camera.fov == 62.0
 if not check(report.front_camera_is_inherited_1216, "Unchanged original 1216 camera/FOV"): await finish(); return
 report.original_weather = {"reference":game.scene_environment.current_reference,"time":game.get_node("Weather42b").time_seconds}
 await capture("01-original61-front")
 if not toggle(true): await finish(); return
 await capture("02-k-trial-front")
 # Separate explicitly labelled diagnostic viewpoints, never substitutes for front.
 var center := Vector3(3954.748,729.156,3658.070)
 game.camera.global_position = center + Vector3(0.7591154,0.2741250,-0.5904230).normalized()*900.0
 game.camera.look_at(center,Vector3.UP)
 await capture("03-k-fixed-side-back")
 game.camera.global_position = center + Vector3(-0.7182465,0.1647742,0.6759967).normalized()*600.0
 game.camera.look_at(center,Vector3.UP)
 await capture("04-k-fixed-near")
 game.camera.global_transform = front
 if not toggle(false): await finish(); return
 report.restored_to_original = not trial.enabled and trial.old_mesh.visible and not trial.unit.visible and game.camera.global_transform == front
 check(report.restored_to_original, "Opt-out and original observation camera restored")
 await finish()

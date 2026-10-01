extends SceneTree
## Fresh-process paired observations; no scene save and no visual acceptance claims.
const BASE := "res://scenes/candidate51b/Game51b.tscn"
const BASE_SHA := "b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1"
const TARGET := "res://scenes/candidate52e/Game52e.tscn"
const FROZEN_TIME := 0.35
const Audit=preload("res://tools/cloudsea52e_audit.gd")
var audit:=Audit.new()
var game:Node3D
var other:Node3D
var controller:Node3D
var output:=""
var version:="52e"
var candidate_sha:=""
var report52:={}
var captures:=[]
var checks:=[]
var movements:=[]
var meshes_world:=[]
var recipes:=[]
var live_cloud_bindings:=[]
var failed:=false
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):output=arg.trim_prefix("--output-dir=")
		if arg.begins_with("--version="):version=arg.trim_prefix("--version=")
	call_deferred("run")
func frames(count:int) -> void:
	for i in range(count):await process_frame
func settle() -> void:
	await frames(3);await RenderingServer.frame_post_draw
func check(ok:bool,label:String,evidence:Variant=null) -> bool:
	checks.append({"passed":ok,"name":label,"evidence":evidence})
	if not ok:failed=true
	print("PASS " if ok else "FAIL ",label)
	return ok
func write_partial(stage:String,pending:Dictionary={}) -> void:
	if output.is_empty() or not DirAccess.dir_exists_absolute(output):return
	var path:=output.path_join("partial-report.json")
	var data:={"run_complete":false,"stage":stage,"version":version,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":candidate_sha,"checks":checks,"captures":captures,"movements":movements,"live_cloud_bindings":live_cloud_bindings,"pending_capture":pending,"renderer":RenderingServer.get_video_adapter_name(),"visual_acceptance":false,"hardware_gpu_acceptance":false,"complete_flight_passed":false,"total_acceptance_passed":false}
	var file:=FileAccess.open(path+".tmp",FileAccess.WRITE)
	if file==null:push_error("Cannot write atomic52e partial report");failed=true;return
	file.store_string(JSON.stringify(data,"  "));file.flush();file.close()
	if DirAccess.rename_absolute(path+".tmp",path)!=OK:push_error("Cannot commit atomic52e partial report");failed=true
func finish() -> void:
	var report:={"limited_structural_runtime_passed":not failed,"version":version,"baseline":BASE,"baseline_sha256":BASE_SHA,"candidate":TARGET,"candidate_sha256":candidate_sha,"checks":checks,"captures":captures,"movements":movements,"live_cloud_bindings":live_cloud_bindings,"renderer":RenderingServer.get_video_adapter_name(),"frozen_world_time":FROZEN_TIME,"visual_acceptance":false,"hardware_gpu_acceptance":false,"complete_flight_passed":false,"total_acceptance_passed":false,"original_350m_failure_waived":false,"prior1344_conversion_failure_waived":false,"scope":"Paired fresh-process51b/52e observations:1128/1343/1216 front,+50degree side,180degree back; three candidate-derived fixed close views and four climb stations. Actual meshes remain present. Original350m route result retained separately. Cloud center/segment tests use actual world-space triangles, with AABB only as broad phase; no claim of sphere clearance against cloud surfaces or full ship/player flight. These are staged camera observations, not player flight."}
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE)
		if file!=null:file.store_string(JSON.stringify(report,"  "));file.close()
	if DisplayServer.get_name()!="headless":await settle()
	if is_instance_valid(game):game.queue_free()
	if is_instance_valid(other):other.free()
	await frames(8)
	print("CLOUDSEA52E OBSERVATIONS ",version," limited=",not failed)
	quit(1 if failed else 0)
func freeze_tree(node:Node) -> void:
	node.set_process(false);node.set_physics_process(false)
	node.set_process_input(false);node.set_process_unhandled_input(false);node.set_process_unhandled_key_input(false)
	if node is AnimationPlayer:node.pause()
	if node is Timer:node.paused=true
	for child in node.get_children():freeze_tree(child)
func collision_state(node:Node) -> Dictionary:
	var result:={}
	for item in node.find_children("*","CollisionObject3D",true,false):result[str(node.get_path_to(item))]=[item.process_mode,item.disable_mode,item.can_process(),item.collision_layer,item.collision_mask,str(item.get_rid())]
	return result
func physical_clear(pos:Vector3) -> bool:
	var sphere:=SphereShape3D.new();sphere.radius=maxf(.12,game.camera.near)
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=sphere;query.transform=Transform3D(Basis.IDENTITY,pos)
	query.collision_mask=5;query.exclude=[game.airship.get_rid()]
	return pos.y-game.world.ground_height(pos)>sphere.radius and game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()
func ray_triangle(origin:Vector3,direction:Vector3,a:Vector3,b:Vector3,c:Vector3) -> float:
	var e1:=b-a;var e2:=c-a;var p:=direction.cross(e2);var det:=e1.dot(p)
	if absf(det)<0.0000001:return -1.0
	var inv:=1.0/det;var t:=origin-a;var u:=t.dot(p)*inv
	if u < -0.000001 or u > 1.000001:return -1.0
	var q:=t.cross(e1);var v:=direction.dot(q)*inv
	if v < -0.000001 or u+v>1.000001:return -1.0
	var distance:=e2.dot(q)*inv
	return distance if distance>0.0001 else -1.0
func mesh_hits(mesh:Dictionary,origin:Vector3,direction:Vector3,limit:float) -> Array:
	var hits:=[]
	var points:PackedVector3Array=mesh.triangles
	for i in range(0,points.size(),3):
		var distance:=ray_triangle(origin,direction,points[i],points[i+1],points[i+2])
		if distance>0 and distance<limit:hits.append(distance)
	hits.sort()
	var unique:=[]
	for value in hits:
		if unique.is_empty() or absf(value-unique[-1])>.001:unique.append(value)
	return unique
func cloud_center_state(pos:Vector3) -> Dictionary:
	var inside:=[]
	var direction:=Vector3(.941,.233,.242).normalized()
	for mesh in meshes_world:
		if not mesh.bounds.grow(.001).has_point(pos):continue
		var hits:=mesh_hits(mesh,pos,direction,100000.0)
		if hits.size()%2==1:inside.append(mesh.path)
	return {"inside_mesh_paths":inside,"outside_all_cloud_centers":inside.is_empty(),"method":"Actual imported world triangles, ray parity per closed mesh; bounds are broad phase only"}
func cloud_segment_hits(start:Vector3,end:Vector3) -> Array:
	var rows:=[];var length:=start.distance_to(end)
	if length==0:return rows
	var direction:=(end-start)/length
	for mesh in meshes_world:
		if mesh.bounds.intersects_segment(start,end)==null:continue
		var hits:=mesh_hits(mesh,start,direction,length)
		if not hits.is_empty():rows.append({"mesh":mesh.path,"distances_m":hits})
	return rows
func collect_cloud_triangles() -> void:
	for anchor in game.get_node("SkyRegion39").get_children():
		if not str(anchor.name).begins_with("CloudSea_"):continue
		for mesh in anchor.find_children("*","MeshInstance3D",true,false):
			var triangles:=PackedVector3Array()
			var faces:PackedVector3Array=mesh.mesh.get_faces()
			var bounds:=AABB(mesh.global_transform*faces[0],Vector3.ZERO)
			for vertex in faces:
				var world:Vector3=mesh.global_transform*vertex
				triangles.append(world);bounds=bounds.expand(world)
			meshes_world.append({"path":str(game.get_path_to(mesh)),"triangles":triangles,"bounds":bounds})
func probe_path(start:Vector3,end:Vector3,label:String,original350:=false) -> Dictionary:
	var shape:=SphereShape3D.new();shape.radius=maxf(.12,game.camera.near)
	var query:=PhysicsShapeQueryParameters3D.new();query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,start);query.motion=end-start;query.collision_mask=5;query.exclude=[game.airship.get_rid()]
	var fractions:PackedFloat32Array=game.get_world_3d().direct_space_state.cast_motion(query)
	var hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(start,end,5,[game.airship.get_rid()]))
	var physical:=physical_clear(start) and physical_clear(end) and fractions.size()==2 and fractions[0]>=1.0 and hit.is_empty()
	var cloud_hits:=cloud_segment_hits(start,end)
	var start_cloud:=cloud_center_state(start);var end_cloud:=cloud_center_state(end)
	var row:={"name":label,"start":[start.x,start.y,start.z],"end":[end.x,end.y,end.z],"original350m":original350,"physical_camera_sphere_clear":physical,"safe_fraction":fractions[0] if fractions.size()>0 else -1.0,"collider":str(game.get_path_to(hit.collider)) if not hit.is_empty() else "none","cloud_actual_triangle_crossings":cloud_hits,"cloud_start":start_cloud,"cloud_end":end_cloud,"cloud_center_segment_clear":cloud_hits.is_empty() and start_cloud.outside_all_cloud_centers and end_cloud.outside_all_cloud_centers,"full_ship_flight_passed":false}
	movements.append(row);return row
func environment_state() -> Dictionary:
	audit.resource_cache.clear()
	var result:={"reference":game.scene_environment.current_reference,"world_time":FROZEN_TIME,"lights":{},"environments":{}}
	for node in game.find_children("*","DirectionalLight3D",true,false):
		result.lights[str(game.get_path_to(node))]=[audit.transform_values(node.global_transform),node.light_color,node.light_energy,node.visible,node.shadow_enabled]
	for node in game.find_children("*","WorldEnvironment",true,false):result.environments[str(game.get_path_to(node))]=audit.canonical(node.environment)
	return result
func check_live_clouds(reference:String) -> void:
	var rows:=[];var material_ids:={};var valid:=true
	for anchor in game.get_node("SkyRegion39").get_children():
		if not str(anchor.name).begins_with("CloudSea_"):continue
		for mesh in anchor.find_children("*","MeshInstance3D",true,false):
			var material:Material=mesh.get_active_material(0)
			var same_world:bool=mesh.is_inside_tree() and mesh.get_world_3d()==game.get_world_3d()
			var standard:bool=material is StandardMaterial3D
			var wrapped:bool=standard and material.diffuse_mode==BaseMaterial3D.DIFFUSE_LAMBERT_WRAP
			var vertex_colors:bool=standard and material.vertex_color_use_as_albedo
			var lit:bool=standard and material.shading_mode==BaseMaterial3D.SHADING_MODE_PER_PIXEL
			valid=valid and same_world and mesh.is_visible_in_tree() and wrapped and vertex_colors and lit and mesh.get_instance().is_valid()
			material_ids[material.get_instance_id()]=true
			rows.append({"path":str(game.get_path_to(mesh)),"same_world":same_world,"visible":mesh.is_visible_in_tree(),"material_class":material.get_class(),"diffuse_wrap":wrapped,"uses_vertex_color":vertex_colors,"physical_per_pixel_lighting":lit,"renderer_instance_valid":mesh.get_instance().is_valid(),"uniform_registration_required":false,"reason":"Inherited StandardMaterial uses shared world Sun/ambient/fog; environment.collect recursively traverses every child and registers ShaderMaterial uniforms only"})
	check(valid and rows.size()==(25 if version=="51b" else 75) and material_ids.size()==3,"All live cloud parts use same world and original three lit wrap materials "+reference)
	live_cloud_bindings.append({"reference":reference,"count":rows.size(),"unique_actual_materials":material_ids.size(),"rows":rows})
func prepare_view(reference:String) -> void:
	game.observe_reference(reference)
	var weather:Node3D=game.get_node("Weather42b")
	weather.seek_time(0.0);weather.seek_time(FROZEN_TIME);weather._process(0.0)
	RenderingServer.global_shader_parameter_set("world_time",FROZEN_TIME)
	game.get_node("World/LakeDepth50").set_depth_enabled(true)
	controller.set_effect_flags(true,true)
	await frames(5);await physics_frame;await RenderingServer.frame_post_draw
	check_live_clouds(reference)
func capture(label:String,reference:String,view:String) -> void:
	for i in range(5):controller.refresh_now();await process_frame
	await physics_frame;await RenderingServer.frame_post_draw
	var im:Image=root.get_texture().get_image();im.convert(Image.FORMAT_RGBA8)
	var path:=output.path_join(label+".png")
	write_partial("saving_capture",{"name":label,"path":path,"reference":reference,"view":view,"camera_transform":audit.transform_values(game.camera.get_camera_transform()),"camera_fov":game.camera.fov,"environment":environment_state(),"png_written":false})
	check(im.save_png(path)==OK,"Actual rendered "+label)
	var pos:Vector3=game.camera.global_position
	var clear:=physical_clear(pos)
	check(clear,"Physical camera clear "+label)
	captures.append({"name":label,"path":path,"sha256":FileAccess.get_sha256(path),"rgba_digest":audit.digest(im.get_data()),"reference":reference,"view":view,"camera_transform":audit.transform_values(game.camera.get_camera_transform()),"camera_fov":game.camera.fov,"camera_near":game.camera.near,"camera_far":game.camera.far,"size":[im.get_width(),im.get_height()],"environment":environment_state(),"physical_camera_clear":clear,"cloud_center":cloud_center_state(pos),"layers_hidden_for_capture":false,"reflection_requested":controller.reflection_enabled,"clip_enabled":controller.clip_enabled,"optical_overscan":controller.optical_overscan})
	write_partial("capture_complete")
func prepare_supplemental_recipes(candidate:Node3D) -> void:
	var anchor:Node3D=candidate.get_node("SkyRegion39/CloudSea_0_0")
	var transform:Transform3D=audit.source_transform(anchor)
	var main:MeshInstance3D=anchor.get_node("CloudSea52e_v2_main_ridge")
	var center:Vector3=main.transform*main.mesh.get_aabb().get_center()
	var span:Vector3=main.mesh.get_aabb().size
	# Bounds frame the camera only. Actual triangle parity/segments are reported.
	for row in [["near-main-side",Vector3(span.x*.5+160,40,0)],["near-main-under",Vector3(0,-span.y*.5-150,160)],["near-main-back",Vector3(0,60,-span.z*.5-160)]]:
		recipes.append({"name":row[0],"reference":"1343","position":transform*(center+row[1]),"target":transform*center,"kind":"close"})
	for height in [250.,500.,800.,1200.]:recipes.append({"name":"climb-y%d" % int(height+700),"reference":"1216","position":transform*Vector3(850,height,0),"target":transform*Vector3(0,220,0),"kind":"climb"})
func run() -> void:
	if not check(DisplayServer.get_name()!="headless","Actual renderer required"):quit(2);return
	if not check(output.is_absolute_path() and not DirAccess.dir_exists_absolute(output) and version in ["51b","52e"],"New absolute output directory and valid version required"):quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	if not check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.file_exists(TARGET),"Immutable baseline/candidate available"):await finish();return
	candidate_sha=FileAccess.get_sha256(TARGET)
	report52=JSON.parse_string(FileAccess.get_file_as_string("res://scenes/candidate52e/build-report-52e.json"))
	if not check(report52.build_saved_reload_passed and report52.candidate_sha256==candidate_sha,"Actual saved52e build report matches"):await finish();return
	var base_packed:PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var cand_packed:PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	var base:Node3D=base_packed.instantiate();var candidate:Node3D=cand_packed.instantiate();await settle()
	for row in report52.inventory:
		audit.excluded_paths[row.removed_path]=true
		for spec in row.new_meshes:audit.excluded_paths[spec.path]=true
	var base_state:=audit.graph_state(base,base_packed)
	check(base_state==audit.graph_state(base,base_packed),"Unchanged double canonical audit stable")
	check(base_state==audit.graph_state(candidate,cand_packed),"Exact unrelated native graph retained")
	check(audit.digest(base_state)==report52.unaffected_graph_fingerprint,"Independent saved graph fingerprint matches build")
	check(audit.weather_state(base)==audit.weather_state(candidate),"48000 weather floats exact")
	check(audit.material_bindings(base)==audit.material_bindings(candidate),"All248 guard fields and114 controller paths exact")
	var changes:=audit.exact_changes(audit.full_snapshot(base),audit.full_snapshot(candidate))
	check(changes==report52.actual_changes,"Actual25 removed75 added and no changed common properties independently reproduced")
	for row in report52.inventory:
		var old:MeshInstance3D=base.get_node(row.removed_path)
		var root_new:Node3D=candidate.get_node(row.root)
		check(root_new.get_child_count()==3,"Three actual closed source parts "+row.root)
		for spec in row.new_meshes:
			var mesh:MeshInstance3D=candidate.get_node(spec.path)
			audit.resource_cache.clear()
			check(audit.canonical(old.get_active_material(0))==audit.canonical(mesh.get_active_material(0)) and audit.mesh_flags(old)==audit.mesh_flags(mesh),"Original51b active material and render flags "+spec.path)
	prepare_supplemental_recipes(candidate)
	game=base if version=="51b" else candidate;other=candidate if version=="51b" else base
	await settle();other.free();other=null
	if failed:await finish();return
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true
	game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node("World/LakeReflection51")
	var collisions:=collision_state(game);freeze_tree(game);await physics_frame;await physics_frame
	check(collisions==collision_state(game),"Callback freeze preserves live collision activity")
	collect_cloud_triangles()
	for reference in ["1128","1343","1216"]:
		await prepare_view(reference)
		var home:Transform3D=game.camera.global_transform
		await capture(reference+"-front",reference,"front")
		game.camera.rotate_y(deg_to_rad(50));await capture(reference+"-side",reference,"side50")
		game.camera.global_transform=home;game.camera.rotate_y(PI);await capture(reference+"-back",reference,"back180")
		game.camera.global_transform=home
		var start:Vector3=game.camera.global_position
		probe_path(start,start+game.camera.global_basis.x*350.,reference+"-original-plus350m",true)
	var last_climb:Variant=null
	for recipe in recipes:
		await prepare_view(recipe.reference)
		game.camera.global_position=recipe.position;game.camera.look_at(recipe.target,Vector3.UP)
		await capture(recipe.name,recipe.reference,recipe.kind)
		if recipe.kind=="climb":
			if last_climb!=null:probe_path(last_climb,recipe.position,"staged-climb-to-"+recipe.name)
			last_climb=recipe.position
	check(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256(TARGET)==candidate_sha,"Saved51b and52e remain unchanged by verification")
	await finish()

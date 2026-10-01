extends SceneTree
const Common=preload("/workspace/scratch/a29d03198654/Aether/source-assets/coast56/integration-preparation/coast56_common.gd")
var c=Common.new()
var game:Node3D
var packed:PackedScene
var output=OS.get_environment("COAST56_OUT")
var report={"stage":"not_started","passed":false,"strict_saved_readback":false,"live_support_cache_collision":false,"captures":[],"support":[],"visual_acceptance":false,"hardware_gpu_acceptance":false,"real_flight_tested":false}
func _initialize():call_deferred("run")
func frames(n:int):for i in range(n):await process_frame
func settle():await frames(3);await RenderingServer.frame_post_draw
func write_report():
 report.failures=c.failures;report.notes=c.notes
 if output.is_absolute_path() and DirAccess.dir_exists_absolute(output):FileAccess.open(output.path_join("verify-report56.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
func finish(ok:bool):
 report.passed=ok;report.stage="finished";write_report()
 if is_instance_valid(game):game.queue_free();game=null
 packed=null;c.audit.resource_cache.clear();await frames(8)
 print("COAST56_VERIFY ",ok);quit(0 if ok else 1)
func raw_faces(mesh:Mesh)->PackedVector3Array:
 var out=PackedVector3Array()
 for s in mesh.get_surface_count():
  var a=mesh.surface_get_arrays(s)
  if a[12]!=null and not a[12].is_empty():
   for i in a[12]:out.append(a[0][i])
  else:out.append_array(a[0])
 return out
func height_on_faces(faces:PackedVector3Array,transform:Transform3D,x:float,z:float)->Variant:
 var start=transform.affine_inverse()*Vector3(x,1200,z);var end=transform.affine_inverse()*Vector3(x,-100,z);var best=null
 for i in range(0,faces.size(),3):
  var hit=Geometry3D.segment_intersects_triangle(start,end,faces[i],faces[i+1],faces[i+2])
  if hit!=null:
   var world:Vector3=transform*hit
   if best==null or world.y>best:best=world.y
 return best
func support_and_cache()->bool:
 var terrain:MeshInstance3D=game.get_node(Common.MESH);var collider:CollisionShape3D=game.get_node(Common.SHAPE);var mesh_faces=raw_faces(terrain.mesh);var shape_faces:PackedVector3Array=collider.shape.get_faces()
 if not c.check(mesh_faces.size()==3198*3 and shape_faces.size()==3198*3,"Runtime actual drawn mesh/collision triangles; no unused vertex false ground"):return false
 var cell=Vector2i(-4,-4)
 if not c.check(game.world.chunks.get(cell)==terrain and game.world.core.has(cell),"Runtime core map binds actual56 MeshInstance"):return false
 var bases={};var cursor=0
 for grove in game.world.get_node("Vegetation").get_children():
  bases[str(game.get_path_to(grove))]=cursor;cursor+=grove.multimesh.instance_count
 for row in c.roots:
  var node:MultiMeshInstance3D=game.get_node(row.node);var actual=node.global_transform*node.multimesh.get_instance_transform(int(row.index));var expected=c.v3(row.candidate_position)
  if not c.check(c.eq(actual.origin,expected),"Actual GL root global position equals source buffer result",[row.node,row.index,actual.origin,expected]):return false
  var mesh_y=height_on_faces(mesh_faces,terrain.global_transform,expected.x,expected.z);var collision_y=height_on_faces(shape_faces,collider.global_transform,expected.x,expected.z)
  if not c.check(mesh_y!=null and collision_y!=null,"Actual mesh and collider support every saved root",[row.node,row.index]):return false
  var query=PhysicsRayQueryParameters3D.create(Vector3(expected.x,1200,expected.z),Vector3(expected.x,-100,expected.z),4)
  var hit=game.get_world_3d().direct_space_state.intersect_ray(query)
  if not c.check(not hit.is_empty() and hit.collider==collider.get_parent(),"Physics ray hits intended native terrain body",[row.node,row.index,hit]):return false
  var runtime_height:float=game.world.ground_height(Vector3(expected.x,1200,expected.z));var raw_clamped=maxf(0,float(mesh_y));var delta_runtime=absf(runtime_height-raw_clamped)
  # Unchanged runtime intentionally samples Mesh.get_faces' 0.1mm cache; 1mm is
  # a fixed numerical execution bound, never a source-array preservation tolerance.
  if not c.check(delta_runtime<=0.001 and absf(float(hit.position.y)-float(collision_y))<=0.001,"Existing runtime cache/physics agree with independently sampled current geometry within documented float/cache bound",[row.node,row.index,mesh_y,collision_y,runtime_height,hit.position.y]):return false
  var expected_offset=float(row.preserved_origin_offset)
  if not c.check(absf(expected.y-float(mesh_y)-expected_offset)<=0.001,"Saved root retains its original support offset",[row.node,row.index]):return false
  var prop_index:int=int(bases[row.node])+int(row.index)
  if not c.check(game.world.prop_transforms.has(prop_index) and c.eq(game.world.prop_transforms[prop_index],actual),"Runtime placement/collision bookkeeping uses the actual new buffer",[row.node,row.index,prop_index]):return false
  report.support.append({"node":row.node,"index":row.index,"root":str(expected),"raw_mesh_y":mesh_y,"raw_shape_y":collision_y,"physics_y":hit.position.y,"ground_height":runtime_height,"cache_delta":delta_runtime,"prop_index":prop_index})
 if not c.check(game.world.terrain_samples.has(cell),"Runtime terrain cache exists after native support probes"):return false
 if not c.check(c.eq(game.world.terrain_samples[cell].triangles,terrain.mesh.get_faces()),"Runtime cache is exactly current56 derived triangles, not old53 or procedural height"):return false
 if not c.verify_mm(game,true):return false
 report.live_support_cache_collision=true;write_report();return true
func camera_clear()->bool:
 var shape=SphereShape3D.new();shape.radius=maxf(.15,game.camera.near)
 var q=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,game.camera.global_position);q.collision_mask=5;q.exclude=[game.airship.get_rid()]
 return game.get_world_3d().direct_space_state.intersect_shape(q).is_empty()
func capture(name:String,identity:String)->bool:
 await frames(12);await physics_frame;await RenderingServer.frame_post_draw
 if not c.check(camera_clear(),"Actual observation camera clear",name):return false
 var png=output.path_join(name+".png");var image:Image=root.get_texture().get_image()
 if not c.check(image.save_png(png)==OK,"Actual GL image written",name):return false
 report.captures.append({"name":name,"reference":identity,"path":png,"sha256":FileAccess.get_sha256(png),"camera_transform":str(game.camera.global_transform),"fov":game.camera.fov,"world_instance":game.world.get_instance_id(),"weather_time":game.get_node("Weather42b").time_seconds,"size":[image.get_width(),image.get_height()]});write_report();return true
func freeze_weather():
 var weather=game.get_node("Weather42b");weather.set_process(false);weather.time_seconds=.35;weather.call("_process",0.0)
func run():
 if not c.check(DisplayServer.get_name()!="headless","Verifier needs real GL; parse is --check-only"):await finish(false);return
 if not c.check(output.is_absolute_path() and DirAccess.dir_exists_absolute(output),"Existing report directory required"):await finish(false);return
 if not c.load_inputs():await finish(false);return
 root.size=Vector2i(1180,664);report.renderer=RenderingServer.get_video_adapter_name();report.software_renderer="llvmpipe" in str(report.renderer).to_lower() or "softpipe" in str(report.renderer).to_lower()
 var build=c.read_json(Common.CANDIDATE.get_base_dir()+"/build-report56.json")
 if not c.check(build!=null and build.get("passed",false) and FileAccess.get_sha256(Common.CANDIDATE)==build.candidate_sha256,"Exact successful56 build required"):await finish(false);return
 for resource in build.resources:
  if not c.check(FileAccess.get_sha256(resource.path)==resource.sha256,"Exact built independent resource",resource.path):await finish(false);return
 report.stage="fresh_GL_original_then_release";write_report()
 packed=ResourceLoader.load(Common.BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=packed.instantiate();await settle()
 if not c.verify_mm(game,false):await finish(false);return
 var before=c.snapshot(game);var mesh_flags=c.mesh_flags(game.get_node(Common.MESH).mesh);var shape_flags=c.shape_flags(game.get_node(Common.SHAPE).shape);var active=c.active_materials(game.get_node(Common.MESH));c.audit.resource_cache.clear();var original_material=str(c.audit.canonical(game.get_node(Common.MESH).mesh.surface_get_material(0)))
 game.free();game=null;packed=null;c.audit.resource_cache.clear();await frames(8)
 report.stage="strict_saved56_readback_before_ready";write_report()
 packed=ResourceLoader.load(Common.CANDIDATE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=packed.instantiate();await settle()
 if not c.check(before==c.snapshot(game),"Fresh inherited56 all unrelated saved data/effective graph exact"):await finish(false);return
 if not c.verify_mm(game,true) or not c.verify_mesh(game.get_node(Common.MESH).mesh,original_material) or not c.verify_shape(game.get_node(Common.SHAPE).shape):await finish(false);return
 if not c.verify_collision_mapping(game.get_node(Common.MESH).mesh,game.get_node(Common.SHAPE).shape):await finish(false);return
 if not c.empty_second_override(game.get_node(Common.MESH)):await finish(false);return
 if not c.check(c.mesh_flags(game.get_node(Common.MESH).mesh)==mesh_flags and c.shape_flags(game.get_node(Common.SHAPE).shape)==shape_flags and c.active_materials(game.get_node(Common.MESH))==[active[0],active[0]],"Fresh mesh/shape flags and both active materials exact"):await finish(false);return
 for resource in build.resources:
  var loaded=ResourceLoader.load(resource.path,"",ResourceLoader.CACHE_MODE_IGNORE)
  if not c.check(c.saved_resource_hash(loaded)==resource.canonical,"Fresh full resource canonical readback",resource.path):await finish(false);return
 report.strict_saved_readback=true;report.candidate_sha256=build.candidate_sha256;write_report();before.clear();c.audit.resource_cache.clear()
 root.add_child(game);await frames(20);await physics_frame
 game.observe_reference("1131");freeze_weather();await frames(5);await physics_frame
 if not support_and_cache():await finish(false);return
 report.stage="eight_bounded_actual_views";write_report()
 for reference in ["1131","1347"]:
  game.observe_reference(reference);freeze_weather();var original_transform:Transform3D=game.camera.global_transform
  for view in [["front",0.0],["side",PI/2.0],["back",PI]]:
   var pose=original_transform;pose.basis=original_transform.basis.rotated(Vector3.UP,float(view[1]));game.camera.global_transform=pose
   if not await capture(reference+"_"+str(view[0]),reference):await finish(false);return
 # Separate diagnostic navigation views. Source reference poses are never edited.
 game.observe_reference("1131");freeze_weather()
 for view in [["local_low_cape",Vector3(-3040,18,-2910),Vector3(-2790,10,-2920)],["adjacent_north_boundary",Vector3(-3210,150,-3180),Vector3(-2820,16,-2940)]]:
  game.world.update_focus(view[1],true);game.camera.position=view[1];game.camera.look_at(view[2]);game.camera.fov=55
  if not await capture(view[0],"diagnostic, same saved world"):await finish(false);return
 if not c.check(report.captures.size()==8,"Exactly6 reference rotations plus2 local diagnostic views"):await finish(false);return
 if not c.verify_mm(game,true) or not c.verify_shape(game.get_node(Common.SHAPE).shape) or not c.immutable_inputs():await finish(false);return
 report.limits="Real renderer saved-state/cache/root support/collision and eight screenshots only. No hardware GPU, complete object-base support, full-world flight, original-opening regression image or all21-reference acceptance. Independent visual review remains required."
 await finish(true)

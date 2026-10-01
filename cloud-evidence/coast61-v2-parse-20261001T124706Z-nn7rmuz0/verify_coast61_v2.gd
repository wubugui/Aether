extends SceneTree
const Common=preload("/workspace/scratch/a29d03198654/Aether/source-assets/coast61-integration/coast61_common.gd")
var c=Common.new()
var game:Node3D
var packed:PackedScene
var output=OS.get_environment("COAST61_OUT")
var report={"stage":"not_started","passed":false,"strict_saved_readback":false,"live_support_cache_collision":false,"captures":[],"support":[],"visual_acceptance":false,"hardware_gpu_acceptance":false,"real_flight_tested":false}
func _initialize():call_deferred("run")
func frames(n:int):for i in range(n):await process_frame
func settle():await frames(3);await RenderingServer.frame_post_draw
func vec(v:Vector3)->Array:return [v.x,v.y,v.z]
func vectors(a:PackedVector3Array)->Array:
 var out=[]
 for v in a:out.append(vec(v))
 return out
func transform12(t:Transform3D)->Array:
 return [t.basis.x.x,t.basis.y.x,t.basis.z.x,t.origin.x,t.basis.x.y,t.basis.y.y,t.basis.z.y,t.origin.y,t.basis.x.z,t.basis.y.z,t.basis.z.z,t.origin.z]
func write_report():
 report.failures=c.failures;report.notes=c.notes
 if output.is_absolute_path() and DirAccess.dir_exists_absolute(output):FileAccess.open(output.path_join("verify-report61.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
func finish(ok:bool):
 report.passed=ok;report.stage="finished";write_report()
 if is_instance_valid(game):game.queue_free();game=null
 packed=null;c.audit.resource_cache.clear();await frames(8)
 print("COAST61_VERIFY ",ok);quit(0 if ok else 1)
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
func support_and_cache(phase:String)->bool:
 # Exercise the unchanged nearby-prop collider factory at the actual coast.
 # Photo mode prevents the controller from moving this focus during the probe.
 game.world.update_focus(Vector3(-3265,60,-3623),true);await frames(2);await physics_frame
 var terrain:MeshInstance3D=game.get_node(Common.MESH);var collider:CollisionShape3D=game.get_node(Common.SHAPE);var mesh_faces=raw_faces(terrain.mesh);var shape_faces:PackedVector3Array=collider.shape.get_faces()
 if not c.check(mesh_faces.size()==2870*3 and shape_faces.size()==2870*3,"Runtime actual drawn mesh/collision triangles; no unused vertex false ground"):return false
 var cell=Vector2i(-5,-5)
 if not c.check(game.world.chunks.get(cell)==terrain and game.world.core.has(cell),"Runtime core map binds actual61 MeshInstance"):return false
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
  var expected_offset=float(row.preserved_origin_offset)-float(row.get("foot_seat_depth",0.0))
  if not c.check(absf(expected.y-float(mesh_y)-expected_offset)<=0.001,"Saved root retains the documented original offset minus actual-foot seating",[row.node,row.index]):return false
  var minimum={"pine":3.0,"rock":0.5,"bush":1.5}[row.kind]
  if not c.check(float(mesh_y)>=float(minimum),"Actual supporting terrain retains original minimum shore-height guard",[row.node,row.index,mesh_y,minimum]):return false
  var prop_index:int=int(bases[row.node])+int(row.index)
  if not c.check(game.world.prop_transforms.has(prop_index) and c.eq(game.world.prop_transforms[prop_index],actual),"Runtime placement/collision bookkeeping uses the actual new buffer",[row.node,row.index,prop_index]):return false
  var body_kind="bush intentionally has no native prop body"
  if row.kind=="bush":
   if not c.check(not game.world.prop_colliders.has(prop_index),"Native bush collider behavior retained",[row.node,row.index]):return false
  else:
   if not c.check(game.world.prop_colliders.has(prop_index),"Actual nearby native prop body exists",[row.node,row.index]):return false
   var body:StaticBody3D=game.world.prop_colliders[prop_index]
   if not c.check(c.eq(body.global_transform,actual) and body.collision_layer==1 and body.collision_mask==2,"Actual prop body uses exact new instance transform and native masks",[row.node,row.index]):return false
   var shape_node:CollisionShape3D=body.get_child(0)
   if row.kind=="pine":
    if not c.check(shape_node.shape is CapsuleShape3D and absf(shape_node.shape.radius-2.4)<0.000001 and shape_node.shape.height==11 and shape_node.position==Vector3(0,5.5,0),"Native pine capsule recipe retained",[row.node,row.index]):return false
    body_kind="native pine capsule"
   else:
    if not c.check(shape_node.shape is ConcavePolygonShape3D and c.eq(shape_node.shape.get_faces(),game.world.model_meshes[row.kind].get_faces()),"Native rock body uses actual existing prefab collision recipe",[row.node,row.index]):return false
    body_kind="native rock mesh body"
  report.support.append({"phase":phase,"node":row.node,"index":row.index,"root":vec(expected),"raw_mesh_y":mesh_y,"raw_shape_y":collision_y,"physics_y":hit.position.y,"ground_height":runtime_height,"cache_delta":delta_runtime,"prop_index":prop_index,"native_prop_body":body_kind})
 if not c.check(game.world.terrain_samples.has(cell),"Runtime terrain cache exists after native support probes"):return false
 if not c.check(c.eq(game.world.terrain_samples[cell].triangles,terrain.mesh.get_faces()),"Runtime cache is exactly current61 derived triangles, not old53 or procedural height"):return false
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
func camera_state()->Dictionary:
 return {"transform":game.camera.transform,"position":game.camera.position,"rotation":game.camera.rotation,"scale":game.camera.scale,"rotation_order":game.camera.rotation_order,"fov":game.camera.fov}
func diagnostic_state(label:String):
 var rows:Array=report.get("diagnostic_camera_states",[])
 rows.append({"label":label,"transform_hex":var_to_bytes(game.camera.transform).hex_encode(),"rotation_hex":var_to_bytes(game.camera.rotation).hex_encode(),"scale_hex":var_to_bytes(game.camera.scale).hex_encode(),"scale":vec(game.camera.scale),"fov":game.camera.fov});report.diagnostic_camera_states=rows;write_report()
func restore_camera(saved:Dictionary,label:String)->bool:
 diagnostic_state(label+" before restore")
 game.camera.transform=saved.transform;game.camera.rotation_order=saved.rotation_order;game.camera.rotation=saved.rotation;game.camera.scale=saved.scale;game.camera.position=saved.position;game.camera.fov=saved.fov
 var exact:bool=c.eq(game.camera.transform,saved.transform) and c.eq(game.camera.rotation,saved.rotation) and c.eq(game.camera.scale,saved.scale) and c.eq(game.camera.position,saved.position) and game.camera.rotation_order==saved.rotation_order and game.camera.fov==saved.fov
 diagnostic_state(label+" after restore")
 return c.check(exact,"Temporary diagnostic restores original exact camera matrix and derived components",label)
func transform_components(t:Transform3D)->Array:
 return [t.basis.x.x,t.basis.y.x,t.basis.z.x,t.basis.x.y,t.basis.y.y,t.basis.z.y,t.basis.x.z,t.basis.y.z,t.basis.z.z,t.origin.x,t.origin.y,t.origin.z]
func pose_comparison(actual:Transform3D,expected_hex:String)->Dictionary:
 var actual_hex=var_to_bytes(actual).hex_encode();var expected:Transform3D=bytes_to_var(expected_hex.hex_decode());var av=transform_components(actual);var ev=transform_components(expected);var delta=[]
 for i in av.size():
  if av[i]!=ev[i]:delta.append({"component":i,"actual":av[i],"expected":ev[i],"delta":av[i]-ev[i]})
 return {"actual_hex":actual_hex,"expected_hex":expected_hex,"exact":actual_hex==expected_hex,"component_differences":delta,"actual_components":av,"expected_components":ev}
func pose_exact(pose:Dictionary,label:String)->bool:
 var actual_camera=pose_comparison(game.camera.transform,str(pose.expected_camera_transform_hex));var actual_ship=pose_comparison(game.airship.transform,str(pose.expected_ship_transform_hex))
 var rows:Array=report.get("inherited_pose_bytes",[]);rows.append({"label":label,"camera":actual_camera,"ship":actual_ship});report.inherited_pose_bytes=rows;write_report()
 return c.check(actual_camera.exact and actual_ship.exact,"Inherited exact camera/ship pose "+label,{"camera":actual_camera,"ship":actual_ship})
func inherited_observations()->bool:
 if not c.check(game.improved_lake_observation and game.improved_cloud_observation,"Inherited55 lake and60 cloud opt-ins remain enabled"):return false
 var lake=c.read_json("res://assets/observation55/lake_observation_poses.json")
 var cloud=c.read_json("res://assets/observation60/cloud_observation_pose.json")
 game.observe_reference("1128");freeze_weather();await frames(3);await physics_frame
 if not pose_exact(lake["1128"],"1128"):return false
 if not await capture("inheritance_1128","1128 unchanged55 pose"):return false
 game.observe_reference("1216");freeze_weather();await frames(3);await physics_frame
 if not pose_exact(cloud["1216"],"1216 enabled"):return false
 if not await capture("inheritance_1216","1216 enabled60 pose"):return false
 game.improved_cloud_observation=false;game.observe_reference("1216");freeze_weather();await frames(3);await physics_frame
 var entry:Dictionary=game.scene_environment.reference("1216");var info:Dictionary=entry.camera
 var position=Vector3(info.x,0,info.z);position.y=float(info.y_abs) if info.has("y_abs") else game.world.ground_height(position)+float(info.get("agl",120))
 var target=Vector3(info.tx,0,info.tz);target.y=float(info.ty_abs) if info.has("ty_abs") else game.world.ground_height(target)+float(info.get("target_agl",0))
 var forward=(target-position).normalized();var right=forward.cross(Vector3.UP).normalized();var placement:Dictionary=entry.airship
 var expected=position+forward*float(placement.get("dist",40))+right*float(placement.get("right",0))+Vector3.UP*float(placement.get("up",0))
 if not c.check(c.eq(game.airship.position,expected) and var_to_bytes(game.camera.transform).hex_encode()==str(cloud["1216"].expected_camera_transform_hex),"60 opt-out restores native reference ship placement with unchanged camera"):return false
 report.inherited_1216_disabled_ship_transform=var_to_bytes(game.airship.transform).hex_encode()
 game.improved_cloud_observation=true;game.observe_reference("1216");freeze_weather();await frames(3);await physics_frame
 if not pose_exact(cloud["1216"],"1216 restored"):return false
 report.inherited_1128_1216_toggle_passed=true;write_report();return true
func export_runtime_native()->bool:
 var terrain:MeshInstance3D=game.get_node(Common.MESH);var collision:CollisionShape3D=game.get_node(Common.SHAPE)
 var data={"candidate":Common.CANDIDATE,"candidate_sha256":FileAccess.get_sha256(Common.CANDIDATE),"mode":"Actual live GL buffers/meshes after61 saved readback and world entry; direct indexed native arrays, not planned data or headless getters", "mesh_faces_source_order":vectors(c.mapped_faces(terrain.mesh)),"terrain_transform":transform12(terrain.global_transform),"shape_faces":vectors(collision.shape.get_faces()),"shape_transform":transform12(collision.global_transform),"groups":{},"support_phases":report.support,"source_shape_error":c.notes.actual_candidate_mesh_collision_max_component_error}
 for path in c.mm_authority:
  var node:MultiMeshInstance3D=game.get_node(path);var mm:MultiMesh=node.multimesh;var surfaces=[]
  for si in mm.mesh.get_surface_count():
   var arrays=mm.mesh.surface_get_arrays(si);var colors=[];var normals=[]
   if arrays[Mesh.ARRAY_COLOR]!=null:
    for color in arrays[Mesh.ARRAY_COLOR]:colors.append([color.r,color.g,color.b,color.a])
   if arrays[Mesh.ARRAY_NORMAL]!=null:normals=vectors(arrays[Mesh.ARRAY_NORMAL])
   surfaces.append({"vertices":vectors(arrays[Mesh.ARRAY_VERTEX]),"indices":Array(arrays[Mesh.ARRAY_INDEX]) if arrays[Mesh.ARRAY_INDEX]!=null else [],"colors":colors,"normals":normals})
  data.groups[path]={"buffer":Array(mm.buffer),"instance_count":mm.instance_count,"global_transform":transform12(node.global_transform),"surfaces":surfaces}
 var filename=output.path_join("runtime-native61.json");var file=FileAccess.open(filename,FileAccess.WRITE)
 if not c.check(file!=null,"Open actual native61 reconciliation data"):return false
 file.store_string(JSON.stringify(data));file.close();report.runtime_native_path=filename;report.runtime_native_sha256=FileAccess.get_sha256(filename);report.full_foot_offline_gate_required=true;write_report();return true
func run():
 if not c.check(DisplayServer.get_name()!="headless","Verifier needs real GL; parse is --check-only"):await finish(false);return
 if not c.check(output.is_absolute_path() and DirAccess.dir_exists_absolute(output),"Existing report directory required"):await finish(false);return
 if not c.load_inputs():await finish(false);return
 root.size=Vector2i(1180,664);report.verifier_revision="v2 exact diagnostic camera restoration";report.renderer=RenderingServer.get_video_adapter_name();report.software_renderer="llvmpipe" in str(report.renderer).to_lower() or "softpipe" in str(report.renderer).to_lower()
 var build=c.read_json(Common.CANDIDATE.get_base_dir()+"/build-report61.json")
 if not c.check(build!=null and build.get("passed",false) and FileAccess.get_sha256(Common.CANDIDATE)==build.candidate_sha256,"Exact successful61 build required"):await finish(false);return
 for resource in build.resources:
  if not c.check(FileAccess.get_sha256(resource.path)==resource.sha256,"Exact built independent resource",resource.path):await finish(false);return
 report.stage="fresh_GL_original_then_release";write_report()
 packed=ResourceLoader.load(Common.BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=packed.instantiate();await settle()
 if not c.verify_mm(game,false):await finish(false);return
 var before=c.snapshot(game);var mesh_flags=c.mesh_flags(game.get_node(Common.MESH).mesh);var shape_flags=c.shape_flags(game.get_node(Common.SHAPE).shape);var active=c.active_materials(game.get_node(Common.MESH));c.audit.resource_cache.clear();var original_material=str(c.audit.canonical(game.get_node(Common.MESH).mesh.surface_get_material(0)))
 game.free();game=null;packed=null;c.audit.resource_cache.clear();await frames(8)
 report.stage="strict_saved61_readback_before_ready";write_report()
 packed=ResourceLoader.load(Common.CANDIDATE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=packed.instantiate();await settle()
 if not c.check(before==c.snapshot(game),"Fresh inherited61 all unrelated saved data/effective graph exact"):await finish(false);return
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
 if not await support_and_cache("initial_coast"):await finish(false);return
 report.stage="coast_views_and_inheritance_smoke";write_report()
 for reference in ["1131","1347"]:
  game.observe_reference(reference);freeze_weather();var saved_diagnostic=camera_state();var original_transform:Transform3D=game.camera.global_transform;diagnostic_state(reference+" original")
  for view in [["front",0.0],["side",PI/2.0],["back",PI]]:
   var pose=original_transform;pose.basis=original_transform.basis.rotated(Vector3.UP,float(view[1]));game.camera.global_transform=pose
   if not await capture(reference+"_"+str(view[0]),reference):await finish(false);return
   if not restore_camera(saved_diagnostic,reference+"_"+str(view[0])):await finish(false);return
 # Separate diagnostic navigation views. Source reference poses are never edited.
 game.observe_reference("1131");freeze_weather();var saved_local_diagnostic=camera_state();diagnostic_state("local original")
 for view in [["local_bay_low",Vector3(-3470,26,-3620),Vector3(-3260,12,-3630)],["adjacent_north_east",Vector3(-3075,145,-3895),Vector3(-3190,52,-3660)]]:
  game.world.update_focus(view[1],true);game.camera.position=view[1];game.camera.look_at(view[2]);game.camera.fov=55
  if not await capture(view[0],"diagnostic, same saved world"):await finish(false);return
  if not restore_camera(saved_local_diagnostic,str(view[0])):await finish(false);return
 if not await inherited_observations():await finish(false);return
 if not c.check(report.captures.size()==10,"Six coast reference rotations, two local views and two inherited reference smoke views"):await finish(false);return
 game.observe_reference("1131");freeze_weather();await frames(5);await physics_frame
 if not await support_and_cache("returned_after_1128_1216"):await finish(false);return
 if not export_runtime_native():await finish(false);return
 if not c.verify_mm(game,true) or not c.verify_shape(game.get_node(Common.SHAPE).shape) or not c.immutable_inputs():await finish(false);return
 report.limits="Real renderer saved-state/cache/root physics,10 views and1128/1216 toggle inheritance. Full native foot/visibility reconciliation must additionally pass in the wrapper after this process exits. No hardware GPU,61 flight, original-opening or all-reference acceptance."
 await finish(true)

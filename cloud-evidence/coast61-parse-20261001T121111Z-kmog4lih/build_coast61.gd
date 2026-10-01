extends SceneTree
const Common=preload("/workspace/scratch/a29d02870654/Aether/source-assets/coast61-integration/coast61_common.gd")
var c=Common.new()
var game:Node3D
var packed:PackedScene
var output=OS.get_environment("COAST61_OUT")
var report={"stage":"not_started","passed":false,"world_entered_tree":false,"renderer_run":false,"resources":[],"full_scene_packed":false,"visual_acceptance":false,"hardware_gpu_acceptance":false}
func _initialize():call_deferred("run")
func frames(n:int):for i in range(n):await process_frame
func settle():await frames(3);await RenderingServer.frame_post_draw
func write_report():
 report.failures=c.failures;report.notes=c.notes
 if output.is_absolute_path() and DirAccess.dir_exists_absolute(output):FileAccess.open(output.path_join("build-report61.json"),FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
func finish(ok:bool):
 report.passed=ok;report.stage="finished";write_report()
 if is_instance_valid(game):game.free();game=null
 packed=null;c.audit.resource_cache.clear();await frames(8)
 print("COAST61_BUILD ",ok);quit(0 if ok else 1)
func save_one(resource:Resource,path:String)->bool:
 var row=c.resource_readback(resource,path)
 if row.is_empty():return false
 report.resources.append(row);write_report();return true
func run():
 if not c.check(DisplayServer.get_name()!="headless","Builder refuses headless saving; use --check-only for parsing"):await finish(false);return
 report.renderer_run=true;report.renderer=RenderingServer.get_video_adapter_name()
 if not c.check(output.is_absolute_path() and DirAccess.dir_exists_absolute(output),"Existing absolute report directory required"):await finish(false);return
 if not c.load_inputs():await finish(false);return
 report.stage="load_real_GL_source60";write_report()
 packed=ResourceLoader.load(Common.BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=packed.instantiate();await settle()
 if not c.verify_mm(game,false):await finish(false);return
 var before=c.snapshot(game);report.unaffected_graph_sha256=c.audit.digest(before)
 var old_mesh:ArrayMesh=game.get_node(Common.MESH).mesh
 var old_shape:ConcavePolygonShape3D=game.get_node(Common.SHAPE).shape
 var expected_mesh_flags=c.mesh_flags(old_mesh);var expected_shape_flags=c.shape_flags(old_shape)
 c.audit.resource_cache.clear();var material_fingerprint=str(c.audit.canonical(old_mesh.surface_get_material(0)))
 var active_materials=c.active_materials(game.get_node(Common.MESH))
 if not c.check(active_materials.size()==1,"Single original active material"):await finish(false);return
 var new_mesh=c.make_mesh(old_mesh)
 if new_mesh==null or not c.verify_mesh(new_mesh,material_fingerprint):await finish(false);return
 var new_shape:ConcavePolygonShape3D=old_shape.duplicate(false);new_shape.set_faces(c.p3(c.candidate.collider_faces))
 if not c.verify_shape(new_shape) or not c.verify_collision_mapping(new_mesh,new_shape):await finish(false);return
 if not c.check(c.mesh_flags(new_mesh)==expected_mesh_flags and c.shape_flags(new_shape)==expected_shape_flags,"All non-geometry mesh/shape flags retained"):await finish(false);return
 report.stage="save_only_six_independent_resources";write_report()
 DirAccess.make_dir_recursive_absolute(Common.ASSETS)
 if not save_one(new_mesh,Common.ASSETS+"Ground_-5_-5_coast61.mesh"):await finish(false);return
 if not save_one(new_shape,Common.ASSETS+"Ground_-5_-5_coast61_collision.res"):await finish(false);return
 game.get_node(Common.MESH).mesh=new_mesh;game.get_node(Common.SHAPE).shape=new_shape
 for path in c.manifest.changed_groups:
  var node:MultiMeshInstance3D=game.get_node(path);var modified=c.copy_mm(node.multimesh,c.expected_buffer(path,true));await settle()
  if not c.check(c.eq(modified.buffer,c.expected_buffer(path,true)),"Allocated GL copy has exact intended buffer",path):await finish(false);return
  if not save_one(modified,Common.ASSETS+path.get_file()+".res"):await finish(false);return
  node.multimesh=modified
 if not c.verify_mm(game,true):await finish(false);return
 if not c.check(before==c.snapshot(game),"All stored node/resource properties and effective graph unchanged outside declared mesh/shape/MM data"):await finish(false);return
 if not c.empty_second_override(game.get_node(Common.MESH)):await finish(false);return
 if not c.check(c.active_materials(game.get_node(Common.MESH))==[active_materials[0],active_materials[0]],"Both surfaces retain exact original active material"):await finish(false);return
 # Template is native inheritance; never pack the large existing world.
 var tiny=FileAccess.get_file_as_string(Common.PREP+"Game61Coast.tscn.template")
 if not c.check(tiny.to_utf8_buffer().size()<4096,"Bounded tiny inheritance template"):await finish(false);return
 if FileAccess.file_exists(Common.CANDIDATE):
  if not c.check(FileAccess.get_file_as_string(Common.CANDIDATE)==tiny,"Refuse nonmatching candidate overwrite"):await finish(false);return
 else:
  DirAccess.make_dir_recursive_absolute(Common.CANDIDATE.get_base_dir())
  var f=FileAccess.open(Common.CANDIDATE,FileAccess.WRITE)
  if not c.check(f!=null,"Open tiny independent candidate"):await finish(false);return
  f.store_string(tiny);f.close()
 report.stage="release_original_before_reload";write_report()
 game.free();game=null;packed=null;old_mesh=null;old_shape=null;new_mesh=null;new_shape=null;c.audit.resource_cache.clear();await frames(8)
 packed=ResourceLoader.load(Common.CANDIDATE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=packed.instantiate();await settle()
 if not c.check(packed.get_state().get_base_scene_state()!=null,"Native61 scene inherits60"):await finish(false);return
 if not c.check(before==c.snapshot(game),"Saved inherited61 strict graph readback"):await finish(false);return
 if not c.verify_mm(game,true) or not c.verify_mesh(game.get_node(Common.MESH).mesh,material_fingerprint) or not c.verify_shape(game.get_node(Common.SHAPE).shape):await finish(false);return
 if not c.verify_collision_mapping(game.get_node(Common.MESH).mesh,game.get_node(Common.SHAPE).shape):await finish(false);return
 if not c.check(c.mesh_flags(game.get_node(Common.MESH).mesh)==expected_mesh_flags and c.shape_flags(game.get_node(Common.SHAPE).shape)==expected_shape_flags,"Saved inherited resource flags exact"):await finish(false);return
 if not c.empty_second_override(game.get_node(Common.MESH)):await finish(false);return
 if not c.check(c.active_materials(game.get_node(Common.MESH))==[active_materials[0],active_materials[0]],"Saved material identities exact"):await finish(false);return
 if not c.immutable_inputs():await finish(false);return
 report.candidate=Common.CANDIDATE;report.candidate_sha256=FileAccess.get_sha256(Common.CANDIDATE);report.candidate_bytes=tiny.to_utf8_buffer().size();report.old_surface_material=material_fingerprint;report.original_active_material=active_materials[0];report.mesh_flags=expected_mesh_flags;report.shape_flags=expected_shape_flags
 report.surface0_triangles=2111;report.surface1_triangles=759;report.checked_MM_groups=4;report.checked_roots=60;report.modified_component_counts=c.manifest.changed_component_counts;report.source_scene_sha256=c.authority.source_sha256
 report.next_gate="Separate fresh-process verifier must repeat exact saved readback, then live cache/60 full-foot/7 relocation/collision, ten bounded views,1128/1216 inheritance and independent full-foot reconciliation. No acceptance implied."
 report.passed=true
 FileAccess.open(Common.CANDIDATE.get_base_dir()+"/build-report61.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 await finish(true)

extends SceneTree
const BASE="res://scenes/candidate51b/Game51b.tscn"
const BASE_SHA="b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1"
const SOURCE="/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53/integration-west53/"
const DEST="res://scenes/candidate53d-west/"
const TARGET=DEST+"Game53dWest.tscn"
const ASSETS="res://assets/rim53d-west/"
const PREFAB=DEST+"massif_west_spur.tscn"
const ASSET="World/Mountains/massif_west_spur"
const MODEL=ASSET+"/Model"
const ORIGINAL=MODEL+"/massif_west_spur"
const SHAPE=ASSET+"/Collision/Shape"
const PARTS=["ridge_shoulders","snow_cap","snow_gully","shore_rock_apron"]
const MATERIAL="res://assets/reflection51b/clip_material_005.tres"
const Audit=preload("/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53/integration-west53/west53_audit.gd")
var audit=Audit.new()
var game:Node3D
var reloaded:Node3D
var payload:Dictionary
var manifest:Dictionary
var output=""
var report={"build_saved_reload_passed":false,"visual_acceptance":false,"hardware_gpu_acceptance":false,"failures":[],"inventory":[],"new_bindings":[]}
func _initialize():
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--report-dir="):output=arg.trim_prefix("--report-dir=")
 call_deferred("build")
func frames(n):for i in range(n):await process_frame
func settle():await frames(3);await RenderingServer.frame_post_draw
func require(ok:bool,what:String,details:Variant=null)->bool:
 if not ok:report.failures.append({"error":what,"details":details});push_error(what)
 return ok
func finish(ok:bool):
 report.build_saved_reload_passed=ok;report.renderer=RenderingServer.get_video_adapter_name()
 if not output.is_empty():
  var f=FileAccess.open(output+"/build-report-west53.json",FileAccess.WRITE)
  if f!=null:f.store_string(JSON.stringify(report,"  "));f.close()
 if ok:
  var f=FileAccess.open(DEST+"build-report-west53.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));f.close()
 if DisplayServer.get_name()!="headless":await settle()
 if is_instance_valid(game):game.free()
 if is_instance_valid(reloaded):reloaded.free()
 await frames(8);print("WEST53 BUILD_SAVED_RELOAD ",ok);quit(0 if ok else 1)
func vec(a)->Vector3:return Vector3(a[0],a[1],a[2])
func tf(a)->Transform3D:return Transform3D(Basis(vec(a.slice(0,3)),vec(a.slice(3,6)),vec(a.slice(6,9))),vec(a.slice(9,12)))
func copy_mm(source:MultiMesh)->MultiMesh:
 var m=MultiMesh.new();m.transform_format=source.transform_format;m.use_colors=source.use_colors;m.use_custom_data=source.use_custom_data;m.mesh=source.mesh;m.custom_aabb=source.custom_aabb;m.physics_interpolation_quality=source.physics_interpolation_quality;m.instance_count=source.instance_count;m.buffer=source.buffer;m.visible_instance_count=source.visible_instance_count;m.resource_local_to_scene=source.resource_local_to_scene;m.resource_name=source.resource_name
 return m
func mesh_for(part:Dictionary,inverse:Transform3D,material:Material)->ArrayMesh:
 var vertices=PackedVector3Array();var normals=PackedVector3Array();var colors=PackedColorArray()
 for p in part.vertices:vertices.append(inverse*vec(p))
 for c in part.colors:colors.append(Color(c[0],c[1],c[2],c[3]))
 for i in range(0,vertices.size(),3):
  var normal=(vertices[i+2]-vertices[i]).cross(vertices[i+1]-vertices[i]).normalized()
  if not require(normal.length_squared()>.5,"Degenerate source triangle",[part.name,i]):return null
  for j in range(3):normals.append(normal)
 var arrays=[];arrays.resize(Mesh.ARRAY_MAX);arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals;arrays[Mesh.ARRAY_COLOR]=colors
 var mesh=ArrayMesh.new();mesh.resource_name="west53d_"+str(part.name);mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays);mesh.surface_set_material(0,material);return mesh
func save_resource(r:Resource,path:String)->bool:
 if not require(not FileAccess.file_exists(path),"Refuse overwrite independent asset",path):return false
 if not require(ResourceSaver.save(r,path)==OK,"Asset save failed",path):return false
 var fresh=ResourceLoader.load(path,"",ResourceLoader.CACHE_MODE_IGNORE)
 audit.resource_cache.clear()
 if not require(fresh!=null and audit.canonical(r)==audit.canonical(fresh),"Asset canonical reload differs",path):return false
 report.inventory.append({"path":path,"sha256":FileAccess.get_sha256(path),"class":r.get_class(),"fingerprint":audit.canonical(fresh)})
 r.take_over_path(path);return true
func own(n:Node,root_node:Node):
 n.scene_file_path=""
 if n!=root_node:n.owner=root_node
 for c in n.get_children():own(c,root_node)
func joined_faces(g:Node)->PackedVector3Array:
 var result=PackedVector3Array();var inv=audit.source_transform(g.get_node(SHAPE)).affine_inverse()
 for node in g.get_node(MODEL).get_children():
  if not node is MeshInstance3D:continue
  var transform=audit.source_transform(node)
  for p in node.mesh.get_faces():result.append(inv*(transform*p))
 return result
func verify_targets(g:Node)->bool:
 var shape:CollisionShape3D=g.get_node(SHAPE)
 if not require(shape.get_parent().collision_layer==5 and shape.get_parent().collision_mask==2,"Layer5/mask2 collider changed"):return false
 var expected=joined_faces(g);var actual=shape.shape.get_faces();var max_error=0.0
 if not require(expected.size()==actual.size() and actual.size()==1780*3,"Combined collision triangle count mismatch"):return false
 for i in expected.size():max_error=maxf(max_error,expected[i].distance_to(actual[i]))
 if not require(max_error<.002,"Collision differs from actual saved component faces",max_error):return false
 for part in payload.mountains[0].components:
  if part.name=="rock_body":continue
  var node:MeshInstance3D=g.get_node(MODEL+"/"+part.name)
  var faces=node.mesh.get_faces();var transform=audit.source_transform(node);max_error=0.0
  if not require(faces.size()==part.vertices.size(),"Added mesh count differs",part.name):return false
  for i in faces.size():max_error=maxf(max_error,(transform*faces[i]).distance_to(vec(part.vertices[i])))
  if not require(max_error<.002,"Added mesh differs from Blender source",[part.name,max_error]):return false
  if not require(node.material_override.resource_path==MATERIAL and node.get_surface_override_material(0).resource_path==MATERIAL and node.mesh.surface_get_material(0).resource_path==MATERIAL,"New component guard binding differs",part.name):return false
 for e in payload.scatter:
  if not require(g.get_node(e.node_path).multimesh.get_instance_transform(int(e.index))==tf(e.after_transform),"Saved scatter transform mismatch",[e.node_path,e.index]):return false
 return true
func build():
 if not require(DisplayServer.get_name()!="headless","Full-scene save requires real renderer; headless parse only"):quit(2);return
 if not require(output.is_absolute_path() and DirAccess.dir_exists_absolute(output),"Existing absolute report directory required"):await finish(false);return
 if not require(FileAccess.get_sha256(BASE)==BASE_SHA and not FileAccess.file_exists(TARGET) and not FileAccess.file_exists(PREFAB),"Immutable51b mismatch or existing candidate; refuse overwrite"):await finish(false);return
 manifest=JSON.parse_string(FileAccess.get_file_as_string(SOURCE+"integration-manifest.json"));payload=JSON.parse_string(FileAccess.get_file_as_string(SOURCE+"integration-payload.json"))
 var gate=JSON.parse_string(FileAccess.get_file_as_string(SOURCE+"source-visual-gate.json")) if FileAccess.file_exists(SOURCE+"source-visual-gate.json") else {}
 if not require(gate.get("source_form_ready_for_integration",false) and gate.get("source_payload_sha256","")==manifest.source_payload_sha256,"Five-view source form gate is pending or does not match exact source"):await finish(false);return
 var source_payload=JSON.parse_string(FileAccess.get_file_as_string(manifest.source_payload_path))
 if not require(payload.mountains==source_payload.mountains,"Integration geometry differs from exact53d source"):await finish(false);return
 if not require(payload.baseline_sha256==BASE_SHA and payload.mountains.size()==1 and payload.mountains[0].name=="massif_west_spur" and payload.scatter.size()==120,"Payload must be exact west-only/120-index scope"):await finish(false);return
 for e in manifest.immutable_inputs:
  if not require(FileAccess.get_sha256(e.path)==e.sha256,"Immutable input changed",e.path):await finish(false);return
 report.baseline=BASE;report.baseline_sha256=BASE_SHA;report.project_default_sha256=FileAccess.get_sha256("res://project.godot");report.manifest_sha256=FileAccess.get_sha256(SOURCE+"integration-manifest.json");report.source_visual_gate=gate
 for part in PARTS:audit.added_paths[MODEL+"/"+part]=true
 audit.shape_edits[SHAPE]=true
 for e in payload.scatter:
  if not require(e.node_path in manifest.scatter_groups and tf(e.before_transform).basis==tf(e.after_transform).basis,"Unexpected scatter group/basis change",e):await finish(false);return
  if not audit.scatter_edits.has(e.node_path):audit.scatter_edits[e.node_path]={}
  if not require(not audit.scatter_edits[e.node_path].has(int(e.index)),"Duplicate scatter index",e):await finish(false);return
  audit.scatter_edits[e.node_path][int(e.index)]=e
 var packed_base:PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);game=packed_base.instantiate();await settle()
 var before=audit.graph_state(game,packed_base);var full_before=audit.full_snapshot(game);var weather=audit.weather_state(game);var bindings=audit.material_bindings(game)
 if not require(weather.Rain.valid and weather.Snow.valid,"Native weather buffer missing"):await finish(false);return
 if not require(before==audit.graph_state(game,packed_base),"Unmodified double snapshot drift"):await finish(false);return
 var scatter_total=0
 for path in manifest.all_six_tile_scatter_counts:
  var mm:MultiMesh=game.get_node(path).multimesh
  if not require(mm.instance_count==int(manifest.all_six_tile_scatter_counts[path]),"Six-tile scatter count changed",path):await finish(false);return
  scatter_total+=mm.instance_count
 if not require(scatter_total==1261,"Expected1261 existing instances"):await finish(false);return
 for path in audit.scatter_edits:
  var indices=audit.scatter_edits[path].keys();indices.sort()
  if not require(indices==manifest.scatter_groups[path],"Affected scatter indices differ from exact120 source-impact set",path):await finish(false);return
 var original_mesh=audit.canonical(game.get_node(ORIGINAL).mesh);report.original_root_mesh_fingerprint=original_mesh
 var mat:ShaderMaterial=game.get_node(ASSET).get("surface_material")
 if not require(mat!=null and mat.resource_path==MATERIAL and mat.shader.code.contains("(CAMERA_VISIBLE_LAYERS & 524288u) != 0u && (CAMERA_VISIBLE_LAYERS & 262144u) == 0u"),"Verified parent dual-guard material missing"):await finish(false);return
 DirAccess.make_dir_recursive_absolute(ASSETS);DirAccess.make_dir_recursive_absolute(DEST)
 var model=game.get_node(MODEL);var inverse=audit.source_transform(model).affine_inverse()
 for part in payload.mountains[0].components:
  if part.name=="rock_body":continue
  if not require(part.name in PARTS and not model.has_node(part.name),"Unexpected or duplicate component",part.name):await finish(false);return
  var mesh=mesh_for(part,inverse,mat)
  if mesh==null or not save_resource(mesh,ASSETS+part.name+".mesh"):await finish(false);return
  var node=MeshInstance3D.new();node.name=part.name;node.mesh=mesh;node.skeleton=NodePath("");node.material_override=mat;node.set_surface_override_material(0,mat);model.add_child(node);node.owner=game.get_node(ORIGINAL).owner
  report.new_bindings.append({"path":MODEL+"/"+part.name,"material_override":MATERIAL,"surface_material_override/0":MATERIAL,"mesh_surface_material/0":MATERIAL,"owner":str(game.get_path_to(node.owner))})
 var collider:CollisionShape3D=game.get_node(SHAPE);var new_shape=collider.shape.duplicate(false);new_shape.set_faces(joined_faces(game))
 if not save_resource(new_shape,ASSETS+"massif_west_spur_collision.res"):await finish(false);return
 collider.shape=new_shape
 for path in audit.scatter_edits:
  var node:MultiMeshInstance3D=game.get_node(path);var mm=copy_mm(node.multimesh);audit.resource_cache.clear()
  if not require(mm.buffer==node.multimesh.buffer and audit.canonical(mm)==audit.canonical(node.multimesh),"MultiMesh copy drift",path):await finish(false);return
  for index in audit.scatter_edits[path]:
   var e=audit.scatter_edits[path][index]
   if not require(mm.get_instance_transform(index)==tf(e.before_transform),"Authoritative before transform mismatch",[path,index]):await finish(false);return
   mm.set_instance_transform(index,tf(e.after_transform))
  if not save_resource(mm,ASSETS+"Grounded_"+path.get_file()+".res"):await finish(false);return
  node.multimesh=mm
 if not require(before==audit.graph_state(game,packed_base) and bindings==audit.material_bindings(game),"Out-of-scope stored graph/material change"):await finish(false);return
 if not verify_targets(game):await finish(false);return
 audit.resource_cache.clear()
 if not require(audit.canonical(game.get_node(ORIGINAL).mesh)==original_mesh,"Original root mesh changed"):await finish(false);return
 # Standalone native prefab is a copy only; original full-scene ownership is untouched.
 var prefab:Node3D=game.get_node(ASSET).duplicate();prefab.transform=Transform3D.IDENTITY;own(prefab,prefab)
 var prefab_packed=PackedScene.new()
 if not require(prefab_packed.pack(prefab)==OK and ResourceSaver.save(prefab_packed,PREFAB)==OK,"Independent prefab pack/save failed"):prefab.free();await finish(false);return
 var prefab_reload:PackedScene=ResourceLoader.load(PREFAB,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);var prefab_node=prefab_reload.instantiate()
 var prefab_exact=audit.graph_state(prefab,prefab_packed,false)==audit.graph_state(prefab_node,prefab_reload,false);prefab.free();prefab_node.free()
 if not require(prefab_exact,"Independent prefab native reload differs"):await finish(false);return
 report.inventory.append({"path":PREFAB,"sha256":FileAccess.get_sha256(PREFAB),"class":"PackedScene","native_reload_exact":true})
 var packed=PackedScene.new()
 if not require(packed.pack(game)==OK and ResourceSaver.save(packed,TARGET)==OK,"Candidate pack/save failed"):await finish(false);return
 var saved_file=FileAccess.open(TARGET,FileAccess.READ);report.candidate_bytes=saved_file.get_length();saved_file.close()
 if not require(report.candidate_bytes<100*1024*1024,"Candidate exceeds100MiB"):await finish(false);return
 var reload_packed:PackedScene=ResourceLoader.load(TARGET,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);reloaded=reload_packed.instantiate();await settle()
 if not require(before==audit.graph_state(reloaded,reload_packed),"Saved reload changed unrelated graph/ownership/order/groups/connections/translation-excluded bytes"):await finish(false);return
 if not require(weather==audit.weather_state(reloaded) and bindings==audit.material_bindings(reloaded),"48000-weather/248-bindings/114-material state changed"):await finish(false);return
 if not verify_targets(reloaded):await finish(false);return
 audit.resource_cache.clear()
 if not require(audit.canonical(reloaded.get_node(ORIGINAL).mesh)==original_mesh,"Reload changed original root mesh"):await finish(false);return
 var delta=audit.exact_changes(full_before,audit.full_snapshot(reloaded));var expected_additions=audit.added_paths.keys();expected_additions.sort()
 if not require(delta.removed_nodes.is_empty() and delta.added_nodes==expected_additions,"Unexpected node addition/deletion",delta):await finish(false);return
 for e in delta.changed_properties:
  if not require((e.path==SHAPE and e.property=="shape") or (audit.scatter_edits.has(e.path) and e.property in ["multimesh","exact_multimesh_buffer"]),"Unexpected common-node property change",e):await finish(false);return
 if not require(FileAccess.get_sha256(BASE)==BASE_SHA and FileAccess.get_sha256("res://project.godot")==report.project_default_sha256,"Baseline/default changed"):await finish(false);return
 report.candidate=TARGET;report.candidate_sha256=FileAccess.get_sha256(TARGET);report.exact_changes=delta;report.unaffected_graph_fingerprint=audit.digest(before);report.weather=weather;report.material_bindings=bindings;report.scatter_changed=120;report.scatter_untouched_in_six_tiles=1141;report.scatter_groups=audit.scatter_edits.keys();report.collision_triangles=1780;report.source_depth_proof=manifest.water_proof;report.scene_entered_live_tree=false;report.prefab=PREFAB;report.next_gate="Fresh process live ready bindings, actual collision and scatter support, saved-world waterline preservation, original1128/1129 plus side/back/near views; no visual pass implied."
 packed_base=null;packed=null;reload_packed=null;prefab_packed=null;prefab_reload=null
 before.clear();full_before.clear();audit.resource_cache.clear()
 await finish(true)

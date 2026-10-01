extends RefCounted
## Shared strict gates. No work occurs on preload/parse; renderer runners call explicitly.
const BASE = "res://scenes/candidate55-observation/Game55Observation.tscn"
const CANDIDATE = "res://scenes/candidate56-coast/Game56Coast.tscn"
const MESH = "World/Terrain/Ground_-4_-4/Model/Ground_-4_-4"
const SHAPE = "World/Terrain/Ground_-4_-4/Collision/Shape"
const SOURCE = "/workspace/scratch/a29d03198654/Aether/source-assets/coast56/"
const PREP = SOURCE+"integration-preparation/"
const ASSETS = "res://assets/coast56/"
const Audit = preload("res://tools/reflection51b_saved_audit.gd")
var failures:Array=[]
var notes:Dictionary={}
var authority:Dictionary
var candidate:Dictionary
var manifest:Dictionary
var mm_authority:Dictionary
var roots:Array
var changed:Dictionary={}
var untouched:Array=[]
var audit=Audit.new()
func check(ok:bool,label:String,detail:Variant=null)->bool:
 if not ok:failures.append({"label":label,"detail":detail});push_error(label)
 return ok
func read_json(path:String):return JSON.parse_string(FileAccess.get_file_as_string(path))
func eq(a:Variant,b:Variant)->bool:return var_to_bytes(a)==var_to_bytes(b)
func v3(a)->Vector3:return Vector3(float(a[0]),float(a[1]),float(a[2]))
func p3(a)->PackedVector3Array:
 var out=PackedVector3Array()
 for p in a:out.append(v3(p))
 return out
func p4(a)->PackedColorArray:
 var out=PackedColorArray()
 for p in a:out.append(Color(float(p[0]),float(p[1]),float(p[2]),float(p[3])))
 return out
func arrays(a:Array)->Array:
 var out=[];out.resize(Mesh.ARRAY_MAX)
 out[0]=p3(a[0]);out[1]=p3(a[1]);out[2]=PackedFloat32Array(a[2]);out[3]=p4(a[3]);out[12]=PackedInt32Array(a[12]);return out
func load_inputs()->bool:
 authority=read_json(SOURCE+"native-authority/authority.json");candidate=read_json(SOURCE+"candidate-native.json");manifest=read_json(PREP+"preparation-manifest.json");mm_authority=read_json(PREP+"static-multimesh-authority.json");roots=read_json(SOURCE+"scatter-replacements.json")
 for path in manifest.immutable_inputs:
  if not check(FileAccess.get_sha256(path)==manifest.immutable_inputs[path],"Immutable source changed",path):return false
 if not check(read_json(SOURCE+"verified-static56.json").passed==true,"Source75 static gate required"):return false
 for i in candidate.changed_triangle_indices:changed[int(i)]=true
 for i in range(3198):
  if not changed.has(i):untouched.append(i)
 if not check(changed.size()==533 and untouched.size()==2665 and roots.size()==44,"Exact source scope required"):return false
 audit.property_masks[MESH]=["mesh","surface_material_override/1"]
 audit.property_masks[SHAPE]=["shape"]
 for path in manifest.changed_groups:
  audit.scatter_edits[path]={}
  for row in mm_authority[path].changed_rows:audit.scatter_edits[path][int(row.index)]=true
 return true
func expected_buffer(path:String,modified:bool)->PackedFloat32Array:
 var out=PackedFloat32Array(mm_authority[path].buffer)
 if modified:
  for row in mm_authority[path].changed_rows:out[int(row.index)*12+7]=float(row.after_y)
 return out
func verify_mm(game:Node,modified:bool)->bool:
 for path in mm_authority:
  var mm:MultiMesh=game.get_node(path).multimesh
  if not check(mm.instance_count==int(mm_authority[path].instance_count) and mm.transform_format==MultiMesh.TRANSFORM_3D and not mm.use_colors and not mm.use_custom_data,"Native MM allocation/format",path):return false
  if not check(eq(mm.buffer,expected_buffer(path,modified)),"Real GL MM buffer equals complete stored TSCN authority plus only authorized Y slots",path):return false
 return true
func effective_graph(game:Node)->Dictionary:
 var result={"order":[],"owners":{},"groups":{},"connections":[],"child_scene_paths":{}}
 var all:Array[Node]=[game];all.append_array(game.find_children("*","",true,false))
 for node in all:
  var path=str(game.get_path_to(node));result.order.append(path);result.owners[path]=str(game.get_path_to(node.owner)) if node.owner else "<none>"
  var groups=[]
  for group in node.get_groups():groups.append(str(group))
  groups.sort();result.groups[path]=groups
  if node!=game:result.child_scene_paths[path]=node.scene_file_path
  for signal_info in node.get_signal_list():
   for connection in node.get_signal_connection_list(signal_info.name):
    if not (int(connection.flags)&Object.CONNECT_PERSIST):continue
    var callback:Callable=connection.callable;var target=callback.get_object()
    result.connections.append([path,str(signal_info.name),str(game.get_path_to(target)) if target is Node else str(target.get_class()),str(callback.get_method()),connection.flags,callback.get_bound_arguments(),callback.get_unbound_arguments_count()])
 result.connections.sort_custom(func(a,b):return str(a)<str(b));return result
func snapshot(game:Node)->Dictionary:return {"stored":audit.snapshot(game),"effective":effective_graph(game)}
func topology_expected()->PackedVector3Array:
 var positions=p3(candidate.surface_arrays[0]);var idx=PackedInt32Array(candidate.surface_arrays[12]);var out=PackedVector3Array()
 for i in idx:out.append(positions[i])
 return out
func frozen_indices()->PackedInt32Array:
 var source_idx=PackedInt32Array(authority.surfaces[0].arrays[12]);var out=PackedInt32Array()
 for face in untouched:
  for corner in range(3):out.append(source_idx[int(face)*3+corner])
 return out
func make_mesh(old:ArrayMesh)->ArrayMesh:
 var original:Array=old.get("_surfaces")
 if not check(original.size()==1 and old.shadow_mesh==null,"Original has one surface and no shadow mesh; otherwise stop for explicit update"):return null
 var old_surface:Dictionary=original[0]
 var lods=old_surface.get("lods",{})
 if not check(lods==null or lods.is_empty(),"Original surface has no LOD indices; never retain stale old triangles in LOD"):return null
 notes.original_lods_absent=true;notes.original_shadow_mesh_absent=true
 var expected_original=arrays(authority.surfaces[0].arrays)
 var actual_original=old.surface_get_arrays(0)
 if not check(eq(actual_original,expected_original),"Actual GL original mesh arrays equal saved native authority"):return null
 var keep=frozen_indices();var frozen:Dictionary=old_surface.duplicate(true)
 var stride=RenderingServer.mesh_surface_get_format_index_stride(int(frozen.format),int(frozen.vertex_count))
 if not check(stride in [2,4],"Recognized native index stride",stride):return null
 var index_data=PackedByteArray();index_data.resize(keep.size()*stride)
 for i in keep.size():
  if stride==2:index_data.encode_u16(i*stride,keep[i])
  else:index_data.encode_u32(i*stride,keep[i])
 frozen.index_data=index_data;frozen.index_count=keep.size()
 var result=ArrayMesh.new();result.set("_surfaces",[frozen]);result.resource_name=old.resource_name;result.resource_local_to_scene=old.resource_local_to_scene;result.blend_shape_mode=old.blend_shape_mode;result.custom_aabb=old.custom_aabb
 # Changed triangles use an uncompressed position stream. Original frozen attribute
 # bytes stay untouched in surface0. Both surfaces use the original material.
 var src=arrays(candidate.surface_arrays);var added=[];added.resize(Mesh.ARRAY_MAX)
 var vertices=PackedVector3Array();var normals=PackedVector3Array();var tangents=PackedFloat32Array();var colors=PackedColorArray()
 for face in range(3198):
  if not changed.has(face):continue
  for corner in range(3):
   var vi:int=src[12][face*3+corner];vertices.append(src[0][vi]);normals.append(src[1][vi]);colors.append(src[3][vi])
   for k in range(4):tangents.append(src[2][vi*4+k])
 added[0]=vertices;added[1]=normals;added[2]=tangents;added[3]=colors
 result.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,added,[],{},0)
 result.surface_set_material(0,old.surface_get_material(0));result.surface_set_material(1,old.surface_get_material(0))
 result.surface_set_name(0,old.surface_get_name(0));result.surface_set_name(1,"Coast56 authorized533 source triangles")
 return result
func verify_mesh(mesh:ArrayMesh,old_material_fingerprint:String)->bool:
 if not check(mesh.get_surface_count()==2 and mesh.shadow_mesh==null,"Only two surfaces, no stale shadow mesh"):return false
 var raw: Array=mesh.get("_surfaces")
 for surface in raw:
  var lods=surface.get("lods",{})
  if not check(lods==null or lods.is_empty(),"No stale LOD indices on either surface"):return false
 var a=mesh.surface_get_arrays(0);var b=mesh.surface_get_arrays(1);var original=arrays(authority.surfaces[0].arrays);var desired=arrays(candidate.surface_arrays)
 for slot in range(Mesh.ARRAY_MAX):
  if slot==Mesh.ARRAY_INDEX:continue
  if not check(eq(a[slot],original[slot]),"All original surface0 GPU fields exact, including unused vertices",slot):return false
 if not check(eq(a[12],frozen_indices()),"Surface0 draws only original2665 frozen triangles"):return false
 if not check(b[0].size()==533*3 and (b[12]==null or b[12].is_empty()),"Surface1 draws only source533 candidate triangles"):return false
 var cursor=0;var max_normal_encoding_delta=0.0
 for face in range(3198):
  if not changed.has(face):continue
  for corner in range(3):
   var vi:int=desired[12][face*3+corner]
   if not check(eq(b[0][cursor],desired[0][vi]) and eq(b[3][cursor],desired[3][vi]),"Candidate surface positions and original colors exact",[face,corner]):return false
   max_normal_encoding_delta=maxf(max_normal_encoding_delta,b[1][cursor].distance_to(desired[1][vi]));cursor+=1
 for surface in range(2):
  audit.resource_cache.clear()
  if not check(str(audit.canonical(mesh.surface_get_material(surface)))==old_material_fingerprint,"Both surfaces retain original material",surface):return false
 # Normals/tangents on edited triangles are canonically packed by the engine;
 # saved/reloaded resource canonical hashes must still match exactly.
 notes.edited_surface_normal_native_encoding_max_delta=max_normal_encoding_delta
 notes.drawn_triangle_count=a[12].size()/3+b[0].size()/3
 return check(notes.drawn_triangle_count==3198,"No old authorized faces rendered through unused original vertices")
func copy_mm(old:MultiMesh,buffer:PackedFloat32Array)->MultiMesh:
 var out=MultiMesh.new();out.transform_format=old.transform_format;out.use_colors=old.use_colors;out.use_custom_data=old.use_custom_data;out.mesh=old.mesh;out.custom_aabb=old.custom_aabb;out.physics_interpolation_quality=old.physics_interpolation_quality;out.instance_count=old.instance_count;out.buffer=buffer;out.visible_instance_count=old.visible_instance_count;out.resource_local_to_scene=old.resource_local_to_scene;out.resource_name=old.resource_name;return out
func verify_shape(shape:ConcavePolygonShape3D)->bool:return check(eq(shape.get_faces(),p3(candidate.collider_faces)),"Actual shape.faces equals exact authorized collision replacement")
func empty_second_override(node:MeshInstance3D)->bool:
 return check(node.mesh.get_surface_count()==2 and node.get_surface_override_material_count()==2 and node.get_surface_override_material(1)==null,"New dynamic surface override slot1 is exactly empty; no other node field masked")
func active_materials(node:MeshInstance3D)->Array:
 var out=[]
 for i in node.mesh.get_surface_count():
  audit.resource_cache.clear();out.append(audit.canonical(node.get_active_material(i)))
 return out
func shape_flags(shape:ConcavePolygonShape3D)->Dictionary:return audit.resource_except(shape,["data"])
func mesh_flags(mesh:ArrayMesh)->Array:return [mesh.resource_name,mesh.resource_local_to_scene,mesh.blend_shape_mode,mesh.custom_aabb]
func source_shape_flags()->Dictionary:return {}
func saved_resource_hash(resource:Resource)->String:
 audit.resource_cache.clear();return str(audit.canonical(resource))
func resource_readback(resource:Resource,path:String)->Dictionary:
 var expected=saved_resource_hash(resource)
 if FileAccess.file_exists(path):
  var existing=ResourceLoader.load(path,"",ResourceLoader.CACHE_MODE_IGNORE)
  if not check(existing!=null and saved_resource_hash(existing)==expected,"Refuse overwrite of a nonmatching existing independent resource",path):return {}
 else:
  if not check(ResourceSaver.save(resource,path)==OK,"Independent resource save",path):return {}
 var loaded=ResourceLoader.load(path,"",ResourceLoader.CACHE_MODE_IGNORE)
 if not check(loaded!=null and saved_resource_hash(loaded)==expected,"Strict resource readback canonical identity",path):return {}
 return {"path":path,"sha256":FileAccess.get_sha256(path),"canonical":expected,"class":resource.get_class()}
func immutable_inputs()->bool:
 for path in manifest.immutable_inputs:
  if not check(FileAccess.get_sha256(path)==manifest.immutable_inputs[path],"Immutable source/default/script changed",path):return false
 return true

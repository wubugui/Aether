extends SceneTree
var checks:=[]
var pairs:=[]
var failed:=false
var Audit
var output: String

func record(name: String, passed: bool, details: Variant=null) -> void:
 checks.append({"name":name,"passed":passed,"details":details})
 if not passed: failed=true

func sample(shadow_variant: String="equal") -> ArrayMesh:
 var source:=ArrayMesh.new()
 var points:=PackedVector3Array([Vector3(0,0,0),Vector3(1,0,0),Vector3(0,1,1),Vector3(0,0,0),Vector3(0,1,1),Vector3(-1,1,0)])
 var arrays:=[]; arrays.resize(Mesh.ARRAY_MAX)
 arrays[Mesh.ARRAY_VERTEX]=points
 arrays[Mesh.ARRAY_NORMAL]=PackedVector3Array([Vector3.UP,Vector3.UP,Vector3.UP,Vector3.UP,Vector3.UP,Vector3.UP])
 arrays[Mesh.ARRAY_INDEX]=PackedInt32Array([0,1,2,3,4,5])
 source.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays,[],{3.0:PackedInt32Array([1,2,5])},Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)
 var shadow:=ArrayMesh.new()
 var alt:=[]; alt.resize(Mesh.ARRAY_MAX)
 alt[Mesh.ARRAY_VERTEX]=PackedVector3Array([points[0],points[1],points[2],points[5]])
 alt[Mesh.ARRAY_INDEX]=PackedInt32Array([0,1,2,0,2,3])
 var lods: Dictionary={3.0:PackedInt32Array([1,2,3])}
 if shadow_variant=="winding": alt[Mesh.ARRAY_INDEX]=PackedInt32Array([0,2,1,0,2,3])
 if shadow_variant=="duplicate": alt[Mesh.ARRAY_INDEX]=PackedInt32Array([0,1,2,0,1,2])
 if shadow_variant=="lod_geometry": lods[3.0]=PackedInt32Array([0,1,2])
 if shadow_variant=="extra_lod": lods[5.0]=PackedInt32Array([0,1,2])
 shadow.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,alt,[],lods,Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)
 source.shadow_mesh=shadow
 return source

func _initialize() -> void:
 var args:=OS.get_cmdline_user_args()
 output=args[2]
 Audit=load(args[0])
 if Audit==null or not Audit.can_instantiate(): quit(1); return
 var audit=Audit.new()
 var valid:=sample()
 var result: Dictionary=audit.audit_array_mesh(valid)
 record("equivalent_fused_shadow_with_extra_source_LOD_triangle",not result.is_empty() and result.faces.size()==9,audit.failures)
 var raw: Array=valid.shadow_mesh.get("_surfaces")
 var api: Array=valid.shadow_mesh.surface_get_arrays(0)
 record("fresh_4_5_1_position_only_ARRAY_VERTEX_absent",api[Mesh.ARRAY_VERTEX]==null)
 record("raw_position_only_decode_has_four_vertices",audit.surface_positions(raw[0],"positive").size()==4)
 var shape: Shape3D=audit.indexed_shape(valid)
 record("query_shape_includes_base_and_all_LOD",shape!=null and shape.get_faces().size()==9)
 for kind in ["winding","duplicate","lod_geometry","extra_lod"]:
  var reject=Audit.new()
  var bad:=sample(kind)
  record("reject_"+kind,reject.audit_array_mesh(bad).is_empty() and not reject.failures.is_empty(),reject.failures)
 var bad_raw: Dictionary=raw[0].duplicate(true)
 bad_raw.format=int(bad_raw.format)|(1<<60)
 var unknown=Audit.new()
 record("reject_unknown_format",unknown.surface_positions(bad_raw,"unknown").is_empty() and not unknown.failures.is_empty(),unknown.failures)
 bad_raw=raw[0].duplicate(true)
 bad_raw.vertex_data=bad_raw.vertex_data.slice(0,bad_raw.vertex_data.size()-1)
 var truncated=Audit.new()
 record("reject_truncated_vertices",truncated.surface_positions(bad_raw,"truncated").is_empty(),truncated.failures)
 var malformed=Audit.new()
 record("reject_out_of_range_index",malformed.decoded_indices(PackedByteArray([4,0,0,0,0,0]),3,4,"range").is_empty(),malformed.failures)
 var wide=Audit.new()
 record("index_width_boundary_65536_u16",wide.decoded_indices(PackedByteArray([255,255,0,0,0,0]),3,65536,"u16")==PackedInt32Array([65535,0,0]))
 record("index_width_boundary_65537_u32",wide.decoded_indices(PackedByteArray([0,0,1,0,0,0,0,0,0,0,0,0]),3,65537,"u32")==PackedInt32Array([65536,0,0]))
 audit.close()
 shape=null
 result.clear()
 valid=null
 var fixture: Resource=load(args[1])
 if fixture==null: record("fixture_loaded",false)
 else:
  var meshes: Dictionary=fixture.get_meta("source_meshes")
  record("all_403_native_shadow_pairs_extracted",meshes.size()==403)
  var lod_pairs:=0
  var triangles:=0
  for name in meshes:
   var checker=Audit.new()
   var mesh: ArrayMesh=meshes[name]
   var data: Dictionary=checker.audit_array_mesh(mesh)
   var row: Dictionary={"mesh":name,"passed":not data.is_empty(),"failures":checker.failures}
   if not data.is_empty():
    row.surfaces=data.surfaces
    row.all_base_and_lod_triangles=data.faces.size()/3
    triangles+=row.all_base_and_lod_triangles
    for surface in data.surfaces:
     if surface.levels.size()>1: lod_pairs+=1
   else: failed=true
   pairs.append(row)
  record("all_native_pairs_passed",not failed,{"pairs":pairs.size(),"surfaces_with_lods":lod_pairs,"all_base_and_lod_triangles":triangles})
  record("twelve_native_pairs_have_lods",lod_pairs==12)
  meshes.clear()
 fixture=null
 var report: Dictionary={"version":"orbit61-mesh-audit-v2","engine":Engine.get_version_info(),"passed":not failed,"checks":checks,"native_pairs":pairs,"scope":"Mesh-only headless fixture. No world instantiation, MultiMesh access, scene save, render, camera input or orbit acceptance."}
 var f:=FileAccess.open(output,FileAccess.WRITE)
 f.store_string(JSON.stringify(report,"  ")+"\n"); f.close()
 print("ORBIT61_MESH_AUDIT ",not failed," pairs=",pairs.size()," checks=",checks.size())
 quit(1 if failed else 0)

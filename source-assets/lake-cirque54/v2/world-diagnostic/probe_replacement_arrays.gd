extends "/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v2/world-diagnostic/diagnose_cirque54v2_world.gd"
func _initialize():call_deferred("probe_arrays")
func probe_arrays():
 var base="/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v2/"
 var encodings=JSON.parse_string(FileAccess.get_file_as_string(base+"world-diagnostic/native-mesh-encoding.json"))
 for row in encodings:encoded_color_hashes[row.component]=row.native_color_float32_hex_sha256
 var asset=Node3D.new();asset.position=Vector3(809.494140625,0,-1780);root.add_child(asset)
 var original=MeshInstance3D.new();original.mesh=load("res://assets/lake48/massif_cirque_wall.mesh");asset.add_child(original)
 var old_rows=raw_world_rows(original);var old_count=old_rows.positions.size()/3
 var source=JSON.parse_string(FileAccess.get_file_as_string(PAYLOAD));var material=StandardMaterial3D.new();var parts=[];var protection={}
 for part in source.mountains[0].components:
  var node=MeshInstance3D.new();node.mesh=make_mesh(part,asset.global_transform.affine_inverse(),material);asset.add_child(node)
  parts.append({"component":part.name,"raw_positions_and_native_encoded_rgba_exact":payload_matches(node,part)})
  if part.name=="remodeled_cirque_body":protection=preserved_native_faces(old_rows,raw_world_rows(node))
 var passed=old_count==692 and protection.oriented_native_world_geometry_rgba_exact and parts.all(func(p):return p.raw_positions_and_native_encoded_rgba_exact)
 var report={"scope":"Only isolated old native cirque ArrayMesh and four generated source components. No scene, physics, MultiMesh, camera or GUI run. Actual world raw-array verification remains required.","original_triangles":old_count,"components":parts,"protected_faces":protection,"passed":passed}
 var f=FileAccess.open(base+"world-diagnostic/isolated-replacement-array-proof.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));f.close();print(JSON.stringify(report));asset.free();quit(0 if passed else 1)

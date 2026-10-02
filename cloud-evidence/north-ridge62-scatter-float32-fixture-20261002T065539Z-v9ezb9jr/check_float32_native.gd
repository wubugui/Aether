extends "collect_scatter62.gd"
## Standalone lightweight Godot fixture. No world, scene/resource load or renderer mutation.
var checks: Dictionary = {}

func check(label: String, value: bool) -> void:
	checks[label] = value

func _initialize() -> void:
	var parsed: Array = JSON.parse_string("[1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,-107.0479736328125,14.084564208984375,-168.0250244140625]")
	var known_hex: String = "0000803f0000000000000000000000000000803f0000000000000000000000000000803f9018d6c2605a6141680628c3"
	var exact: Array = Array(known_hex.hex_decode().to_float32_array())
	var known: Dictionary = transform_identity(exact,parsed,known_hex)
	check("known_json_y_float64_1ulp",known.actual_float64_hex.substr(160,16) == "000000004c2b2c40" and known.parsed_expected_float64_hex.substr(160,16) == "010000004c2b2c40" and not known.json_float64_equal)
	check("known_float32_identity_passes",known.passed)
	check("empty_sha256",bytes_sha(PackedByteArray()) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
	check("nonempty_sha256",bytes_sha("abc".to_utf8_buffer()) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
	var one_ulp: PackedByteArray = known_hex.hex_decode()
	one_ulp.encode_u32(0,one_ulp.decode_u32(0)+1)
	check("one_float32_ulp_basis_rejected",not transform_identity(Array(one_ulp.to_float32_array()),parsed,known_hex).passed)
	one_ulp = known_hex.hex_decode()
	one_ulp.encode_u32(40,one_ulp.decode_u32(40)+1)
	check("one_float32_ulp_origin_rejected",not transform_identity(Array(one_ulp.to_float32_array()),parsed,known_hex).passed)
	check("canonical_one_ulp_rejected",not transform_identity(exact,parsed,one_ulp.hex_encode()).passed)
	var nonsymmetric: Transform3D = Transform3D(Basis(Vector3(2,7,17),Vector3(3,11,19),Vector3(5,13,23)),Vector3(101,103,107))
	var n: Array = transform_columns(nonsymmetric)
	var nhex: String = PackedFloat32Array(n).to_byte_array().hex_encode()
	var nwitness: Dictionary = transform_identity(n,n,nhex)
	var transposed: Array = [2.0,3.0,5.0,7.0,11.0,13.0,17.0,19.0,23.0,101.0,103.0,107.0]
	check("transposed_basis_rejected",not transform_identity(transposed,n,nhex).passed)
	var changed: Array = n.duplicate()
	changed[9] = n[10]; changed[10] = n[9]
	check("reordered_origins_rejected",not transform_identity(changed,n,nhex).passed)
	check("wrong_count_rejected",not transform_identity(n.slice(0,11),n,nhex).passed)
	changed = n.duplicate(); changed[0] = NAN
	check("nan_rejected",not transform_identity(changed,n,nhex).passed)
	changed = n.duplicate(); changed[0] = INF
	check("infinity_rejected",not transform_identity(changed,n,nhex).passed)
	changed = n.duplicate(); changed[0] = 1.0e100
	check("float32_overflow_rejected",not transform_identity(changed,n,nhex).passed)
	changed = n.duplicate(); changed[0] = "2"
	check("wrong_type_rejected",not transform_identity(changed,n,nhex).passed)
	check("sub_float32_actual_change_rejected",not transform_identity(parsed,parsed,known_hex).passed)
	check("malformed_hex_rejected",not transform_identity(n,n,nhex.substr(0,95)+"z").passed)
	check("truncated_hex_rejected",not transform_identity(n,n,nhex.substr(0,94)).passed)
	var nr: Dictionary = transform_record(nonsymmetric)
	var native_rows: PackedFloat32Array = PackedFloat32Array([2,3,5,7,11,13,17,19,23,101,103,107])
	check("nonsymmetric_variant_layout",nr.native_variant_hex == "12000000"+native_rows.to_byte_array().hex_encode() and nwitness.passed)
	var passed: bool = issues.is_empty()
	for value in checks.values(): passed = passed and value
	var output: Dictionary = {"passed":passed,"checks":checks,"issues":issues,"known_witness":known,"nonsymmetric_witness":nwitness,"nonsymmetric_transform":nr,"world_loaded":false,"native_collection_passed":false,"all_occupancy_complete":false}
	var file: FileAccess = FileAccess.open(OS.get_environment("SCATTER62_OUTPUT"),FileAccess.WRITE)
	if file == null: printerr("Unable to save lightweight fixture evidence"); quit(2); return
	file.store_string(JSON.stringify(output,"\t",true,true)); file.flush(); file.close()
	print("NORTH62_FLOAT32_FIXTURE_END checks=",checks.size()," passed=",passed)
	quit(0 if passed else 2)

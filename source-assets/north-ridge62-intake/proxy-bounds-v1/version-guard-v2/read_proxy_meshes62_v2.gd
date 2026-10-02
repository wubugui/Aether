extends "../read_proxy_meshes62.gd"
## Override only initialization/version checking. All v1 mesh readers stay unchanged.
const EXPECTED_ENGINE: Dictionary = {"major":4,"minor":5,"patch":1,"status":"stable","build":"official","hash":"f62fdbde15035c5576dad93e586201f4d41ef0cb","hex":263425,"string":"4.5.1-stable (official)","timestamp":0}
const ENGINE_POLICY: String = "strict_fixed_4_5_1_structured_fields_full_commit_hash_v2"

func engine_guard(observed: Dictionary) -> Dictionary:
	var mismatches: Array = []
	for field in EXPECTED_ENGINE:
		var wanted: Variant = EXPECTED_ENGINE[field]
		if not observed.has(field):
			mismatches.append({"field":field,"reason":"missing_field","expected":wanted})
			continue
		var actual: Variant = observed[field]
		if typeof(actual) != typeof(wanted):
			mismatches.append({"field":field,"reason":"type_mismatch","expected":wanted,"observed":actual,"expected_variant_type":typeof(wanted),"observed_variant_type":typeof(actual)})
		elif actual != wanted:
			mismatches.append({"field":field,"reason":"value_mismatch","expected":wanted,"observed":actual})
	var fields: Array = observed.keys()
	fields.sort()
	for field in fields:
		if not EXPECTED_ENGINE.has(field):
			mismatches.append({"field":field,"reason":"unexpected_field","observed":observed[field]})
	return {"policy":ENGINE_POLICY,"expected":EXPECTED_ENGINE.duplicate(true),"passed":mismatches.is_empty(),"mismatches":mismatches}

func _initialize() -> void:
	# Record the entire observed dictionary BEFORE validating any version field.
	var observed: Dictionary = Engine.get_version_info()
	result.engine_version_info = observed.duplicate(true)
	result.engine_version_guard = engine_guard(observed)
	if not result.engine_version_guard.passed:
		for difference in result.engine_version_guard.mismatches:
			issues.append({"kind":"fixed_engine_version_mismatch","diagnostic":difference})
		finish()
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("PROXY62_REQUEST")))
	if not check(parsed is Dictionary,"request JSON missing"): finish(); return
	request = parsed
	if not check(request.get("engine_version_info") is Dictionary and request.get("engine_version_policy") == ENGINE_POLICY and not request.has("engine_version"),"v2 engine request mismatch"): finish(); return
	result.request_sha256 = FileAccess.get_sha256(OS.get_environment("PROXY62_REQUEST"))
	for want in request.visual_meshes:
		read_visual(want)
		if not issues.is_empty(): finish(); return
	read_rock()
	finish()

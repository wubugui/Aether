extends RefCounted
## Exact-copy material factory. No resource or scene saves, no mutation of inputs.
const CLIP_PARAMETER := "lake50_clip_enabled"
var failure := ""
var shader_entries := {}
var native_groups := []
var materials := {}
var shaders := {}
var material_ledger := []
var shader_ledger := []
var fingerprint: Callable
var canonical_value: Callable
var source_root := ""
func reject(message: String) -> bool:
	failure=message;push_error(message);return false
func props(resource: Resource, omit: Array=[]) -> Dictionary:
	var result := {}
	for property in resource.get_property_list():
		var name: String=property.name
		if property.usage & PROPERTY_USAGE_STORAGE and name!="resource_path" and name not in omit: result[name]=resource.get(name)
	return result
func shader_parameters(material: ShaderMaterial) -> Dictionary:
	var result := {}
	for uniform in material.shader.get_shader_uniform_list(): result[str(uniform.name)]=material.get_shader_parameter(uniform.name)
	return result
func configure(root: String, digest_callback: Callable, canonical_callback: Callable) -> bool:
	source_root=root;fingerprint=digest_callback;canonical_value=canonical_callback
	var ledger: Variant=JSON.parse_string(FileAccess.get_file_as_string(root+"/clip-sources/shader-injection-ledger.json"))
	if not ledger is Dictionary or ledger.get("clip_uniform","")!=CLIP_PARAMETER: return reject("Clip injection ledger absent or mismatched")
	for row in ledger.shaders:
		if row.source_sha256!=str(row.original_code).sha256_text() or row.copy_sha256!=str(row.copied_code).sha256_text() or not row.insertion_only_roundtrip_exact: return reject("Invalid shader insertion ledger "+row.source_sha256)
		shader_entries[row.source_sha256]=row
	var first: Variant=JSON.parse_string(FileAccess.get_file_as_string(root+"/../../cloud-evidence/reflection50-material-intake/native-feature-groups.json"))
	var groups: Array=first.groups
	var fourth: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(root+"/../../cloud-evidence/reflection50-material-intake/native-feature-group04-lantern.json"))
	groups.append(fourth)
	var converted := JSON.parse_string(FileAccess.get_file_as_string(root+"/official-native-conversions/conversion-manifest.json")) as Array
	converted.append_array(JSON.parse_string(FileAccess.get_file_as_string(root+"/official-native-conversions/conversion-manifest-group04.json")))
	for i in range(4):
		var group: Dictionary=groups[i]
		var representative: StandardMaterial3D=ResourceLoader.load(group.representative_path,"StandardMaterial3D",ResourceLoader.CACHE_MODE_IGNORE)
		var path := root+"/official-native-conversions/native_group_%02d_shader.tres"%(i+1)
		if representative==null or FileAccess.get_sha256(path)!=str(converted[i].material_sha256): return reject("Native representative or official template hash mismatch group "+str(i+1))
		var template: ShaderMaterial=ResourceLoader.load(path,"ShaderMaterial",ResourceLoader.CACHE_MODE_IGNORE)
		if template==null or template.shader.code.sha256_text()!=str(converted[i].shader_sha256): return reject("Official generated shader SHA mismatch group "+str(i+1))
		# Compare typed actual storage values, including script/null flags. Native
		# identity/localness and albedo are the ONLY varying native properties.
		native_groups.append({"group":i+1,"source_feature_sha256":group.feature_sha256,"feature_state":props(representative,["resource_name","resource_local_to_scene","albedo_color"]),"representative":representative,"representative_path":group.representative_path,"representative_sha256":FileAccess.get_sha256(group.representative_path),"template":template,"template_path":path,"template_sha256":FileAccess.get_sha256(path)})
	return true
func copy_shader(source: Shader) -> Shader:
	var id := source.get_instance_id()
	if shaders.has(id): return shaders[id]
	var sha := source.code.sha256_text()
	if not shader_entries.has(sha): reject("Unknown shader code; refuse approximate injection "+sha);return null
	var row: Dictionary=shader_entries[sha]
	var copy := source.duplicate(false) as Shader
	copy.code=row.copied_code
	if props(source,["code"])!=props(copy,["code"]): reject("Shader copy changed non-code stored properties");return null
	var exported := row.duplicate(true)
	exported.source_resource_path=source.resource_path
	exported.source_resource_name=source.resource_name
	exported.stored_flags_fingerprint=fingerprint.call(canonical_value.call(props(source,["code"])))
	exported.output_resource_instance_id=copy.get_instance_id()
	shader_ledger.append(exported);shaders[id]=copy
	return copy
func copy_material(source: Material) -> ShaderMaterial:
	if source==null: reject("Missing target material");return null
	var id := source.get_instance_id()
	if materials.has(id): return materials[id]
	var copy: ShaderMaterial
	var record := {"source_path":source.resource_path,"source_class":source.get_class(),"source_name":source.resource_name,"source_local_to_scene":source.resource_local_to_scene,"source_fingerprint":fingerprint.call(canonical_value.call(source))}
	if source is ShaderMaterial:
		copy=source.duplicate(false)
		copy.shader=copy_shader(source.shader)
		if copy.shader==null: return null
		copy.set_shader_parameter(CLIP_PARAMETER,false)
		if canonical_value.call(props(source,["shader"]))!=canonical_value.call(props(copy,["shader","shader_parameter/"+CLIP_PARAMETER])):
			reject("Copied ShaderMaterial changed original stored uniform/flags "+source.resource_path);return null
		var old_parameters := shader_parameters(source)
		var actual_parameters := shader_parameters(copy)
		actual_parameters.erase(CLIP_PARAMETER)
		if canonical_value.call(old_parameters)!=canonical_value.call(actual_parameters): reject("Copied ShaderMaterial changed declared uniform values "+source.resource_path);return null
		record.mode="exact_shader_copy_with_clip_insertions"
		record.original_uniforms=canonical_value.call(old_parameters)
		record.new_uniforms_excluding_clip=canonical_value.call(actual_parameters)
		record.old_shader_sha256=source.shader.code.sha256_text()
	elif source is StandardMaterial3D:
		var feature := props(source,["resource_name","resource_local_to_scene","albedo_color"])
		var match_group := {}
		for group in native_groups:
			if feature==group.feature_state: match_group=group;break
		if match_group.is_empty(): reject("Unknown exact native feature set: "+source.resource_path+" "+str(fingerprint.call(canonical_value.call(feature))));return null
		var template: ShaderMaterial=match_group.template
		copy=template.duplicate(false)
		copy.resource_name=source.resource_name
		copy.resource_local_to_scene=source.resource_local_to_scene
		copy.set_shader_parameter("albedo",source.albedo_color)
		copy.shader=copy_shader(template.shader)
		if copy.shader==null: return null
		copy.set_shader_parameter(CLIP_PARAMETER,false)
		var omitted := ["shader","resource_name","resource_local_to_scene","shader_parameter/albedo","shader_parameter/"+CLIP_PARAMETER]
		if canonical_value.call(props(template,omitted))!=canonical_value.call(props(copy,omitted)): reject("Official template changed beyond albedo/identity/clip");return null
		if copy.get_shader_parameter("albedo")!=source.albedo_color: reject("Native albedo/alpha failed exact transfer");return null
		record.mode="official_native_shader_conversion_only"
		record.native_group=match_group.group
		record.native_feature_sha256=match_group.source_feature_sha256
		record.native_typed_feature_fingerprint=fingerprint.call(canonical_value.call(feature))
		record.native_feature_properties=canonical_value.call(feature)
		record.representative_sha256=match_group.representative_sha256
		record.official_template_sha256=match_group.template_sha256
		record.original_albedo=canonical_value.call(source.albedo_color)
		record.original_template_uniforms=canonical_value.call(shader_parameters(template))
		record.new_uniforms=canonical_value.call(shader_parameters(copy))
		record.old_shader_sha256=template.shader.code.sha256_text()
	else: reject("Unsupported material class "+source.get_class());return null
	record.new_shader_sha256=copy.shader.code.sha256_text()
	record.new_fingerprint=fingerprint.call(canonical_value.call(copy))
	record.output_resource_instance_id=copy.get_instance_id()
	record.clip_default=false
	material_ledger.append(record);materials[id]=copy
	return copy

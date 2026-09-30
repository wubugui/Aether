extends RefCounted
## Avoid Resource.duplicate() property-order dependence for allocated MultiMeshes.
## Flags must be set before allocating; copy through typed accessors afterwards.
static func copy(source: MultiMesh) -> MultiMesh:
	assert(source != null)
	var result := MultiMesh.new()
	result.transform_format = source.transform_format
	result.use_colors = source.use_colors
	result.use_custom_data = source.use_custom_data
	result.mesh = source.mesh
	result.custom_aabb = source.custom_aabb
	result.physics_interpolation_quality = source.physics_interpolation_quality
	result.instance_count = source.instance_count
	for i in range(source.instance_count):
		if source.transform_format == MultiMesh.TRANSFORM_3D:
			result.set_instance_transform(i, source.get_instance_transform(i))
		else:
			result.set_instance_transform_2d(i, source.get_instance_transform_2d(i))
		if source.use_colors:
			result.set_instance_color(i, source.get_instance_color(i))
		if source.use_custom_data:
			result.set_instance_custom_data(i, source.get_instance_custom_data(i))
	result.visible_instance_count = source.visible_instance_count
	result.resource_local_to_scene = source.resource_local_to_scene
	result.resource_name = source.resource_name
	return result

static func equivalent(source: MultiMesh, result: MultiMesh) -> bool:
	if source == result or source.transform_format != result.transform_format:
		return false
	if source.use_colors != result.use_colors or source.use_custom_data != result.use_custom_data:
		return false
	if source.instance_count != result.instance_count or source.visible_instance_count != result.visible_instance_count:
		return false
	if source.mesh != result.mesh or source.custom_aabb != result.custom_aabb:
		return false
	for i in range(source.instance_count):
		if source.transform_format == MultiMesh.TRANSFORM_3D:
			if not source.get_instance_transform(i).is_equal_approx(result.get_instance_transform(i)):
				return false
		elif not source.get_instance_transform_2d(i).is_equal_approx(result.get_instance_transform_2d(i)):
			return false
		if source.use_colors and not source.get_instance_color(i).is_equal_approx(result.get_instance_color(i)):
			return false
		if source.use_custom_data and not source.get_instance_custom_data(i).is_equal_approx(result.get_instance_custom_data(i)):
			return false
	return true

static func restore_weather_custom_data(result: MultiMesh) -> void:
	# Historical 42b/42c weather resources omitted buffers entirely. Recover
	# their authored custom payload from build_weather42b's exact RNG sequence.
	assert(result.use_custom_data)
	var rng := RandomNumberGenerator.new()
	rng.seed = 4200 + result.instance_count
	for i in range(result.instance_count):
		rng.randf_range(-110,110) # original X
		rng.randf_range(-110,110) # original Z
		result.set_instance_custom_data(i,Color(rng.randf_range(0,160),rng.randf(),0,1))

static func place_weather42c(result: MultiMesh) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 4242 + result.instance_count
	for i in range(result.instance_count):
		result.set_instance_transform(i,Transform3D(Basis.IDENTITY,Vector3(rng.randf_range(-110,110),rng.randf_range(-80,80),rng.randf_range(-110,110))))

extends SceneTree
const MultiMeshCopy = preload('res://tools/multimesh_copy42d.gd')
var failures := 0
var checks := 0
func _initialize() -> void: call_deferred('run')
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures += 1
	print('PASS ' if ok else 'FAIL ', label)
func run() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("A real rendering server is required: headless dummy rendering cannot validate or preserve MultiMesh instance buffers")
		quit(2)
		return
	# Cross-product protects optional payloads and zero-count allocation.
	for format in [MultiMesh.TRANSFORM_2D, MultiMesh.TRANSFORM_3D]:
		for colors in [false, true]:
			for custom in [false, true]:
				for count in [0, 3]:
					var source := MultiMesh.new()
					source.transform_format = format
					source.use_colors = colors
					source.use_custom_data = custom
					source.mesh = BoxMesh.new()
					source.custom_aabb = AABB(Vector3(-4,-5,-6),Vector3(8,10,12))
					source.instance_count = count
					for i in range(count):
						if format == MultiMesh.TRANSFORM_3D:
							source.set_instance_transform(i,Transform3D(Basis(Vector3.UP,.2*i).scaled(Vector3(1,2,3)),Vector3(i,10+i,-i)))
						else:
							source.set_instance_transform_2d(i,Transform2D(.2*i,Vector2(3+i,-i)))
						if colors: source.set_instance_color(i,Color(.1*i,.3,.4,.5))
						if custom: source.set_instance_custom_data(i,Color(20+i,.2*i,-.4,1))
					for visible_count in [-1, 0, count]:
						source.visible_instance_count = visible_count
						var result: MultiMesh = MultiMeshCopy.copy(source)
						check(MultiMeshCopy.equivalent(source,result),'copy format=%s colors=%s custom=%s count=%s visible=%s' % [format,colors,custom,count,visible_count])
						var stride := (12 if format == MultiMesh.TRANSFORM_3D else 8) + (4 if colors else 0) + (4 if custom else 0)
						check(result.buffer.size() == count*stride,'allocated buffer matches enabled payload stride')
	# Read the actual two source declarations without loading the full 99 MiB
	# world/sky/textures into this allocation unit test. Require the observed
	# missing-buffer schema explicitly instead of assuming source data exists.
	var scene_text := FileAccess.get_file_as_string('res://scenes/candidate42b/Game42b.tscn')
	for entry in [{'name':'Rain','count':1800},{'name':'Snow','count':1200}]:
		var declaration := ''
		for section in scene_text.split('\n\n'):
			if section.begins_with('[sub_resource type="MultiMesh"') and section.contains('instance_count = '+str(entry.count)+'\n'):
				declaration = section
		var schema_ok := declaration.contains('transform_format = 1\n') and declaration.contains('use_custom_data = true\n') and not declaration.contains('buffer =') and not declaration.contains('_array =')
		check(schema_ok,'historical '+entry.name+' source declaration confirms absent buffer')
		var source := MultiMesh.new()
		source.transform_format = MultiMesh.TRANSFORM_3D
		source.use_custom_data = true
		source.instance_count = entry.count
		var result: MultiMesh = MultiMeshCopy.copy(source)
		MultiMeshCopy.restore_weather_custom_data(result)
		MultiMeshCopy.place_weather42c(result)
		var restored := result.get_instance_custom_data(0)
		check(restored.r > 0 and restored.a == 1.0 and result.get_instance_transform(0).basis.is_equal_approx(Basis.IDENTITY),'authored '+entry.name+' seeded payload and nondegenerate transform recovered')
	print('MULTIMESH42D ',checks-failures,'/',checks,' passed')
	call_deferred('finish')

func finish() -> void:
	for i in range(8): await process_frame
	quit(0 if failures == 0 else 1)

extends SceneTree
const DEST := 'res://scenes/candidate42d/'
const MultiMeshCopy = preload('res://tools/multimesh_copy42d.gd')
func _initialize() -> void:call_deferred('build')
func own(node: Node,root_node: Node) -> void:
	node.scene_file_path=''
	if node!=root_node:node.owner=root_node
	for child in node.get_children():own(child,root_node)
func build() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("A real rendering server is required: headless dummy rendering cannot validate or preserve MultiMesh instance buffers")
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(DEST)
	assert(not FileAccess.file_exists(DEST+'Game42d.tscn'))
	var game: Node3D=load('res://scenes/candidate42b/Game42b.tscn').instantiate()
	var weather: Node3D=game.get_node('Weather42b');weather.set_script(load('res://scripts/weather42c.gd'))
	for name in ['Rain','Snow']:
		var node: MultiMeshInstance3D=weather.get_node(name)
		var original: MultiMesh=node.multimesh
		var multi: MultiMesh=MultiMeshCopy.copy(original)
		assert(MultiMeshCopy.equivalent(original,multi), "Allocation-safe copy must preserve every instance payload")
		var old_mesh: Mesh=multi.mesh
		var scale_factor:=.28 if name=='Rain' else .45
		var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
		st.append_from(old_mesh,0,Transform3D(Basis.IDENTITY.scaled(Vector3.ONE*scale_factor),Vector3.ZERO))
		multi.mesh=st.commit()
		MultiMeshCopy.restore_weather_custom_data(multi)
		MultiMeshCopy.place_weather42c(multi)
		node.multimesh=multi
		var shader:=Shader.new()
		shader.code='shader_type spatial; render_mode blend_mix,depth_draw_never,cull_disabled; uniform vec3 tint; uniform float precipitation_time=0.; void fragment(){float eye_distance=length(VERTEX);float fade=smoothstep(8.,18.,eye_distance);ALBEDO=tint;ROUGHNESS=1.;ALPHA=.48*fade;if(ALPHA<.01)discard;}'
		var material:=ShaderMaterial.new();material.shader=shader;material.set_shader_parameter('tint',Vector3(.47,.59,.73) if name=='Rain' else Vector3(.90,.94,1))
		node.material_override=material
	for i in range(3): await process_frame
	own(game,game)
	var packed:=PackedScene.new();assert(packed.pack(game)==OK)
	assert(ResourceSaver.save(packed,DEST+'Game42d.tscn')==OK)
	var reloaded: Node3D = ResourceLoader.load(DEST+'Game42d.tscn','PackedScene',ResourceLoader.CACHE_MODE_IGNORE).instantiate()
	for name in ['Rain','Snow']:
		var built: MultiMesh = game.get_node('Weather42b/'+name).multimesh
		var restored: MultiMesh = reloaded.get_node('Weather42b/'+name).multimesh
		assert(restored.buffer.size() == built.instance_count*16, 'Serialized weather buffer must exist')
		assert(restored.buffer == built.buffer, 'Saved/reloaded weather payload must match every float')
		assert(restored.get_instance_transform(0).basis.is_equal_approx(Basis.IDENTITY),'Serialized particle basis must be nondegenerate')
	# Godot 4.5.1 GLES3 Sky dirty-list processing must finish before disposal.
	# This settles only renderer resources; the game never enters the live tree.
	for i in range(3): await process_frame
	await RenderingServer.frame_post_draw
	reloaded.free()
	var report:={'baseline_sha256':FileAccess.get_sha256('res://scenes/candidate42b/Game42b.tscn'),'candidate_sha256':FileAccess.get_sha256(DEST+'Game42d.tscn'),'prior_candidate_sha256':FileAccess.get_sha256('res://scenes/candidate42c/Game42c.tscn'),'allocation_fix':'Explicit flags before instance_count; accessor copy preserves transforms, colors and custom data. Historical 42b/42c weather buffers were absent; recover authored custom payload from 42b seed and placement from 42c seed. Serialized buffers checked by full reload equality.','scope':'Preserved full world and weather; actual particle transforms replace vertex deformation; native mesh scaling and physically near-eye transparency fade. No camera movement or geometry removal.'}
	var file:=FileAccess.open(DEST+'build-report42d.json',FileAccess.WRITE);file.store_string(JSON.stringify(report,'  '));file.close()
	game.free();print('PARTICLES42D BUILT ',report.candidate_sha256);call_deferred('finish')

func finish() -> void:
	for i in range(8): await process_frame
	quit()

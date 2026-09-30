extends SceneTree
const DEST := 'res://scenes/candidate42c/'
func _initialize() -> void:call_deferred('build')
func own(node: Node,root_node: Node) -> void:
	node.scene_file_path=''
	if node!=root_node:node.owner=root_node
	for child in node.get_children():own(child,root_node)
func build() -> void:
	DirAccess.make_dir_recursive_absolute(DEST)
	assert(not FileAccess.file_exists(DEST+'Game42c.tscn'))
	var game: Node3D=load('res://scenes/candidate42b/Game42b.tscn').instantiate()
	var weather: Node3D=game.get_node('Weather42b');weather.set_script(load('res://scripts/weather42c.gd'))
	for name in ['Rain','Snow']:
		var node: MultiMeshInstance3D=weather.get_node(name)
		var multi: MultiMesh=node.multimesh.duplicate()
		var old_mesh: Mesh=multi.mesh
		var scale_factor:=.28 if name=='Rain' else .45
		var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
		st.append_from(old_mesh,0,Transform3D(Basis.IDENTITY.scaled(Vector3.ONE*scale_factor),Vector3.ZERO))
		multi.mesh=st.commit()
		var rng:=RandomNumberGenerator.new();rng.seed=4242+multi.instance_count
		for i in range(multi.instance_count):multi.set_instance_transform(i,Transform3D(Basis.IDENTITY,Vector3(rng.randf_range(-110,110),rng.randf_range(-80,80),rng.randf_range(-110,110))))
		node.multimesh=multi
		var shader:=Shader.new()
		shader.code='shader_type spatial; render_mode blend_mix,depth_draw_never,cull_disabled; uniform vec3 tint; uniform float precipitation_time=0.; void fragment(){float eye_distance=length(VERTEX);float fade=smoothstep(8.,18.,eye_distance);ALBEDO=tint;ROUGHNESS=1.;ALPHA=.48*fade;if(ALPHA<.01)discard;}'
		var material:=ShaderMaterial.new();material.shader=shader;material.set_shader_parameter('tint',Vector3(.47,.59,.73) if name=='Rain' else Vector3(.90,.94,1))
		node.material_override=material
	own(game,game)
	var packed:=PackedScene.new();assert(packed.pack(game)==OK)
	assert(ResourceSaver.save(packed,DEST+'Game42c.tscn')==OK)
	var report:={'baseline_sha256':FileAccess.get_sha256('res://scenes/candidate42b/Game42b.tscn'),'candidate_sha256':FileAccess.get_sha256(DEST+'Game42c.tscn'),'scope':'Preserved full world and weather; actual particle transforms replace vertex deformation; native mesh scaling and physically near-eye transparency fade. No camera movement or geometry removal.'}
	var file:=FileAccess.open(DEST+'build-report42c.json',FileAccess.WRITE);file.store_string(JSON.stringify(report,'  '));file.close()
	game.free();print('PARTICLES42C BUILT ',report.candidate_sha256);quit()

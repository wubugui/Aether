extends SceneTree
const DEST := "res://scenes/candidate42b/"
var asset_reports: Array = []
func _initialize() -> void: call_deferred('build')
func own(node: Node, root_node: Node) -> void:
	node.scene_file_path = ''
	if node != root_node: node.owner = root_node
	for child in node.get_children(): own(child,root_node)
func source(name: String) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	assert(doc.append_from_file('res://assets/weather42b/'+name+'.glb',state)==OK)
	var node: Node3D = doc.generate_scene(state)
	asset_reports.append({'name':name,'sha256':FileAccess.get_sha256('res://assets/weather42b/'+name+'.glb'),'parts':node.find_children('*','MeshInstance3D',true,false).size()})
	own(node,node)
	var packed := PackedScene.new();assert(packed.pack(node)==OK)
	assert(ResourceSaver.save(packed,DEST+name+'.tscn')==OK)
	return node
func particles(name: String, model: Node3D, count: int, speed: float, drift: float, tint: Vector3) -> MultiMeshInstance3D:
	var nodes: Array = model.find_children('*','MeshInstance3D',true,false)
	assert(nodes.size()==1)
	var multi := MultiMesh.new();multi.transform_format=MultiMesh.TRANSFORM_3D
	multi.use_custom_data=true;multi.mesh=nodes[0].mesh;multi.instance_count=count
	var rng := RandomNumberGenerator.new();rng.seed=4200+count
	for i in range(count):
		multi.set_instance_transform(i,Transform3D(Basis.IDENTITY,Vector3(rng.randf_range(-110,110),80,rng.randf_range(-110,110))))
		multi.set_instance_custom_data(i,Color(rng.randf_range(0,160),rng.randf(),0,1))
	var shader := Shader.new()
	shader.code='shader_type spatial; render_mode blend_mix,depth_draw_never,cull_disabled; uniform float precipitation_time=0.; uniform float fall_speed; uniform float drift; uniform vec3 tint; void vertex(){float fall=mod(precipitation_time*fall_speed+INSTANCE_CUSTOM.x,160.);VERTEX.y-=fall;VERTEX.x+=fall*drift+sin(precipitation_time+INSTANCE_CUSTOM.y*6.28)*2.;} void fragment(){ALBEDO=tint;ROUGHNESS=1.;ALPHA=.68;}'
	var mat := ShaderMaterial.new();mat.shader=shader
	mat.set_shader_parameter('fall_speed',speed);mat.set_shader_parameter('drift',drift);mat.set_shader_parameter('tint',tint)
	var node := MultiMeshInstance3D.new();node.name=name;node.multimesh=multi;node.material_override=mat
	node.custom_aabb=AABB(Vector3(-160,-85,-115),Vector3(320,175,230));node.visible=false
	return node
func build() -> void:
	DirAccess.make_dir_recursive_absolute(DEST)
	assert(not FileAccess.file_exists(DEST+'Game42b.tscn'))
	var rain := source('rain_streak42b');var snow := source('snow_crystal42b')
	var rainbow := source('rainbow42b');var bolts: Array[Node3D] = []
	for i in range(3): bolts.append(source('lightning42b_'+str(i)))
	var game: Node3D = load('res://scenes/candidate41b/Game41b.tscn').instantiate()
	game.set_script(load('res://scripts/game42b.gd'))
	var environment: Node = game.get_node('SceneEnvironment40')
	environment.name='SceneEnvironment42b';environment.set_script(load('res://scripts/environment42b.gd'))
	var region: Node3D = game.get_node('SkyRegion39')
	var replaced := 0
	for old in region.get_children():
		if not str(old.name).begins_with('UpperCloudBank41_'): continue
		var replacement: Node3D = load('res://scenes/candidate41b/cloud_sea_41_'+str(replaced%3)+'.tscn').instantiate()
		replacement.name=old.name;replacement.position=old.position;replacement.rotation=old.rotation
		replacement.scale=Vector3(2.0,1.1,1.4)
		region.remove_child(old);old.free();region.add_child(replacement);replaced+=1
	var weather := Node3D.new();weather.name='Weather42b';weather.set_script(load('res://scripts/weather42b.gd'));game.add_child(weather)
	weather.add_child(particles('Rain',rain,1800,36,.22,Vector3(.45,.58,.70)))
	weather.add_child(particles('Snow',snow,1200,5,.12,Vector3(.89,.94,1)))
	rainbow.name='Rainbow';rainbow.position=Vector3(-2300,-250,-3900);rainbow.visible=false;weather.add_child(rainbow)
	for mesh in rainbow.find_children('*','MeshInstance3D',true,false):
		var existing: StandardMaterial3D = mesh.mesh.surface_get_material(0)
		var mat: StandardMaterial3D = existing.duplicate()
		mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;mat.albedo_color.a=.35
		mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;mat.cull_mode=BaseMaterial3D.CULL_DISABLED
		mesh.material_override=mat
	for zone_name in ['CoastalStorm','CloudStorm']:
		var zone := Node3D.new();zone.name=zone_name;weather.add_child(zone)
		for i in range(3):
			var bolt: Node3D = bolts[i].duplicate();bolt.name='Bolt_'+str(i);bolt.visible=false
			bolt.position=Vector3(-3100-i*700,750+i*40,-3500-i*700) if zone_name=='CoastalStorm' else Vector3(3750+i*750,925,3100-i*300)
			zone.add_child(bolt)
			for mesh in bolt.find_children('*','MeshInstance3D',true,false):
				var mat := StandardMaterial3D.new();mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
				mat.albedo_color=Color(.95,.78,1);mat.emission_enabled=true;mat.emission=mat.albedo_color;mat.emission_energy_multiplier=3
				mesh.material_override=mat
			var lamp := OmniLight3D.new();lamp.name='LightningLocal_'+str(i)
			lamp.position=bolt.position+Vector3(0,-140,0);lamp.omni_range=480;lamp.light_color=Color(.85,.62,1);lamp.light_energy=0
			zone.add_child(lamp)
	rain.free();snow.free()
	for bolt in bolts:bolt.free()
	own(game,game)
	var packed := PackedScene.new();assert(packed.pack(game)==OK)
	assert(ResourceSaver.save(packed,DEST+'Game42b.tscn')==OK)
	var report := {'baseline_sha256':FileAccess.get_sha256('res://scenes/candidate41b/Game41b.tscn'),'candidate_sha256':FileAccess.get_sha256(DEST+'Game42b.tscn'),'upper_clouds_rebuilt':replaced,'weather_sources':asset_reports,'rain_instances':1800,'snow_instances':1200,'spatial_bolts':6,'scope':'Preserved world/cabins/islands; real upper cloud thickness, shared night lighting and editable native weather controlled in live game.'}
	var file := FileAccess.open(DEST+'build-report42b.json',FileAccess.WRITE);file.store_string(JSON.stringify(report,'  '));file.close()
	game.free();print('WEATHER42B BUILT ',report.candidate_sha256);quit()

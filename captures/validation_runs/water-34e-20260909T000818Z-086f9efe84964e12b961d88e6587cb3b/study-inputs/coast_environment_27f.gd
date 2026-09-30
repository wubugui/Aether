extends RefCounted
## Actual scene/material lighting experiment. The caller owns the temporary game.
var folder:String
var night:bool
var material_cache:Dictionary={}
var shader_cache:Dictionary={}
var bindings:Array=[]
var unmapped_shaders:Array=[]
var light_records:Array=[]
var emissive_surfaces:int=0
var water_reflection_bindings:Array=[]
const MOON=Vector3(-.184,.38,-.907)
func shader_from(name:String) -> Shader:
	if shader_cache.has(name):return shader_cache[name]
	var shader:=Shader.new();shader.code=FileAccess.get_file_as_string(folder.path_join(name+".gdshader"))
	assert(not shader.code.is_empty());shader_cache[name]=shader;return shader
func adapted(source:Material) -> Material:
	if source==null:return null
	var key:=source.get_instance_id()
	if material_cache.has(key):return material_cache[key]
	var result:Material=source
	if source is ShaderMaterial:
		var original:String=source.shader.resource_path.get_file().get_basename()
		if FileAccess.file_exists(folder.path_join(original+".gdshader")):
			result=source.duplicate();result.shader=shader_from(original)
			result.set_shader_parameter("study_night",1. if night else 0.)
			result.set_shader_parameter("study_fill",Vector3(.22,.32,.60) if night else Vector3.ONE)
			result.set_shader_parameter("study_haze",Vector3(.018,.045,.13) if night else Vector3(.40,.53,.65))
			result.set_shader_parameter("moon_direction",MOON.normalized())
			bindings.append({"original_shader":source.shader.resource_path,"candidate_shader":original+".gdshader","original_material":source.resource_path})
		elif not shader_cache.values().has(source.shader) and not unmapped_shaders.has(source.shader.resource_path):
			unmapped_shaders.append(source.shader.resource_path)
	elif source is StandardMaterial3D and night:
		if source.resource_name.contains("Keeper window glass"):
			result=source.duplicate();result.emission_enabled=true;result.emission=Color(1.,.38,.065);result.emission_energy_multiplier=.8;emissive_surfaces+=1
		elif source.resource_name.contains("Lamp core"):
			result=source.duplicate();result.emission_enabled=true;result.emission=Color(1.,.42,.07);result.emission_energy_multiplier=2.;emissive_surfaces+=1
	material_cache[key]=result;return result
func configure(game:Node3D,region:Node3D,input_folder:String,is_night:bool) -> Dictionary:
	folder=input_folder;night=is_night
	var environment:Environment=game.get_node("Environment").environment.duplicate(true)
	game.get_node("Environment").environment=environment
	var sky_material:=ShaderMaterial.new();sky_material.shader=shader_from("open_sky")
	sky_material.set_shader_parameter("study_night",1. if night else 0.)
	sky_material.set_shader_parameter("moon_direction",MOON.normalized())
	environment.sky.sky_material=sky_material
	var sun:DirectionalLight3D=game.get_node("Sun")
	if night:
		sun.look_at(sun.global_position-MOON.normalized(),Vector3.UP)
		sun.light_color=Color(.50,.63,1.);sun.light_energy=.85;sun.shadow_opacity=.75
		environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
		environment.ambient_light_color=Color(.36,.46,.70);environment.ambient_light_energy=1.0
		environment.fog_light_color=Color(.045,.09,.20);environment.fog_density=.00038
	for node in game.find_children("*","GeometryInstance3D",true,false):
		if node.material_override!=null:node.material_override=adapted(node.material_override)
		if node is MeshInstance3D and node.mesh!=null:
			for index in range(node.mesh.get_surface_count()):
				var source:Material=node.get_active_material(index)
				if source!=null:node.set_surface_override_material(index,adapted(source))
		elif node is MultiMeshInstance3D and node.multimesh!=null and node.material_override==null:
			var multi:MultiMesh=node.multimesh.duplicate();multi.mesh=multi.mesh.duplicate()
			for index in range(multi.mesh.get_surface_count()):multi.mesh.surface_set_material(index,adapted(multi.mesh.surface_get_material(index)))
			node.multimesh=multi
	var sky_assets:=Node3D.new();sky_assets.name="NativeCoastalSky27f";game.add_child(sky_assets)
	var asset_records:Array=[]
	var cloud_positions:Array=[[-3376.25328, 660.28843, -148.35449, 4.6, 2, 1.0], [-1404.38293, 781.76074, -1883.21798, 3.7, 1, 1.0], [-2194.46176, 699.47833, -3038.5317, 7.0, 1, 0.55], [1070.99498, 1014.64244, -4150.91888, 5.6, 1, 1.0], [97.10955, 631.88721, -2802.91106, 3.2, 2, 1.0], [1533.83301, 612.24635, -5382.75595, 6.5, 1, 0.78], [-4656.20507, 505.7129, -537.066, 4.2, 2, 0.7]]
	for item in cloud_positions:
		var document:=GLTFDocument.new();var state:=GLTFState.new()
		var asset_name:String="cloud_bank_"+str(item[4])
		assert(document.append_from_file(folder.path_join("sky-assets/"+asset_name+".glb"),state)==OK)
		var node:Node3D=document.generate_scene(state);sky_assets.add_child(node)
		node.position=Vector3(-2350+item[0],item[1],-1650+item[2]);node.scale=Vector3(float(item[3]),float(item[3])*float(item[5]),float(item[3]));node.rotation.y=.35
		var vapor:=ShaderMaterial.new();vapor.shader=shader_from("cloud_surface")
		vapor.set_shader_parameter("study_night",1. if night else 0.);vapor.set_shader_parameter("moon_direction",MOON.normalized())
		for mesh in node.find_children("*","MeshInstance3D",true,false):mesh.material_override=vapor
		asset_records.append({"asset":asset_name,"position":[node.position.x,node.position.y,node.position.z],"scale":[node.scale.x,node.scale.y,node.scale.z]})
	if night:
		var document:=GLTFDocument.new();var state:=GLTFState.new()
		assert(document.append_from_file(folder.path_join("sky-assets/moon.glb"),state)==OK)
		var moon:Node3D=document.generate_scene(state);sky_assets.add_child(moon)
		moon.position=Vector3(-2278,60,-1632)+MOON.normalized()*9000.
		var seen_water_materials:Dictionary={}
		for material in material_cache.values():
			if material is ShaderMaterial and material.shader==shader_cache.get("open_water"):
				if seen_water_materials.has(material.get_instance_id()):continue
				seen_water_materials[material.get_instance_id()]=true
				material.set_shader_parameter("moon_world_center",moon.global_position)
				material.set_shader_parameter("moon_world_radius",330.)
				var actual:Vector3=material.get_shader_parameter("moon_world_center")
				assert(actual.is_equal_approx(moon.global_position))
				water_reflection_bindings.append({"material_instance_id":material.get_instance_id(),"moon_node":str(moon.get_path()),"center":[actual.x,actual.y,actual.z],"radius_m":material.get_shader_parameter("moon_world_radius"),"scope":"Actual world sphere bound to each water material; per-water-point incident ray in shader."})
		assert(not water_reflection_bindings.is_empty())
		for mesh in moon.find_children("*","MeshInstance3D",true,false):
			for index in range(mesh.mesh.get_surface_count()):
				var source:Material=mesh.mesh.surface_get_material(index)
				var shade:int=int(source.resource_name.get_slice(" ",2))
				var lunar:=ShaderMaterial.new();lunar.shader=shader_from("moon")
				lunar.set_shader_parameter("moon_color",Vector3(.40+shade*.055,.46+shade*.055,.64+shade*.05))
				mesh.set_surface_override_material(index,lunar)
		asset_records.append({"asset":"moon","position":[moon.position.x,moon.position.y,moon.position.z],"radius_m":330.,"scope":"Fixed world position near9000m; angular direction matches reference-camera moon light, finite-distance approximation during flight."})
	if night:
		for tower in region.get_children():
			if not str(tower.name).begins_with("Lighthouse_"):continue
			# Saved19h lamp center: authored23.20m minus the3.60m shaft compression.
			var lamp:=OmniLight3D.new();lamp.name="NativeLanternLight";lamp.position=Vector3(0,19.60,0)
			lamp.light_color=Color(1.,.48,.12);lamp.light_energy=2.;lamp.omni_range=13.;lamp.omni_attenuation=1.5
			tower.add_child(lamp)
			light_records.append({"node":str(lamp.get_path()),"position":[lamp.global_position.x,lamp.global_position.y,lamp.global_position.z],"energy":lamp.light_energy,"range_m":lamp.omni_range})
	return {"water_reflection_bindings":water_reflection_bindings,"unmapped_shader_paths":unmapped_shaders,"local_light_records":light_records,"ambient_source":environment.ambient_light_source,"ambient_color":[environment.ambient_light_color.r,environment.ambient_light_color.g,environment.ambient_light_color.b],"native_sky_assets":asset_records,"night":night,"moon_direction":[MOON.normalized().x,MOON.normalized().y,MOON.normalized().z],"directional_light_energy":sun.light_energy,"ambient_energy":environment.ambient_light_energy,"fog_density":environment.fog_density,"material_bindings":bindings,"emissive_material_variants":emissive_surfaces,"scope":"27f actual cloud geometry, cloud transmission/haze and irregular world-water normals;21c lights and moon retained. No fullscreen tint. Beams, streaming transitions and other weather states remain unimplemented."}

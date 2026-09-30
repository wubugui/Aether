extends RefCounted
## Actual scene/material lighting experiment. The caller owns the temporary game.
var folder:String
var night:bool
var material_cache:Dictionary={}
var shader_cache:Dictionary={}
var bindings:Array=[]
var emissive_surfaces:int=0
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
			result.set_shader_parameter("study_fill",Vector3(.055,.085,.18) if night else Vector3.ONE)
			result.set_shader_parameter("study_haze",Vector3(.008,.024,.065) if night else Vector3(.40,.53,.65))
			result.set_shader_parameter("moon_direction",MOON.normalized())
			bindings.append({"original_shader":source.shader.resource_path,"candidate_shader":original+".gdshader","original_material":source.resource_path})
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
		sun.light_color=Color(.40,.53,1.);sun.light_energy=.50;sun.shadow_opacity=.75
		environment.ambient_light_color=Color(.15,.23,.43);environment.ambient_light_energy=.28
		environment.fog_light_color=Color(.020,.049,.115);environment.fog_density=.00038
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
	if night:
		for tower in region.get_children():
			if not str(tower.name).begins_with("Lighthouse_"):continue
			# Saved19h lamp center: authored23.20m minus the3.60m shaft compression.
			var lamp:=OmniLight3D.new();lamp.name="NativeLanternLight";lamp.position=Vector3(0,19.60,0)
			lamp.light_color=Color(1.,.48,.12);lamp.light_energy=2.;lamp.omni_range=13.;lamp.omni_attenuation=1.5
			tower.add_child(lamp)
	return {"night":night,"moon_direction":[MOON.normalized().x,MOON.normalized().y,MOON.normalized().z],"directional_light_energy":sun.light_energy,"ambient_energy":environment.ambient_light_energy,"fog_density":environment.fog_density,"material_bindings":bindings,"emissive_material_variants":emissive_surfaces,"scope":"Temporary actual shader, scene light and sky changes; no fullscreen tint. Streaming transitions and other weather states remain unimplemented."}

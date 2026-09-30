extends RefCounted
var root_node:Node3D
var rain:MultiMeshInstance3D
var materials:Array[ShaderMaterial]=[]
var lightning:Array[MeshInstance3D]=[]
var flashes:Array[OmniLight3D]=[]
var shader_dir:String
var shader_cache:Dictionary={}
var converted:Dictionary={}
var skipped:Array=[]
var source_records:Array=[]
var flash_center:=Vector3(-3500,420,-4250)
func shader_named(name:String)->Shader:
	if shader_cache.has(name):return shader_cache[name]
	var s:=Shader.new();s.code=FileAccess.get_file_as_string(shader_dir.path_join(name+".gdshader"));shader_cache[name]=s;return s
func register(m:ShaderMaterial)->ShaderMaterial:
	if not materials.has(m):materials.append(m)
	return m
func mask_at(p:Vector3)->float:
	var edge:float=-2350.+150.*sin((p.z+3500.)*.0007)
	return (1.-smoothstep(-450.,450.,p.x-edge))*(1.-smoothstep(5200.,6800.,absf(p.z+3500.)))*smoothstep(-12000.,-10000.,p.x)
func adapt(m:Material)->Material:
	if m==null:return null
	var id:int=m.get_instance_id()
	if converted.has(id):return converted[id]
	var replacement:Material=m
	if m is ShaderMaterial:
		if m.shader!=null and m.shader.code.contains("storm35_mask"):
			register(m)
	elif m is StandardMaterial3D:
		if m.transparency==BaseMaterial3D.TRANSPARENCY_DISABLED:
			var fresh:=ShaderMaterial.new();fresh.shader=shader_named("storm_native")
			fresh.set_shader_parameter("base_color",m.albedo_color)
			fresh.set_shader_parameter("use_vertex_color",m.vertex_color_use_as_albedo)
			fresh.set_shader_parameter("base_roughness",m.roughness)
			fresh.set_shader_parameter("has_texture",m.albedo_texture!=null)
			if m.albedo_texture!=null:fresh.set_shader_parameter("base_texture",m.albedo_texture)
			fresh.set_shader_parameter("source_emission",Vector3(m.emission.r,m.emission.g,m.emission.b)*m.emission_energy_multiplier if m.emission_enabled else Vector3.ZERO)
			replacement=register(fresh)
		else:skipped.append({"material":m.resource_name,"reason":"Existing transparent native material retained; no claim of weather adaptation."})
	converted[id]=replacement
	return replacement
func configure(game:Node3D,folder:String)->Dictionary:
	shader_dir=folder
	root_node=Node3D.new();root_node.name="SpatialStormFront35a";game.add_child(root_node)
	var old_sky:Node3D=game.get_node_or_null("NativeCoastalSky27f")
	if old_sky!=null:old_sky.visible=false
	var sun:DirectionalLight3D=game.get_node("Sun")
	var sun_direction:=Vector3(.32,.14,-.94).normalized()
	sun.look_at(sun.global_position-sun_direction,Vector3.UP);sun.light_color=Color(1.,.76,.43);sun.light_energy=1.0
	var env:Environment=game.get_node("Environment").environment
	var sky:=ShaderMaterial.new();sky.shader=shader_named("storm_sky");register(sky);env.sky.sky_material=sky
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color(.38,.43,.52);env.ambient_light_energy=.32
	env.fog_light_color=Color(.40,.43,.49);env.fog_density=.000015
	for node in game.find_children("*","GeometryInstance3D",true,false):
		if node.material_override!=null:node.material_override=adapt(node.material_override)
		elif node is MeshInstance3D and node.mesh!=null:
			for i in range(node.mesh.get_surface_count()):node.set_surface_override_material(i,adapt(node.get_active_material(i)))
		elif node is MultiMeshInstance3D and node.multimesh!=null:
			var multi:MultiMesh=node.multimesh.duplicate();multi.mesh=multi.mesh.duplicate()
			for i in range(multi.mesh.get_surface_count()):multi.mesh.surface_set_material(i,adapt(multi.mesh.surface_get_material(i)))
			node.multimesh=multi
	for row in range(4):
		var z:float=-1000.-2100.*row
		var x:float=-2650.+150.*sin((z+3500.)*.0007)
		for item in [["storm_front_shelf",Vector3(x,920.+35.*sin(row*1.5),z),Vector3.ONE],
			["storm_rear_anvil",Vector3(x-200.,1040.,z-180.),Vector3(1.05,1.,1.05)],
			["storm_rain_scud",Vector3(x-80.,685.,z-90.),Vector3(.85,.72,.86)]]:
			var doc:=GLTFDocument.new();var state:=GLTFState.new()
			var path:String=folder.path_join("cloud-assets/"+str(item[0])+".glb")
			assert(doc.append_from_file(path,state)==OK)
			var cloud:Node3D=doc.generate_scene(state);root_node.add_child(cloud)
			cloud.position=item[1];cloud.scale=item[2]
			var cloud_material:=ShaderMaterial.new();cloud_material.shader=shader_named("storm_cloud");register(cloud_material)
			for mesh in cloud.find_children("*","MeshInstance3D",true,false):mesh.material_override=cloud_material
			source_records.append({"asset":item[0],"position":vector_array(cloud.position),"scale":vector_array(cloud.scale),"glb_sha256":FileAccess.get_sha256(path),"mesh_parts":cloud.find_children("*","MeshInstance3D",true,false).size()})
	# Finite native sphere for the low sun, in the same coordinate space.
	var sphere:=SphereMesh.new();sphere.radius=220.;sphere.height=440.;sphere.radial_segments=48;sphere.rings=24
	var sun_mesh:=MeshInstance3D.new();sun_mesh.name="LowSunSphere35a";sun_mesh.mesh=sphere
	sun_mesh.position=Vector3(-2278,420,-1300)+sun_direction*13000.;root_node.add_child(sun_mesh)
	var sun_mat:=StandardMaterial3D.new();sun_mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;sun_mat.albedo_color=Color(1.,.92,.48);sun_mesh.material_override=sun_mat
	# Crossed, world-oriented thin rain ribbons. The mesh is never camera-facing.
	var rain_mesh:=ArrayMesh.new();var arrays:Array=[];arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX]=PackedVector3Array([Vector3(-.055,0,0),Vector3(.055,0,0),Vector3(-1.145,9.,.6),Vector3(-1.255,9.,.6),Vector3(0,0,-.055),Vector3(0,0,.055),Vector3(-1.2,9.,.655),Vector3(-1.2,9.,.545)])
	arrays[Mesh.ARRAY_INDEX]=PackedInt32Array([0,1,2,0,2,3,4,5,6,4,6,7]);rain_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var multi:=MultiMesh.new();multi.transform_format=MultiMesh.TRANSFORM_3D;multi.mesh=rain_mesh;multi.instance_count=14000
	var rng:=RandomNumberGenerator.new();rng.seed=350109
	for i in range(multi.instance_count):multi.set_instance_transform(i,Transform3D(Basis.IDENTITY,Vector3(rng.randf_range(-650.,650.),rng.randf_range(-450.,450.),rng.randf_range(-650.,650.))))
	rain=MultiMeshInstance3D.new();rain.name="WorldOrientedRain35a";rain.multimesh=multi;root_node.add_child(rain)
	var rain_mat:=ShaderMaterial.new();rain_mat.shader=shader_named("storm_rain");rain.material_override=register(rain_mat)
	create_lightning()
	return {"assets":source_records,"rain_instances":multi.instance_count,"rain_seed":350109,"native_materials_adapted":converted.size(),"transparent_materials_retained":skipped,"sun_direction":vector_array(sun_direction),"sun_position":vector_array(sun_mesh.position),"front_mask":"world X - curved X(Z), 900m horizontal transition and finite north/south extent","scope":"Actual new Blender clouds, world-oriented rain, fixed spatial lightning, shared world weather mask. Cloud shadow uses an authored weather-field approximation, not ray-marched cloud optical transport. Existing land unchanged; reference landforms still incomplete."}
func vector_array(v:Vector3)->Array:return [v.x,v.y,v.z]
func create_lightning()->void:
	var rng:=RandomNumberGenerator.new();rng.seed=350102
	for n in range(3):
		var bottom:=Vector3(-3450.-n*440.,10.,-4000.-n*1600.)
		var top:=bottom+Vector3(110.,730.,90.)
		var points:Array[Vector3]=[top]
		for i in range(1,15):points.append(top.lerp(bottom,float(i)/14.)+Vector3(rng.randf_range(-32.,32.),0.,rng.randf_range(-25.,25.)))
		for i in range(points.size()-1):
			bolt_segment(points[i],points[i+1],2.2)
			if i in [4,8,10]:
				var end:Vector3=points[i]+Vector3(-90.,-120.,65.)
				bolt_segment(points[i],points[i].lerp(end,.45)+Vector3(15.,8.,-8.),.7)
				bolt_segment(points[i].lerp(end,.45)+Vector3(15.,8.,-8.),end,.55)
		var light:=OmniLight3D.new();light.position=bottom+Vector3(0,220,0);light.omni_range=1600.;light.light_color=Color(.68,.72,1.);light.light_energy=0.;light.shadow_enabled=true;root_node.add_child(light);flashes.append(light)
func bolt_segment(a:Vector3,b:Vector3,radius:float)->void:
	var cylinder:=CylinderMesh.new();cylinder.top_radius=radius*.65;cylinder.bottom_radius=radius;cylinder.height=a.distance_to(b);cylinder.radial_segments=5;cylinder.rings=1
	var mesh:=MeshInstance3D.new();mesh.mesh=cylinder;root_node.add_child(mesh);mesh.position=(a+b)*.5
	var axis:Vector3=(b-a).normalized();var across:Vector3=axis.cross(Vector3.FORWARD).normalized();mesh.basis=Basis(across,axis,across.cross(axis)).orthonormalized()
	var m:=StandardMaterial3D.new();m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;m.albedo_color=Color(2.8,2.65,4.);mesh.material_override=m;lightning.append(mesh)
func sample(camera:Camera3D,time:float)->Dictionary:
	var pulse:float=1. if time>=2. and time<2.14 else 0.
	rain.position=Vector3(floor(camera.position.x/100.)*100.,camera.position.y,floor(camera.position.z/100.)*100.)
	for m in materials:
		m.set_shader_parameter("storm_flash",pulse);m.set_shader_parameter("storm_camera",camera.global_position)
	for mesh in lightning:mesh.visible=pulse>0.
	for lamp in flashes:lamp.light_energy=pulse*9.
	return {"time":time,"flash":pulse,"camera_weather":mask_at(camera.position),"rain_center":vector_array(rain.position),"weather_probes":[{"position":[-3500,0,-3500],"storm":mask_at(Vector3(-3500,0,-3500))},{"position":[-2350,0,-3500],"storm":mask_at(Vector3(-2350,0,-3500))},{"position":[-1200,0,-3500],"storm":mask_at(Vector3(-1200,0,-3500))}],"material_bindings":materials.size(),"lightning_native_lights":flashes.size(),"lightning_segments":lightning.size(),"scope":"Discrete sampled observation positions in the same world; not a continuous flight replay."}

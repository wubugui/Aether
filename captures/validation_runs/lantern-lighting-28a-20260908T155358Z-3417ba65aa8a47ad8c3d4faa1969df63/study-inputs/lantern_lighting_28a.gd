extends RefCounted
## Static scene study: real light-space collision depth and view-depth volume clipping.
const LENGTH:=560.
const FAR_RADIUS:=51.2
const RAY_GRID:=33
var folder:String
var volume_shader:Shader
func load_volume(asset:String,parent:Node3D) -> Node3D:
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	assert(document.append_from_file(folder.path_join(asset+".glb"),state)==OK)
	var node:Node3D=document.generate_scene(state);parent.add_child(node)
	return node
func occlusion_map(game:Node3D,tower:Node3D,beam:Node3D) -> Dictionary:
	var excluded:Array[RID]=[]
	for body in tower.find_children("*","CollisionObject3D",true,false):excluded.append(body.get_rid())
	var image:=Image.create(RAY_GRID,RAY_GRID,false,Image.FORMAT_RF)
	var depths:Array=[];var hits:Array=[];var blocked:=0
	for y in range(RAY_GRID):
		for x in range(RAY_GRID):
			var local_target:=Vector3((float(x)/(RAY_GRID-1)*2.-1.)*FAR_RADIUS,(float(y)/(RAY_GRID-1)*2.-1.)*FAR_RADIUS,-LENGTH)
			var target:Vector3=beam.to_global(local_target)
			var query:=PhysicsRayQueryParameters3D.create(beam.global_position,target,0xffffffff,excluded)
			var hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(query)
			var axial:=LENGTH
			if not hit.is_empty():
				axial=clampf(-beam.to_local(hit.position).z,0.,LENGTH);blocked+=1
				hits.append({"x":x,"y":y,"depth_m":axial,"collider":str(hit.collider.get_path()),"hit":[hit.position.x,hit.position.y,hit.position.z]})
			image.set_pixel(x,y,Color(axial/LENGTH,0.,0.,1.));depths.append(axial)
	return {"texture":ImageTexture.create_from_image(image),"report":{"grid":RAY_GRID,"rays":RAY_GRID*RAY_GRID,"blocked_rays":blocked,"excluded_own_tower_bodies":excluded.size(),"axial_depths_m":depths,"hits":hits,"scope":"Actual static scene collision depths from lamp origin; own lighthouse excluded so optical housing transmits.33x33 angular samples with linear interpolation, not exact thin-object shadow boundaries or animated occlusion."}}
func assign_volume(node:Node3D,kind:float,texture:Texture2D) -> void:
	for mesh in node.find_children("*","MeshInstance3D",true,false):
		var material:=ShaderMaterial.new();material.shader=volume_shader
		material.set_shader_parameter("volume_kind",kind)
		material.set_shader_parameter("beam_to_world",mesh.global_transform)
		material.set_shader_parameter("beam_occlusion",texture)
		material.set_shader_parameter("light_energy",1.7 if kind>.5 else .65)
		mesh.material_override=material
		mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
func configure(game:Node3D,region:Node3D,input_folder:String,night:bool) -> Dictionary:
	folder=input_folder
	if not night:return {"night":false,"beams":[],"lamp_materials":[],"scope":"New lantern optics disabled in daylight."}
	volume_shader=Shader.new();volume_shader.code=FileAccess.get_file_as_string(folder.path_join("lantern_volume.gdshader"))
	var beams:Array=[];var material_records:Array=[]
	var directions:Dictionary={"Lighthouse_island_a":Vector3(.50,-.04,-.866),"Lighthouse_island_b":Vector3(-.8,-.02,.6),"Lighthouse_island_c":Vector3(-.6,-.02,.8),"Lighthouse_island_d":Vector3(-.92,-.025,-.39)}
	for tower in region.get_children():
		if not directions.has(str(tower.name)):continue
		for mesh in tower.find_children("*","MeshInstance3D",true,false):
			for index in range(mesh.mesh.get_surface_count()):
				var source:Material=mesh.get_active_material(index)
				if not source is StandardMaterial3D:continue
				var energy:=0.
				if source.resource_name.contains("Lamp core"):energy=6.
				elif source.resource_name.contains("Clear slightly amber lantern glass"):energy=.75
				elif source.resource_name.contains("Clear optical lens glass"):energy=1.2
				if energy<=0.:continue
				var material:StandardMaterial3D=source.duplicate()
				material.emission_enabled=true;material.emission=Color(1.,.58,.16);material.emission_energy_multiplier=energy
				mesh.set_surface_override_material(index,material)
				material_records.append({"mesh":str(mesh.get_path()),"surface":index,"source_name":source.resource_name,"energy":energy,"alpha":material.albedo_color.a,"transparency":material.transparency})
		var lamp_origin:Vector3=tower.to_global(Vector3(0,19.60,0))
		var direction:Vector3=directions[str(tower.name)].normalized()
		var beam:=load_volume("lantern_beam",region);beam.name="OpticalBeam_"+str(tower.name)
		beam.global_position=lamp_origin;beam.look_at(lamp_origin+direction,Vector3.UP)
		assert(beam.global_basis.get_scale().distance_to(Vector3.ONE)<.0001)
		var occlusion:=occlusion_map(game,tower,beam)
		assign_volume(beam,0.,occlusion.texture)
		var halo:=load_volume("lantern_halo",tower);halo.name="OpticalLampHalo";halo.position=Vector3(0,19.60,0)
		assign_volume(halo,1.,occlusion.texture)
		var lamp:OmniLight3D=tower.get_node("NativeLanternLight")
		lamp.light_energy=4.;lamp.omni_range=28.;lamp.shadow_enabled=true
		var spot:=SpotLight3D.new();spot.name="NativeLanternSpot";tower.add_child(spot)
		spot.global_position=lamp_origin;spot.look_at(lamp_origin+direction,Vector3.UP)
		spot.light_color=Color(1.,.62,.20);spot.light_energy=8.;spot.spot_range=LENGTH
		spot.spot_angle=rad_to_deg(atan(FAR_RADIUS/LENGTH));spot.spot_attenuation=.65;spot.shadow_enabled=true
		beams.append({"tower":str(tower.get_path()),"position":[lamp_origin.x,lamp_origin.y,lamp_origin.z],"direction":[direction.x,direction.y,direction.z],"length_m":LENGTH,"far_radius_m":FAR_RADIUS,"volume_asset":"lantern_beam.glb","halo_asset":"lantern_halo.glb","occlusion":occlusion.report,"omni_energy":lamp.light_energy,"omni_range":lamp.omni_range,"spot_energy":spot.light_energy,"spot_angle":spot.spot_angle,"spot_shadows":spot.shadow_enabled})
	return {"night":true,"beams":beams,"lamp_materials":material_records,"scope":"Four fixed world beams in editable Blender control volumes.32step density integration, camera-depth clipping and33x33 static collision shadow maps. Native spot/omni lights illuminate receivers. Finite sampled approximation; no rotating-beam animation, local-water reflection or full-weather acceptance. World positions/directions are authored design."}

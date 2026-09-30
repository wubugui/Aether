extends RefCounted
## Local surveyed harbor assembly; never edits World or its saved resources.
var game:Node3D
var root:Node3D
var folder:String
var templates:Dictionary={}
var buildings:Array=[]
var light_records:Array=[]
var asset_records:Array=[]
var removed_scatter:Array=[]
var is_night:bool
var path_adapter
var path_report:Dictionary
var main_landing:Node3D
var main_boat:Node3D
func point(values:Array) -> Vector3:return Vector3(values[0],values[1],values[2])
func ground(at:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(at.x,300,at.z),Vector3(at.x,-30,at.z),4)
	var hit:=game.get_world_3d().direct_space_state.intersect_ray(query);assert(not hit.is_empty());return hit
func spawn(name:String,at:Vector3,yaw:float=0.,house:bool=false) -> Node3D:
	if not templates.has(name):
		var document:=GLTFDocument.new();var state:=GLTFState.new()
		var path:String=folder.path_join("keeper_house.glb") if house else folder.path_join("harbor-kit/"+name+".glb")
		assert(document.append_from_file(path,state)==OK);templates[name]=document.generate_scene(state)
	var node:Node3D=templates[name].duplicate();node.name="Harbor_"+name+"_"+str(root.get_child_count());node.position=at;node.rotation.y=yaw;root.add_child(node)
	for mesh in node.find_children("*","MeshInstance3D",true,false):
		mesh.create_trimesh_collision()
		for body in mesh.find_children("*","StaticBody3D",true,false):body.collision_layer=1
		if name=="harbor_lantern" and not is_night:
			for surface in range(mesh.mesh.get_surface_count()):
				var material:Material=mesh.mesh.surface_get_material(surface)
				if material is StandardMaterial3D and material.resource_name.contains("Harbor lantern flame"):
					material=material.duplicate();material.emission_enabled=false;mesh.set_surface_override_material(surface,material)
	asset_records.append({"node":str(node.name),"asset":name,"position":[at.x,at.y,at.z],"yaw":yaw})
	return node
func lamp(at:Vector3,yaw:float,role:String) -> Node3D:
	var node:=spawn("harbor_lantern",at,yaw)
	var light:=OmniLight3D.new();light.name="HarborWarmLight";light.position=Vector3(.84,2.44,0)
	light.light_color=Color(1.,.47,.12);light.light_energy=1.8 if is_night else 0.;light.omni_range=11.;light.omni_attenuation=1.3;node.add_child(light)
	light_records.append({"node":str(light.get_path()),"role":role,"position":[light.global_position.x,light.global_position.y,light.global_position.z],"energy":light.light_energy,"range_m":light.omni_range,"parent":str(node.name)})
	return node
func clear_house_vegetation() -> void:
	for grove in game.get_node("World/Vegetation").get_children():
		if not grove is MultiMeshInstance3D or grove.multimesh==null:continue
		var original:MultiMesh=grove.multimesh;var kept:Array=[];var removed:Array=[]
		for index in range(original.instance_count):
			var transform:=original.get_instance_transform(index);var world:Vector3=grove.global_transform*transform.origin;var conflict:=false
			for house in buildings:
				var local:Vector3=house.to_local(world)
				if absf(local.x)<5.2 and absf(local.z)<7.6:conflict=true;break
			if conflict:removed.append({"index":index,"position":[world.x,world.y,world.z]})
			else:kept.append(index)
		if removed.is_empty():continue
		var replacement:MultiMesh=original.duplicate();replacement.instance_count=kept.size()
		for index in range(kept.size()):
			replacement.set_instance_transform(index,original.get_instance_transform(kept[index]))
			if original.use_colors:replacement.set_instance_color(index,original.get_instance_color(kept[index]))
			if original.use_custom_data:replacement.set_instance_custom_data(index,original.get_instance_custom_data(kept[index]))
		grove.multimesh=replacement;removed_scatter.append({"node":str(grove.get_path()),"removed_from_temporary_copy":removed})
func configure(scene:Node3D,input_folder:String,night:bool,camera:Camera3D,view:String) -> Dictionary:
	game=scene;folder=input_folder;is_night=night
	root=Node3D.new();root.name="SurveyedHarborStudy22d";game.add_child(root)
	var survey:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("harbor-survey.json")))
	assert(survey.world_sha256==FileAccess.get_sha256("res://scenes/world/World.tscn"))
	var footing:Array=[];var pier_checks:Array=[]
	for item in survey.houses:
		var at:=point(item.position);var house:=spawn("keeper_house",at,item.yaw,true);buildings.append(house)
		var samples:Array=[]
		for x in [-3.9,0.,3.9]:
			for z in [-5.4,0.,5.4]:
				var vertex:Vector3=house.to_global(Vector3(x,-.65,z));var hit:=ground(vertex)
				samples.append({"position":[vertex.x,vertex.y,vertex.z],"gap_m":vertex.y-hit.position.y,"collider":str(hit.collider.get_path())})
		footing.append({"node":str(house.name),"samples":samples})
		var lantern_at:Vector3=house.to_global(Vector3(4.8,0,6.1));lantern_at.y=ground(lantern_at).position.y
		lamp(lantern_at,float(item.yaw),"house lane")
	for index in range(survey.piers.size()):
		var item:Dictionary=survey.piers[index];var pier:=spawn("timber_pier",point(item.pier_center),item.yaw)
		var landing:=spawn("pier_landing",point(item.landing_center),item.yaw)
		spawn("repair_awning",landing.to_global(Vector3(-1.65,2.35,0)),item.yaw)
		spawn("harbor_cargo",landing.to_global(Vector3(3.05,2.35,-.05)),item.yaw)
		for local in [Vector3(-4.9,2.35,2.5),Vector3(4.9,2.35,2.5),Vector3(-1.95,2.35,-4.6),Vector3(1.95,2.35,-4.6)]:
			var at:Vector3=landing.to_global(local) if absf(local.x)>3. else pier.to_global(local)
			lamp(at,float(item.yaw),"dock deck")
		var boat:=spawn("moored_fishing_boat",pier.to_global(Vector3(3.90,0.02,3.5)),float(item.yaw)+.08)
		if index==1:main_landing=landing;main_boat=boat
		var entry:Vector3=point(item.entry);var checks:Array=[]
		for x in [-2.2,0.,2.2]:
			var at:Vector3=entry+Basis(Vector3.UP,float(item.yaw))*Vector3(x,0,0);var hit:=ground(at)
			checks.append({"position":[at.x,hit.position.y,at.z],"deck_gap_m":2.35-hit.position.y,"collider":str(hit.collider.get_path())})
		pier_checks.append({"node":str(pier.name),"entry":checks,"scope":"Entry deck gap only; land routes and seabed anchoring not yet completed."})
	path_adapter=load(folder.path_join("harbor_path_runtime_22d.gd")).new()
	path_report=path_adapter.configure(game,folder,self)
	clear_house_vegetation()
	path_report["vegetation_adjustments"]=path_adapter.clear_path_vegetation()
	var basis:=Basis(Vector3.UP,-.98)
	match view:
		"dock-front":camera.position=main_landing.position+basis*Vector3(16,11,19);camera.look_at(main_landing.position+Vector3(0,3,0));camera.fov=62
		"dock-back":camera.position=main_landing.position+basis*Vector3(-15,10,-19);camera.look_at(main_landing.position+Vector3(0,3,0));camera.fov=62
		"boat-close":camera.position=main_boat.position+basis*Vector3(8,5,8);camera.look_at(main_boat.position+Vector3(0,2.1,0));camera.fov=58
	var route:Dictionary=path_adapter.source.routes[1]
	var entry:=point(route.origin);var end:=point(route.end);var middle:Vector3=(entry+end)*.5;middle.y=10.
	match view:
		"path-approach":camera.position=entry+basis*Vector3(9,7,8);camera.look_at(entry-basis*Vector3(0,-7,15));camera.fov=62
		"paths-overview":camera.position=middle+Vector3(-34,34,31);camera.look_at(middle);camera.fov=62
		"path-door":camera.position=end+basis*Vector3(5,20,8);camera.look_at(end+Vector3(0,16,0));camera.fov=58
		"path0-curve":
			var first:Dictionary=path_adapter.source.routes[0];var center:=point(first.origin)
			camera.position=center+Vector3(-15,23,22);camera.look_at(center+Vector3(20,8,-4));camera.fov=65
	for template in templates.values():template.free()
	return {"source_survey_run":survey.run_id,"scope":"Temporary23 surveyed houses and4 detailed docks with scene boats in existing continuous World. Bounding foundation samples, not full contact/route/boat physics proof.","assets":asset_records,"house_footings":footing,"pier_entries":pier_checks,"lights":light_records,"vegetation_adjustments":removed_scatter,"night":night,"stone_paths":path_report}

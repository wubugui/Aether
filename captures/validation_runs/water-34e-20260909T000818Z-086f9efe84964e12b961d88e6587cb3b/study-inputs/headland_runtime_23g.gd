extends RefCounted
var game:Node3D
var region:Node3D
var folder:String
var houses:Array=[]
var records:Array=[]
var lights:Array=[]
var scatter_changes:Array=[]
var layout:Dictionary
func point(p:Array)->Vector3:return Vector3(p[0],p[1],p[2])
func hit(at:Vector3,mask:int=256)->Dictionary:
	return game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(at.x,300,at.z),Vector3(at.x,-30,at.z),mask))
func spawn(asset:String,at:Vector3,yaw:float=0.,layer:int=1)->Node3D:
	var path:String=folder.path_join("keeper_house.glb") if asset=="keeper_house" else folder.path_join("headland/"+asset+".glb")
	var document:=GLTFDocument.new();var state:=GLTFState.new();assert(document.append_from_file(path,state)==OK)
	var node:Node3D=document.generate_scene(state);node.name=asset+"_"+str(region.get_child_count());node.position=at;node.rotation.y=yaw;region.add_child(node)
	for mesh in node.find_children("*","MeshInstance3D",true,false):
		mesh.create_trimesh_collision()
		for body in mesh.find_children("*","StaticBody3D",true,false):body.collision_layer=layer
	records.append({"asset":asset,"node":str(node.name),"position":[at.x,at.y,at.z],"yaw":yaw,"sha256":FileAccess.get_sha256(path)})
	return node
func configure(scene:Node3D,directory:String,night:bool,camera:Camera3D,view:String)->void:
	game=scene;folder=directory;layout=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("headland/layout.json")))
	region=Node3D.new();region.name="MainlandVillage23g";game.add_child(region)
	spawn("mainland_headland",point(layout.origin),0.,261)
	for item in layout.houses:
		var house:=spawn(item.asset,point(item.position),item.yaw);houses.append(house)
		var lantern_doc:=GLTFDocument.new();var state:=GLTFState.new()
		assert(lantern_doc.append_from_file(folder.path_join("harbor-kit/harbor_lantern.glb"),state)==OK)
		var lamp:Node3D=lantern_doc.generate_scene(state);lamp.name="VillageLantern";house.add_child(lamp)
		lamp.position=Vector3(-2.7 if item.asset!="quay_workshop" else -3.9,0.,4.8 if item.asset=="fisher_cottage" else (4.5 if item.asset=="quay_workshop" else 6.8))
		var light:=OmniLight3D.new();light.name="VillageWarmLight";light.position=Vector3(.84,2.44,0);light.light_color=Color(1,.47,.12);light.light_energy=1.8 if night else 0.;light.omni_range=11.;light.omni_attenuation=1.3;lamp.add_child(light)
		lights.append({"house":item.name,"position":[light.global_position.x,light.global_position.y,light.global_position.z],"energy":light.light_energy})
	match view:
		"headland-front":camera.position=Vector3(-2301,36,-1808);camera.look_at(Vector3(-2240,10,-1750));camera.fov=62
		"headland-back":camera.position=Vector3(-2103,68,-1710);camera.look_at(Vector3(-2220,12,-1800));camera.fov=65
		"headland-bay":camera.position=Vector3(-2288,28,-1930);camera.look_at(Vector3(-2224,8,-1873));camera.fov=62
		"headland-seam":camera.position=Vector3(-2070,88,-1960);camera.look_at(Vector3(-2160,10,-1860));camera.fov=67
func finish()->Dictionary:
	var footings:Array=[]
	for i in range(houses.size()):
		var house:Node3D=houses[i];var item:Dictionary=layout.houses[i];var samples:Array=[]
		var wide:float=3.9 if item.asset=="keeper_house" else (3.05 if item.asset=="fisher_cottage" else 4.4)
		var depth:float=5.4 if item.asset=="keeper_house" else (4.1 if item.asset=="fisher_cottage" else 3.4)
		for x in [-wide,0.,wide]:
			for z in [-depth,0.,depth]:
				var at:Vector3=house.to_global(Vector3(x,-.65,z));var ground:=hit(at);assert(not ground.is_empty())
				samples.append({"position":[at.x,at.y,at.z],"gap_m":at.y-ground.position.y,"collider":str(ground.collider.get_path())})
		footings.append({"name":item.name,"samples":samples})
	var trees:Array=[]
	var tree_sites:Array=[[-2251,-1730,.52],[-2239,-1725,.63],[-2225,-1715,.7],[-2240,-1778,.54],[-2222,-1788,.72],[-2210,-1777,.83],[-2200,-1760,.90],[-2207,-1728,.7],[-2188,-1743,.9],[-2165,-1750,.75],[-2188,-1800,.8],[-2175,-1813,.67],[-2200,-1818,.6],[-2214,-1805,.64],[-2196,-1839,.7],[-2190,-1855,.95],[-2200,-1880,.73],[-2210,-1900,.76],[-2223,-1907,.52],[-2185,-1910,.85],[-2160,-1897,.9],[-2170,-1860,.75],[-2215,-1930,.73],[-2200,-1950,.95],[-2225,-1977,.62],[-2235,-2010,.69],[-2215,-2005,.85],[-2160,-1730,.8]]
	for item in tree_sites:
		var at:=Vector3(item[0],0,item[1]);var ground:=hit(at,260)
		if ground.is_empty():continue
		at.y=ground.position.y;var near_house:=false
		for house in houses:
			var local:Vector3=house.to_local(at)
			if absf(local.x)<6.1 and absf(local.z)<8.4:near_house=true;break
		if near_house:continue
		var tree:Node3D=load("res://scenes/prefabs/pine.tscn").instantiate()
		tree.name="HeadlandPine_"+str(trees.size());tree.position=at;tree.scale=Vector3.ONE*float(item[2]);region.add_child(tree)
		trees.append({"node":str(tree.name),"position":[at.x,at.y,at.z],"scale":item[2],"ground_collider":str(ground.collider.get_path())})
	# Refit only temporary scatter copies intersecting the new local terrain.
	for grove in game.get_node("World/Vegetation").get_children():
		if not grove is MultiMeshInstance3D or grove.multimesh==null:continue
		var source:MultiMesh=grove.multimesh;var kept:Array=[];var changed:Array=[]
		for index in range(source.instance_count):
			var transform:=source.get_instance_transform(index);var at:Vector3=grove.global_transform*transform.origin;var remove:=false
			if at.x>=-2300 and at.x<=-1985 and at.z>=-2055 and at.z<=-1635:
				var ground:=hit(at)
				if not ground.is_empty():
					ground=hit(at,260)
					for house in houses:
						var local:Vector3=house.to_local(at)
						if absf(local.x)<5.2 and absf(local.z)<7.6:remove=true;break
					if remove:changed.append({"index":index,"action":"removed at new house"})
					elif absf(ground.position.y-at.y)>.1:
						var old_y:float=at.y;at.y=ground.position.y;transform.origin=grove.to_local(at);changed.append({"index":index,"action":"refit to current terrain","old_y":old_y,"new_y":at.y})
			if not remove:kept.append({"index":index,"transform":transform})
		if changed.is_empty():continue
		var copy:MultiMesh=source.duplicate();copy.instance_count=kept.size()
		for i in range(kept.size()):
			copy.set_instance_transform(i,kept[i].transform)
			if source.use_colors:copy.set_instance_color(i,source.get_instance_color(kept[i].index))
			if source.use_custom_data:copy.set_instance_custom_data(i,source.get_instance_custom_data(kept[i].index))
		grove.multimesh=copy;scatter_changes.append({"node":str(grove.get_path()),"changes":changed})
	return {"assets":records,"footings":footings,"lights":lights,"scatter_changes":scatter_changes,"trees":trees,"scope":"Local actual solid headland and nine detailed native village houses. 3x3 footing probes only; no full terrain contact, routes, movement or reference acceptance."}

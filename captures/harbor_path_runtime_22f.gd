extends RefCounted
var game:Node3D
var root:Node3D
var source:Dictionary
var report:Dictionary
func point(a:Array) -> Vector3:return Vector3(a[0],a[1],a[2])
func ray(at:Vector3,mask:int,up:bool=false) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(at.x,-30 if up else 300,at.z),Vector3(at.x,300 if up else -30,at.z),mask)
	return game.get_world_3d().direct_space_state.intersect_ray(query)
func ground(at:Vector3) -> Dictionary:
	var result:=ray(at,4);assert(not result.is_empty());return result
func configure(scene:Node3D,folder:String,harbor) -> Dictionary:
	game=scene;root=Node3D.new();root.name="SurveyedStoneApproaches22f";game.add_child(root)
	var source_path:=folder.path_join("stone-approaches/model-report.json")
	source=JSON.parse_string(FileAccess.get_file_as_string(source_path))
	assert(source.world_sha256==FileAccess.get_sha256("res://scenes/world/World.tscn"))
	var assets:Array=[];var lamps:Array=[]
	for route in source.routes:
		var path:String=folder.path_join("stone-approaches/"+str(route.asset)+".glb")
		var document:=GLTFDocument.new();var state:=GLTFState.new();assert(document.append_from_file(path,state)==OK)
		var node:Node3D=document.generate_scene(state);node.name=route.asset;node.position=point(route.origin);root.add_child(node)
		for mesh in node.find_children("*","MeshInstance3D",true,false):
			mesh.create_trimesh_collision()
			for body in mesh.find_children("*","StaticBody3D",true,false):body.collision_layer=129
		assets.append({"asset":route.asset,"position":route.origin,"glb_sha256":FileAccess.get_sha256(path),"length_m":route.length_m,"cells":route.cells.size()})
		var next_distance:=10.
		for cell in route.cells:
			var distance:float=cell.distance_range_m[0]
			if distance<next_distance or distance>float(route.length_m)-5.:continue
			var center:=point(cell.center);var tangent:=point(cell.row_start.tangent)
			var transverse:=Vector3(-tangent.z,0,tangent.x)
			var at:Vector3=center+transverse*(float(cell.start_width)*.5+.70);at.y=ground(at).position.y
			harbor.lamp(at,atan2(tangent.x,tangent.z),"stone approach")
			lamps.append({"path":route.asset,"distance_m":distance,"position":[at.x,at.y,at.z]});next_distance+=12.
	report={"source_survey_run":source.source_survey_run,"source_sha256":FileAccess.get_sha256(source_path),"assets":assets,"lamp_sites":lamps,"scope":"Native Blender stone treads, landings and bases. Contact results are added after physics frames; no full movement, reference or production acceptance."}
	return report
func clear_path_vegetation() -> Array:
	var changes:Array=[];var bounds:Array=[]
	for route in source.routes:
		var low:=Vector2(INF,INF);var high:=Vector2(-INF,-INF)
		for cell in route.cells:
			var at:=point(cell.center);low=low.min(Vector2(at.x,at.z));high=high.max(Vector2(at.x,at.z))
		bounds.append({"low":low-Vector2(4,4),"high":high+Vector2(4,4),"route":route})
	for grove in game.get_node("World/Vegetation").get_children():
		if not grove is MultiMeshInstance3D or grove.multimesh==null:continue
		var original:MultiMesh=grove.multimesh;var kept:Array=[];var removed:Array=[]
		for index in range(original.instance_count):
			var transform:=original.get_instance_transform(index);var at:Vector3=grove.global_transform*transform.origin;var conflict:=false
			for box in bounds:
				if at.x<box.low.x or at.x>box.high.x or at.z<box.low.y or at.z>box.high.y:continue
				for cell in box.route.cells:
					var center:=point(cell.center)
					if Vector2(at.x-center.x,at.z-center.z).length()<float(cell.start_width)*.5+1.1:conflict=true;break
				if conflict:break
			if conflict:removed.append({"index":index,"position":[at.x,at.y,at.z]})
			else:kept.append(index)
		if removed.is_empty():continue
		var replacement:MultiMesh=original.duplicate();replacement.instance_count=kept.size()
		for index in range(kept.size()):
			replacement.set_instance_transform(index,original.get_instance_transform(kept[index]))
			if original.use_colors:replacement.set_instance_color(index,original.get_instance_color(kept[index]))
			if original.use_custom_data:replacement.set_instance_custom_data(index,original.get_instance_custom_data(kept[index]))
		grove.multimesh=replacement;changes.append({"node":str(grove.get_path()),"removed_from_temporary_copy":removed})
	return changes
func validate() -> Dictionary:
	var checks:Array=[];var errors:Array=[]
	for route in source.routes:
		var tops:Array=[];var foundations:Array=[]
		for cell in route.cells:
			var center:=point(cell.center);var tangent:Vector3=(point(cell.row_start.tangent)+point(cell.row_end.tangent)).normalized();var transverse:=Vector3(-tangent.z,0,tangent.x)
			var width:float=(float(cell.start_width)+float(cell.end_width))*.5
			for ratio in [-.28,0.,.28]:
				var at:Vector3=center+transverse*width*float(ratio)
				var top:=ray(at,128);var base:=ray(at,128,true);var soil:=ground(at)
				if top.is_empty() or base.is_empty():errors.append([route.asset,cell.index,ratio,"missing path surface"]);continue
				var error:float=top.position.y-float(cell.top_y);var gap:float=base.position.y-soil.position.y
				tops.append({"cell":cell.index,"ratio":ratio,"position":[top.position.x,top.position.y,top.position.z],"error_m":error,"collider":str(top.collider.get_path())})
				foundations.append({"cell":cell.index,"ratio":ratio,"bottom_y":base.position.y,"original_ground_y":soil.position.y,"gap_m":gap,"collider":str(base.collider.get_path()),"ground_collider":str(soil.collider.get_path())})
				if absf(error)>.015 or gap>=0 or not str(top.collider.get_path()).contains(str(route.asset)):errors.append([route.asset,cell.index,ratio,error,gap])
		checks.append({"asset":route.asset,"treads":tops,"foundations":foundations,"start_top_y":route.start_top_y,"end_top_y":route.end_top_y,"max_authored_riser_m":route.max_riser_m})
	return {"passed":errors.is_empty(),"errors":errors,"paths":checks,"scope":"Three actual down/up path collision rays per tread plus original terrain ray at the same point. Does not cover every surface, side wall, full movement or reference fidelity."}
func bed_without_sea(at:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(at.x,300,at.z),Vector3(at.x,-30,at.z),4)
	var result:=game.get_world_3d().direct_space_state.intersect_ray(query)
	if not result.is_empty() and str(result.collider.get_path()).contains("SeaCollision"):
		query.exclude=[result.rid];result=game.get_world_3d().direct_space_state.intersect_ray(query)
	return result
func validate_boats(harbor_root:Node3D) -> Array:
	var boats:Array=[];var previous_offset:=Basis(Vector3.UP,-.98)*Vector3(0,0,-3.1)
	for boat in harbor_root.get_children():
		if not str(boat.name).contains("moored_fishing_boat"):continue
		var positions:Array=[];var seen:Dictionary={}
		for mesh in boat.find_children("*","MeshInstance3D",true,false):
			for surface in range(mesh.mesh.get_surface_count()):
				var arrays:Array=mesh.mesh.surface_get_arrays(surface)
				for vertex in arrays[Mesh.ARRAY_VERTEX]:
					var world:Vector3=mesh.global_transform*vertex
					if world.y>.12:continue
					var key:="%.4f,%.4f,%.4f"%[world.x,world.y,world.z]
					if seen.has(key):continue
					seen[key]=true;positions.append(world)
		var samples:Array=[]
		for current in positions:
			for mode in ["previous_22a","candidate_22f"]:
				var at:Vector3=current+previous_offset if mode=="previous_22a" else current
				var bed:=bed_without_sea(at)
				samples.append({"placement":mode,"position":[at.x,at.y,at.z],"bed_y":null if bed.is_empty() else bed.position.y,"clearance_m":null if bed.is_empty() else at.y-bed.position.y,"collider":null if bed.is_empty() else str(bed.collider.get_path())})
		boats.append({"node":str(boat.name),"sample_vertices":positions.size(),"samples":samples,"scope":"Actual exported mesh vertices at or below0.12m, with SeaCollision excluded. Null means no original ground collision hit down to-30m, not authored bathymetry or buoyancy proof. Faces between vertices not fully sampled."})
	return boats

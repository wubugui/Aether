extends RefCounted
var game:Node3D
var region:Node3D
var design:Dictionary
var layout:Dictionary
var records:Array=[]
func point(p:Array)->Vector3:return Vector3(p[0],p[1],p[2])
func ray(at:Vector3,mask:int)->Dictionary:
	return game.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(at.x,150,at.z),Vector3(at.x,-20,at.z),mask))
func configure(scene:Node3D,folder:String,camera:Camera3D,view:String)->void:
	game=scene;design=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("village-paving/paving-design.json")))
	layout=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("headland/layout.json")))
	var grading:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("village-grading/build-report.json")))
	assert(design.headland_glb_sha256==grading.source_glb_sha256)
	var revision:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("rightcoast-revision.json")))
	assert(revision.retained_grading_glb_sha256==grading.glb_sha256)
	assert(revision.parent_revision_native_check_sha256==FileAccess.get_sha256(folder.path_join("rightcoast-parent-native-check.json")))
	var parent:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("rightcoast-parent-native-check.json")))
	assert(parent.glb_sha256==revision.immediate_source_glb_sha256 and parent.immediate_source_glb_sha256==grading.glb_sha256)
	assert(revision.retained_grading_report_sha256==FileAccess.get_sha256(folder.path_join("village-grading/build-report.json")))
	assert(revision.retained_paving_design_sha256==FileAccess.get_sha256(folder.path_join("village-paving/paving-design.json")))
	assert(revision.glb_sha256==FileAccess.get_sha256(folder.path_join("headland/mainland_headland.glb")))
	assert(grading.paving_design_sha256==FileAccess.get_sha256(folder.path_join("village-paving/paving-design.json")))
	region=Node3D.new();region.name="SharedVillageStreets26b";game.add_child(region)
	for group in design.groups:
		var path:String=folder.path_join("village-paving/village_"+group.name+".glb")
		var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(path,state)==OK)
		var node:Node3D=doc.generate_scene(state);node.name="Street_"+group.name;node.position=point(group.origin);region.add_child(node)
		for mesh in node.find_children("*","MeshInstance3D",true,false):
			mesh.create_trimesh_collision()
			for body in mesh.find_children("*","StaticBody3D",true,false):body.collision_layer=513
		records.append({"asset":"village_"+group.name,"position":group.origin,"sha256":FileAccess.get_sha256(path)})
	match view:
		"village-foreground":camera.position=Vector3(-2272,36,-1723);camera.look_at(Vector3(-2246,11,-1750));camera.fov=62
		"village-bay":camera.position=Vector3(-2270,32,-1851);camera.look_at(Vector3(-2232,8,-1875));camera.fov=62
		"village-door":camera.position=Vector3(-2263,15,-1744);camera.look_at(Vector3(-2252,11,-1750));camera.fov=58
		"village-upper":camera.position=Vector3(-2221,31,-1744);camera.look_at(Vector3(-2234,13,-1747));camera.fov=62
func validate()->Dictionary:
	var samples:Array=[];var omitted:=0;var failures:Array=[];var bases:Array=[]
	for group in design.groups:
		for solid in group.solids:
			var largest:=-1.;var center:=Vector3.ZERO
			for ids in solid.cap_triangles:
				var a:=Vector2(solid.vertices_xz[ids[0]][0],solid.vertices_xz[ids[0]][1]);var b:=Vector2(solid.vertices_xz[ids[1]][0],solid.vertices_xz[ids[1]][1]);var c:=Vector2(solid.vertices_xz[ids[2]][0],solid.vertices_xz[ids[2]][1])
				var area:float=absf((b-a).cross(c-a))*.5;var perimeter:float=a.distance_to(b)+b.distance_to(c)+c.distance_to(a)
				var expected_y:float=(float(solid.top_heights[ids[0]])+float(solid.top_heights[ids[1]])+float(solid.top_heights[ids[2]]))/3.
				var at:=Vector3((a.x+b.x+c.x)/3.,expected_y,(a.y+b.y+c.y)/3.)
				if area>largest:largest=area;center=at
				if solid.kind!="paver":continue
				if perimeter<.001 or 2*area/perimeter<.004:omitted+=1;continue
				var hit:=ray(at,512);var ground:=ray(at,4)
				if hit.is_empty() or ground.is_empty():failures.append({"solid":solid.name,"issue":"missing collision"});continue
				var error:float=hit.position.y-expected_y;var clearance:float=hit.position.y-ground.position.y
				var sample:={"solid":solid.name,"position":[at.x,hit.position.y,at.z],"expected_y":expected_y,"top_error_m":error,"ground_clearance_m":clearance,"ground_collider":str(ground.collider.get_path()),"paving_collider":str(hit.collider.get_path())}
				samples.append(sample)
				if absf(error)>.015 or clearance<-.015:failures.append(sample)
			if solid.kind=="foundation":
				var ground:=ray(center,4);assert(not ground.is_empty())
				bases.append({"solid":solid.name,"position":[center.x,solid.bottom_y,center.z],"bottom_ground_gap_m":float(solid.bottom_y)-ground.position.y})
	var doors:Array=[]
	for h in layout.houses:
		var depth:float=6.4 if h.asset=="keeper_house" else (4.95 if h.asset=="fisher_cottage" else 4.25)
		var transform:=Transform3D(Basis(Vector3.UP,h.yaw),point(h.position));var row:Array=[]
		for u in [-.7,0.,.7]:
			var at:Vector3=transform*Vector3(u,.18,depth+.04);var hit:=ray(at,512)
			var gap=null if hit.is_empty() else hit.position.y-at.y
			row.append({"position":[at.x,at.y,at.z],"paving_step_gap_m":gap})
			if gap==null or absf(float(gap))>.02:failures.append({"door":h.name,"position":[at.x,at.y,at.z],"paving_gap":gap})
		doors.append({"house":h.name,"samples":row})
	return {"passed":failures.is_empty(),"assets":records,"paver_collision_samples":samples,"foundation_samples":bases,"door_interfaces":doors,"omitted_tiny_cap_triangles":omitted,"failures":failures,"scope":"Actual native top and underlying graded headland plus original World terrain collision at cap-triangle centroids with inradius>=4mm; 3 door samples per house. Bases compare designed bottom with actual terrain at largest-cap centroid. Not whole-foot movement, every crack/edge or all ground contact acceptance."}


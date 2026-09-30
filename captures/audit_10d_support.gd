extends SceneTree
## Read-only audit: original native placement, in-memory candidate geometry only.
var world:Node3D
var points:Array=[]
var input_hashes:Dictionary={}
var output:String="res://captures/round-10d-readonly-support.json"
var replacements:Dictionary={
	"Cliffs/cliff_front_columns":"res://captures/cliff_sections_10d_prototype.glb",
	"Cliffs/cliff_western_slab":"res://captures/cliff_sections_10d_western_slab.glb",
	"Cliffs/cliff_crown":"res://captures/cliff_sections_10d_crown.glb",
	"Cliffs/cliff_central_wall":"res://captures/cliff_sections_10d_central_wall.glb",
	"Cliffs/cliff_shadow_buttress":"res://captures/cliff_sections_10d_shadow_buttress.glb",
	"Terrain/Ground_0_0":"res://captures/round-10d-Ground_0_0.glb",
	"Terrain/Ground_0_-1":"res://captures/round-10d-Ground_0_-1.glb"}

func _initialize() -> void:
	call_deferred("audit")

func v(p:Vector3) -> Array:
	return [p.x,p.y,p.z]

func sample(p:Vector3) -> Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4)
	var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():return {"miss":true}
	return {"height":hit.position.y,"owner":str(world.get_path_to(hit.collider)),"normal":v(hit.normal)}

func add_point(category:String,object:String,p:Vector3,detail:String) -> void:
	points.append({"category":category,"object":object,"point":v(p),"detail":detail,"baseline":sample(p)})

func mesh_nodes(node:Node) -> Array:
	var result:Array=node.find_children("*","MeshInstance3D",true,false)
	if node is MeshInstance3D:result.push_front(node)
	return result

func surface_points(asset:Node3D,category:String) -> void:
	var name:String=str(world.get_path_to(asset))
	for mesh:MeshInstance3D in mesh_nodes(asset):
		if mesh.mesh==null:continue
		var faces:PackedVector3Array=mesh.mesh.get_faces()
		for i in range(0,faces.size(),3):
			var a:Vector3=mesh.to_global(faces[i]);var b:Vector3=mesh.to_global(faces[i+1]);var c:Vector3=mesh.to_global(faces[i+2])
			var samples:Array=[(a+b+c)/3,a*.6+b*.2+c*.2,a*.2+b*.6+c*.2,a*.2+b*.2+c*.6,(a+b)*.5,(b+c)*.5,(c+a)*.5]
			for j in samples.size():add_point(category,name,samples[j],"%s:triangle%d:sample%d"%[asset.get_path_to(mesh),i/3,j])

func replace_asset(asset:Node3D,file:String) -> void:
	var prior:Node3D=asset.get_node("Model")
	var prior_transform:Transform3D=prior.transform
	asset.remove_child(prior);prior.free()
	var document:=GLTFDocument.new();var state:=GLTFState.new()
	assert(document.append_from_file(ProjectSettings.globalize_path(file),state)==OK)
	var model:Node3D=document.generate_scene(state)
	model.name="Model";asset.add_child(model);model.transform=prior_transform
	var collider:CollisionShape3D=asset.get_node("Collision/Shape")
	var faces:=PackedVector3Array()
	for mesh:MeshInstance3D in mesh_nodes(model):
		var local:Transform3D=collider.global_transform.affine_inverse()*mesh.global_transform
		for p in mesh.mesh.get_faces():faces.append(local*p)
	var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(faces)
	collider.shape=shape

func view_hits(camera:Camera3D,view:String,uvs:Array) -> Array:
	if view=="cliff-side":camera.position=Vector3(30,140,90);camera.look_at(Vector3(185,50,-50))
	else:camera.position=Vector3(0,145,250);camera.rotation=Vector3(deg_to_rad(-3.5),0,0)
	var rows:Array=[]
	for uv:Vector2 in uvs:
		var p:Vector3=camera.project_ray_origin(uv)
		var q:=PhysicsRayQueryParameters3D.create(p,p+camera.project_ray_normal(uv)*3000,4)
		var hit:=world.get_world_3d().direct_space_state.intersect_ray(q)
		rows.append({"pixel":[uv.x,uv.y],"owner":str(world.get_path_to(hit.collider)) if hit.has("collider") else "MISS","point":v(hit.position) if hit.has("position") else [],"normal":v(hit.normal) if hit.has("normal") else []})
	return rows

func audit() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	root.size=Vector2i(1672,941)
	input_hashes["res://scenes/world/World.tscn"]=FileAccess.get_sha256("res://scenes/world/World.tscn")
	for file:String in replacements.values():input_hashes[file]=FileAccess.get_sha256(file)
	world=load("res://scenes/world/World.tscn").instantiate();world.set_script(null);root.add_child(world)
	await physics_frame;await physics_frame
	for asset:Node3D in world.get_node("LandDetails").get_children():
		surface_points(asset,"road" if str(asset.name).begins_with("Trail_") else "field")
		await process_frame
	print("Prepared land surface samples ",points.size())
	for category in ["Settlements","Ports"]:
		for asset:Node3D in world.get_node(category).get_children():
			var object:String=str(world.get_path_to(asset))
			add_point("landmark",object,asset.global_position,"origin")
			for mesh:MeshInstance3D in mesh_nodes(asset):
				var box:AABB=mesh.get_aabb()
				for u in [0.0,0.5,1.0]:
					for w in [0.0,0.5,1.0]:
						add_point("landmark",object,mesh.to_global(box.position+Vector3(box.size.x*u,0,box.size.z*w)),"%s:bottom-aabb:%s,%s"%[asset.get_path_to(mesh),u,w])
	var grove_total:int=0
	for grove:MultiMeshInstance3D in world.get_node("Vegetation").get_children():
		if not grove.multimesh:continue
		for i in grove.multimesh.instance_count:
			var p:Vector3=grove.to_global(grove.multimesh.get_instance_transform(i).origin)
			grove_total+=1
			# Candidate tiles plus margin; report only actual before/after differences.
			if p.x>=-50 and p.x<=800 and p.z>=-800 and p.z<=800:
				add_point("vegetation",str(world.get_path_to(grove)),p,"instance%d"%i)
	print("Prepared all samples ",points.size()," scanned vegetation ",grove_total)
	for path:String in replacements:replace_asset(world.get_node(path),replacements[path])
	await physics_frame;await physics_frame
	var summaries:Dictionary={};var affected:Array=[];var misses:Array=[];var old_bad:int=0;var new_bad:int=0;var roads:int=0
	var sample_index:int=0
	for row:Dictionary in points:
		sample_index+=1
		var a:Array=row.point;var p:=Vector3(a[0],a[1],a[2]);var changed:Dictionary=sample(p)
		var key:String=row.object
		if not summaries.has(key):summaries[key]={"category":row.category,"samples":0,"affected":0,"max_support_delta":0.0,"baseline_failed_road_samples":0,"candidate_failed_road_samples":0,"max_candidate_road_error":0.0}
		var summary:Dictionary=summaries[key];summary.samples+=1
		if row.baseline.has("miss") or changed.has("miss"):
			row["candidate"]=changed;misses.append(row);continue
		var delta:float=changed.height-row.baseline.height
		if row.category=="road":
			roads+=1
			var old_error:float=p.y-row.baseline.height-.10;var error:float=p.y-changed.height-.10
			if absf(old_error)>.08:old_bad+=1;summary.baseline_failed_road_samples+=1
			if absf(error)>.08:new_bad+=1;summary.candidate_failed_road_samples+=1
			summary.max_candidate_road_error=maxf(summary.max_candidate_road_error,absf(error))
			row["baseline_road_error"]=old_error;row["candidate_road_error"]=error
		if absf(delta)>.01:
			row["candidate"]=changed;row["support_delta_metres"]=delta
			row["candidate_clearance_metres"]=p.y-changed.height
			affected.append(row);summary.affected+=1;summary.max_support_delta=maxf(summary.max_support_delta,absf(delta))
		if sample_index%2500==0:await process_frame
	var camera:=Camera3D.new();camera.fov=50;world.add_child(camera);camera.current=true
	var side:Array=view_hits(camera,"cliff-side",[Vector2(940,730),Vector2(980,750),Vector2(1020,770),Vector2(1060,770),Vector2(1110,765),Vector2(1170,755),Vector2(1230,730),Vector2(1250,780),Vector2(1120,715),Vector2(970,710)])
	var opening:Array=view_hits(camera,"opening",[Vector2(1415,880),Vector2(1450,900),Vector2(1500,925),Vector2(1000,900),Vector2(970,925),Vector2(1040,880)])
	var unchanged:bool=true
	for file:String in input_hashes:unchanged=unchanged and FileAccess.get_sha256(file)==input_hashes[file]
	var report:Dictionary={"audit_completed":true,"passed_as_render_acceptance":false,"scope":"Read-only original native placement, memory replacement of five cliffs and two 10d terrain GLBs. Road/field surface seven interior and edge samples per actual imported triangle; landmarks origin and model-bottom AABB 3x3 support probes, not whole-body intersection proof; vegetation origin samples within two changed tiles plus margin.","gpu":RenderingServer.get_video_adapter_name(),"input_hashes":input_hashes,"inputs_unchanged":unchanged,"sample_count":points.size(),"road_samples":roads,"baseline_failed_road_samples":old_bad,"candidate_failed_road_samples":new_bad,"scanned_vegetation":grove_total,"misses":misses,"objects":summaries,"affected_samples":affected,"side_ownership_rays":side,"opening_ownership_rays":opening}
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("10D SUPPORT completed: roads=",roads," old_bad=",old_bad," new_bad=",new_bad," affected=",affected.size()," misses=",misses.size()," unchanged=",unchanged)
	quit(0 if unchanged and misses.is_empty() else 1)

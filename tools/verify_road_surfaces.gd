extends "res://tools/assemble_world.gd"
## Check the imported road interiors against the assembled world's actual
## physical ground, including independent cliffs and alpine massifs.
func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	var world_path:="res://scenes/world/World.tscn";var before:=FileAccess.get_sha256(world_path)
	var world:Node3D=load(world_path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);world.set_script(null);root.add_child(world)
	await physics_frame;await physics_frame
	var reports:Array=[];var total:=0;var failures:=0
	for item in JSON.parse_string(FileAccess.get_file_as_string("res://assets/road_kit.json")):
		var road:Node3D=world.get_node("LandDetails/"+item.name)
		var tested:=0;var bad:=0;var maximum:=0.0;var examples:Array=[]
		for mesh in road.find_children("*","MeshInstance3D",true,false):
			var vertices:PackedVector3Array=mesh.mesh.get_faces()
			for i in range(0,vertices.size(),3):
				var a:Vector3=mesh.to_global(vertices[i]);var b:Vector3=mesh.to_global(vertices[i+1]);var c:Vector3=mesh.to_global(vertices[i+2])
				for p in [(a+b+c)/3,a*.6+b*.2+c*.2,a*.2+b*.6+c*.2,a*.2+b*.2+c*.6,(a+b)*.5,(b+c)*.5,(c+a)*.5]:
					var query:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4)
					var hit:=world.get_world_3d().direct_space_state.intersect_ray(query)
					var difference:float=absf(p.y-hit.position.y-.10) if not hit.is_empty() else 9999.0
					maximum=maxf(maximum,difference);tested+=1
					if difference>.08:
						bad+=1
						if examples.size()<5:examples.append({"point":str(p),"error_metres":difference,"ground":str(hit.get("position",Vector3.ZERO))})
				if i%1500==0:await process_frame
		total+=tested;failures+=bad
		reports.append({"name":item.name,"passed":bad==0,"sample_count":tested,"failed_samples":bad,"maximum_height_error_metres":maximum,"examples":examples,"glb_sha256":FileAccess.get_sha256("res://"+item.path)})
		print("ROAD INTERIOR ",item.name," samples=",tested," failures=",bad," max_error=",maximum)
	world.free();await process_frame
	var after:=FileAccess.get_sha256(world_path)
	var report:={"passed":failures==0 and before==after,"world_sha256":before,"world_unchanged":before==after,"samples":total,"roads":reports,"scope":"Seven interior/edge samples per actual imported road triangle versus full assembled terrain, cliff and massif physics. Expected road clearance 0.10 m; tolerance 0.08 m."}
	report["provenance"]=preload("res://scripts/validation_context.gd").snapshot()
	var file:=FileAccess.open("res://captures/road-surface-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	quit(0 if report.passed else 1)

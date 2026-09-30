extends SceneTree
## Move the actual compound airship collider against each independently
## instantiated cliff from front, side and above in a disposable physics scene.
var checks:Array=[]
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var space:=Node3D.new();root.add_child(space)
	var ship:CharacterBody3D=load("res://scenes/prefabs/Airship.tscn").instantiate();space.add_child(ship)
	var kit:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/cliff_kit.json"))
	if "--mountain-test" in OS.get_cmdline_user_args():kit=JSON.parse_string(FileAccess.get_file_as_string("res://assets/mountain_kit.json"))
	for item in kit:
		var cliff:Node3D=load("res://scenes/prefabs/"+item.name+".tscn").instantiate();space.add_child(cliff)
		cliff.position=Vector3(80,160,-120);cliff.rotation.y=.29
		var body:StaticBody3D=cliff.get_node("Collision")
		var shape_node:CollisionShape3D=body.get_node("Shape")
		var faces:PackedVector3Array=shape_node.shape.get_faces()
		await physics_frame
		await physics_frame
		for direction in [Vector3.FORWARD,Vector3.RIGHT,Vector3.UP]:
			var best:=-INF;var center:=Vector3.ZERO;var normal:=Vector3.UP
			for i in range(0,faces.size(),3):
				var a:Vector3=faces[i];var b:Vector3=faces[i+1];var c:Vector3=faces[i+2]
				var cross:Vector3=(b-a).cross(c-a)
				var n:Vector3=-cross.normalized()
				var score:float=n.dot(direction)*1000+minf(cross.length(),200)*.05
				if score>best:best=score;center=(a+b+c)/3;normal=n
			center=shape_node.to_global(center);normal=(shape_node.global_basis*normal).normalized()
			ship.global_transform=Transform3D(Basis.IDENTITY,center+normal*45)
			ship.velocity=Vector3.ZERO
			await physics_frame
			var collision:=ship.move_and_collide(-normal*85)
			var ok:=collision!=null and collision.get_collider()==body and collision.get_travel().length()<85
			var detail:={"name":item.name,"approach":str(direction),"passed":ok,"start":str(center+normal*45),"finish":str(ship.position),"travel":collision.get_travel().length() if collision else 85.0}
			checks.append(detail);print("PASS " if ok else "FAIL ",JSON.stringify(detail))
		ship.position=Vector3(1000,1000,1000);cliff.queue_free()
		await physics_frame
		await physics_frame
	var failures:=checks.filter(func(c):return not c.passed)
	var report:={"passed":failures.is_empty(),"checks":checks,"ship_prefab_sha256":FileAccess.get_sha256("res://scenes/prefabs/Airship.tscn"),"world_sha256":FileAccess.get_sha256("res://scenes/world/World.tscn"),"scope":"Actual airship compound CharacterBody3D against each independent cliff prefab at a translated and rotated test pose. Front, side and descent use move_and_collide."}
	var output:="res://captures/mountain-flight-validation.json" if "--mountain-test" in OS.get_cmdline_user_args() else "res://captures/cliff-flight-validation.json"
	report["provenance"]=preload("res://scripts/validation_context.gd").snapshot()
	var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	space.queue_free();await process_frame
	quit(0 if failures.is_empty() else 1)

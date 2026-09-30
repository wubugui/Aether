extends "res://tools/assemble_world.gd"
## Inspect actual derived colliders and actual native terrain in a GPU world.
func build() -> void:
	if DisplayServer.get_name()=="headless":quit(1);return
	var path:="res://scenes/world/World.tscn";var before:=FileAccess.get_sha256(path)
	var world:Node3D=load(path).instantiate(PackedScene.GEN_EDIT_STATE_INSTANCE);world.set_script(null);root.add_child(world)
	await physics_frame;await physics_frame
	var excluded:Array[RID]=[]
	for category_name in ["Cliffs","Mountains"]:
		for body in world.get_node(category_name).find_children("*","StaticBody3D",true,false):excluded.append(body.get_rid())
	var results:Array=[];var passed:=true;var total:=0
	for kind in ["cliff_crown","cliff_western_slab","cliff_front_columns","cliff_central_wall","cliff_shadow_buttress","cliff_eastern_plateau"]:
		var asset:Node3D=world.get_node("Cliffs/"+kind)
		var shape:CollisionShape3D=asset.get_node("Collision/Shape")
		var faces:PackedVector3Array=shape.shape.get_faces();var edges:Dictionary={}
		# These native source assets have a closed floor at local Y=-15 m.
		# Mixed floor/roof triangles identify their actual contact rim.
		for i in range(0,faces.size(),3):
			var above:Array[Vector3]=[];var has_floor:=false
			for p in [faces[i],faces[i+1],faces[i+2]]:
				if p.y< -14:has_floor=true
				else:above.append(p)
			if has_floor and above.size()==2:
				var key:String=str(above[0])+"/"+str(above[1]);var reverse:String=str(above[1])+"/"+str(above[0])
				if not edges.has(reverse):edges[key]=above
		var count:=0;var misses:=0;var exposed:=0;var high:=-INF;var low:=INF;var examples:Array=[]
		for edge in edges.values():
			var a:Vector3=shape.to_global(edge[0]);var b:Vector3=shape.to_global(edge[1])
			var steps:int=maxi(1,ceili(Vector2(a.x,a.z).distance_to(Vector2(b.x,b.z))/.5))
			for j in range(steps+1):
				var p:Vector3=a.lerp(b,float(j)/steps)
				var ray:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4,excluded)
				var hit:=world.get_world_3d().direct_space_state.intersect_ray(ray);count+=1
				if hit.is_empty():misses+=1;continue
				var delta:float=p.y-hit.position.y;high=maxf(high,delta);low=minf(low,delta)
				if delta>.02:
					exposed+=1
					if examples.size()<5:examples.append({"point":p,"above_ground_metres":delta,"ground":hit.position})
			if count%200<steps:await process_frame
		var ok:bool=not edges.is_empty() and misses==0 and exposed==0;passed=passed and ok;total+=count
		results.append({"name":kind,"passed":ok,"contact_edges":edges.size(),"samples":count,"misses":misses,"exposed_samples":exposed,"maximum_above_terrain_metres":high,"minimum_above_terrain_metres":low,"examples":examples})
		print("GROUND RIM ",kind," samples=",count," exposed=",exposed," max=",high)
	world.free();await process_frame
	passed=passed and FileAccess.get_sha256(path)==before
	var report:={"passed":passed,"world_sha256":before,"samples":total,"assets":results,"scope":"Six current native colliders: final floor-to-roof rim edges sampled at <=0.5 m in world XZ against actual terrain/ocean physics, excluding all cliff and mountain bodies. This checks rim seating, not all internal overlaps or flight paths."}
	report["provenance"]=preload("res://scripts/validation_context.gd").snapshot()
	var file:=FileAccess.open("res://captures/cliff-ground-rim-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	quit(0 if passed else 1)

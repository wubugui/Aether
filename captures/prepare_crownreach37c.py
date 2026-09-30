from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'tools/render_crownreach37b.gd').read_text().replace('37b','37c')
s=s.replace('var game:Node3D=load(','''# Use the saved prefab instance in World, keeping its independent
	# scene boundary and editable asset owner instead of embedding a copy.
	castle.free();castle=load(native).instantiate()
	model=castle.get_node("Model")
	var game:Node3D=load(''')
# Reopen the newly serialized full Game in a fresh object tree before GPU.
s=s.replace('\troot.add_child(game);game.set_process(false);game.set_physics_process(false)', '''	game.free();game=load(native_game).instantiate()
	root.add_child(game);game.set_process(false);game.set_physics_process(false)
	world=game.get_node("World")''')
start=s.index('\tvar views:Array=[');end=s.index('\tvar records:Array=[]',start)
s=s[:start]+'''	var views:Array=[
		["castle-front",Vector3(109,62,-197),Vector3(43.288,30,-282.521),55.0],
		["gate-low",Vector3(43.288,21.6,-261),Vector3(43.288,21.1,-283),65.0]]
'''+s[end:]
# Replace the repeated camera orbit with actual existing physics control.
start=s.index('\tvar route:Array=[]');end=s.index('\tvar paving:Array=[]',start)
s=s[:start]+'''	var route:Array=[]
	game.airship.show();game.hud.show();game.testing=true;game.test_override_input=true
	game.test_input=Vector3(0,0,1);game.test_frozen=false;game.photo_mode=false
	game.airship.position=Vector3(160,80,-280);game.airship.velocity=Vector3.ZERO
	game.heading=-deg_to_rad(13);game.throttle=1.0;game.anchored=false
	game.set_process(true);game.set_physics_process(true)
	var flight_start:Vector3=game.airship.position
	var collision_frames:int=0
	for i in range(300):
		await physics_frame
		if game.airship.get_slide_collision_count()>0:collision_frames+=1
		if i%30==0:route.append({"frame":i,"position":xyz(game.airship.position),"velocity":xyz(game.airship.velocity),"clearance":game.clearance})
	game.test_frozen=true;game.set_process(false);game.set_physics_process(false)
	var flight_end:Vector3=game.airship.position
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("flight-end.png"))==OK)
'''+s[end:]
s=s.replace('"orbit_camera_samples":route,','"physical_flight_samples":route,"flight_start":xyz(flight_start),"flight_end":xyz(flight_end),"flight_displacement_m":flight_start.distance_to(flight_end),"collision_frames":collision_frames,"world_processing_during_flight":world.is_processing(),')
s=s.replace('var p:Vector3=node.to_global(Vector3(box.position.x+box.size.x*.5,box.position.y,box.position.z+box.size.z*.5))','var p:Vector3=node.to_global(Vector3(box.position.x+box.size.x*.5,box.position.y,box.position.z+box.size.z*.5))\n\t\t\tvar top:Vector3=node.to_global(Vector3(box.position.x+box.size.x*.5,box.end.y,box.position.z+box.size.z*.5))')
s=s.replace('"gap_m":p.y-world.ground_height(p)','"gap_m":p.y-world.ground_height(p),"top_above_ground":top.y-world.ground_height(top)')
s=s.replace('"scope":"New castle asset in existing candidate World; daytime camera observations and limited support/portal checks, not flight or reference acceptance."','"scope":"Saved standalone castle prefab, fresh full native Game object reload, two local daylight views and 300 existing-controller physics frames over the central castle. World streaming frozen; not whole-world flight or reference acceptance."')
(R/'tools/render_crownreach37c.gd').write_text(s,encoding='utf-8')
p=(R/'tools/render_crownreach37b.py').read_text().replace('37b','37c')
p=p.replace("image=folder/'opening.png'","image=folder/'castle-front.png'")
p=p.replace("['castle-front','castle-back','castle-river','gate-low','orbit-end']","['gate-low','flight-end']")
p=p.replace("'37A GPU '","'37C NATIVE AND FLIGHT '")
(R/'tools/render_crownreach37c.py').write_text(p,encoding='utf-8');print('37c scripts ready')

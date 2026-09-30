from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'tools/render_crownreach37a.gd').read_text()
s=s.replace('37a','37b')
s=s.replace('var output:String','var output:String\nvar scatter_changes:Array=[]')
s=s.replace('func gather(','''func own_boundaries(node:Node,scene:Node)->void:
	for c in node.get_children():
		c.owner=scene
		if c.scene_file_path.is_empty():own_boundaries(c,scene)
func save_scene(node:Node,path:String)->void:
	node.scene_file_path="";own_boundaries(node,node)
	var p:=PackedScene.new();assert(p.pack(node)==OK);assert(ResourceSaver.save(p,path)==OK)
func clear_entry(world:Node3D)->void:
	var corridor:=AABB(Vector3(40.1,18.,-281.),Vector3(6.4,9.0,25.0))
	for grove in world.get_node("Vegetation").get_children():
		var kind:String=grove.get_meta("asset_kind")
		if kind not in ["oak","poplar","pine","bush","rock"]:continue
		var source:MultiMesh=grove.multimesh
		var keep:Array[Transform3D]=[];var removed:Array=[]
		for i in range(source.instance_count):
			var tr:Transform3D=source.get_instance_transform(i)
			var actual:Transform3D=grove.transform*tr
			if absf(actual.origin.x-43.288)>20 or absf(actual.origin.z+269)>30:
				keep.append(tr);continue
			var box:AABB=actual*source.mesh.get_aabb()
			if box.intersects(corridor):
				removed.append({"index":i,"kind":kind,"position":xyz(actual.origin),"bounds":str(box)})
			else:keep.append(tr)
		if not removed.is_empty():
			var copy:MultiMesh=source.duplicate();copy.instance_count=keep.size()
			for i in range(keep.size()):copy.set_instance_transform(i,keep[i])
			grove.multimesh=copy
			scatter_changes.append({"grove":str(grove.name),"before":source.instance_count,"after":copy.instance_count,"removed":removed,"reason":"Actual instance mesh AABB intersects gate approach; retained grove authoring helper."})
func gather(''')
start=s.index('\t# Keep the existing candidate driver')
end=s.index('\tvar storm:Node3D',start)
s=s[:start]+'''	# Assemble into a fresh unready World so saved scatter drives its later
	# collision bookkeeping. No transient runtime bodies enter the candidate.
	var world:Node3D=game.get_node("World")
	var old:Node3D=world.get_node("Settlements/castle_57174")
	castle.position=old.position;var parent:Node=old.get_parent()
	var idx:int=old.get_index();parent.remove_child(old);old.free();parent.add_child(castle);parent.move_child(castle,idx)
	clear_entry(world)
	var native_world:String=output.path_join("World37b.tscn").replace("\\\\","/")
	save_scene(world,native_world)
	game.remove_child(world);world.free()
	world=load(native_world).instantiate();world.name="World";game.add_child(world)
	var native_game:String=output.path_join("Game37b.tscn").replace("\\\\","/")
	save_scene(game,native_game)
	root.add_child(game);game.set_process(false);game.set_physics_process(false)
	game.sound_enabled=false;game.airship.hide();game.hud.hide();world.set_process(false)
	castle=world.get_node("Settlements/castle_57174");model=castle.get_node("Model")
	var daylight:Node3D=load("res://scenes/game.tscn").instantiate();held.append(daylight)
	held.append(game.get_node("Environment").environment)
	game.get_node("Environment").environment=daylight.get_node("Environment").environment
	var sun:DirectionalLight3D=game.get_node("Sun");var ds:DirectionalLight3D=daylight.get_node("Sun")
	sun.transform=ds.transform;sun.light_color=ds.light_color;sun.light_energy=ds.light_energy
	for cloud in world.get_node("Clouds").find_children("*","MeshInstance3D",true,false):
		held.append(cloud.material_override);cloud.material_override=load("res://materials/cloud.tres")
''' +s[end:]
s=s.replace('"paving_center_probes":paving,','"paving_center_probes":paving,"scatter_changes":scatter_changes,"native_world":native_world,"native_game":native_game,')
s=s.replace('"gate-low",Vector3(43.288,23,-260),Vector3(43.288,21.1,-283)','"gate-low",Vector3(43.288,21.6,-261),Vector3(43.288,21.1,-283)')
s=s.replace('castle.to_global(Vector3(x,1.7,9))','castle.to_global(Vector3(x,1.7,6))')
# Add a same-asset short moving observation around the central courtyard.
s=s.replace('\tvar paving:Array=[]','''	var route:Array=[]
	for i in range(25):
		var a:float=lerpf(-.5,.65,float(i)/24.)
		var p:Vector3=castle.position+Vector3(sin(a)*95.,40.,cos(a)*95.)
		game.camera.position=p;game.camera.look_at(castle.position+Vector3(0,10,0));game.camera.fov=58.
		world.update_focus(p,true);game.candidate_weather.sample(game.camera,0.0)
		for frame in range(3):await process_frame
		route.append({"position":xyz(p),"ground":world.ground_height(p),"clearance":p.y-world.ground_height(p)})
	await RenderingServer.frame_post_draw
	assert(root.get_texture().get_image().save_png(output.path_join("orbit-end.png"))==OK)
	var paving:Array=[]''')
s=s.replace('"gate_rays":gate,','"gate_rays":gate,"orbit_camera_samples":route,')
(R/'tools/render_crownreach37b.gd').write_text(s,encoding='utf-8')
p=(R/'tools/render_crownreach37a.py').read_text().replace('37a','37b')
p=p.replace("'gate-low']","'gate-low','orbit-end']")
p=p.replace("folder/'castle37b.tscn']","folder/'castle37b.tscn',folder/'World37b.tscn',folder/'Game37b.tscn']")
(R/'tools/render_crownreach37b.py').write_text(p,encoding='utf-8')
print('37b native and GPU scripts prepared')

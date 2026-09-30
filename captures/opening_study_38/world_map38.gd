extends SceneTree
# 38: sample the candidate world's ground_height on a grid and write a raw float map
# (JSON) so locations for coasts, lakes and snow valleys can be chosen from real data.
var output: String
func _initialize()->void: call_deferred("run")
func run()->void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--output="):output=a.trim_prefix("--output=")
	var game:Node3D=load("res://captures/candidate_opening38/Game38.tscn").instantiate()
	game.set_script(load("res://scripts/game.gd"));game.save_path="user://map38_unused.json"
	root.add_child(game);game.set_process(false);game.set_physics_process(false)
	var world:Node3D=game.get_node("World");world.set_process(false)
	for i in range(4):await process_frame
	var step:=50.0;var x0:=-4600.0;var x1:=5400.0;var z0:=-7700.0;var z1:=4600.0
	var nx:=int((x1-x0)/step);var nz:=int((z1-z0)/step)
	var rows:Array=[]
	for j in range(nz):
		var row:=PackedFloat32Array()
		for i in range(nx):row.append(world.ground_height(Vector3(x0+i*step,0,z0+j*step)))
		rows.append(Array(row))
	var marks:Array=[]
	for parent in ["Mountains","Cliffs","Ports","Settlements"]:
		var n:Node=world.get_node_or_null(parent)
		if n==null:continue
		for c in n.get_children():
			if c is Node3D and (parent!="Settlements" or String(c.name).begins_with("lighthouse") or String(c.name).begins_with("mill") or String(c.name).begins_with("dock")):
				marks.append({"name":String(c.name),"parent":parent,"x":c.global_position.x,"z":c.global_position.z,"y":c.global_position.y})
	var f:=FileAccess.open(output,FileAccess.WRITE)
	f.store_string(JSON.stringify({"x0":x0,"z0":z0,"step":step,"nx":nx,"nz":nz,"h":rows,"marks":marks}));f.close()
	quit()

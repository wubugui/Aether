extends SceneTree
# 38: one Godot process renders several look variants of the 36c candidate world
# by patching shader code / uniforms / environment at runtime. No project file is
# modified. Args: --output-dir=<dir> --variants=<json> [--views=opening,castle-front]
var output: String
var variants_path: String
var view_filter: PackedStringArray = []
var game_path: String = "res://captures/candidate_highcoast36c/Game36c.tscn"
var swap_castle: String = ""
var shaders: Array = []          # unique Shader resources in the scene
var originals: Dictionary = {}   # Shader -> original code
var materials: Array = []        # unique ShaderMaterials
var orig_params: Dictionary = {} # "idx|name" -> original value

func _initialize()->void: call_deferred("run")
func xyz(v:Vector3)->Array:return [v.x,v.y,v.z]

func add_material(m:Material)->void:
	if m==null:return
	if m is ShaderMaterial:
		if not materials.has(m):materials.append(m)
		var s:Shader=m.shader
		if s!=null and not shaders.has(s):
			shaders.append(s);originals[s]=s.code
	if m.next_pass!=null:add_material(m.next_pass)

func collect(n:Node)->void:
	if n is GeometryInstance3D:
		add_material(n.material_override)
		var mesh:Mesh=null
		if n is MeshInstance3D:
			mesh=n.mesh
			for i in range(n.get_surface_override_material_count()):add_material(n.get_surface_override_material(i))
		elif n is MultiMeshInstance3D and n.multimesh!=null:
			mesh=n.multimesh.mesh
		if mesh!=null:
			for i in range(mesh.get_surface_count()):add_material(mesh.surface_get_material(i))
	for c in n.get_children():collect(c)

func to_value(v):
	if v is Array and v.size()==3:return Vector3(v[0],v[1],v[2])
	if v is Array and v.size()==4:return Color(v[0],v[1],v[2],v[3])
	return v

func apply_variant(game:Node3D,env:Environment,base_env:Environment,sun:DirectionalLight3D,base_sun:Dictionary,variant:Dictionary)->Dictionary:
	var counts:Dictionary={}
	for s in shaders:
		var code:String=originals[s]
		for pair in variant.get("replace",[]):
			var n:int=code.count(pair[0])
			if n>0:
				counts[pair[0]]=counts.get(pair[0],0)+n
				code=code.replace(pair[0],pair[1])
		if code!=s.code:s.code=code
	# uniforms: restore originals first, then set requested ones where the shader declares them
	for i in range(materials.size()):
		var m:ShaderMaterial=materials[i]
		for key in orig_params.keys():
			if key.begins_with(str(i)+"|"):m.set_shader_parameter(key.get_slice("|",1),orig_params[key])
	var params:Dictionary=variant.get("params",{})
	var touched:=0
	for i in range(materials.size()):
		var m:ShaderMaterial=materials[i]
		if m.shader==null:continue
		for pname in params.keys():
			if m.shader.code.contains("uniform") and m.shader.code.contains(" "+pname):
				var k:String=str(i)+"|"+pname
				if not orig_params.has(k):orig_params[k]=m.get_shader_parameter(pname)
				m.set_shader_parameter(pname,to_value(params[pname]));touched+=1
	# environment
	var e:Dictionary=variant.get("env",{})
	for prop in ["fog_density","fog_light_energy","ambient_light_energy","fog_sky_affect","adjustment_saturation","adjustment_contrast","adjustment_brightness","tonemap_exposure","fog_height","fog_height_density","fog_aerial_perspective"]:
		env.set(prop,e.get(prop,base_env.get(prop)))
	for prop in ["fog_light_color","ambient_light_color"]:
		env.set(prop,to_value(e[prop]) if e.has(prop) else base_env.get(prop))
	env.adjustment_enabled=e.has("adjustment_saturation") or e.has("adjustment_contrast") or e.has("adjustment_brightness")
	var sv:Dictionary=variant.get("sun",{})
	sun.light_color=to_value(sv["light_color"]) if sv.has("light_color") else base_sun["light_color"]
	sun.light_energy=sv.get("light_energy",base_sun["light_energy"])
	return {"replacements":counts,"params_set":touched}

func run()->void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--output-dir="):output=a.trim_prefix("--output-dir=")
		if a.begins_with("--variants="):variants_path=a.trim_prefix("--variants=")
		if a.begins_with("--views="):view_filter=a.trim_prefix("--views=").split(",")
		if a.begins_with("--game="):game_path=a.trim_prefix("--game=")
		if a.begins_with("--swap-castle="):swap_castle=a.trim_prefix("--swap-castle=")
	DirAccess.make_dir_recursive_absolute(output)
	var variants:Array=JSON.parse_string(FileAccess.get_file_as_string(variants_path))
	var t0:=Time.get_ticks_msec()
	var game:Node3D=load(game_path).instantiate()
	game.set_script(load("res://scripts/game.gd"))
	game.save_path="user://opening38_inspection_unused.json"
	var daylight:Node3D=load("res://scenes/game.tscn").instantiate()
	game.get_node("Environment").environment=daylight.get_node("Environment").environment.duplicate(true)
	var sun:DirectionalLight3D=game.get_node("Sun")
	var day_sun:DirectionalLight3D=daylight.get_node("Sun")
	sun.transform=day_sun.transform;sun.light_color=day_sun.light_color;sun.light_energy=day_sun.light_energy
	daylight.free()
	root.add_child(game)
	game.set_process(false);game.set_physics_process(false);game.sound_enabled=false
	game.airship.hide();game.hud.hide()
	var world:Node3D=game.get_node("World")
	world.set_process(false)
	if swap_castle!="":
		var old:Node3D=world.get_node("Settlements/castle_57174")
		var nc:Node3D=load(swap_castle).instantiate();nc.name="castle_57174"
		nc.position=old.position;var par:Node=old.get_parent();var idx:int=old.get_index()
		par.remove_child(old);old.free();par.add_child(nc);par.move_child(nc,idx)
		print("castle swapped: ",swap_castle)
	var env:Environment=game.get_node("Environment").environment
	var base_env:Environment=env.duplicate(true)
	var base_sun:={"light_color":sun.light_color,"light_energy":sun.light_energy}
	var all_views:Array=[
		["opening",Vector3(0,145,250),Vector3(0,83.837,-750),50.0],
		["castle-front",Vector3(109,62,-197),Vector3(43.288,30,-282.521),55.0],
		["side-east",Vector3(420,160,-120),Vector3(-300,40,-700),55.0],
		["reverse",Vector3(0,150,-900),Vector3(0,40,200),55.0]]
	var views:Array=[]
	for v in all_views:
		if view_filter.is_empty() or view_filter.has(v[0]):views.append(v)
	# first focus pass so streamed terrain/scatter exist before collecting materials
	game.camera.position=views[0][1];game.camera.look_at(views[0][2]);game.camera.fov=views[0][3]
	world.update_focus(views[0][1],true)
	for i in range(8):await process_frame
	collect(game)
	var env_mat:Material=env.sky.sky_material if env.sky!=null else null
	add_material(env_mat)
	var load_ms:=Time.get_ticks_msec()-t0
	var rows:Array=[]
	for variant in variants:
		var info:=apply_variant(game,env,base_env,sun,base_sun,variant)
		for view in views:
			game.camera.position=view[1];game.camera.look_at(view[2]);game.camera.fov=view[3]
			world.update_focus(view[1],true)
			for i in range(16):await process_frame
			await RenderingServer.frame_post_draw
			var path:String=output.path_join("%s__%s.png"%[variant["name"],view[0]])
			assert(root.get_texture().get_image().save_png(path)==OK)
			rows.append({"variant":variant["name"],"view":view[0],"image":path,"position":xyz(view[1]),"target":xyz(view[2]),"fov":view[3]})
		rows.append({"variant":variant["name"],"apply":info})
		print("variant done: ",variant["name"]," ",info)
	var report:={"source_game":game_path,"shaders":shaders.size(),"materials":materials.size(),"load_ms":load_ms,"total_ms":Time.get_ticks_msec()-t0,"rows":rows,"scope":"Runtime look study only; no project file modified."}
	var f:=FileAccess.open(output.path_join("report.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));f.close()
	game.queue_free();await process_frame;await process_frame;quit()

extends SceneTree
## Isolate the remaining two shutdown textures without altering acceptance evidence.
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var mode := "sky"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
	var parent := Node3D.new()
	root.add_child(parent)
	var world_env := WorldEnvironment.new()
	var environment := Environment.new()
	var sky := Sky.new()
	var material := ShaderMaterial.new()
	material.shader = load("res://scripts/environment39_sky.gdshader")
	sky.sky_material = material
	environment.background_mode = Environment.BG_SKY
	environment.sky = sky
	world_env.environment = environment
	parent.add_child(world_env)
	if mode == "swap-sky":
		var second_environment := Environment.new()
		var second_sky := Sky.new()
		var second_material := ShaderMaterial.new()
		second_material.shader = load("res://scripts/environment39_sky.gdshader")
		second_sky.sky_material = second_material
		second_environment.background_mode = Environment.BG_SKY
		second_environment.sky = second_sky
		world_env.environment = second_environment
	var camera := Camera3D.new()
	parent.add_child(camera)
	if mode == "font":
		var control := Control.new()
		parent.add_child(control)
		var font := SystemFont.new()
		font.font_names = PackedStringArray(["Microsoft YaHei UI", "Arial"])
		control.draw.connect(func(): control.draw_string(font, Vector2(20,40), "Skyfarer 测试",HORIZONTAL_ALIGNMENT_LEFT,-1,17))
		control.queue_redraw()
	for i in range(8): await process_frame
	parent.queue_free()
	for i in range(8): await process_frame
	print("RENDERER PROBE DONE ",mode)
	quit()

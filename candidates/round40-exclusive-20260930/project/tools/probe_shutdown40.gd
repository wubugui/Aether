extends SceneTree
## Narrow lifecycle probe of actual candidate; never changes saved resources.
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var mode := "normal"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--mode="): mode = arg.trim_prefix("--mode=")
	var game: Node3D = load("res://scenes/candidate40/Game40b.tscn").instantiate()
	root.add_child(game)
	game.sound_enabled = false
	game.test_frozen = true
	if mode == "no-hud": game.get_node("Flight interface").queue_free()
	if mode == "no-sky":
		game.get_node("Environment").environment.sky = null
		game.get_node("Environment").environment.background_mode = Environment.BG_COLOR
	for i in range(15): await process_frame
	if mode == "clear-font-cache":
		var text_server := TextServerManager.get_primary_interface()
		var fonts: Array[Font] = [ThemeDB.fallback_font, game.hud.ui_font]
		for font in fonts:
			for rid in font.get_rids():
				for cache_size in text_server.font_get_size_cache_list(rid):
					text_server.font_clear_textures(rid,cache_size)
	game.queue_free()
	for i in range(15): await process_frame
	print("SHUTDOWN40 PROBE ",mode)
	quit()

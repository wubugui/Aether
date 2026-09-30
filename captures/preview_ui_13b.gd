extends SceneTree
func _initialize() -> void:call_deferred("preview")
func preview() -> void:
	var game:Node3D=load("res://scenes/game.tscn").instantiate()
	game.set_script(load("res://captures/game_13b.gd"));root.add_child(game)

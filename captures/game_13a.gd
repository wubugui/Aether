extends "res://scripts/game.gd"
func _ready() -> void:
	super._ready()
	var canvas:CanvasLayer=hud.get_parent()
	canvas.remove_child(hud);hud.queue_free()
	hud=preload("res://captures/game_hud_13a.gd").new();hud.game=self;canvas.add_child(hud)

extends "res://scripts/game.gd"
@export var candidate_weather_folder:String
var candidate_weather:RefCounted

func _ready()->void:
	save_path="user://highcoast36b_candidate_progress.json"
	super._ready()
	airship.position=Vector3(-2280,230,-1910)
	airship.velocity=Vector3.ZERO
	world.update_focus(airship.position,true)
	camera.position=Vector3(-2250,250,-1870)
	camera.look_at(Vector3(-3040,120,-3580));camera.fov=65.
	altitude=airship.position.y;anchored=true
	candidate_weather=load(candidate_weather_folder.path_join("storm_front_35c.gd")).new()
	candidate_weather.configure(self,candidate_weather_folder)

func _process(delta:float)->void:
	super._process(delta)
	if candidate_weather!=null:candidate_weather.sample(camera,elapsed)

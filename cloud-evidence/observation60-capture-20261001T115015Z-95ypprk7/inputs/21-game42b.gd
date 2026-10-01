extends "res://scripts/game.gd"
## Same live game and environment used by player and acceptance captures.
@export var candidate_weather_folder: String
var scene_environment: Node
var reference_observation := false

func _ready() -> void:
	save_path = "user://round42b_progress.json"
	super._ready()
	scene_environment = get_node("SceneEnvironment42b")
	# Child environment initialized against the exact loaded native scene.
	scene_environment.apply_reference("1343")
	toast("第40轮候选 · B切换日夜 · [ / ]参考观察点 · W/S/A/D/E/Q飞行", 18)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_B:
			scene_environment.apply_reference("1342" if scene_environment.current_reference != "1342" else "1343")
			toast("月夜" if scene_environment.current_reference == "1342" else "白日")
			return
		if event.physical_keycode in [KEY_BRACKETLEFT, KEY_BRACKETRIGHT]:
			var ids: Array[String] = []
			for entry in scene_environment.plan: ids.append(str(entry.ref))
			var index: int = ids.find(scene_environment.current_reference)
			index = posmod(index + (1 if event.physical_keycode == KEY_BRACKETRIGHT else -1), ids.size())
			observe_reference(ids[index])
			return
	super._unhandled_input(event)
	if not photo_mode: reference_observation = false

func update_camera(delta: float) -> void:
	if reference_observation and photo_mode: return
	super.update_camera(delta)

func observe_reference(id: String) -> Dictionary:
	var entry: Dictionary = scene_environment.reference(id)
	assert(not entry.is_empty())
	var c: Dictionary = entry["camera"]
	var position := Vector3(c['x'],0,c['z'])
	position.y = float(c['y_abs']) if c.has('y_abs') else world.ground_height(position)+float(c.get('agl',120))
	var target := Vector3(c['tx'],0,c['tz'])
	target.y = float(c['ty_abs']) if c.has('ty_abs') else world.ground_height(target)+float(c.get('target_agl',0))
	photo_mode = true
	reference_observation = true
	airship.velocity = Vector3.ZERO
	vertical_speed = 0
	speed = 0
	throttle = 0
	auto_pilot = false
	docked = false
	dock_id = ""
	anchored = true
	# Inspection viewpoint is navigation in this actual world, not new scenery.
	airship.position = position + Vector3(0, 35, 45)
	if entry.has("airship"):
		var placement: Dictionary = entry["airship"]
		var forward := (target - position).normalized()
		var right := forward.cross(Vector3.UP).normalized()
		airship.position = position + forward * float(placement.get("dist", 40)) + right * float(placement.get("right", 0)) + Vector3.UP * float(placement.get("up", 0))
		airship.rotation.y = float(placement.get("yaw", .4))
	heading = airship.rotation.y - deg_to_rad(13)
	world.update_focus(position, true)
	camera.position = position
	camera.look_at(target)
	camera.fov = float(c.get("fov", 55))
	visuals.visible = id not in ["1274", "1278"]
	var result: Dictionary = scene_environment.apply_reference(id)
	toast("参考 " + id + " · F2退出观察继续飞行", 12)
	return result

extends Node3D
## Persistent physical weather in the live world. No camera-owned effects.
var time_seconds := 0.0
var rain_strength := 0.0
var snow_strength := 0.0
var cloud_lightning := false
var coastal_lightning := false
var phase := 0.0
@export var time_scale := 1.0
var local_illumination_enabled := true

func apply_state(state: Dictionary) -> void:
	rain_strength = float(state.get('rain',0.0))
	snow_strength = float(state.get('snow',0.0))
	cloud_lightning = float(state.get('lightning',0.0)) > 0
	coastal_lightning = state.has('bolts')
	$Rain.visible = rain_strength > 0
	$Snow.visible = snow_strength > 0
	$Rain.multimesh.visible_instance_count = int($Rain.multimesh.instance_count*rain_strength)
	$Snow.multimesh.visible_instance_count = int($Snow.multimesh.instance_count*snow_strength)
	$Rainbow.visible = state.has('rainbow')
	update_flash()

func seek_time(seconds: float) -> void:
	time_seconds = seconds
	update_precipitation()
	update_flash()

func _process(delta: float) -> void:
	time_seconds += delta*time_scale
	# The local simulation window moves on a world grid around the aircraft,
	# with fixed native particle locations. Camera rotation does not move it.
	var ship: Node3D = get_parent().get_node_or_null('Airship')
	if ship != null:
		var anchor := ship.global_position.snapped(Vector3(64,32,64))
		$Rain.global_position = anchor
		$Snow.global_position = anchor
	update_precipitation()
	update_flash()

func update_precipitation() -> void:
	$Rain.material_override.set_shader_parameter('precipitation_time',time_seconds)
	$Snow.material_override.set_shader_parameter('precipitation_time',time_seconds)

func update_flash() -> void:
	var cycle := fposmod(time_seconds,5.4)
	phase = 1.0 if (cycle < .10 or (cycle > .18 and cycle < .24)) else 0.0
	for zone in [$CoastalStorm,$CloudStorm]:
		var active: bool = coastal_lightning if zone.name == 'CoastalStorm' else cloud_lightning
		for node in zone.get_children():
			if node is Light3D: node.light_energy = (9.0 if active and local_illumination_enabled else 0.0)*phase
			else: node.visible = active and phase > 0

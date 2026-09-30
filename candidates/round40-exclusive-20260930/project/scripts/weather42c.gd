extends "res://scripts/weather42b.gd"
## Actual per-instance world-space motion avoids clipping a deformed GPU mesh
## at the eye. Meshes retain their Blender shape and native engine lighting.
var rest_positions: Dictionary = {}
var last_update := -INF
func _ready() -> void:
	for node in [$Rain,$Snow]:
		var points: Array[Vector3] = []
		for i in range(node.multimesh.instance_count):points.append(node.multimesh.get_instance_transform(i).origin)
		rest_positions[node.name]=points
	update_precipitation()

func update_precipitation() -> void:
	if rest_positions.is_empty():return
	if absf(time_seconds-last_update)<.025:return
	last_update=time_seconds
	for node in [$Rain,$Snow]:
		if not node.visible:continue
		var speed := 36.0 if node.name=='Rain' else 5.0
		var drift := .22 if node.name=='Rain' else .12
		var points: Array=rest_positions[node.name]
		for i in range(node.multimesh.visible_instance_count):
			var p: Vector3=points[i]
			p.y=fposmod(p.y+80-time_seconds*speed,160)-80
			p.x=fposmod(p.x+110+time_seconds*speed*drift,220)-110
			node.multimesh.set_instance_transform(i,Transform3D(Basis.IDENTITY,p))
		node.material_override.set_shader_parameter('precipitation_time',time_seconds)

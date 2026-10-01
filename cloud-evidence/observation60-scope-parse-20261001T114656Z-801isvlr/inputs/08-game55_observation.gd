extends "res://scripts/game42b.gd"
## Independent observation candidate; same original world and flight controller.
## Only these two photo/navigation poses change. Source geometry and FOV do not.
@export var improved_lake_observation := true
const POSES_FILE := "res://assets/observation55/lake_observation_poses.json"
var _lake_poses: Dictionary = {}

func observe_reference(id: String) -> Dictionary:
 var result: Dictionary = super.observe_reference(id)
 if not improved_lake_observation or id not in ["1128", "1129"]:
  return result
 if _lake_poses.is_empty():
  var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(POSES_FILE))
  assert(parsed is Dictionary and parsed.has(id), "Missing independent lake pose data")
  _lake_poses = parsed
 var pose: Dictionary = _lake_poses[id]
 var camera_angles: Vector3 = camera.rotation
 camera.position.y = float(pose.camera_y)
 camera_angles.x = deg_to_rad(float(pose.camera_pitch_degrees))
 camera.rotation = camera_angles
 var position_values: Array = pose.ship_position
 var ship_angles: Vector3 = airship.rotation
 ship_angles.y = float(pose.ship_yaw)
 airship.position = Vector3(position_values[0], position_values[1], position_values[2])
 airship.rotation = ship_angles
 # Preserve ordinary controller continuity when F2 exits reference observation.
 heading = airship.rotation.y - deg_to_rad(13)
 altitude = airship.position.y
 clearance = altitude - world.ground_height(airship.position)
 get_node("World/LakeReflection51").refresh_now()
 return result

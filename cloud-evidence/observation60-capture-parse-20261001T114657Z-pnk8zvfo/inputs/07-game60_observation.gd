extends "res://scripts/game55_observation.gd"
## Independent switchable cloud observation; inherited native coast/lake world.
@export var improved_cloud_observation := true
const CLOUD_POSE_FILE := "res://assets/observation60/cloud_observation_pose.json"
var _cloud_pose: Dictionary = {}

func observe_reference(id: String) -> Dictionary:
 var result: Dictionary = super.observe_reference(id)
 if not improved_cloud_observation or id != "1216":
  return result
 if _cloud_pose.is_empty():
  var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CLOUD_POSE_FILE))
  assert(parsed is Dictionary and parsed.has(id), "Missing cloud observation pose")
  _cloud_pose = parsed
 var pose: Dictionary = _cloud_pose[id]
 var position_values: Array = pose.ship_position
 var angles: Vector3 = airship.rotation
 airship.position = Vector3(position_values[0], position_values[1], position_values[2])
 angles.y = float(pose.ship_yaw)
 airship.rotation = angles
 heading = airship.rotation.y - deg_to_rad(13)
 altitude = airship.position.y
 clearance = altitude - world.ground_height(airship.position)
 get_node("World/LakeReflection51").refresh_now()
 return result

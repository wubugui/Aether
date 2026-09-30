extends RefCounted
## Bind validation evidence to the files that actually ran.
static func snapshot() -> Dictionary:
	var hashes:={}
	var run_id:=""
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--validation-run="):run_id=argument.trim_prefix("--validation-run=")
	for path in ["res://scenes/world/World.tscn","res://scenes/prefabs/Airship.tscn","res://scripts/game.gd","res://scripts/world_math.gd","res://scripts/hud.gd","res://assets/mountain_kit.json","res://assets/cliff_kit.json","res://assets/road_kit.json"]:
		if FileAccess.file_exists(path):hashes[path]=FileAccess.get_sha256(path)
	var packaged:=OS.has_feature("template")
	if packaged:
		var executable:=OS.get_executable_path()
		hashes[executable]=FileAccess.get_sha256(executable)
		var pack:=executable.get_basename()+".pck"
		if FileAccess.file_exists(pack):hashes[pack]=FileAccess.get_sha256(pack)
	return {"run_id":run_id,"utc":Time.get_datetime_string_from_system(true),"packaged":packaged,"engine":Engine.get_version_info().string,"sha256":hashes}

extends SceneTree
func _initialize() -> void:
	print("ACTUAL ENVIRONMENT CONSTANTS ",JSON.stringify({"background":Environment.AMBIENT_SOURCE_BG,"disabled":Environment.AMBIENT_SOURCE_DISABLED,"color":Environment.AMBIENT_SOURCE_COLOR,"sky":Environment.AMBIENT_SOURCE_SKY}))
	quit()

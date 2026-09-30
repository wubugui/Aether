extends SceneTree
func _initialize() -> void:
	for name in ["EditorInterface","EditorFileSystem","EditorUndoRedoManager"]:
		var selected:Array=[]
		for method in ClassDB.class_get_method_list(name):
			if "scene" in method.name or "inspect" in method.name or "select" in method.name or "reimport" in method.name or "action" in method.name:selected.append(method.name)
		print(name,": ",selected)
	quit()

extends SceneTree
func _initialize()->void:call_deferred("inspect")
func inspect()->void:
	var world:Node=load("res://captures/candidate_highcoast36c/World36c.tscn").instantiate()
	var total:int=0;var pines:Array=[]
	for grove in world.get_node("Vegetation").get_children():
		total+=grove.multimesh.instance_count
		if str(grove.name).contains("CoastalPines"):
			pines.append({"name":str(grove.name),"count":grove.multimesh.instance_count})
	var result:String=JSON.stringify({"total":total,"pine_groups":pines,"groves":world.get_node("Vegetation").get_child_count()})
	var file:=FileAccess.open("res://captures/candidate_highcoast36c/scatter-intake36f.json",FileAccess.WRITE);file.store_string(result);file.close();print(result)
	world.free();await process_frame;quit()

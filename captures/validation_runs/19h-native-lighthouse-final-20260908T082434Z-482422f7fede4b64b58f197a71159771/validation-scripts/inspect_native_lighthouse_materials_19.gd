extends SceneTree
func _initialize() -> void:
	var scene:Node3D=load("res://scenes/prefabs/lighthouse.tscn").instantiate()
	root.add_child(scene)
	var rows:Array=[]
	for node in scene.get_node("Model").find_children("*","MeshInstance3D",true,false):
		for i in range(node.mesh.get_surface_count()):
			var mat:BaseMaterial3D=node.get_active_material(i)
			rows.append({"node":str(node.name),"material":mat.resource_name,"transparency_enum":mat.transparency,"alpha":mat.albedo_color.a,"override":node.material_override!=null})
	print(JSON.stringify({"ALPHA":BaseMaterial3D.TRANSPARENCY_ALPHA,"ALPHA_DEPTH_PRE_PASS":BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS,"materials":rows},"  "))
	quit()

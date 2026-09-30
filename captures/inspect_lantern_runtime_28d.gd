extends SceneTree
func _initialize():
	for asset in ["lantern_beam","lantern_halo"]:
		var doc:=GLTFDocument.new();var state:=GLTFState.new()
		assert(doc.append_from_file("res://captures/lantern_volume_assets_28a/"+asset+".glb",state)==OK)
		var node=doc.generate_scene(state);root.add_child(node)
		print("OPTICAL ROOT ",asset," ",node.get_class()," ",node.name)
		var nodes:Array=[node];nodes.append_array(node.find_children("*","",true,false))
		for n in nodes:
			print("NODE ",n.name," ",n.get_class())
			if n is MeshInstance3D:print("MESH surfaces=",n.mesh.get_surface_count()," bounds=",n.get_aabb()," visible=",n.is_visible_in_tree())
	quit()

extends "res://tools/reflection51b_saved_audit.gd"
## Exact 25 deleted / 75 added mesh paths only. Roots and all connections stay audited.
var excluded_paths := {}
func snapshot(game: Node, _mask_edits := true) -> Dictionary:
	var data: Dictionary=super.snapshot(game,false)
	for path in excluded_paths:data.erase(path)
	return data
func graph_state(game: Node, packed: PackedScene, _mask_new := true) -> Dictionary:
	var result: Dictionary=super.graph_state(game,packed,false)
	var order := []
	for path in result.order:
		if not excluded_paths.has(path):order.append(path)
	result.order=order
	for field in ["owners","groups","scene_paths"]:
		for path in excluded_paths:result[field].erase(path)
	# Keep all persistent connections: a connection touching a deleted node is
	# never silently excused. Keep PackedScene flags, excluding private string IDs.
	result.packed_resource_flags=resource_except(packed,["_bundled"])
	return result
func full_snapshot(game: Node) -> Dictionary:return super.snapshot(game,false)
func exact_changes(a: Dictionary,b: Dictionary) -> Dictionary:
	var result := {"removed_nodes":[],"added_nodes":[],"changed_properties":[]}
	for path in a:
		if not b.has(path):result.removed_nodes.append(path);continue
		for key in a[path]:
			if not b[path].has(key) or a[path][key]!=b[path][key]:result.changed_properties.append({"path":path,"property":key,"before":a[path][key],"after":b[path].get(key)})
		for key in b[path]:
			if not a[path].has(key):result.changed_properties.append({"path":path,"property":key,"before":null,"after":b[path][key]})
	for path in b:
		if not a.has(path):result.added_nodes.append(path)
	result.removed_nodes.sort();result.added_nodes.sort()
	return result
func mesh_flags(node: MeshInstance3D) -> Dictionary:
	resource_cache.clear()
	var result := {}
	for property in node.get_property_list():
		var key: String=property.name
		if property.usage & PROPERTY_USAGE_STORAGE and key not in ["owner","scene_file_path","name","mesh","transform"]:result[key]=canonical(node.get(key))
	return result
func source_transform(node: Node3D) -> Transform3D:
	var result: Transform3D=node.transform
	var parent := node.get_parent()
	while parent!=null:
		if parent is Node3D:result=parent.transform*result
		parent=parent.get_parent()
	return result
func transform_values(value: Transform3D) -> Array:
	return [value.basis.x.x,value.basis.x.y,value.basis.x.z,value.basis.y.x,value.basis.y.y,value.basis.y.z,value.basis.z.x,value.basis.z.y,value.basis.z.z,value.origin.x,value.origin.y,value.origin.z]
func weather_state(game: Node) -> Dictionary:
	resource_cache.clear()
	var data := {}
	for pair in [["Rain",1800],["Snow",1200]]:
		var mm: MultiMesh=game.get_node("Weather42b/"+str(pair[0])).multimesh
		data[pair[0]]={"count":mm.instance_count,"floats":mm.buffer.size(),"valid":mm.instance_count==pair[1] and mm.buffer.size()==pair[1]*16 and mm.get_instance_transform(0).basis.determinant()!=0,"buffer_sha256":digest(mm.buffer),"canonical":canonical(mm)}
	return data
func material_bindings(game: Node) -> Dictionary:
	resource_cache.clear()
	var result := {}
	var report: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://scenes/candidate51b/build-report-51b.json"))
	for row in report.binding_ledger:
		var material: Material=game.get_node(row.path).get(row.property)
		result[row.path+"|"+row.property]=[material.resource_path,canonical(material),material.shader.resource_path if material is ShaderMaterial else ""]
	var paths := []
	for material in game.get_node(CTRL).get("clipping_materials"):paths.append(material.resource_path)
	result["controller_exact_clipping_paths"]=paths
	return result

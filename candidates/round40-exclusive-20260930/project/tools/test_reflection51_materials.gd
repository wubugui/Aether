extends "res://tools/build_lake_reflection51.gd"
## Headless source-resource factory check only. No scene instantiation or save;
## no MultiMesh buffer read, no GPU correctness claim.
var test_state: SceneState
var by_path := {}
func _initialize() -> void: call_deferred("test_factory")
func property_at(path: String,name: String,fallback: Variant=null) -> Variant:
	if not by_path.has(path): return fallback
	var index: int=by_path[path]
	for j in range(test_state.get_node_property_count(index)):
		if str(test_state.get_node_property_name(index,j))==name: return test_state.get_node_property_value(index,j)
	return fallback
func test_factory() -> void:
	var packed: PackedScene=ResourceLoader.load(BASE,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE)
	test_state=packed.get_state()
	for i in range(test_state.get_node_count()): by_path[str(test_state.get_node_path(i)).trim_prefix("./")]=i
	var sources := {}
	var scope: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(SCOPE_PATH))
	for row in scope.node_scope:
		var path: String=row.node_path
		if not by_path.has(path): continue
		var authority: String=str(row.authority_owner) if row.authority_owner!=null else ""
		var source: Material
		if path.begins_with("Airship/Visuals/") and not property_at(path,"metadata/persistent_material40",false):
			source=property_at("Airship","cloth_material" if path.get_file()=="Flag" else "hull_material")
		elif not authority.is_empty(): source=property_at(authority,"surface_material")
		else:
			source=property_at(path,"material_override")
			if source==null:
				var mesh: Mesh=property_at(path,"mesh")
				if mesh==null:
					var mm: MultiMesh=property_at(path,"multimesh")
					if mm!=null: mesh=mm.mesh
				if mesh==null: push_error("Missing mesh "+path);quit(1);return
				for surface in range(mesh.get_surface_count()):
					var material: Material=property_at(path,"surface_material_override/"+str(surface),mesh.surface_get_material(surface))
					if material!=null: sources[material.get_instance_id()]=material
		if source!=null: sources[source.get_instance_id()]=source
	for key in ["stream_terrain_material","stream_world_material","stream_cloud_material"]:
		var material: Material=property_at("World",key)
		sources[material.get_instance_id()]=material
	var factory := Factory.new()
	if not factory.configure(SOURCE_ROOT,Callable(self,"digest"),Callable(self,"canonical")): print(factory.failure);quit(1);return
	var originals := {}
	for id in sources: originals[id]=digest(canonical(sources[id]))
	for id in sources:
		if factory.copy_material(sources[id])==null: print("FACTORY TEST FAILED ",factory.failure);quit(1);return
	resource_cache.clear()
	var ok := sources.size()==114 and factory.materials.size()==114
	for id in sources: ok=ok and originals[id]==digest(canonical(sources[id]))
	var classes := {}
	for row in factory.material_ledger: classes[row.source_class]=int(classes.get(row.source_class,0))+1
	print(JSON.stringify({"source_only_factory_passed":ok,"source_material_count":sources.size(),"copied_material_count":factory.materials.size(),"classes":classes,"next_pass_null_count":factory.material_ledger.size(),"injection_source_count":factory.shader_entries.size(),"copied_shader_resource_count":factory.shaders.size(),"no_scene_instantiation":true,"no_scene_or_resource_save":true,"no_MM_buffer_reads":true,"gpu_verified":false}))
	for i in range(3): await process_frame
	quit(0 if ok else 1)

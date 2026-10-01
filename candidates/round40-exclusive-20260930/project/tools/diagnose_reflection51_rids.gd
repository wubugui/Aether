extends "res://tools/diagnose_reflection51_groups.gd"
## Unrun backup diagnostic: identical original materials with only new resource
## identities. No conversion, clipping insertion, shader rewrite or saved changes.
var material_clones := {}
var shader_clones := {}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
	call_deferred("run")
func duplicate_original(material: Material,duplicate_shader: bool) -> Material:
	var id := material.get_instance_id()
	if not material_clones.has(id): material_clones[id]=material.duplicate(false)
	var copy: Material=material_clones[id]
	if material is ShaderMaterial:
		if duplicate_shader:
			var shader_id: int=material.shader.get_instance_id()
			if not shader_clones.has(shader_id):shader_clones[shader_id]=material.shader.duplicate(false)
			copy.shader=shader_clones[shader_id]
		else:copy.shader=material.shader
		for uniform in material.shader.get_shader_uniform_list():copy.set_shader_parameter(uniform.name,material.get_shader_parameter(uniform.name))
	resource_cache.clear()
	check(canonical(copy)==canonical(material),"RID-only clone retains every original material/code/uniform property",{"source":material.resource_path,"new_material_rid":str(copy.get_rid()),"shader_rid_also_new":duplicate_shader and material is ShaderMaterial})
	return copy
func apply_rid_mode(duplicate_shader: bool) -> void:
	apply_bindings(true)
	for row in stored_rows:
		game.get_node(row.path).set(row.property,duplicate_original(row.original,duplicate_shader))
	for row in live_rows.values():
		var node:=game.get_node_or_null(row.path)
		if node!=null:node.set(row.property,duplicate_original(row.original,duplicate_shader))
	var ocean: ShaderMaterial=duplicate_original(source_ocean,duplicate_shader)
	game.get_node("World/Ocean").material_override=ocean;depth_controller.water=ocean;depth_controller.set_depth_enabled(false)
	# Preserve original render-layer selection throughout both RID-only controls.
	game.camera.cull_mask=original_camera_mask;game.get_node("World/Ocean").layers=original_ocean_layers
	controller.set_effect_flags(false,false)
func observations() -> void:
	root.size=Vector2i(1180,664);root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	var before:=collision_activity(game);freeze_tree(game);await physics_frame;await physics_frame
	check(before==collision_activity(game),"RID diagnostic preserves active physics")
	if not await prepare_view("1128"):return
	apply_bindings(true);reference_image=await shot("RID-A-original","1128")
	apply_rid_mode(false)
	var material_only:=await shot("RID-B-identical-material-clones","1128")
	group_results.append({"name":"identical-material-new-RID-only","pixel_delta":pixel_delta(reference_image,material_only),"conversion":false,"injection":false})
	apply_rid_mode(true)
	var shader_also:=await shot("RID-C-identical-material-and-shader-clones","1128")
	group_results.append({"name":"identical-material-plus-identical-shader-new-RID","pixel_delta":pixel_delta(reference_image,shader_also),"conversion":false,"injection":false})
	group_results.append({"name":"same-material-RIDs-original-vs-cloned-shader-RIDs","pixel_delta":pixel_delta(material_only,shader_also),"standard_material_internal_shaders_unchanged":true})
	apply_bindings(true)
	var restored:=await shot("RID-A2-original-restored","1128")
	check(pixel_delta(reference_image,restored).changed_pixels==0,"RID-only test restores original rendered image exactly")
	apply_bindings(false);depth_controller.set_depth_enabled(true);controller.set_effect_flags(false,false)

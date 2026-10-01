extends "res://tools/verify_lake_reflection51b.gd"
## Runtime-only material bisection. Frozen51b remains untouched. Every trial starts
## from full canonical-identical original material copies and uses the same pose, uniforms and time.
var group_results := []
var reference_image: Image
var metadata_by_path := {}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
	call_deferred("run")
func diagnostic_pixel_delta(a: Image,b: Image) -> Dictionary:
	var aa := a.get_data();var bb := b.get_data()
	if a.get_size()!=b.get_size() or aa.size()!=bb.size(): return {"same_size":false,"changed_pixels":-1}
	if aa==bb: return {"same_size":true,"changed_pixels":0,"max_channel_delta":0,"points":[],"bounds":[]}
	var width := a.get_width();var count := 0;var maximum := 0
	var min_x := width;var max_x := -1;var min_y := a.get_height();var max_y := -1
	var points := []
	for index in range(0,aa.size(),4):
		var changed := false
		for channel in range(4):
			var delta := absi(int(aa[index+channel])-int(bb[index+channel]));maximum=maxi(maximum,delta);changed=changed or delta!=0
		if changed:
			var pixel := index/4;var x := pixel%width;var y := pixel/width
			count+=1;min_x=mini(min_x,x);max_x=maxi(max_x,x);min_y=mini(min_y,y);max_y=maxi(max_y,y)
			if points.size()<1000: points.append({"x":x,"y":y,"original":[aa[index],aa[index+1],aa[index+2],aa[index+3]],"trial":[bb[index],bb[index+1],bb[index+2],bb[index+3]]})
	return {"same_size":true,"changed_pixels":count,"max_channel_delta":maximum,"bounds":[min_x,min_y,max_x,max_y],"points":points,"points_truncated":count>1000}
func selected(row: Dictionary,kind: String,key: String) -> bool:
	if kind=="native":
		return row.original is StandardMaterial3D and (key.is_empty() or str(metadata_by_path[row.converted.resource_path].native_feature_sha256)==key)
	if kind=="custom":
		return row.original is ShaderMaterial and (key.is_empty() or row.original.shader.code.sha256_text()==key)
	return false
func apply_subset(kind: String,key := "") -> int:
	apply_copy_baseline()
	var count := 0
	for row in stored_rows:
		if selected(row,kind,key): game.get_node(row.path).set(row.property,row.converted);count+=1
	for row in live_rows.values():
		var node := game.get_node_or_null(row.path)
		if node!=null and selected(row,kind,key): node.set(row.property,row.converted);count+=1
	if kind=="ocean":
		game.get_node("World/Ocean").material_override=new_ocean;depth_controller.water=new_ocean;depth_controller.set_depth_enabled(false);count+=1
	if kind=="layers":
		game.camera.cull_mask=candidate_camera_mask;game.get_node("World/Ocean").layers=WATER_LAYER
	controller.set_effect_flags(false,false)
	return count
func trial(label: String,kind: String,key := "") -> Dictionary:
	var switched := apply_subset(kind,key)
	var image := await shot(label,"1344")
	var delta := diagnostic_pixel_delta(reference_image,image)
	var row := {"name":label,"kind":kind,"source_key":key,"switched_binding_assignments":switched,"pixel_delta":delta,"camera_mask":game.camera.cull_mask,"ocean_layers":game.get_node("World/Ocean").layers,"original_uniforms_fingerprint":digest(original_parameter_state())}
	group_results.append(row);print("GROUP_DELTA ",label," pixels=",delta.changed_pixels," max=",delta.get("max_channel_delta",0)," bounds=",delta.get("bounds",[]))
	return row
func same_rid_plain_control(kind: String,key: String) -> void:
	var guarded_image := Image.load_from_file(str(captures.back().path))
	guarded_image.convert(Image.FORMAT_RGBA8)
	var shaders := {}
	var proof := []
	for path in material_pairs:
		var pair: Dictionary=material_pairs[path]
		if not selected({"original":pair.original,"converted":pair.converted},kind,key):continue
		var shader: Shader=pair.converted.shader
		var plain: String
		if pair.original is StandardMaterial3D:
			var group: int=int(metadata_by_path[path].native_group)
			plain=FileAccess.get_file_as_string("/workspace/scratch/a29d03198654/Aether/source-assets/reflection50/official-native-conversions/native_group_%02d.gdshader"%group)
			check(plain.sha256_text()==metadata_by_path[path].old_shader_sha256,"Exact official pre-injection shader source "+path)
		else:
			plain=pair.original.shader.code
		var id: int=shader.get_instance_id()
		if not shaders.has(id):shaders[id]={"shader":shader,"guarded_code":shader.code,"plain_code":plain,"rid":str(shader.get_rid())}
		else:check(shaders[id].plain_code==plain,"Shared shader maps to one exact original source")
		proof.append({"material":path,"same_material_rid":str(pair.converted.get_rid()),"shader_rid":str(shader.get_rid()),"original_code_sha":plain.sha256_text(),"guarded_code_sha":shader.code.sha256_text()})
	for row in shaders.values():row.shader.code=row.plain_code
	var plain_image := await shot("same-rid-plain-"+kind+"-"+key.substr(0,12),"1344")
	var plain_delta := diagnostic_pixel_delta(reference_image,plain_image)
	var injection_delta := diagnostic_pixel_delta(plain_image,guarded_image)
	for row in shaders.values():
		row.shader.code=row.guarded_code
		check(str(row.shader.get_rid())==row.rid,"Original Shader RID retained across plain/guard code swap")
	var restored := await shot("same-rid-guard-restored-"+kind+"-"+key.substr(0,12),"1344")
	check(diagnostic_pixel_delta(guarded_image,restored).changed_pixels==0,"Same-RID guarded source image restores exactly")
	group_results.append({"name":"same-rid-plain-vs-guarded-"+kind+"-"+key.substr(0,12),"plain_vs_copy_baseline":plain_delta,"plain_vs_guarded":injection_delta,"proof":proof,"candidate_assets_saved":false})
	print("SAME_RID_PLAIN ",kind," ",key," plain_vs_copy=",plain_delta.changed_pixels," plain_vs_guard=",injection_delta.changed_pixels)
func observations() -> void:
	root.size=Vector2i(1180,664)
	root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	var before := collision_activity(game);freeze_tree(game);await physics_frame;await physics_frame
	check(before==collision_activity(game),"Bisection freeze preserves every live physics object")
	for row in build_report.material_ledger:metadata_by_path[row.new_material_path]=row
	if not await prepare_view("1344"): return
	if not prepare_copy_baseline(): return
	var initial := original_parameter_state()
	apply_copy_baseline()
	reference_image=await shot("01-C-all-identical-copies","1344")
	var ocean := await trial("02-Ocean-only","ocean")
	var native := await trial("03-native-only","native")
	var custom := await trial("04-custom-only","custom")
	apply_bindings(false)
	var full := await shot("05-B-all-converted","1344")
	var full_delta := diagnostic_pixel_delta(reference_image,full)
	group_results.append({"name":"05-B-all-converted","kind":"full","pixel_delta":full_delta})
	print("GROUP_DELTA full pixels=",full_delta.changed_pixels)
	apply_copy_baseline()
	var restored := await shot("06-C2-identical-copies-restored","1344")
	check(diagnostic_pixel_delta(reference_image,restored).changed_pixels==0,"Exact same-value copy C/C2 repeatability after first six controls")
	# Adaptive second stage: only subdivide a family that actually changes pixels.
	for family in [["native",native],["custom",custom]]:
		if int(family[1].pixel_delta.changed_pixels)<=0: continue
		var keys := {}
		for path in material_pairs:
			var pair: Dictionary=material_pairs[path]
			if family[0]=="native" and pair.original is StandardMaterial3D: keys[str(metadata_by_path[path].native_feature_sha256)]=true
			if family[0]=="custom" and pair.original is ShaderMaterial: keys[pair.original.shader.code.sha256_text()]=true
		var sorted := keys.keys();sorted.sort()
		for key in sorted:
			var guarded_row := await trial("adaptive-"+str(family[0])+"-"+str(key).substr(0,12),family[0],key)
			if int(guarded_row.pixel_delta.changed_pixels)>0:
				await same_rid_plain_control(family[0],key)
	if int(ocean.pixel_delta.changed_pixels)==0 and int(native.pixel_delta.changed_pixels)==0 and int(custom.pixel_delta.changed_pixels)==0 and int(full_delta.changed_pixels)>0:
		await trial("adaptive-camera-mask-and-water-layer-only","layers")
	apply_copy_baseline()
	var final_original := await shot("final-identical-copies-restored","1344")
	check(diagnostic_pixel_delta(reference_image,final_original).changed_pixels==0,"Final copy-baseline restoration remains exact")
	check(initial==original_parameter_state(),"All original uniforms/native albedos stayed fixed through bisection")
	apply_bindings(false);depth_controller.set_depth_enabled(true);controller.set_effect_flags(false,false)
func finish() -> void:
	var valid := failures.is_empty()
	for row in checks: valid=valid and row.passed
	var report := {"diagnostic_instrumentation_passed":valid,"candidate_sha256":candidate_sha,"source_scene_unchanged":FileAccess.get_sha256(B_TARGET)==candidate_sha,"purpose":"Only1344 copy-baseline family control plus same-RID exact official/plain versus guarded source and restoration for each nonzero family. All observed differences retained; no tolerance or saved asset edits.","groups":group_results,"checks":checks,"failures":failures,"captures":captures,"uniform_sync_ledger":uniform_sync_ledger,"copy_baseline_ledger":copy_ledger,"new_candidate_written":false,"mainpass_acceptance":false,"visual_acceptance":false,"total_acceptance_passed":false,"renderer":RenderingServer.get_video_adapter_name()}
	if not output.is_empty():
		var f:=FileAccess.open(output.path_join("group-report.json"),FileAccess.WRITE)
		if f!=null:f.store_string(JSON.stringify(report,"  "));f.close()
	if is_instance_valid(game):await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51B1344 BISECTION COMPLETE instrumentation=",valid," trials=",group_results.size());quit(0 if valid else 1)

extends "res://tools/verify_lake_reflection51.gd"
## Runtime-only material bisection. Frozen51 remains untouched. Every trial starts
## from full original ready bindings and uses the same pose, uniforms and time.
var group_results := []
var reference_image: Image
var metadata_by_path := {}
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="): output=arg.trim_prefix("--output-dir=")
	call_deferred("run")
func pixel_delta(a: Image,b: Image) -> Dictionary:
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
	apply_bindings(true)
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
	var image := await shot(label,"1128")
	var delta := pixel_delta(reference_image,image)
	var row := {"name":label,"kind":kind,"source_key":key,"switched_binding_assignments":switched,"pixel_delta":delta,"camera_mask":game.camera.cull_mask,"ocean_layers":game.get_node("World/Ocean").layers,"original_uniforms_fingerprint":digest(original_parameter_state())}
	group_results.append(row);print("GROUP_DELTA ",label," pixels=",delta.changed_pixels," max=",delta.get("max_channel_delta",0)," bounds=",delta.get("bounds",[]))
	return row
func observations() -> void:
	root.size=Vector2i(1180,664)
	root.add_child(game);game.sound_enabled=false;game.test_frozen=true;game.get_node("Weather42b").time_scale=0.0
	await frames(20);await RenderingServer.frame_post_draw
	controller=game.get_node(NEW_GROUP);depth_controller=game.get_node("World/LakeDepth50")
	var before := collision_activity(game);freeze_tree(game);await physics_frame;await physics_frame
	check(before==collision_activity(game),"Bisection freeze preserves every live physics object")
	for row in build_report.material_ledger:metadata_by_path[row.new_material_path]=row
	if not await prepare_view("1128"): return
	var initial := original_parameter_state()
	apply_bindings(true)
	reference_image=await shot("01-A-all-original","1128")
	var ocean := await trial("02-Ocean-only","ocean")
	var native := await trial("03-native-only","native")
	var custom := await trial("04-custom-only","custom")
	apply_bindings(false)
	var full := await shot("05-B-all-converted","1128")
	var full_delta := pixel_delta(reference_image,full)
	group_results.append({"name":"05-B-all-converted","kind":"full","pixel_delta":full_delta})
	print("GROUP_DELTA full pixels=",full_delta.changed_pixels)
	apply_bindings(true)
	var restored := await shot("06-A2-all-original-restored","1128")
	check(pixel_delta(reference_image,restored).changed_pixels==0,"Exact original A/A2 repeatability after first six controls")
	# Diagnostic only: uses_discard changes GLES3 shared-shadow optimization even
	# when its uniform is false. Separate shadow sensitivity without treating
	# disabled shadows as an acceptable production fix.
	var sun := game.get_node("Sun") as DirectionalLight3D
	var original_shadow := sun.shadow_enabled
	sun.shadow_enabled=false;apply_bindings(true)
	var shadow_a := await shot("shadow-disabled-A-original","1128")
	apply_bindings(false)
	var shadow_b := await shot("shadow-disabled-B-converted","1128")
	var shadow_delta := pixel_delta(shadow_a,shadow_b)
	group_results.append({"name":"shadow-disabled-original-vs-converted","kind":"shadow_diagnostic_only","original_sun_shadow_enabled":original_shadow,"pixel_delta":shadow_delta,"production_fix":false})
	print("GROUP_DELTA shadow-disabled pixels=",shadow_delta.changed_pixels," max=",shadow_delta.get("max_channel_delta",0))
	sun.shadow_enabled=original_shadow;apply_bindings(true)
	var shadow_restore := await shot("shadow-restored-original","1128")
	check(sun.shadow_enabled==original_shadow and pixel_delta(reference_image,shadow_restore).changed_pixels==0,"Original Sun.shadow_enabled and original image exactly restored")
	# Adaptive second stage: only subdivide a family that actually changes pixels.
	for family in [["native",native],["custom",custom]]:
		if int(family[1].pixel_delta.changed_pixels)<=0: continue
		var keys := {}
		for path in material_pairs:
			var pair: Dictionary=material_pairs[path]
			if family[0]=="native" and pair.original is StandardMaterial3D: keys[str(metadata_by_path[path].native_feature_sha256)]=true
			if family[0]=="custom" and pair.original is ShaderMaterial: keys[pair.original.shader.code.sha256_text()]=true
		var sorted := keys.keys();sorted.sort()
		for key in sorted: await trial("adaptive-"+str(family[0])+"-"+str(key).substr(0,12),family[0],key)
	if int(ocean.pixel_delta.changed_pixels)==0 and int(native.pixel_delta.changed_pixels)==0 and int(custom.pixel_delta.changed_pixels)==0 and int(full_delta.changed_pixels)>0:
		await trial("adaptive-camera-mask-and-water-layer-only","layers")
	apply_bindings(true)
	var final_original := await shot("final-original-restored","1128")
	check(pixel_delta(reference_image,final_original).changed_pixels==0,"Final original restoration remains exact")
	check(initial==original_parameter_state(),"All original uniforms/native albedos stayed fixed through bisection")
	apply_bindings(false);depth_controller.set_depth_enabled(true);controller.set_effect_flags(false,false)
func finish() -> void:
	var valid := failures.is_empty()
	for row in checks: valid=valid and row.passed
	var report := {"diagnostic_instrumentation_passed":valid,"candidate_sha256":candidate_sha,"source_scene_unchanged":FileAccess.get_sha256(TARGET)==candidate_sha,"purpose":"First six whole-world group controls, then only failing material-family feature/SHA subdivisions. Pixel differences are findings, never tolerance-accepted.","groups":group_results,"checks":checks,"failures":failures,"captures":captures,"uniform_sync_ledger":uniform_sync_ledger,"new_candidate_written":false,"mainpass_acceptance":false,"visual_acceptance":false,"total_acceptance_passed":false,"renderer":RenderingServer.get_video_adapter_name()}
	if not output.is_empty():
		var f:=FileAccess.open(output.path_join("group-report.json"),FileAccess.WRITE)
		if f!=null:f.store_string(JSON.stringify(report,"  "));f.close()
	if is_instance_valid(game):await settle();game.queue_free();game=null
	await frames(8)
	print("REFLECTION51 BISECTION COMPLETE instrumentation=",valid," trials=",group_results.size());quit(0 if valid else 1)

extends SceneTree
const SCENE := 'res://scenes/candidate42d/Game42d.tscn'
const MultiMeshCopy = preload('res://tools/multimesh_copy42d.gd')
var output := ''
var game: Node3D
var rows: Array = []
var checks: Array = []
func _initialize() -> void: call_deferred('run')
func check(ok: bool, label: String, evidence: Variant = null) -> void:
	checks.append({'passed':ok,'name':label,'evidence':evidence})
	print('PASS ' if ok else 'FAIL ',label)
func frames(count: int) -> void:
	for i in range(count): await process_frame
func capture(name: String) -> Image:
	await frames(3)
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	var path := output.path_join(name+'.png')
	check(image.save_png(path)==OK,'Saved actual rendered '+name)
	return image
func difference(a: Image,b: Image) -> Dictionary:
	var sum := 0.0
	var changed := 0
	for y in range(a.get_height()):
		for x in range(a.get_width()):
			var av := a.get_pixel(x,y)
			var bv := b.get_pixel(x,y)
			var d := absf(av.r-bv.r)+absf(av.g-bv.g)+absf(av.b-bv.b)
			sum += d
			if d > .03: changed += 1
	return {'rgb_absolute_sum':sum,'pixels_over_003':changed,'total_pixels':a.get_width()*a.get_height()}
func positions(multi: MultiMesh) -> Array:
	var result: Array = []
	for i in range(multi.instance_count): result.append(multi.get_instance_transform(i).origin)
	return result
func run() -> void:
	if DisplayServer.get_name()=='headless':
		push_error('Actual rendered smoke requires graphics');quit(2);return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with('--output-dir='): output=arg.trim_prefix('--output-dir=')
	assert(not output.is_empty() and not DirAccess.dir_exists_absolute(output),'Use a unique output directory')
	DirAccess.make_dir_recursive_absolute(output)
	game=load(SCENE).instantiate()
	# Serialized reload checks run before _ready alters precipitation positions.
	for name in ['Rain','Snow']:
		var actual: MultiMesh=game.get_node('Weather42b/'+name).multimesh
		var expected:=MultiMesh.new()
		expected.transform_format=MultiMesh.TRANSFORM_3D
		expected.use_custom_data=true
		expected.instance_count=1800 if name=='Rain' else 1200
		MultiMeshCopy.restore_weather_custom_data(expected)
		MultiMeshCopy.place_weather42c(expected)
		check(actual.buffer==expected.buffer,name+' serialized reload exactly matches all seeded transforms/custom data',{'floats':actual.buffer.size(),'instances':actual.instance_count})
	root.add_child(game)
	game.sound_enabled=false
	game.test_frozen=true
	await frames(3)
	var weather: Node3D=game.get_node('Weather42b')
	weather.time_scale=0.0
	for id in ['1341','1275','1276']:
		game.process_mode=Node.PROCESS_MODE_INHERIT
		game.observe_reference(id)
		weather.seek_time(0.0)
		await frames(3) # allow live weather anchor to settle at authored observation
		game.process_mode=Node.PROCESS_MODE_DISABLED
		var name: String='Rain' if id=='1341' else 'Snow'
		var node: MultiMeshInstance3D=weather.get_node(name)
		var before:=positions(node.multimesh)
		var image0: Image=await capture('reference-'+id+'-time-0')
		weather.seek_time(.35)
		var after:=positions(node.multimesh)
		var changed:=0
		for i in range(before.size()):
			if not before[i].is_equal_approx(after[i]): changed+=1
		check(changed==node.multimesh.visible_instance_count and changed>0,name+' all visible transforms advance '+id,{'changed':changed,'allocated':node.multimesh.instance_count,'visible':node.multimesh.visible_instance_count})
		var image1: Image=await capture('reference-'+id+'-time-035')
		var was_visible: bool=node.visible
		node.visible=false
		var off: Image=await capture('reference-'+id+'-precipitation-off')
		node.visible=was_visible
		var restored: Image=await capture('reference-'+id+'-precipitation-restored')
		rows.append({'reference':id,'particle':name,'changed_transforms':changed,'allocated':node.multimesh.instance_count,'visible_instances':node.multimesh.visible_instance_count,'camera_transform':str(game.camera.global_transform),'particle_anchor':str(node.global_position),'t0_to_t035':difference(image0,image1),'precipitation_on_off':difference(image1,off),'precipitation_restored_vs_off':difference(restored,off),'on_restored_control':difference(image1,restored),'scope':'Pixel differences are diagnostics; moving shader-time scenery may contribute. Review images for precipitation visibility and near-eye artifacts.'})
		print('SMOKE REFERENCE COMPLETE ',id)
	game.process_mode=Node.PROCESS_MODE_INHERIT
	weather.time_scale=1.0
	var passed:=true
	for item in checks: passed=passed and item.passed
	var report:={'checks_passed':passed,'checks':checks,'views':rows,'source_scene':SCENE,'source_sha256':FileAccess.get_sha256(SCENE),'renderer':RenderingServer.get_video_adapter_name(),'display_driver':DisplayServer.get_name(),'scope':'Quick actual rendered precipitation smoke, not full visual or hardware GPU acceptance'}
	var file:=FileAccess.open(output.path_join('report.json'),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,'  '));file.close()
	game.queue_free()
	game=null
	await frames(8)
	print('SMOKE42D COMPLETE ',passed)
	quit(0 if passed else 1)

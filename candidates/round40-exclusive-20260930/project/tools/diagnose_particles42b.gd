extends SceneTree
var game: Node3D
var output := 'E:/FeiTing/candidates/round40-exclusive-20260930/evidence/gpu-h-particle-diagnosis42b'
func _initialize() -> void:call_deferred('run')
func shot(name: String) -> void:
	for i in range(8):await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output.path_join(name+'.png'))
	print('DIAGNOSTIC IMAGE ',name)
func run() -> void:
	DirAccess.make_dir_recursive_absolute(output)
	game=load('res://scenes/candidate42b/Game42b.tscn').instantiate()
	root.add_child(game);game.test_frozen=true;game.sound_enabled=false
	for i in range(20):await process_frame
	var weather: Node3D=game.get_node('Weather42b');weather.time_scale=0
	for node in [weather.get_node('Rain'),weather.get_node('Snow')]:print('PARTICLE MESH ',node.name,' ',node.multimesh.mesh.get_aabb())
	game.observe_reference('1276');await shot('snow-on')
	weather.get_node('Snow').visible=false;await shot('snow-off')
	game.observe_reference('1341');await shot('rain-on')
	weather.get_node('Rain').visible=false;await shot('rain-off')
	game.observe_reference('1344');await shot('rainbow')
	game.queue_free();for i in range(4):await process_frame
	quit()

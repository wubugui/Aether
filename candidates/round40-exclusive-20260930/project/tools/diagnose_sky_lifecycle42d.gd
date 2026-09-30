extends SceneTree
const MultiMeshCopy = preload('res://tools/multimesh_copy42d.gd')
var failed := false
func _initialize() -> void: call_deferred('run')
func run() -> void:
	var mode := 'sky-immediate'
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with('--mode='): mode=arg.trim_prefix('--mode=')
	print('LIFECYCLE MODE ',mode)
	if mode=='reload-settled':
		var game: Node3D=ResourceLoader.load('res://scenes/candidate42d/Game42d.tscn','PackedScene',ResourceLoader.CACHE_MODE_IGNORE).instantiate()
		for name in ['Rain','Snow']:
			var actual: MultiMesh=game.get_node('Weather42b/'+name).multimesh
			var expected:=MultiMesh.new()
			expected.transform_format=MultiMesh.TRANSFORM_3D
			expected.use_custom_data=true
			expected.instance_count=1800 if name=='Rain' else 1200
			MultiMeshCopy.restore_weather_custom_data(expected)
			MultiMeshCopy.place_weather42c(expected)
			var equal: bool=actual.buffer==expected.buffer
			failed=failed or not equal
			print('RELOAD ',name,' all buffer floats match = ',equal,' count=',actual.instance_count,' floats=',actual.buffer.size())
		# Render-server dirty-sky initialization must complete before freeing.
		# Do not add to scene tree, run gameplay _ready, save, or change materials.
		for i in range(3): await process_frame
		await RenderingServer.frame_post_draw
		game.free()
	else:
		var sky:=Sky.new()
		var material:=ShaderMaterial.new()
		material.shader=load('res://scripts/environment39_sky.gdshader')
		sky.sky_material=material
		print('SKY radiance enum=',sky.radiance_size,' default256 RGBA8 mip-accounting bytes=349524')
		if mode=='sky-settled':
			for i in range(3): await process_frame
			await RenderingServer.frame_post_draw
		sky=null
		material=null
	call_deferred('finish')
func finish() -> void:
	for i in range(8): await process_frame
	print('LIFECYCLE COMPLETE')
	quit(1 if failed else 0)

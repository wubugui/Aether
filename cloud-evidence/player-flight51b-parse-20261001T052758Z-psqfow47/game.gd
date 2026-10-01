extends Node3D
## Physical airship, camera, docking, navigation and exploration game loop.
const HOME_SHIP := Vector3(-4.15,136.8,184)
const HOME_CAMERA := Vector3(0,145,250)
const SAVE_PATH := "user://skyfarer_progress.json"
var save_path := SAVE_PATH
@onready var world = $World
@onready var airship: CharacterBody3D = $Airship
@onready var visuals: Node3D = $Airship/Visuals
@onready var propeller: Node3D = $Airship/Visuals/Propeller
@onready var camera: Camera3D = $Camera
var hud: Control
var throttle := 0.0
var speed := 0.0
var heading := 0.0
var altitude := 136.8
var clearance := 136.8
var fuel := .60
var shield := .71
var health := .74
var navigation_open := false
var anchored := true
var docked := false
var dock_id := ""
var help_open := false
var map_open := false
var photo_mode := false
var wireframe := false
var cockpit := false
var orbit := Vector2.ZERO
var zoom := 1.0
var elapsed := 0.0
var travelled := 0.0
var completed: Dictionary = {}
var collected_rings: Dictionary = {}
var target_port := 1
var score := 0
var notice := ""
var notification_time := 0.0
var impact_timer := 0.0
var last_safe_port := 0
var vertical_speed := 0.0
var focus_timer := 0.0
var engine_player: AudioStreamPlayer
var engine_playback: AudioStreamGeneratorPlayback
var audio_phase := 0.0
var sound_enabled := true
var testing := false
var test_frozen := false
var test_input := Vector3.ZERO
var test_override_input := false
var test_runner: RefCounted
var boost_active := false
var screenshot_pending := false
var frame_times: Array[float] = []
var auto_pilot := false
var tour_waypoint := 0
var tour_visited := 0
const TOUR := [Vector3(100,210,-530),Vector3(430,440,-1610),Vector3(1110,700,-2910),Vector3(2060,730,-3510),Vector3(2300,570,-790),Vector3(1320,240,880),Vector3(72,170,105)]

func _ready() -> void:
	testing = "--game-test" in OS.get_cmdline_user_args() or "--tour-test" in OS.get_cmdline_user_args() or "--stream-test" in OS.get_cmdline_user_args() or "--cliff-tour-test" in OS.get_cmdline_user_args()
	var canvas := CanvasLayer.new()
	canvas.name = "Flight interface"
	add_child(canvas)
	hud = preload("res://scripts/game_hud.gd").new()
	hud.game = self
	canvas.add_child(hud)
	reset_flight()
	if not testing and not "--capture" in OS.get_cmdline_user_args():
		load_progress(false)
		setup_audio()
	toast("W / S 油门 · A / D 转向 · E / Q 升降 · Shift 加速 · F1 操作说明",13)
	if "--game-test" in OS.get_cmdline_user_args():
		test_runner=preload("res://scripts/game_tests.gd").new()
		test_runner.run(self)
	if "--tour-test" in OS.get_cmdline_user_args():
		testing=true
		auto_pilot=true
		Engine.time_scale=8
		test_runner=preload("res://scripts/flight_tour_test.gd").new()
		test_runner.run(self)
	if "--stream-test" in OS.get_cmdline_user_args():
		Engine.time_scale=4
		test_runner=preload("res://scripts/stream_flight_test.gd").new()
		test_runner.run(self)
	if "--cliff-tour-test" in OS.get_cmdline_user_args():
		test_runner=preload("res://scripts/cliff_tour_test.gd").new()
		test_runner.run(self)
	if "--capture" in OS.get_cmdline_user_args():
		photo_mode = true
		capture_scene()

func reset_flight() -> void:
	fuel=.60
	shield=1.0 if testing else .71
	health=1.0 if testing else .74
	auto_pilot=false
	airship.position = HOME_SHIP
	airship.velocity = Vector3.ZERO
	airship.rotation = Vector3(0,deg_to_rad(13),0)
	visuals.rotation = Vector3.ZERO
	heading = 0
	throttle = 0
	speed = 0
	vertical_speed = 0
	anchored = true
	docked = false
	orbit = Vector2.ZERO
	zoom = 1
	cockpit = false
	visuals.visible = true
	camera.position = HOME_CAMERA
	camera.rotation_degrees = Vector3(-3.5,0,0)
	altitude = airship.position.y
	clearance = altitude-world.ground_height(airship.position)
	world.update_focus(airship.position,true)

func _physics_process(delta: float) -> void:
	if photo_mode or test_frozen: return
	var turn := float(Input.is_physical_key_pressed(KEY_A))-float(Input.is_physical_key_pressed(KEY_D))
	var lift := float(Input.is_physical_key_pressed(KEY_E))-float(Input.is_physical_key_pressed(KEY_Q))
	var power := float(Input.is_physical_key_pressed(KEY_W))-float(Input.is_physical_key_pressed(KEY_S))
	if testing and test_override_input: turn=test_input.x; lift=test_input.y; power=test_input.z
	if auto_pilot:
		var destination:Vector3=TOUR[tour_waypoint]
		var difference:=destination-airship.position
		var wanted_heading:=atan2(difference.z,-difference.x)-deg_to_rad(13)
		turn=clampf(wrapf(wanted_heading-heading,-PI,PI)*2,-1,1)
		lift=clampf(difference.y*.025,-1,1)
		power=1
		if difference.length()<145:
			tour_waypoint=(tour_waypoint+1)%TOUR.size()
			tour_visited+=1
	boost_active = Input.is_physical_key_pressed(KEY_SHIFT) and fuel>0 and not anchored
	if power>0 or lift!=0 or turn!=0:
		if docked:
			docked=false
			airship.position.y+=1.0
			toast("已离港。祝航行顺利。")
		anchored=false
	throttle=clampf(throttle+power*delta*.34,0,1)
	heading+=turn*delta*(.52 if boost_active else .66)
	airship.rotation.y=heading+deg_to_rad(13)
	var wanted_vertical := lift*(75.0 if boost_active else 42.0)
	vertical_speed=move_toward(vertical_speed,0 if anchored else wanted_vertical,delta*26)
	var target_speed := throttle*(175.0 if boost_active else 88.0)
	if anchored or fuel<=0:target_speed=0
	var horizontal := Vector3(airship.velocity.x,0,airship.velocity.z)
	var direction := -airship.global_basis.x
	horizontal=horizontal.move_toward(direction*target_speed,delta*(26 if anchored else 17 if boost_active else 11))
	airship.velocity=horizontal+Vector3.UP*vertical_speed
	if docked:airship.velocity=Vector3.ZERO
	var before:=airship.position
	var impact_speed:=airship.velocity.length()
	airship.move_and_slide()
	travelled+=airship.position.distance_to(before)
	speed=Vector2(airship.velocity.x,airship.velocity.z).length()
	vertical_speed=airship.velocity.y
	impact_timer=maxf(0,impact_timer-delta)
	if airship.get_slide_collision_count()>0 and impact_timer<=0:
		var collision:=airship.get_slide_collision(0)
		var contact_speed:=absf(collision.get_normal().dot(horizontal+Vector3.UP*wanted_vertical))
		if contact_speed>9 and impact_speed>10:
			take_damage(clampf(contact_speed*.0025,.025,.32))
			impact_timer=1.2
			throttle*=.45
	if speed>1:fuel=maxf(0,fuel-delta*(.00009+throttle*.00016)*(2.5 if boost_active else 1.0))
	altitude=airship.position.y
	clearance=altitude-world.ground_height(airship.position)
	visuals.rotation.x=lerp_angle(visuals.rotation.x,-turn*.12,delta*3)
	visuals.rotation.z=lerp_angle(visuals.rotation.z,-vertical_speed*.002,delta*3)
	if not docked:visuals.position.y=sin(elapsed*.72)*.08
	check_rings()
	focus_timer+=delta
	if focus_timer>.2:
		world.update_focus(airship.position)
		focus_timer=0

func _process(delta: float) -> void:
	RenderingServer.global_shader_parameter_set("world_time",elapsed)
	frame_times.append(delta)
	if frame_times.size()>240:frame_times.pop_front()
	if not photo_mode:
		elapsed+=delta
		propeller.rotation.x+=delta*(2+speed*.8+throttle*12)
		notification_time=maxf(0,notification_time-delta)
	update_camera(delta)
	if photo_mode:
		altitude=airship.position.y
		clearance=altitude-world.ground_height(airship.position)
	if is_instance_valid(hud):hud.queue_redraw()
	fill_audio()

func update_camera(delta: float) -> void:
	var desired: Vector3
	var target: Vector3
	if cockpit:
		desired=airship.to_global(Vector3(-2.5,.3,0))
		var look_direction:Vector3=(-airship.global_basis.x).rotated(Vector3.UP,orbit.x)
		look_direction=look_direction.rotated(look_direction.cross(Vector3.UP).normalized(),orbit.y)
		target=desired+look_direction*80
	else:
		var relative: Vector3=(HOME_CAMERA-HOME_SHIP)*zoom
		relative=relative.rotated(Vector3.RIGHT,-orbit.y)
		relative=relative.rotated(Vector3.UP,heading+orbit.x)
		desired=airship.position+relative
		target=airship.position+Vector3(4.15,4.2,1.1).rotated(Vector3.UP,heading)
		var query:=PhysicsRayQueryParameters3D.create(target,desired,1,[airship.get_rid()])
		var hit:=get_world_3d().direct_space_state.intersect_ray(query)
		if not hit.is_empty():desired=hit.position+(target-hit.position).normalized()*2.2
	var next_position:=camera.position.lerp(desired,1-exp(-delta*9))
	# Orbit interpolation can cross a cliff even if both desired endpoints are
	# clear. Validate the actual smoothed camera position as well.
	if not cockpit:
		var query:=PhysicsRayQueryParameters3D.create(target,next_position,1,[airship.get_rid()])
		var hit:=get_world_3d().direct_space_state.intersect_ray(query)
		if not hit.is_empty():next_position=hit.position+(target-hit.position).normalized()*2.2
	camera.position=next_position
	if camera.position.distance_to(target)>.1:camera.look_at(target,Vector3.UP)
	visuals.visible=not cockpit

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode in [KEY_W,KEY_S,KEY_A,KEY_D,KEY_E,KEY_Q,KEY_SPACE]:auto_pilot=false
		match event.physical_keycode:
			KEY_SPACE:
				anchored=not anchored
				if anchored:throttle=0
				toast("制动悬停" if anchored else "继续航行")
			KEY_F:try_dock()
			KEY_R:reset_flight();toast("已返回出发空域")
			KEY_C:cockpit=not cockpit;orbit=Vector2.ZERO
			KEY_M:map_open=not map_open
			KEY_H:navigation_open=not navigation_open
			KEY_TAB:target_port=(target_port+1)%world.ports.size()
			KEY_F1:help_open=not help_open;map_open=false
			KEY_F2:photo_mode=not photo_mode
			KEY_F3:
				wireframe=not wireframe
				world.set_wireframe(wireframe)
			KEY_F4:
				auto_pilot=not auto_pilot
				toast("导览航线已开启，操作飞行键可随时接管" if auto_pilot else "已关闭自动导览",5)
			KEY_F5:save_progress();toast("航行进度已保存")
			KEY_F9:load_progress(true)
			KEY_N:sound_enabled=not sound_enabled
			KEY_F11:
				DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if DisplayServer.window_get_mode()==DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_FULLSCREEN)
			KEY_F12:save_screenshot()
			KEY_ESCAPE:help_open=false;map_open=false;orbit=Vector2.ZERO
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		orbit+=event.relative*Vector2(-.004,-.003)
		orbit.y=clampf(orbit.y,-1.05,1.05)
	if event is InputEventMouseButton and event.pressed:
		if event.button_index==MOUSE_BUTTON_WHEEL_UP:zoom=maxf(.3,zoom*.88)
		if event.button_index==MOUSE_BUTTON_WHEEL_DOWN:zoom=minf(3.5,zoom*1.12)

func activate_ability(index: int) -> void:
	match index:
		0:vertical_speed=25;anchored=false
		1:throttle=1.0;anchored=false
		2:try_dock()
		3:anchored=not anchored;throttle=0 if anchored else throttle

func nearest_port() -> int:
	var nearest:=0
	var distance:=INF
	for i in range(world.ports.size()):
		var p: Dictionary=world.ports[i]
		var d:=airship.position.distance_to(Vector3(p.x,p.pad_y+5,p.z))
		if d<distance:distance=d;nearest=i
	return nearest

func try_dock() -> bool:
	var index:=nearest_port()
	var port: Dictionary=world.ports[index]
	var center:=Vector3(port.x,port.pad_y+5,port.z)
	var horizontal:=Vector2(airship.position.x-center.x,airship.position.z-center.z).length()
	if horizontal>24 or absf(airship.position.y-center.y)>9:
		toast("请接近港口甲板并降低高度，再按 F 停靠补给")
		return false
	if speed>12:
		toast("速度过快，请按空格制动后停靠")
		return false
	airship.position=center
	airship.velocity=Vector3.ZERO
	vertical_speed=0
	throttle=0
	speed=0
	anchored=true
	docked=true
	dock_id=port.id
	fuel=1
	shield=1
	health=1
	last_safe_port=index
	if not completed.has(port.id):
		completed[port.id]=true
		score+=100
	if index==target_port:
		for i in range(1,world.ports.size()+1):
			var candidate: int=(index+i)%world.ports.size()
			if not completed.has(world.ports[candidate].id):target_port=candidate;break
	toast("停靠成功：燃料与船体已恢复。探索进度 %d / 6" % completed.size(),6)
	save_progress()
	return true

func check_rings() -> void:
	for i in range(world.rings.size()):
		if collected_rings.has(str(i)):continue
		var ring: Node3D=world.rings[i]
		if (airship.global_position+Vector3.UP*3).distance_to(ring.global_position)<8.0:
			collected_rings[str(i)]=true
			ring.visible=false
			score+=20
			fuel=minf(1,fuel+.04)
			toast("穿越航标 +20 · 燃料补充",3)

func take_damage(amount: float) -> void:
	var absorbed:=minf(shield,amount)
	shield-=absorbed
	health=maxf(0,health-(amount-absorbed))
	toast("发生碰撞，请减速并调整高度",3)
	if health<=0:
		var port: Dictionary=world.ports[last_safe_port]
		airship.position=Vector3(port.x,port.pad_y+16,port.z)
		airship.velocity=Vector3.ZERO
		throttle=0
		anchored=true
		health=.75
		shield=.5
		fuel=maxf(fuel,.3)
		world.update_focus(airship.position,true)
		toast("飞艇已由最近港口救援。可停靠维修。",7)

func toast(message: String,duration:=4.0) -> void:
	notice=message
	notification_time=duration

func save_progress() -> void:
	if testing or "--capture" in OS.get_cmdline_user_args():return
	var p:=airship.position
	var data: Dictionary={"version":1,"position":[p.x,p.y,p.z],"heading":heading,"fuel":fuel,"shield":shield,"health":health,"completed":completed,"rings":collected_rings,"score":score,"target":target_port,"safe_port":last_safe_port}
	var file:=FileAccess.open(save_path,FileAccess.WRITE)
	if file:file.store_string(JSON.stringify(data))

func load_progress(restore_position: bool) -> void:
	if not FileAccess.file_exists(save_path):return
	var data=JSON.parse_string(FileAccess.get_file_as_string(save_path))
	if not data is Dictionary or data.get("version",0)!=1:return
	completed=data.get("completed",{})
	collected_rings=data.get("rings",{})
	score=int(data.get("score",0))
	target_port=clampi(int(data.get("target",1)),0,world.ports.size()-1)
	last_safe_port=clampi(int(data.get("safe_port",0)),0,world.ports.size()-1)
	for i in range(world.rings.size()):world.rings[i].visible=not collected_rings.has(str(i))
	if restore_position:
		var p: Array=data.get("position",[HOME_SHIP.x,HOME_SHIP.y,HOME_SHIP.z])
		airship.position=Vector3(p[0],p[1],p[2])
		heading=float(data.get("heading",0))
		airship.rotation.y=heading+deg_to_rad(13)
		fuel=clampf(data.get("fuel",1),0,1)
		shield=clampf(data.get("shield",1),0,1)
		health=clampf(data.get("health",1),.1,1)
		airship.velocity=Vector3.ZERO
		throttle=0
		anchored=true
		world.update_focus(airship.position,true)
		camera.position=airship.position+(HOME_CAMERA-HOME_SHIP).rotated(Vector3.UP,heading)
		toast("已恢复保存的航行位置")

func setup_audio() -> void:
	var generator:=AudioStreamGenerator.new()
	generator.mix_rate=16000
	generator.buffer_length=.15
	engine_player=AudioStreamPlayer.new()
	engine_player.stream=generator
	engine_player.volume_db=-29
	add_child(engine_player)
	engine_player.play()
	engine_playback=engine_player.get_stream_playback()

func fill_audio() -> void:
	if not engine_playback:return
	var count:=engine_playback.get_frames_available()
	var frequency:=32+throttle*24+speed*.18
	for i in range(count):
		audio_phase=fmod(audio_phase+frequency/16000,1.0)
		var wave:=sin(audio_phase*TAU)*.55+sin(audio_phase*TAU*2)*.2+sin(audio_phase*TAU*4)*.08
		wave*=.25+throttle*.5
		engine_playback.push_frame(Vector2.ONE*wave if sound_enabled and not photo_mode else Vector2.ZERO)

func save_screenshot() -> void:
	if screenshot_pending:return
	screenshot_pending=true
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("user://screenshots"))
	var path: String="user://screenshots/game-"+Time.get_datetime_string_from_system().replace(":","-")+".png"
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(path))
	screenshot_pending=false
	toast("截图已保存到游戏用户数据目录的 screenshots 文件夹")

func capture_scene() -> void:
	var output:="res://captures/game-opening.png"
	var view:="opening"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
		if arg.begins_with("--view="):view=arg.trim_prefix("--view=")
	if view=="summit":
		airship.position=Vector3(1160,650,-3180)
		heading=2.6
		orbit=Vector2(.15,.3)
	elif view=="harbor":
		var p:Dictionary=world.ports[0]
		airship.position=Vector3(p.x+4,p.pad_y+10,p.z+35)
		zoom=.72
		orbit=Vector2(.55,.3)
	elif view=="reverse":orbit=Vector2(PI,.12)
	elif view=="village":
		airship.position=Vector3(1330,95,950)
		heading=.3
		orbit=Vector2(.6,.2)
	elif view=="remote":
		airship.position=Vector3(8000,600,1800)
		heading=1.8
		world.update_focus(airship.position,true)
	elif view=="wire":world.set_wireframe(true)
	elif view=="map":map_open=true
	airship.rotation.y=heading+deg_to_rad(13)
	world.update_focus(airship.position,true)
	camera.position=airship.position+(HOME_CAMERA-HOME_SHIP).rotated(Vector3.UP,heading+orbit.x)
	notification_time=0
	if view=="remote":
		# This inspection camera jumps into an unloaded area; allow the same
		# background loader used by normal flight to finish its visible region.
		var warmup_deadline:int=Time.get_ticks_msec()+30000
		while (not world.load_queue.is_empty() or world.generation_thread) and Time.get_ticks_msec()<warmup_deadline:
			await get_tree().process_frame
	for i in range(80):await get_tree().process_frame
	var inspection_views:={
		"cliff-back":[Vector3(380,190,-330),Vector3(170,40,-20)],
		"cliff-side":[Vector3(30,140,90),Vector3(185,50,-50)],
		"cliff-low":[Vector3(128,32,125),Vector3(140,30,-20)],
		"cliff-top":[Vector3(150,300,120),Vector3(160,40,-70)],
		"mountain-back":[Vector3(1950,760,-4250),Vector3(1150,150,-2500)],
		"mountain-side":[Vector3(250,460,-2370),Vector3(1260,160,-2490)]}
	if inspection_views.has(view):
		set_process(false);set_physics_process(false)
		camera.position=inspection_views[view][0];camera.look_at(inspection_views[view][1])
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output).get_base_dir())
	var result:=get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(output))
	if frame_times.size()>20:
		var sample:Array[float]=frame_times.slice(frame_times.size()/2)
		sample.sort()
		print("FRAME METRICS median_ms=",sample[sample.size()/2]*1000," p95_ms=",sample[mini(sample.size()-1,int(sample.size()*.95))]*1000)
	print("GAME CAPTURE ",view," ",output," status=",result," terrain=",world.chunks.size())
	get_tree().quit(result)

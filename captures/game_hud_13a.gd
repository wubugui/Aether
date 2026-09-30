extends "res://captures/hud_13a.gd"
## Reference-styled instruments, backed by actual flight and navigation data.
var ui_font: SystemFont
var map_texture: ImageTexture
var map_center := Vector2.ZERO
const NAMES := {"hearth":"炉风港","crown":"王冠城堡","summit":"霜峰观测站","mill":"琥珀风车镇","lantern":"灯塔海岸","ruins":"古老天门"}

func _ready() -> void:
	super._ready()
	ui_font=SystemFont.new()
	ui_font.font_names=PackedStringArray(["Microsoft YaHei UI","Microsoft YaHei","Arial"])
	tooltips=["Ascend · E","Full throttle · W","Dock / supply · F","Brake · Space"]

func text_at(point: Vector2,message: String,sz:=16,tint:=LIGHT) -> void:
	draw_string(ui_font,point+Vector2(1,1),message,HORIZONTAL_ALIGNMENT_LEFT,-1,sz,Color(0.10,.15,.14,.65))
	draw_string(ui_font,point,message,HORIZONTAL_ALIGNMENT_LEFT,-1,sz,tint)

func _draw() -> void:
	super._draw()
	if not ui_font:return
	if not game.navigation_open:
		if game.map_open:draw_map()
		return
	var rect:=Rect2(519,849,640,69)
	var style:=panel_style()
	style.bg_color=Color(.18,.24,.25,.78)
	draw_style_box(style,rect)
	text_at(Vector2(538,875),"航速 %03d km/h     海拔 %04d m     离地 %04d m" % [game.speed*3.6,game.altitude,game.clearance],17)
	var port:Dictionary=game.world.ports[game.target_port]
	var distance:float=game.airship.position.distance_to(Vector3(port.x,port.pad_y+5,port.z))
	var name:String=NAMES.get(port.id,port.name)
	text_at(Vector2(538,900),"%s  %s  ·  港口 %d / 6  ·  航标 %d / 12  ·  %d 分" % [name,"%.1f km" % (distance/1000) if distance>1000 else "%d m" % distance,game.completed.size(),game.collected_rings.size(),game.score],15)
	text_at(Vector2(538,937),"F1 帮助     M 地图     Tab 目的地     C 驾驶视角     F 停靠     F4 导览",13,Color("e0dfc8"))
	if game.notification_time>0:
		var width:=ui_font.get_string_size(game.notice,HORIZONTAL_ALIGNMENT_LEFT,-1,17).x+36
		draw_style_box(style,Rect2((1672-width)*.5,131,width,35))
		text_at(Vector2((1672-width)*.5+18,155),game.notice,17)
	draw_destination(port,name,distance)
	if game.docked:
		text_at(Vector2(718,817),"已停靠 · 按 W 或 E 再次起航",18)
	else:
		var near:Dictionary=game.world.ports[game.nearest_port()]
		var delta_xz:=Vector2(game.airship.position.x-near.x,game.airship.position.z-near.z)
		if delta_xz.length()<130:
			text_at(Vector2(535,817),"码头甲板 %d m · 减速并降低到 %d m，按 F 停靠" % [near.pad_y,near.pad_y+5],16)
	if game.map_open:draw_map()

func draw_destination(port:Dictionary,label:String,distance:float) -> void:
	var point:=Vector3(port.x,port.pad_y+22,port.z)
	if game.camera.is_position_behind(point) or distance<40:return
	var screen:Vector2=game.camera.unproject_position(point)/(get_viewport_rect().size/Vector2(1672,941))
	if not Rect2(130,245,1330,535).has_point(screen):return
	diamond(screen,Vector2(7,10),Color(.82,.73,.43,.85),LIGHT)
	text_at(screen+Vector2(14,5),label+"  %d m" % distance,14)

func build_map() -> void:
	map_center=Vector2(roundf(game.airship.position.x/2000)*2000,roundf(game.airship.position.z/2000)*2000)
	var img:=Image.create(160,160,false,Image.FORMAT_RGB8)
	for y in range(160):
		for x in range(160):
			var p:=map_center+(Vector2(x,y)/160-Vector2(.5,.5))*14000
			var h:float=game.world.geography.height_at(p.x,p.y)
			var c:=Color("3b7188")
			if h>0:c=Color("a5b780").darkened(clampf(h/1000,0,.25))
			if h>240:c=Color("a6b4b4")
			if h>320:c=Color("e6e9df")
			if h>0 and h<5:c=Color("d8cda4")
			img.set_pixel(x,y,c)
	map_texture=ImageTexture.create_from_image(img)

func map_point(x:float,z:float) -> Vector2:
	return Vector2(566,223)+(Vector2(x,z)-map_center)/14000*540+Vector2(270,270)

func draw_map() -> void:
	if not map_texture or map_center.distance_to(Vector2(game.airship.position.x,game.airship.position.z))>3000:build_map()
	draw_style_box(panel_style(),Rect2(534,166,604,663))
	text_at(Vector2(566,201),"航海图  /  世界地形与港口",22)
	draw_texture_rect(map_texture,Rect2(566,223,540,540),false)
	for i in range(game.world.ports.size()):
		var port:Dictionary=game.world.ports[i]
		var p:=map_point(port.x,port.z)
		if not Rect2(568,225,535,535).has_point(p):continue
		var tint:=Color("f6db94") if i==game.target_port else Color("e8e7cb")
		diamond(p,Vector2(5,7),tint,Color("48584b"))
		text_at(p+Vector2(9,4),NAMES.get(port.id,port.name),12,Color("273f3c"))
	var ship:=map_point(game.airship.position.x,game.airship.position.z)
	var angle:float=game.heading+deg_to_rad(13)
	var forward:=Vector2(-cos(angle),sin(angle))
	var right:=Vector2(-forward.y,forward.x)
	poly([ship+forward*11,ship-forward*7+right*6,ship-forward*4,ship-forward*7-right*6],Color("fff1be"),Color("4d625d"),1.5)
	text_at(Vector2(566,797),"Tab 切换目的地 · M 关闭 · 已飞行 %.1f km" % (game.travelled/1000),16)

func help_panel() -> void:
	if not ui_font:return
	draw_style_box(panel_style(),Rect2(526,200,620,592))
	text_at(Vector2(556,239),"AETHER  /  飞艇航行指南",25)
	text_at(Vector2(556,272),"自由探索山脉、岛屿与村庄，停靠六处港口。",17)
	var rows:=["W / S           增加 / 减少油门（松开后保持）","A / D           左转 / 右转","E / Q           上升 / 下降","Shift           按住加速，消耗更多燃料","空格            制动悬停 / 继续","右键拖动        360° 环绕；滚轮缩放","C               第三人称 / 驾驶视角","F               低速接近码头甲板后停靠、维修和补给","M / Tab         地图 / 切换目的地","R               救援回出发空域","F5 / F9         保存 / 恢复航行位置","F2 / F3 / F12   暂停画面 / 地形线框 / 截图","N / F11         声音开关 / 全屏"]
	for i in range(rows.size()):text_at(Vector2(556,312+i*31),rows[i],17,Color("dedbc3"))
	text_at(Vector2(556,764),"F1 关闭     当前 %d FPS" % Engine.get_frames_per_second(),15)

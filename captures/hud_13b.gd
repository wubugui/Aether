extends Control

var game: Node3D
const GOLD := Color("c2bba0")
const LIGHT := Color("d9cfb2")
const EDGE := Color("8e8c7b")
const INK := Color(0.24, 0.27, 0.26, 0.76)
var hover := -1
var buttons := [Vector2(104, 732), Vector2(72, 829), Vector2(172, 829), Vector2(1550, 811)]
var tooltips := ["Ascend · E", "Propeller · W / S", "Refuel", "Anchor · Space"]

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

func line(a: Vector2, b: Vector2, color: Color = GOLD, width: float = 1.5) -> void:
	draw_line(a,b,color,width*.68 if width<=2.5 else width,true)

func poly(points: Array, fill: Color, stroke: Color = Color.TRANSPARENT, width: float = 1.5) -> void:
	var p := PackedVector2Array()
	for v in points: p.append(v)
	draw_colored_polygon(p, fill)
	if stroke.a > 0:
		p.append(p[0])
		draw_polyline(p,stroke,width*.68,true)

func hexagon(center: Vector2, radius: float, fill: Color) -> void:
	var p := []
	for i in range(6): p.append(center + Vector2.from_angle(PI / 3 * i - PI / 2) * Vector2(radius * 1.045, radius * .975))
	poly(p, fill, GOLD, 2.5)
	p.clear()
	for i in range(6): p.append(center + Vector2.from_angle(PI / 3 * i - PI / 2) * Vector2((radius - 5) * 1.045, (radius - 5) * .975))
	poly(p, Color.TRANSPARENT, Color("a9a58f"), 1.0)
	line(center+Vector2(0,-radius-1),center+Vector2(0,-radius+5),LIGHT,2)
	line(center+Vector2(0,radius-5),center+Vector2(0,radius+2),EDGE,2)

func ring(center: Vector2, radius: float, color: Color, width: float = 1.5) -> void:
	draw_arc(center,radius,0,TAU,128,color,width*.75 if width<=3 else width,true)

func diamond(center: Vector2, radius: Vector2, fill: Color, stroke: Color = GOLD) -> void:
	poly([center+Vector2(0,-radius.y),center+Vector2(radius.x,0),center+Vector2(0,radius.y),center-Vector2(radius.x,0)],fill,stroke)

func _draw() -> void:
	var ratio := get_viewport_rect().size / Vector2(1672,941)
	draw_set_transform(Vector2.ZERO,0,ratio)
	status_bar(64,game.fuel,Color("cf7b2c"),0)
	status_bar(133,game.shield,Color("93ac88"),1)
	status_bar(202,game.health,Color("bf6461"),2)
	compass_line()
	compass()
	for i in range(3):
		hexagon(buttons[i],43,Color(.325,.369,.408,.96))
		ability_icon(buttons[i],i)
	wheel(buttons[3])
	if hover >= 0:
		var pos: Vector2 = buttons[hover] + Vector2(50,-13)
		if hover==3: pos=buttons[3]+Vector2(-191,-13)
		draw_style_box(panel_style(),Rect2(pos,Vector2(144,28)))
		draw_string(ThemeDB.fallback_font,pos+Vector2(10,19),tooltips[hover],HORIZONTAL_ALIGNMENT_LEFT,-1,14,LIGHT)
	if game.help_open: help_panel()

func status_bar(y: float, value: float, tint: Color, kind: int) -> void:
	var left := 86.0
	var center := Vector2(61,y)
	y-=kind
	poly([Vector2(left,y-7),Vector2(327,y-7),Vector2(337,y+4),Vector2(327,y+16),Vector2(left,y+16)],(Color(.342,.435,.478,.75) if kind==1 else Color(0.282,0.36,0.46,0.75)),GOLD,2)
	draw_rect(Rect2(left+4,y-5,237,3),Color("5d645f"))
	draw_rect(Rect2(left+4,y+12,237,3),Color("62665b"))
	var divisions:Array=([90,106,120,149,177,207,237,265,293,325] if kind==0 else [90,119,148,177,206,234,263,292,325] if kind==1 else [90,129,157,185,214,243,271,299,325])
	var fill_end:=minf(325,92+242*clampf(value,0,1))
	for i in range(divisions.size()-1):
		var x:float=divisions[i]+1
		var end:float=minf(divisions[i+1]-1,fill_end)
		if end>x:
			var col:=tint
			if kind==0 and i==0:col=Color("d4c2a0")
			elif kind==0 and i==5:col=Color("f5d58a")
			for row in range(16):
				var factor:float=.82 if row==0 or row==15 else 1.+sin(float(row)*.29)*.018
				draw_rect(Rect2(x,y-3+row,end-x,1),Color(col.r*factor,col.g*factor,col.b*factor))
		line(Vector2(divisions[i],y-3),Vector2(divisions[i],y+13),Color(.29,.32,.30,.72),1.3)
	line(Vector2(left+4,y-6),Vector2(326,y-6),Color("bbbcb0"),1)
	line(Vector2(left+4,y+15),Vector2(326,y+15),Color("d1d0ba"),1)
	var leather:=Color("564d41") if kind==0 else Color("50594f") if kind==1 else Color("5d5146")
	draw_circle(center,29.5,leather,true,-1,true)
	draw_arc(center,29.4,0,TAU,96,Color("aba58e"),1.0,true)
	draw_arc(center+Vector2(-.25,-.25),28.8,-2.65,-.55,44,Color("d0c7a9"),1.05,true)
	draw_arc(center,28.8,.55,2.65,44,Color("8b897b"),.8,true)
	poly([center+Vector2(-30,-14),center+Vector2(-27,-16),center+Vector2(-27,16),center+Vector2(-30,14)],Color("7c7e6f"),GOLD,.9)
	poly([center+Vector2(28,-16),center+Vector2(30,-13),center+Vector2(30,14),center+Vector2(28,16)],Color("7c7e6f"),GOLD,.9)
	line(center+Vector2(0,-34),center+Vector2(0,-29),Color("bab59b"),.9)
	line(center+Vector2(0,29),center+Vector2(0,34),Color("8e907f"),.9)
	match kind:
		0: flame(center)
		1:
			poly([center+Vector2(-13,-14),center+Vector2(0,-10),center+Vector2(13,-14),center+Vector2(12,4),center+Vector2(7,12),center+Vector2(0,17),center+Vector2(-8,11),center+Vector2(-13,3)],LIGHT,Color("e6dbbb"),1)
			poly([center+Vector2(1,-10),center+Vector2(12,-13),center+Vector2(11,4),center+Vector2(6,12),center+Vector2(1,16)],Color("c6bfa2"))
		2:
			var pts := []
			for i in range(48):
				var t := TAU*i/48.0
				pts.append(center+Vector2(16*pow(sin(t),3),-(13*cos(t)-5*cos(2*t)-2*cos(3*t)-cos(4*t)))*1.05)
			poly(pts,Color("bd6561"),Color("d29380"),1.2)

func flame(c: Vector2) -> void:
	curved_shape(c,[[Vector2(2,-19),Vector2(-8,-13),Vector2(-7,-7),Vector2(-8,-2)],[Vector2(-8,-2),Vector2(-18,9),Vector2(-9,19),Vector2(0,19)],[Vector2(0,19),Vector2(15,19),Vector2(16,6),Vector2(8,-2)],[Vector2(8,-2),Vector2(3,-6),Vector2(0,-13),Vector2(2,-19)]],Color("e9b86a"))
	curved_shape(c,[[Vector2(0,-1),Vector2(5,6),Vector2(-7,8),Vector2(0,17)],[Vector2(0,17),Vector2(9,12),Vector2(7,5),Vector2(0,-1)]],Color("766146"))

func curved_shape(c:Vector2,segments:Array,fill:Color,angle:=0.0) -> void:
	var points:Array=[]
	for segment in segments:
		for i in range(12):
			var t:=float(i)/12;var s:=1-t
			var p:Vector2=segment[0]*s*s*s+segment[1]*3*s*s*t+segment[2]*3*s*t*t+segment[3]*t*t*t
			points.append(c+p.rotated(angle))
	poly(points,fill)

func compass_line() -> void:
	line(Vector2(559,71),Vector2(1113,71),Color("8f9589"),4)
	line(Vector2(559,73),Vector2(1113,73),LIGHT,1.6)
	poly([Vector2(553,72),Vector2(565,61),Vector2(565,84)],Color("a2b4b3"),GOLD,2)
	poly([Vector2(1120,72),Vector2(1107,61),Vector2(1107,84)],Color("a2b4b3"),GOLD,2)
	for i in range(-8,9):
		if i==0: continue
		var x := 834.0 + i*19.5
		line(Vector2(x,67),Vector2(x,78),Color("b3b49e"),1.2)
		line(Vector2(x+1,68),Vector2(x+1,75),Color("e0d4b4"),1)
	diamond(Vector2(834,72),Vector2(10,12),Color("9badac"),GOLD)
	diamond(Vector2(834,72),Vector2(5,7),Color("a3c2ca"),LIGHT)
	poly([Vector2(821,112),Vector2(834,98),Vector2(847,112)],Color("c7c5af"),Color("9ea79c"),1.4)
	poly([Vector2(826,109),Vector2(834,101),Vector2(842,109)],LIGHT)

func compass() -> void:
	var c := Vector2(1555,125)
	draw_circle(c,89,Color("747b78"),true,-1,true)
	ring(c,88,Color("c4c3b5"),2)
	ring(c,84,Color("676e6c"),7)
	ring(c,79,Color("b5b9ad"),1.6)
	for r in range(75,0,-4):
		draw_circle(c,r,Color("7395b1").lerp(Color("7d9bb6"),1-float(r)/75),true,-1,true)
	draw_arc(c,87,-2.7,-.7,60,Color("ced0c0"),1,true)
	ring(c,73,Color(.70,.77,.74,.55),1.0)
	ring(c,85,Color(.83,.79,.67,.55),.8)
	for i in range(8):
		var t := i*TAU/8
		var dir := Vector2.from_angle(t)
		line(c+dir*80,c+dir*91,GOLD,2.0)
		if i%2==0:
			var side := Vector2(-dir.y,dir.x)
			poly([c+dir*95,c+dir*84+side*5,c+dir*80,c+dir*84-side*5],Color("c8c3a9"),Color("9caa9f"),1)
	for i in range(4):
		var d := Vector2.from_angle(i*PI/2)
		line(c+d*61,c+d*71,Color("becbbf"),1)
	diamond(c+Vector2(0,-94),Vector2(8,10),Color.TRANSPARENT,GOLD)
	var a: float = -game.heading
	var pts := [Vector2(0,-22),Vector2(-13,10),Vector2(-1,7),Vector2(14,17)]
	var transformed := []
	for p in pts: transformed.append(c+p.rotated(a))
	poly(transformed,Color("d9ceaa"),Color("8f9688"),1.5)
	poly([c+Vector2(0,-19).rotated(a),c+Vector2(0,5).rotated(a),c+Vector2(11,13).rotated(a)],Color("b4ad91"))
	line(c+Vector2(0,-19).rotated(a),c+Vector2(-10,9).rotated(a),Color("f0dfb6"),1.1)

func ability_icon(c: Vector2, index: int) -> void:
	match index:
		0:
			draw_circle(c+Vector2(-12,5),10,Color("d7c8ad"),true,-1,true)
			draw_circle(c+Vector2(1,-2),12,Color("d7c8ad"),true,-1,true)
			draw_circle(c+Vector2(15,6),9,Color("d7c8ad"),true,-1,true)
			draw_rect(Rect2(c+Vector2(-12,4),Vector2(28,10)),Color("d7c8ad"))
			line(c+Vector2(-18,14),c+Vector2(19,14),Color("a9a18a"),1)
		1:
			for i in range(3):
				var theta := i*TAU/3
				curved_shape(c,[[Vector2(-2,0),Vector2(-3,-6),Vector2(-11,-15),Vector2(-6,-20)],[Vector2(-6,-20),Vector2(0,-28),Vector2(9,-16),Vector2(2,-7)],[Vector2(2,-7),Vector2(0,-4),Vector2(1,-1),Vector2(-2,0)]],Color("d7c8ad"),theta)
			draw_circle(c,4.5,Color("b6ac8c"),true,-1,true)
			ring(c,3,Color("d7c8ad"),1.3)
		2:
			poly([c+Vector2(0,-20),c+Vector2(-12,2),c+Vector2(-13,10),c+Vector2(-9,17),c+Vector2(-2,20),c+Vector2(5,19),c+Vector2(11,14),c+Vector2(13,6)],Color("d7c8ad"),Color("e5d7b0"),1)
			draw_arc(c+Vector2(1,7),8,0.12,2.95,20,Color("a49c83"),2.6,true)

func wheel(c: Vector2) -> void:
	draw_circle(c,77,Color(0.319,0.277,0.237,0.92),true,-1,true)
	ring(c,76,Color("c3b99b"),2)
	ring(c,72,Color("817968"),1.2)
	ring(c,66,Color("c3b89a"),1.8)
	ring(c,30,LIGHT,6)
	ring(c,10,LIGHT,4)
	for i in range(8):
		var a: float = TAU*i/8+game.heading
		var d := Vector2.from_angle(a)
		line(c+d*11,c+d*44,LIGHT,4)
		draw_circle(c+d*44,3.1,LIGHT,true,-1,true)
		line(c+d*34,c+d*41,Color("d3c6a0"),6)
	for i in range(4):
		var d := Vector2.from_angle(i*PI/2)
		line(c+d*64,c+d*69,Color("8e8874"),2)
	if hover==3: ring(c,79,Color(0.9,0.85,0.68,0.5),1)

func panel_style() -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = Color(0.19,0.23,0.23,0.95)
	s.border_color = GOLD
	s.set_border_width_all(1)
	s.set_corner_radius_all(4)
	return s

func help_panel() -> void:
	var r := Rect2(570,248,540,427)
	draw_style_box(panel_style(),r)
	var font := ThemeDB.fallback_font
	draw_string(font,Vector2(604,291),"A E T H E R  /  FLIGHT CONTROLS",HORIZONTAL_ALIGNMENT_LEFT,-1,21,LIGHT)
	var mode_text := "Blender models / real-time 3D"
	draw_string(font,Vector2(604,320),mode_text,HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("a8b4aa"))
	line(Vector2(604,336),Vector2(1076,336),EDGE,1)
	var rows := ["W / S                 Increase / decrease throttle", "A / D                  Turn left / right", "E / Q                  Ascend / descend", "Right mouse        Orbit the 3D scene", "Space                  Anchor / resume", "R                         Restore reference framing", "F3                       Inspect mesh wireframe", "F2 / F12              Freeze frame / save screenshot", "F11                      Full screen"]
	for i in range(rows.size()):draw_string(font,Vector2(604,366+i*28),rows[i],HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("d0ccb4"))
	draw_string(font,Vector2(604,653),"F1 to close",HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("a8b4aa"))

func _input(event: InputEvent) -> void:
	if event is InputEventMouse:
		var p: Vector2 = event.position / (get_viewport_rect().size / Vector2(1672,941))
		hover = -1
		for i in range(4):
			if p.distance_to(buttons[i]) < (77 if i==3 else 39): hover=i
		if event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_LEFT and hover>=0:
			game.activate_ability(hover)
			get_viewport().set_input_as_handled()

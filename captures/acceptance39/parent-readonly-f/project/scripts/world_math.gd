@tool
extends RefCounted
## World-space terrain generation. Same equations and triangles as Blender.
const CHUNK := 768.0
const CELLS := 32
const STEP := 24.0
var peaks: Array = []
var river: Array = []
var rivers: Array = []
var coast_points: Array = []
var coast_survey_bounds:Array=[]
var ports: Array = []
var river_polygons: Array[PackedVector2Array] = []
var water_regions:Array=[]
var sculpt_regions:Array=[]
var has_mountain_kit:=false

func configure(data: Dictionary) -> void:
	peaks = data.peaks
	river = data.river
	rivers = data.rivers
	coast_points = data.coast
	coast_survey_bounds=data.get("coast_survey_bounds",[-1e9,-1e9])
	ports = data.ports
	water_regions.clear()
	has_mountain_kit=FileAccess.file_exists("res://assets/mountain_kit.json")
	sculpt_regions=JSON.parse_string(FileAccess.get_file_as_string("res://assets/terrain_sculpt.json")) if FileAccess.file_exists("res://assets/terrain_sculpt.json") else []
	var source:Array=JSON.parse_string(FileAccess.get_file_as_string("res://assets/water_geography.json")) if FileAccess.file_exists("res://assets/water_geography.json") else []
	for region in source:
		var rings:Array[PackedVector2Array]=[]
		var low:=Vector2(INF,INF);var high:=Vector2(-INF,-INF)
		for ring in [region.outer]+region.holes:
			var points:=PackedVector2Array()
			for p in ring:
				var v:=Vector2(p[0],p[1]);points.append(v);low=low.min(v);high=high.max(v)
			rings.append(points)
		water_regions.append({"rings":rings,"bounds":Rect2(low-Vector2.ONE*151,high-low+Vector2.ONE*302)})
	river_polygons.clear()
	for channel in rivers:
		var polygon:=PackedVector2Array()
		for p in channel.banks[0]:polygon.append(Vector2(p[0],p[1]))
		for i in range(channel.banks[1].size()-1,-1,-1):
			var p:Array=channel.banks[1][i]
			polygon.append(Vector2(p[0],p[1]))
		river_polygons.append(polygon)

func noise_at(x: float, z: float) -> float:
	return sin(x*.007+z*.004)*cos(z*.009-x*.003)*.5+sin(x*.021+z*.017)*.25+cos(x*.053-z*.041)*.15+sin(z*.13+x*.11)*.07

func raw_height(x: float, z: float) -> float:
	var n := noise_at(x,z)
	var h := 15+n*5+sin(x*.0031-z*.0023)*5+sin(x*.0009+z*.0015)*7
	h+=pow(maxf(0,noise_at(x*.43+871,z*.43-319)),2)*92
	for peak_index in range(peaks.size()):
		var p:Array=peaks[peak_index]
		var peak_height:float=15+(p[2]-15)*.42 if peak_index>=16 and peak_index<=21 else p[2]
		if peak_index<10 and has_mountain_kit:peak_height=15+(p[2]-15)*.45
		if peak_index in [11,12]:peak_height=15+(p[2]-15)*.30
		var dx: float = (x-p[0])/p[3]
		var dz: float = (z-p[1])/p[3]
		var dist := sqrt(dx*dx+dz*dz)
		if dist > 1.43: continue
		var angle := atan2(dz,dx)
		var profile := pow(clampf((1-dist*(1+sin(angle*5+p[0])*p[5]+sin(angle*9)*p[5]*.4))/(1-p[4]),0,1),1.28)
		var mass:float=15+(peak_height-15)*profile
		mass+=(sin(x*.07+z*.037)*2+sin(x*.13-z*.09))*profile*(1-profile)*minf(peak_height/100,2)
		h=maxf(h,mass)
	h=sculpt_height(x,z,h)
	var far_factor := smoothstep(4800,6600,maxf(absf(x),absf(z+1500)))
	var remote := pow(maxf(0,sin(x*.00063+sin(z*.00039)*1.7)*cos(z*.00051)),3)*510
	h = maxf(h,remote*far_factor)
	var coast:float=coast_points[0][1] if z<coast_points[0][0] else coast_points[-1][1]
	for i in range(coast_points.size()-1):
		if z>=coast_points[i][0] and z<=coast_points[i+1][0]:
			coast=lerpf(coast_points[i][1],coast_points[i+1][1],(z-coast_points[i][0])/(coast_points[i+1][0]-coast_points[i][0]))
			break
	var waves:float=1-smoothstep(coast_survey_bounds[0]-40,coast_survey_bounds[0],z)*(1-smoothstep(coast_survey_bounds[1],coast_survey_bounds[1]+40,z))
	coast += (sin(z*.09)*2+sin(z*.17)*1.5)*waves
	var shore_distance:=absf(x-coast)
	for i in range(coast_points.size()-1):
		var a:=Vector2(coast_points[i][1],coast_points[i][0]);var b:=Vector2(coast_points[i+1][1],coast_points[i+1][0])
		if x<minf(a.x,b.x)-151 or x>maxf(a.x,b.x)+151 or z<minf(a.y,b.y)-151 or z>maxf(a.y,b.y)+151:continue
		var point:=Vector2(x,z);var t:=clampf((point-a).dot(b-a)/maxf((b-a).length_squared(),1e-9),0,1)
		shore_distance=minf(shore_distance,point.distance_to(a+(b-a)*t))
	h=minf(h,-shore_distance*.72) if x<coast else lerpf(minf(h,shore_distance*.30),minf(h,shore_distance*.52),smoothstep(22,60,shore_distance))
	var island := maxf(0,1-Vector2((x+2850)/600,(z+120)/470).length())*155
	island = maxf(island,maxf(0,1-Vector2((x+1950)/430,(z-1270)/350).length())*115)
	h = maxf(h,island-8)
	var islet_peak:Array=peaks[22]
	var islet_delta:=Vector2((x-islet_peak[0])/37,(z-islet_peak[1])/29)
	var islet:float=-8+(islet_peak[2]+8)*clampf((1-islet_delta.length()*(1+.10*sin(islet_delta.angle()*5)))/.70,0,1)
	h=maxf(h,islet)
	for river_index in range(river_polygons.size()):
		if river_index==0 and not water_regions.is_empty():continue
		var polygon:PackedVector2Array=river_polygons[river_index]
		var bank:=1e9
		for i in range(polygon.size()):
			var a:Vector2=polygon[i]
			var b:Vector2=polygon[(i+1)%polygon.size()]
			var point:=Vector2(x,z)
			var t:=clampf((point-a).dot(b-a)/(b-a).length_squared(),0,1)
			bank=minf(bank,point.distance_to(a+(b-a)*t))
		if Geometry2D.is_point_in_polygon(Vector2(x,z),polygon):bank=-bank
		h=minf(h,bank*.72) if bank<0 else h*smoothstep(0,14,bank)
	var point:=Vector2(x,z)
	for region in water_regions:
		if not region.bounds.has_point(point):continue
		var distance:=INF;var inside_water:=false
		for ring_index in range(region.rings.size()):
			var polygon:PackedVector2Array=region.rings[ring_index]
			var inside:=Geometry2D.is_point_in_polygon(point,polygon)
			if ring_index==0:inside_water=inside
			else:inside_water=inside_water and not inside
			for i in range(polygon.size()):
				var a:Vector2=polygon[i];var b:Vector2=polygon[(i+1)%polygon.size()]
				var t:=clampf((point-a).dot(b-a)/maxf((b-a).length_squared(),1e-10),0,1)
				distance=minf(distance,point.distance_to(a+(b-a)*t))
		h=minf(h,-distance*.72) if inside_water else lerpf(minf(h,distance*.38),h,smoothstep(100,150,distance))
	return maxf(h,-95)

func sculpt_height(x:float,z:float,h:float) -> float:
	for sculpt in sculpt_regions:
		var bounds:Array=sculpt.bounds
		var margin:float=minf(minf(x-bounds[0],bounds[2]-x),minf(z-bounds[1],bounds[3]-z))
		var blend:=smoothstep(0,60 if "foothills" in sculpt.name else 140,margin)
		if blend<=0:continue
		for triangle in sculpt.triangles:
			var a:Array=sculpt.points[triangle[0]];var b:Array=sculpt.points[triangle[1]];var c:Array=sculpt.points[triangle[2]]
			var den:float=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
			var wa:float=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
			var wb:float=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den
			var wc:float=1-wa-wb
			if minf(wa,minf(wb,wc))>=-.0000001:
				h=lerpf(h,wa*a[1]+wb*b[1]+wc*c[1]+noise_at(x*1.3,z*1.3)*.85,blend)
				break
	return h

func height_at(x: float,z: float) -> float:
	var h := raw_height(x,z)
	for port in ports:
		var d := Vector2(x-port.x,z-port.z).length()
		if d < port.outer_radius:
			var blend := 1-smoothstep(port.inner_radius,port.outer_radius,d)
			h = lerpf(h,port.ground,blend)
	return h

func vertex_xz(ix:float,iz:float) -> Vector2:
	var jx:=fposmod(sin(ix*127.1+iz*311.7)*43758.5453,1)*2-1
	var jz:=fposmod(sin(ix*269.5+iz*183.3)*43758.5453,1)*2-1
	if fposmod(ix,CELLS)==0 or fposmod(iz,CELLS)==0:
		jx=0;jz=0
	return Vector2(ix*STEP+jx*7.5,iz*STEP+jz*7.5)

func surface_height(x: float,z: float) -> float:
	var ix := floori(x/STEP)
	var iz := floori(z/STEP)
	for dz in [0,-1,1]:
		for dx in [0,-1,1]:
			var gx:int=ix+dx
			var gz:int=iz+dz
			var corners:=[vertex_xz(gx,gz),vertex_xz(gx+1,gz),vertex_xz(gx,gz+1),vertex_xz(gx+1,gz+1)]
			var triangles:=[[0,2,3],[0,3,1]] if posmod(gx+gz,2)==0 else [[0,2,1],[1,2,3]]
			for triangle in triangles:
				var a:Vector2=corners[triangle[0]]
				var b:Vector2=corners[triangle[1]]
				var c:Vector2=corners[triangle[2]]
				var den:float=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
				var wa:float=((b.y-c.y)*(x-c.x)+(c.x-b.x)*(z-c.y))/den
				var wb:float=((c.y-a.y)*(x-c.x)+(a.x-c.x)*(z-c.y))/den
				var wc:float=1-wa-wb
				if minf(wa,minf(wb,wc))>=-.00001:
					return height_at(a.x,a.y)*wa+height_at(b.x,b.y)*wb+height_at(c.x,c.y)*wc
	return height_at(x,z)

func terrain_color(point: Vector3,normal: Vector3) -> Color:
	var palette := [Color("b1af83"),Color("bab789"),Color("c2bc8e"),Color("c9c18f")]
	var variation := fposmod(sin(point.x*12.9898+point.z*78.233)*43758.5453,1)
	var patch:=clampf(.5+noise_at(point.x*.14,point.z*.14)*.52+(variation-.5)*.08,0,.999)
	var c: Color = palette[int(patch*4)]
	if point.y<3.2: c=Color("c4c3ad")
	elif point.y<7: c=Color("c0c28d")
	var rock:=normal.y<.78 and point.y>35
	if rock:c=Color("aaa99e")
	var alpine:=(point.y>120 and point.z<-1500) or (point.y>52 and point.x>300 and point.x<1900 and point.z>-3500 and point.z< -980)
	if alpine:c=Color("91a3bb")
	var snowline:=210+38*sin(point.x*.009)+28*sin(point.z*.014)
	if alpine and point.y>snowline and normal.y>.40:c=Color("eeefec")
	var sunlight:=maxf(0,normal.dot(Vector3(-.48,.82,.30)))
	if alpine:
		var shade:=Vector3(.67,.74,.85).lerp(Vector3(1.02,1.01,1),sunlight)
		c*=Color(shade.x,shade.y,shade.z)
	elif rock:c*=.61+.49*sunlight
	else:c*=.80+.24*sunlight
	var biome:=smoothstep(-150,-50,point.x)*(1-smoothstep(260,350,point.x))*smoothstep(-220,-100,point.z)*(1-smoothstep(140,240,point.z))*smoothstep(10,25,point.y)
	if biome>0 and not rock:
		var upland:=[Color("899871"),Color("9eaa78"),Color("91a177"),Color("a6b080")]
		c=c.lerp(upland[int(patch*4)]*(.50+.62*sunlight),biome)
	c *= .99+variation*.02
	c.a = 1
	return c.srgb_to_linear()

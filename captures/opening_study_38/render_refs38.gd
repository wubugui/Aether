extends SceneTree
# 38 reference rig: renders every reference view of the one candidate world in a
# single Godot process. Each plan entry = camera (agl or absolute y) + env preset.
# Args: --output-dir=<dir> --plan=<json> [--game=res://...] [--only=1128,1342]
var output: String
var plan_path: String
var game_path: String = "res://captures/candidate_opening38/Game38.tscn"
var only: PackedStringArray = []
var materials: Array = []
var uniform_cache: Dictionary = {}  # Shader -> PackedStringArray of uniform names

func _initialize()->void: call_deferred("run")
func xyz(v:Vector3)->Array:return [v.x,v.y,v.z]
func v3(a,d:Vector3)->Vector3:
	if a is Array and a.size()>=3:return Vector3(a[0],a[1],a[2])
	return d
func col(a,d:Color)->Color:
	if a is Array and a.size()>=3:return Color(a[0],a[1],a[2])
	return d

func add_material(m:Material)->void:
	if m==null:return
	if m is ShaderMaterial and not materials.has(m):
		materials.append(m)
		var s:Shader=m.shader
		if s!=null and not uniform_cache.has(s):
			var names:=PackedStringArray()
			for u in s.get_shader_uniform_list():names.append(u["name"])
			uniform_cache[s]=names
	if m.next_pass!=null:add_material(m.next_pass)

func collect(n:Node)->void:
	if n is GeometryInstance3D:
		add_material(n.material_override)
		var mesh:Mesh=null
		if n is MeshInstance3D:
			mesh=n.mesh
			for i in range(n.get_surface_override_material_count()):add_material(n.get_surface_override_material(i))
		elif n is MultiMeshInstance3D and n.multimesh!=null:
			mesh=n.multimesh.mesh
		if mesh!=null:
			for i in range(mesh.get_surface_count()):add_material(mesh.surface_get_material(i))
	for c in n.get_children():collect(c)

# Shaders without study_fill (castle/world_surface, clouds, props) get a rig-only
# rig_fill uniform injected at the end of fragment() so night/storm presets dim them.
func inject_rig_fill()->int:
	var done:=0
	for s in uniform_cache.keys():
		var names:PackedStringArray=uniform_cache[s]
		if names.has("study_fill") or names.has("rig_fill"):continue
		var code:String=s.code
		if not code.contains("shader_type spatial"):continue
		var f:=code.find("void fragment()")
		if f<0:continue
		var open:=code.find("{",f)
		var depth:=0;var close:=-1
		for i in range(open,code.length()):
			var ch:=code[i]
			if ch=="{":depth+=1
			elif ch=="}":
				depth-=1
				if depth==0:close=i;break
		if close<0:continue
		var tail:="\n\tEMISSION*=rig_fill;ALBEDO*=mix(vec3(1.),rig_fill,.5);\n"
		if code.contains("unshaded"):tail="\n\tALBEDO*=clamp(rig_fill*1.8,vec3(0.),vec3(1.));\n"
		code=code.substr(0,close)+tail+code.substr(close)
		code=code.replace("shader_type spatial;","shader_type spatial;\nuniform vec3 rig_fill=vec3(1.);")
		s.code=code
		names.append("rig_fill");uniform_cache[s]=names;done+=1
	return done

# ---- 38 sky region: Blender-hub sky kit (cabins, floating islands, cloud sea) placed
# high above the south-east of the same world. Built at runtime from the GLBs.
const SKY_KIT:="E:/FeiTing/blender/sky_kit_38/hub_output_v2/"
const SKY_ORIGIN:=Vector3(3200,0,3000)
var cloud_mats:Array=[]
var airship_mats:Array=[]
func glb(name:String)->Node3D:
	var doc:=GLTFDocument.new();var state:=GLTFState.new()
	assert(doc.append_from_file(SKY_KIT+name+".glb",state)==OK)
	var n:Node3D=doc.generate_scene(state);n.name=name;return n
func omni(parent:Node3D,pos:Vector3,color:Color,energy:float,range_m:float)->void:
	var l:=OmniLight3D.new();l.position=pos;l.light_color=color;l.light_energy=energy;l.omni_range=range_m
	l.shadow_enabled=false;parent.add_child(l)
func build_sky_region(world:Node3D)->Dictionary:
	var sky:=Node3D.new();sky.name="SkyRegion38";world.add_child(sky)
	var tile:Node3D=glb("cloud_sea_tile")
	for mi in tile.find_children("*","MeshInstance3D",true,false):
		for si in range(mi.mesh.get_surface_count()):
			var sm:Material=mi.mesh.surface_get_material(si)
			if sm is BaseMaterial3D and not cloud_mats.has(sm):cloud_mats.append(sm)
	for i in range(-2,3):
		for j in range(-2,3):
			var t:Node3D=tile.duplicate() if not (i==-2 and j==-2) else tile
			t.position=SKY_ORIGIN+Vector3(i*1150,700,j*1150);t.rotation.y=(i*3+j)*1.1
			sky.add_child(t)
	var islands:=[["floating_island_3",Vector3(-420,905,-120),0.0],["floating_island_1",Vector3(-260,960,160),1.2],
		["floating_island_2",Vector3(-170,1010,-40),2.3],["floating_island_1",Vector3(-700,1030,-420),0.6],
		["floating_island_2",Vector3(-520,1120,260),4.0],["floating_island_3",Vector3(-1100,880,300),2.9],
		["floating_island_2",Vector3(260,980,-300),1.7],["floating_island_1",Vector3(420,900,-120),5.1],
		["floating_island_3",Vector3(-300,860,-700),3.3]]
	for d in islands:
		var isl:Node3D=glb(d[0]);isl.position=SKY_ORIGIN+d[1];isl.rotation.y=d[2];sky.add_child(isl)
	var cab_a:Node3D=glb("cabin_a");cab_a.position=SKY_ORIGIN+Vector3(0,930,0);sky.add_child(cab_a)
	omni(cab_a,Vector3(-0.9,2.05,-0.2),Color(1,.68,.34),3.2,7.0)
	omni(cab_a,Vector3(1.2,0.6,-0.9),Color(1,.5,.18),3.0,4.5)
	var cab_b:Node3D=glb("cabin_b");cab_b.position=SKY_ORIGIN+Vector3(150,960,700);cab_b.rotation.y=PI;sky.add_child(cab_b)
	omni(cab_b,Vector3(-0.9,1.9,-1.9),Color(1,.66,.32),2.6,5.0)
	omni(cab_b,Vector3(2.4,1.1,1.0),Color(1,.66,.32),2.8,5.0)
	omni(cab_b,Vector3(-2.4,0.6,0.3),Color(1,.5,.18),3.2,4.5)
	# lightning bolts under the cloud deck (for the night thunderstorm view)
	var bolt_mat:=StandardMaterial3D.new();bolt_mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	bolt_mat.albedo_color=Color(.92,.82,1.0)
	var bolts:=Node3D.new();bolts.name="Lightning";sky.add_child(bolts)
	var starts:=[Vector3(300,790,300),Vector3(750,785,120),Vector3(1150,790,-250),Vector3(550,788,-650),Vector3(1500,785,-500),Vector3(950,790,650),Vector3(100,786,-200)]
	for s in starts:
		var p:Vector3=SKY_ORIGIN+s
		for k in range(5):
			var q:=p+Vector3(sin(k*2.3+s.x)*30,-30,cos(k*1.7+s.z)*30)
			var seg:=MeshInstance3D.new();var bm:=BoxMesh.new();bm.size=Vector3(7.0,7.0,p.distance_to(q));seg.mesh=bm
			seg.material_override=bolt_mat;bolts.add_child(seg);seg.look_at_from_position((p+q)/2,q,Vector3.RIGHT)
			p=q
		omni(bolts,SKY_ORIGIN+s+Vector3(0,-70,0),Color(.72,.5,1.0),22.0,520.0)
	bolts.visible=false
	return {"sky":sky,"bolts":bolts,"lights":[]}

# ---- 38 weather effects shared by many references (rain, snow, rainbow, extra bolts)
var fx_root:Node3D
func fx_particles(kind:String,density:float,pos:Vector3,wind:Vector3)->void:
	var p:=CPUParticles3D.new();fx_root.add_child(p)
	var q:=QuadMesh.new();var m:=StandardMaterial3D.new()
	m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.billboard_mode=BaseMaterial3D.BILLBOARD_FIXED_Y if kind=="rain" else BaseMaterial3D.BILLBOARD_ENABLED
	if kind=="rain":
		q.size=Vector2(0.05,2.6);m.albedo_color=Color(.78,.82,.9,.32)
		p.amount=int(4000*density);p.gravity=Vector3(wind.x,-60,wind.z);p.initial_velocity_min=25;p.initial_velocity_max=35
		p.emission_box_extents=Vector3(45,30,45)
	else:
		q.size=Vector2(0.3,0.3);m.albedo_color=Color(.95,.97,1.0,.85)
		p.amount=int(6000*density);p.gravity=Vector3(wind.x,-2.5,wind.z);p.initial_velocity_min=1;p.initial_velocity_max=3
		p.emission_box_extents=Vector3(28,18,28)
	q.material=m;p.mesh=q;p.direction=Vector3(0,-1,0);p.spread=8
	p.emission_shape=CPUParticles3D.EMISSION_SHAPE_BOX;p.lifetime=3.0 if kind=="rain" else 9.0
	p.preprocess=p.lifetime;p.local_coords=false;p.global_position=pos+Vector3(0,12,0);p.emitting=true
func fx_rainbow(center:Vector3,radius:float,look_from:Vector3)->void:
	var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var bands:=[Color(.9,.25,.2),Color(.95,.6,.2),Color(.95,.9,.3),Color(.35,.8,.35),Color(.3,.5,.95),Color(.55,.3,.8)]
	var w:=radius*0.012;var n:=48
	for b in range(bands.size()):
		var r0:=radius-b*w;var r1:=r0-w
		for i in range(n):
			var a0:=PI*i/n;var a1:=PI*(i+1)/n
			var c:Color=bands[b];c.a=.30
			var v:=[Vector3(cos(a0)*r0,sin(a0)*r0,0),Vector3(cos(a1)*r0,sin(a1)*r0,0),Vector3(cos(a1)*r1,sin(a1)*r1,0),Vector3(cos(a0)*r1,sin(a0)*r1,0)]
			for idx in [0,1,2,0,2,3]:st.set_color(c);st.add_vertex(v[idx])
	var mi:=MeshInstance3D.new();mi.mesh=st.commit()
	var m:=StandardMaterial3D.new();m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;m.vertex_color_use_as_albedo=true
	m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;m.cull_mode=BaseMaterial3D.CULL_DISABLED
	mi.material_override=m;fx_root.add_child(mi);mi.global_position=center
	var flat:=Vector3(look_from.x,center.y,look_from.z);mi.look_at(flat,Vector3.UP);mi.rotate_object_local(Vector3.UP,PI)
func fx_bolts(points:Array)->void:
	var bm:=StandardMaterial3D.new();bm.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;bm.albedo_color=Color(.95,.9,1.0)
	for s in points:
		var p:=Vector3(s[0],s[1],s[2]);var h:float=s[3] if s.size()>3 else 400.0
		var steps:=6
		for k in range(steps):
			var q:=p+Vector3(sin(k*2.1+p.x)*h*.08,-h/steps,cos(k*1.3+p.z)*h*.08)
			var seg:=MeshInstance3D.new();var b:=BoxMesh.new();b.size=Vector3(h*.012,h*.012,p.distance_to(q));seg.mesh=b
			seg.material_override=bm;fx_root.add_child(seg);seg.look_at_from_position((p+q)/2,q,Vector3.RIGHT);p=q
		var l:=OmniLight3D.new();l.light_color=Color(.8,.75,1.0);l.light_energy=8.0;l.omni_range=h*1.5;fx_root.add_child(l)
		l.global_position=Vector3(s[0],s[1]-h*.5,s[2])
func apply_fx(e:Dictionary,cam:Vector3,env:Environment)->void:
	if fx_root!=null:fx_root.free()
	fx_root=Node3D.new();fx_root.name="Fx38";root.add_child(fx_root)
	var wind:=v3(e.get("wind"),Vector3(4,0,1))
	if float(e.get("rain",0.0))>0.0:fx_particles("rain",float(e["rain"]),cam,wind)
	if float(e.get("snow",0.0))>0.0:fx_particles("snow",float(e["snow"]),cam,wind)
	if e.has("rainbow"):
		var r:Array=e["rainbow"];fx_rainbow(Vector3(r[0],r[1],r[2]),float(r[3]) if r.size()>3 else 600.0,cam)
	if e.has("bolts"):fx_bolts(e["bolts"])
	env.fog_height=float(e.get("fog_height",0.0));env.fog_height_density=float(e.get("fog_height_density",0.0))

func inject_haze_rate()->int:
	var done:=0
	for sh in uniform_cache.keys():
		var code:String=sh.code
		if not code.contains("*.00070))*low_air"):continue
		code=code.replace("*.00070))*low_air","*rig_haze_rate))*low_air")
		code=code.replace("shader_type spatial;","shader_type spatial;
uniform float rig_haze_rate=.0007;")
		sh.code=code
		var names:PackedStringArray=uniform_cache[sh];names.append("rig_haze_rate");uniform_cache[sh]=names;done+=1
	return done
func add_props(list:Array,world:Node3D)->void:
	for pr in list:
		var inst:Node3D=load(String(pr[0])).instantiate();fx_root.add_child(inst)
		var gx:float=pr[1];var gz:float=pr[2]
		var gy:float=max(world.ground_height(Vector3(gx,0,gz)),0.0)+float(pr[3])
		inst.global_position=Vector3(gx,gy,gz);inst.rotation.y=float(pr[4]) if pr.size()>4 else 0.0
		if pr.size()>5:inst.scale=Vector3.ONE*float(pr[5])

func inject_glint()->int:
	var done:=0
	for sh in uniform_cache.keys():
		var code:String=sh.code
		if not code.contains("normalize(vec3(.97,.11,-.20))*13000."):continue
		code=code.replace("normalize(vec3(.97,.11,-.20))*13000.","normalize(rig_sun_dir)*13000.")
		code=code.replace("+vec3(.55,.52,.45)*sun_reflection","+rig_glint*sun_reflection")
		code=code.replace("shader_type spatial;","shader_type spatial;
uniform vec3 rig_sun_dir=vec3(.97,.11,-.20);
uniform vec3 rig_glint=vec3(.55,.52,.45);")
		sh.code=code
		var names:PackedStringArray=uniform_cache[sh];names.append("rig_sun_dir");names.append("rig_glint");uniform_cache[sh]=names;done+=1
	return done
func add_lights(list:Array,world:Node3D)->void:
	var glow:=StandardMaterial3D.new();glow.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;glow.albedo_color=Color(1,.78,.42)
	for L in list:
		var gy:float=max(world.ground_height(Vector3(L[0],0,L[1])),0.0)+float(L[2]) if L.size()<7 else float(L[6])
		var pos:=Vector3(L[0],gy,L[1])
		var o:=OmniLight3D.new();o.light_color=Color(1,.7,.35);o.light_energy=float(L[3]);o.omni_range=float(L[4]);fx_root.add_child(o);o.global_position=pos
		var b:=MeshInstance3D.new();var sm:=SphereMesh.new();sm.radius=float(L[5]);sm.height=float(L[5])*2;sm.radial_segments=6;sm.rings=3;b.mesh=sm
		b.material_override=glow;fx_root.add_child(b);b.global_position=pos
func add_beam(bm:Array)->void:
	var cone:=CylinderMesh.new();cone.top_radius=1.2;cone.bottom_radius=float(bm[4]) if bm.size()>4 else 45.0;cone.height=float(bm[3]) if bm.size()>3 else 420.0
	var m:=StandardMaterial3D.new();m.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED;m.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color=Color(1,.92,.7,.22);m.blend_mode=BaseMaterial3D.BLEND_MODE_ADD;m.cull_mode=BaseMaterial3D.CULL_DISABLED
	var mi:=MeshInstance3D.new();mi.mesh=cone;mi.material_override=m;fx_root.add_child(mi)
	var origin:=Vector3(bm[0],bm[1],bm[2]);var dir:=v3(bm[5] if bm.size()>5 else null,Vector3(1,0,0)).normalized()
	mi.global_position=origin+dir*cone.height*0.5
	mi.global_transform.basis=Basis(Quaternion(Vector3.UP,-dir))
	var o:=OmniLight3D.new();o.light_color=Color(1,.85,.55);o.light_energy=6.0;o.omni_range=40.0;fx_root.add_child(o);o.global_position=origin

func set_all(pname:String,value)->int:
	var n:=0
	for m in materials:
		if m.shader!=null and uniform_cache.get(m.shader,PackedStringArray()).has(pname):
			m.set_shader_parameter(pname,value);n+=1
	return n

func run()->void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--output-dir="):output=a.trim_prefix("--output-dir=")
		if a.begins_with("--plan="):plan_path=a.trim_prefix("--plan=")
		if a.begins_with("--game="):game_path=a.trim_prefix("--game=")
		if a.begins_with("--only="):only=a.trim_prefix("--only=").split(",")
	DirAccess.make_dir_recursive_absolute(output)
	var plan:Array=JSON.parse_string(FileAccess.get_file_as_string(plan_path))
	var t0:=Time.get_ticks_msec()
	var game:Node3D=load(game_path).instantiate()
	game.set_script(load("res://scripts/game.gd"))
	game.save_path="user://refrig38_unused.json"
	root.add_child(game)
	game.set_process(false);game.set_physics_process(false);game.sound_enabled=false
	game.airship.hide();game.hud.hide()
	var world:Node3D=game.get_node("World")
	world.set_process(false)
	var sun:DirectionalLight3D=game.get_node("Sun")
	# deterministic environment owned by the rig
	var sky_mat:=ShaderMaterial.new();sky_mat.shader=load("res://captures/opening_study_38/rig_sky38.gdshader")
	var sky:=Sky.new();sky.sky_material=sky_mat
	var env:=Environment.new()
	env.background_mode=Environment.BG_SKY;env.sky=sky
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.tonemap_mode=Environment.TONE_MAPPER_LINEAR
	env.fog_enabled=true;env.fog_sky_affect=0.0
	game.get_node("Environment").environment=env
	var sky_region:=build_sky_region(world)
	var storm_w:RefCounted=null
	var need_storm:=false
	for pp in plan:
		if pp.has("storm35") and (only.is_empty() or only.has(str(pp["ref"]))):need_storm=true
	if need_storm:
		var folder:="res://captures/validation_runs/highcoast-36b-20260909T015215Z-0c71bb650bcf43d890987772791f1dff/study-inputs/storm35c"
		storm_w=load(folder.path_join("storm_front_35c.gd")).new();storm_w.configure(game,folder)
		print("storm35 configured")
	var key_light:=OmniLight3D.new();key_light.light_color=Color(.85,.9,1.0);key_light.visible=false;root.add_child(key_light)
	var rows:Array=[]
	var collected:=false
	for p in plan:
		var ref:String=str(p["ref"])
		if not only.is_empty() and not only.has(ref):continue
		var c:Dictionary=p["camera"];var e:Dictionary=p["env"]
		var cx:float=c["x"];var cz:float=c["z"];var tx:float=c["tx"];var tz:float=c["tz"]
		var cy:float;var ty:float
		if c.has("y_abs") and c["y_abs"]!=null:cy=c["y_abs"]
		else:cy=max(world.ground_height(Vector3(cx,0,cz)),0.0)+float(c.get("agl",60.0))
		if c.has("ty_abs") and c["ty_abs"]!=null:ty=c["ty_abs"]
		else:ty=max(world.ground_height(Vector3(tx,0,tz)),0.0)+float(c.get("target_agl",0.0))
		var pos:=Vector3(cx,cy,cz);var tgt:=Vector3(tx,ty,tz)
		world.update_focus(pos,true)
		for i in range(4):await process_frame
		# ground height is only valid once the focus streamed in; recompute
		if not (c.has("y_abs") and c["y_abs"]!=null):pos.y=max(world.ground_height(Vector3(cx,0,cz)),0.0)+float(c.get("agl",60.0))
		if not (c.has("ty_abs") and c["ty_abs"]!=null):tgt.y=max(world.ground_height(Vector3(tx,0,tz)),0.0)+float(c.get("target_agl",0.0))
		if not collected:
			collect(game);add_material(sky_mat);collected=true
			print("rig_fill injected into ",inject_rig_fill()," shaders")
			print("haze rate injected into ",inject_haze_rate()," shaders")
			print("glint injected into ",inject_glint()," shaders")
			var before:=materials.duplicate();materials.clear();collect(game.airship);airship_mats=materials.duplicate()
			materials=before
			for m in airship_mats:
				if not materials.has(m):materials.append(m)
		game.camera.position=pos;game.camera.look_at(tgt);game.camera.fov=float(c.get("fov",55.0))
		game.camera.far=max(game.camera.far,20000.0)
		# environment preset
		var sd:=v3(e.get("sun_dir"),Vector3(-.48,.82,.30)).normalized()
		var up:=Vector3.UP if abs(sd.y)<.98 else Vector3.FORWARD
		sun.global_transform=Transform3D(Basis.looking_at(-sd,up),Vector3.ZERO)
		sun.light_color=col(e.get("sun_color"),Color(1,.97,.89));sun.light_energy=float(e.get("sun_energy",.85))
		sky_mat.set_shader_parameter("zenith",v3(e.get("sky_zenith"),Vector3(.44,.63,.837)))
		sky_mat.set_shader_parameter("horizon",v3(e.get("sky_horizon"),Vector3(.815,.905,.94)))
		sky_mat.set_shader_parameter("glow",v3(e.get("sky_glow"),Vector3(.13,.12,.07)))
		sky_mat.set_shader_parameter("sun_dir",sd)
		sky_mat.set_shader_parameter("disc",float(e.get("disc",0.0)))
		sky_mat.set_shader_parameter("stars",float(e.get("stars",0.0)))
		env.ambient_light_color=col(e.get("ambient_color"),Color(.84,.91,1));env.ambient_light_energy=float(e.get("ambient_energy",.6))
		env.fog_light_color=col(e.get("fog_color"),Color(.76,.85,.89));env.fog_density=float(e.get("fog_density",.00028))
		var n_fill:=set_all("study_fill",v3(e.get("study_fill"),Vector3.ONE))
		var n_haze:=set_all("study_haze",v3(e.get("study_haze"),Vector3(.7,.78,.82)))
		var n_night:=set_all("study_night",float(e.get("water_night",0.0)))
		set_all("rig_fill",v3(e.get("study_fill"),Vector3.ONE))
		sky_region["bolts"].visible=float(e.get("lightning",0.0))>0.5
		apply_fx(e,pos,env)
		set_all("rig_haze_rate",float(e.get("haze_rate",.0007)))
		if p.has("props"):add_props(p["props"],world)
		set_all("rig_sun_dir",sd);set_all("rig_glint",v3(e.get("glint"),Vector3(.55,.52,.45)))
		if p.has("lights"):add_lights(p["lights"],world)
		if p.has("beam"):add_beam(p["beam"])
		if storm_w!=null:
			storm_w.root_node.visible=p.has("storm35")
			if p.has("storm35"):storm_w.sample(game.camera,float(p["storm35"]))
		var sf:Vector3=v3(p["airship"].get("fill"),Vector3.ONE) if p.has("airship") else Vector3.ONE
		for m in airship_mats:
			var un:PackedStringArray=uniform_cache.get(m.shader,PackedStringArray()) if m.shader!=null else PackedStringArray()
			if un.has("rig_fill"):m.set_shader_parameter("rig_fill",sf)
			if un.has("study_fill"):m.set_shader_parameter("study_fill",sf)
		for cm in cloud_mats:cm.albedo_color=col(e.get("cloud_tint"),Color(1,1,1))
		if p.has("airship"):
			var a:Dictionary=p["airship"]
			game.airship.show();game.airship.set_physics_process(false)
			var ap:=pos+(tgt-pos).normalized()*float(a.get("dist",40.0))
			var right:=(tgt-pos).cross(Vector3.UP).normalized()
			ap+=right*float(a.get("right",0.0))+Vector3.UP*float(a.get("up",0.0))
			if a.has("pos"):ap=Vector3(a["pos"][0],a["pos"][1],a["pos"][2])
			game.airship.global_position=ap;game.airship.rotation=Vector3(0,float(a.get("yaw",0.0)),0)
			if float(a.get("key_light",0.0))>0.0:
				key_light.visible=true;key_light.global_position=pos+(ap-pos)*0.5+Vector3.UP*6
				key_light.light_energy=float(a["key_light"]);key_light.omni_range=pos.distance_to(ap)*1.6
			else:
				key_light.visible=false
		else:
			game.airship.hide();key_light.visible=false
		for i in range(16):await process_frame
		await RenderingServer.frame_post_draw
		var path:String=output.path_join("ref_%s.png"%ref)
		assert(root.get_texture().get_image().save_png(path)==OK)
		rows.append({"ref":ref,"image":path,"position":xyz(pos),"target":xyz(tgt),"fov":game.camera.fov,"ground_at_camera":world.ground_height(Vector3(cx,0,cz)),"params_set":{"study_fill":n_fill,"study_haze":n_haze,"study_night":n_night}})
		print("rendered ",ref," ",pos," -> ",tgt)
	var report:={"source_game":game_path,"plan":plan_path,"materials":materials.size(),"total_ms":Time.get_ticks_msec()-t0,"rows":rows,"scope":"Reference rig snapshots of the candidate world; env built by rig; no project file modified."}
	var f:=FileAccess.open(output.path_join("rig-report.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"  "));f.close()
	game.queue_free();await process_frame;await process_frame;quit()

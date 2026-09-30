@tool
extends Node3D
## Runtime for the native Godot World.tscn assembly. Placement comes from saved
## engine instances; Blender imports supply individual asset geometry only.
const Geography = preload("res://scripts/world_math.gd")
const WORLD_MATERIAL = preload("res://materials/world.tres")
const CHUNK := 768.0
var geography = Geography.new()
var layout: Dictionary
var ports: Array = []
var chunks: Dictionary = {}
var core: Dictionary = {}
var terrain_bodies: Dictionary = {}
var prop_buckets: Dictionary = {}
var prop_colliders: Dictionary = {}
var model_meshes: Dictionary = {}
var landmarks: Array[Node3D] = []
var rotors: Array[Node3D] = []
var rings: Array[Node3D] = []
var ocean: MeshInstance3D
var focus := Vector3.ZERO
var load_queue: Array[Vector2i] = []
var last_cell := Vector2i(99999,99999)
var collision_clock := 0.0
var wire_lines: Array[MeshInstance3D] = []
var inspection := false
var generated_chunks := 0
var free_prop_indices: Array[int] = []
var generation_thread: Thread
var pending_cell := Vector2i.ZERO
var terrain_samples: Dictionary = {}
var prop_transforms: Dictionary = {}

func _ready() -> void:
	if Engine.is_editor_hint():return
	layout = JSON.parse_string(FileAccess.get_file_as_string("res://assets/world_layout.json"))
	# Engine scene markers, not an external layout, own live docking positions.
	ports.clear()
	for marker in $Ports.get_children():ports.append(marker.definition())
	layout.ports=ports
	geography.configure(layout)
	for item in JSON.parse_string(FileAccess.get_file_as_string("res://assets/asset_catalog.json")):
		var scene: Node = load("res://scenes/prefabs/"+item.name+".tscn").instantiate()
		var mesh_node := first_mesh(scene)
		model_meshes[item.name] = mesh_node.mesh
		scene.free()
	for tile in $Terrain.get_children():
		var node:=first_mesh(tile)
		# The native prefab and its AssetInstance already own the material.
		# Runtime bookkeeping must preserve editor-authored terrain materials.
		node.visibility_range_end = 15000
		var cell:=cell_at(tile.global_position+Vector3(.01,0,.01))
		chunks[cell]=node;core[cell]=true
		terrain_bodies[cell]=tile.get_node("Collision")
	for node in $Settlements.get_children():
		if node.asset_kind=="mill_rotor":rotors.append(node)
		else:landmarks.append(node)
	for node in $FlightRings.get_children():rings.append(node)
	rings.sort_custom(func(a,b):return int(a.get_meta("ring_index",0))<int(b.get_meta("ring_index",0)))
	# MultiMesh resources are saved by the editor. Read their actual transforms
	# so moving a grove or editing an instance also moves its collision.
	layout.props=[]
	for grove in $Vegetation.get_children():
		var kind:String=grove.get_meta("asset_kind")
		for i in range(grove.multimesh.instance_count):
			var transform:Transform3D=grove.global_transform*grove.multimesh.get_instance_transform(i)
			var p:=transform.origin
			var entry:=[kind,p.x,p.y,p.z,transform.basis.get_scale().x,transform.basis.get_euler().y,true]
			var index:int=layout.props.size();layout.props.append(entry);prop_transforms[index]=transform
			var cell:=cell_at(p)
			if not prop_buckets.has(cell):prop_buckets[cell]=[]
			prop_buckets[cell].append(index)
	ocean=$Ocean
	update_focus(Vector3(-4,137,184),true)
	print("WORLD READY: ",core.size()," independent terrain scenes, ",layout.props.size()," saved scatter instances, ",landmarks.size()," scene landmarks, ",ports.size()," scene ports")

func first_mesh(node: Node) -> MeshInstance3D:
	if node is MeshInstance3D: return node
	for child in node.get_children():
		var found := first_mesh(child)
		if found: return found
	return null

func cell_at(point: Vector3) -> Vector2i:
	return Vector2i(floori(point.x/CHUNK),floori(point.z/CHUNK))

func new_model(p: Array) -> Node3D:
	var node:Node3D=load("res://scenes/prefabs/"+p[0]+".tscn").instantiate()
	node.name = p[0]
	node.position = Vector3(p[1],p[2],p[3])
	node.rotation.y = p[5]
	node.scale = Vector3.ONE*float(p[4])
	add_child(node)
	return node

func add_multimesh(kind: String,cell: Vector2i,entries: Array) -> MultiMeshInstance3D:
	var multi := MultiMesh.new()
	multi.transform_format = MultiMesh.TRANSFORM_3D
	multi.mesh = model_meshes[kind]
	multi.instance_count = entries.size()
	var origin := Vector3(cell.x*CHUNK,0,cell.y*CHUNK)
	for i in range(entries.size()):
		var p: Array = entries[i]
		var basis := Basis(Vector3.UP,float(p[5])).scaled(Vector3.ONE*float(p[4]))
		multi.set_instance_transform(i,Transform3D(basis,Vector3(p[1],p[2],p[3])-origin))
	var node := MultiMeshInstance3D.new()
	node.name = kind+"_grove"
	node.multimesh = multi
	node.material_override = WORLD_MATERIAL
	node.position = origin
	node.visibility_range_end = 16000 if kind.begins_with("cloud") else 3200
	if kind.begins_with("cloud"):
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		node.material_override = preload("res://materials/cloud.tres")
	add_child(node)
	return node

func make_ocean() -> void:
	ocean = MeshInstance3D.new()
	ocean.name = "Continuous ocean"
	var plane := PlaneMesh.new()
	plane.size = Vector2(100000,100000)
	ocean.mesh = plane
	var water := ShaderMaterial.new()
	water.shader = preload("res://scripts/open_water.gdshader")
	ocean.material_override = water
	ocean.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(ocean)
	var water_body := StaticBody3D.new()
	water_body.name = "Sea level collision"
	water_body.collision_layer = 1
	water_body.collision_mask = 2
	var boundary := WorldBoundaryShape3D.new()
	boundary.plane = Plane(Vector3.UP,0)
	var collider := CollisionShape3D.new()
	collider.shape = boundary
	water_body.add_child(collider)
	add_child(water_body)

func update_focus(point: Vector3,force := false) -> void:
	focus = point
	var cell := cell_at(point)
	ocean.position = Vector3(point.x,0,point.z)
	if cell != last_cell or force:
		last_cell = cell
		load_queue.clear()
		for z in range(-7,8):
			for x in range(-7,8):
				var key := cell+Vector2i(x,z)
				if not chunks.has(key): load_queue.append(key)
		load_queue.sort_custom(func(a,b):return (a-cell).length_squared()<(b-cell).length_squared())
		for key in chunks.keys():
			if not core.has(key) and (key-cell).length()>10:
				if terrain_bodies.has(key):
					terrain_bodies[key].queue_free()
					terrain_bodies.erase(key)
				chunks[key].queue_free()
				chunks.erase(key)
				terrain_samples.erase(key)
				for index in prop_buckets.get(key,[]):
					if prop_colliders.has(index):
						prop_colliders[index].queue_free()
						prop_colliders.erase(index)
					layout.props[index]=null
					prop_transforms.erase(index)
					free_prop_indices.append(index)
				prop_buckets.erase(key)
	if force:
		for z in range(-1,2):
			for x in range(-1,2):
				var key := cell+Vector2i(x,z)
				if not chunks.has(key): build_chunk(key)
		refresh_collisions()

func _process(delta: float) -> void:
	if Engine.is_editor_hint():return
	for rotor in rotors: rotor.rotation.z += delta*.35
	for ring in rings:
		if ring.visible: ring.rotation.z += delta*.05
	if generation_thread and generation_thread.is_started() and not generation_thread.is_alive():
		var data:Dictionary=generation_thread.wait_to_finish()
		if not chunks.has(pending_cell) and (pending_cell-last_cell).length()<10:
			apply_chunk_data(pending_cell,data)
		generation_thread=null
	if not generation_thread and not load_queue.is_empty():
		var key: Vector2i = load_queue.pop_front()
		if not chunks.has(key):
			pending_cell=key
			generation_thread=Thread.new()
			var err:=generation_thread.start(generate_chunk_data.bind(key))
			if err!=OK:
				generation_thread=null
				build_chunk(key)
	collision_clock += delta
	if collision_clock>.4:
		collision_clock = 0
		refresh_collisions()

func _exit_tree() -> void:
	if generation_thread and generation_thread.is_started():generation_thread.wait_to_finish()

func build_chunk(cell: Vector2i) -> MeshInstance3D:
	return apply_chunk_data(cell,generate_chunk_data(cell))

func generate_chunk_data(cell: Vector2i) -> Dictionary:
	var grid := PackedVector3Array()
	for z in range(33):
		for x in range(33):
			var point:Vector2 = geography.vertex_xz(cell.x*32+x,cell.y*32+z)
			grid.append(Vector3(point.x-cell.x*CHUNK,geography.height_at(point.x,point.y),point.y-cell.y*CHUNK))
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var colors := PackedColorArray()
	for z in range(32):
		for x in range(32):
			var a := z*33+x
			var faces := [[a,a+33,a+34],[a,a+34,a+1]] if (x+z)%2==0 else [[a,a+33,a+1],[a+1,a+33,a+34]]
			for f in faces:
				var p: Vector3 = grid[f[0]]
				var q: Vector3 = grid[f[1]]
				var r: Vector3 = grid[f[2]]
				var normal := (q-p).cross(r-p).normalized()
				var color: Color = geography.terrain_color((p+q+r)/3+Vector3(cell.x*CHUNK,0,cell.y*CHUNK),normal)
				# Godot front faces are clockwise. Blender's glTF importer reverses
				# triangle indices too; keep the outward normal while matching it.
				vertices.append_array(PackedVector3Array([p,r,q]))
				normals.append_array(PackedVector3Array([normal,normal,normal]))
				colors.append_array(PackedColorArray([color,color,color]))
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_COLOR] = colors
	var rng := RandomNumberGenerator.new()
	rng.seed = absi(cell.x*73856093 ^ cell.y*19349663)
	var entries: Array = []
	for i in range(65):
		var wx := (cell.x+rng.randf())*CHUNK
		var wz := (cell.y+rng.randf())*CHUNK
		var hy: float = geography.surface_height(wx,wz)
		if hy<7 or hy>280: continue
		entries.append(["pine" if hy>140 else "oak",wx,hy,wz,rng.randf_range(.65,1.25),rng.randf_range(0,TAU),true])
	return {"arrays":arrays,"entries":entries}

func apply_chunk_data(cell:Vector2i,data:Dictionary) -> MeshInstance3D:
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,data.arrays)
	var node := MeshInstance3D.new()
	node.name = "Generated_ground_%s_%s" % [cell.x,cell.y]
	node.position = Vector3(cell.x*CHUNK,0,cell.y*CHUNK)
	node.mesh = mesh
	node.material_override = WORLD_MATERIAL
	node.visibility_range_end = 14500
	add_child(node)
	chunks[cell] = node
	generated_chunks += 1
	# The extension also contains actual vegetation meshes and their colliders.
	var entries:Array=data.entries
	for p in entries:
		if not prop_buckets.has(cell): prop_buckets[cell] = []
		if free_prop_indices.is_empty():
			prop_buckets[cell].append(layout.props.size())
			layout.props.append(p)
		else:
			var index:int=free_prop_indices.pop_back()
			layout.props[index]=p
			prop_buckets[cell].append(index)
	for kind in ["oak","pine"]:
		var selected := entries.filter(func(p): return p[0]==kind)
		if not selected.is_empty():
			var grove := add_multimesh(kind,cell,selected)
			grove.reparent(node,true)
	return node

func mesh_body(mesh: Mesh,parent: Node3D,ground_surface:=false) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.collision_layer = 5 if ground_surface else 1
	body.collision_mask = 2
	var shape := ConcavePolygonShape3D.new()
	shape.backface_collision = true
	shape.set_faces(mesh.get_faces())
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	parent.add_child(body)
	return body

func refresh_collisions() -> void:
	var cell := cell_at(focus)
	for key in chunks:
		if abs(key.x-cell.x)<=2 and abs(key.y-cell.y)<=2:
			if not terrain_bodies.has(key): terrain_bodies[key] = mesh_body(chunks[key].mesh,chunks[key],true)
	for key in terrain_bodies.keys():
		if core.has(key):
			terrain_bodies[key].collision_layer=5 if abs(key.x-cell.x)<=3 and abs(key.y-cell.y)<=3 else 4
			continue
		if abs(key.x-cell.x)>3 or abs(key.y-cell.y)>3:
			terrain_bodies[key].queue_free()
			terrain_bodies.erase(key)
	var nearby: Dictionary = {}
	for dz in range(-1,2):
		for dx in range(-1,2):
			for index in prop_buckets.get(cell+Vector2i(dx,dz),[]):
				var p: Array = layout.props[index]
				if not p[6] or p[0]=="bush": continue
				var pos := Vector3(p[1],p[2],p[3])
				if Vector2(focus.x-pos.x,focus.z-pos.z).length()>350 or abs(focus.y-pos.y)>150: continue
				nearby[index] = true
				if prop_colliders.has(index): continue
				var body: StaticBody3D
				if p[0] in ["oak","pine","poplar"]:
					body = StaticBody3D.new()
					body.collision_layer=1
					body.collision_mask=2
					var shape := CapsuleShape3D.new()
					shape.radius = 2.4
					shape.height = 11
					var collider := CollisionShape3D.new()
					collider.shape = shape
					collider.position.y=5.5
					body.add_child(collider)
					add_child(body)
				else:
					body = mesh_body(model_meshes[p[0]],self)
				body.transform = prop_transforms.get(index,Transform3D(Basis(Vector3.UP,float(p[5])).scaled(Vector3.ONE*float(p[4])),pos))
				prop_colliders[index] = body
	for index in prop_colliders.keys():
		if not nearby.has(index):
			prop_colliders[index].queue_free()
			prop_colliders.erase(index)

func ground_height(point: Vector3) -> float:
	var height:=terrain_height(point)
	# The ground-probe layer includes actual terrain, cliff modules and sea.
	# Probe BELOW the caller: a cliff overhang above the ship is not its ground.
	# Retain the mesh sample even when distant physics bodies are not loaded;
	# the infinite ocean must not turn real streamed land into zero AGL height.
	if is_inside_tree():
		var ray:=PhysicsRayQueryParameters3D.create(point+Vector3.UP*.01,Vector3(point.x,-100,point.z),4)
		var hit:=get_world_3d().direct_space_state.intersect_ray(ray)
		if not hit.is_empty():height=maxf(height,hit.position.y)
	return height

func terrain_height(point:Vector3) -> float:
	var cell:=cell_at(point)
	if not chunks.has(cell):return maxf(0,geography.surface_height(point.x,point.z))
	var ground:MeshInstance3D=chunks[cell]
	if not terrain_samples.has(cell):
		var triangles:=ground.mesh.get_faces()
		var buckets:Dictionary={}
		for i in range(0,triangles.size(),3):
			var a:Vector3=triangles[i]
			var b:Vector3=triangles[i+1]
			var c:Vector3=triangles[i+2]
			var low:=Vector2i(clampi(floori(minf(a.x,minf(b.x,c.x))/24),0,31),clampi(floori(minf(a.z,minf(b.z,c.z))/24),0,31))
			var high:=Vector2i(clampi(floori(maxf(a.x,maxf(b.x,c.x))/24),0,31),clampi(floori(maxf(a.z,maxf(b.z,c.z))/24),0,31))
			for z in range(low.y,high.y+1):
				for x in range(low.x,high.x+1):
					var key:=Vector2i(x,z)
					if not buckets.has(key):buckets[key]=[]
					buckets[key].append(i)
		terrain_samples[cell]={"triangles":triangles,"buckets":buckets}
	var sample:Dictionary=terrain_samples[cell]
	var local:=ground.to_local(point)
	var key:=Vector2i(clampi(floori(local.x/24),0,31),clampi(floori(local.z/24),0,31))
	for i in sample.buckets.get(key,[]):
		var a:Vector3=sample.triangles[i]
		var b:Vector3=sample.triangles[i+1]
		var c:Vector3=sample.triangles[i+2]
		var denominator:float=(b.z-c.z)*(a.x-c.x)+(c.x-b.x)*(a.z-c.z)
		if absf(denominator)<1e-8:continue
		var wa:float=((b.z-c.z)*(local.x-c.x)+(c.x-b.x)*(local.z-c.z))/denominator
		var wb:float=((c.z-a.z)*(local.x-c.x)+(a.x-c.x)*(local.z-c.z))/denominator
		var wc:float=1-wa-wb
		if minf(wa,minf(wb,wc))>=-.0001:
			return maxf(0,ground.to_global(Vector3(local.x,a.y*wa+b.y*wb+c.y*wc,local.z)).y)
	push_error("Terrain triangle sampling missed ",cell," at ",point)
	return maxf(0,geography.height_at(point.x,point.z))

func set_wireframe(enabled: bool) -> void:
	inspection = enabled
	if wire_lines.is_empty() and enabled:
		var line_material := StandardMaterial3D.new()
		line_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		line_material.albedo_color = Color("263e4b")
		line_material.no_depth_test = false
		for key in chunks:
			if (key-cell_at(focus)).length()>4:continue
			var source: MeshInstance3D = chunks[key]
			var faces := source.mesh.get_faces()
			var edges := PackedVector3Array()
			for i in range(0,faces.size(),3):edges.append_array(PackedVector3Array([faces[i],faces[i+1],faces[i+1],faces[i+2],faces[i+2],faces[i]]))
			var arrays:=[]
			arrays.resize(Mesh.ARRAY_MAX)
			arrays[Mesh.ARRAY_VERTEX]=edges
			var mesh:=ArrayMesh.new()
			mesh.add_surface_from_arrays(Mesh.PRIMITIVE_LINES,arrays)
			var node:=MeshInstance3D.new()
			node.mesh=mesh
			node.material_override=line_material
			node.position.y=.07
			source.add_child(node)
			wire_lines.append(node)
	for line_node in wire_lines: line_node.visible=enabled

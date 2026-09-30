extends RefCounted
var world:Node3D
var changed_cells:Dictionary={}
var tile_records:Array=[]
var scatter_records:Array=[]
var unresolved:Array=[]
var source_refs:Array=[]
var output_folder:String
func vec(v:Vector3)->Array:return [v.x,v.y,v.z]
func inside(p:Vector3)->bool:return p.x>=-3750. and p.x<=-900. and p.z>=-4400. and p.z<=-2150.
func terrain_hit(p:Vector3)->Dictionary:
	var query:=PhysicsRayQueryParameters3D.create(Vector3(p.x,1100,p.z),Vector3(p.x,-100,p.z),4)
	return world.get_world_3d().direct_space_state.intersect_ray(query)
func first_mesh(node:Node)->MeshInstance3D:
	if node is MeshInstance3D:return node
	for child in node.get_children():
		var found:MeshInstance3D=first_mesh(child)
		if found!=null:return found
	return null
func configure(game:Node3D,folder:String,output:String)->Dictionary:
	world=game.get_node("World");world.set_process(false);output_folder=output
	DirAccess.make_dir_recursive_absolute(output.path_join("native-scenes"))
	# Snapshot actual saved MultiMesh transforms and old mesh support before edits.
	var groves:Array=[];var global_index:int=0
	for grove in world.get_node("Vegetation").get_children():
		var entries:Array=[]
		for i in range(grove.multimesh.instance_count):
			var transform:Transform3D=grove.global_transform*grove.multimesh.get_instance_transform(i)
			var selected:bool=inside(transform.origin)
			entries.append({"source_index":i,"global_index":global_index,"transform":transform,"selected":selected,"old_ground":world.terrain_height(transform.origin) if selected else 0.})
			global_index+=1
		groves.append({"node":grove,"entries":entries,"kind":str(grove.get_meta("asset_kind"))})
	assert(global_index==world.layout.props.size())
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("model-report.json")))
	for item in plan.native_tiles:
		var tile:Node3D=world.get_node("Terrain/"+str(item.name))
		var old:Node3D=tile.get_node("Model");old.visible=false
		var doc:=GLTFDocument.new();var state:=GLTFState.new();var source:String=folder.path_join(str(item.name)+".glb")
		assert(doc.append_from_file(source,state)==OK)
		var model:Node3D=doc.generate_scene(state);model.name="NativeModel36a";tile.add_child(model)
		var mesh:MeshInstance3D=first_mesh(model);assert(mesh!=null)
		var terrain_material:Material=load("res://materials/terrain.tres")
		mesh.material_override=terrain_material
		var shape:=ConcavePolygonShape3D.new();shape.backface_collision=true;shape.set_faces(mesh.mesh.get_faces())
		tile.get_node("Collision/Shape").shape=shape
		var cell:Vector2i=world.cell_at(tile.global_position+Vector3(.01,0,.01));world.chunks[cell]=mesh
		world.terrain_samples.erase(cell);changed_cells[cell]=true
		source_refs.append(old);old.queue_free()
		# Save a native editable local tile with the actual generated collision.
		var native:=Node3D.new();native.name=str(item.name)
		var saved_model:Node3D=model.duplicate();native.add_child(saved_model)
		set_owner_recursive(saved_model,native)
		var body:=StaticBody3D.new();body.name="Collision";body.collision_layer=5;body.collision_mask=2;native.add_child(body);body.owner=native
		var collider:=CollisionShape3D.new();collider.shape=shape;body.add_child(collider);collider.owner=native
		var packed:=PackedScene.new();assert(packed.pack(native)==OK)
		var destination:String=output.path_join("native-scenes/"+str(item.name)+".tscn")
		assert(ResourceSaver.save(packed,destination)==OK);native.free()
		tile_records.append({"name":item.name,"world_position":vec(tile.global_position),"mesh_triangles":mesh.mesh.get_faces().size()/3,"collision_faces":shape.get_faces().size()/3,"glb_sha256":FileAccess.get_sha256(source),"native_scene":destination,"native_scene_sha256":FileAccess.get_sha256(destination)})
	await world.get_tree().physics_frame;await world.get_tree().physics_frame;await world.get_tree().physics_frame
	for row in groves:
		var grove:MultiMeshInstance3D=row.node;var remaining:Array[Transform3D]=[];var pines:Array[Transform3D]=[];var touched:bool=false
		for entry in row.entries:
			var original:Transform3D=entry.transform;var transform:Transform3D=original;var kind:String=row.kind;var converted_to_pine:bool=false
			if entry.selected:
				var hit:Dictionary=terrain_hit(original.origin)
				if hit.is_empty():unresolved.append({"grove":str(grove.name),"source_index":entry.source_index,"reason":"No actual terrain collision"})
				else:
					var height_delta:float=hit.position.y-float(entry.old_ground)
					if absf(height_delta)>.05:
						touched=true
						var tree:bool=kind in ["oak","poplar","pine"]
						var target:Dictionary=find_site(original.origin,hit,tree)
						if target.is_empty():unresolved.append({"grove":str(grove.name),"source_index":entry.source_index,"reason":"No dry supported destination within480m"})
						else:
							var offset:float=clampf(original.origin.y-float(entry.old_ground),-1.5,1.5)
							transform.origin=target.position+Vector3(0,offset,0)
							if tree:kind="pine";converted_to_pine=true
							var index:int=entry.global_index
							var prop:Array=world.layout.props[index];prop[0]=kind;prop[1]=transform.origin.x;prop[2]=transform.origin.y;prop[3]=transform.origin.z
							world.layout.props[index]=prop;world.prop_transforms[index]=transform
							if world.prop_colliders.has(index):world.prop_colliders[index].queue_free();world.prop_colliders.erase(index)
							scatter_records.append({"source_grove":str(grove.name),"source_index":entry.source_index,"global_prop_index":index,"source_kind":row.kind,"kind":kind,"old_position":vec(original.origin),"new_position":vec(transform.origin),"ground_y":target.position.y,"normal":vec(target.normal),"clearance":offset,"horizontal_move_m":Vector2(transform.origin.x-original.origin.x,transform.origin.z-original.origin.z).length(),"new_grove":str(grove.name)+"_CoastalPines36a" if converted_to_pine else str(grove.name),"new_index":pines.size() if converted_to_pine else remaining.size()})
			if converted_to_pine:pines.append(grove.global_transform.affine_inverse()*transform)
			else:remaining.append(grove.global_transform.affine_inverse()*transform)
		if touched:
			var old_multi:MultiMesh=grove.multimesh;source_refs.append(old_multi)
			grove.multimesh=make_multi(old_multi.mesh,remaining)
			assert(ResourceSaver.save(grove.multimesh,output.path_join("native-scenes/"+str(grove.name)+".res"))==OK)
			if not pines.is_empty():
				var pine:=MultiMeshInstance3D.new();pine.name=str(grove.name)+"_CoastalPines36a"
				pine.multimesh=make_multi(world.model_meshes["pine"],pines);pine.material_override=load("res://materials/world.tres")
				grove.get_parent().add_child(pine);pine.global_transform=grove.global_transform;pine.set_meta("asset_kind","pine")
				assert(ResourceSaver.save(pine.multimesh,output.path_join("native-scenes/"+str(pine.name)+".res"))==OK)
	# Keep global prop indices stable while rebuilding buckets for relocations.
	world.prop_buckets.clear()
	for index in range(world.layout.props.size()):
		var p:Array=world.layout.props[index];var cell:Vector2i=world.cell_at(Vector3(p[1],p[2],p[3]))
		if not world.prop_buckets.has(cell):world.prop_buckets[cell]=[]
		world.prop_buckets[cell].append(index)
	world.focus=Vector3(-2600,130,-2900);world.refresh_collisions()
	await world.get_tree().physics_frame;await world.get_tree().physics_frame
	var support_failures:Array=[];var max_error:float=0.
	for entry in scatter_records:
		var p:=Vector3(entry.new_position[0],entry.new_position[1],entry.new_position[2]);var hit:Dictionary=terrain_hit(p)
		var error:float=INF if hit.is_empty() else absf(p.y-float(entry.clearance)-hit.position.y)
		max_error=maxf(max_error,error)
		if error>.03:support_failures.append({"global_index":entry.global_prop_index,"error_m":error})
	var probes:Array=[]
	for item in plan.tidal_estuary_controls:
		var p:=Vector3(item[0],800,item[1]);var hit:Dictionary=terrain_hit(p)
		probes.append({"position_xz":[p.x,p.z],"actual_collision_y":null if hit.is_empty() else hit.position.y,"collider":null if hit.is_empty() else str(hit.collider.get_path())})
	var report:Dictionary={"tiles":tile_records,"scatter_changes":scatter_records,"scatter_total_preserved":world.layout.props.size(),"unresolved":unresolved,"support_failures":support_failures,"max_axis_support_error_m":max_error,"estuary_probes":probes,"scope":"Actual14 saved tile models/collisions replaced locally; influenced saved scatter re-grounded or moved to dry slope, affected broadleaf instances become native pines. Global prop indices preserved and collision buckets synchronized. Axis support is not full canopy/trunk overlap proof. LandDetails/settlement/route exclusion from independent actual GLB intake; existing33f coast/islands retained. Native tile scenes and split MultiMesh resources saved as candidate artifacts, not installed production.","production_modified":false}
	var file:=FileAccess.open(output.path_join("highcoast-runtime.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	assert(unresolved.is_empty() and support_failures.is_empty())
	return {"tile_count":tile_records.size(),"scatter_changes":scatter_records.size(),"max_axis_support_error_m":max_error,"report_sha256":FileAccess.get_sha256(output.path_join("highcoast-runtime.json")),"unresolved":unresolved.size(),"scope":report.scope}
func set_owner_recursive(node:Node,owner_node:Node)->void:
	node.owner=owner_node
	for child in node.get_children():set_owner_recursive(child,owner_node)
func make_multi(mesh:Mesh,transforms:Array[Transform3D])->MultiMesh:
	var m:=MultiMesh.new();m.transform_format=MultiMesh.TRANSFORM_3D;m.mesh=mesh;m.instance_count=transforms.size()
	for i in range(transforms.size()):m.set_instance_transform(i,transforms[i])
	return m
func suitable(hit:Dictionary,tree:bool)->bool:
	return not hit.is_empty() and hit.position.y>3. and hit.normal.y>(.65 if tree else .50) and (not tree or hit.position.y<315.)
func find_site(p:Vector3,initial:Dictionary,tree:bool)->Dictionary:
	if suitable(initial,tree):return initial
	for radius in range(24,481,24):
		for angle in range(16):
			var q:=p+Vector3(cos(float(angle)*TAU/16.)*radius,0,sin(float(angle)*TAU/16.)*radius)
			if not inside(q):continue
			var hit:Dictionary=terrain_hit(q)
			if suitable(hit,tree):return hit
	return {}

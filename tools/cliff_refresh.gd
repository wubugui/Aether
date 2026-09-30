extends RefCounted
## Geometry refresh bookkeeping. All transforms are measured on actual instances.
## These helpers mutate only the supplied in-memory world and scatter resources.

static func matching_instances(world:Node3D,kit:Array) -> Dictionary:
	var by_path:Dictionary={};var by_kind:Dictionary={};var result:Dictionary={}
	for item in kit:
		by_path["res://scenes/prefabs/"+item.name+".tscn"]=item.name
		# Tests and alternate authored libraries may supply their prefab path.
		if item.has("prefab_path"):by_path[item.prefab_path]=item.name
		by_kind[item.name]=true;result[item.name]=[]
	for node in world.find_children("*","Node3D",true,false):
		var kind:String=by_path.get(node.scene_file_path,"")
		if kind.is_empty():
			for property in node.get_property_list():
				if property.name=="asset_kind":
					var value=node.get("asset_kind")
					if value is String and by_kind.has(value):kind=value
					break
		if not kind.is_empty():result[kind].append(node)
	return result

static func collision_bounds(instance:Node3D) -> Array[AABB]:
	var result:Array[AABB]=[]
	for node in instance.find_children("*","CollisionShape3D",true,false):
		if not node.shape:continue
		if node.shape is ConcavePolygonShape3D:
			var faces:PackedVector3Array=node.shape.get_faces()
			if faces.is_empty():continue
			var bounds:=AABB(node.global_transform*faces[0],Vector3.ZERO)
			for p in faces:bounds=bounds.expand(node.global_transform*p)
			result.append(bounds.grow(2.0))
		else:
			result.append((node.global_transform*node.shape.get_debug_mesh().get_aabb()).grow(2.0))
	return result

static func snapshot(world:Node3D,kit:Array) -> Dictionary:
	var records:Array=[];var bounds:Array[AABB]=[]
	var matches:=matching_instances(world,kit)
	for kind in matches:
		for instance in matches[kind]:
			var old_bounds:=collision_bounds(instance)
			bounds.append_array(old_bounds)
			records.append({"path":str(world.get_path_to(instance)),"kind":kind,
				"transform":instance.global_transform,"bounds":old_bounds})
	return {"instances":records,"bounds":bounds}

static func finish(world:Node3D,kit:Array,before:Dictionary) -> Dictionary:
	var changed_bounds:Array[AABB]=[];var fresh_bounds:Array[AABB]=[];var count:=0
	changed_bounds.append_array(before.get("bounds",[]))
	var matches:=matching_instances(world,kit)
	for item in kit:
		var origin:=Vector3(item.position[0],item.position[1],item.position[2])
		for instance in matches[item.name]:
			if item.has("original_origin"):
				var legacy:Vector3=Vector3(item.original_origin[0],item.original_origin[1],item.original_origin[2])
				var previous:Vector3=instance.get_meta("asset_origin",legacy)
				instance.position+=instance.basis*(origin-previous)
			instance.set_meta("asset_origin",origin)
			var model:Node3D=instance.get_node_or_null("Model")
			if model:
				var nodes:Array[Node]=model.find_children("*","MeshInstance3D",true,false)
				if model is MeshInstance3D:nodes.append(model)
				for node in nodes:fresh_bounds.append((node.global_transform*node.get_aabb()).grow(2.0))
			count+=1
	changed_bounds.append_array(fresh_bounds)
	return {"changed_bounds":changed_bounds,"new_bounds":fresh_bounds,"instance_count":count}

static func in_footprints(p:Vector3,bounds:Array) -> bool:
	for box in bounds:
		if p.x>=box.position.x and p.x<=box.end.x and p.z>=box.position.z and p.z<=box.end.z:return true
	return false

static func reseat_grove(world:Node3D,grove:MultiMeshInstance3D,regions:Dictionary,changed_bounds:Array) -> Dictionary:
	var data:MultiMesh;var removed:Dictionary={};var moved:=0
	for i in range(grove.multimesh.instance_count):
		var tr:Transform3D=grove.global_transform*grove.multimesh.get_instance_transform(i)
		var p:=tr.origin;var affected:=in_footprints(p,changed_bounds)
		if not affected:
			for region in regions.get(Vector2i(floori(p.x/768),floori(p.z/768)),[]):
				var local:Vector3=region.to_local(p)
				if local.x>=0 and local.x<=768 and local.z>=0 and local.z<=768:affected=true;break
		if not affected:continue
		var ray:=PhysicsRayQueryParameters3D.create(Vector3(p.x,2200,p.z),Vector3(p.x,-100,p.z),4)
		var hit:=world.get_world_3d().direct_space_state.intersect_ray(ray)
		if hit.is_empty():continue
		if hit.position.y<.6:removed[i]=true;continue
		if grove.get_meta("asset_kind","") in ["oak","pine","poplar","bush"] and (hit.normal.y<.60 or (hit.position.y>170 and p.z< -1500)):
			removed[i]=true;continue
		if absf(hit.position.y-p.y)<.01:continue
		if not data:data=preload("res://scripts/scatter_group.gd").copy_data(grove.multimesh)
		tr.origin.y=hit.position.y
		data.set_instance_transform(i,grove.global_transform.affine_inverse()*tr);moved+=1
	if not removed.is_empty():
		var source:MultiMesh=data if data else grove.multimesh
		var remaining:=MultiMesh.new();remaining.transform_format=MultiMesh.TRANSFORM_3D
		remaining.mesh=source.mesh;remaining.use_colors=source.use_colors;remaining.use_custom_data=source.use_custom_data
		remaining.instance_count=source.instance_count-removed.size()
		var next:=0
		for i in range(source.instance_count):
			if removed.has(i):continue
			remaining.set_instance_transform(next,source.get_instance_transform(i))
			if source.use_colors:remaining.set_instance_color(next,source.get_instance_color(i))
			if source.use_custom_data:remaining.set_instance_custom_data(next,source.get_instance_custom_data(i))
			next+=1
		data=remaining
	return {"data":data,"moved":moved,"removed":removed.size()}

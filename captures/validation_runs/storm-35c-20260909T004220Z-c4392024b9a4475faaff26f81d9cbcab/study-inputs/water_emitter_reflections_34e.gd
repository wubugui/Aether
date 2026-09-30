extends RefCounted
## Bounded static reflection study: actual emitter dimensions and opaque geometry.
const MAP_W:=64
const MAP_H:=32
const MAX_DISTANCE:=450.
const REFLECTION_LAYER:=1048576
var records:Array=[]
var excluded:Array[RID]=[]
var excluded_paths:Array=[]
var opaque_records:Array=[]
func xyz(v:Vector3)->Array:return [v.x,v.y,v.z]
func emitter(owner:Node3D,needle:String)->Dictionary:
	var low:=Vector3(INF,INF,INF);var high:=Vector3(-INF,-INF,-INF)
	var color:=Color.BLACK;var multiplier:=0.;var surfaces:Array=[];var count:=0
	for mesh in owner.find_children("*","MeshInstance3D",true,false):
		if mesh.mesh==null:continue
		for index in range(mesh.mesh.get_surface_count()):
			var material:Material=mesh.get_active_material(index)
			if not material is StandardMaterial3D or not material.resource_name.contains(needle):continue
			assert(material.emission_enabled)
			var arrays:Array=mesh.mesh.surface_get_arrays(index)
			var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
			for vertex in vertices:
				var at:Vector3=mesh.to_global(vertex);low=low.min(at);high=high.max(at);count+=1
			color=material.emission;multiplier=material.emission_energy_multiplier
			surfaces.append({"mesh":str(mesh.get_path()),"surface":index,"material":material.resource_name,"vertices":vertices.size()})
	assert(count>0 and multiplier>0.)
	return {"center":(low+high)*.5,"half_axes":(high-low)*.5,"color":color,"energy":multiplier,"surfaces":surfaces,"vertices":count}
func opaque_tower(tower:Node3D,parent:Node3D)->void:
	# Replace only the coarse tower colliders for this query with its actual
	# opaque triangle surfaces, keeping shaft/canopy/rail occlusion.
	for body in tower.find_children("*","CollisionObject3D",true,false):
		excluded.append(body.get_rid());excluded_paths.append(str(body.get_path()))
	var triangles:=PackedVector3Array();var surfaces:Array=[]
	for mesh in tower.find_children("*","MeshInstance3D",true,false):
		if mesh.mesh==null:continue
		for index in range(mesh.mesh.get_surface_count()):
			var material:Material=mesh.get_active_material(index)
			if not material is StandardMaterial3D:continue
			if material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED:continue
			if material.resource_name.contains("Lamp core") or material.resource_name.to_lower().contains("glass"):continue
			var arrays:Array=mesh.mesh.surface_get_arrays(index);var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
			var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
			if indices.is_empty():
				for vertex in vertices:triangles.append(mesh.to_global(vertex))
			else:
				for vertex_index in indices:triangles.append(mesh.to_global(vertices[vertex_index]))
			surfaces.append({"mesh":str(mesh.get_path()),"surface":index,"material":material.resource_name})
	assert(triangles.size()>0 and triangles.size()%3==0)
	var body:=StaticBody3D.new();body.name=str(tower.name)+"OpaqueReflectionCaster";body.collision_layer=REFLECTION_LAYER;body.collision_mask=0;parent.add_child(body)
	var collision:=CollisionShape3D.new();var shape:=ConcavePolygonShape3D.new();shape.set_faces(triangles);shape.backface_collision=true;collision.shape=shape;body.add_child(collision)
	opaque_records.append({"tower":str(tower.get_path()),"body":str(body.get_path()),"triangles":triangles.size()/3,"surfaces":surfaces})
func configure(game:Node3D,environment_adapter:RefCounted,output_folder:String,night:bool)->Dictionary:
	if not night:return {"night":false,"emitters":[],"scope":"No emissive-source reflection in daylight."}
	var casters:=Node3D.new();casters.name="ActualOpaqueReflectionCasters34e";game.add_child(casters)
	for body in game.find_children("*","CollisionObject3D",true,false):
		if str(body.name)=="SeaCollision":excluded.append(body.get_rid());excluded_paths.append(str(body.get_path()))
	var lights:Array=[]
	for light in game.find_children("*","OmniLight3D",true,false):
		if str(light.name) not in ["NativeLanternLight","VillageWarmLight","HarborWarmLight"]:continue
		if not light.is_visible_in_tree() or light.light_energy<=0.:continue
		lights.append(light)
	lights.sort_custom(func(a,b):return str(a.get_path())<str(b.get_path()))
	assert(lights.size()==67)
	var positions:=PackedVector4Array();var dimensions:=PackedVector4Array();var colors:=PackedVector4Array()
	positions.resize(80);dimensions.resize(80);colors.resize(80)
	for index in range(lights.size()):
		var light:OmniLight3D=lights[index];var tower:bool=str(light.name)=="NativeLanternLight";var owner:Node3D=light.get_parent()
		var data:Dictionary=emitter(owner,"Lamp core" if tower else "Harbor lantern flame")
		var center:Vector3=data.center;var axes:Vector3=data.half_axes;var color:Color=data.color
		positions[index]=Vector4(center.x,center.y,center.z,0.)
		dimensions[index]=Vector4(axes.x,axes.y,axes.z,.024 if tower else .006)
		colors[index]=Vector4(color.r,color.g,color.b,float(data.energy))
		records.append({"index":index,"light_node":str(light.get_path()),"light_world_position":xyz(light.global_position),"omni_energy":light.light_energy,"omni_range":light.omni_range,"emitter_center":xyz(center),"emitter_half_axes":xyz(axes),"emission_color":[color.r,color.g,color.b],"emission_multiplier":data.energy,"angular_roughness":dimensions[index].w,"actual_surfaces":data.surfaces})
		if tower:opaque_tower(owner,casters)
	await game.get_tree().physics_frame;await game.get_tree().physics_frame;await game.get_tree().physics_frame
	var image:=Image.create(MAP_W,MAP_H*lights.size(),false,Image.FORMAT_RF)
	for index in range(lights.size()):
		var p:Vector4=positions[index];var origin:=Vector3(p.x,p.y,p.z);var distances:Array=[];var hits:Array=[]
		for y in range(MAP_H):
			for x in range(MAP_W):
				var azimuth:float=((float(x)+.5)/MAP_W-.5)*TAU;var down:float=(float(y)+.5)/MAP_H
				var lateral:float=sqrt(1.-down*down);var direction:=Vector3(cos(azimuth)*lateral,-down,sin(azimuth)*lateral)
				var query:=PhysicsRayQueryParameters3D.create(origin,origin+direction*MAX_DISTANCE,0xffffffff,excluded)
				var hit:Dictionary=game.get_world_3d().direct_space_state.intersect_ray(query);var distance:float=MAX_DISTANCE
				if not hit.is_empty():
					distance=origin.distance_to(hit.position);hits.append({"x":x,"y":y,"collider":str(hit.collider.get_path()),"position":xyz(hit.position),"distance_m":distance})
				image.set_pixel(x,index*MAP_H+y,Color(distance/MAX_DISTANCE,0.,0.,1.));distances.append(distance)
		records[index]["occlusion_distances_m"]=distances;records[index]["occlusion_hits"]=hits
	var texture:=ImageTexture.create_from_image(image);var bindings:=0;var seen_materials:Dictionary={};var bound_ids:Array=[]
	for material in environment_adapter.material_cache.values():
		if material is ShaderMaterial and material.shader==environment_adapter.shader_cache.get("open_water"):
			if seen_materials.has(material.get_instance_id()):continue
			seen_materials[material.get_instance_id()]=true;bound_ids.append(material.get_instance_id())
			material.set_shader_parameter("emitter_count",lights.size());material.set_shader_parameter("emitter_positions",positions)
			material.set_shader_parameter("emitter_dimensions",dimensions);material.set_shader_parameter("emitter_colors",colors)
			material.set_shader_parameter("emitter_occlusion",texture);bindings+=1
	assert(bindings>0)
	var report:={"night":true,"emitters":records,"water_material_bindings":bindings,"material_instance_ids":bound_ids,"map_width":MAP_W,"map_rows_per_emitter":MAP_H,"rays":MAP_W*MAP_H*lights.size(),"max_distance_m":MAX_DISTANCE,"excluded_original_colliders":excluded_paths,"actual_opaque_tower_colliders":opaque_records,"scope":"Actual67 native emission surfaces approximated by their world AABB half axes and angular roughness; material emission read after lighting setup.64x32 static downward hemisphere radial collision map per emitter,450m finite extent; outside extent emits no reflected contribution. Original coarse tower colliders replaced for reflection queries by actual opaque mesh faces, not entire tower shadow removal. Nearest map sampling is approximate for thin/edge occluders. All54 existing harbor lamps plus9village lamps and4tower cores; window/other scene emission not included. Roughness broadened with explicit radiance gain18; no physical radiometric calibration."}
	var file:=FileAccess.open(output_folder.path_join("actual-emitter-reflection.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	return {"night":true,"count":records.size(),"water_material_bindings":bindings,"rays":report.rays,"report_sha256":FileAccess.get_sha256(output_folder.path_join("actual-emitter-reflection.json")),"scope":report.scope}

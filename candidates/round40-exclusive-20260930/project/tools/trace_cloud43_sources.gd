extends SceneTree
## Read-only geometric attribution of visible-direction cloud surfaces in 42c.
## Triangle hits exclude terrain occlusion; this is source diagnosis, not a render.
var clouds: Array = []
func _initialize() -> void: call_deferred("run")
func transform_to_root(node: Node3D, game: Node) -> Transform3D:
	var t := node.transform
	var p := node.get_parent()
	while p != game:
		if p is Node3D: t = p.transform*t
		p = p.get_parent()
	return t
func run() -> void:
	var game: Node3D = load("res://scenes/candidate42c/Game42c.tscn").instantiate()
	for mesh in game.find_children("*","MeshInstance3D",true,false):
		var path := str(game.get_path_to(mesh))
		var group := ""
		for pair in [["SkyRegion39/UpperCloudBank41_","upper"],["SkyRegion39/CloudSea_","sea"],["SkyRegion39/DistantCloudBank41_","distant"],["World/Clouds/","world"],["NativeCoastalSky27f/cloud","coastal"]]:
			if path.begins_with(pair[0]): group=pair[1]
		if group.is_empty(): continue
		var t := transform_to_root(mesh,game)
		clouds.append({"path":path,"group":group,"transform":t,"inverse":t.affine_inverse(),"bounds":t*mesh.mesh.get_aabb(),"faces":mesh.mesh.get_faces()})
	var report := {"scope":"Exact cloud triangle ray hits on 42c upper half of each reference frame; does not test terrain occlusion and is not visual acceptance", "views":[]}
	var plan: Array = JSON.parse_string(FileAccess.get_file_as_string("res://assets/reference_views42.json"))
	for entry in plan:
		var c: Dictionary = entry.camera
		if not c.has("y_abs") or not c.has("ty_abs"):
			report.views.append({"ref":str(entry.ref),"skipped":"Requires runtime terrain-height camera resolution"})
			continue
		var origin := Vector3(c.x,c.y_abs,c.z)
		var basis := Basis.looking_at(Vector3(c.tx,c.ty_abs,c.tz)-origin,Vector3.UP)
		var counts := {}
		var hits := []
		for y in [0.04,0.16,0.28,0.40,0.52]:
			for x in [0.05,0.2,0.35,0.5,0.65,0.8,0.95]:
				var half_height := tan(deg_to_rad(float(c.fov))*.5)
				var direction: Vector3 = basis*Vector3((x*2-1)*half_height*1672.0/941.0,(1-y*2)*half_height,-1).normalized()
				var distance := INF
				var found := {}
				for cloud in clouds:
					if cloud.bounds.intersects_ray(origin,direction)==null: continue
					var local_origin: Vector3 = cloud.inverse*origin
					var local_direction: Vector3 = cloud.inverse.basis*direction
					var faces: PackedVector3Array = cloud.faces
					for i in range(0,faces.size(),3):
						var hit = Geometry3D.ray_intersects_triangle(local_origin,local_direction,faces[i],faces[i+1],faces[i+2])
						if hit == null: continue
						var d: float = (cloud.transform*hit).distance_to(origin)
						if d < distance:
							distance=d
							found={"path":cloud.path,"group":cloud.group,"distance":d,"uv":[x,y]}
				if not found.is_empty():
					hits.append(found)
					counts[found.group]=counts.get(found.group,0)+1
		report.views.append({"ref":str(entry.ref),"counts":counts,"hits":hits,"sample_count":35})
	var f := FileAccess.open("res://../evidence/cloud43-source-rays.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(report,"  "))
	game.free();quit()

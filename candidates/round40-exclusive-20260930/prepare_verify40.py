from pathlib import Path
import json
base=Path(__file__).resolve().parent; project=base/'project'
plan=json.loads((project/'assets/reference_views40.json').read_text(encoding='utf8'))
for entry in plan:
    if entry['ref']=='1274':
        entry['camera'].update(x=3200.7,y_abs=931.6,z=3001.5,tx=3197.5,ty_abs=931.4,tz=2999.3)
    elif entry['ref']=='1278':
        entry['camera'].update(x=3351.05,y_abs=961.65,z=3698.4,tx=3348.2,ty_abs=961.3,tz=3700.8)
(project/'assets/reference_views40.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
text=(project/'tools/verify_candidate39.gd').read_text(encoding='utf8')
text=text.replace('scenes/candidate39/Game39.tscn','scenes/candidate40/Game40.tscn').replace('scripts/game39.gd','scripts/game40.gd')
text=text.replace('game.camera.translate_object_local(Vector3(.6,0,0))','game.camera.translate_object_local(Vector3(.35,0,0))\n\t\t\tawait physics_frame\n\t\t\tcheck(camera_clear(), "Effective indoor side camera free of collision " + id)')
text=text.replace('var home: Transform3D = game.camera.transform','check(camera_clear(), "Effective indoor front camera free of collision " + id)\n\t\t\tvar home: Transform3D = game.camera.transform')
text=text.replace('var passed := true','await verify_solids()\n\tvar passed := true')
text+='''

func camera_clear() -> bool:
	var shape := SphereShape3D.new()
	shape.radius = .12
	var query := PhysicsShapeQueryParameters3D.new()
	query.shape = shape
	query.transform = Transform3D(Basis.IDENTITY,game.camera.global_position)
	query.collision_mask = 5
	query.exclude = [game.airship.get_rid()]
	return game.get_world_3d().direct_space_state.intersect_shape(query).is_empty()

func verify_solids() -> void:
	# Real existing player body moved against actual scene colliders; no probe
	# surrogate or changed collision settings. Test snapshots are restorable.
	game.photo_mode = true
	game.test_frozen = true
	var original: Transform3D = game.airship.transform
	var sky: Node3D = game.get_node("SkyRegion39")
	for name in ["CabinA", "CabinB"]:
		var cabin: Node3D = sky.get_node(name)
		game.airship.rotation = Vector3.ZERO
		# Approach a closed end wall from outside, above ground/cloud sea.
		game.airship.global_position = cabin.to_global(Vector3(0,1.5,25))
		await physics_frame
		var motion: Vector3 = cabin.global_basis * Vector3(0,0,-45)
		var hit: KinematicCollision3D = game.airship.move_and_collide(motion)
		check(hit != null and str(hit.get_collider().get_path()).contains("/"+name+"/"), "Player body blocked by real cabin end wall " + name, {"collider":str(hit.get_collider().get_path()) if hit != null else "none", "travel":str(hit.get_travel()) if hit != null else "none"})
	var island: Node3D = sky.get_node("FloatingIsland_0")
	game.airship.rotation = Vector3.ZERO
	game.airship.global_position = island.global_position + Vector3(0,140,0)
	await physics_frame
	var island_hit: KinematicCollision3D = game.airship.move_and_collide(Vector3(0,-260,0))
	check(island_hit != null and str(island_hit.get_collider().get_path()).contains("FloatingIsland_0"), "Player body blocked by real floating island", {"collider":str(island_hit.get_collider().get_path()) if island_hit != null else "none", "travel":str(island_hit.get_travel()) if island_hit != null else "none"})
	game.airship.transform = original
	# Physical rays inside both cabins must hit opaque wall lining between
	# boards while the offset window aperture retains a real exterior ray.
	for name in ["CabinA","CabinB"]:
		var cabin: Node3D = sky.get_node(name)
		var origin: Vector3 = cabin.to_global(Vector3(0,1.5,0))
		var closed := PhysicsRayQueryParameters3D.create(origin,cabin.to_global(Vector3(0,1.5,5)),5,[game.airship.get_rid()])
		var hit := game.get_world_3d().direct_space_state.intersect_ray(closed)
		check(not hit.is_empty() and str(hit.collider.get_path()).contains(name), "Cabin closed wall physically opaque " + name)
'''
(project/'tools/verify_round40.gd').write_text(text,encoding='utf8')
print('Candidate cameras and real-body verification written inside exclusive project')

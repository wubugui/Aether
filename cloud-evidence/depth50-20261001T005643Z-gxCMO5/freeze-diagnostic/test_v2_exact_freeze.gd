extends "res://tools/verify_lake_depth50_v2.gd"
var fixture: Node3D
func _initialize() -> void: call_deferred("test_v2")
func fixture_hit() -> bool:
	return not fixture.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(0,5,0),Vector3(0,-5,0),1)).is_empty()
func test_v2() -> void:
	fixture=Node3D.new();root.add_child(fixture)
	var body := StaticBody3D.new();fixture.add_child(body)
	var shape := CollisionShape3D.new();shape.shape=BoxShape3D.new();body.add_child(shape)
	await physics_frame;await physics_frame
	var before := collision_activity_state(fixture);var hit_before := fixture_hit()
	freeze_tree(fixture)
	await physics_frame;await physics_frame
	var after := collision_activity_state(fixture);var hit_after := fixture_hit()
	var ok := before==after and hit_before and hit_after
	print(JSON.stringify({"v2_exact_freeze_method_preserves_physics":ok,"body_count":before.size(),"before_hit":hit_before,"after_hit":hit_after,"all_mode_layer_rid_fields_equal":before==after,"game_scene_loaded":false,"saved_any_resource":false}))
	quit(0 if ok else 1)

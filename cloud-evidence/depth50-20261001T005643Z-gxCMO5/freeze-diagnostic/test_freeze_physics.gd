extends SceneTree
var world: Node3D
func _initialize() -> void: call_deferred("run")
func probe() -> bool:
	var query := PhysicsRayQueryParameters3D.create(Vector3(0,5,0),Vector3(0,-5,0),1)
	return not world.get_world_3d().direct_space_state.intersect_ray(query).is_empty()
func run() -> void:
	world=Node3D.new();root.add_child(world)
	var body := StaticBody3D.new();world.add_child(body)
	var collision := CollisionShape3D.new();collision.shape=BoxShape3D.new();body.add_child(collision)
	await physics_frame;await physics_frame
	var active := probe()
	world.process_mode=Node.PROCESS_MODE_DISABLED
	await physics_frame;await physics_frame
	var disabled := probe()
	world.process_mode=Node.PROCESS_MODE_INHERIT
	world.set_process(false);world.set_physics_process(false);body.set_process(false);body.set_physics_process(false)
	await physics_frame;await physics_frame
	var callbacks_off := probe()
	print(JSON.stringify({"active_ray_hit":active,"PROCESS_MODE_DISABLED_ray_hit":disabled,"script_callbacks_off_ray_hit":callbacks_off,"body_disable_mode":body.disable_mode,"scene_or_assets_loaded":false}))
	quit(0 if active and not disabled and callbacks_off else 1)

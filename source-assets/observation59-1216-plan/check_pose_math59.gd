extends SceneTree
func _initialize():
 var body:=Node3D.new()
 var target:=Basis(Vector3.UP,deg_to_rad(133.0))
 var angles:=target.get_euler(body.rotation_order)
 body.rotation=Vector3(0.0,angles.y,0.0)
 print(JSON.stringify({"order":body.rotation_order,"recovered_euler":str(angles),"basis_max_error":maxf((body.basis.x-target.x).length(),maxf((body.basis.y-target.y).length(),(body.basis.z-target.z).length())),"target_yaw_degrees":133.0,"actual_yaw_degrees":rad_to_deg(body.rotation.y),"whole_world_loaded":false}))
 var ok:=body.basis.is_equal_approx(target)
 body.free();quit(0 if ok else 1)

extends SceneTree
## Pure matrix/camera test. Headless is intentional; never visual evidence.
func _initialize():call_deferred("run")
func run():
 root.size=Vector2i(1180,664)
 var a=Camera3D.new();root.add_child(a)
 var v=SubViewport.new();v.size=Vector2i(1180,664);root.add_child(v)
 var b=Camera3D.new();v.add_child(b)
 var rng=RandomNumberGenerator.new();rng.seed=51001
 var max_error=0.0;var count=0;var failures=[]
 for projection_mode in [Camera3D.PROJECTION_PERSPECTIVE,Camera3D.PROJECTION_ORTHOGONAL,Camera3D.PROJECTION_FRUSTUM]:
  for i in range(40):
   a.projection=projection_mode;a.keep_aspect=i%2;a.fov=40.0+i;a.size=30.0+i;a.frustum_offset=Vector2(.2,-.3);a.near=.5;a.far=20000
   a.position=Vector3(rng.randf_range(-1500,1500),rng.randf_range(10,1000),rng.randf_range(-1500,1500));a.rotation=Vector3(rng.randf_range(-1.0,-.1),rng.randf_range(-PI,PI),rng.randf_range(-.5,.5));a.h_offset=3.0;a.v_offset=-2.0
   var src=a.get_camera_transform();var R=Basis(Vector3(1,0,0),Vector3(0,-1,0),Vector3(0,0,1))
   b.global_transform=Transform3D(Basis(R*src.basis.x,-R*src.basis.y,R*src.basis.z).orthonormalized(),R*src.origin)
   b.projection=a.projection;b.keep_aspect=a.keep_aspect;b.fov=a.fov;b.size=a.size;b.frustum_offset=Vector2(a.frustum_offset.x,-a.frustum_offset.y);b.near=a.near;b.far=a.far;b.h_offset=0;b.v_offset=0
   for j in range(20):
    var p=Vector3(rng.randf_range(-3000,3000),0,rng.randf_range(-3000,3000))
    var av=a.get_camera_transform().affine_inverse()*p;var bv=b.get_camera_transform().affine_inverse()*p
    var ca=a.get_camera_projection()*Vector4(av.x,av.y,av.z,1);var cb=b.get_camera_projection()*Vector4(bv.x,bv.y,bv.z,1)
    if ca.w<1.0 or cb.w<1.0:continue
    var error=Vector2(ca.x/ca.w-cb.x/cb.w,ca.y/ca.w+cb.y/cb.w).length();max_error=maxf(max_error,error);count+=1
    if error>0.002:failures.append({"projection":projection_mode,"error":error})
 print(JSON.stringify({"scope":"Pure Godot camera optical matrix test, not rendered evidence","sample_count":count,"max_ndc_error":max_error,"tolerance":.002,"failures":failures,"visual_acceptance":false}))
 a.queue_free();v.queue_free();await process_frame;quit(0 if failures.is_empty() and count>1000 else 1)

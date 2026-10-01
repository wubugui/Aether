extends Node3D
## Independent51b: 1.08 optical overscan and enabled-by-default live reflection.
## Same-World3D planar reflection. This node never moves the primary camera,
## touches simulation, creates duplicate world geometry, or edits source assets.
const WATER_LAYER := 262144
const MARKER_LAYER := 524288
@export var main_camera_path: NodePath = NodePath("../../Camera")
@export var ocean_path: NodePath = NodePath("../Ocean")
@export var clip_enabled := true
@export var reflection_enabled := true
@export var clipping_materials: Array[ShaderMaterial] = []
@export_range(.25,1.0,.05) var reflection_scale := 1.0
@export_range(1.0,1.25,.01) var optical_overscan := 1.08
@export_range(0.0,1.0,.01) var reflection_strength := .94
var main_camera: Camera3D
var ocean: MeshInstance3D
var viewport: SubViewport
var reflection_camera: Camera3D
var water: ShaderMaterial
var failure := ""
var sync_count := 0
var effective_reflection := false
var texture_bound := false
func _ready() -> void:
	process_priority=1000
	main_camera=get_node_or_null(main_camera_path) as Camera3D
	ocean=get_node_or_null(ocean_path) as MeshInstance3D
	viewport=get_node_or_null("ReflectionViewport") as SubViewport
	reflection_camera=get_node_or_null("ReflectionViewport/ReflectionCamera") as Camera3D
	if main_camera==null or ocean==null or viewport==null or reflection_camera==null or not ocean.material_override is ShaderMaterial:
		failure="Missing exact reflection51b camera/ocean/viewport/material binding";push_error(failure);set_process(false);return
	water=ocean.material_override
	viewport.own_world_3d=false
	viewport.world_3d=get_world_3d()
	viewport.transparent_bg=false
	viewport.disable_3d=false
	viewport.render_target_update_mode=SubViewport.UPDATE_DISABLED
	reflection_camera.current=true
	water.set_shader_parameter("lake51_reflection_texture",viewport.get_texture())
	texture_bound=true
	set_effect_flags(clip_enabled,reflection_enabled)
func _process(_delta: float) -> void:
	refresh_now()
func set_effect_flags(clip: bool, reflection: bool) -> void:
	clip_enabled=clip
	reflection_enabled=reflection
	for material in clipping_materials:
		if material!=null:
			material.set_shader_parameter("lake51_reflection_clip_enabled",clip)
			material.set_shader_parameter("lake51_reflection_plane_y",0.0)
	refresh_now()
func reflected_y(value: Vector3) -> Vector3:
	return Vector3(value.x,-value.y,value.z)
func refresh_now() -> void:
	if main_camera==null or viewport==null or reflection_camera==null or water==null:return
	# Bit19 is a camera-only pass marker; no old geometry owns that layer.
	if clip_enabled:main_camera.cull_mask=main_camera.cull_mask & ~MARKER_LAYER
	reflection_camera.cull_mask=(main_camera.cull_mask | MARKER_LAYER) & ~WATER_LAYER
	# Effective optical pose includes h/v offsets. Reflect it once, then keep
	# secondary offsets zero. Flip reflected up as well to retain det=+1 and roll.
	var source: Transform3D=main_camera.get_camera_transform()
	var basis := Basis(reflected_y(source.basis.x),-reflected_y(source.basis.y),reflected_y(source.basis.z)).orthonormalized()
	reflection_camera.global_transform=Transform3D(basis,reflected_y(source.origin))
	reflection_camera.projection=main_camera.projection
	reflection_camera.keep_aspect=main_camera.keep_aspect
	# Expand the optical frustum, not the texture UV. The shader receives the
	# actual expanded projection below, preserving every world-plane mapping.
	reflection_camera.fov=rad_to_deg(2.0*atan(tan(deg_to_rad(main_camera.fov)*.5)*optical_overscan))
	reflection_camera.size=main_camera.size*optical_overscan
	reflection_camera.frustum_offset=Vector2(main_camera.frustum_offset.x,-main_camera.frustum_offset.y)
	reflection_camera.near=main_camera.near
	reflection_camera.far=main_camera.far
	reflection_camera.h_offset=0.0
	reflection_camera.v_offset=0.0
	reflection_camera.environment=main_camera.environment
	reflection_camera.attributes=main_camera.attributes
	var source_viewport: Viewport=main_camera.get_viewport()
	var source_size: Vector2=source_viewport.get_visible_rect().size
	var target_size := Vector2i(maxi(64,roundi(source_size.x*reflection_scale)),maxi(64,roundi(source_size.y*reflection_scale)))
	if viewport.size!=target_size:viewport.size=target_size
	viewport.msaa_3d=source_viewport.msaa_3d
	viewport.screen_space_aa=source_viewport.screen_space_aa
	# Reflection below/at the water surface has no valid above-water mirror view.
	effective_reflection=reflection_enabled and clip_enabled and source.origin.y>.05
	viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS if effective_reflection else SubViewport.UPDATE_DISABLED
	water.set_shader_parameter("lake51_reflection_enabled",effective_reflection)
	water.set_shader_parameter("lake51_reflection_strength",reflection_strength)
	water.set_shader_parameter("lake51_reflection_view",reflection_camera.get_camera_transform().affine_inverse())
	water.set_shader_parameter("lake51_reflection_projection",reflection_camera.get_camera_projection())
	sync_count+=1
func get_diagnostic_state() -> Dictionary:
	var materials := []
	for material in clipping_materials:
		materials.append({"resource_path":material.resource_path,"clip_enabled":material.get_shader_parameter("lake51_reflection_clip_enabled"),"plane_y":material.get_shader_parameter("lake51_reflection_plane_y")})
	var shared := viewport!=null and is_inside_tree() and viewport.world_3d==get_world_3d()
	return {"failure":failure,"clip_enabled":clip_enabled,"reflection_requested":reflection_enabled,"reflection_effective":effective_reflection,"same_world3d":shared,"world3d_instance":get_world_3d().get_instance_id() if is_inside_tree() else 0,"world3d_scenario":str(get_world_3d().scenario) if is_inside_tree() else "","reflection_world3d_instance":viewport.world_3d.get_instance_id() if viewport!=null and viewport.world_3d!=null else 0,"primary_transform":str(main_camera.get_camera_transform()) if main_camera!=null else "","reflection_transform":str(reflection_camera.get_camera_transform()) if reflection_camera!=null else "","primary_cull_mask":main_camera.cull_mask if main_camera!=null else 0,"reflection_cull_mask":reflection_camera.cull_mask if reflection_camera!=null else 0,"ocean_layers":ocean.layers if ocean!=null else 0,"viewport_size":viewport.size if viewport!=null else Vector2i.ZERO,"texture_bound":texture_bound,"texture_rid":str(viewport.get_texture().get_rid()) if viewport!=null else "","texture_size":[viewport.get_texture().get_width(),viewport.get_texture().get_height()] if viewport!=null else [],"fov":reflection_camera.fov if reflection_camera!=null else 0,"near":reflection_camera.near if reflection_camera!=null else 0,"far":reflection_camera.far if reflection_camera!=null else 0,"keep_aspect":reflection_camera.keep_aspect if reflection_camera!=null else -1,"projection":str(reflection_camera.get_camera_projection()) if reflection_camera!=null else "","sync_count":sync_count,"optical_overscan":optical_overscan,"clipping_materials":materials,"water_recursion_excluded":reflection_camera!=null and (reflection_camera.cull_mask & WATER_LAYER)==0,"hardware_gpu_acceptance":false,"visual_acceptance":false}

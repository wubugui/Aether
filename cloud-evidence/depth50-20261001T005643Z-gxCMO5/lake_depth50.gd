extends Node3D
## Independent vertical bathymetry binding. Does not alter any geometry,
## camera, layer, world generation, material authority or simulation.
@export var ocean_path: NodePath = NodePath("../Ocean")
@export var depth_enabled := true
@export var base_height_image: Image
@export var patch_images: Array[Image] = []
@export var patch_bounds: Array[Vector4] = []
@export var patch_sizes: Array[Vector2i] = []
var textures: Array[ImageTexture] = []
var water: ShaderMaterial
var bound := false
var failure := ""
var image_report: Array = []
func _ready() -> void:
	var ocean := get_node_or_null(ocean_path) as MeshInstance3D
	if ocean == null or not ocean.material_override is ShaderMaterial:
		failure="Missing Ocean ShaderMaterial";push_error(failure);return
	water=ocean.material_override
	water.set_shader_parameter("lake50_depth_enabled",false)
	if base_height_image == null or base_height_image.get_format()!=Image.FORMAT_RF or base_height_image.get_size()!=Vector2i(769,1537):
		failure="Invalid base R32F height image";push_error(failure);return
	if patch_images.size()!=4 or patch_bounds.size()!=4 or patch_sizes.size()!=4:
		failure="Expected exactly four independent height patches";push_error(failure);return
	for i in range(4):
		if patch_images[i]==null or patch_images[i].get_format()!=Image.FORMAT_RF or patch_images[i].get_size()!=patch_sizes[i]:
			failure="Invalid R32F patch "+str(i);push_error(failure);return
	image_report.append(describe_image(base_height_image))
	textures.append(ImageTexture.create_from_image(base_height_image))
	water.set_shader_parameter("lake50_height",textures[0])
	for i in range(4):
		image_report.append(describe_image(patch_images[i]))
		textures.append(ImageTexture.create_from_image(patch_images[i]))
		water.set_shader_parameter("lake50_patch"+str(i),textures[i+1])
		water.set_shader_parameter("lake50_patch_bounds"+str(i),patch_bounds[i])
		water.set_shader_parameter("lake50_patch_size"+str(i),Vector2(patch_sizes[i]))
	bound=true
	set_depth_enabled(depth_enabled)
func set_depth_enabled(enabled: bool) -> void:
	depth_enabled=enabled
	if water!=null:water.set_shader_parameter("lake50_depth_enabled",enabled and bound)
func refresh_now() -> void:
	set_depth_enabled(depth_enabled)
func describe_image(im: Image) -> Dictionary:
	var hasher := HashingContext.new()
	hasher.start(HashingContext.HASH_SHA256)
	hasher.update(im.get_data())
	return {"path":im.resource_path,"size":im.get_size(),"format":im.get_format(),"data_sha256":hasher.finish().hex_encode(),"file_sha256":FileAccess.get_sha256(im.resource_path) if FileAccess.file_exists(im.resource_path) else ""}
func get_diagnostic_state() -> Dictionary:
	var paths := []
	if base_height_image!=null:paths.append(base_height_image.resource_path)
	for patch in patch_images:paths.append(patch.resource_path)
	return {"bound":bound,"enabled":depth_enabled,"actual_uniform":water.get_shader_parameter("lake50_depth_enabled") if water!=null else null,"failure":failure,"image_paths":paths,"images":image_report,"texture_count":textures.size(),"patch_bounds":patch_bounds,"patch_sizes":patch_sizes,"base_bounds":[768,-2304,1536,-768],"base_spacing_m":1.0,"patch_spacing_m":0.25,"patch_feather_m":8.0,"domain_feather_m":32.0,"camera_or_layer_changes":false,"reflection":false}

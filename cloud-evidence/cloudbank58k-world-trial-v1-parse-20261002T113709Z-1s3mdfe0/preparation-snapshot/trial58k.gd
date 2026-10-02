extends Node3D
## Explicit one-unit trial. The saved inherited game and its entry stay unchanged.
@export var enabled := false
const OLD_PATH := "CloudSea_1_1/cloud_sea_46_0_continuous_crown"
const K_SCENE := "res://cloud_k_trial/accepted-native-k.tscn"
const K_SHA := "91ab3412c67b5f82449396677a30a9bbe1542a338c00150dc1822910cdf7f789"
const ANCHOR := Vector3(3958, 0, 3667)
var old_mesh: MeshInstance3D
var unit: Node3D
var shell: MeshInstance3D
var old_visible := true
var failure := ""

func require_value(ok: bool, message: String) -> bool:
 if not ok:
  failure = message
  push_error(message)
 return ok

func _ready() -> void:
 if enabled: activate()

func digest(bytes: PackedByteArray) -> String:
 var h := HashingContext.new()
 h.start(HashingContext.HASH_SHA256)
 if not bytes.is_empty(): h.update(bytes)
 return h.finish().hex_encode()

func activate() -> bool:
 if unit != null:
  enabled = true
  old_mesh.visible = false
  unit.visible = true
  return true
 if not require_value(global_transform == Transform3D.IDENTITY, "Identity trial parent frame required"): return false
 old_mesh = get_parent().get_node_or_null(OLD_PATH) as MeshInstance3D
 if not require_value(old_mesh != null and old_mesh.mesh is ArrayMesh, "Exact one current-61 old cloud unit required"): return false
 var old_arrays: Array = old_mesh.mesh.surface_get_arrays(0)
 if not require_value(old_mesh.mesh.get_surface_count() == 1 and old_arrays[Mesh.ARRAY_VERTEX].size() == 14374 and old_arrays[Mesh.ARRAY_INDEX].size() == 15492, "Pinned old46 unit counts"): return false
 if not require_value(FileAccess.get_sha256(K_SCENE) == K_SHA, "Successful saved native K scene required"): return false
 var packed := ResourceLoader.load(K_SCENE, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
 if not require_value(packed != null, "Load native K PackedScene"): return false
 unit = packed.instantiate() as Node3D
 if not require_value(unit != null and unit.get_child_count() == 1 and unit.transform == Transform3D.IDENTITY, "Exact native K root identity"): return false
 shell = unit.get_child(0) as MeshInstance3D
 if not require_value(shell != null and shell.transform == Transform3D.IDENTITY and shell.mesh is ArrayMesh and shell.material_override == null, "Unchanged native K mesh and authored material"): return false
 var surfaces: Array = shell.mesh.get("_surfaces")
 if not require_value(surfaces.size() == 1 and int(surfaces[0].format) == 34359742471, "Exact K surface format"): return false
 if not require_value(digest(surfaces[0].vertex_data) == "6d3e3be9014ae790556976d1e40cf60ee460e9aa869efca6b9abce397f9b8262" and digest(surfaces[0].index_data) == "ea7db52bc6c7f11cafcbaeb3043feac4593f2eed131d0a0ce9fe11e59fd46a2d", "Exact K position/normal/tangent/index stored payloads"): return false
 old_visible = old_mesh.visible
 add_child(unit)
 # K local coordinates already use world axes and absolute world Y.
 # This is the one translation; no old root rotation, UV frame, scale or recenter.
 unit.transform = Transform3D(Basis.IDENTITY, ANCHOR)
 if not require_value(unit.global_transform == Transform3D(Basis.IDENTITY, ANCHOR), "Exact identity-basis world placement"): return false
 old_mesh.visible = false
 unit.visible = true
 enabled = true
 return true

func deactivate() -> void:
 if old_mesh != null: old_mesh.visible = old_visible
 if unit != null: unit.visible = false
 enabled = false

func material_state(mesh: MeshInstance3D) -> Dictionary:
 var m := mesh.get_active_material(0) as StandardMaterial3D
 if m == null: return {"standard": false}
 var textures := 0
 for i in range(BaseMaterial3D.TEXTURE_MAX):
  if m.get_texture(i) != null: textures += 1
 return {"standard": true, "albedo": [m.albedo_color.r,m.albedo_color.g,m.albedo_color.b,m.albedo_color.a],
  "diffuse_mode": m.diffuse_mode, "roughness": m.roughness, "metallic": m.metallic,
  "cull_mode": m.cull_mode, "transparency": m.transparency, "shading_mode": m.shading_mode,
  "vertex_color_use_as_albedo": m.vertex_color_use_as_albedo, "texture_count": textures,
  "emission_enabled": m.emission_enabled, "next_pass": m.next_pass != null,
  "disable_fog": m.disable_fog}

func state() -> Dictionary:
 var storage := {}
 if shell != null:
  var surfaces: Array = shell.mesh.get("_surfaces")
  storage = {"format":int(surfaces[0].format), "vertex_count":int(surfaces[0].vertex_count),
   "index_count":int(surfaces[0].index_count), "vertex_data_sha256":digest(surfaces[0].vertex_data),
   "index_data_sha256":digest(surfaces[0].index_data)}
 return {"enabled":enabled, "old_path":OLD_PATH, "old_visible":old_mesh.visible if old_mesh else null,
  "k_visible":unit.visible if unit else false, "k_world_transform":var_to_bytes(unit.global_transform).hex_encode() if unit else "",
  "k_storage":storage,
  "old_material":material_state(old_mesh) if old_mesh else {}, "k_material":material_state(shell) if shell else {},
  "failure":failure, "world_unit_count":1 if unit else 0}
